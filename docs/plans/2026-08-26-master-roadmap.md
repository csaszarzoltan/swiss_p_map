# Swiss P Map — Master Roadmap & Audit Entry Point

> **Cél:** egyetlen dokumentum, ami az auditort 5 percen belül képbe hoz. Részletes tervek: lásd linkek.

- **Dátum:** 2026-08-27 (frissítve — v0.2.1 után)
- **Állapot:** Phase 1+2 KÉSZ — i18n + Politics/Place live + AI summary + Ort 6 csempe + Planning refresh + Solar/ÖREB fix + OGD 2982 backfill 22k (v0.2.1)
- **Board:** `swiss-p-map` kanban — 15 done, 0 blocked
- **Következő:** Release hygiene done — opcionális PostGIS / ÖREB kanton-független külön ADR, nem blokkol

---

## 1. Hol tartunk (faktok, 2026-08-27 live validált)

| Réteg | Állapot | Bizonyíték |
|---|---|---|
| Docs (research/ADR/competitor) | ✅ 9 ADR, 12 research | ADR-001…009 mind accepted, W35 scan + 8 live research (ai-summary, ort-expansion, solar-fix, oereb-live, zh-steuerfuss, ogd-backfill) |
| Backend domain modellek | ✅ bővítve | `place.py` +4 mező (solar_kwh_m2/solar_class/oereb_zone/steuerfuss_source) |
| Backend szolgáltatások | ✅ élő OGD | `place_service 400 sor` (ARE/BAFU/BFE WGS84 + ZH WFS Nutzungsplanung + zh.ch HTML), `ogd_service 97 sor` (2982 CSV 22k), `politics_service 197 sor` (PARIS CQL), `ai_summary 64 sor` (8013 gateway), `amtsblatt_service` (XML 1.24/1.26) |
| FastAPI | ✅ 8 endpoint | `/health`, geo/convert, politics?live, place/{pc}?live, planning/baugesuche + /refresh + **/backfill**, ai/summary, CORS env |
| Tesztek | ✅ 47 passed | test_place_ort_expansion (Kernzone) + test_place_zh_steuerfuss 2/2 + test_ogd_backfill 2/2 + test_planning_refresh + test_ai_summary 2/2 |
| Minőségkapuk | ✅ zöldek | mypy 18 clean, ruff clean, build SSG 4 nyelv |
| CI | ✅ 2 job | backend (ruff/mypy/pytest) + frontend (npm ci/lint/build) |
| Frontend | ✅ 4 nyelv élő | de/en/fr/it `always`, SearchPanel+Ort 6 csempe (solar sárga + öreb lila), aiSummary fetch 8013→fallback, KI-ZUSAMMENFASSUNG mind 4 nyelven, BASE 8310 |
| Élő füst | ✅ bizonyított | `8310 v0.2.1 ok` + `place 8004?live solar 1208 sehr gut oereb Kernzone steuer zh-steueramt-html` + `POST /backfill 22141 ogd (8004: 4 items)` + `FE 3310 lang de/en/fr/it 200` + `4/4 PW 21.2s` |

## 2. Ami MÉG stub / mock (őszintén, 2026-08-27)

- **FE dev wrapper:** production `next start -p 3310` stabil (Ready 572ms, `DBUS_SESSION_BUS_ADDRESS` env -u wrapper), de `next dev` Hermès DBUS-wrapper EADDRINUSE-ral hal — workshop-körben productionnel megy (known, non-blocking, nem funkció-hiány)
- Minden korábbi stub **feloldva**: ZH Steuerfuss `zh-steueramt-html` (ADR-008), Solar `1208 sehr gut` (WGS84 hit), ÖREB `Kernzone` (ZH WFS), OGD 2982 `22k` (ADR-009)

## 3. Következő lépések (minden research→ADR→kód)

| Terv | Fájl | Scope | Állapot |
|---|---|---|---|
| ~~API ↔ Map integráció~~ | `2026-08-26-api-map-integration.md` | kereső+marker+geokódolás | ✅ done |
| ~~Planning PH2~~ | `2026-08-26-planning-pillar-phase2.md` | Baugesuch + SQLite + /refresh | ✅ 678a056 |
| ~~i18n 4 nyelv~~ | ADR-004 | next-intl always | ✅ 2ba49b6 |
| ~~Politics/Place live~~ | ADR-005 | PARIS + api3 ARE/BAFU | ✅ 02c57bd+561e1ea |
| ~~AI summary~~ | ADR-006 | gateway 8013 4.62/5 | ✅ bd68613 |
| ~~Ort expansion~~ | ADR-007 | Solar+ÖREB 4.50/5 | ✅ cbfebf3 |
| ~~ZH Steuerfuss~~ | ADR-008 | zh.ch HTML 4.12/5 | ✅ 07b5548 |
| ~~Solar/ÖREB fix~~ | research 2026-08-27 | WGS84 + WFS Kernzone | ✅ a91af31 (400 sor) |
| ~~OGD 2982 backfill~~ | ADR-009 | 2982 CSV 22k hibrid | ✅ 6eebd9a (97 sor) |
| ~~Release 0.2.1~~ | README/CHANGELOG | 47 passed 18 mypy 4/4 PW 21.2s | ✅ 7f57c31 v0.2.1 |
| ~~Multi-Kanton Place~~ | ADR-011 | Szövetségi ARE/BAFU/BFE (BE/BS/ZH/GE) | ✅ 50 passed 18 mypy |
| ~~BFS Népszavazási Adatok~~ | ADR-012 | 26 kanton valós szavazati arányai (13. AHV-Rente) | ✅ 54 passed 20 mypy |
| ~~3D Építési Markerek~~ | ADR-013 | Borostyánsárga 3D pin-ek + raycast + Einsprache számláló | ✅ 8/8 PW passed |
| ~~Többkantonos Planning~~ | ADR-014 | Bern (3011), Basel (4001), Genf (1201) Baugesuche | ✅ 54 passed 20 mypy |

## 4. Audit-checklist

1. research → ADR → scaffold → RED→GREEN lánc minden featuren (git log végigkövethető: 17 commit 26-27-én, mind max 3 file)
2. Tesztek MockTransport/httpx DI + CSV/XML/WFS mock, fallback stub → E2E nem törik upstream leállásnál (ZH WFS 400→null, zh.ch 500→stub, CSV empty→0)
3. Stub-transparency: lásd 2. szekció — 1 ismert non-blocking maradt (FE dev)
4. Konkurencia: W35 scan validálva, Houzy/smartconext állítások stimmelnek
5. Biztonság: publikus read-only API + ai/summary gateway, nincs auth — alacsony kockázat, POST /refresh + /backfill nincs rate-limit (backlog)
