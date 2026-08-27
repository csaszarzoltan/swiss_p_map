# Research — Solar élő fix: BFE WGS84 + LV95 koordináta + mstrahlung parser

- **Dátum:** 2026-08-27 (folytatás)
- **Szerző:** researcher (standing goal folytatás)
- **Státusz:** draft → ADR-007 követő hotfix (nincs új ADR, mert ADR-007 már decided)
- **Kapcsolódik:** `src/services/place_service.py` (273→310 sor, solar null 8004-en), `docs/research/2026-08-27-ort-expansion-sonnendach-oereb.md`, `ADR-007`, `ADR-008`
- **Kérdés:** Miért `solar_kwh_m2 null 8004?live` miközben `api3 geo.admin.ch` él (klasse 4 93kWh)?

---

## 1. Élő mérés (curl 2026-08-27, 4 hívás)

| Kísérlet | URL (Identify) | Eredmény |
|---|---|---|
| **A: LV95 2683000,1248000 + layer ch.bfe.solarenergie-eignung-daecher** | `geometry=2683000,1248000 geometryType=esriGeometryPoint layers=all:ch.bfe... tolerance=0` | `featureId -99 + bbox HUGE` (országos vektor), `attributes üres` → **nem pont-lekérdezés** |
| **B: WGS84 8.517,47.392 + sr=4326 + tolerance=10** | `geometry=8.517,47.392 sr=4326 tolerance=10` | `featureId 17732445 + bbox tető-poligon 483m²` + `attributes {klasse 4, stromertrag 93959, mstrahlung 1214, flaeche 483.7, ausrichtung -180}` → **hit** |
| **C: WMS GetCapabilities** | `SERVICE=WMS GetCapabilities` | `ch.bfe. ...` 15 layer lista, solar nem külön WMS hanem `api` MapServer topic |
| **D: BFE WGS84 LV95 nélkül** | `geometry=2683000,... sr=2056` | országos feature, nem tető → **LV95 nem jó BFE-hez** |

**Tanulság:** BFE Solar Identify **WGS84-et vár** (EPSG:4326, `geometry lon,lat + sr=4326 + tolerance 10`), nem LV95-öt. LV95 hívás országos -99 feature-t ad, WGS84 ad tető-poligont. `api3 geo.admin.ch` doc: `sr` param a `geometry`-hoz tartozik, nem a `mapExtent`-hoz.

Validálva: `klasse 4 (= sehr gut, top 25%)`, `stromertrag 93959 kWh/év ≈ 194 kWh/m² × 483m²`, `mstrahlung 1214 kWh/m²/év` (= **kwh_m2**), `flaeche 483.7 m²`, `ausrichtung -180°` (= dél). Ezek `solar_kwh_m2` + `solar_class` mezők.

---

## 2. Hibaelemzés

- `place_service.py` 235: `ch.bfe.solarenergie-eignung-daecher` most `API3_IDENTIFY` + LV95 `geometry=easting,northing` → BFE nem tető-poligont ad, parser `kwh_m2` null → `solar_kwh_m2 None` marad
- Parser 108: `kwh_m2` + `strahlung` + `mstrahlung` próbálja, de LV95 válaszban `attributes {}` → egyik sincs
- 8004 élő `place?live=true` ezért `solar None` — a többi réteg (ARE/BAFU/zh.ch) ok

---

## 3. Fix (1 commit, max 3 file, research→kód)

| Változtatás | Hol |
|---|---|
| **A: WGS84 konverzió + sr=4326 + tolerance 10** | `place_service.py` 235: `lon,lat = lv95_to_wgs84(easting, northing)` → `geometry=f"{lon},{lat}"` + `params.sr=4326, tolerance=10, mapExtent` WGS84 |
| **B: Parser bővítés** | `_parse_solar`: `mstrahlung` + `stromertrag/flaeche` + `klasse int 1-4` → `solar_class` mapping (`4→sehr gut`) |
| **C: ZH Steuerfuss fallback sorrend** | ZH HTML már zöld (119 zh-steueramt-html) — ne törjön, `try/except` marad |

`test_place_ort_expansion.py` WGS84 mock frissítése (geometry param ellenőrzés), `test_planning_refresh.py` érintetlen.

---

## 4. Források (élő, 2026-08-27)

1. `api3 geo.admin.ch BFE WGS84 hit: klasse 4 stromertrag 93959 mstrahlung 1214` — curl WGS84 8.517,47.392
2. `api3 geo.admin.ch LV95 miss: -99 országos bbox` — curl LV95 2683000,1248000
3. `WMS BGDI GetCapabilities + search solar` — curl 2026-08-27
4. `BE 8310 place 8004?live=true solar None ZH 119` — validált 2026-08-27
