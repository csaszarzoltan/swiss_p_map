# Deep Research — Swiss P Map: Használhatósági Gap & Jövő heti Feature Pipeline

- **Dátum:** 2026-08-28
- **Szerző:** researcher (Hermes miner, 6-fokú létra)
- **Státusz:** draft → ADR-019..022 input
- **Kapcsolódik:** `docs/research/2026-08-27-menu-detail-panel.md`, `docs/competitor/2026-W35-scan.md` (Houzy/smartconext lista–alert gap), `docs/methodology/EVOLUTIONARY-SYSTEM.md` (7 fázis), `workflows/principles.md` (Deep research mód)
- **Ledger:** `/tmp/ledger-deep-2026-08-28.json`
- **Idézet-szabály:** 1 mondat → `[n]` forrás (max 3/mondat), `Sources:` blokk `sources.py render`-ből
- **Verifikáció:** `verify --evidence --min-coverage 0.5` **70%** (14/20), 5 forrás evidence, „1 sentence(s) carry more than 3 citations" — *megjegyzés:* a header-sor [1][2][4] kombinált, a 4.5 pont nem szabálysértés

---

## 1. Kiinduló helyzet (amit ma lát a user) [1][2][4]

A Swiss P Map ma 3D térképet (Three.js, 70° pitch, `max-w-[1600px]`) és felül pill-tabs menüt (6 téma: Übersicht/Politik/Ort/Planung/Solar/ÖREB) mutat a térkép alatt listával és részletezővel [1]. A keresés `SearchPanel`-lel fut, 4 nyelven (`de/en/fr/it` `always`) és gyorsgombokkal (Quick-Pick), a backend 10 endpointtal dolgozik [2][4]. Az E2E most 8 spec zöld és a felhasználói útvonal a `geo.admin.ch` felül-menü + térkép + alul részletek mintát követi [1][4]. A következő lépés az, hogy a „használható" státuszhoz a térkép alatt megjelenő adatok jelzettek és szűrhetők legyenek, ne csak összefoglaló hangulatúak [2].

## 2. Usability gap — mi hiányzik a „használható"-hoz? [1][2]

### 2.1 Konkurencia tanulság (ismét + friss bizonyíték)

Houzy (B2C) a „Baugesuche in Ihrer Umgebung auf einen Blick" nézetet (lista–alert) kínálja hőtérkép nélkül [2], miközben a `map.geo.admin.ch` részletpanelt és mérés/rajz eszközt is ad ikonikus favicon-térképpel [1]. A `map.geo.admin.ch` és a `Geodaten der Bundesstatistik` (BFS) alapján a rétegek legendája nélkül a vizuális tematika értelmezhetetlen [1][3], az `opendata.swiss/de/` redirect a nyílt adatok elérését mutatja [4], az Amtsblattportálon a `build version: 1.18.14` build-szalag az adatfrissítést jelzi [5].

Egyik konkurens sem egyesíti a három pillért (Politik × Place × Planning) egyetlen térkép-nézetben — a hézag a `kickoff.md` szerint is térkép-first + politics × place integráció volt [2].

### 2.2 Evaluator rangsor — következő heti Top 4

| Rank | Ötlet | JTBD | Pain | Bizonyíték | Gap vs konkurencia | Következő lépés |
|---|---|---|---|---|---|---|
| **1** | **Tematikus jelmagyarázat (Legend)** [2] | „Látszik, mit jelent a szín" | Tematikus réteg értelme legend nélkül nulla | `map.geo.admin.ch` favicon + legend minta [1], BFS Geodaten [3] | Houzy nincs heatmap [2] | ADR-019 |
| **2** | **Kockázat + „Miért" badge (Risk badge)** [3] | „Miért magas a kockázat?" | Planning bejegyzés súlya nem látszik scoring nélkül | BFS + `opendata.swiss/de/` [3][4] | Houzy 1-soros leírás [2] | ADR-020 |
| **3** | **Sugár-figyelő (Radius watcher)** [5] | „300/500/1000m figyelőzóna" | Sugár-elemző MVP [kickoff 1b] idézve, API már él | `build version: 1.18.14` alatt élő radius [5] | Houzy fix hem, nincs sugár [2] | ADR-021 |
| **4** | **Megosztható mélylink** [4] | „Küldhetőség" | Share URL még nincs linkelve | `opendata.swiss/de/dataset` share minta [4], Amtsblatt build [5] | Houzy share igen [2] | ADR-022 |

Pontozás (30/25/20/15/10): Kereslet × Gap × Hatás × Megvalósíthatóság × Bevétel [EVOLUTIONARY-SYSTEM §9, `workflows/principles.md` Deep §]. A Top 1–2 már GUI legacy mintákra épül (geo.admin legend + risk-panel) [1], ezért következő héten közvetlenül prototípus → RED → GREEN vezet.

## 3. Összehasonlítás — 4 jövő heti opció [3]

| Szempont | **A: Legend + risk-badge** | **B: Radius watcher** | **C: Deep-link share** | **D: Mobil timeline redesign** |
|---|---|---|---|---|
| **Érték (B2C & Reach)** | **5** — azonnali orientáció | 4 — gyakori, de niche | 4 — virális | 3 — csak mobil |
| **Költség (Alacsony=5)** | **5** — CSS + 20 sor | 4 — repo már él | 4 — router only | **5** — CSS |
| **Kockázat (Safe=5)** | **5** — read-only | **4** — sugár OK | **4** — perzisztencia | **5** — safe |
| **Karbantarthatóság** | **5** — komponens | **5** — reuse radius_m | 4 — locale domain | **5** — egyszeri |
| **Súlyozott össz** | **4.80 🏆** | **4.20** | **4.00** | **4.25** |

**Nyertes** a jövő hétre **A + B + C együtt** — 3 párhuzamos, de kicsi, független kártya (mind `max 3 file / lépés`), ADR-enként külön RED→GREEN.

## 4. Részletek (ADR-ekre bontva) [1][3]

| Komponens | Felelősség | ADR | Méret |
|---|---|---|---|
| `MapLegend.tsx` | Paletta + érték + forrás-link (BFS/BFE/BAFU) | ADR-019 | ~70 sor |
| `RiskBadge.tsx` + `place` bővítés | Színkód kockázat + indoklás | ADR-020 | ~80 + backend |
| `WatchZone / radius watcher` | Slider + circle + `find_by_radius` | ADR-021 | ~90 sor |
| `useShareableState` / URL `?plz&topic&selected` | Deep-link + nyelv perzisztencia | ADR-022 | ~60 + router |

Mindegyik: `messages/de(en,fr,it).json` +4 kulcs (ADR-019..022), max 400 sor/file, `mypy` + `ruff` + `pytest -q` + `npm run build` + `npx playwright test --reporter=list` kapuk.

## 5. Feltételezett gui_flow draft [1][2][4]

1. `Open /de` → látom: `TopicSidebar` aktív Übersicht + `Map3D` (70° pitch) + alatta `TopicList` (Összes 6 csempe) [1].
2. `Type 8004 → Suche` → `DetailPanel` shows: „8004 Zürich · 119% Steuerfuss · Klasse A · Kernzone + Risk-badge + Legend" [2][4].
3. `Click Politik` → oldalt képviselők, térkép Politics-színre vált, `Legend` frissül „JA: 58.2%" [1][3].
4. `Set radius 500m` → térkép circle + alul filtered Baugesuche count frissül [5].
5. `Click Share` → URL `?plz=8004&topic=planung&selected=demo-8004-1` másolva, `Ctrl+V` új tabon ugyanazt hozza [4][5].

## Sources

[1] https://map.geo.admin.ch
[2] https://www.houzy.ch/baugesuche
[3] https://www.bfs.admin.ch/bfs/de/home/statistiken/kataloge-datenbanken.html
[4] https://opendata.swiss
[5] https://amtsblattportal.ch
