# BRIEF-019: Intelligens Cím- és Geokódolási Kereső

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-019  
**Forrás:** a Swisstopo geocoding keresőmotor (`api3.geo.admin.ch/rest/services/api/SearchServer`) és a keresési panel alapján

## Probléma

A felhasználók nem mindig 4-jegyű irányítószámot (PLZ) ismernek, hanem pontos utcanevet, házszámot vagy településnevet (pl. "Bahnhofstrasse 1, Zürich" vagy "Bundesplatz 3, Bern") írnak be. Irányítószám-kényszer esetén a keresés sikertelen lesz.

## Célcsoport és kontextus

Minden látogató, aki tetszőleges svájci címet vagy látványosságot akar megkeresni.

## Kívánt eredmény

Intelligens, automatikusan kiegészítő (autocomplete) keresőmező, amely szöveges címekre, utcákra és községekre is azonnal a hivatalos Swisstopo geokódolt koordinátákkal válaszol, és ráközelíti a 3D térképet a pontos épületre.

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-019-01:** Felhasználóként utcanevet és házszámot beírva szeretnék intelligens címjavaslatokat kapni a Swisstopo adatbázisából.
- **US-019-02:** Felhasználóként kiválasztva egy javasolt címet, a rendszernek automatikusan azonosítania kell a megfelelő irányítószámot és koordinátákat.
- **US-019-03:** Felhasználóként szeretném, hogy a 3D térkép kamerája automatikusan a kiválasztott cím fölé repüljön (fly-to animáció).

## Scope

- `SwisstopoService.search_addresses` integráció.
- Élő geokódolási javaslatok a `SearchPanel.tsx`-ben.
- Automatikus koordináta-feloldás és 3D kameramozgatás.

## Non-scope

- Útvonaltervezés (pl. Google Maps stílusú A-ból B-be navigáció).

## Érintett rendszerek

- `src/services/swisstopo_service.py`, `src/main.py`, `frontend/src/app/SearchPanel.tsx`, `frontend/src/app/Map3D.tsx`

## Bizonytalanságok

- Hálózati késleltetés gépelés közbeni gyors kereséseknél (debounce 300ms szükséges).
