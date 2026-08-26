# ADR-001: Technológiai Stack és Rendszerarchitektúra Kiválasztása

- **Dátum:** 2026-08-26
- **Státusz:** proposed
- **Szerző:** analyst (research: `docs/research/2026-08-26-kickoff.md`)
- **Kanban:** #swiss-p-map-001

## Kontextus
A **Swiss P Map** célja egy svájci interaktív térképes és döntéstámogató platform létrehozása, amely egyesíti a helyi építési engedélyeket (*Baugesuche*), a zónabesorolást (*ÖREB*), a környezeti/zajadatokat (*sonBASE*) és a helyi képviselői/önkormányzati információkat (*Wahlkreise, Vorstösse, PARIS-API*). A rendszernek azonnal betöltődőnek, mobilbarátnak, 60fps térkép-renderelést biztosítónak és megbízható OGD adatfolyammal ellátottnak kell lennie.

## Döntés
Az **Opció A: Modern Web App (Next.js + MapLibre GL JS + Python ETL Backend)** architektúrát választjuk az alábbi technológiai összetevőkkel:

1. **Frontend & Térképmotor:**
   - **Next.js (React / TypeScript / Tailwind CSS):** SSR/Edge képességek, beépített API route-ok, SEO és parcellaszintű megosztható linkek.
   - **MapLibre GL JS:** Hardveresen gyorsított (WebGL/WebGPU) nyílt forráskódú vektoros térképkliens, közvetlen integrációval a hivatalos Swisstopo vektoros stílusokhoz (`https://vectortiles.geo.admin.ch/styles/ch.swisstopo.lightbasemap.vt/style.json`).
2. **Backend & Adatpipeline (ETL):**
   - **Python 3.11+ (FastAPI):** Erős térinformatikai ökoszisztéma (Shapely, GeoPandas, PyProj) a svájci koordinátarendszer (LV95 / EPSG:2056 $\leftrightarrow$ WGS84 / EPSG:4326) kezelésére és az OGD API-k (Swisstopo, Zürich OGD, PARIS, Curia Vista) aszinkron szinkronizációjára.
3. **Adattár:**
   - **PostgreSQL + PostGIS:** Térbeli indexeléshez, körzet- és sugárlekérdezésekhez (*ST_DWithin, ST_Contains*). Helyi fejlesztéshez és tesztekhez: SQLite + SpatiaLite vagy mock GeoJSON.
4. **AI Réteg:**
   - LLM Provider Gateway (Claude / Gemini) egyszerű nyelvi összefoglalók és többnyelvű fordítások (DE, FR, IT, EN) generálására.

## Elvetve
| Opció | Miért nem |
|---|---|
| **Mobil Natív App (Flutter / React Native)** | Magasabb kezdeti fejlesztési költség, zárt app store jóváhagyások, nehézkes linkmegosztás és alacsonyabb azonnali elérés a lakosság számára. |
| **Mapbox GL JS (Kereskedelmi)** | Költséges licencdíj és használati korlátok; a MapLibre 100% nyílt forráskódú és natívan kompatibilis a Swisstopo stílusokkal. |
| **Leaflet / OpenLayers (Raster)** | Nem támogatja a folytonos 60fps vektoros zoomolást és a 3D épületkiemeléseket olyan teljesítménnyel, mint a WebGL-alapú MapLibre. |

## Következmény
- **Scaffold feladatok:**
  - `src/` backend és frontend mappa-struktúra kialakítása (Python modulok + Next.js kliens).
  - `tests/` keretrendszer felállítása (pytest a Python ETL logikára és API végpontokra; vitest / playwrigh a frontendhez és E2E-hez).
  - CI workflow (`.github/workflows/ci.yml`) szintaxis- és teszt-ellenőrzéssel.
- **Fejlesztői fókusz:** Max 3 fájl / lépés szabály betartása, RED $\rightarrow$ GREEN tesztvezérelt megvalósítás.
- **Validáció:** Unit tesztek a koordináta-konverzióra és OGD parserekre + E2E teszt a térkép és a kereső működésére.

## Kapcsolódó
- Research: `docs/research/2026-08-26-kickoff.md`
- Kód: `src/`, `tests/`
- Következő ADR: `docs/decisions/ADR-002-data-ingestion-pipeline.md`
