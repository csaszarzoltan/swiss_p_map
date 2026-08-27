# ADR-013: 3D Építési Projektek & Interaktív Markerek (3D Baugesuch Pins)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** architect & QA lead (research: `docs/research/2026-08-27-3d-baugesuch-pins.md`)
- **Kanban:** #swiss-p-map-013

## Kontextus
A Planning-pillér legfőbb értéke az építési projektek térbeli láthatósága. Bár a backend 22k rekordot kezel, a 3D térképen koordináta-hiány miatt alig jelentek meg markerek.

## Döntés
1. **Koordináták biztosítása a backfillben:** Az `ogd_service.py` a cím/irányítószám alapján determinisztikus WGS84 koordinátákat rendel minden Baugesuch rekordhoz, így 100%-uk térképesíthetővé válik.
2. **3D Pin Stílus és Animáció:** A `Map3D.tsx` lüktető borostyánsárga jelölőket rajzol ki az aktív építkezésekhez.
3. **Fellebbezési Időablak Kiemelés:** A lebegő infókártya automatikusan jelzi a kerületben aktív, 20 napos fellebbezési határidőn belüli projektek számát.

## Elvetve
| Opció | Miért nem |
|---|---|
| Csak táblázatos megjelenítés | Nem adja meg a svájci környék 3D térbeli rálátását |
| Minden egyes címre külön élő REST geokódolás | 22k hívás blokkolná az upstream API-t és a szervert |

## Következmény
- Bármely zürichi vagy egyéb körzetben a keresés azonnal 3D markerekkel népesíti be a térképet.
- Teljes összhang a 3D nézet és az alsó részletező lista között.

## Kapcsolódó
- Research: `docs/research/2026-08-27-3d-baugesuch-pins.md`
- Kód: `src/services/ogd_service.py`, `frontend/src/app/Map3D.tsx`
- Következő ADR: ADR-014 (Többkantonos Építési Engedély Federáció)
