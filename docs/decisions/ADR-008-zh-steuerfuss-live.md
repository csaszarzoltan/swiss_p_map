# ADR-008: ZH Steuerfuss live — steueramt.zh.ch HTML + stub fallback

- **Dátum:** 2026-08-27
- **Státusz:** proposed → **accepted** (2026-08-27 — programozott folytatás, ADR-005/007-tel együtt)
- **Szerző:** analyst (research: `docs/research/2026-08-27-zh-steuerfuss-live.md`)
- **Kanban:** ZH-place ZH Steuerfuss live (ADR-007 Ort után)

## Kontextus

`PlaceInfo.steuerfuss_percent` ma `119.0` stub mindkét pilot PLZ-re (`steuerfuss_source="stub"`). Opendata.swiss ZH dataset ma **404** + API **403** + City CKAN **404** — nincs élő CSV 2026-08-27. Cél: `8004/8001` → valós ZH Gemeindesteuerfuss élő, `?live=true` mintával, 4 nyelven, hiba → `119%` fallback.

## Döntés

**A: `steueramt.zh.ch` HTML scrape + napi cache + stub fallback (4.12/5 nyert).**

- `GET https://www.steueramt.zh.ch/.../steuerfuesse` (de/steuern-finanzen aloldal), parser `Zürich → 119%` (`re` + lxml-tolerant), cache `data/steuerfuss_zh.json` napi TTL, hiba → stub `119.0`
- `PlaceService.get_by_postcode_live` +1 `try: GET → parse → steuerfuss_source="zh-steueramt-html"` → `httpx DI + MockTransport`
- `source_url` kötelező ADR-002 mintára, `max 400 sor/file` (parser <60 sor)

## Elvetve

| Opció | Miért nem |
|---|---|
| B: CKAN CSV | ma 404+403 — nincs élő 200 2026-08-27 |
| C: statikus CSV | nem „online scrape”, karbantartás kézi |

## Következmény

- Kártyák: `feat: ZH Steuerfuss live (ZH pilot)` → `place_service.py` +1 parser + `tests/unit/test_place_zh_steuerfuss.py` (MockTransport 200→119 + 500→stub), `messages` tooltip opcionális, max 400 sor/file, 4 nyelv hreflang `always`
- Validálás: `place 8004?live=true source zh-steueramt-html + 119%` Identify próba + mock `green` + `mypy clean` + `4/4 PW`
- Kapcsolódó: Research `2026-08-27-zh-steuerfuss-live.md`, kód `src/services/place_service.py`, következő: BE live stabil

## Kapcsolódó

- Research: `docs/research/2026-08-27-zh-steuerfuss-live.md`
- Kód: `src/services/place_service.py`, `src/models/place.py`
- Következő ADR: — (ZH után 2 stub marad)
