# Changelog — Swiss P Map

Minden jelentős változás ebben a fájlban dokumentálva. Formátum: Keep a Changelog + SemVer.

## [Unreleased]

### Added
- Kickoff research: `docs/research/2026-08-26-kickoff.md` (3-pilléres koncepció, comparison table)
- ADR-001: `docs/decisions/ADR-001-stack-and-architecture.md` (Next.js + MapLibre + FastAPI + PostGIS, accepted)
- Competitor scan: `docs/competitor/2026-W35-scan.md` (Houzy Pro, smartconext)
- Scaffold: `pyproject.toml`, `requirements.txt`, `tests/unit/test_geo_converter.py`, `tests/conftest.py`
- CI: `.github/workflows/ci.yml` (backend + frontend split: ruff/mypy/pytest + npm ci/lint/build)
- Phase 1 backend: `src/models/{geo,place,politics}.py`, `src/services/{geo_converter,swisstopo,politics,place}_service.py`, `src/main.py` (FastAPI: /health, /api/v1/geo/convert, /api/v1/politics/representatives, /api/v1/place/{postcode}, CORS), `tests/e2e/test_core_e2e.py` — 20 passed
- Phase 1 frontend: `frontend/` (Next.js 14 + MapLibre Swisstopo Light), `src/app/{Map,SearchPanel,postcode_coords}.tsx`, `src/lib/api.ts` — build zöld, audit A/B

### Changed
- Lean módszertan: `.agent-pipeline/` kivezetve, kanban+ADR+research marad (commit `0bb2cec`)
- Audit 9.5/10 finomhangolások: Task 3 szabad szöveg (A), Map CSS layout.tsx (B), live OGD jegyzet (C)
- Frontend CSS: `maplibre-gl.css` → `layout.tsx` (Next 14 globális import, build/lint zöld)

### Verified
- Füstteszt (élő uvicorn 18081): /health, /api/v1/place/8004, /api/v1/politics/representatives?postcode=8004, /api/v1/geo/convert, CORS preflight → mind 200 OK

## [0.1.0] - 2026-08-26
- Bootstrap: `AGENTS.md`, `METHODOLOGY.md`, `workflows/principles.md`, ADR/research/competitor keret (commit `31ba465`)

[Unreleased]: https://github.com/csaszarzoltan/swiss_p_map/compare/0bb2cec...HEAD
[0.1.0]: https://github.com/csaszarzoltan/swiss_p_map/releases/tag/v0.1.0
