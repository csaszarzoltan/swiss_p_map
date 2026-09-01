# BRIEF-014: Többkantonos Építési Engedély Federáció

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-014 (ADR-014)  
**Forrás:** a többkantonos hirdetmény-adatbázis (Zürich, Bern, Basel, Genf) és a federált tervezési végpontok alapján

## Probléma

Az építési engedélyek kantonális szinten külön-külön hivatalos lapokban (pl. Amtsanzeiger Bern, Kantonsblatt Basel-Stadt, FAO Genève) jelennek meg. A felhasználónak külön oldalakat kellene felkeresnie ahelyett, hogy egyetlen svájci platformon látná az országos építési aktivitást.

## Célcsoport és kontextus

Országos ingatlanfejlesztők, építész irodák és a svájci nagyvárosok lakói.

## Kívánt eredmény

Egy federált adatmodell és keresési réteg, amely támogatja Zürich (`8004`, `8001`, `8610`), Bern (`3011`), Basel (`4001`), és Genf (`1201`) aktív építkezéseit mind a 3D térképen, mind a listában.

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-014-01:** Felhasználóként Bernre keresve (`3011`) szeretném látni a berni óvárosi és üzleti átalakítási projekteket.
- **US-014-02:** Felhasználóként Bázelre keresve (`4001`) szeretném látni a bázeli homlokzatfelújításokat és napelemes projekteket.
- **US-014-03:** Felhasználóként Genfre keresve (`1201`) franciául szeretném látni a helyi építési engedélyeket (*Surélévation d'immeuble*).

## Scope

- Multi-kanton `Baugesuch` seedek és API lekérdezések.
- Típusos egységtesztek kanton-szintű szűrésekre (`test_planning_multi_canton.py`).
- Playwright E2E teszt a Bern és Basel közötti tervezési váltásra.

## Non-scope

- Az összes kisebb svájci falu (2000+ önkormányzat) napi engedélyeinek azonnali scrapelése (fokozatos kiterjesztés).

## Érintett rendszerek

- `src/main.py`, `src/services/planning_service.py`, `tests/unit/test_planning_multi_canton.py`

## Bizonytalanságok

- Nyugati francia kantonok (Vaud, Genève, Neuchâtel) és a német kantonok jogi határidő-számítási különbségei.
