# ADR-021: Térképi Sugár-Figyelő (Radius Watcher / Watch Zone)

- **Dátum:** 2026-08-28
- **Státusz:** accepted (jövő heti backlog #3)
- **Szerző:** researcher (research: `docs/research/2026-08-28-usability-deep-dive.md` Rank #3, kickoff MVP sugár-elemző)
- **Kanban:** #swiss-p-map-021 — P1 | Epic: Planning térbeli

## Kontextus

A Planning sugárszolgáltatás (`GET /api/v1/planning/radius?lat&lon&radius_m`) és a bbox nézeti lekérdezés (ADR-018) már él a `PlanningRepo.find_by_radius / find_by_bbox` formájában [5]. A kickoff MVP (1b) a 300/500/1000m-es sugár-elemzőt használta [2], de a térkép alatt lista-detail mellé még nincs sugár-vezérlés. Houzy fix hem-en, smartconext portfolio hem-en marad sugár nélkül [2].

## Döntés

1. **Viewer:** `frontend/src/components/WatchZone.tsx` (~90 sor) — slider (300/500/1000/2000m) + Three.js circle overlay a `Map3D`-ben + filtered Baugesuche szám élő frissítése a `GET /planning/radius` hívásból [5]; a circle a `DetailPanel` fölötti szalagban is visszajelzi a darabszámot.
2. **Térkép-hook:** `Map3D.tsx` `watchRadiusM` prop + GSAP ring — a circle a `find_by_radius` eredményhez kötött, nem csak dísz [5].
3. **Adatkapu:** meglévő `radius` + `bbox` végpontok reuse-ja, nincs új backend model; a `radius_m` paraméter már elfogadott 50–50000 között [5].

## Elvetve

| Opció | Miért nem |
|---|---|
| Kliens-oldali haversine csak | Nem lapoz, nem indexelt, `find_by_radius` pre-filter <5ms 22k rekordon jobb [ADR-018] |
| PostGIS konténer csak watcher-hez | 22k méretre túl nagy deploy költség [ADR-018] |

## Következmény

- Kártya: `WatchZone.tsx` + `messages/*.json` +4 kulcs, max 90 sor; `Map3D.tsx` +~40 sor.
- Validálás: `pytest` `test_planning_spatial.py` már zöld (`radius`/`bbox`) [5]; E2E `watch zone slider -> filtered count` (us_021_watchzone).
- UX: a radius watcher *kiegészít* a TopicList/DetailPanel alatt — nem helyettesíti.

## Kapcsolódó

- Research: `docs/research/2026-08-28-usability-deep-dive.md` (Rank #3), `docs/research/2026-08-27-spatial-radius-engine.md`
- Kód: `frontend/src/components/WatchZone.tsx`, `frontend/src/app/Map3D.tsx`, `src/db/planning_repo.py`
- Következő ADR: ADR-022 (Deep-link)
