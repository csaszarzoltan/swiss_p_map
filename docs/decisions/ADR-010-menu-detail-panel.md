# ADR-010: Menü + Részletező panel (UI architektúra refaktor)

- **Dátum:** 2026-08-27
- **Státusz:** proposed → **accepted** (emberi jóváhagyás: `[aaa bbb] mehet`)
- **Szerző:** analyst (research: `docs/research/2026-08-27-menu-detail-panel.md`)
- **Kanban:** swiss-p-map

## Kontextus

A Swiss P Map jelenleg egy 3D rendering engine bemutató: `page.tsx` (269 sor) monolitikus, lapos kártya 4 tabbal. Nincs navigációs menü, nincs részletező panel, a felhasználó nem tudja hol kezdje.

## Döntés

**Opció A: Bal sidebar + Alul részletező panel** (4.5/5 nyert) — geo.admin.ch mintára.

Layout: `TopicSidebar (bal 25%)` + `Map3D (közép)` + `DetailPanel (alul)`.

6 téma: Összes, Politik, Ort, Planung, Sonnendach, ÖREB — sidebar ikon+szám, kattintás→lista→részletező.

State: `activeTopic` (sidebar) + `selectedItem` (lista elem) — térkép reagál (`highlightTopic` prop).

5 komponens: `TopicSidebar.tsx` + `TopicList.tsx` + `DetailPanel.tsx` + `page.tsx` refactor + `Map3D.tsx` bővítés. Max 400 sor/file, `messages/*.json` bővítés 4 nyelven.

## Elvetve

| Opció | Miért nem |
|---|---|
| B: Felső menü sor | kevesebb hely a részletezőnek, nem OGD standard |
| C: Alsó sáv + csúszó panel | rejtett, nem nyilvánvaló, animáció kezelés |

## Következmény

- Kártyák: `TopicSidebar + TopicList + DetailPanel + page refactor + Map3D bővítés`
- Validálás: E2E PW: sidebar→téma→lista→részletező látható, 4/4 nyelv, build SSG
- Max 3 file/lépés: 1) research+ADR 2) komponensek 3) refactor+teszt

## Kapcsolódó

- Research: `docs/research/2026-08-27-menu-detail-panel.md`
- Kód: `frontend/src/components/{TopicSidebar,TopicList,DetailPanel}.tsx`
- Következő ADR: — (ez a UI architektúra alapja)
