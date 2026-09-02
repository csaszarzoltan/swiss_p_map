---
id: FEAT-002
title: Építési Hirdetmények Betöltése és Adatpipeline
status: SPEC_READY
version: 1
risk: medium
owner: product-owner
approvedBy: system-architect
approvedAt: 2026-09-02T09:00:00Z
baseCommit: HEAD
brief: BRIEF-002
---

# FEAT-002: Építési Hirdetmények Betöltése és Adatpipeline

## 1. Cél és felhasználói eredmény


Siker akkor áll fenn, ha a brief négy felhasználói útja determinisztikusan végrehajtható, a hibaállapot megfigyelhető, és a forrás, frissesség vagy becslési státusz nem vész el.

## 2. Kontextus és források
- Kapcsolódó brief: `BRIEF-002` (`docs/briefs/BRIEF-002-epitesi-hirdetmenyek-betoltese-es-adatpipeline.md`)
- Kapcsolódó research: `docs/research/2026-08-26-amtsblatt-oereb-api.md`
- Kapcsolódó ADR: `ADR-002` (`docs/decisions/ADR-002-*.md`)
- Kapcsolódó domain-invariánsok: `INV-DATA-001` forráshűség, `INV-TRACE-001` REQ-AC-teszt nyomkövethetőség, `INV-A11Y-001` hozzáférhető alternatíva
- Implementációs bizonyíték / tervezett érintettség: `src/main.py; src/services/amtsblatt_service.py; src/services/planning_service.py; src/db/planning_repo.py`

## 3. Scope
### Benne van
- A briefben rögzített felhasználói utak és adatkontraktus.

### Nincs benne
- A briefben explicit nem vállalt képességek.

## 4. Szereplők és előfeltételek
- ACT-001: Elsődleges felhasználó: a Swiss P Map nyilvános látogatója.
- ACT-002: Üzemeltető vagy automatizált provider-folyamat, amely adatot frissít és auditál.
- PRE-001: A frontend betöltődött támogatott böngészőben; API-kérésnél a backend elérhető vagy hiteles cache áll rendelkezésre.
- PRE-002: Helyalapú műveletnél az irányítószám négy számjegy, illetve a WGS84 koordináta latitude `[-90,90]`, longitude `[-180,180]` tartományban van.
- PRE-003: Külső adat esetén a válaszhoz forrásazonosító és lekérési idő tartozik.

## 5. Funkcionális követelmények
- REQ-001 [MUST]: A rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi. A művelet sikerét a felületen és az API-válaszban azonos domainállapot reprezentálja.
- REQ-002 [MUST]: A rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi. Minden megjelenített értékhez típus, mértékegység és forrás tartozik, ha az érték adatforrásból ered.
- REQ-003 [MUST]: A rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi. Hiányzó, részleges vagy alacsony felbontású adatot a rendszer explicit `unavailable`, `estimated` vagy `fallback` állapottal jelöl.
- REQ-004 [MUST]: A rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi. Az elsődleges művelet egér, érintés és billentyűzet használatával is végrehajtható.
- REQ-005 [MUST NOT]: A rendszer nem jeleníthet meg ismeretlen eredetű, lejárt vagy becsült adatot élő, pontos vagy hivatalosan garantált adatként.
- REQ-006 [ALWAYS]: Az aktív hely, téma, kiválasztás és nyelv közötti állapot konzisztens marad siker, hiba és újrapróbálkozás után.
- REQ-007 [CONCURRENCY]: Párhuzamos vagy későn beérkező kérések közül csak a legutóbbi felhasználói szándékhoz tartozó válasz módosíthatja az aktív nézetet; idempotens írásnál azonos kulcs nem hozhat létre duplikátumot.

## 6. Nem funkcionális követelmények
- NFR-001 [PERFORMANCE]: Kliensoldali állapotváltás 100 ms-on belül ad visszajelzést; hálózati kérés 300 ms után loading állapotot mutat; 10 s után kontrollált timeout vagy hiteles fallback lép életbe.
- NFR-002 [ACCESSIBILITY]: A feature megfelel a WCAG 2.1 AA releváns sikerkritériumainak; minden művelet billentyűzettel elérhető, a fókusz látható, a dinamikus állapot `aria-live` visszajelzést kap.
- NFR-003 [SECURITY]: Bemenetek allowlist és típus szerint validáltak; felhasználói vagy upstream HTML nem kerül nyers DOM-injektálásra; URL-ek csak `https` vagy belső relatív sémát használhatnak.
- NFR-004 [PRIVACY]: A feature csak a szükséges adatot tárolja; személyes vagy privát adat nem kerül naplóba vagy exportba külön jogalap és explicit hozzájárulás nélkül.
- NFR-005 [OBSERVABILITY]: Hibák stabil hibakódot, korrelációs azonosítót és forrás/provider nevet tartalmaznak; titok és teljes személyes payload nem naplózható.

## 7. UI-szerződés
- UI-001: `feature-{num}`, elsődleges panel; állapotok: `idle`, `loading`, `success`, `empty`, `error`, `stale`.
- UI-002: `feature-{num}-primary-action`, Button/Select/MapControl; `disabled` csak hiányzó előfeltételnél, és az ok programozottan elérhető.
- UI-003: `feature-{num}-status`, Status/Alert; loading, forrás, frissesség, fallback és validation error szövegesen jelenik meg.
- UI-004: `feature-{num}-details`, Panel/List/Table; hiányzó érték helyén lokalizált „nem elérhető” állapot, nem nulla vagy üres, félreérthető mező.
- UI-005: Minden térképi vagy grafikus információhoz lineáris lista, táblázat vagy szöveges alternatíva tartozik.

## 8. GUI-folyamat
1. A felhasználó megnyitja a feature-t az aktuális hely, nyelv és téma megtartásával.
2. A rendszer azonnal `loading` vagy cache-frissességi állapotot jelenít meg.
3. Siker esetén megjelennek a feature-adatok, a forrás, az időbélyeg és a végrehajtható következő műveletek.
4. Üres eredménynél a rendszer `empty` állapotot és módosítható keresési vagy rétegválasztási kontrollt mutat.
5. Hiba esetén lokalizált hibakód, megőrzött korábbi érvényes nézet, újrapróbálás és ahol releváns hivatalos forráslink jelenik meg.
6. Billentyűzetes használatkor a fókusz az aktiváló kontrollról az eredmény címsorára vagy hibaüzenetére kerül, majd logikus sorrendben folytatható.

## 9. Állapotmodell
Állapotok: `IDLE`, `LOADING`, `SUCCESS`, `EMPTY`, `STALE`, `ERROR`.

Átmenetek:
- `IDLE + activate -> LOADING`
- `LOADING + valid-data -> SUCCESS`
- `LOADING + no-data -> EMPTY`
- `LOADING + cached-data-and-provider-error -> STALE`
- `LOADING + unrecoverable-error -> ERROR`
- `SUCCESS|EMPTY|STALE|ERROR + retry-or-input-change -> LOADING`
- Bármely aszinkron válasz csak akkor alkalmazható, ha request tokenje megegyezik az aktuális state tokennel.

## 10. Acceptance scenario-k
### AC-001: Felhasználói út 1
Given a rendszer érvényes kiinduló állapotban van és a szükséges adatforrás elérhető
When a rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi
Then a rendszer megfigyelhető, lokalizált eredményt jelenít meg, a releváns mezőket és forrásállapotot rögzíti, és nem veszti el a korábbi érvényes állapotot

### AC-002: Felhasználói út 2
Given a rendszer érvényes kiinduló állapotban van és a szükséges adatforrás elérhető
When a rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi
Then a rendszer megfigyelhető, lokalizált eredményt jelenít meg, a releváns mezőket és forrásállapotot rögzíti, és nem veszti el a korábbi érvényes állapotot

### AC-003: Felhasználói út 3
Given a rendszer érvényes kiinduló állapotban van és a szükséges adatforrás elérhető
When a rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi
Then a rendszer megfigyelhető, lokalizált eredményt jelenít meg, a releváns mezőket és forrásállapotot rögzíti, és nem veszti el a korábbi érvényes állapotot

### AC-004: Felhasználói út 4
Given a rendszer érvényes kiinduló állapotban van és a szükséges adatforrás elérhető
When a rendszer a építési hirdetmények betöltése és adatpipeline hiányos vagy hibás adatát explicit állapotként jelzi
Then a rendszer megfigyelhető, lokalizált eredményt jelenít meg, a releváns mezőket és forrásállapotot rögzíti, és nem veszti el a korábbi érvényes állapotot

### AC-005: Hiányos vagy hibás adat
Given az elsődleges adatforrás hibát, üres választ vagy nem kompatibilis sémát ad
When a felhasználó aktiválja a feature-t
Then a rendszer explicit hiba-, fallback- vagy nem elérhető állapotot mutat, nem állít hamis pontosságot, és felkínál újrapróbálást vagy hivatalos forráslinket

### AC-006: Versengő válaszok
Given két kérés egymást átfedve fut különböző felhasználói állapothoz
When a korábbi kérés a későbbi kérés után fejeződik be
Then a korábbi válasz nem írja felül a legutóbbi felhasználói választást, és nem keletkezik duplikált perzisztens rekord

## 11. API-szerződés
- Szerződés: `GET /api/v1/planning/baugesuche?postcode={PLZ}&active_only={bool}`; `POST /api/v1/planning/refresh`
- Request: path/query/body mezők típusa a FastAPI/Pydantic modellekkel egyezik; hibás input esetén HTTP 400 vagy 422, hiányzó erőforrásnál 404.
- Response 200: JSON objektum vagy `{"items": [...]}`; mezők nullabilitása a jelenlegi modelleket követi.
- Response 5xx: szabványos `{"detail": "..."}`; a dokumentált fallback-képességeknél 200 válasz és forrásjelzés.

## 12. Tesztleképezés
- REQ-001 -> AC-001 -> Unit + Integration + E2E teszt
- REQ-002 -> AC-002 -> Schema/contract + E2E teszt
- REQ-003 -> AC-003 és AC-005 -> Provider-failure integration + E2E teszt
- REQ-004 -> AC-004 -> Keyboard, touch és axe/Playwright E2E teszt
- REQ-005 -> AC-005 -> Negatív contract és provenance teszt
- REQ-006 -> AC-001..AC-005 -> State-machine unit + E2E teszt
- REQ-007 -> AC-006 -> Concurrency/race unit vagy integration teszt
- NFR-001 -> Performance budget teszt mérhető küszöbbel
- NFR-002 -> axe + billentyűzetes Playwright teszt
- NFR-003 -> input fuzz/validation + XSS regressziós teszt
- NFR-004 -> privacy/log/export contract teszt
- NFR-005 -> strukturált hibaséma és log-redaction teszt

## 13. Kockázatok és emberi döntések
- HR-001: Nincs külön briefben rögzített bizonytalanság; provider- és adatkontraktus-változás esetén architekturális review szükséges.
- HR-002: A fejlesztés előtt a product-owner és system-architect ellenőrzi, hogy a külső adatok licence, felbontása, jogi státusza és frissítési ciklusa támogatja-e a szerződést.
- HR-003: Jogi, egészségügyi, pénzügyi, eljárási vagy személyes adatot érintő kimenet tájékoztató jellegű; döntést vagy garanciát nem állíthat.

## 14. Nyitott kérdések és Definition of Done
- Nincs implementációt blokkoló nyitott kérdés a jóváhagyott scope-on belül; a HR-001-ben jelzett provider- vagy jogi döntés új research/ADR stop-gate-et nyit, ha még nincs elfogadva.
- DoD: minden REQ és NFR legalább egy futtatható teszttel leképezett; célzott RED bizonyíték archivált; minimális GREEN implementáció elkészült; célzott és teljes regressziós tesztek tool-használattal lefutottak.
- DoD: `pytest`, `ruff`, `mypy`, frontend lint/typecheck/build és releváns Playwright/axe suite zöld; nincs kihagyott vagy xfail-lal elrejtett kötelező scenario.
- DoD: `docs/specs/index.json`, `docs/specs/README.md` és `docs/specs/VALIDATION.md` szinkronban van ezzel a fájllal.
