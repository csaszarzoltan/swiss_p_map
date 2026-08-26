# Swiss P Map

> **„A svájci környék egyetlen térképén”** — Integrált interaktív döntéstámogató térkép a helyi politika, életminőség és épített környezet metszetében.

## Áttekintés

A **Swiss P Map** egyesíti a svájci nyílt kormányzati adatokat (**Open Government Data - OGD**):
- **Politics (MVP Fázis 1):** Választókerületi képviselők (*Gemeinderat / Kantonsrat / Nationalrat*), parlamenti indítványok (*Vorstösse*), lobbi-összeférhetetlenségek (*Lobbywatch*), helyi szavazások (*Abstimmungen*).
- **Place & Property (MVP Fázis 1):** Községi adókulcs (*Gemeindesteuerfuss*), zajterhelési térkép (*sonBASE*), tömegközlekedési minőség (*ÖV-Güteklassen*), épületregiszter (*GWR*).
- **Planning (Fázis 2):** Áramló 20 napos építési engedélykérelmek (*Amtsblattportal / eAuflageZH*), fellebbezési visszaszámláló (*Einsprachefrist*) és zónabesorolás (*ÖREB*).

---

## Architektúra & Stack (ADR-001)

- **Frontend:** Next.js (React / TypeScript / Tailwind CSS) + **MapLibre GL JS** (hardveresen gyorsított WebGL vektoros térképkliens, 60fps)
- **Térképréteg:** Hivatalos **Swisstopo Vector Tiles** (`vectortiles.geo.admin.ch`)
- **Backend & Geodata ETL:** Python 3.11+ (FastAPI, PyProj, Shapely a svájci LV95 $\leftrightarrow$ WGS84 konverzióhoz)
- **Adattár:** PostgreSQL + PostGIS (térbeli indexeléshez és sugaras lekérdezésekhez)
- **AI Réteg:** Claude / Gemini API a képviselői indítványok és helyi ügyek közérthető lakossági összefoglalására (DE, FR, IT, EN)

---

## Mappastruktúra

```
swiss_p_map/
├── .agent-pipeline/          # Agent vezérelt specifikációs és E2E pipeline
│   ├── 00_index/manifest.json
│   ├── 02_specs/pending/     # SPEC-001 részletes specifikáció
│   └── 03_e2e_suites/        # Feketedobozos API/GUI E2E tesztek
├── docs/
│   ├── competitor/           # W35 heti versenytárs scout (Houzy, smartconext)
│   ├── decisions/            # ADR-001 stack döntés
│   └── research/             # Kickoff domain elemzés
├── tests/                    # Unit és integrációs tesztcsomag
│   ├── conftest.py
│   ├── test_pipeline_manifest.py
│   └── unit/
├── .github/workflows/ci.yml  # GitHub Actions CI workflow
├── AGENTS.md                 # Agent belépési szabályok
├── METHODOLOGY.md            # Kódolási és minőségi irányelvek
└── pyproject.toml            # Python projekt & teszt konfiguráció
```

---

## Fejlesztés és Tesztelés

```bash
# Függőségek telepítése
pip install -r requirements.txt

# Tesztek futtatása (pytest)
pytest -v
```
