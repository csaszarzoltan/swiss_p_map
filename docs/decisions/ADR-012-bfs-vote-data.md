# ADR-012: Valós Szövetségi Népszavazási Adatok (BFS / FSO Vote Data)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** architect & QA lead (research: `docs/research/2026-08-27-bfs-vote-data.md`)
- **Kanban:** #swiss-p-map-012

## Kontextus
A 3D térképen a kantonok lebegő infódobozában eddig beégetett minta szavazati arányok (`61.4% JA`) jelentek meg. A felhasználóknak valós, megbízható politikai képre van szükségük. A svájci Szövetségi Statisztikai Hivatal (BFS) nyílt VoteInfo OGD API-n keresztül közzéteszi az összes hivatalos szövetségi népszavazás eredményét kantonális bontásban, 4 nyelven.

## Döntés
1. **VoteService & Domain Modell:** Létrehozunk egy `VoteService` osztályt és `FederalVoteProposal` Pydantic modellt.
2. **Beágyazott Alapértelmezett Referendum + Élő Letöltés:** Az azonnali offline stabilitás és gyors indítás érdekében a legfontosabb mérföldkő-szavazás (13. AHV-nyugdíj / BVG) adatai helyben gyorstárazva állnak rendelkezésre, miközben az API képes a legfrissebb szövetségi JSON letöltésére.
3. **4-nyelvű címek és 26 kanton:** Minden kanton (ZH, BE, LU, UR, SZ, OW, NW, GL, ZG, FR, SO, BS, BL, SH, AR, AI, SG, GR, AG, TG, TI, VD, VS, NE, GE, JU) valós, pontos Igen/Nem százalékot kap.
4. **Végpont:** `GET /api/v1/politics/votes/latest` visszaadja az aktuális szavazás adatait a frontend és egyéb API fogyasztók számára.

## Elvetve
| Opció | Miért nem |
|---|---|
| Csak mock adatok használata | Nem felel meg az éles elvárásoknak és a valós használhatóságnak |
| Közvetlen böngészős lekérés az S3 JSON-ra | CORS korlátok és hálózati lassulás kockázata |

## Következmény
- A 3D térkép kanton infódoboza a valós népszavazási adatokat jeleníti meg a kanton felett.
- A szavazás címe megjelenik a statisztikai kártyán.
- 50+ automatizált teszt lefedettség biztosítja a formátum és a végpont stabilitását.

## Kapcsolódó
- Research: `docs/research/2026-08-27-bfs-vote-data.md`
- Kód: `src/models/vote.py`, `src/services/vote_service.py`
- Következő ADR: ADR-013 (3D Építési Projektek Interaktív Markerei)
