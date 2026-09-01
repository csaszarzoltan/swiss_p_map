# BRIEF-009: Történeti és Tömeges Építési Engedély Backfill

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-009 (ADR-009)  
**Forrás:** a Kanton Zürich Nyílt Kormányzati Adatbázisa (OGD 2982 CSV) és a tömeges adatbetöltési szolgáltatás (`OgdService`) alapján

## Probléma

Az Amtsblatt csak az éppen aktuális, napi hirdetményeket tartalmazza. Ha a felhasználó egy körzet építési trendjeit, korábbi engedélyeit vagy sűrűségét akarja vizsgálni, a rendszer üresnek tűnhet, ha az elmúlt napokban nem volt új beadás.

## Célcsoport és kontextus

Statisztikusok, ingatlanpiaci elemzők és építészek, akik a történeti engedélyezési aktivitást vizsgálják.

## Kívánt eredmény

Egy gombnyomással vagy időzített feladattal futtatható OGD backfill folyamat (`POST /api/v1/planning/backfill`), amely 22,000+ valós építési engedélyt tölt be a központi SQLite adatbázisba, idempotensen és hibabiztosan.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-009-01:** Rendszeradminisztrátorként szeretném egyetlen API hívással betölteni a teljes kantonális OGD 2982 CSV adatbázist.
- **US-009-02:** Felhasználóként szeretném, ha a kereséskor a körzetemhez tartozó történeti projektek is azonnal megjelennének a listában.
- **US-009-03:** Rendszerként szeretném, hogy az ismételt backfill ne hozzon létre duplikációkat (ON CONFLICT UPDATE azonosító alapján).

- **US-009-04:** Üzemeltetőként szeretném a backfill eredményében látni a beolvasott, frissített, kihagyott és hibás rekordok számát, hogy auditálható legyen a futás.

## Scope

- `OgdService` aszinkron CSV letöltő és soronkénti értelmező (`csv.DictReader`).
- Idempotens tömeges beszúrás (`PlanningRepo.upsert_many`).
- `POST /api/v1/planning/backfill` REST végpont.

## Non-scope

- 10+ gigabájtos raszteres tervrajzok letöltése.

## Érintett rendszerek

- `src/services/ogd_service.py`, `src/db/planning_repo.py`, `src/main.py`

## Bizonytalanságok

- CSV kódolási és formátum-változások a kantonális OGD portálon (UTF-8 validálás).
