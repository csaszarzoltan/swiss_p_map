# Swiss P Map — Master Roadmap & Audit Entry Point

> **Cél:** egyetlen dokumentum, ami az auditort 5 percen belül képbe hoz. Részletes tervek: lásd linkek.

- **Dátum:** 2026-08-27 (frissítve)
- **Állapot:** Phase 1+2 KÉSZ — i18n + Politics/Place live + AI summary + Ort expansion + Planning refresh (678a056)
- **Board:** `swiss-p-map` kanban — 11 done, 0 blocked
- **Következő:** Stabilizálás (FE dev wrapper DBUS-fix + BE prod supervisord) + dokumentum konszolidáció

---

## 1. Hol tartunk (faktok, 2026-08-27)

| Réteg | Állapot | Bizonyíték |
|---|---|---|
| Docs (research/ADR/competitor) | ✅ 8 ADR, 8 research | ADR-001…007 mind accepted, W35 scan, kickoff, ai-summary-live, ort-expansion |
| Backend domain modellek | ✅ bővítve | `place.py` +4 mező (solar_kwh_m2/solar_class/oereb_zone/steuerfuss_source) |
| Backend szolgáltatások | ✅ élő OGD | `place_service 273 sor` (ARE/BAFU/BFE + OEREB), `politics_service 197 sor` (PARIS CQL), `ai_summary 64 sor` (8013 gateway), `amtsblatt_service` (XML 1.24/1.26 toleráns) |
| FastAPI | ✅ 9 endpoint | `/health`, geo/convert, politics?live, place/{pc}?live, planning/baugesuche + /refresh, ai/summary, CORS env |
| Tesztek | ✅ 43 passed | 41→43, test_place_ort_expansion + test_planning_refresh mock + test_ai_summary 2/2 |
| Minőségkapuk | ✅ zöldek | mypy 17 clean, ruff clean, build SSG 4 nyelv |
| CI | ✅ 2 job | backend (ruff/mypy/pytest) + frontend (npm ci/lint/build) |
| Frontend | ✅ 4 nyelv élő | de/en/fr/it `always`, SearchPanel+Ort 6 csempe (solar sárga + öreb lila), aiSummary fetch 8013→fallback, KI-ZUSAMMENFASSUNG mind 4 nyelven |
| Élő füst | ✅ bizonyított | 8310 health ok + place 8004?live A/62.5dB + planning/refresh count 100 ZH + FE 3310 lang de 200 + 4/4 PW 21s |

## 2. Ami MÉG stub / mock (őszintén)

- **Steuerfuss ZH:** `ZH-CSV Opendatasoft` wiring hiányzik (oereb_zone stub fallback), ma még 119% stub — ZH OGD join a következő kártya (ADR-007 követő)
- **FE dev wrapper:** production `next start -p 3310` stabil (Ready 637ms), de `next dev` Hermès DBUS-wrapper EADDRINUSE-ral hal — workshop-körben productionnel megy (known, non-blocking)
- **ÖREB WFS:** `ch.vd.oereb` Identify layer minta, kanton-független WFS `maps.zh.ch/wfs/OerebKatasterZHWFS` wiring a következő ADR-003
- **OGD 2982 backfill:** történeti Baugesuche JSON előtt `?live` demo seed + napi poll; backfill külön kártya

## 3. Következő lépések (minden research→ADR→kód)

| Terv | Fájl | Scope | Állapot |
|---|---|---|---|
| ~~API ↔ Map integráció~~ | `2026-08-26-api-map-integration.md` | kereső+marker+geokódolás | ✅ done |
| ~~Planning PH2~~ | `2026-08-26-planning-pillar-phase2.md` | Baugesuch + SQLite + /refresh | ✅ 678a056 |
| ~~i18n 4 nyelv~~ | ADR-004 | next-intl always | ✅ 2ba49b6 |
| ~~Politics/Place live~~ | ADR-005 | PARIS + api3 ARE/BAFU | ✅ 02c57bd+561e1ea |
| ~~AI summary~~ | ADR-006 | gateway 8013 4.62/5 | ✅ bd68613 |
| ~~Ort expansion~~ | ADR-007 | Solar+ÖREB 4.50/5 | ✅ cbfebf3 |
| Stabilizálás | — | FE dev DBUS wrapper + BE supervisord + roadmap 2. szekció | ⏳ ez a kör |

## 4. Audit-checklist

1. research → ADR → scaffold → RED→GREEN lánc minden featuren (git log végigkövethető: 12 commit 26-án + 3 27-én)
2. Tesztek MockTransport-tal, httpx DI, fallback stub → E2E nem törik upstream leállásnál
3. Stub-transparency: lásd 2. szekció — 3 nyílt tétel maradt
4. Konkurencia: W35 scan validálva, Houzy/smartconext állítások stimmelnek
5. Biztonság: publikus read-only API + ai/summary gateway, nincs auth — alacsony kockázat, POST /refresh nincs rate-limit

