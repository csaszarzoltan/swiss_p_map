# BRIEF-056: Élő BFS VoteInfo és Szövetségi Szavazási API Konnektor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-056  
**Forrás:** 2. Opció (Valódi Élő Svájci OGD & Külső API Integrációk), Szövetségi Statisztikai Hivatal (BFS) VoteInfo OGD API és a `SPEC-046` specifikáció alapján

## Probléma

A szövetségi és kantonális népszavazási vasárnapokon (évente 4 alkalommal) az adatok percről percre érkeznek be a településekről a kantonális kancelláriákra, majd a BFS központi rendszerébe. Ahhoz, hogy a Swiss P Map valós időben közvetíthesse a szavazási eredményeket, közvetlen élő csatlakozásra van szükség a hivatalos BFS VoteInfo JSON végponthoz.

## Célcsoport és kontextus

Svájci választópolgárok, politikai elemzők és újságírók, akik a szavazási vasárnapon élőben szeretnék követni az eredmények alakulását.

## Kívánt eredmény

Egy hivatalos BFS VoteInfo élő integrációs modul:
1. **Élő Szavazási Eredményfolyam (*Live-Ticker*) Szavazási Vasárnapokon:**
   - 12:00-tól (urnazárás) kezdve a települési szintű eredmények automatikus frissülése 60 másodpercenként.
   - Beérkezett települések aránya (*Ausgezählte Gemeinden %*).
2. **Hivatalos Szövetségi Archívum Szinkronizáció:**
   - A korábbi szövetségi szavazások (1848-tól napjainkig) hivatalos BFS azonosítóinak és archív eredményeinek automatikus frissítése.
3. **Kantonális Szavazási Adatok:**
   - A 26 kanton saját kantonális javaslatainak (kantonalen Vorlagen) lekérése és struktúrálása.
4. **Adatbiztonság és Verziókezelés:**
   - SHA256 ellenőrzőösszeg a letöltött BFS JSON állományokra a manipulációmentesség garantálására.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-056-01:** Választópolgárként a szavazási vasárnap délutánján a saját településem hivatalos, feldolgozott eredményét akarom látni amint a kancellária lezárja a számlálást.
- **US-056-02:** Elemzőként a korábbi népszavazások hivatalos szövetségi adatait szeretném visszakeresni közvetlenül a BFS adatbázisából.
- **US-056-03:** Felhasználóként látni akarom, hogy a szavazási adatok melyik pillanatban szinkronizálódtak a Bundeskanzlei rendszerével.

## Scope

- `src/services/connectors/bfs_voteinfo_client.py` kliens.
- BFS JSON séma validátor és leképező (`VoteProposal`, `CantonVoteResult`, `MunicipalityVoteResult`).
- Élő szinkronizációs háttérfolyamat (*scheduled poll*) szavazási vasárnapokon.

## Non-scope

- Közvetlen kapcsolat a kantonális elektronikus szavazórendszerek (E-Voting) titkosított szervereihez.

## Érintett rendszerek

- `src/services/vote_analysis_service.py`, `src/services/vote_service.py`, `src/models/vote.py`
