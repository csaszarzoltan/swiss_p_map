# Swiss P Map — Master Roadmap & Audit Entry Point

> **Cél:** egyetlen dokumentum, ami az auditort 5 percen belül képbe hoz. Részletes tervek: lásd linkek.

- **Dátum:** 2026-08-26
- **Állapot:** Phase 1 backend + frontend scaffold KÉSZ, pusholva (`92f9345`)
- **Board:** `swiss-p-map` kanban — 6/6 task done

---

## 1. Hol tartunk (faktok)

| Réteg | Állapot | Bizonyíték |
|---|---|---|
| Docs (research/ADR/competitor) | ✅ kész | ADR-001 accepted, W35 scan, kickoff |
| Backend domain modellek | ✅ kész | `src/models/{geo,place,politics}.py` |
| Backend szolgáltatások | ✅ kész (stub adatokkal) | `src/services/*` — Swisstopo DI+mockolt httpx |
| FastAPI | ✅ fut | `/health`, `/api/v1/geo/convert`, `/api/v1/politics/representatives`, `/api/v1/place/{postcode}` |
| Tesztek | ✅ 19 passed | 12 unit + 7 E2E (TestClient) |
| Minőségkapuk | ✅ zöldek | mypy strict clean (16 file), ruff clean, compileall OK |
| CI | ✅ 2 job | backend (ruff/mypy/pytest) + frontend (npm ci/lint/build) |
| Frontend scaffold | ✅ build zöld | Next.js 14 + Tailwind + maplibre-gl, Swisstopo Light stílus, ZH HB marker |

## 2. Ami MÉG stub / mock (őszintén, audit szempontból fontos)

- **`politics_service.py`**: 2 postcode (8004, 8001) beégetett stub — PARIS-API még NINCS bekötve
- **`place_service.py`**: Steuerfuss/zaj/ÖV számok példaadatok, nem hivatalos forrásból
- **`swisstopo_service.py`**: valódi API-hívásra írt, DE tesztek mockolják; élő hívás még nem volt élesben validálva
- **Adattár nincs** — minden memóriában; PostGIS az ADR-001-ben eldöntve, de még nem épült
- **Frontend↔backend híd nincs** — a Map komponens még nem hívja az API-t
- **AI réteg (LLM összefoglalók)** — csak az ADR-ben szerepel, nulla implementáció

## 3. Következő lépések (tervek)

| Terv | Fájl | Scope | Becslés |
|---|---|---|---|
| API ↔ Map integráció | `docs/plans/2026-08-26-api-map-integration.md` | postcode keresés → Place+Politics panel a térképen | ~8 bite-sized task |
| Planning pillér (Phase 2) | `docs/plans/2026-08-26-planning-pillar-phase2.md` | Amtsblattportal API feed + ÖREB, 20 napos ablak | kutatás→ADR előfeltétel |
| Roadmap utána | — | PostGIS réteg, AI összefoglalók, országos kiterjesztés | külön ADR-ek |

## 4. Audit-checklist (mit nézzen)

1. **Módszertan betartás:** research → ADR → scaffold → RED→GREEN (git log láncolat végigkövethető)
2. **Teszt-minőség:** van-e hamis teszt? (korábban javítottuk: `test_swiss_bounds_*`) — most minden teszt valódi modult hív
3. **Stub-transparency:** a 2. szekció listája fed-e mindent?
4. **Konkurencia-pozicionálás:** W35 scan állításai (Houzy/smartconext) még aktuálisak-e?
5. **Biztonság:** jelenleg nincs auth — a stub API publikus read-only; POST endpoint nincs. Kockázat: alacsony, de az audit mondjon véleményt.
