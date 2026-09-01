# BRIEF-023: Térképi Sugár-Figyelő és Közelben Lévő Projektek

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** ADR-021  
**Forrás:** meglévő kód, ADR-018 és ADR-021

## Probléma
A sugár- és bbox API már létezik, de a felhasználó nem tudja kényelmesen kiválasztani, mekkora környezetet figyeljen, és nem kap azonnali találati visszajelzést.

## Célcsoport és kontextus
Lakosok és ingatlanérdeklődők, akik egy kiválasztott cím 300, 500 vagy 1000 méteres környezetét vizsgálják.

## Kívánt eredmény
A felhasználó egyetlen vezérlővel módosítja a sugarat, látja a térképi gyűrűt és az adott körbe eső aktív projektek számát.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-023-01:** Felhasználóként szeretnék 300, 500 vagy 1000 méteres figyelési sugarat választani.
- **US-023-02:** Felhasználóként szeretném a térképen látni a kiválasztott sugár határát.
- **US-023-03:** Felhasználóként szeretném élőben látni a körön belüli projektek számát.
- **US-023-04:** Felhasználóként szeretném, hogy API-hiba vagy hiányzó középpont esetén érthető állapot jelenjen meg, és a felület használható maradjon.

## Scope
- WatchZone vezérlő és aktivált sugár.
- A meglévő radius végpont használata, loading és error állapot, térképi ring.

## Non-scope
- Háttérben futó értesítés vagy felhasználói fiókhoz mentett zóna.

## Érintett rendszerek
- frontend/src/components/WatchZone.tsx
- frontend/src/app/Map3D.tsx
- src/db/planning_repo.py
- src/main.py

## Bizonytalanságok
- A 2000 méteres opció ADR-ben szerepel, a jelenlegi komponensben viszont nincs; lapozás és nagy találatszám UX-e.
