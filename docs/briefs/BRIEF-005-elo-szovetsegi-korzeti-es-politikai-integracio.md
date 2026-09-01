# BRIEF-005: Élő Szövetségi Körzeti és Politikai Integráció

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-005 (ADR-005)  
**Forrás:** a Swisstopo api3 Identify geoszolgáltatás (ARE ÖV-Güteklassen, BAFU zajszennyezés) és a PARIS parlamenti CQL API alapján

## Probléma

A körzeti adatok és a parlamenti képviselet adatai elszigetelt kormányzati adatbázisokban találhatók. Egy lakos nem tudja egy helyen megnézni, hogy a lakókörzetében milyen a tömegközlekedési minőségi osztály (ÖV-Klasse A-D), mekkora az átlagos nappali decibel zajterhelés, és kik a körzet parlamenti képviselői.

## Célcsoport és kontextus

Állampolgárok, választópolgárok és ingatlankeresők, akik a lakókörzetük infrastrukturális minőségét és politikai képviseletét vizsgálják.

## Kívánt eredmény

Egyetlen API hívással lekérdezhető körzeti profil, amely élőben azonosítja a szövetségi GIS rétegeket (ARE/BAFU) és lekéri a helyi parlamenti képviselők névsorát és pártállását.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-005-01:** Felhasználóként szeretném megtudni egy svájci irányítószámhoz (pl. 8004 Zürich) tartozó tömegközlekedési minőségi besorolást (pl. "Klasse A").
- **US-005-02:** Felhasználóként szeretném látni a becsült nappali zajszintet (pl. "58 dB(A)"), hogy felmérjem a környék csendességét.
- **US-005-03:** Felhasználóként a Politika fülön szeretném látni a körzet képviselőit (név, párt, választókerület).
- **US-005-04:** Rendszerként szeretném, ha a külső szövetségi szerverek kiesésekor a rendszer determinisztikus tartalék (fallback) adatokkal szolgálna kiabálás helyett.

## Scope

- `PlaceService` élő `api3.geo.admin.ch/rest/services/api/MapServer/identify` integrációval.
- `PoliticsService` PARIS CQL API integrációval.
- Szigorú fallback és timeout védelem (upstream 500 hiba esetén stabil válasz).

## Non-scope

- Közvetlen e-mail küldés a képviselőknek a felületről.

## Érintett rendszerek

- `src/services/place_service.py`, `src/services/politics_service.py`, `src/main.py`

## Bizonytalanságok

- Szövetségi GeoAdmin API sebesség- és hívásszám-korlátai (caching bevezetése szükséges).
