# Research — Place élő OGD források: Steuerfuss · sonBASE · ÖV-Güteklassen · GWR

> **Dátum:** 2026-08-26 | **Szerző:** Research Agent 3 | **Módszer:** élő web_search (exa fallback) + curl HTML-check (2026-08-26), opendata.swiss / geocat.ch / bafu/are/bfs portálok
> **Kapcsolódik:** `src/models/place.py`, `src/services/place_service.py` (stub 8001/8004 119%), `docs/research/2026-08-26-adr002-data-pipeline-deep-dive.md` (#1 Place-first prior)
> **Státusz:** draft — ADR-002 Place-rész input

## 0) TL;DR — van-e „egy nemzeti CSV mind a 4-re"?

**Nincs.** A Place pillér 4 téglája eltérő OGD-rendszerben él:

| Pillér | „Nemzeti CSV opendata.swiss-en?" | Valóság |
|---|---|---|
| **Steuerfuss** | de jure van dataset, de **csak Basel-Landschaft** + széttört kanton-datasettek | országos aggregátor nincs OGD-ben; ESTV nem publikál Gemeindesteuerfuss-CSV-t |
| **sonBASE Lärm** | van dataset-lap, de **nincs letölthető CSV** — SPARQL/raster | WMS/WMTS + facade-pontok a valós hozzáférés |
| **ÖV-Güteklassen ARE** | van dataset-lap, de **nincs CSV-lista** — vektor csempék | WMS/WMTS + data.geo.admin.ch collection + Identify-API |
| **GWR Gebäude** | van BFS dataset-lap, de **nincs nemzeti CSV-dump opendata.swiss-en** | geo.admin.ch WMS/WFS + kanton-daily CSV (BS) |

**Következmény ZH pilotra:** A → nem elég; **hibrid B (geocat + data.geo.admin.ch + api3 Identify) + kiegészítő kanton-CSV** a működő út. C scrape csak fallback.

---

## 1) Steuerfuss (Gemeindesteuerfuss) — BFS/ESTV helyett kanton-OGD

### 1.1 Vezető találat opendata.swiss-en

| Mező | Érték |
|---|---|
| **Dataset címe** | Steuerfüsse und Steuersätze nach Gemeinde und Jahr (seit 1975) |
| **opendata.swiss URL** | `https://opendata.swiss/de/dataset/steuerfusse-und-steuersatze-nach-gemeinde-und-jahr-ab-1975` |
| **Identifier (DCAT)** | `10580@kanton-basel-landschaft` |
| **Permalink** | `/de/perma/10580@kanton-basel-landschaft` |
| **Publisher** | Kanton Basel-Landschaft (daten@bl.ch) — **nem BFS országos** |
| **Publikáció** | 2022-09-05 · **Änderungsdatum: 2026-07-23** · Intervall **Jährlich** |
| **Resszursok (9)** | `CSV` `JSON` `JSONL` `XLS` `Parquet` `RDF Turtle` `RDF XML` `N3` `JSON-LD` |
| **Landing / direct** | `https://data.bl.ch/explore/dataset/10580/` → exportok `https://data.bl.ch/api/v2/catalog/datasets/10580/exports/csv?use_labels=true` (és json/parquet/xls) |
| **Licence** | `terms_by` — „Freie Nutzung. Quellenangabe ist Pflicht." (ikonos CC-BY jelleg) |
| **Format stabilitás** | Opendatasoft v2 API — stabil |
| **Postcode felbontás** | **Nincs PLZ-oszlop.** Kulcs: `Gemeinde` + `BFS-Nr` + `Jahr` + `Steuerfuss %`. PLZ→Gemeinde mapping külön kell (BFS Amtliches Gemeindeverzeichnis / POST PLZ-Verzeichnis). |
| **Tartalom** | Steuerfüsse + Steuersätze, Gebühren, Ersatzabgaben — 1975-től évente |

> **Élő verifikáció 2026-08-26:** HTML-ben 23. Juli 2026 update látszik, 9 resource download-linkkel. CKAN `package_show` API közvetlen `https://opendata.swiss/api/3/action/package_show?id=...` 403 nginx (curl visszaadott „403 Forbidden") — CKAN JSON tehát WAF mögött, **böngésző/HTML a biztosabb**. A `data.bl.ch/api/v2/...` direct export viszont élőnek tűnik (Opendatasoft).

### 1.2 További kanton-datasettek (széttörtség bizonyítéka)

| Kanton | Dataset | ID | URL | Frissítés |
|---|---|---|---|---|
| TG | Gemeindesteuerfüsse der Politischen Gemeinden Kanton Thurgau (ab 2004) | `sk-stat-69@kanton-thurgau` | `https://opendata.swiss/de/dataset/gemeindesteuerfusse-der-politischen-gemeinden-kanton-thurgau1` → `https://data.tg.ch/explore/dataset/sk-stat-69/` | 2025-07-01 (jährlich) |
| ZG | Steuerfüsse der Einwohnergemeinden (2007–2026, inkl. Bürger-/Kirchgemeinde) | — | `https://opendata.swiss/de/dataset/steuerfusse-der-einwohnergemeinden` | — |
| ZH | Steuerfüsse der Zürcher Gemeinden (nat./jur. Personen) | showcase | `https://opendata.swiss/showcase/dataset/steuerfusse-der-zurcher-gemeinden...` + `https://data.stadt-zuerich.ch` (OGD ZH) | 2026-03-24 körüli showcase update |

**ZH pilot tanulság:** Zürichre a ZH-OGD a forrás (Stadt ZH / Kanton ZH finance), nem a BL-dataset. Országos pilothoz **26 kanton-forrást kellene fésülni** → nem skáláz OGD-ből.

### 1.3 Nem-OGD aggregátor (C opcióhoz)

`https://mysalario.ch/de/datensaetze/gemeindesteuerfuesse-2026` — CSV+JSON CC-BY, 26 kanton aggregált 2026-ra (2026-05-26). Jogi státusz: kanton-adatok újrahasznosítása, de **nem hivatalos OGD pipeline** → licence másodlagos.

---

## 2) BAFU sonBASE Lärmkarte — Lärmbelastung durch Verkehr

### 2.1 opendata.swiss dataset-lapok

| Mező | Érték |
|---|---|
| **Fő dataset** | Lärmbelastung durch Verkehr | 
| **URL** | `https://opendata.swiss/de/dataset/larmbelastung-durch-verkehr` |
| **Identifier** | `ubd003701@bundesamt-fur-umwelt-bafu` |
| **Publisher** | Bundesamt für Umwelt BAFU · `noise@bafu.admin.ch` |
| **Publikáció / Änderung** | 2017-07-04 / **2025-08-04** |
| **Zeitliche Abdeckung** | 2015-01-01 – 2015-12-31 (modell-év) |
| **Räumlich** | Schweiz (flächendeckend) |
| **Aktualisierung** | **Unregelmässig** (gyakorlat: 3–6 évente modellfrissítés) |
| **Resszurs** | **SPARQL Endpoint** + `visualize.admin.ch` link — **nincs natív CSV/GeoJSON download** a lapon |
| **Licence** | BAFU OGD terms_by (forrásmegjelöléssel szabad) |
| **Informativ oldal** | `https://www.bafu.admin.ch/de/sonbase` — sonBASE GIS-DB bemutató, swisstopo swissBUILDINGS3D/TLM3D/ALTI3D alapokon, ARE/ASTRA/BAV/BAZL/BFS/kanton geodaten integrációval |

**Rész-datasettek (ugyanaz a modell, bontva):**

- `Daytime road traffic noise exposure (Lr_Tag)` — ID `87f3f029-4685-4d51-9de2-2a409b32aff5@bundesamt-fur-umwelt-bafu`, Modified 2021-12-31, road network ~45 000 km, ~4000 Zählstellen 2021 (NPVM), nem jogilag kötött (ASTRA/kanton a mérvadó).
- `Nighttime road traffic noise exposure (Lr_Nacht)` — ID `89a0b0bc-10ff-4e3e-a4e4-36d081e2e672@bundesamt-fur-umwelt-bafu`, azonos meta.
- `Lärmimmissionen Strassen- und Eisenbahnverkehr (Fassadenpunkte)` — ~36 Mio Fassadenpunkt (tényleges épület-homlokzati dB-értékek) — **ez az épület-szintű OGD**, de csak geodataként.

### 2.2 Valós hozzáférés (B opció) — geocat / geo.admin.ch

| Csatorna | Layer / URL |
|---|---|
| **WMS-BGDI** | `https://wms.geo.admin.ch/?SERVICE=WMS&...&LAYERS=ch.bafu.larm-strassenlaerm_tag` (+ `_nacht`, `ch.bafu.larm-eisenbahnlaerm_*`) |
| **WMTS** | `https://wmts.geo.admin.ch/EPSG/3857/1.0.0/WMTSCapabilities.xml` → `ch.bafu.larm-strassenlaerm_tag` |
| **map.geo.admin.ch preview** | `https://map.geo.admin.ch/?layers=ch.bafu.larm-strassenlaerm_tag` |
| **geocat.ch meta** | `https://www.geocat.ch/geonetwork/srv/api/records/...` + Strassen-Lärm-Belastungs-Kataster (SLBK) `61117cb2-...` (Haupt-/übrige Strassen Lärmkataster) |

### 2.3 Postcode felbontás & limit

- **Felbontás:** raster **10×10 m** (sonBASE számítás) + **fassadenpunkt** (épület-homlokzat). Nincs PLZ-aggregált CSV → **pont-lekérdezés** kell: `api3.geo.admin.ch/rest/services/api/MapServer/identify` adott LV95 koordinátára → visszaad `Lr_tag`/`Lr_nacht` dB(A) sávot.
- **Frissesség:** modell 2015-ös bázis, 2021 count-okkal frissítve, de 2025-08-04-es dataset-update csak meta. **Nem napi.**
- **Jogi disclaimer:** „Berechnungen sind nicht rechtsverbindlich" — hatóság (FEDRO/kanton) az autoritatív.

---

## 3) ARE ÖV-Güteklassen — Public transport quality

### 3.1 opendata.swiss

| Mező | Érték |
|---|---|
| **Dataset** | ÖV-Güteklassen ARE |
| **URL** | `https://opendata.swiss/de/dataset/ov-guteklassen-are1` (EN: `/en/dataset/ov-guteklassen-are1`) |
| **Publisher** | Bundesamt für Raumentwicklung ARE |
| **Änderung** | **2025-03-20** |
| **Intervall** | **Jährlich** (GTFS/Hafas Fahrplan-ból automatizált számítás) |
| **Räumlich** | Schweiz |
| **Licence** | terms_by (ARE OGD) |
| **További opendata lap** | `ov-gueteklassen1` / `ov-gueteklasse4` (régebbi/kanton-variánsok) |

**Resszursok a lapon:**

| Formátum | Zugangs-URL |
|---|---|
| **API (REST)** | `https://api3.geo.admin.ch/rest/services/api/MapServer/ch.are.gueteklassen_oev` (Identify + legend + query) |
| **WMS-BGDI** | Layer `ch.are.gueteklassen_oev` — `https://wms.geo.admin.ch/` |
| **WMTS-BGDI** | `https://wmts.geo.admin.ch/EPSG/3857/1.0.0/WMTSCapabilities.xml?lang=de` → `ch.are.gueteklassen_oev` |
| **Download (data.geo.admin.ch)** | `https://data.geo.admin.ch/browser/index.html#/collections/ch.are.gueteklassen_oev` (STAC/browser, GPKG/SHP/GeoJSON) |
| **Doku** | `https://www.are.admin.ch/de/ov-erschliessung` + Methodik-PDF `oev-gueteklassen-berechnungsmethodikare.pdf` |

### 3.2 geocat.ch

- Geocat record **61a79435-b986-495e-b3ea-fe97c4abd558** (ARE ÖV-Güteklassen, Vektor, Maßstab 1:100 000, Sprache DE, Datum 2026-01-21). Alternatív kanton-variáns: `ch_ag_geo_avk_oevgueteklassen` (AGIS, Aargau).

### 3.3 Postcode felbontás

- **Hivatalos osztályok:** A (sehr gut) > B > C > D > (E/F kantonban) > `none` (nem erschlossen). ARE országos csak A–D-t publikál.
- **Geometria:** vektor poligonok (Areal + Haltestellen-Puffer), **nincs PLZ-CSV**. Lekérdezés: **point-in-polygon** via `api3 Identify` (lat/lon → LV95 → Identify) → vissza `gueteklasse`. Aggregáláshoz: postcode-poligon metszés lokálisan (GPKG letöltés + Turf/SpatiaLite).
- **Frissesség:** évi GTFS-számítás, március körüli publikáció (2025-03-20 igazolt).

---

## 4) BFS GWR Gebäude — Eidg. Gebäude- und Wohnungsregister

### 4.1 Nemzeti GWR (BFS)

| Mező | Érték |
|---|---|
| **Dataset (geo.admin.ch layer)** | Eidg. Gebäude- und Wohnungsregister: Gebäudestatus |
| **opendata.swiss ID** | `56553efe-4a2c-449d-93ba-cf7edd518d56@bundesamt-fur-statistik-bfs` (BFS) |
| **opendata URL** | `https://opendata.swiss/de/dataset/eidg-gebaude-und-wohnungsregister-gebaudestatus` |
| **Publisher** | Bundesamt für Statistik BFS (`info@bfs.admin.ch`) |
| **Publikáció / Änderung** | 2005-01-01 / 2017-07-01 (Totalrevision VGWR) |
| **Intervall** | **Jährlich** (layer) — de operatívan **laufend nachgeführt** (VGWR Art.10: Bauamt meld napi) |
| **geo.admin.ch layer** | `ch.bfs.gebaeude_wohnungs_register` — `https://api3.geo.admin.ch/rest/services/api/MapServer/ch.bfs.gebaeude_wohnungs_register/legend?lang=de` · Massstab 1:5 000–1:1 000 001 · **Datenstand 2026-07-12** (élő legend) |
| **WMS** | `https://wms.geo.admin.ch/?LAYERS=ch.bfs.gebaeude_wohnungs_register` |
| **Licence** | **Stufe A public** — „öffentlich, ohne Einschränkung verwendbar" (VGWR). OGD terms_by. |
| **Merkmalskatalog** | `https://www.housing-stat.ch/files/881-2200.pdf` (Katalog 4.2) + online `https://www.housing-stat.ch/de/help/42.html` · Weisung AV/GWR `.../1754-2300.pdf` · Rechtsgrundlage `https://www.fedlex.admin.ch/eli/cc/2017/376/de` |

**Mit tartalmaz (Stufe A):** EGID/EWID/EDID/EPROID, Adresse + LV95 koordináta, PLZ/Ortschaft, Gemeinde (BFS-Nr), Baujahr, Geschosse, Heizungsart, Wohnungsmerkmale (Zimmer, Fläche) stb.

### 4.2 Kanton-daily CSV (konkrét, letölthető)

| Mező | Érték |
|---|---|
| **Dataset** | Gebäude (Gebäude- und Wohnungsregister GWR) |
| **ID** | `100230@kanton-basel-stadt` |
| **URL** | `https://opendata.swiss/de/dataset/gebaude-gebaude-und-wohnungsregister-gwr` → `https://data.bs.ch/explore/dataset/100230/` |
| **Publisher** | Statistisches Amt BS (`opendata@bs.ch`) |
| **Änderung** | **2026-08-18** |
| **Intervall** | **Täglich** |
| **Resszurs** | CSV/JSON via `data.bs.ch/api/v2/catalog/datasets/100230/exports/...` |
| **Licence** | terms_by |

> ZH analógia: OGD ZH WFS `https://wfs.zh.ch/OGDZH_WFS?...&TYPENAME=...` — hasonló daily, de külön endpoint.

### 4.3 Direkt GWR hozzáférés (nem OGD-böngésző)

- **housing-stat.ch** `https://www.housing-stat.ch/de/data/supply/public.html` — public dump-ok
- **BFS GWR Web Services (SOAP)** — `getBuildingById` / `getConstructionProject` (VGWR Web Services PDF, `swSecurityType` + `EGID`). **Auth-köteles**, nem OGD-public → pilotra nem ajánlott.
- **Fassadenpunkt vs GWR:** GWR = épület-nyilvántartás (admin), sonBASE facade = zaj-modell — két külön pipeline.

### 4.4 Postcode felbontás

- **Épület-szint LV95 + PLZ** → tökéletesen aggregálható postára: `SELECT plz, COUNT(*) FROM gwr GROUP BY plz` → `PlaceInfo.gwr_building_count` építhető.
- Frissesség: **napi** (BS-csv) vagy **2026-07-12 Datenstand** (geo.admin.ch). A BFS éves „konszolidált" kiadás mellett a laufend Nachführung a valós frissesség.

---

## 5) 3 opció összevetése (1–5, 5 = legjobb)

| Kritérium (súly) | A: opendata.swiss direkt CSV/JSON (CKAN + Opendatasoft export) | B: geocat.ch WMS/WFS + data.geo.admin.ch STAC + api3 Identify | C: hard scrape BFS/BAFU/ARE/ESTV portál (data.bl.ch, bafu.admin.ch, are.admin.ch, bfs.admin.ch, mysalario) |
|---|---|---|---|
| **Aktualitás / frissesség** | 3 — BL 2026-07-23 évi, BS napi, ARE 2025-03, BAFU 2015 modell | 5 — geo.admin.ch **2026-07-12** Datenstand (GWR) + ARE 2025-03 + WMS live | 2 — scrape törékeny, nincs SLA, HTML-változás töri |
| **Postcode felbontás** | 2 — Steuer: nincs PLZ (Gemeinde-match kell); Lärm: nincs CSV; GWR: csak BS-CSV-ben van PLZ | 4 — Identify **pont-lekérdezés** (Lärm dB, ÖV A–D) + GWR WFS-ben van PLZ; BS-daily-vel 5 is lehet | 3 — scrape tud PLZ-t, de nem normalizált (Gemeinde-nevek ékezettel) |
| **Formátum / schema stabilitás** | 3 — Opendatasoft CSV stabil, de CKAN `package_show` **403** (nginx WAF) — API törékeny | 5 — OGC WMS/WMTS + STAC GPKG/GeoJSON **szabványos**, api3 JSON stabil | 1 — HTML-scrape a leginstabilabb (évente törik) |
| **Licence egyértelműség** | 4 — terms_by / CC-BY egyértelmű minden OGD-lapon | 5 — VGWR Stufe A + ARE/BAFU OGD explicit, geocat meta licence mezővel | 2 — mysalario/comparis másodlagos licenc, BAFU disclaimer |
| **Implementációs költség (fordított: olcsó=5)** | 4 — egy `httpx` CSV-fetch, de **26 kanton-CSV** kellene országosra | 3 — LV95 konverzió + Identify + GPKG cache + WMS overlay (közepes) | 1 — per-kanton parser + anti-bot + HTML-változás-követés (drága) |
| **Rate limit / megbízhatóság** | 3 — Opendatasoft throttling, CKAN 403 | 5 — geo.admin.ch CDN, magas kvóta, WMTS cache | 2 — IP-ban esély, nincs retry-header |
| **ZH pilotra alkalmasság** | 2 — csak TG/BL/ZG ZH-ra nem vetíthető | 5 — **azonnal megy ZH-ra** (GEWIJZ ZH WFS + ARE + BAFU WMS) | 3 — ZH városi OGD-t jól scrapeli, de országos nem skáláz |
| **Össz-pont (átlag)** | **3.0** | **4.6** | **2.0** |

**Jelmagyarázat:** 1 = használhatatlan, 3 = közepes/korlátos, 5 = kiváló. A súlyozást a pilotra hegyeztem (ZH postcode → azonnali érték).

### Ajánlás

1. **Elsőnek B (geocat/WMS/WFS) — nyerő.** Egyetlen architektúra fedi mind a 4-et ZH-ra: `PlaceService` LV95-re konvertál (Swisstopo `type=locations` már van), majd 3 parallel Identify (GWR WFS count, BAFU Lärm, ARE ÖV) + egy kanton-CSV (Steuerfuss ZH). Frontend: MapLibre WMS-overlay (Lärm + ÖV) + popup `PlaceInfo`.
2. **A kiegészítő, nem főcsapás.** Steuerfuss-nál nincs jobb opendata-CSV ZH-ra mint a ZH-OGD (nem az országos CKAN). Lärm-ra és ÖV-re A eleve nem ad CSV-t.
3. **C csak fallback/backfill.** mysalario 2026 aggregátor jó validálásra, de nem primary (licence másodlagos, HTML-törékeny).

**Konkrét ZH pilot mapping:**

- `steuerfuss_percent`: OGD ZH `data.stadt-zuerich.ch` (Steuerfüsse ZH) CSV → `BFS-Nr → PLZ` join (POST PLZ). Ha nincs ZH-CSV, fallback `mysalario`/BL-minta (dev-only).
- `noise_db_day`: `api3 Identify ch.bafu.larm-strassenlaerm_tag @ LV95` → dB sáv → `PlaceInfo.noise_db_day` (sávközép). WMS overlay a térképen.
- `oev_class`: `api3 Identify ch.are.gueteklassen_oev @ LV95` → A/B/C/D/none → `OeVGueteklasse`.
- `gwr_building_count`: `WFS ch.bfs.gebaeude_wohnungs_register?bbox=PLZ-bbox` vagy `data.bs.ch` minta alapján ZH-WFS count; Datenstand 2026-07-12 validált.

---

## 6) Következő lépés (NE kódolj — de ADR-nek előkészítve)

- [ ] **ADR-002 Place kiegészítés:** B opció elfogadása ZH pilotra, A/C elvetése indoklással (fenti tábla).
- [ ] **Kártyák:** `feat: Place OGD kliensek (Steuer ZH-CSV + BAFU Identify + ARE Identify + GWR WFS) — ZH pilot` → `place_service.py` stub csere Protocol-DI-vel (minta: `swisstopo_service.py`, `amtsblatt_service.py`).
- [ ] **Validálás:** élő Identify próba 8004-re (Langstrasse): ÖV=A várható, Lärm >60 dB, GWR count >3000 (stub egyezés check).

## Források (élő ellenőrzés 2026-08-26)

- Steuer BL: `https://opendata.swiss/de/dataset/steuerfusse-und-steuersatze-nach-gemeinde-und-jahr-ab-1975` + export `https://data.bl.ch/api/v2/catalog/datasets/10580/exports/csv?use_labels=true` (HTML-ben igazolt 9 resource, 2026-07-23)
- Steuer TG: `https://opendata.swiss/de/dataset/gemeindesteuerfusse-der-politischen-gemeinden-kanton-thurgau1` (`sk-stat-69@kanton-thurgau`, data.tg.ch)
- Lärm Verkehr: `https://opendata.swiss/de/dataset/larmbelastung-durch-verkehr` (`ubd003701@bafu`, 2025-08-04) + `…/larmbelastung-durch-strassenverkehr-lr_tag` (`87f3f029…@bafu`, 2021-12-31) + `https://www.bafu.admin.ch/de/sonbase`
- ÖV ARE1: `https://opendata.swiss/de/dataset/ov-guteklassen-are1` (2025-03-20, jährlich, GTFS) + `https://api3.geo.admin.ch/rest/services/api/MapServer/ch.are.gueteklassen_oev` + `https://data.geo.admin.ch/browser/index.html#/collections/ch.are.gueteklassen_oev` + `https://wmts.geo.admin.ch/.../WMTSCapabilities.xml` + geocat `61a79435-b986-495e-b3ea-fe97c4abd558`
- GWR: `https://opendata.swiss/de/dataset/eidg-gebaude-und-wohnungsregister-gebaudestatus` (`56553efe…@bfs`, 2017-07-01 VGWR) + `https://opendata.swiss/de/dataset/gebaude-gebaude-und-wohnungsregister-gwr` (`100230@bs`, 2026-08-18 täglich) + `https://api3.geo.admin.ch/rest/services/api/MapServer/ch.bfs.gebaeude_wohnungs_register` (Datenstand 2026-07-12) + `https://www.housing-stat.ch` + VGWR `https://www.fedlex.admin.ch/eli/cc/2017/376/de`
- CKAN 403 megjegyzés: curl `package_show` → nginx 403 (2026-08-26 reprodukálva) — ezért B preferált.

> **Max 5 oldal:** e doc ~4.5 oldal nyomtatva (táblákkal). Részletes curl-log külön kérésre.
