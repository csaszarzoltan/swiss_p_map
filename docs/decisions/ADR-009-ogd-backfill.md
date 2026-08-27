# ADR-009: OGD 2982 backfill — CSV batch + Amtsblatt hibrid

- **Dátum:** 2026-08-27
- **Státusz:** proposed → **accepted** (2026-08-27 — programozott folytatás, ADR-002 A+B hibrid)
- **Szerző:** analyst (research: `docs/research/2026-08-27-ogd-backfill.md`)
- **Kanban:** OGD backfill történeti

## Kontextus

`planning/baugesuche?postcode=8004 → 2 demo + refresh 100 ZH` él, de OGD `2982@...` **22145** történeti rekord (2024 ősz óta napi FK OGD) még nincs bekötve — „minden információ” hiány. CSV `daten.statistik.zh.ch/.../KTZH_00002982_00006183.csv` **200 22k sor**, postcode közvetlen (`projectLocation_swissZipCode`), ID UUID ≡ Amtsblatt (idempotens upsert).

## Döntés

**A: hibrid CSV backfill + Amtsblatt incremental (4.25/5 nyert).**

- `GET CSV → csv.DictReader → Baugesuch(title=projectDescription, postcode=4jegy, publicationDate, expirationDate, auflage+20d, source_url, buildingZone)` → `repo.upsert_many` → `POST /planning/backfill {source:"ogd"} → {count}`
- `ogd_service.py` 60 sor, `httpx DI MockTransport`, `max 400 sor/file`, 4 nyelv változatlan (csak count nő)

## Elvetve

| Opció | Miért nem |
|---|---|
| B: csak XML | nem teljes (csak 1 év), nem „minden információ” |
| C: csak CSV | nincs jogi legalRemedy meta, anonimizálás |

## Következmény

- Kártyák: `feat: OGD 2982 backfill` → `ogd_service.py` + `planning_service.backfill` + `POST /backfill` + `tests/unit/test_ogd_backfill.py` (mock 8004→Kernzone, üres→0)
- Validálás: `planning/baugesuche?postcode=8004 → 22k+` mock `green` + `mypy clean` + `4/4 PW`
- Kapcsolódó: Research `2026-08-27-ogd-backfill.md`, kód `src/services/ogd_service.py`, következő: `0.2.1` release

## Kapcsolódó

- Research: `docs/research/2026-08-27-ogd-backfill.md`
- Kód: `src/services/ogd_service.py`, `src/db/planning_repo.py`
- Következő ADR: — (utána 0.2.1)
