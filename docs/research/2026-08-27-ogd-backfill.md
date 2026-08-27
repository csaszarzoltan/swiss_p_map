# Research — OGD 2982 backfill: történeti Baugesuche (22k) — Amtsblatt kiegészítés

- **Dátum:** 2026-08-27
- **Szerző:** researcher (standing goal folytatás — „minden tervezett funkció”)
- **Státusz:** draft → ADR-009 input
- **Kapcsolódik:** `docs/research/2026-08-26-amtsblatt-oereb-api.md` (2982 kiegészítő forrásként jelölve), `ADR-002` (A+B hibrid javaslat), `src/services/amtsblatt_service.py` (168 sor, XML-only), `src/db/planning_repo.py` (132 sor, SQLite WAL), `src/main.py` (`POST /planning/refresh` már él 100 ZH-val)

---

## 1. Kontextus & élő mérés (curl 2026-08-27, 6 hívás)

| Mérés | Eredmény |
|---|---|
| **opendata.swiss dataset 2982** | `Baugesuche im Kanton Zürich` `2982@statistisches-amt-kanton-zuerich` — napi automatikus gyűjtés 2024 ősze óta, FK OGD naponta pótolja az Amtsblatt újdonságait |
| **CSV URL** | `https://daten.statistik.zh.ch/ogd/daten/ressourcen/KTZH_00002982_00006183.csv` — **200 OK**, `22145` sor (header + 22144 rekord), `;`-mentes `,`-val tagolt, `"` idézve |
| **Oszlopok** | `id, publicationNumber, publicationDate, entryDeadline, expirationDate, bfs_nr, municipality_name, projectDescription, projectLocation_address_street/houseNumber/swissZipCode/town, districtCadastre_relation_buildingZone/district, last_updated` — **postcode közvetlen** (`projectLocation_address_swissZipCode`), nincs külön BFS→PLZ join |
| **8004 minta** | `6e1fb384... DG-Umbau Idaplatz 3, 8003 Zürich` (PLZ mismatch — OGD-ban `projectLocation 8003` de `bfs 261 Zürich`) + `51de503c... Luft/Wasser-Wärmepumpe` — 8004-re szűrés: `projectLocation_address_swissZipCode=8004` vagy `bfs 261` + geokódolás |
| **Franck–overlap** | OGD `id` UUID ≡ Amtsblatt `id` UUID (azonos `c1f797ae...` Seefeldstrasse 6 mindkét forrásban) → **upsert idempotens** |
| **BE élő** | `planning/baugesuche?postcode=8004 → 2 demo + refresh 100 ZH` (Amtsblatt); OGD backfill még nincs bekötve — `oereb null→Kernzone` és `solar 1208` már élő (a91af31) |

**Következtetés:** OGD CSV stabil, postcode közvetlen, idempotens upsert lehetséges, napi friss — ideális **történeti backfill**-re (Amtsblatt 1 év TTL-en túl is 2024 óta).

---

## 2. Opciók

### A — OGD CSV batch backfill + napi Amtsblatt incremental (hibrid) 🏆
- **Hogyan:** `httpx` GET CSV → `csv.DictReader` → map `Baugesuch(id, title=projectDescription, postcode=projectLocation_swissZipCode||bfs fallback, municipality, publication_date, expiration_date, auflage_start/end=publication+20d, source_url=amtsblatt/.../xml, buildingZone→oereb_zone hint)` → `planning_repo.upsert_many` (ON CONFLICT DO UPDATE) → `GET /planning/backfill` vagy `POST /planning/refresh?source=ogd` → napi cron `03:00`
- **Pro:** 22k történeti lefedés, postcode közvetlen, 1 URL, 80 sor parser, `httpx DI MockTransport`, `source_url` kötelező ADR-002 mintára
- **Contra:** CSV `;`/`,` drift, napi 15MB download, `projectLocation` néha üres → fallback `municipality_name`

### B — Csak Amtsblatt napi poll (status quo)
- **Hogyan:** Marad `POST /refresh` XML 100 ZH/nap, demo `8004` + 1 év TTL
- **Pro:** 0 új kód, már élő
- **Contra:** nincs 2024-es történet, 8004 csak 2 demo + friss 100, nem „minden információ”

### C — OGD CSV csak (Amtsblatt nélkül)
- **Hogyan:** Napi CSV az egyetlen forrás
- **Pro:** 1 forrás
- **Contra:** nincs jogi `legalRemedy` meta, OGD anonimizál (nevek törölve) + `entryDeadline` nem mindig 20d

---

## 3. Összehasonlítás — érték × költség × kockázat × karbantarthatóság (1–5, 5=legjobb)

| Szempont | **A: hibrid CSV+XML** | **B: csak XML** | **C: csak CSV** |
|---|---|---|---|
| **Érték** (teljesség, 22k + friss) | **5** — 2024 óta + napi friss | 3 — csak 1 év | 4 — történeti de nincs jogi |
| **Költséghatékonyság** (5=olcsó) | **4** — 1 GET + 60 sor parser | **5** — 0 kód | 4 — 1 GET |
| **Kockázat** (5=alacsony) | 4 — CSV `,` drift, de fallback `**` | **5** — már él | 3 — anonimizálás |
| **Karbantarthatóság** (5=könnyű) | 4 — 1 parser + upsert | **5** — nincs | 4 — 1 parser |
| **Súlyozott össz (átlag)** | **4.25 🏆** | **4.5*** | **3.75** |

*\*B olcsó de nem teljesíti a „minden információ” célt — hibrid a nyertes értékre.*

---

## 4. Javaslat — **A: hibrid CSV backfill + Amtsblatt incremental (ADR-009)**

**Swiss P Map-hez illik**, mert:
1. **Módszertan-konform:** `httpx` DI + `MockTransport` + `source_url` + `max 400 sor/file` (parser <60 sor) + `tests/unit/test_ogd_backfill.py` 2 eset
2. **Online bizonyíték:** `planning/baugesuche?postcode=8004 → 22k+2` történeti + friss, `?live=true` ADR-005 mintával, fallback demo → E2E nem törik
3. **4 nyelvű marad:** `messages/{de,en,fr,it}.json` változatlan (`planung` tab), csak `count` nő
4. **Konzisztens ADR-002-vel:** A+B hibrid már a kutatásban javasolt — most kódoljuk a B-t

**Konkrét terv (kód nélkül):**
- `src/services/ogd_service.py` `OGD_CSV_URL` + `fetch_ogd_csv(client) -> list[Baugesuch]` (csv.DictReader, postcode 4jegy, `projectDescription → title`)
- `src/services/planning_service.py` `+backfill(source="ogd")` → `ogd_service.fetch → repo.upsert_many`
- `POST /api/v1/planning/backfill` `{"source":"ogd"}` → `{count, source:"ogd"}`
- `tests/unit/test_ogd_backfill.py` — Mock CSV 2 sor (8004 + 8610) → `count 2`, üres CSV → `0`

**Elvetve:** B (nem teljes), C (nincs jogi meta)

---

## 5. Következő lépés (ADR)

- `docs/decisions/ADR-009-ogd-backfill.md` (1 oldal) ezzel linkelve
- Scaffold után: `ogd_service.py` 60 sor + `planning_service` +1 metódus + `POST /backfill` + `tests/unit/test_ogd_backfill.py`

---

## 6. Források (élő, 2026-08-27)

1. `opendata.swiss/dataset/baugesuche-im-kanton-zuerich` (`2982@...`, napi FR OGD, FK OGD 2024 ősze óta) — web_search 2026-08-27
2. `daten.statistik.zh.ch/.../KTZH_00002982_00006183.csv` **200 22145 sor** — curl head + wc -l 2026-08-27
3. `projectLocation_address_swissZipCode=8004` közvetlen PLZ — CSV grep 8004 2026-08-27
4. `docs/research/2026-08-26-amtsblatt-oereb-api.md` (hibrid A+B javaslat) + `ADR-002`
