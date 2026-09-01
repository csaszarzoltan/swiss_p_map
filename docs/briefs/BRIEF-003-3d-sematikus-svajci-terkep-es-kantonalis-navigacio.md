# BRIEF-003: 3D Sematikus Svájci Térkép és Kantonális Navigáció

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-003 (ADR-003)  
**Forrás:** a Three.js WebGL 3D motor, a 26 kanton szilárd extruded geometriája és a raycaster interakciók alapján

## Probléma

A hagyományos 2D térképek sík, statikus és unalmas felületet nyújtanak. A felhasználók számára nehéz átlátni a svájci kantonok domborzatát, kiterjedését és határait.

## Célcsoport és kontextus

Látogatók és elemzők, akik vizuálisan vonzó, modern és interaktív 3D élményen keresztül szeretnék felfedezni Svájc kantonjait és településeit.

## Kívánt eredmény

Egy Three.js alapú, sötét tónusú kiber-üveg (cyber-glass) stílusú 3D Svájc-modell, mind a 26 kanton pontos határvonalával, egérmozgatásra reagáló kanton-kiemeléssel, sima kameramozgással és városi alrétegekkel.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-003-01:** Látogatóként szeretném forgatni, dönteni és zoomolni a 3D svájci térképet az egérrel vagy érintéssel.
- **US-003-02:** Felhasználóként szeretném, hogy az egér kanton fölé húzásakor a kanton kiemelkedjen és kék fénnyel világítson, miközben megjelennek az adatai (népesség, szavazati arány).
- **US-003-03:** Felhasználóként szeretnék rákattintani egy kantonra, hogy a kamera ráközelítsen, és feltárja a kantonhoz tartozó városokat és körzeteket.
- **US-003-04:** Felhasználóként szeretnék az iránytűre és az eligazító szövegekre támaszkodva könnyen navigálni a térképen.

## Scope

- Three.js OrbitControls kamera- és nézetvezérlés.
- 26 kantonális ExtrudeGeometry szilárd 3D modell (`swissCantons.ts`).
- Raycaster alapú hover és click eseménykezelés HTML tooltip lebegő ablakkal.
- GSAP kameramozgatás és visszaállító gomb (*"SCHWEIZ"*).

## Non-scope

- Fotorealisztikus 3D épületmodellek és fák renderelése (a hangsúly a sematikus, elegáns vizualizáción van).

## Érintett rendszerek

- `frontend/src/app/Map3D.tsx`, `frontend/src/app/swissCantons.ts`, `frontend/src/app/cityOutlines.ts`

## Bizonytalanságok

- Régebbi mobiltelefonokon a Three.js canvas teljesítményének fenntartása (60 FPS cél).
