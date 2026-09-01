# BRIEF-026: Kataszteri Rétegválasztó és Parcella-adatlekérdezés

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-026  
**Forrás:** ADR-007, ADR-015 és terméklogikai hiány

## Probléma
Az ÖREB-zóna jelenleg összefoglaló értékként vagy tematikus színezésként jelenik meg, de a felhasználó nem tud hivatalos rétegek között választani és egy konkrét parcellára lekérdezni.

## Célcsoport és kontextus
Tulajdonosok, építészek és fejlesztők, amikor egy telek övezeti, korlátozási vagy kataszteri kontextusát vizsgálják.

## Kívánt eredmény
A felhasználó ellenőrzött réteglistából kapcsolhatja a kataszteri rétegeket, parcellára kattintva pedig forrásolt attribútumokat és elérhetőségi állapotot kap.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-026-01:** Felhasználóként szeretném be- és kikapcsolni az elérhető ÖREB és kataszteri rétegeket.
- **US-026-02:** Felhasználóként szeretnék parcellára kattintva zóna- és korlátozási adatokat látni.
- **US-026-03:** Felhasználóként szeretném látni, mely réteg mely kantonban és milyen frissességgel érhető el.
- **US-026-04:** Felhasználóként szeretném, hogy egy hibás réteg ne törje el a térképet, hanem külön hibaállapotot kapjon.

## Scope
- Rétegkatalógus, toggle állapot, loading/error, parcella identify és forrásmetaadat.
- Kantonális provider-képességek és fallback megjelenítése.

## Non-scope
- Tulajdoni lap vagy nem nyilvános személyes tulajdonosi adatok megjelenítése.

## Érintett rendszerek
- frontend térképi rétegkezelés
- tervezett ÖREB provider adapterek
- Swisstopo és kantonális ÖREB M2M/WFS szolgáltatások

## Bizonytalanságok
- Kantononként eltérő szolgáltatások, licencek, parcellaazonosítók és geometria-teljesítmény külön research/ADR-t igényelnek.
