---
id: SPEC-052
feature: FEAT-052
title: Svájci Időjárási, Riasztási és Tavi Vízhőmérsékleti Widget
status: SPEC_READY
implementationStatus: PENDING_DEV
version: 1
risk: medium
owner: product-owner
approvedBy: system-architect
approvedAt: 2026-09-02T13:00:00Z
brief: BRIEF-052
---
# SPEC-052: Svájci Időjárási, Riasztási és Tavi Vízhőmérsékleti Widget
## 1. Cím és metaadatok
`SPEC-052`, `BRIEF-052`, verzió 1, SPEC_READY, implementáció PENDING_DEV.
## 2. Cél és kontextus
Resident-first civic UX, élő OGD integráció vagy hozzájárulás-alapú értesítés biztosítása ellenőrizhető forrással.
## 3. Funkcionális követelmények
- REQ-052-001 [MUST]: A feature típusos, determinisztikus sikeres választ vagy UI-eredményt ad.
- REQ-052-002 [MUST]: Minden külső adat source, fetched_at és trust_state metaadatot tartalmaz.
- REQ-052-003 [MUST]: Loading, success, empty, stale/source_pending és error állapot támogatott.
- REQ-052-004 [MUST NOT]: Duplikált értesítés, hamis élő adat vagy hozzájárulás nélküli kézbesítés tilos.
- REQ-052-005 [ALWAYS]: A fallback nem jelenhet meg official_measurement státusszal.
- REQ-052-006 [CONCURRENCY]: Idempotency/deduplikáció és legutóbbi kérés nyer szabály kötelező.
## 4. Nem-funkcionális követelmények
- NFR-052-001 [PERFORMANCE]: UI feedback 100 ms; API timeout 10 s; connector cache a provider ciklusához kötött.
- NFR-052-002 [ACCESSIBILITY]: WCAG 2.1 AA, billentyűzet, aria-live, grafikonhoz szöveges alternatíva.
- NFR-052-003 [PRIVACY]: nDSG/GDPR minimalizálás; email/push token titkos vagy hash-elt tárolása.
## 5. Elfogadási kritériumok
### AC-052-001: Happy path
Given érvényes bemenet és elérhető függőség
When a felhasználó aktiválja a funkciót
Then forrásolt, hozzáférhető eredmény jelenik meg.
### AC-052-002: Provider kiesés
Given a külső provider nem elérhető
When a lekérés lefut
Then stale vagy source_pending állapot jelenik meg hamis frissesség nélkül.
### AC-052-003: Hibás vagy ismételt kérés
Given hibás input vagy azonos idempotency kulcs
When az API feldolgozza
Then 400/422 vagy deduplikált siker válasz érkezik.
## 6. Negatív tesztesetek és hibakezelés
Pydantic 422; hiányzó erőforrás 404; konfliktus 409; kontrollált provider-hiba 503; nyers 500 részlet tiltott.
## 7. Python interfészek, Pydantic modellek és típusdefiníciók
BaseModel request/response, Literal status, Protocol-alapú connector, teljes type hinting.
## 8. API végpont specifikációk
`Frontend-only WeatherVisualWidget consuming weather APIs`. JSON response source/trust/cache metaadatokkal; írások idempotency mezővel.
## 9. Frontend komponensek és UI interakciós szerződések
Civic komponens loading/empty/error állapotokkal; modal Escape; 44 px célméret; nyers JSON nem végleges UI.
## 10. Adatforrások, frissítési ciklusok és bizalmi állapot
SourceTrustBadge; official_measurement, official_publication, modeled_estimate, stale, source_pending. Connector TTL dokumentált.
## 11. Nemzetköziesítés
DE/EN/FR/IT kulcsnévtér: `phase3.feature052.*`.
## 12. Akadálymentesség
WCAG 2.1 AA; tab/arrow/Escape; aria-live; színtől független jelentés.
## 13. Biztonság, adatvédelem és jogi felelősség
SSRF allowlist, HTML sanitization, VAPID/email titkok env-ben, double opt-in, leiratkozás; nem jogi/pénzügyi/vészhelyzeti tanács.
## 14. REQ → AC → Teszt Traceability Mátrix
- REQ-052-001 -> AC-052-001 -> unit + API/E2E.
- REQ-052-002 -> AC-052-001 -> contract test.
- REQ-052-003 -> AC-052-001..003 -> UI state test.
- REQ-052-004 -> AC-052-003 -> negative/dedup test.
- REQ-052-005 -> AC-052-002 -> fallback test.
- REQ-052-006 -> AC-052-003 -> concurrency/idempotency test.
