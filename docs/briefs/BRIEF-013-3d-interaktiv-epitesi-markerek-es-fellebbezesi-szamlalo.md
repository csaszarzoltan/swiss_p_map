# BRIEF-013: 3D Interaktív Építési Markerek és Fellebbezési Számláló

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-013 (ADR-013)  
**Forrás:** a Three.js borostyánsárga 3D pin jelölők, a raycasting eseménykezelés és a 22,000 OGD építkezés determinisztikus térbeli elhelyezése alapján

## Probléma

Az építési engedélyek korábban csak szöveges listában jelentek meg. A felhasználó nem látta a 3D térképen, hogy egy város melyik pontján, mekkora sűrűségben zajlanak építkezések, és hol van érvényben aktív fellebbezési határidő.

## Célcsoport és kontextus

Szomszédok, lakosok és ingatlanpiaci befektetők, akik térben akarják látni az aktív építkezéseket.

## Kívánt eredmény

Látványos, borostyánsárga 3D pin-ek a Three.js térképen az aktív projektek pontos helyén, lüktető animációval, föléhúzáskor lebegő címkártyával, és kattintásra azonnali projekt-betöltéssel.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-013-01:** Felhasználóként szeretném a 3D térképen látni az aktív építkezéseket jelző 3D borostyánsárga tüskéket (pin-eket).
- **US-013-02:** Felhasználóként az egérrel egy 3D pin fölé mozogva szeretném látni a projekt címét és az Auflagefrist határidejét.
- **US-013-03:** Felhasználóként rákattintva egy 3D pin-re, a projektnek azonnal ki kell jelölődnie a lenti listában és a részletező panelen.

- **US-013-04:** Mobilfelhasználóként szeretném érintéssel kijelölni a markert és bezárni a részleteket, hogy hover nélkül is teljes legyen a funkció.

## Scope

- Three.js CylinderGeometry + SphereGeometry kombinált 3D pin mesh.
- Raycasting detekció a `pinGroup` gyermekein.
- Determinisztikus WGS84 koordináta-generálás az OGD 2982 CSV rekordokhoz.

## Non-scope

- 3D épület tömegmodell generálása (egyelőre precíz pin jelölők).

## Érintett rendszerek

- `frontend/src/app/Map3D.tsx`, `src/services/ogd_service.py`

## Bizonytalanságok

- Egymáshoz nagyon közeli (azonos telek/házszám) projektek markereinek átfedése (clustering megoldás a jövőben).
