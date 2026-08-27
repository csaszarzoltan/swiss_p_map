# ADR-019: Tematikus Jelmagyarázat (Map Legend)

- **Dátum:** 2026-08-28
- **Státusz:** accepted (jövő heti backlog #1)
- **Szerző:** researcher (research: `docs/research/2026-08-28-usability-deep-dive.md` Rank #1)
- **Kanban:** #swiss-p-map-019 — P0 | Epic: Térkép UX

## Kontextus

A Politics/Solar/ÖREB témaváltás után a 3D kantonok szép színe értelmezhetetlen, ha a user nem látja mit jelent a paletta [1][3]. `map.geo.admin.ch` a rétegekhez külön legendát mutat [1], a BFS pedig a szövetségi geoadatok forrását jelöli [3]. A Houzy lista-alert nézetben nincs színséma [2].

## Döntés

1. **Komponens:** `frontend/src/components/MapLegend.tsx` (~70 sor) — tematikus `switch(activeTopic)`: JA/NEM %, kWh/m², ÖREB-zóna típus; alatta forrás-link `BFS / BFE / BAFU` [1][3]. Nincs logika-változás a backenden, read-only komponens.
2. **Elhelyezés:** a 3D térkép jobb-alsó sarokban, `TopicSidebar` pill-tabs alatt, a `DetailPanel` fölé csatolva (desktop), mobilon a `Map3D` konténerbe overlay-ként.
3. **Trigger:** `activeTopic` prop (már él a `page.tsx`-ben); a Legend minden témaváltás után azonnal frissül [1].

## Elvetve

| Opció | Miért nem |
|---|---|
| WMS raszter legend stream | 35–50 FPS + GPU memória [ADR-015] — túl nehéz |
| Nincs legend (csak tooltip) | Tooltip mobilon láthatatlan, a11y fail |

## Következmény

- Kártya: `MapLegend.tsx` + `messages/de(en,fr,it).json` (+4 kulcs), max 70 sor.
- Validálás: `npm run build` + `npx playwright test` — `TopicSidebar` aktív Politics + Legend látható „JA:" szöveggel (RED→GREEN us_019_legend spec).
- Méret: max 400 sor/file OK; `src/` nem változik.

## Kapcsolódó

- Research: `docs/research/2026-08-28-usability-deep-dive.md` (§2.2 Rank #1)
- Kód: `frontend/src/components/MapLegend.tsx`
- Következő ADR: ADR-020 (Risk badge)
