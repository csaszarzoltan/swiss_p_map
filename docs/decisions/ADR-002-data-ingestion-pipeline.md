# ADR-002: Planning pillér adat-útvonal (Amtsblatt XML ETL + SQLite TTL)

> Template alapján — 1 oldal. Research: `docs/research/2026-08-26-amtsblatt-oereb-api.md`

- **Dátum:** 2026-08-26
- **Státusz:** accepted (2026-08-26 — „Mehet az A” emberi jóváhagyás)
- **Szerző:** analyst (research: élő API-próbák, 2026-08-26)
- **Kanban:** t_add5150f (done 2026-08-26 — unblocked, Task 1+ indul)

## Kontextus

A Planning pillérnek gépi hozzáférés kell a ZH Baugesuch-publikációkhoz (20 napos Auflage-ablak logika) és később az ÖREB zónákhoz. Az Amtsblattportal publikus REST API-ja élően igazolt (6669 BP-ZH rekord; ~17/nap), de nincs koordináta és nincs JSON-lista — XML a kontraktum.

## Döntés

- **Ingestion: napi poll** az `amtsblattportal.ch/api/v1/publications/xml` végpontról (`publicationStates=PUBLISHED&cantons=ZH&rubrics=BP-ZH&publicationDate.start=<last_run>`), `httpx` + Protocol-DI (`amtsblatt_service.py`, minta: `swisstopo_service.py`).
- **Tárolás: SQLite** (`data/swisspm.db`, `baugesuche` tábla): id (UUID), title, postcode, municipality, municipality_id, publication_date, expiration_date, auflage_start (= publication_date), auflage_end (= start+`AUFLAGE_DAYS`, default 20), source_url, geocode_precision. PostGIS később, külön ADR.
- **Geokódolás:** cím a `title.de`-ből Swisstopo `type=locations` (már integrált); nem található → községközéppont; `geocode_precision` = `address|locality|none`. Koordináta a forrásban NINCS.
- **Auflage-logika:** `Baugesuch.is_active(on)` a meglévő terv szerint; a portál 1 éves láthatósági TTL-t külön `expiration_date`-ben tároljuk. Közelítés dokumentálva (a jogi Auflage-friss nincs gépi mezőben).
- **Endpoint:** `GET /api/v1/planning/baugesuche?postcode=&active_only=` (METHODOLOGY lista-formátum).
- **ÖREB M2M elhalasztva** → ADR-003, külön kutatási ciklus (WFS/DATA-Extract komplexitás).

## Elvetve

| Opció | Miért nem |
|---|---|
| `/json` lista-végpont | nem létezik (élően igazolva: NOT FOUND exception) |
| ÖREB M2M most (Task 5 ebben a ciklusban) | parcella-szintű extract + Interlis/XML — külön kutatást érdemel |
| Csak OGD 2982 batch | jó backfill-forrás, DE nincs saját friss-feed kontroll és jogi meta; hibrid marad későbbi kártya |

## Következmény

- Kártyák: Task 1 domain modell → Task 2 Amtsblatt client (mockolt teszt) → Task 3 planning service + endpoint → Task 4 frontend markerek → (utána) OGD backfill + Audit-C live OGD kártya.
- Developer figyeljen: XML parse (`xml.etree`, namespaced bulk-export), max 400 sor/file, minden rekordban `source_url`.
- Validálás: unit (modell/client mock) + E2E endpoint; élő füst: napi poll ≥1 rekordot hoz a 8004-re eső publikációkkal.

## Kapcsolódó

- Research: `docs/research/2026-08-26-amtsblatt-oereb-api.md`
- Terv: `docs/plans/2026-08-26-planning-pillar-phase2.md`
- Kód: `src/services/amtsblatt_service.py` (létrehozandó), `src/models/planning.py`
- Következő ADR: ADR-003 (ÖREB M2M)
