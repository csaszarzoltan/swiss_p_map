# ADR-007: Ort-bővítés — Sonnendach + ÖREB + ZH Steuerfuss live

- **Dátum:** 2026-08-27
- **Státusz:** proposed → **accepted** (2026-08-27 — programozott folytatás, ADR-005/006-tal együtt)
- **Szerző:** analyst (research: `docs/research/2026-08-27-ort-expansion-sonnendach-oereb.md`)
- **Kanban:** Ort-pillér bővítés (ADR-005 live után, ADR-006 AI után)

## Kontextus

`PlaceInfo` 4 mező (steuerfuss 119% stub + noise sonBASE + ÖV A + GWR) csak 2 PLZ-re. Ort-fiók 6 csempére bővítendő: Solar + ÖREB + ZH Steuerfuss live, 4 nyelven, `api3/WMS Identify` mintával, `max 400 sor/file`, fallback stubbal.

## Döntés

**A: hibrid `api3/WMS Identify` + kanton-CSV (4.50/5 nyert).**

- `PlaceInfo` bővül: `solar_kwh_m2: float | None` + `oereb_zone: str | None` + `solar_class: str | None` (kWh/m² + Klasse, `source_url` kötelező)
- `PlaceService.get_by_postcode_live` +2 réteg: `api3 Identify ch.bfe.solarenergie-eignung-daecher @LV95` + `ZH OGD CSV` (Opendatasoft v2, BFS-Nr→PLZ join, napi cache, fallback 119% stub), mind `httpx DI + MockTransport`
- FE: Ort tab 6 csempe + 3D `detailOverlay` solar (sárga) + ÖREB (lila) 0.34 opacity, `messages/{de,en,fr,it}.json` kulcsok

## Elvetve

| Opció | Miért nem |
|---|---|
| B: WMS/WFS only | Steuerfuss nem WMS-ből jön, Sonnendach/ÖREB bbox-törékeny |
| C: batch CSV+ZIP | nem „online scrape”, Interlis/XML túlnehéz pilotra (Amtsblatt schema drift 1.24→1.26) |

## Következmény

- Kártyák: `feat: Ort expansion — Solar + ÖREB + ZH Steuerfuss live` → `place.py` + `place_service.py` (<150 sor bővítés) + `tests/unit/test_place_ort_expansion.py` (3 réteg MockTransport) + FE Ort 6 csempe + `messages` + `Map3D detailOverlay`, max 400 sor/file, 4 nyelv hreflang `always`
- Validálás: `place 8004?live=true Solar Kwh>0 + ÖREB W2` Identify próba + ZH-CSV, mock `green` + `mypy clean` + `4/4 PW`
- Kapcsolódó: Research `2026-08-27-ort-expansion-sonnendach-oereb.md`, kód `src/models/place.py` + `src/services/place_service.py`, következő: BE live stabil + FE 500 fix külön nem kell ADR

## Kapcsolódó

- Research: `docs/research/2026-08-27-ort-expansion-sonnendach-oereb.md`
- Kód: `src/models/place.py`, `src/services/place_service.py`, `frontend/src/app/[locale]/page.tsx`, `frontend/messages/*.json`
- Következő ADR: — (Ort után planning PH2 már ADR-002-ben)
