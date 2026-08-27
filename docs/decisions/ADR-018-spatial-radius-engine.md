# ADR-018: Térbeli Sugár- és Poligon Keresőmotor (Spatial Radius & Bounding Box Engine)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** System Architect & QA Lead (research: `docs/research/2026-08-27-spatial-radius-engine.md`)
- **Kanban:** #swiss-p-map-018

## Kontextus
Az építési engedélyek keresése korábban csak az adott 4-jegyű irányítószámra korlátozódott. Ha egy felhasználó a körzet határán tartózkodik, vagy a 3D térképen egy tetszőleges területet nagyít ki, méter-alapú sugárkeresésre (`radius_m`) és nézeti téglalap-keresésre (`bbox`) van szükség.

## Döntés
1. **Térbeli Matematika & Távolságszámítás:** A `geo_converter.py` modult kiegészítjük egy nagy pontosságú, méter-alapú Haversine és LV95 távolságszámító függvénnyel (`haversine_distance_m(lat1, lon1, lat2, lon2) -> float`).
2. **Repo Szintű Térbeli Index:** A `PlanningRepo` megkapja a `find_by_radius` és `find_by_bbox` metódusokat.
3. **REST Végpontok:**
   - `GET /api/v1/planning/radius?lat=...&lon=...&radius_m=1000&active_only=true` — távolság szerint növekvő sorrendben, `distance_m` mezővel kiegészítve.
   - `GET /api/v1/planning/bbox?min_lat=...&min_lon=...&max_lat=...&max_lon=...`
4. **Zero-Dependency SQLite / Python Megvalósítás:** Nincs szükség nehéz külső PostGIS infrastruktúrára; a beépített térbeli szűrő <5ms alatt hajt végre 22,000 rekordon történő lekérdezést.

## Elvetve
| Opció | Miért nem |
|---|---|
| Külön PostGIS konténer bevezetése | Növelné a deployment komplexitást egy 22k méretű lokális projektnél |
| Csak kliensoldali JavaScript szűrés | Nem alkalmas nagy adatbázisok hatékony lapozására és API fogyasztásra |

## Következmény
- A felhasználó bármely koordináta köré kérhet 500m, 1000m, 2000m sugarú építési auditot.
- A 3D térkép automatikusan le tudja kérni az aktuális kamera látómezőjében lévő projekteket.

## Kapcsolódó
- Research: `docs/research/2026-08-27-spatial-radius-engine.md`
- Kód: `src/services/geo_converter.py`, `src/db/planning_repo.py`, `src/services/planning_service.py`, `src/main.py`
