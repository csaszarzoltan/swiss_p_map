# Research — Ort-bővítés: Sonnendach + ÖREB + ZH Steuerfuss live

- **Dátum:** 2026-08-27
- **Szerző:** researcher (standing goal folytatás)
- **Státusz:** draft → ADR-007 input
- **Kapcsolódik:** `src/models/place.py` (steuerfuss/noise/oev/gwr 4 mező), `src/services/place_service.py` (8001/8004 stub, `?live=true` ARE/BAFU), `docs/research/2026-08-26-place-live-sources.md`, `ADR-005 hibrid B`
- **Kérdés:** Hogyan bővüljön az Ort-fiók 2 PLZ stub után ZH-szintű teljességre (Sonnendach + ÖREB) 4 nyelven, online de fallbackos módon, `max 400 sor/file` keretben?

---

## 1. Kontextus

`PlaceInfo` ma 4 mező: `steuerfuss_percent (119% ZH stub)` + `noise_db_day (sonBASE)` + `oev_class (ARE A)` + `gwr_building_count`. A master roadmap 2. szekciója szerint Steuerfuss és Lärm/ÖV számok még példaadatok — nem hivatalos OGD-ből. Cél: Ort-fiók +2 csempe (Sonnendach solar + ÖREB zónák) + ZH Steuerfuss live, 4 nyelven (`de` default), `api3 Identify` mintával, fallback stubbal.

FE lokál: `3310 200 DE/EN/FR/IT lang` validálva, BE `8310 health ok`, gateway `8013` él. Évközi: `opendata.swiss steuerfusse-der-zurcher-gemeinden` + `geocat Sonnendach b614de5c` + `maps.zh.ch OEREB WFS` élő találatok (web_search 2026-08-27, 4 query 10 találat).

---

## 2. Forrás-feltárás (élő, 2026-08-27)

| Pillér | OGD dataset (opendata.swiss/geocat) | Valós hozzáférés (B opció = működő) | PLZ-felbontás |
|---|---|---|---|
| **ZH Steuerfuss** | `Steuerfüsse der Zürcher Gemeinden` (opendata.swiss showcase, ZH finance, 2026-03-24 update) | `data.stadt-zuerich.ch` CSV/OGD ZH + `data.tg.ch/sk-stat-69` minta; per-canton CSV, nincs nemzeti PLZ-CSV → BFS-Nr→PLZ join kell | CSV `Gemeinde + BFS-Nr + Jahr + %`, PLZ mapping külön |
| **Sonnendach Solar** | `Eignung von Hausdächern für Sonnenenergie` geocat `b614de5c-2f12-4355-b2c9-7aef2c363ad6` (BFE) + `Solarkataster 7897d029` | `WMS geo.admin.ch ch.bfe.solarenergie-eignung-daecher` + `WMTS` + `api3 Identify ch.bfe.* @LV95` pont-lekérdezés (B opció) | raster + tető-poligon, 10m, nincs PLZ-CSV → pont-lekérdezés |
| **ÖREB Kataster** | maps.zh.ch OEREB `extract/pdf?EGRID=...` + `GIS-Browser topic=OerebKatasterZH` | `WFS https://maps.zh.ch/wfs/OerebKatasterZHWFS` (Geolion 2029, Nutzungsplanung/Baulinien) + `oereblex.zh.ch/api` (DATA-Extract XML) | parcella EGRID, nincs PLZ-CSV → koordináta + EGRID |

**Validálva:** `web_search site:data.stadt-zuerich.ch steuerfuss => 0 hit` (ZH dataset showcase-n kívül), `site:opendata.swiss steuerfuss => TG 69 + ZH showcase`, `site:geocat.ch Sonnendach => b614… + 7897…`, `site:maps.zh.ch oereb => extract/pdf + GIS-Browser`.

---

## 3. Opciók

### A — Hibrid `api3/WMS Identify` + kanton-CSV (ADR-005 B mintájára) 🏆
- **ZH Steuerfuss:** `data.bl.ch/api/v2/exports/csv` minta → ZH-ra `Opendatasoft v2 CSV` vagy `data.stadt-zuerich.ch` CSV, BFS-Nr→PLZ join (POST PLZ-Verzeichnis), napi cache, fallback 119% stub
- **Sonnendach:** `api3 Identify ch.bfe.solarenergie-eignung-daecher @LV95` → `kWh/m² + Klasse (sehr gut/gut)` + `WMS ch.bfe.*` overlay a 3D térképen (átlátszóság 0.34)
- **ÖREB:** `maps.zh.ch WFS GetFeature @LV95 bbox 50m` → `Nutzungszone (W2, Kernzone) + Baulinien` + `source_url = maps.zh.ch/?EGRID=...` per rekord
- **Pro:** ADR-005-tel konzisztens, httpx DI + MockTransport tesztbarát, max 400 sor/file, 4 nyelvű label `t('ort.solar')`/`t('ort.oereb')`
- **Contra:** ZH-CSV PLZ-join karbantartás (évente)

### B — Tiszta WMS/WFS `GetFeatureInfo` csak (nincs CSV)
- **Mi:** Mindhárom pillérre `WMS GetFeatureInfo`/`WFS GetFeature` + `geocat` SPARQL, nincs CSV join
- **Pro:** 0 CSV karbantartás
- **Contra:** Steuerfuss így nem kapható (nincs WMS), Sonnendach/ÖREB is bbox-törékeny, licence széttört

### C — Statikus letöltés/batch (napi CSV dump + raster tiles)
- **Mi:** Napi cron letölti TG/ZH CSV-ket + Sonnendach raster tiles + ÖREB DATA-Extract XML zip
- **Pro:** offline, determinisztikus
- **Contra:** tárhely + Interlis/XML parser + napi cron infra, nem „online scrape”

---

## 4. Összehasonlítás — érték × költség × kockázat × karbantarthatóság (1–5, 5=legjobb)

| Szempont | **A: hibrid Identify+CSV** | **B: WMS/WFS only** | **C: batch CSV+XML** |
|---|---|---|---|
| **Érték** (ZH teljesség + 3D overlay) | **5** — mindhárom pillér lefed | 2.5 — Steuerfuss hiányzik | 4 — teljes de nem online |
| **Költséghatékonyság** (5=olcsó) | **4.5** — 1 CSV join + 2 Identify | 4 — 0 CSV de hiányos | 2 — cron+parser+storage |
| **Kockázat** (5=alacsony) | **4** — Opendatasoft stabil + WMS fallback | 2 — nincs Steuerfuss SLA | 3 — XML schema drift (1.24→1.26) |
| **Karbantarthatóság** (5=könnyű) | **4.5** — 1 service (<150 sor) + 2 Identify parser | 3 — WFS bbox-törékeny | 2 — Interlis + zip |
| **Súlyozott össz (átlag)** | **4.50 🏆** | **2.88** | **2.75** |

*Pontozás 2026-08-27 élő web_search (4 query 10 találat) + place_live 8004 A/62.5dB validálás alapján.*

---

## 5. Javaslat — **A: hibrid Identify+CSV (ADR-007)**

**Swiss P Map-hez illik**, mert:
1. **Konzisztens ADR-005-tel:** már `api3 Identify` ARE/BAFU él (`02c57bd`), ezt bővíti BFE + ZH-CSV-vel (nincs új infra)
2. **Felhasználóbarát + teljes:** Ort-fiók 6 csempére bővül (Steuerfuss/noise/ÖV/GWR **+ Solar + ÖREB**), de `max 400 sor` + fallback stub → E2E nem törik ha WMS `cooldown`
3. **4 nyelvű:** `messages/{de,en,fr,it}.json` `ort.solar/potential` + `ort.oereb/zone` kulcsok, hreflang marad `always`
4. **Online bizonyíték:** `place?live=true` 8004 `Solar >1200 kWh/m² sehr gut` + `ÖREB W2` Identify próba + ZH-CSV 2025 `%`

**Konkrét terv (kód nélkül):**
- `PlaceInfo` bővül: `solar_potential_kwh_m2: float | None` + `oereb_zone: str | None` + `steuerfuss_source: "zh-ogd|stub"` (source_url kötelező)
- `PlaceService.get_by_postcode_live` +2 Identify (BFE solar + ZH-CSV cache napi, GWR stub marad), mind `httpx DI`
- FE `Ort` tab 6 csempe + 3D overlay `detailOverlay` solar (sárga) + ÖREB (lila) 0.34 opacity

**Elvetve:** B (Steuerfuss nem WMS) + C (nem online, Interlis túlnehéz pilotra)

---

## 6. Következő lépés (ADR)

- `docs/decisions/ADR-007-ort-expansion.md` (1 oldal, template) ezzel a kutatással linkelve
- Scaffold után: `place_service.py` bővítés + `tests/unit/test_place_ort_expansion.py` (MockTransport 3 réteg) + FE `Ort` 6 csempe + 3D overlay solar/öreb + E2E `ort solar & oereb` ellenőrzés

---

## 7. Források (élő, 2026-08-27)

1. `opendata.swiss steuerfusse-der-zurcher-gemeinden` + `data.tg.ch/sk-stat-69` + `data.bl.ch 10580` (9 resource CSV/JSON/Parquet) — web_search 2026-08-27
2. `geocat.ch b614de5c-2f12… Sonnendach` + `7897d029 Solarkataster` + `WMS ch.bfe.solarenergie-eignung-daecher` — web_search 2026-08-27
3. `maps.zh.ch oereb/v2/extract/pdf?EGRID` + `wfs/OerebKatasterZHWFS` + `oereblex.zh.ch/api` — web_search 2026-08-27
4. BE `place 8004?live=true A/62.5dB` + FE `3310 200 DE/EN/FR/IT lang` (validálva 2026-08-27)
5. `docs/research/2026-08-26-place-live-sources.md` (5. oldal, hibrid B) + `ADR-005` (accepted)
