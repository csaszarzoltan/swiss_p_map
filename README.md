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
├── docs/
│   ├── decisions/            # ADR-döntések (ADR-000-template.md)
│   ├── research/             # Kutatások (kickoff + scout)
│   └── competitor/           # Heti versenytárs-scout jegyzetek
├── tests/                    # Tesztek (keretrendszer: amit az ADR-001 választ)
│   ├── conftest.py
│   └── unit/
├── .github/workflows/ci.yml  # GitHub Actions (az ADR-001 után)
├── AGENTS.md                 # Agent belépési szabályok
├── METHODOLOGY.md            # Kódolási és minőségi irányelvek
└── pyproject.toml            # Projekt & teszt konfiguráció (ADR-001 után)
```

> Nincs `.agent-pipeline/` — a lean módszertan kanban boardon + ADR-en + research-ön alapul. A pipeline (`01_requirements`→`02_specs`→`06_e2e_discovery`) csak 20+ feature-nél / audit-igénynél kell; akkor hozd vissza külön.

---

## Fejlesztés és Tesztelés

```bash
# Függőségek telepítése
pip install -r requirements.txt

# Tesztek futtatása (pytest)
pytest -v
```
