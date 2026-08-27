# Research — ÖREB élő: ZH WFS + geo.admin ch.vd.oereb 400

- **Dátum:** 2026-08-27 (folytatás)
- **Szerző:** researcher (standing goal folytatás)
- **Státusz:** draft → ADR-007 követő (nincs új ADR, mert ÖREB már ADR-007 scope de 400 miatt wiring bukott)
- **Kapcsolódik:** `src/services/place_service.py` (oereb null 8004-en), `ADR-007`, `2026-08-27-ort-expansion`
- **Kérdés:** Miért `oereb_zone null 8004?live` miközben ZH WFS + geo.admin él?

---

## 1. Élő mérés (curl 2026-08-27, 5 hívás)

| Kísérlet | Eredmény |
|---|---|
| **A: api3 Identify ch.vd.oereb LV95 2683000,1248000** | `400 No GeoTable was found for ch.vd.oereb` |
| **B: api3 Identify ch.vd.oereb WGS84 8.534,47.378 sr 4326** | `400 No GeoTable was found for ch.vd.oereb` — **layer nem létezik api3-on** |
| **C: WMS GetCapabilities wms.geo.admin.ch** | `ch.swisstopo-vd.stand-oerebkataster` létezik (Verfügbarkeit, nem zone), `ch.*oereb*` 4 layer de WMS GetFeatureInfo `Invalid values for BBOX` / `Unsupported INFO_FORMAT` |
| **D: maps.zh.ch ZH WFS GetCapabilities** | **200 OK** — `<Title>ÖREB-Kataster WFS</Title>` `<Abstract>Geodienst GIS-ZH</Abstract>` `gis@bd.zh.ch`, `ServiceType WFS 2.0.0` — **ZH saját WFS él** |
| **E: place 8004?live true** | `solar 1208 sehr gut + steuer zh-steueramt-html` ok, `oereb null` — wiring előtt |

**Tanulság:** `ch.vd.oereb` **nem geo.admin api3 layer** (Vaud-only?), ZH-ra `maps.zh.ch/wfs/OerebKatasterZHWFS` a korrekt (ZH WFS 2.0.0). BE jelenleg `ch.vd.oereb` api3-at hív → 400 → `oereb null` marad (fallback, nem törés).

---

## 2. Hibaelemzés

- `place_service.py` 280: `ch.vd.oereb` api3 Identify → mindig 400 → `oereb_zone None` marad (honest fallback, Ort panel `—` mutat, nem hazudik)
- ZH WFS `https://maps.zh.ch/wfs/OerebKatasterZHWFS?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=...&BBOX=2683000,1248000,2683100,1248100` kell (WFS GetFeature, nem Identify)
- Következő lépés: ZH WFS wiring vagy `ch.swisstopo-vd.stand-oerebkataster` availability check (de zone nem jön belőle)

---

## 3. Javaslat (következő kör, 1 commit, max 3 file)

| Változtatás | Hol |
|---|---|
| **A: ZH WFS GetFeature** | `place_service.py`: `POST maps.zh.ch/wfs/OerebKatasterZHWFS` → `TYPENAMES Nutzungsplanung` + `BBOX LV95 100m` → parse zone `Wohnzone W2` |
| **B: Fallback** | 400→null fallback marad, Ort `—` + `oerebDesc` valid, E2E nem törik |

Elhalasztva: ez a kör a research, kód a következő `folytasd`-ra (mert 1 commit per kör szabály + solar fix volt a mostani). ÖREB null honest, nem blokkol.

---

## 4. Források (élő, 2026-08-27)

1. `api3 ch.vd.oereb 400 No GeoTable` — curl 2026-08-27
2. `WMS ch.swisstopo-vd.stand-oerebkataster` — GetCapabilities 2026-08-27
3. `maps.zh.ch WFS ÖREB 200 OK` — GetCapabilities WFS 2.0.0 2026-08-27
4. `place 8004?live solar 1208 oereb null` — BE 8310 validált
