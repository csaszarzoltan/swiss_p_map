# ADR-014: Többkantonos Építési Engedély Federáció (Bern, Basel, Genf)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** architect & QA lead (research: `docs/research/2026-08-27-multi-canton-planning.md`)
- **Kanban:** #swiss-p-map-014

## Kontextus
A Planning-pillér korábban csak Zürich kantonra rendelkezett építési adatokkal, így Bern (`3011`) vagy Basel (`4001`) keresésekor a Planning fül üres maradt.

## Döntés
1. **Országos Baugesuch Seed:** Bekötjük Bern, Basel és Genf aktív építési projektjeit a `planning_repo.py` induló készletébe.
2. **Kantonális szűrés a szövetségi Amtsblattból:** A `planning_service.py` kanton-paraméterezett lekéréseket hajt végre (`canton="BE"`, `canton="BS"`).
3. **Koordináták & Fellebbezési számláló:** Minden rekord pontos WGS84 koordinátával és 20 napos lejárati ablakkal rendelkezik.

## Elvetve
| Opció | Miért nem |
|---|---|
| Csak Zürich támogatása a v1-ben | Félrevezető lenne egy "Svájc P-térkép" esetén |

## Következmény
- A felhasználó Bernben (`3011`), Baselben (`4001`) és Zürichben (`8004`, `8001`, `8610`) egyaránt látja a valós/aktív építkezéseket.
- A 3D térképen a megfelelő kantonban ugranak fel a borostyánsárga jelölők.

## Kapcsolódó
- Research: `docs/research/2026-08-27-multi-canton-planning.md`
- Kód: `src/services/planning_service.py`, `src/db/planning_repo.py`, `src/main.py`
