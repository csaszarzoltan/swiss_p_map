# Swiss P Map

> **„A svájci környék egyetlen térképén”** — Integrált interaktív döntéstámogató térkép a helyi politika, életminőség és épített környezet metszetében. 4 nyelven: **de / en / fr / it**.

## Áttekintés

A **Swiss P Map** online scrapeli a svájci nyílt kormányzati adatokat (**OGD**):

- **Politics:** Választókerületi képviselők (*Wahlkreis → Nationalrat*), PARIS-API CQL (`?live=true` → `GET /api/v1/politics/representatives?postcode=8004`)
- **Ort / Place (6 csempe):** Steuerfuss (zh.ch HTML 119%), Lärm sonBASE, ÖV-Güteklasse ARE, GWR Gebäudezahl, **Sonnendach** BFE WGS84 (`1208 kWh/m² sehr gut`), **ÖREB** ZH WFS Nutzungsplanung (`Kernzone`) — `GET /api/v1/place/{postcode}?live=true`
- **Planung:** 20 napos Baugesuche (Amtsblattportal XML 1.24/1.26 + SQLite WAL), `GET /api/v1/planning/baugesuche?postcode=8004` + `POST /api/v1/planning/refresh`
- **KI-Zusammenfassung:** 2 mondat, 4 nyelven, llm-budget-gateway `8013` → fallback sablon (`POST /api/v1/ai/summary`)
- **Resident-first civic (SPEC-045/047/051…054/058 — IMPLEMENTED):** `LocalInformationHub` i18n + a11y tablist (`GET /api/v1/local/briefing`), `VotingVisualCard` (`GET /api/v1/votes/proposals` + `/{id}/analysis`), `WeatherVisualWidget` live Open-Meteo (`GET /api/v1/weather/current|forecast|alerts|water-temperatures`), `WasteCalendarVisual` + valós `.ics` (`GET /api/v1/municipal/waste-calendar[.ics]`), `CostOfLivingCalculator` breakdown + `size_m2` (`GET /api/v1/costs/assessment`), Amtsblatt hír-pipeline (`POST /api/v1/connectors/amtsblatt/ingest`, `GET /api/v1/news/local`)
- **Geo:** LV95 ↔ WGS84 (`GET /api/v1/geo/convert`), Swisstopo Search geokódolás
- **i18n:** `next-intl 3.26.5`, `localePrefix: always`, `de` default, hreflang/sitemap

## Architektúra & Stack (ADR-001…022)

- **Backend:** Python 3.11+ (FastAPI, Pydantic, httpx) — `src/main.py` **51 route**, `src/services/*` (civic: `local_information`, `local_news`, `weather_climate`, `cost_of_living`, `municipal`, `vote_analysis`, connectorok: `meteoswiss`, `bfs_voteinfo`, `sbb_transport`, `amtsblatt_news_pipeline` + `newsletter`, `web_push`)
- **Frontend:** Next.js 14 App Router (TS strict) + next-intl + Tailwind + Three.js 0.160 + MapLibre Light + swiss-maps TopoJSON + gsap
- **Adattár:** SQLite WAL (`data/swisspm.db` — 22k Baugesuche + daily poll), PostGIS később külön ADR
- **AI:** llm-budget-gateway `8013` (cooldown `502 ai_unavailable` → sablon)

## API (BE `8310`)

| Method | Path | Live |
|---|---|---|
| GET | `/health` | — |
| GET | `/api/v1/geo/convert?easting=&northing=` | — |
| GET | `/api/v1/politics/representatives?postcode=&live=` | PARIS CQL |
| GET | `/api/v1/place/{postcode}?live=` | ARE/BAFU/BFE+ZH WFS+zh.ch |
| GET | `/api/v1/planning/baugesuche?postcode=&active_only=` | SQLite 22k |
| POST | `/api/v1/planning/refresh` `{"canton":"ZH"}` | Amtsblatt XML |
| POST | `/api/v1/planning/backfill` | OGD 2982 CSV — 22k |
| POST | `/api/v1/ai/summary` `{"locale","postcode","place","politics","baugesuche"}` | gateway 8013 |
| GET | `/api/v1/local/briefing?postcode=` | LocalInformation (045) |
| GET | `/api/v1/votes/proposals` + `/{id}/analysis` | VoteAnalysis (051) |
| GET | `/api/v1/news/local?postcode=` | Amtsblatt pipeline (047/058) |
| GET | `/api/v1/weather/current|forecast|alerts|water-temperatures` | Open-Meteo live (052) |
| GET | `/api/v1/costs/assessment?postcode=&income_chf=&size_m2=` | CostOfLiving (054) |
| GET | `/api/v1/municipal/waste-calendar[.ics]` | Municipal (053) |

CORS: `SWISSPM_CORS_ORIGINS=http://localhost:3310,http://127.0.0.1:3310`

## Mappastruktúra

```
swiss_p_map/
├── src/
│   ├── main.py                 # FastAPI 51 route (geo/politics/place/planning/ai + civic/connectors)
│   ├── models/{geo,place,politics,planning}.py
│   ├── services/{geo_converter,place,politics,planning,amtsblatt,ogd_service,ai_summary}.py
│   ├── services/{local_information,local_news,weather_climate,cost_of_living,municipal,vote_analysis,newsletter,web_push}.py
│   ├── services/connectors/{amtsblatt_news_pipeline,meteoswiss_client,bfs_voteinfo_client,sbb_transport_client}.py
│   └── db/planning_repo.py     # SQLite WAL upsert_many
├── frontend/
│   ├── src/app/[locale]/page.tsx  # Übersicht/Politik/Ort/Planung + civic panelek + KI-Zusammenfassung
│   ├── src/components/civic/{VotingVisualCard,WeatherVisualWidget,WasteCalendarVisual,CostOfLivingCalculator}.tsx
│   ├── src/components/LocalInformationHub.tsx  # SPEC-045 i18n + a11y tablist
│   ├── src/app/Map3D.tsx       # Three.js 70° + detailOverlay + pinGroup amber stem
│   ├── src/lib/api.ts          # BASE 8310 + place/politics/planning/civic live
│   └── messages/{de,en,fr,it}.json
├── tests/{unit,e2e}
├── docs/{decisions/ADR-009*,research/ogd-backfill.md,plans/master-roadmap.md}
├── .github/workflows/ci.yml
└── pyproject.toml
```

## Fejlesztés és Tesztelés

```bash
# Backend
.venv/bin/python -m pytest tests/unit -q  # 129 passed
.venv/bin/python -m mypy src  # 47 clean
.venv/bin/python -m ruff check src tests

# Backend lokálisan (DBUS-clean)
SWISSPM_CORS_ORIGINS=http://localhost:3310,http://127.0.0.1:3310 \
  .venv/bin/python -m uvicorn src.main:app --host 127.0.0.1 --port 8310 --log-level warning
# → http://127.0.0.1:8310/docs + /health

# Frontend lokálisan
cd frontend && npm run build && npx next start -p 3310
# → http://127.0.0.1:3310/de  (/en /fr /it)
# dev: env -u DBUS_SESSION_BUS_ADDRESS -u DBUS_SYSTEM_BUS_ADDRESS npx next dev -p 3310
```

## Kanban & Docs

Board: `swiss-p-map`. Docs: 22 ADR (001…022) + SPEC-001…060 (`docs/specs/`, 7 IMPLEMENTED: 045/047/051/052/053/054/058). Master roadmap: `docs/plans/2026-08-26-master-roadmap.md`.

## Usability package
ADR-019..022 adds a thematic legend, explainable risk metadata, radius controls, and shareable locale-aware state.
