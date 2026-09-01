# BRIEF-017: Interaktív Történeti Szavazási Idővonal és Referendum Választó

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-017 (ADR-017)  
**Forrás:** a multi-referendumos szövetségi szavazási adatbázis és a 3D térképi téma-választó alapján

## Probléma

A politikai pillér korábban csak egyetlen szavazásra (13. AHV-Rente) korlátozódott. Svájcban évente 4 szavazási vasárnap van több mint 10 szövetségi témával. A felhasználók nem tudták összehasonlítani, hogy a kantonok hogyan szavaztak más témákban (pl. BVG-nyugdíjreform, Autópálya-bővítés, Stromgesetz).

## Célcsoport és kontextus

Állampolgárok, politikai elemzők és újságírók, akik a szavazási mintázatokat és a híres *Röstigraben* törésvonalat vizsgálják.

## Kívánt eredmény

Egy interaktív szavazás-választó (Dropdown / Selector) a 3D térkép kártyáján:
1. `6670`: 13. AHV-Rente (2024-03-03 — 58.2% Igen)
2. `6680`: BVG-Reform (2024-09-22 — 32.9% Igen)
3. `6690`: Ausbauschritt Nationalstrassen (2024-11-24 — 47.3% Igen)
4. `6700`: Stromgesetz (2024-06-09 — 68.7% Igen)
Kiválasztáskor a 3D kantonok azonnal az adott szavazás kantonális eredményeire frissülnek és átszíneződnek!

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-017-01:** Felhasználóként szeretnék egy lenyíló listából kiválasztani a legutóbbi 4 szövetségi népszavazás bármelyikét.
- **US-017-02:** Felhasználóként szeretném látni, ahogy a 3D térkép azonnal átszíneződik a választott referendum kantonális eredményei szerint.
- **US-017-03:** Rendszerként a `GET /api/v1/politics/votes/list` és `GET /api/v1/politics/votes/{id}` végpontokon keresztül szeretném kiszolgálni az adatokat.

- **US-017-04:** Felhasználóként szeretném, hogy hibás vagy nem létező referendumazonosító esetén a rendszer lokalizált hibaállapotot és visszalépési lehetőséget adjon.

## Scope

- `VoteService` multi-proposal támogatással.
- REST végpontok a javaslatok listázására és lekérésére.
- 3D Térkép integráció.

## Non-scope

- Egyéni polgárok szavazólapjainak digitális leadása.

## Érintett rendszerek

- `src/services/vote_service.py`, `src/models/vote.py`, `src/main.py`, `frontend/src/app/Map3D.tsx`

## Bizonytalanságok

- Régebbi, 1990-es évekbeli szavazások adatainak digitalizálása és pontossága.
