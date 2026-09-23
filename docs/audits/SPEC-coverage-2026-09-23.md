# SPEC-lefedettségi audit — swiss-p-map (2026-09-23)

Feladat: `t_6c1d025b`. Módszer: `test_spec_<NNN>_*` függvénynevek gyűjtése a
`tests/unit` + `tests/e2e` fákból, kiegészítve ADR-címkés (`ADR-0NN`) és
névtelen (route-/service-alapú) evidenciákkal. Baseline a méréskor:
**172 passed** (full suite, zöld).

## 1. Összefoglaló

- Név szerint (`test_spec_NNN`) lefedett SPEC: **34 / 60**.
- ADR-címkén vagy névtelen route/service-teszten keresztül közvetetten
  lefedett SPEC: **16 / 60** (001, 002, 005–009, 011, 012, 014, 016–019, 022, 023).
- Teszteletlen SPEC: **10 / 60** — szinte kivétel nélkül frontend/vizuális
  scope (003, 004, 010, 013, 015, 020, 021, 024, 031, 044).
- A task-premissza pontosítása: a 046/055/056/057/059/060 SPEC-ekhez
  **létezett** vékony lefedettség (`test_phase3_civic_services.py`,
  `test_phase3_civic_api.py`, `test_resident_first_*`), de SPEC-enként csak
  1 unit + 1 API happy-path assert. A hiány a **mélységben** volt, nem a
  létben — ezt zárja a mostani contract-suite
  (`tests/unit/test_spec046_055_060_contract.py`, 24 teszt).

## 2. SPEC → tesztfile mátrix (mind a 60 SPEC)

Jelmagyarázat — COVERED: unit + API, REQ/AC-nyomkövetett. THIN: csak 1+1
happy-path. INDIRECT: ADR-címke vagy névtelen route/service-teszt, SPEC-név
nélkül. PLACEHOLDER: `assert True` csonk. NONE: nincs tesztnyom.

| SPEC | Cím (rövid) | Unit | E2E / API | FE e2e | Státusz |
|------|-------------|------|-----------|--------|---------|
| 001 | Térinformatikai architektúra | test_geo_converter.py | test_core_e2e.py (geo/convert) | – | INDIRECT (ADR-001-minta, SPEC-név nélkül) |
| 002 | Építési hirdetmény pipeline | test_amtsblatt_service.py, test_planning_repo.py, test_planning_refresh.py, test_spec047_058_news_pipeline.py (ADR-002) | – | – | INDIRECT (erős) |
| 003 | 3D sematikus térkép + kanton-nav | – | – | – | NONE (frontend 3D, nincs teszt) |
| 004 | Négynyelvű i18n | – | – | – | NONE (LanguageSwitcher + next-intl teszt nélkül) |
| 005 | Élő körzeti/politikai integráció | test_place_live.py (ADR-005), test_politics_live.py | test_core_e2e.py (politics, place) | – | INDIRECT |
| 006 | AI körzeti összefoglaló | test_ai_summary.py | – (POST /ai/summary route-teszt nincs) | – | INDIRECT |
| 007 | Helyi körzetbővítés | test_place_ort_expansion.py (ADR-007) | – | – | INDIRECT |
| 008 | Kantonális adókulcs-lekérdezés | test_place_zh_steuerfuss.py (ADR-008) | – | – | INDIRECT |
| 009 | Backfill (történeti/tömeges) | test_ogd_backfill.py (ADR-009) | – | – | INDIRECT |
| 010 | Témaválasztó sáv + drawer | – | – | – | NONE (TopicSidebar/DetailPanel teszt nélkül) |
| 011 | Országos helyfeloldás | test_place_multi_kanton.py (ADR-011) | test_core_e2e.py (place/8004) | – | INDIRECT |
| 012 | BFS népszavazási adatfolyam | test_vote_service.py (ADR-012) | – | – | INDIRECT |
| 013 | 3D építési markerek | – | – | – | NONE |
| 014 | Többkantonos engedély-federáció | test_planning_multi_canton.py (ADR-014) | – | – | INDIRECT |
| 015 | Tematikus hőtérkép/rétegek | – | – | – | NONE |
| 016 | Projekt-részletező + kockázat | test_planning_models.py (ADR-016) | – | – | INDIRECT |
| 017 | Történeti szavazási idővonal | test_vote_service.py (ADR-017) | – | – | INDIRECT |
| 018 | Sugár/poligon keresőmotor | test_planning_spatial.py (ADR-018) | radius/bbox route-tesztek uo. | – | INDIRECT (erős) |
| 019 | Cím-/geokódolási kereső | test_swisstopo_service.py, test_geo_converter.py | – | – | INDIRECT |
| 020 | Export / audit-csomag | – | – | – | NONE (nincs export-route) |
| 021 | Jelmagyarázat + forráshivatkozás | – | – | – | NONE (MapLegend teszt nélkül) |
| 022 | Kockázatjelzés + indoklás | test_place_risk_schema.py | – | – | INDIRECT |
| 023 | Sugár-figyelő | test_planning_spatial.py (radius) | – | – | INDIRECT (részleges) |
| 024 | Mélylink + nyelvperzisztencia | – | – | – | NONE (ShareButton teszt nélkül) |
| 025 | Mentett figyelési zónák | – | test_final_roadmap_api.py (`assert True`) | – | PLACEHOLDER |
| 026 | Kataszteri réteg/parcella | test_final_roadmap_services.py | test_final_roadmap_api.py | – | COVERED |
| 027 | Offline PWA | – | test_final_roadmap_api.py (`assert True`) | – | PLACEHOLDER (PwaStatus komponens van) |
| 028 | Körzet-összehasonlítás | test_final_roadmap_services.py | test_final_roadmap_api.py | – | COVERED |
| 029 | Forrás/frissesség/bizalom | test_final_roadmap_services.py | test_final_roadmap_api.py | – | COVERED |
| 030 | Mobil/a11y/billentyűzet | – | test_final_roadmap_api.py (`assert True`) | – | PLACEHOLDER |
| 031 | Tavak + alpesi domborzat 3D | – | – | – | NONE |
| 032 | Adóverseny/Steuerfuss-hőtérkép | test_p0_strategic_services.py | test_p0_strategic_api.py | – | COVERED |
| 033 | SBB mobilitási főhálózat | test_final_roadmap_services.py | test_final_roadmap_api.py | – | COVERED |
| 034 | Lakásár-trendek/index | test_p0_strategic_services.py | test_p0_strategic_api.py | – | COVERED |
| 035 | Természeti veszélyek | test_p0_strategic_services.py | test_p0_strategic_api.py | – | COVERED |
| 036 | ISOS műemlékvédelem | test_p0_strategic_services.py | test_p0_strategic_api.py | – | COVERED |
| 037 | Mikroklíma/hősziget | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 038 | Iskolák/ellátási körzetek | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 039 | Észrevétel/fellebbezési tér | test_final_roadmap_services.py | test_final_roadmap_api.py | – | COVERED |
| 040 | Levegő/pollen | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 041 | Egészségügyi/mentési elérés | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 042 | Szélessáv/mobil-elérés | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 043 | Épületenergetika/fűtéscsere | test_p1_p2_strategic_services.py | test_p1_p2_strategic_api.py | – | COVERED |
| 044 | Glassmorphism HUD/design | – | – | – | NONE (vizuális rendszer, természeténél fogva) |
| 045 | Helyi információs központ | test_local_information_hub.py, test_resident_first_services.py | test_resident_first_api.py, test_local_information_hub_api.py | local-information-hub.spec.ts | COVERED (erős) |
| 046 | Szavazási/választási infóközpont | test_resident_first_services.py (1) + **test_spec046_055_060_contract.py (5)** | test_resident_first_api.py (2) + **contract (3 API)** | – | COVERED (e taskkal) |
| 047 | Helyi hírek (3 szint) | test_spec047_058_news_pipeline.py (6) | test_resident_first_api.py | – | COVERED |
| 048 | Időjárás/riasztás/klíma | test_resident_first_services.py | test_resident_first_api.py | – | COVERED |
| 049 | Költségkalkulátor | test_resident_first_services.py | test_resident_first_api.py | – | COVERED |
| 050 | Önkormányzati ügyintézés/hulladék | test_resident_first_services.py | test_resident_first_api.py | – | COVERED |
| 051 | Szavazási vizualizációs kártyák | test_spec051_voting_contract.py | uo. (TestClient) | voting-visual-card.spec.ts | COVERED |
| 052 | Időjárás/riasztás/víz-widget | test_spec052_weather_contract.py | uo. (TestClient) | weather-visual-widget.spec.ts | COVERED |
| 053 | Hulladéknaptár + iCal | test_spec053_waste_calendar.py | uo. (TestClient) | waste-calendar-visual.spec.ts | COVERED |
| 054 | Költségkalkulátor UI | test_spec054_cost_of_living.py | uo. (TestClient) | cost-of-living-calculator.spec.ts | COVERED |
| 055 | MeteoSwiss OGD konnektor | test_phase3_civic_services.py (1) + **contract (2)** | test_phase3_civic_api.py (1) + **contract (2 API)** | – | COVERED (e taskkal) |
| 056 | BFS VoteInfo konnektor | test_phase3_civic_services.py (1) + **contract (2)** | test_phase3_civic_api.py (1) + **contract (1 API)** | – | COVERED (e taskkal) |
| 057 | SBB Transport konnektor | test_phase3_civic_services.py (1) + **contract (1)** | test_phase3_civic_api.py (1) + **contract (3 API)** | – | COVERED (e taskkal) |
| 058 | Amtsblatt aggregator | test_spec047_058_news_pipeline.py (6) + test_phase3_civic_services.py | test_phase3_civic_api.py | – | COVERED |
| 059 | Hírlevél (double opt-in) | test_phase3_civic_services.py (1) + **contract (2)** | test_phase3_civic_api.py (1) + **contract (3 API)** | – | COVERED (e taskkal) |
| 060 | Web Push + zóna-riasztás | test_phase3_civic_services.py (1) + **contract (2)** | test_phase3_civic_api.py (1) + **contract (3 API)** | – | COVERED (e taskkal) |

## 3. A 6 SPEC-re írt contract-tesztek (REQ/AC-nyomkövetés)

`tests/unit/test_spec046_055_060_contract.py` — 24 teszt, service-szint +
valós API-endpoint (TestClient), minden névben SPEC/REQ/AC:

- **046** (5): final proposal → eredmény + üres polls (REQ-004/AC-002:
  felmérés soha nem eredmény); upcoming → minta + hibahatár, nincs
  fabrikált eredmény (REQ-004); proposals-lista source-meta (REQ-002);
  analysis pro/contra nem üres (REQ-001); ismeretlen id → 404 (REQ-003).
- **055** (4): snapshot trust-meta (official_measurement, TTL 300,
  fetched_at — REQ-002); current-API kontraktus kulcsai (REQ-001);
  station-paraméter átvitel (REQ-001); fallback soha nem official (REQ-005).
- **056** (3): sync determinisztikus sha256 (REQ-001/006); trust-meta
  official_publication (REQ-002); sync-API kontraktus (REQ-001).
- **057** (4): departures-szerződés + last_night_service (REQ-001);
  API station-echo (REQ-001); **/transport/hubs API** — eddig 0 teszt
  fedte (REQ-001); station-validáció 422 (REQ-003).
- **059** (4): service double-opt-in (REQ-001); consent nélkül
  ValueError + API 400 (REQ-004); teljes API-lánc
  subscribe→confirm→subscribed + re-confirm 404 (REQ-001/006);
  hibás email/PLZ → 422 (REQ-003).
- **060** (4): service dedup queued→deduplicated (REQ-006);
  **watch-alert API-lánc** — eddig 0 API-teszt fedte (REQ-001/006);
  ismeretlen subscription → subscription_not_found (REQ-003);
  nem-https endpoint → 422 (REQ-003).

TDD: a tesztek a meglévő implementáció valós viselkedését rögzítik
(futtatva: 24/24 zöld az első futtatáson, mert mindegyikhez van élő
endpoint/service; külön RED-lépés nem volt szükséges — nincs új
produkciós kód). Meglévő phase3/resident fájlokhoz nem nyúltam.

## 4. Maradék rések / kockázatok (nem e task scope-ja)

1. `assert True` placeholderek: SPEC-025/027/030
   (`tests/e2e/test_final_roadmap_api.py:53-62`) — valódi kontraktusra
   cserélendők.
2. SPEC-055 §8 második endpointja (`GET .../meteoswiss/alerts`) **nem
   létezik** a backendben (csak `/current`) — implementációs rés.
3. Konnektor-határok statikus adatot adnak vissza (MeteoSwiss 21.5 °C,
   SBB 2 fix indulás, VoteInfo 1 fix sor) — élő provider-hívás még nincs;
   a tesztek a szerződést (alak + trust-meta) rögzítik, nem az élősséget.
4. SPEC-003/004/010/013/015/020/021/024/031/044: nincs Python-tesztnyom
   (frontend/vizuális scope; Playwright csak 045/051–054-re van).
5. SPEC-006: POST /ai/summary route-nak nincs API-tesztje.
