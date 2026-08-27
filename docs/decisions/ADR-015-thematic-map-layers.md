# ADR-015: Tematikus Térképi Hőtérkép & Rétegek (Sonnendach, Lärm, ÖREB 3D Vizualizáció)

- **Dátum:** 2026-08-27
- **Státusz:** accepted
- **Szerző:** System Architect & QA Lead (research: `docs/research/2026-08-27-thematic-map-layers.md`)
- **Kanban:** #swiss-p-map-015

## Kontextus
A felületen a felhasználó 6 téma között válthat (Übersicht, Politik, Ort, Planung, Sonnendach, ÖREB), de eddig a 3D térkép megjelenése statikus maradt. A valódi térinformatikai érték akkor érvényesül, ha a téma kiválasztásakor a 3D térkép anyaga és színezése azonnal tükrözi a témához kapcsolódó svájci adatréteget.

## Döntés
1. **Dinamikus Tematikus Színezési Motor (`Map3D.tsx`):**
   - **`politik` mód:** A kantonok színe a valós BFS Igen-szavazati arányt tükrözi (kék = magas jóváhagyás, korallvörös = elutasítás).
   - **`solar` mód:** A kantonok szolár potenciál színskálára váltanak (`#f59e0b` / `#fbbf24` arany izzás a magas napenergia-hozamú alpesi és déli kantonokban).
   - **`oereb` mód:** Kataszteri zónaszínezés (Kernzone = lila `#a855f7`, Wohnzone = kék, Freihaltezone = zöld).
   - **`overview` / `planung` mód:** Sötét kiber-üveg téma a kiemelt borostyánsárga építési jelölőkkel.
2. **GSAP Finom Átmenet:** A témaváltás nem ugrik, hanem 0.35 másodperces `color.lerp` és `opacity` átmenettel simán fuzionál.
3. **Tematikus Jelmagyarázat (Legend):** A 3D térkép jobb alsó sarkában dinamikus színmagyarázó sáv jelenik meg az aktuális mód skálájával.

## Elvetve
| Opció | Miért nem |
|---|---|
| Külön 2D térképre váltás minden menüpontnál | Megtöri az egységes 3D UX élményt és a felhasználói fókuszt |
| Nehéz WMS raszter textúrák streamelése Three.js-be | Mobil eszközökön és lassabb hálózaton akadozást és késleltetést okozna |

## Következmény
- A 6 fül közötti navigáció azonnali, látványos vizuális visszajelzést ad a térképen.
- A szövetségi BFE, BAFU és BFS adatok térbeli mintázatai (pl. Röstigraben, alpesi napsütéses órák) azonnal felismerhetővé válnak.

## Kapcsolódó
- Research: `docs/research/2026-08-27-thematic-map-layers.md`
- Kód: `frontend/src/app/Map3D.tsx`, `frontend/src/app/[locale]/page.tsx`
- Következő ADR: ADR-016 (Építési Projektek Részletező & Kockázatelemző Panel)
