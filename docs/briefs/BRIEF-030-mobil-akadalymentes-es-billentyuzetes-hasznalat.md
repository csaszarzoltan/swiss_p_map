# BRIEF-030: Mobil, Akadálymentes és Billentyűzetes Használat

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-030  
**Forrás:** meglévő reszponzív UI, E2E módszertan és termékigény

## Probléma
A WebGL térkép, vízszintes témasáv, tooltipek és sűrű részletezők mobilon, billentyűzettel vagy segítő technológiával nem minden útvonalon egyenértékűek.

## Célcsoport és kontextus
Mobiltelefonos, billentyűzetes, képernyőolvasós, csökkentett mozgást vagy nagy kontrasztot igénylő felhasználók.

## Kívánt eredmény
A fő keresési, témaváltási, térképi kijelölési és részletezési útvonalak WCAG-alapú, érintésbarát és automatizált E2E/axe ellenőrzéssel bizonyítottan használhatók.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-030-01:** Mobilfelhasználóként szeretném egy kézzel elérni a keresést, témákat és részleteket vízszintes túlcsordulás nélkül.
- **US-030-02:** Billentyűzetes felhasználóként szeretném logikus fókuszsorrendben használni az összes fő műveletet.
- **US-030-03:** Képernyőolvasós felhasználóként szeretnék szemantikus neveket és élő állapot-visszajelzéseket kapni.
- **US-030-04:** Csökkentett mozgást kérő felhasználóként szeretném kikapcsolva vagy rövidítve kapni a GSAP és pulzáló animációkat.

## Scope
- Mobil breakpointok, 44px érintési célok, focus visible, ARIA, reduced-motion és kontraszt.
- Kritikus journey-k mobil Playwright és axe ellenőrzése.

## Non-scope
- Natív iOS/Android alkalmazás készítése.

## Érintett rendszerek
- frontend/src/app/Map3D.tsx
- frontend/src/components/*
- frontend/src/app/globals.css
- frontend/e2e

## Bizonytalanságok
- A WebGL canvas interakcióinak képernyőolvasós alternatívája és a célzott WCAG megfelelési szint véglegesítése.
