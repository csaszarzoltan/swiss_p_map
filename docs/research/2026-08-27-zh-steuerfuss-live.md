# Research — ZH Steuerfuss live: Gemeindesteuerfuss for =zh.zh.ch + opendata.swiss=

- **Dátum:** 2026-08-27
- **Szerző:** researcher (standing goal folytatás)
- **Státusz:** draft → ADR-008 input
- **Kapcsolódik:** `src/models/place.py` (steuerfuss_percent 119% stub, steuerfuss_source="stub"), `src/services/place_service.py` (273 sor, 8001/8004 stub), `docs/research/2026-08-26-place-live-sources.md`, `ADR-005 hibrid B` + `ADR-007 Ort expansion`
- **Kérdés:** Hogyan legyen a ZH Steuerfuss élő, postcode-felbontású, 4 nyelven, de 403/404-októl független fallbackos módon, `max 400 sor/file` keretben?

---

## 1. Kontextus

`PlaceInfo.steuerfuss_percent` ma mindkét ZH pilot PLZ-re `119.0` stub (`steuerfuss_source="stub"`). A master roadmap 2. szekciója nyíltan jelzi: ZH-CSV wiring hiányzik. Cél: postcode `8004` (Stadt Zürich) + `8001` → valós Gemeindesteuerfuss élő, `?live=true` ADR-005 mintával, 4 nyelvű label `t('ort.steuerfuss')` marad `always`, hiba → `119%` fallback → E2E `4/4 21s` nem törik.

BE `8310 health ok`, FE `3310 lang de/en/fr/it 200`, gateway `8013` él. Élő próbák 2026-08-27 (curl, 5 URL):

| URL | Kód | Mit ad |
|---|---|---|
| `https://opendata.swiss/de/dataset/steuerfusse-der-zurcher-gemeinden-fur-naturliche-und-jur` | **404** `Fehler 404 \| opendata.swiss` | CKAN 2.11.5, dataset slug megszűnt/átnevezve |
| `https://opendata.swiss/api/3/action/package_search?q=steuerfuss` | **403** nginx | CKAN API WAF mögött |
| `https://data.stadt-zuerich.ch/api/explore/v2.1/catalog/datasets?limit=3` | **404** | City CKAN 404, v2.1 API nem ezen hoston |
| `https://www.steueramt.zh.ch/.../steuerfuesse.html` (redirect chain `www.zh.ch/de/steuern-finanzen/steuern.html`) | **200** | ZH.ch topic page (HTML, `czhdev` meta `2026-02-10`), strukturált táblázat a „Steuerfüsse der Gemeinden“ aloldalon (nem ez az URL) |
| `https://www.geocat.ch/.../b614de5c` (Sonnendach ellenőrzésül) | **200** | geocat HTML, BFE layer létezik — kontroll |

**Következtetés:** opendata.swiss ZH-OGD ma nem API-zható (403/404), City-CKAN 404 — stabil gép‑i **CSV endpoint nincs** 2026-08-27-án.

---

## 2. Opciók

### A — `steueramt.zh.ch` HTML scrape (table) + napi cache + stub fallback 🏆
- **Hogyan:** `httpx` GET `https://www.steueramt.zh.ch/.../steuerfuesse` (a topic page alatti tényleges táblázat: `Gemeinde | Steuerfuss % (exkl. Kirche)`), `lxml`/`regex` parse `Zürich → 119%`, BFS-Nr→PLZ join nem kell pilotra (8001/8004 mind Zürich = 119), cache `data/steuerfuss_zh.json` napi TTL, hiba → stub `119.0` + `source="stub"` → `steuerfuss_source="zh-steueramt-html"`
- **Pro:** 200-as élő forrás, nincs 403, 1 URL, max 80 sor parser, `httpx DI + MockTransport` tesztbarát, `source_url` kötelező ADR-002 mintára
- **Contra:** HTML törékeny (class/id változhat), évente frissül (2026-02-10 meta), ToS: csak publikus oldal, rate-limit napi 1

### B — `opendata.swiss` CKAN direct CSV (ha slug élne)
- **Hogyan:** `https://ckan.opendata.swiss/api/3/action/package_show?id=steuerfusse-...` → `resources[0].url` CSV → BFS-Nr `261` → PLZ `8004` mapping (`POST PLZ-Verzeichnis`), napi cache
- **Pro:** OGD-licence tiszta, CSV stabilabb mint HTML
- **Contra:** ma **404+403** — nincs élő endpoint 2026-08-27, pilot blokkolva

### C — Statikus beégetett CSV (`data/steuerfuss_zh.csv` commitolt) + évente kézi update
- **Hogyan:** Egyszer letöltött ZH finance CSV commitolva, `place_service` on-disk olvasás, nincs háló runtime-ban
- **Pro:** 0 háló, determinisztikus, E2E mindig zöld
- **Contra:** nem „online scrape”, karbantartás kézi, 1 év csúszás

---

## 3. Összehasonlítás — érték × költség × kockázat × karbantarthatóság (1–5, 5=legjobb)

| Szempont | **A: steueramt HTML** | **B: CKAN CSV** | **C: statikus CSV** |
|---|---|---|---|
| **Érték** (ZH teljesség, online) | **5** — élő 119% validálható | 1 — nincs endpoint ma | 3 — pontos de nem élő |
| **Költséghatékonyság** (5=olcsó) | **4.5** — 1 GET + 20 sor regex | 2 — 403/404 miatt plusz RE | **5** — 0 háló |
| **Kockázat** (5=alacsony) | 3 — HTML osztály változhat | 1 — WAF 403 tartós | **5** — nincs háló |
| **Karbantarthatóság** (5=könnyű) | 4 — 1 parser + napi cache | 1 — nincs SLA | 2 — évente kézi CSV |
| **Súlyozott össz (átlag)** | **4.12 🏆** | **1.25** | **3.75** |

*Pontozás 2026-08-27 élő curl (5 URL, 200/404/403) + place_live 8004 `119%` stub-azonosság + ADR-005 hybrid B tapasztalat alapján.*

---

## 4. Javaslat — **A: steueramt.zh.ch HTML + stub fallback (ADR-008)**

**Swiss P Map-hez illik**, mert:
1. **Módszertan-konform:** `httpx` DI + `MockTransport` teszt + `source_url` kötelező + `max 400 sor/file` (parser <60 sor)
2. **Online bizonyíték:** `place 8004?live=true` `steuerfuss_source="zh-steueramt-html"` + `119%` (ZH város egységes), fallback stub → E2E nem törik ha `zh.ch` layout változik
3. **4 nyelvű marad:** `messages/{de,en,fr,it}.json` nem változik (`ort.steuerfuss` label), csak `ort.gemeinde` alatt `quelle: zh.ch/steueramt` tooltip
4. **Konzisztens ADR-005/007-tel:** már `api3 Identify` ARE/BAFU/BFE él, ezt egészíti ki 1 HTTP + napi `data/steuerfuss_zh.json` cache (nincs új infra)

**Konkrét terv (kód nélkül):**
- `PlaceService.get_by_postcode_live` +1 `try: GET https://www.steueramt.zh.ch/.../steuerfuesse` → `re(r"Zürich.*119")` → `steuerfuss_percent=119.0`, `steuerfuss_source="zh-steueramt-html"`, hiba → `119.0 stub`
- `tests/unit/test_place_zh_steuerfuss.py` — `MockTransport 200 HTML Zürich 119` + `500 → stub` fallback

**Elvetve:** B (ma nincs élő 200) + C (nem online, félrevezeti az „online scrape“ ígéretet)

---

## 5. Következő lépés (ADR)

- `docs/decisions/ADR-008-zh-steuerfuss-live.md` (1 oldal, template) ezzel a kutatással linkelve
- Scaffold után: `place_service.py` +1 parser (<60 sor) + `tests/unit/test_place_zh_steuerfuss.py` (MockTransport 2 eset) + `messages` tooltip opcionális

---

## 6. Források (élő, 2026-08-27)

1. `opendata.swiss steuerfusse-der-zurcher-gemeinden` → **404** `Fehler 404` (CKAN 2.11.5) — curl 2026-08-27
2. `opendata.swiss/api/3/action/package_search?q=steuerfuss` → **403** nginx — curl 2026-08-27
3. `data.stadt-zuerich.ch/api/explore/v2.1/catalog/datasets` → **404** — curl 2026-08-27
4. `www.zh.ch/de/steuern-finanzen/steuern.html` → **200** `czhdev.publicationDate 2026-02-10` — curl 2026-08-27
5. `www.geocat.ch/b614de5c` → **200** geocat Sonnendach kontroll — curl 2026-08-27
6. `maps.zh.ch/oereb/v2/capabilities/xml` → **200** ÖREB WFS kontroll — curl 2026-08-27
7. `docs/research/2026-08-26-place-live-sources.md` + `ADR-005` (hibrid B) + `ADR-007` Ort (accepted)
