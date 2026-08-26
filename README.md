# Swiss P Map

> **„A svájci környék egyetlen térképén”** — Integrált interaktív döntéstámogató térkép a helyi politika, életminőség és épített környezet metszetében.

## Áttekintés

A **Swiss P Map** egyesíti a svájci nyílt kormányzati adatokat (**Open Government Data - OGD**):
- **Politics (MVP Fázis 1 — kész):** Választókerületi képviselők (*Wahlkreis*), `GET /api/v1/politics/representatives?postcode=8004`
- **Place & Property (MVP Fázis 1 — kész):** Adókulcs, zaj, ÖV-Güteklassen, `GET /api/v1/place/{postcode}`
- **Geo (kész):** LV95 ↔ WGS84 konverzió, Swisstopo search, `GET /api/v1/geo/convert?easting=&northing=`
- **Planning (Fázis 2):** Áramló 20 napos építési kérelmek (*Amtsblattportal / eAuflageZH*), *ÖREB* zónák

---

## Architektúra & Stack (ADR-001)

- **Backend:** Python 3.11+ (FastAPI, Pydantic, PyProj, Shapely) — kész
- **Frontend:** Next.js 14 + MapLibre GL JS (Swisstopo Light `vectortiles.geo.admin.ch`) — kész
- **Adattár (tervezett):** PostgreSQL + PostGIS
- **AI Réteg (tervezett):** Claude / Gemini — képviselői indítványok közérthető összefoglalója

---

## Mappastruktúra

```
swiss_p_map/
├── src/
│   ├── main.py                 # FastAPI app (CORS: localhost:3000)
│   ├── models/geo.py|place.py|politics.py
│   └── services/geo_converter.py|swisstopo_service.py|politics_service.py|place_service.py
├── frontend/
│   ├── src/app/Map.tsx         # MapLibre + Swisstopo Light, flyTo lngLat
│   ├── src/app/SearchPanel.tsx # PLZ vagy szabad szöveg (audit A)
│   ├── src/app/postcode_coords.ts # Swisstopo SearchServer élő geokódolás
│   └── src/lib/api.ts          # típusos fetch wrapper
├── tests/
│   ├── conftest.py
│   ├── unit/test_geo_converter.py|test_domain_models.py|test_swisstopo_service.py
│   └── e2e/test_core_e2e.py
├── docs/
│   ├── decisions/ADR-001-stack-and-architecture.md
│   ├── research/2026-08-26-kickoff.md
│   └── competitor/2026-W35-scan.md
├── .github/workflows/ci.yml
├── AGENTS.md / METHODOLOGY.md / workflows/principles.md
└── pyproject.toml
```

> Nincs `.agent-pipeline/` — a lean módszertan kanban boardon + ADR-en + research-ön alapul. A pipeline (`01_requirements`→`02_specs`→`06_e2e_discovery`) csak 20+ feature-nél / audit-igénynél kell; akkor hozd vissza külön.

---

## Fejlesztés és Tesztelés

```bash
pip install -r requirements.txt
pytest -v          # 20 passed (unit + e2e, CORS preflight)
mypy src tests --ignore-missing-imports
ruff check src tests

# Backend lokálisan
uvicorn src.main:app --reload --port 8000
# → http://127.0.0.1:8000/docs  (Swagger)
# → http://127.0.0.1:8000/health

# Frontend lokálisan (külön terminál)
cd frontend && npm run dev
# → http://localhost:3000  (kereső: 8004 vagy Bahnhofstrasse 10 — audit A)
```

## Kanban

Board: `swiss-p-map` (`hermes kanban --board swiss-p-map ls`) — 6 done (geo models, swisstopo, politics+place+API, frontend scaffold, map component).

## API ↔ Map Integration (2026-08-26)

6 task (CORS → API client → SearchPanel szabad szöveg → fly-to → élő geokódolás → füstteszt) — `docs/plans/2026-08-26-api-map-integration.md` — végrehajtva, audit A/B/C beépítve.
