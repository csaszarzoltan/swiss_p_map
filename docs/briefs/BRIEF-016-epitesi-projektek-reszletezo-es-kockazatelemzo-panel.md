# BRIEF-016: Építési Projektek Részletező és Kockázatelemző Panel

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-016 (ADR-016)  
**Forrás:** a Baugesuch Deep Inspector adatmodell (kivitelező, építész, parcellaszám, zónatípus, automatikus kockázati besorolás) alapján

## Probléma

A kiválasztott építési projektekről korábban csak az alapvető cím és a közzététel dátuma volt látható. Egy professzionális ingatlanelemző vagy szomszéd számára elengedhetetlen a kivitelező cég, a felelős építész iroda, a helyrajzi parcellaszám, a zónabesorolás és a fellebbezési kockázat azonnali ismerete.

## Célcsoport és kontextus

Ingatlanbefektetők, helyi lakóközösségek és építészek.

## Kívánt eredmény

Egy mélyreható részletező kártya és oldalsó fiók (Drawer), amely megjeleníti az építtetőt (`contractor`), az építészt (`architect`), a parcellaszámot (`parcel_number`), az építési övezetet (`zone_type`), a fellebbezési határidőig hátralévő napok számát és a jogi kockázati szintet (`low`, `medium`, `high`).

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-016-01:** Felhasználóként egy építkezésre kattintva szeretném látni a felelős építész irodát és a kivitelező céget.
- **US-016-02:** Felhasználóként látni szeretném a projekt automatikus kockázati szintjét (pl. 🔴 Magas kockázat: tetőtér-beépítés / bontás Kernzone-ban).
- **US-016-03:** Felhasználóként látni szeretném a pontos parcellaszámot és a közvetlen linket az Amtsblattportal hivatalos hirdetményéhez.

## Scope

- `Baugesuch` domain modell kibővítése (`contractor`, `architect`, `parcel_number`, `zone_type`, `risk_level`).
- Automatikus kockázati pontozó logika a cím és a zóna alapján.
- SQLite és REST API kiterjesztés.

## Non-scope

- Automatikus ügyvédi megbízás generálása.

## Érintett rendszerek

- `src/models/planning.py`, `src/db/planning_repo.py`, `frontend/src/components/DetailPanel.tsx`

## Bizonytalanságok

- Bizonyos régebbi OGD rekordoknál a magánszemély építtetők nevének anonimizálása (adatvédelmi megfelelőség).
