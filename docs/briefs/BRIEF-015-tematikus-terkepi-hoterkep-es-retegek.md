# BRIEF-015: Tematikus Térképi Hőtérkép és Rétegek

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-015 (ADR-015)  
**Forrás:** a 3D Three.js dinamikus színskálázás (Sonnendach napenergia, ÖREB zónaszínezés, Lärm zaj-izofonák, Politika szavazati arányok) alapján

## Probléma

A felső menüpontok (Sonnendach, ÖREB, Lärm, Politik) váltásakor a 3D térkép megjelenése statikus maradt. A felhasználó nem kap közvetlen térbeli visszajelzést arról, hogyan oszlik meg a napenergia-potenciál vagy a szavazati arány az országban.

## Célcsoport és kontextus

Vizuális elemzők és felhasználók, akik egy pillantással meg akarják érteni a svájci térbeli mintázatokat.

## Kívánt eredmény

Dinamikus anyag- és színváltás a 3D térképen:
- **`Politik` fül:** A kantonok színe a valós BFS Igen-szavazati arányt tükrözi (kék = magas jóváhagyás, korallvörös = elutasítás).
- **`Sonnendach` fül:** Arany/borostyánsárga szolár hőtérkép (magas napenergia-hozamú alpesi és déli kantonok kiemelése).
- **`ÖREB` fül:** Kataszteri zónaszínezés (Kernzone lila, Wohnzone kék, Gewerbe narancs).
- **`Ort / Lärm` fül:** Zajterhelési izofonák.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-015-01:** Felhasználóként a Politik fülre kattintva szeretném, ha a 3D térkép azonnal a szavazási eredmények szerinti hőtérképre váltana.
- **US-015-02:** Felhasználóként a Sonnendach fülre kattintva szeretném látni az arany szolár potenciál térképet.
- **US-015-03:** Felhasználóként szeretném, hogy az átmenetek sima animációval (GSAP color.lerp) menjenek végbe 60 FPS sebesség mellett.

- **US-015-04:** Színlátási nehézséggel élő felhasználóként szeretném, hogy a színek mellett szöveges jelmagyarázat és megfelelő kontraszt is közvetítse az értékeket.

## Scope

- Dinamikus Three.js MeshStandardMaterial színkezelés és GSAP átmenetek.
- Tematikus jelmagyarázat (Legend) a 3D térkép sarkában.

## Non-scope

- Nehéz, nagy felbontású WMS raszteres textúrák streamelése GPU memóriába (helyette gyors vertex és kantonális színkódolás).

## Érintett rendszerek

- `frontend/src/app/Map3D.tsx`, `frontend/src/app/[locale]/page.tsx`

## Bizonytalanságok

- Színvak felhasználók számára megfelelő kontrasztos színskálák biztosítása (a11y).
