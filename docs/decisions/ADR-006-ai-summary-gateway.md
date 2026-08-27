# ADR-006: KI-Zusammenfassung 4 nyelven — llm-budget-gateway (8013)

- **Dátum:** 2026-08-27
- **Státusz:** proposed → **accepted** (2026-08-27 — programozott folytatás, ADR-004/005-tel együtt, emberi `folytasd` szóban OK)
- **Szerző:** analyst (research: `docs/research/2026-08-27-ai-summary-live.md`)
- **Kanban:** AI-pillér (ADR-005 live után, i18n után)

## Kontextus

Fiók tetején `KI-ZUSAMMENFASSUNG` 2 mondat ma `t('summary.template')` sablon (de/en/fr/it fordított, de nem LLM). Cél: élő, **bizonyíték-alapú** (place/politics/planning JSON a promptban), 4 nyelven, gatewayen át, fallback sablonnal ha 8013 `cooldown`.

## Döntés

**A: `llm-budget-gateway` 8013 OpenAI-compat `POST /v1/chat/completions` (4.62/5 nyert) + fallback sablon.**

- `src/services/ai_summary_service.py` (<120 sor, Protocol-DI `httpx`, `MockTransport` tesztbarát, 120s timeout, promptban `locale` + `place/politics/baugesuche` JSON max 400 token, `source_url` kötelező, `nur aus JSON`)
- `POST /api/v1/ai/summary {postcode, locale, place, politics, baugesuche}` → gateway → `{"summary": "2 mondat"}` + `X-Source: gateway|template`
- FE: `fetch` a `SummaryBar`-ban `?ai=1` / `NEXT_PUBLIC_AI_SUMMARY=1` flag, hiba → `t('summary.template')` fallback → E2E nem törik
- Prompt system: `DE: Fasse in 2 Sätzen auf Deutsch zusammen, nur aus JSON` / `EN/FR/IT` locale szerint

## Elvetve

| Opció | Miért nem |
|---|---|
| B: direct provider httpx | nincs budget/fallback lánc, kulcs rotáció kézi, METHODOLOGY 1.3.1 gatewayt ír elő |
| C: sablon only | determinisztikus de nem „KI”, nem hoz tömörítést |

## Következmény

- Kártyák: `feat: ai summary gateway (DE/EN/FR/IT live)` → `ai_summary_service.py` + `main.py` `POST /api/v1/ai/summary` + FE `SummaryBar ?ai=1` + `tests/unit/test_ai_summary.py` (MockTransport), max 400 sor/file, `NEXT_PUBLIC_AI_SUMMARY` flag
- Validálás: `curl POST /api/v1/ai/summary {8004,de} → 200 summary 2 mondat` + mock teszt `gateway 200 → summary` + `gateway 500 → template fallback`; E2E `ai summary fallback` nem törik ha 8013 `cooldown`
- Kapcsolódó: Research `2026-08-27-ai-summary-live.md`, kód `src/services/ai_summary_service.py`, következő: BE live stabil + FE 500 dev fix külön ADR nélkül

## Kapcsolódó

- Research: `docs/research/2026-08-27-ai-summary-live.md`
- Kód: `src/services/ai_summary_service.py`, `src/main.py`, `frontend/src/app/[locale]/page.tsx`, `frontend/messages/*.json`
- Következő ADR: — (AI live után BE/FE élesítés stabil)
