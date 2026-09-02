# BRIEF-051: Interaktív Szavazási és Népszavazási Vizualizációs UI Kártyák

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-051  
**Forrás:** 1. Opció (Civic Panelek Prémium UI Redesignja), OpenBorough Elections UI és a `SPEC-046` svájci szavazási specifikáció alapján

## Probléma

A szavazási és választási adatok korábban technikai, nyers formában jelentek meg. A svájci polgárok számára elengedhetetlen, hogy a szavazási kérdések tétjét, a pro és kontra érveket, a felmérések állását, valamint az urnazárás utáni végeredményeket modern, intuitív, infografika jellegű vizualizációban lássák.

## Célcsoport és kontextus

Minden szavazópolgár, helyi közösségi tag és politikai elemző, aki a szövetségi és kantonális szavazások előtt és után gyors, áttekinthető vizuális összefoglalót igényel.

## Kívánt eredmény

Egy prémium Glassmorphism szavazási UI komponenscsalád:
1. **Szavazási Mérlegsáv (*Voting Balance Bar*):**
   - Vizuális IGEN (kék/zöld) és NEM (piros/korall) megoszlási sáv a szavazás utáni eredményekhez vagy a szavazás előtti felmérésekhez.
   - Részvételi arány (*Stimmbeteiligung %*) számláló és kantonális rangsor.
2. **Kinyitható Pro / Kontra Kártyák (*Argumente-Akkordeon*):**
   - A szövetségi füzet (*Abstimmungsbüchlein*) hivatalos érvei kártyákba rendezve, támogató pártok logóival és hivatalos forráshivatkozással.
3. **Közvélemény-kutatási Idővonal (*Poll Trend Chart*):**
   - Vizuális grafikon a szavazás előtti felmérési trendekről kötelező hibahatár-sávval ($\pm 3\%$) és mintanagyság ($N$) feltüntetésével.
4. **Helyi Eltérés Jelvény (*Local Deviation Badge*):**
   - Kiemelés, ha az adott település szignifikánsan eltért az országos vagy kantonális átlagtól (pl. *„Zürich 8004: +12.4% JA az országoshoz képest”*).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-051-01:** Választópolgárként szeretném egyetlen színes mérlegsávon látni a népszavazási javaslat IGEN/NEM arányát.
- **US-051-02:** Felhasználóként egy kattintással szeretném lenyitni a hivatalos pro és kontra érveket anélkül, hogy hosszú PDF-eket kellene böngésznem.
- **US-051-03:** Helyi lakosként látni akarom, hogyan szavazott a saját választókerületem a szövetségi átlaghoz viszonyítva.

## Scope

- `frontend/src/components/civic/VotingVisualCard.tsx` és kapcsolódó diagram-komponensek.
- Glassmorphism stílus, reszponzív mobil elrendezés és akadálymentes ARIA címkék.

## Non-scope

- Szavazási preferenciák tárolása a felhasználó profiljában (teljes anonimitás).

## Érintett rendszerek

- `frontend/src/components/ResidentCivicPanels.tsx`, `frontend/src/components/LocalInformationHub.tsx`, `src/services/vote_analysis_service.py`
