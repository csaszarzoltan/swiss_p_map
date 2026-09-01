# BRIEF-018: Térbeli Sugár- és Poligon Keresőmotor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-018 (ADR-018)  
**Forrás:** a Haversine és LV95 geodéziai távolságszámítási motor, a `PlanningRepo.find_by_radius` és `PlanningRepo.find_by_bbox` metódusok alapján

## Probléma

Az építési engedélyek keresése korábban csak a 4-jegyű irányítószámra támaszkodott. Ha a felhasználó egy kerület vagy kanton határán lakik, a tőle 50 méterre lévő projektek nem jelentek meg, csak mert más irányítószámhoz tartoztak. Emellett a 3D térkép mozgatásakor (pan/zoom) hiányzott a nézeti téglalapban lévő projektek lekérése.

## Célcsoport és kontextus

Minden felhasználó, aki egy adott cím körüli méter-alapú környezetben (pl. 500m, 1000m körben) vagy a térkép aktuális látómezőjében keres építkezéseket.

## Kívánt eredmény

Nagy sebességű (<5ms) térbeli lekérdező motor:
- `GET /api/v1/planning/radius?lat=...&lon=...&radius_m=1000`: távolság szerint növekvő sorrendben adja vissza az építkezéseket `distance_m` mezővel.
- `GET /api/v1/planning/bbox?min_lat=...&max_lat=...&min_lon=...&max_lon=...`: a képernyőnézetbe eső projekteket adja vissza.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-018-01:** Felhasználóként egy kiválasztott koordináta köré 1000 méteres sugarú keresést szeretnék indítani, hogy lássam a közvetlen szomszédságomban lévő projekteket.
- **US-018-02:** Felhasználóként a találati listában látni szeretném a projektek tőlem mért pontos távolságát méterben (pl. "240.5 m").
- **US-018-03:** Rendszerként szeretném, ha a 22,000+ rekordon futó térbeli szűrés minimális erőforrás-igényű lenne SQLite előszűréssel és Haversine formulával.

- **US-018-04:** Felhasználóként szeretném, hogy túl nagy, negatív vagy hibás sugár és bbox esetén az API egyértelmű validációs hibát adjon.

## Scope

- `haversine_distance_m` függvény a `geo_converter.py` modulban.
- `PlanningRepo.find_by_radius` és `PlanningRepo.find_by_bbox` metódusok.
- `GET /api/v1/planning/radius` és `GET /api/v1/planning/bbox` REST végpontok.

## Non-scope

- Nehéz külső PostGIS adatbázisszerver telepítése (beépített zéró-függőségű SQLite megoldás).

## Érintett rendszerek

- `src/services/geo_converter.py`, `src/db/planning_repo.py`, `src/services/planning_service.py`, `src/main.py`

## Bizonytalanságok

- Nagyon nagy sugarak (pl. 50km+) esetén a Haversine számítás CPU-terhelése (határ: max 50,000 méter).
