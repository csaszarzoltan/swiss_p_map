# BRIEF-010: Intuitív Témaválasztó Sáv és Részletező Drawer

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-010 (ADR-010)  
**Forrás:** a felső 6-lapos `TopicSidebar` navigáció, a `Quick-Picks` gyorsgombok és az alsó `DetailPanel` komponens alapján

## Probléma

A korábbi oldalsávos (sidebar) elrendezés összenyomta a 3D térképet, és megnehezítette a mobilos használatot. A felhasználók számára nem volt egyértelmű, hogyan válthatnak az áttekintés, a politika, a helyi adatok és az építkezések között.

## Célcsoport és kontextus

Minden látogató asztali gépen, tableten és mobiltelefonon.

## Kívánt eredmény

Egy modern, felső elhelyezésű vízszintes lapsáv (Tabs), dinamikus számláló jelvényekkel (pl. "Planung (4)", "Politik (12)"), Quick-Pick gyorsválasztó gombokkal a kiemelt városokra (`8004`, `8001`, `8610`, `3011`, `4001`), és egy térkép alatti gazdag részletező panellel.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-010-01:** Felhasználóként szeretném a 6 fül (Übersicht, Politik, Ort, Planung, Sonnendach, ÖREB) közötti váltással azonnal szűrni a kapcsolódó listát és térképet.
- **US-010-02:** Felhasználóként szeretnék az egyes füleken számláló jelvényeket látni (badge), hogy tudjam, hány releváns adat tartozik a körzethez.
- **US-010-03:** Felhasználóként szeretnék a Quick-Pick gombokra (pl. "8001 Altstadt", "3011 Bern") kattintva egyetlen mozdulattal betölteni a mintakörzeteket.
- **US-010-04:** Mobilos látogatóként szeretném, hogy a lapsáv vízszintesen görgethető legyen és ne lógjon le a képernyőről.

## Scope

- `TopicSidebar.tsx` komponens 6 témával és dinamikus counts objektummal.
- `DetailPanel.tsx` komponens témánként specializált kártyanézetekkel.
- `Quick-Picks` sáv a `SearchPanel.tsx`-ben.

## Non-scope

- Felhasználó által átrendezhető egyedi fül-sorrend (konzisztens fix struktúra).

## Érintett rendszerek

- `frontend/src/components/TopicSidebar.tsx`, `frontend/src/components/DetailPanel.tsx`, `frontend/src/app/SearchPanel.tsx`

## Bizonytalanságok

- Különböző képernyőszélességeken a szövegek tördelése és olvashatósága (reszponzív tesztek szükségesek).
