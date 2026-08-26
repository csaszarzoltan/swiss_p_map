# Changelog — Swiss P Map

Minden jelentős változás ebben a fájlban dokumentálva. Formátum: Keep a Changelog + SemVer.

## [Unreleased]

### Added
- Kickoff research: `docs/research/2026-08-26-kickoff.md` (3-pilléres koncepció, comparison table)
- ADR-001: `docs/decisions/ADR-001-stack-and-architecture.md` (Next.js + MapLibre + FastAPI + PostGIS, accepted)
- Competitor scan: `docs/competitor/2026-W35-scan.md` (Houzy Pro, smartconext)
- Scaffold: `pyproject.toml`, `requirements.txt`, `tests/unit/test_geo_converter.py`, `tests/conftest.py`
- CI: `.github/workflows/ci.yml`

### Changed
- Lean módszertan: `.agent-pipeline/` kivezetve, kanban+ADR+research marad (commit `0bb2cec`)

## [0.1.0] - 2026-08-26
- Bootstrap: `AGENTS.md`, `METHODOLOGY.md`, `workflows/principles.md`, ADR/research/competitor keret (commit `31ba465`)

[Unreleased]: https://github.com/csaszarzoltan/swiss_p_map/compare/0bb2cec...HEAD
[0.1.0]: https://github.com/csaszarzoltan/swiss_p_map/releases/tag/v0.1.0
