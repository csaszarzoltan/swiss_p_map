# Swiss P Map — Master Roadmap & Audit Entry Point

> **Cél:** egyetlen dokumentum, ami az auditort 5 percen belül képbe hoz. Részletes tervek: lásd linkek.

- **Dátum:** 2026-08-26
- **Állapot:** Phase 1 KÉSZ + API↔Map integráció végrehajtva (`aa634ac`) + Planning kutatás/ADR-002 proposed (`ae2099f`)
- **Board:** `swiss-p-map` kanban — 6 done + 1 blocked (ADR-002 jóváhagyásra vár)

---

## 1. Hol tartunk (faktok)

| Réteg | Állapot | Bizonyíték |
|---|---|---|
| Docs (research/ADR/competitor) | ✅ kész | ADR-001 accepted, W35 scan, kickoff, **ADR-002 proposed** |
| Backend domain modellek | ✅ kész | `src/models/{geo,place,politics}.py` |
| Backend szolgáltatások | ✅ kész (stub adatokkal) | `src/services/*` — Swisstopo DI+mockolt httpx |
| FastAPI | ✅ fut | `/health`, geo/convert, politics, place + **CORS env-állítható** |
| Tesztek | ✅ **23 passed** | 12 unit (+3 CORS cfg) + E2E (+1 preflight) |
| Minőségkapuk | ✅ zöldek | mypy strict clean (17 file), ruff clean |
| CI | ✅ 2 job | backend (ruff/mypy/pytest) + frontend (npm ci/lint/build) |
| Frontend | ✅ **integrálva** | kereső (PLZ/szabad szöveg) → panel + fly-to marker, élő Swisstopo geokódolás |
| Élő füst | ✅ bizonyított | uvicorn 8310 (/health, /place, /politics, CORS) + FE 3310 (HTML OK) |

## 2. Ami MÉG stub / mock (őszintén, audit szempontból fontos)

- **`politics_service.py`**: 2 postcode (8004, 8001) beégetett stub — PARIS-API még NINCS bekötve
- **`place_service.py`**: Steuerfuss/zaj/ÖV számok példaadatok, nem hivatalos forrásból
- **`swisstopo_service.py`** (backend): tesztek mockolják; élő Swisstopo hívás egyelőre a frontend geokódolásban fut (`postcode_coords.ts`)
- **Adattár nincs** — minden memóriában; PostGIS az ADR-001-ben eldöntve, de még nem épült (ADR-002: SQLite MVP)
- **AI réteg (LLM összefoglalók)** — csak az ADR-ben szerepel, nulla implementáció
- **Planning pillér** — kutatás kész, ADR-002 **proposed**; kód CSAK jóváhagyás után

## 3. Következő lépések (tervek)

| Terv | Fájl | Scope | Becslés |
|---|---|---|---|
| ~~API ↔ Map integráció~~ | `docs/plans/2026-08-26-api-map-integration.md` | ✅ VÉGREHAJTVA (`aa634ac`) | done |
| Planning pillér (Phase 2) | `docs/plans/2026-08-26-planning-pillar-phase2.md` | Task 0 kutatás ✅ + ADR-002 proposed → **jóváhagyásra vár** | gate |
| Roadmap utána | — | ÖREB M2M (ADR-003), OGD 2982 backfill, Audit-C live OGD, AI összefoglalók | külön ADR-ek |

## 4. Audit-checklist (mit nézzen)

1. **Módszertan betartás:** research → ADR → scaffold → RED→GREEN (git log láncolat végigkövethető)
2. **Teszt-minőség:** van-e hamis teszt? (korábban javítottuk: `test_swiss_bounds_*`) — most minden teszt valódi modult hív
3. **Stub-transparency:** a 2. szekció listája fed-e mindent?
4. **Konkurencia-pozicionálás:** W35 scan állításai (Houzy/smartconext) még aktuálisak-e?
5. **Biztonság:** jelenleg nincs auth — a stub API publikus read-only; POST endpoint nincs. Kockázat: alacsony, de az audit mondjon véleményt.
