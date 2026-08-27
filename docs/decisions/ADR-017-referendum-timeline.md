# ADR-017: Interaktív Történeti Szavazási Idővonal & Témaválasztó (Federal Referendum Selector)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** System Architect & QA Lead (research: `docs/research/2026-08-27-referendum-timeline.md`)
- **Kanban:** #swiss-p-map-017

## Kontextus
Az ADR-012 bevezette a valós szövetségi szavazási adatokat, de csak a 2024-03-03-as 13. AHV-Rente népszavazást jelenítette meg. Svájcban évi 4 népszavazási vasárnapon több mint 10-15 szövetségi ügy kerül szavazásra, amelyek mindegyike eltérő kantonális támogatottsági mintázatot mutat.

## Döntés
1. **Több-referendumos Adatbázis & Szolgáltatás:** A `VoteService` több előterjesztést kezel:
   - `6670`: 13. AHV-Rente (2024-03-03 — 58.2% Igen)
   - `6680`: BVG-Reform (2024-09-22 — 32.9% Igen)
   - `6690`: Ausbauschritt Nationalstrassen (2024-11-24 — 47.3% Igen)
   - `6700`: Stromgesetz (2024-06-09 — 68.7% Igen)
2. **REST API Bővítés:**
   - `GET /api/v1/politics/votes/list`: Elérhető szavazások listája (ID, címek 4 nyelven, dátum, országos eredmény)
   - `GET /api/v1/politics/votes/{proposal_id}`: Adott szavazás 26 kantonos részletezése
3. **Interaktív Témaváltó a 3D Kártyán:**
   - A 3D infódoboz tetején egy diszkrét szavazás-választó jelenik meg.
   - Kiválasztáskor a 3D kantonok azonnal az adott szavazás kantonális eredményeire frissülnek.

## Elvetve
| Opció | Miért nem |
|---|---|
| Csak egyetlen statikus szavazás megtartása | Nem mutatja be a svájci közvetlen demokrácia sokszínűségét és dinamizmusát |
| 100+ korábbi szavazás egyszerre történő letöltése | Növelné a kezdeti betöltési időt feleslegesen |

## Következmény
- A felhasználó összehasonlíthatja, hogyan szavazott például Zürich vagy Valais a nyugdíjreformra vs. az autópálya-bővítésre.
- A politikai pillér mély, interaktív elemzőeszközzé válik.

## Kapcsolódó
- Research: `docs/research/2026-08-27-referendum-timeline.md`
- Kód: `src/services/vote_service.py`, `src/models/vote.py`, `frontend/src/app/Map3D.tsx`
- Következő ADR: ADR-018 (Térbeli Sugár- és Poligon Keresőmotor)
