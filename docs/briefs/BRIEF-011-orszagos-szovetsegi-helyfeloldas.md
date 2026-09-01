# BRIEF-011: Országos Szövetségi Helyfeloldás

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-011 (ADR-011)  
**Forrás:** a svájci szövetségi GIS rétegek (ARE, BAFU, BFE) kanton-független integrációja és az országos települési adatbázis alapján

## Probléma

A prototípus kezdetben csak zürichi irányítószámokat támogatott, miközben a szövetségi ARE, BAFU és BFE adatok egész Svájcra elérhetők. Bern, Basel, Genf, Lausanne és más nagyvárosok lakói nem kaptak releváns adatokat.

## Célcsoport és kontextus

Minden svájci lakos a 26 kanton bármelyik településén.

## Kívánt eredmény

Egész Svájcra kiterjedő helyfeloldás: bármely érvényes svájci irányítószámra (`3011 Bern`, `4001 Basel`, `1201 Genève`, `8610 Uster`, stb.) azonnal betöltődnek a szövetségi rétegek (zaj, tömegközlekedés, napenergia) és a helyi politikai képviselet.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-011-01:** Felhasználóként beírva a `3011` irányítószámot, szeretném látni Bern adatait és a berni politikai képviselőket.
- **US-011-02:** Felhasználóként beírva a `4001` irányítószámot, szeretném látni Basel-Stadt adatait.
- **US-011-03:** Rendszerként szeretném, hogy az élő szövetségi API lekérdezés a megfelelő kantonális scraperre fusson (pl. zürichi scraperek csak ZH esetén fussanak).

- **US-011-04:** Felhasználóként szeretném, hogy ismeretlen vagy érvénytelen svájci irányítószám esetén lokalizált, javítható hibaüzenetet kapjak.

## Scope

- Multi-kanton `PlaceService` és `PoliticsService` stub és élő támogatással.
- Svájci koordináta-tábla (`postcode_coords.ts`) a kiemelt városokra.
- Egységtesztek a kantonok közötti szétválasztásra (`test_place_multi_kanton.py`).

## Non-scope

- Lichtenstein és külföldi címek kezelése (szigorúan Svájc 26 kantonja).

## Érintett rendszerek

- `src/services/place_service.py`, `src/services/politics_service.py`, `frontend/src/app/postcode_coords.ts`

## Bizonytalanságok

- Részletes kantonális adókulcsok scrapelése mind a 26 kanton adóhivatalából (szövetségi becslés fallback).
