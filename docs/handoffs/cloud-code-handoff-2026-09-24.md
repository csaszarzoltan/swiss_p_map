# Cloud Code handoff — Swiss P Map pillanatkép (2026-09-24, v0.3.0)

> Cél: Cloud Code vegye át a következő fejlesztési hullámot. Ez a dokumentum a teljes kontextust adja — olvasd el, válassz következő lépést, dolgozd ki a SPEC-et, és implementáld TDD-vel.

## 1. Mi ez a projekt?

**Swiss P Map** — "A svájci környék egyetlen térképén" (Politics × Place × Planning + ebből generált 2-mondatos AI-összefoglaló).
- **Célközönség:** svájci lakosok (DE/EN/FR/IT), akik költözés / építkezés / helyi ügyek előtt döntést hoznak.
- **Értékígéret:** adó × építés × életvitel × proaktív értesítés egyetlen térképen, nem 4 külön portálon.
- **Repo:** `github.com/csaszarzoltan/swiss_p_map` · branch `master` · jelenleg **v0.3.0** (`4dfb106`, tag pusholva)
- **Élő környezet:** BE `0.0.0.0:8310` + FE `3310/3410` (NEXT_PUBLIC_API_URL=`http://144.91.73.225:8310`)
- **Módszertan:** `AGENTS.md` + `METHODOLOGY.md` + `docs/methodology/EVOLUTIONARY-SYSTEM.md` (7 fázis, behavior-first, 100% E2E, stop-gate) + `workflows/principles.md`
- **Szabályok:** research → ADR (proposed→accepted) → kód; max 400 sor/file; type hints + docstring; commit `<scope>: <leírás>`; max 3 file/lépés; RED→GREEN TDD; LLM-független teszt+dokumentáció. **Kódolás CSAK kanban-kártyával** — `hermes kanban boards switch swiss-p-map`.

## 2. Stack (ADR-001)

| Réteg | Választás |
|-------|-----------|
| Frontend | Next.js 14 App Router, TS strict, Tailwind, Three.js 0.160 ESM + R3F + OrbitControls, gsap 3.12, d3-geo mercator, swiss-maps@4 ch-combined.json, next-intl 3.26.5 (de/en/fr/it, localePrefix:'always'), MapLibre kivezetve |
| Backend | Python 3.11 FastAPI + Pydantic + httpx + pyproj/shapely + PostGIS (később), LV95/EPSG:2056↔WGS84 |
| DB | SQLite `data/swisspm.db` (séma-migráció induláskor), demo seed `8004:2 3011:2 4001:1` |
| Infra | BE `uvicorn 0.0.0.0:8310`, FE `next start 3310/3410` (közvetlen `node_modules/.bin/next`, DBUS wrapper `env -u DBUS_*`) |

## 3. Hol tartunk — számokban

- **56 route** (`openapi.json`), **57 BE route** (`src/main.py` + `/health`)
- **238 passed, 1 skipped** (`pytest`), **91 source files mypy clean**, `ruff clean`, `tsc --noEmit` + `build SSG` zöld, **8/8 Playwright E2E** (37s)
- **23 ADR** (ADR-001…023, mind accepted; ADR-023 2026-09-24)
- **60 SPEC**, `docs/audits/SPEC-coverage-2026-09-23.md` mátrix: 34 COVERED + 16 INDIRECT + 10 NONE (frontend/vizuális)
- **Kanban:** `swiss-p-map` board, 18 done + 4 új (ADR-023 A/B/C + release), jelenleg 0 nyitott

## 4. Mit építettünk eddig (időrend, commit-lánc)

```
v0.1.0 bootstrap (AGENTS, METHODOLOGY, scaffold, CI)
  → v0.2.0 i18n 4 nyelv + Politics/Place live (PARIS-API, api3, BFE Solar 1208 kWh/m², ZH WFS Kernzone, ZH Steuerfuss 119%, OGD backfill 22k)
  → v0.2.1 OGD 2982 22141 sor
  → 703aa91 séma-migráció + ADR-012 BFS szavazás (13. AHV-Rente 58.2%) + dead code fix
  → SPEC-051 VotingVisualCard + 052 WeatherWidget + 053 WasteCalendar (.ics) + 054 CostOfLiving (élő adatok)
  → SPEC-045 LocalInformationHub i18n/a11y + SPEC-047/058 Amtsblatt hír-pipeline (valós XML, idempotens upsert)
  → SPEC-coverage audit (60 SPEC mátrix) + contract-mélység 046/055/056/057/059/060 (24 új teszt)
  → ADR-023 research (2026-09-23 proaktív civic features) — versenytárs-rés: swisstaxmap/moneyland/comparis/houzy/geoda mind egy-doménes
  → ADR-023/A watch-zone értesítési lánc (3edb777): WatchZone CRUD consent-kapu, WatchStore dedup, WatchMatcher, 5 endpoint, push→WebPush + email→Newsletter, publication+20 nap → deadline/days_left (open/due_soon≤3/expired), REQ-B3 disclaimer
  → ADR-023/B watch UI (3370820): WatchEventsCard event-lista + Einsprachefrist visszaszámláló + consent-gated channel-választó, 4 nyelv, 11 unit + 10 E2E
  → ADR-023/C ÖREB zóna (c02048c): OerebService OGC API LV95 (bbox-crs+crs kötelező, 0.36-formula), kanton-detektálás, GET /api/v1/cadastre/zone (GE:Mischzonen live, ZH:source_pending honest), 24h cache
  → v0.3.0 release (4dfb106) — 69 commit v0.2.1 óta
```

### Élő bizonyíték (2026-09-24, magam teszteltem, nem worker-állítás)

- `POST /watch/zones consent=false` → `consent_required: REQ-A1` elutasítva
- Ismételt `/watch/run` → 3 deduplikált, nincs dupla értesítés
- `GET /cadastre/zone?lat=46.20&lon=6.14` (GE) → `Mischzonen inKraft official_measurement`
- `GET /cadastre/zone?lat=47.378&lon=8.534` (ZH) → `source_pending` + `https://maps.zh.ch/` (becsületes fallback)
- `GET /watch/deadlines?postcode=8004` → Einsprachefrist élő, due_soon/expired színezés

## 5. Minden ADR (23 db)

| ADR | Cím | Státusz |
|-----|-----|---------|
| 001 | Stack + architektúra | accepted |
| 002 | Data ingestion pipeline | accepted |
| 003 | Map 3D schematic (Three.js) | accepted |
| 004 | i18n next-intl 4 nyelv | accepted |
| 005 | Politics/Place live | accepted |
| 006 | AI summary gateway (8013, fallback sablon) | accepted |
| 007 | Ort expansion (6 csempe + 3D overlay) | accepted |
| 008 | ZH Steuerfuss live (HTML scrape) | accepted |
| 009 | OGD backfill (22k) | accepted |
| 010 | Menu detail panel | accepted |
| 011 | Federal place expansion (ARE/BAFU/BFE) | accepted |
| 012 | BFS vote data (26 kanton) | accepted |
| 013 | 3D Baugesuch pins (amber pulse) | accepted |
| 014 | Multi-canton planning federation (8004/3011/4001/1201) | accepted |
| 015 | Thematic map layers | accepted |
| 016 | Baugesuch deep inspector | accepted |
| 017 | Referendum timeline | accepted |
| 018 | Spatial radius engine | accepted |
| 019 | Map legend | accepted |
| 020 | Risk badge | accepted |
| 021 | Radius watcher | accepted |
| 022 | Shareable link (locale-aware deep-link) | accepted |
| 023 | Watch-zone értesítési lánc + Einsprachefrist (A/B/C) | accepted 2026-09-24 |

## 6. SPEC-lefedettség (audit 2026-09-23)

- **34 COVERED** (unit + API, REQ/AC nyomkövetett) — köztük 045/046/047/051-060 mind
- **16 INDIRECT** (ADR-címke vagy névtelen service-teszt: 001,002,005-009,011,012,014,016-019,022,023)
- **10 NONE** — mind frontend/vizuális, nincs Python-tesztnyom: **003,004,010,013,015,020,021,024,031,044**
- **3 PLACEHOLDER** (`assert True` csonk): 025,027,030
- Legutóbbi audit: `docs/audits/SPEC-coverage-2026-09-23.md` (134 sor, 60 SPEC mátrix)

## 7. Ismert rések / tech adósság

1. **Frontend E2E-rés:** 003/004/010/013/015/021/024/031/044 — csak `045/051-054` van Playwright-tel fedve.
2. **PWA offline (SPEC-027):** `PwaStatus` komponens van, de placeholder teszt.
3. **Export/audit-csomag (SPEC-020):** nincs route.
4. **Konnektorok statikusak:** MeteoSwiss 21.5°C, SBB 2 fix indulás, VoteInfo 1 sor — élő provider-hívás még nincs (szerződés + trust-meta van, élősség nincs).
5. **SPEC-055 §8 második endpoint** (`/meteoswiss/alerts`) nem létezik (csak `/current`).
6. **Board-flakiness:** más session-ök átváltják a boardot `veritas-dogfood`-ra → `create` előtt mindig `boards list | grep ●` ellenőrzés kötelező.

## 8. Kérdés Cloud Code-nak: mi legyen a következő?

Három opciót pontoztam (érték × költség × kockázat × karbantarthatóság, 1-5, magasabb = jobb; kockázat/karbantarthatóság fordított skála a táblában):

| Opció | Leírás | Érték | Költség | Kockázat | Karbant. | Össz. |
|-------|--------|-------|---------|----------|----------|-------|
| **A — Frontend E2E + PWA + Export bezárása** | 10 NONE SPEC-re Playwright + SPEC-027 PWA offline + SPEC-020 export route | 4 | 3 | 4 | 4 | **15** |
| **B — Élő konnektorok (MeteoSwiss/SBB/VoteInfo)** | statikus mock → élő provider (cache + fallback, trust-meta marad) | 5 | 2 | 2 | 3 | 12 |
| **C — Tematikus rétegek + megosztás (015/024/021)** | heatmap/layers + deep-link + legend E2E | 3 | 3 | 4 | 4 | 14 |

**Ajánlásom: A** — a v0.3.0 után a legnagyobb kockázat a frontend regresszió (10 SPEC teszt nélkül). Az A bezárja a SPEC-mátrixot és a PWA/Export adósságot, mielőtt új élő integrációkat nyitnánk. De Cloud Code döntsön — mindhárom valid.

### Mit kérek Cloud Code-tól?

1. **Válassz** a 3 opció közül (vagy javasolj negyediket, ha lát jobb rést).
2. **Dolgozd ki** a részletes követelményt: SPEC-kiegészítés vagy új SPEC, REQ/AC bontás, API-kontraktus, i18n-kulcsok, E2E-forgatókönyvek.
3. **Implementáld** TDD-vel (RED→GREEN), max 3 file/lépés, kanban-kártyán (`swiss-p-map` board, `●` ellenőrzéssel), kapuk: `pytest 238+`, `mypy 91 clean`, `ruff`, `tsc+build`, `8/8+ E2E`.
4. **Dokumentáld:** ADR ha architekturális döntés, CHANGELOG `[Unreleased]`, README frissítés.

## 9. Hogyan dolgozz (Cloud Code bootstrap)

```bash
# 1. Olvasd el (sorrendben):
cat AGENTS.md
cat workflows/principles.md
cat METHODOLOGY.md
cat docs/methodology/EVOLUTIONARY-SYSTEM.md
cat docs/decisions/ADR-023-watch-zone-alert-pipeline.md
cat docs/audits/SPEC-coverage-2026-09-23.md
cat docs/research/2026-09-23-proactive-civic-features.md
cat CHANGELOG.md | head -60

# 2. Ellenőrizd a boardot MINDIG:
hermes kanban boards list | grep "●"   # swiss-p-map kell legyen!
hermes kanban boards switch swiss-p-map
hermes kanban list | tail -5
git pull --rebase && git status --short
curl -s http://127.0.0.1:8310/health   # version 0.3.0 kell legyen

# 3. Research → ADR → kanban → kód (TDD) → kapuk → E2E → commit → push
# Hotspot-fájlok (max 3/lépés!): src/main.py, frontend/src/lib/api.ts, messages/*.json
```

## 10. Kapcsolat

- **Hermes (én):** kanban `swiss-p-map`, BE/FE újraindítás `env -u DBUS_*` wrapperrel, FE build `NEXT_PUBLIC_API_URL=http://144.91.73.225:8310`
- **Te (Cloud Code):** dolgozz a `swiss-p-map` boardon, `developer` vagy `release-manager` szerepben, láncolt kártyákkal ha hotspot-ütközés van.
- **Kérdés esetén:** írj ADR-t `docs/decisions/ADR-024-*.md` (template: `ADR-000-template.md`), státusz `proposed` → implementálás után `accepted`.

---
*Generálva: 2026-09-24 15:30 UTC · Hermes Agent · v0.3.0 (4dfb106) · 238 passed / 91 mypy / 8/8 E2E*
