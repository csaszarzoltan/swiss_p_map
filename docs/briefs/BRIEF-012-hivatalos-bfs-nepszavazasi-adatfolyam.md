# BRIEF-012: Hivatalos BFS Népszavazási Adatfolyam

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-012 (ADR-012)  
**Forrás:** a Svájci Szövetségi Statisztikai Hivatal (BFS / VoteInfo OGD) hivatalos népszavazási API-ja és a 26 kanton szavazati eredményei alapján

## Probléma

A politikai pillér és a 3D térkép korábban csak példa (mock) szavazási százalékokat mutatott, amelyek nem tükrözték a valós svájci népszavazási eredményeket és a kantonok közötti szociokulturális különbségeket.

## Célcsoport és kontextus

Állampolgárok, politológusok, újságírók és érdeklődők, akik a svájci közvetlen demokrácia kantonális mintázatait vizsgálják.

## Kívánt eredmény

Hivatalos szövetségi népszavazási adatok (pl. 2024.03.03 13. AHV-nyugdíj: 58.2% országos Igen, valós részvétel) mind a 26 kantonra pontosan lebontva, 4 nyelven elérhető előterjesztési címekkel.

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-012-01:** Felhasználóként szeretném a 3D térképen látni a legutóbbi szövetségi népszavazás hivatalos címét és országos jóváhagyási arányát.
- **US-012-02:** Felhasználóként az egérrel bármely kanton (pl. Vaud, Zürich, Appenzell) fölé mozogva szeretném látni az adott kanton valós Igen/Nem százalékát és részvételi arányát.
- **US-012-03:** Rendszerként a `GET /api/v1/politics/votes/latest` végponton keresztül strukturált JSON formátumban szeretném kiszolgálni a 26 kanton eredményét.

## Scope

- `VoteService` és `FederalVoteProposal` Pydantic modellek.
- BFS hivatalos kanton-kódolás (1=ZH .. 26=JU).
- 26 kanton valós adatai a `Map3D.tsx` és `swissCantons.ts` modulokban.

## Non-scope

- Községi (Gemeinde) szintű 2000+ településes szavazati bontás (első körben kantonális szint).

## Érintett rendszerek

- `src/models/vote.py`, `src/services/vote_service.py`, `src/main.py`, `frontend/src/app/Map3D.tsx`

## Bizonytalanságok

- Régebbi, 10+ évvel ezelőtti archív szavazási JSON-ok mezőszerkezetének kompatibilitása.
