---
id: FEAT-048
title: Svájci Időjárás, Élő Riasztások és CH2025 Klímatendenciák Központ
status: SPEC_READY
implementationStatus: PENDING_DEV
version: 1
risk: medium
owner: product-owner
approvedBy: system-architect
approvedAt: 2026-09-02T12:00:00Z
baseCommit: HEAD
brief: BRIEF-048
---

# FEAT-048: Svájci Időjárás, Élő Riasztások és CH2025 Klímatendenciák Központ

## 1. Cím és metaadatok
- Specifikáció: `SPEC-048`; kapcsolódó brief: `BRIEF-048`.
- Implementációs státusz: `PENDING_DEV`; specifikációs kapu: `SPEC_READY`.

## 2. Cél és kontextus
Resident-first, forrásolt helyi információ biztosítása úgy, hogy a térkép opcionális elemzőeszköz maradjon.

## 3. Funkcionális követelmények
- REQ-048-001 [MUST]: Érvényes bemenetre strukturált, típusos választ kell adni.
- REQ-048-002 [MUST]: Minden állításhoz forrás, időbélyeg és bizalmi állapot kell.
- REQ-048-003 [MUST]: A UI loading, success, empty, source_pending és error állapotot kezel.
- REQ-048-004 [MUST NOT]: Felmérés nem jelenhet meg eredményként, becslés mérésként vagy generált hír tényként.
- REQ-048-005 [ALWAYS]: Hiba után megmarad a hely, nyelv és korábbi érvényes állapot.
- REQ-048-006 [CONCURRENCY]: Csak a legutóbbi kérés válasza frissítheti az aktív nézetet.

## 4. Nem-funkcionális követelmények
- NFR-048-001 [PERFORMANCE]: 100 ms-on belüli loading visszajelzés és 10 s timeout.
- NFR-048-002 [ACCESSIBILITY]: WCAG 2.1 AA, billentyűzet, látható fókusz és aria-live.
- NFR-048-003 [SECURITY]: Pydantic validáció, HTTPS linkek, HTML-injektálás tiltása.

## 5. Elfogadási kritériumok
### AC-048-001: Sikeres lekérés
Given érvényes bemenet és elérhető forrás
When a felhasználó megnyitja a funkciót
Then lokalizált, strukturált és forrásolt eredményt kap.

### AC-048-002: Forráskiesés
Given az elsődleges forrás nem elérhető
When a lekérés lefut
Then source_pending vagy stale állapot jelenik meg kitalált tartalom nélkül.

### AC-048-003: Hibás bemenet
Given formailag hibás bemenet
When az API fogadja a kérést
Then 422 vagy dokumentált 404 válasz érkezik.

## 6. Negatív tesztesetek és hibakezelés
- Hibás PLZ és negatív numerikus érték: 422; hiányzó erőforrás: 404.
- Provider-hiba: 503 vagy hiteles stale fallback; nyers 500 részlet nem szivároghat.

## 7. Python interfészek és típusok
Pydantic BaseModel, Literal állapotok, teljes type hinting és konkrét service response modellek kötelezők.

## 8. API végpont specifikációk
- `GET /api/v1/weather/current; GET /api/v1/weather/alerts; GET /api/v1/weather/water-temperatures`
- HTTP 200: verziózható JSON; hibák: 404, 422, kontrollált 503.

## 9. Frontend komponensek és UI interakciók
- `frontend/src/components/WeatherCenter.tsx`; interaktív tab/modal, Escape bezárás, „Auf Karte” csak szükség esetén.

## 10. Adatforrások, frissítési ciklusok és bizalmi állapot
Minden rekord tartalmaz source, source_url, refreshed_at és trust_state mezőt; megjelenítés SourceTrustBadge komponenssel.

## 11. Nemzetköziesítés
DE, EN, FR és IT; kulcsnévtér `resident.feature048.*`; felhasználói szöveg nem hardkódolható a végleges UI-ban.

## 12. Akadálymentesség és billentyűzetes kezelés
WCAG 2.1 AA; modal Escape-pel zárható; nyilak kezelik a tablistet; grafikonnak táblázatos alternatíva kell.

## 13. Biztonság, adatvédelem és jogi nyilatkozatok
Nincs jogi, pénzügyi, orvosi vagy választási ajánlás. Felméréshez minta és hibahatár; költséghez becslési disclaimer kötelező.

## 14. RVAD Traceability Mátrix
- REQ-048-001 -> AC-048-001 -> unit + API + E2E.
- REQ-048-002 -> AC-048-001 -> contract + SourceTrustBadge.
- REQ-048-003 -> AC-048-001..003 -> UI state E2E.
- REQ-048-004 -> AC-048-002 -> negatív forrás-integritási teszt.
- REQ-048-005 -> AC-048-002 -> state recovery.
- REQ-048-006 -> AC-048-002 -> concurrency teszt.
