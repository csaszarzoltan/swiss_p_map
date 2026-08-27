# Changelog — Swiss P Map

Minden jelentős változás ebben a fájlban dokumentálva. Formátum: Keep a Changelog + SemVer.

## [Unreleased]

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

[Unreleased]: https://github.com/csaszarzoltan/swiss_p_map/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/csaszarzoltan/swiss_p_map/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/csaszarzoltan/swiss_p_map/releases/tag/v0.1.0
