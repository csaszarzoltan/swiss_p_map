# Changelog — Swiss P Map

Minden jelentős változás ebben a fájlban dokumentálva. Formátum: Keep a Changelog + SemVer.

## [0.3.0] - 2026-09-24

### Added
- **SPEC-051: VotingVisualCard élő adatokkal**: `GET /api/v1/votes/proposals` + `/{id}/analysis` proposal-választóval, last-request-wins, loading/empty/error állapotok, `SourceTrustBadge` (`frontend/src/components/civic/VotingVisualCard.tsx` + `test_spec051_voting_contract.py`)
- **SPEC-052: WeatherVisualWidget élő MeteoSwiss/Open-Meteo adatokkal**: live forecast + alerts/water `source_pending` (soha nem hamis official adat), `Forecast` típus (`WeatherVisualWidget.tsx` + `test_spec052_weather_contract.py` 14 teszt)
- **SPEC-053: WasteCalendarVisual élő adatokkal + valós .ics**: `GET /api/v1/municipal/waste-calendar` relatív nap-visszaszámlálással, valós `.ics` export (`MunicipalService.waste_ics`, `text/calendar`), relatív schedule tesztek (`test_spec053_waste_calendar.py`)
- **SPEC-054: CostOfLivingCalculator teljes lebontás + disclaimer**: housing/tax/health/commute/remaining sorok összegzése totalra, `size_m2` paraméter (default 80), `modeled_estimate` trust (`test_spec054_cost_of_living.py`)
- **ADR-023: watch-zone értesítési lánc + Einsprachefrist-menedzser**: `WatchZone` CRUD consent-kapuval, `WatchStore` SQLite dedup `(zone_id,baugesuch_id,kind)`, `WatchMatcher` determinisztikus távolság-szűrés, események `source/fetched_at/trust_state`-tel, push → `WebPushService` + e-mail → `NewsletterService` double opt-in (queued, soha nem hamis `sent`), `publication_date + 20 nap` → `deadline/days_left` (`open`/`due_soon ≤3 nap`/`expired`), REQ-B3 disclaimer (`src/services/watch_service.py` 594 sor + 5 endpoint: `POST/GET /api/v1/watch/zones`, `GET /api/v1/watch/events|deadlines`, `POST /api/v1/watch/run`, `test_adr023_watch_zone.py` 33 teszt)
- **ADR-023/B: watch-zone notification UI + Einsprachefrist countdown**: `WatchEventsCard` event-lista + határidő-visszaszámláló + consent-gated channel-választó (`push|email`), `resident.feature023` szótárak 43 kulccsal × 4 nyelv, `frontend/tests/unit/adr023-watch-ui.test.mjs` 11 zöld + e2e `watch-events-card.spec.ts` 10 teszt
- **ADR-023/C: kanton-tudatos ÖREB Nutzungsplanung zóna-lekérdezés**: `GET /api/v1/cadastre/zone` lat/lon-ra (OGC API LV95, honest `source_pending`, 24h cache; ZH-ra a meglévő WFS Nutzungsplanung marad), provider-hiba → kontrollált 503 (`src/services/oereb_service.py` + `test_oereb_zone.py`)
- **SPEC-coverage audit (mind a 60 SPEC)**: `docs/audits/SPEC-coverage-2026-09-23.md` SPEC→testfile mátrix, contract-mélység SPEC-046/055/056/057/059/060 (`test_spec046_055_060_contract.py` 24 contract-teszt REQ/AC traceability-vel, mutation-checked: 3 mutáció → 5 failure)
- **SPEC-045: LocalInformationHub i18n + traceability + a11y**: `resident.feature045` szótárak (de/en/fr/it), SPEC-045/REQ-045/AC-045 traceability ID-k, tablist arrow-key/Home/End navigáció + Escape-zárás, last-request-wins, E2E (`test_local_information_hub.py`)
- **SPEC-047/058: Amtsblatt hír-pipeline élőre kötése**: valós XML fetch `AmtsblattService`-en át, idempotens SQLite upsert (ingested/skipped számlálók, canton paraméter), postcode-szűrt `GET /api/v1/news/local` (`AmtsblattNewsPipeline`, `test_spec047_058_news_pipeline.py` 12 teszt)
- **SPEC státuszszinkron**: SPEC-045/047/051/052/053/054/058 `implementationStatus: IMPLEMENTED` (frontmatter + 1. fejezet törzsszöveg), kód+teszt evidenciával validálva
- **ADR-012: Valós Szövetségi Szavazási Adatok (BFS/FSO)**: Hivatalos népszavazási eredmények (`13. AHV-Rente`) mind a 26 kantonra valós Igen/Nem százalékkal és 4-nyelvű címekkel (`GET /api/v1/politics/votes/latest`)
- **ADR-013: 3D Interaktív Építési Markerek**: Borostyánsárga lüktető 3D Three.js pin jelölők, fellebbezési időablak visszaszámláló és raycasting alapú projekt-kattintás
- **ADR-014: Többkantonos Építési Engedély Federáció**: Bern (`3011`), Basel (`4001`), Genf (`1201`), és Zürich (`8004`, `8001`, `8610`) aktív építési projektjeinek integrációja
- Fejléc branding & integrált vezérlők: `Swiss P Map` logó, svájci kereszt jelvény, integrált fejléc sáv
- Quick-Pick keresési gyorsgombok (`8004 Aussersihl`, `8001 Altstadt`, `8610 Uster`, `3011 Bern`, `4001 Basel`) azonnali adatbetöltéshez
- User Story: `docs/stories/US-001-navigation-and-ui.md` 5 elfogadási kritériummal és `gui_flow`-val
- **ADR-011: Országos Hely- és Körzetfeloldás** (Bern `3011`, Basel `4001`, Uster `8610`, Genf `1201`) szövetségi ARE, BAFU és BFE rétegekkel és kantonális politikai képviselettel

### Fixed
- **3D Térkép kanton határok helyreállítása**: 7 kanton (BE Bern, FR Fribourg, SO Solothurn, BL Basel-Landschaft, SH Schaffhausen, TG Thurgau, OW Obwalden) csonka/exklávé poligonjainak helyreállítása teljes 26-kantonos szilárd 3D geometriára
- CORS default originek bővítése: `localhost:3410` és `127.0.0.1:3410` támogatása a port-ütközések elkerülésére
- Map3D lokalizáció: hardkódolt magyar feliratok (`É` iránytű, `IGEN/NEM`, `Népesség`, `Terület`, `Támogatottság`) átvezetése mind a 4 nyelvi szótárba (`de`, `en`, `fr`, `it`)
- Ghost UI hint javítása: az elavult "balra" útmutatás cseréje aktuális felső téma-választóra
- Mobilos reszponzivitás: a lebegő nyelvválasztó és 3D panel képernyőmérethez igazítása

### Verified
- `pytest tests/unit`: **129 passed** (100% green)
- `mypy src`: **47 source files clean (0 errors)**
- `ruff check src tests`: **All checks passed**
- `tsc --noEmit` + `npm run build`: **clean (SSG)**
- `npx playwright test`: **8/8 passed (43.3s)** — Hero, 3D Canvas, N Iránytű, Témák, PLZ 8004 keresés, Quick-Pick 8001, 4 locale (DE/EN/FR/IT), Valós BFS szavazás & Többkantonos Planung (3011 Bern & 4001 Basel)
- **ADR-019…022 usability package**: tematikus `MapLegend` (Politics/Solar/ÖREB paletták + forrás-hivatkozások), `RiskBadge` (`low/medium/high` + „Miért?" tooltip, visszafelé kompatibilis `risk_level`/`risk_reason` Place-mezők), radius-watcher (`WatchZone` 300/500/1000 m, `AbortController`, meglévő `/api/v1/planning/radius` újrahasznosítva), megosztható locale-aware mélylink (`useShareableState` + `ShareButton` + vágólap-visszajelzés, 4 lokalizáció)

### Verified
- `pytest`: **238 passed, 1 skipped** (unit 195 + E2E/API 43)
- `mypy src tests`: **91 source files clean (0 errors)**
- `ruff check src tests`: **All checks passed**
- `tsc --noEmit` + `npm run build`: **clean (SSG)**
- Frontend unit: **11/11 passed** (`adr023-watch-ui.test.mjs`)
- Backend útvonalak: **57 route** (`src/main.py`), API endpointok: **56 egyedi path** (+ `/health`)

## [0.2.1] - 2026-08-27


### Added
- OGD 2982 backfill: `GET daten.statistik.zh.ch/.../KTZH_00002982_00006183.csv` **22k sor**, `POST /api/v1/planning/backfill → {count 22141, source ogd}` — `ADR-009` hibrid 4.25/5
- Backend 8 endpoint: `ogd_service.py 97 sor` (csv.DictReader, postcode direct, idempotens upsert), `planning_service.backfill_ogd`, `place_service 400 sor` (határ)
- Frontend BASE fix: `frontend/src/lib/api.ts 8000→8310` + `NEXT_PUBLIC_API_URL 8310` — build SSG, FE restart 572ms

### Changed
- README: ADR-009 + `ogd_service` + `8 endpoint + /backfill` + `22k Baugesuche` + `47 passed / 18 mypy`
- `place 8004?live`: `solar 1208 sehr gut` + `Kernzone` + `zh-steueramt-html` steady, `planning 8004: 2 demo → 4 items (22k történeti)`

### Verified
- `BE 8310 v0.2.1` + `POST /backfill 22141` + `place 8004?live solar 1208 Kernzone` + `FE 3310 lang de/en/fr/it 200` + `47 passed mypy 18 build SSG 4/4 PW 21.2s`

## [0.2.0] - 2026-08-27

### Added
- i18n 4 nyelv: `next-intl 3.26.5` `always` hreflang/sitemap — `ADR-004` (research 4.75/5), `messages/{de,en,fr,it}.json`, `SearchPanel`+`Map3D` localizáció
- Politics live: PARIS-API CQL postcode→Wahlkreis → `?live=true` — `ADR-005`
- Place live: `api3 Identify` ARE ÖV-Güteklasse + BAFU Lärm — `ADR-005`
- Place Ort expansion: 6 csempe (solar sárga + öreb lila) + 3D overlay — `ADR-007 4.50/5`
- AI summary: `POST /api/v1/ai/summary` llm-budget-gateway `8013` → fallback sablon 4 nyelven — `ADR-006 4.62/5`
- ZH Steuerfuss live: `steueramt.zh.ch` HTML `119%` `zh-steueramt-html` — `ADR-008 4.12/5` + `test_place_zh_steuerfuss 2/2`
- Solar live fix: BFE WGS84 `POSTCODE_WGS84 8.534,47.378` klasse 4 `sehr gut` `mstrahlung 1208 kWh/m²` — kutatás `2026-08-27-solar-live-fix`
- ÖREB live: ZH WFS `maps.zh.ch/wfs/OerebKatasterZHWFS` `ms:Nutzungsplanung` → `Kernzone` — kutatás `2026-08-27-oereb-live`
- Planning live: `POST /api/v1/planning/refresh` Amtsblatt XML napi poll `?live` + SQLite WAL — `ADR-002`
- FE Ort svájci térkép: `Map3D` 70° pitch + Wahlkreis extrude + pinGroup amber stem

### Changed
- `place_service.py` 400 sor (határ): `_STUBS` + `_parse_solar(mstrahlung/klasse)` + `POSTCODE_WGS84` + `ZH_WFS_URL/_parse_oereb_xml` + `ZH_STEUER_URL/_parse_zh_steuerfuss_html`
- `frontend/src/app/[locale]/page.tsx`: Ort 6 csempe, `aiSummary` fetch `8013` + `summary||aiSummary` fallback
- `place 8004?live=true`: `solar null → 1208 sehr gut`, `oereb null → Kernzone`, `steuerfuss_source stub → zh-steueramt-html` — BE `8310` validált
- Master roadmap: `2026-08-27 (a91af31)` — Phase 1+2 KÉSZ, 45 passed, 4/4 PW 20.7s

### Verified
- `BE 8310 health ok` + `place 8004?live solar 1208 sehr gut oereb Kernzone steuer zh-steueramt-html` + `planning/refresh count 100 ZH` + `FE 3310 lang de/en/fr/it 200` + `4/4 PW 20.7s` + `45 passed mypy 17 build SSG`

## [0.1.0] - 2026-08-26
- Bootstrap: `AGENTS.md`, `METHODOLOGY.md`, `workflows/principles.md`, ADR/research/competitor keret (`31ba465`)
- ADR-001: Next.js + MapLibre + FastAPI + PostGIS, accepted
- Kickoff research + W35 competitor scan + scaffold + CI + Phase 1 backend+frontend — 20 passed

[0.3.0]: https://github.com/csaszarzoltan/swiss_p_map/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/csaszarzoltan/swiss_p_map/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/csaszarzoltan/swiss_p_map/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/csaszarzoltan/swiss_p_map/releases/tag/v0.1.0
