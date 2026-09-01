# BRIEF-002: Építési Hirdetmények Betöltése és Adatpipeline

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-002 (ADR-002)  
**Forrás:** a svájci szövetségi Hivatalos Lap (Amtsblattportal.ch) XML API, a Baugesuch domain modell és a 20 napos Auflage-ablak logika alapján

## Probléma

A svájci építési engedélyezési hirdetmények (Baugesuche) hivatalosan közzétételre kerülnek az Amtsblattban, de a 20 napos törvényes fellebbezési időszak (Auflagefrist) után a lakosság és a szomszédok elveszítik a betekintési és észrevételezési jogukat. A hirdetmények nehezen követhetők kézzel, XML formátumban érkeznek, és hiányzik az automatikus határidő-számítás.

## Célcsoport és kontextus

Környékbeli lakosok, építészek és ingatlanfejlesztők, akik időben értesülni akarnak a szomszédos telkeken tervezett építkezésekről és átalakításokról.

## Kívánt eredmény

Automatizált háttérfolyamat és REST végpont, amely letölti az Amtsblatt XML hirdetményeket, kiszámítja a 20 napos Auflage időablakot, kiszűri a lejárt engedélyeket, és geokódolt koordinátákkal látja el a projekteket.

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-002-01:** Felhasználóként szeretném látni az aktív építési engedélyeket az irányítószámom alatt, hogy tudjam, mi épül a közelemben.
- **US-002-02:** Felhasználóként szeretném látni a fellebbezési határidő kezdetét és végét (`auflage_start` és `auflage_end`), hogy ne késsek le a határidőről.
- **US-002-03:** Rendszerként szeretném a `POST /api/v1/planning/refresh` végponton keresztül automatikusan frissíteni a hirdetményeket.

## Scope

- `Baugesuch` Pydantic domain modell (`id`, `title`, `postcode`, `canton`, `publication_date`, `auflage_start`, `auflage_end`, `source_url`, `lat`, `lon`).
- `AmtsblattService` HTTP kliens XML feldolgozással.
- SQLite alapú perzisztencia (`PlanningRepo`) és memóriabeli tesztkörnyezet.

## Non-scope

- Automatikus jogi fellebbezési űrlap benyújtása a bíróságra (csak tájékoztatás és forráslink).

## Érintett rendszerek

- `src/models/planning.py`, `src/services/amtsblatt_service.py`, `src/db/planning_repo.py`, `src/main.py`

## Bizonytalanságok

- Az egyes kantonok eltérő XML struktúrájú Amtsblatt hirdetményeket publikálhatnak (egységesítő parser szükséges).
