# P0 stratégiai feature csomag QA audit

## Implementált specifikációk
- SPEC-032: 26 kantonos adó-összehasonlítás, rangsor, szomszédos kantonok, frontend színsáv.
- SPEC-034: BFS/FSO IMPI forrásjelölt regionális ártrend, két lakástípus, frontend kártya és indexsáv.
- SPEC-035: BAFU jelentésű veszélyértékelés, explicit bizonytalanság és frontend badge.
- SPEC-036: ISOS I/II screening és Baugesuch védőzóna-figyelmeztetés.

## TDD bizonyíték
A csomag új unit és HTTP acceptance tesztjei a tesztnevekben és docstringekben tartalmazzák a SPEC, REQ és AC hivatkozást.

## Minőségkapuk
- `python -m pytest tests/ -q`: 72 passed, 1 külső deprecációs warning.
- `python -m mypy src`: Success, 24 source files.
- `python -m ruff check src tests`: All checks passed.
- `python docs/specs/validate_specs.py`: PASS, 44 SPEC, 100% coverage.
- `npx tsc --noEmit`: a végrehajtási sandboxban nem volt befejezhető, mert a ZIP nem tartalmaz `node_modules` könyvtárat és az npm dependency telepítés időkorlátba ütközött. A parancs változatlanul futtatható `npm ci` után.

## Adatminőségi korlát
Az offline csomag determinisztikus, forrásjelölt referencia-snapshotot használ. A válaszok `quality_state` és disclaimer mezői nem állítják a becsült PLZ-adatot ingatlanértékbecslésnek, a hazard screeninget pedig jogilag kötelező veszélytérképnek. Éles provider-sync külön research/ADR és szerződéses teszt után kapcsolható be.

## Git művelet
A bemeneti ZIP nem tartalmazott `.git` metaadatot vagy távoli remote konfigurációt, ezért ebből a környezetből hiteles commit és push nem volt végrehajtható.
