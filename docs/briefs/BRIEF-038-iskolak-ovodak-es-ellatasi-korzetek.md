# BRIEF-038: Iskolák, Óvodák és Oktatási Ellátási Körzetek

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-038  
**Forrás:** BFS/FSO oktatási statisztikák, kantonális és önkormányzati iskola- és körzeti geoportálok

## Probléma

A családok egy helyen látják a közlekedést és környezeti adatokat, de nem tudják megállapítani, melyik iskola vagy óvoda tartozik a címhez, mennyire biztonságos az út, és mennyire friss a körzetinformáció.

## Célcsoport és kontextus

Családok, költözők, önkormányzati tervezők és ingatlan-tanácsadók lakóhelyválasztás vagy beiratkozás előkészítésekor.

## Kívánt eredmény

Címhez rendelt, forrásolt oktatási intézménylista, ahol elérhető körzethatár, gyalogos elérhetőség, korosztály, nyelv és hivatalos beiratkozási link jelenik meg.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-038-01:** Szülőként szeretném látni a címhez tartozó állami iskolát és óvodát, hogy értsem a várható ellátási helyet.
- **US-038-02:** Szülőként szeretném összehasonlítani a gyalogos távolságot és a közlekedési kockázati pontokat több intézményhez.
- **US-038-03:** Felhasználóként szeretném, hogy hivatalos körzethatár hiányában a rendszer csak közeli intézményeket mutasson, és ne állítson garantált felvételi körzetet.
- **US-038-04:** Mobil- és képernyőolvasós felhasználóként szeretném az intézményeket térkép mellett rendezhető, jól címkézett listában is elérni.

## Scope

- Állami óvodák és iskolák intézményi pontjai, korosztály és hivatalos link.
- Körzethatárok provider-adapterrel ott, ahol nyílt geoadat érhető el.
- Gyalogos távolság és biztonságos út alapmutatók, adatfrissesség.

## Non-scope

- Iskolai minőségi rangsor, felvételi garancia, gyermekprofil vagy személyes tanulói adat.

## Érintett rendszerek

- tervezett education_service és school modellek
- tervezett school/catchment adatbázistáblák
- frontend family topic és route summary
- BFS, kantonális és kommunális portálok

## Bizonytalanságok

- Nincs egységes országos körzeti API; a körzetek tanévenként változhatnak, és egyes kantonokban eltérő iskolarendszer vagy nyelvi besorolás érvényes.
