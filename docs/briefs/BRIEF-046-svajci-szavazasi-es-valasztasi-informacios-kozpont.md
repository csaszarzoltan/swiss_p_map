# BRIEF-046: Svájci Szavazási és Választási Információs Központ

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-046  
**Forrás:** OpenBorough Elections & Legislation modul mintája, a svájci közvetlen demokrácia sajátosságai (szövetségi, kantonális és önkormányzati népszavazási vasárnapok) és a 2026-09-02-i egyeztetés alapján

## Probléma

A szavazási adatok korábban csak egyszerű múltbéli diagramként jelentek meg, anélkül, hogy a felhasználó megértené a közelgő szavazások valódi tétjét, a hivatalos pro/kontra érveket, a közvélemény-kutatások módszertanát, vagy a szavazás utáni települési szintű eltéréseket az országos átlagtól.

## Célcsoport és kontextus

Minden svájci választópolgár, politikai döntéshozó, újságíró és helyi közösségi tag, aki a népszavazási döntések előtt és után tényalapú, manipulációmentes tájékoztatást keres.

## Kívánt eredmény

Egy dedikált szavazási és választási hub:
1. **Szavazás előtt (Előkészületi szakasz):**
   - A kérdés közérthető összefoglalása ("Mi változik IGEN / NEM esetén?").
   - Hivatalos szövetségi füzet (*Abstimmungsbüchlein*) pro és kontra érveinek tényalapú kivonata.
   - Pártok és kezdeményező bizottságok hivatalos álláspontjai.
   - Közvélemény-kutatások (pl. SRG / gfs.bern) kötelező metaadatokkal: kutatóintézet, felvétel dátuma, mintanagyság ($N$), hibahatár ($\pm\%$), finanszírozó és reprezentativitás.
2. **Szavazás után (Eredményközpont):**
   - Országos, kantonális és települési szintű JA/NEIN eredmények és részvételi arány.
   - Jelentős helyi eltérések kiemelése a szövetségi átlagtól (pl. Röstigraben vagy város-vidék különbségek).
   - Térképi JA/NEIN kantonális és járási színezés + számszerű táblázat.
3. **Forráskategóriák szigorú szétválasztása:** Hivatalos állami dokumentum, közvélemény-kutatás, szerkesztőségi cikk és független tényellenőrzés.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-046-01:** Választópolgárként szeretném látni a következő országos szavazási vasárnap kérdéseit, a hivatalos füzet rövidített érveivel együtt.
- **US-046-02:** Felhasználóként egy közvélemény-kutatási grafikont látva kötelezően látni akarom a hibahatárt, a mintanagyságot és a felmérés készítőjét.
- **US-046-03:** Helyi lakosként a szavazás lezárulta után látni szeretném, hogyan szavazott a saját településem és kantonunk az országos átlaghoz képest.
- **US-046-04:** Felhasználóként a szavazási eredményeket interaktív térképen és rendezhető táblázatban is meg akarom tekinteni.

## Scope

- Szavazási előkészületi és eredmény-megjelenítő komponensek.
- `GET /api/v1/votes/proposals`, `GET /api/v1/votes/proposal/{id}/analysis`, `GET /api/v1/votes/polls` végpontok.
- BFS VoteInfo és BK (Bundeskanzlei) adatmodell integráció.

## Non-scope

- Anonim elektronikus szavazatleadási platform üzemeltetése (a rendszer szigorúan tájékoztató jellegű).

## Érintett rendszerek

- `src/services/vote_service.py`, `src/models/vote.py`, `frontend/src/components/LocalInformationHub.tsx`, `frontend/src/app/Map3D.tsx`
