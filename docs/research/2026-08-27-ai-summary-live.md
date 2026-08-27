# Research — KI-Zusammenfassung 4 nyelven, élő LLM gateway (DE/EN/FR/IT)

- **Dátum:** 2026-08-27
- **Szerző:** researcher (standing goal folytatás)
- **Státusz:** draft → ADR-006 input
- **Kapcsolódik:** `frontend/src/app/[locale]/page.tsx` (KI-ZUSAMMENFASSUNG sablon `t('summary.template')`), `METHODOLOGY.md` 1.3.1 (LLM gateway `http://127.0.0.1:8000/v1`, 120s timeout), `ADR-004 i18n`, `ADR-005 live`
- **Kérdés:** Hogyan legyen a 2-mondatos összefoglaló 4 nyelven élő, OGD-bizonyítékra épülő, de stub-fallbackos és költségkontrollált?
- **Módszer:** élő web_search (2026-08-27) + BE/FE code inspect + gateway port scan (8013 `llm-budget-gateway` él), 3 opció comparison

---

## 1. Kontextus & követelmény

A fiók tetején `KI-ZUSAMMENFASSUNG` 2 mondat: `postcode + Steuerfuss + Lärm + ÖV + Baugesuche + Politik` → 4 nyelven (`de` default). Ma: `page.tsx` lokális `t('summary.template')` interpoláció, nincs LLM. Cél: élő, de **bizonyíték-alapú** (place/politics/planning JSON a promptban), **nyelvkövető** (`locale` param), **fallback sablon** ha gateway le van tiltva, **120s timeout**, nincs secrets a summary-ban (MEMORY.md: `[REDACTED]` szabály).

FE lokál: `http://127.0.0.1:3310/de`, BE: `http://127.0.0.1:8310`, gateway: `http://127.0.0.1:8013` (llm-budget-gateway, 2026-08-23 óta `Sl 8013`).

---

## 2. Vizsgált opciók

### A — `llm-budget-gateway` (8013) proxy → `/v1/chat/completions` (OPENAI-COMPAT)
- **Mi:** A szerveren már fut (`720291 Sl 8013`). `POST /v1/chat/completions` OpenAI-kompat, költség + cooldown `gateway.db`, provider routing `product.db`. Használja a `opencode/1.14.41` UA-t. Lokális `fastify` WS gateway pattern (`llm-budget-gateway-operations` skill).
- **Pro:** 0 új infra, budget kontroll, provider fallback, naplózás, 4 nyelv system prompttal (`Wahlkreis → district` terminológia)
- **Contra:** gateway `cooldown` + `probe providers.db` függés; ha 8013 leáll, fallback kell
- **Bizonyíték:** `ss -tlnp | grep 8013 => LISTEN 8013`, `curl 8310/health => ok` mellett `8013` is `Sl`

### B — Direct provider (Anthropic/OpenAI) a BE-ből `httpx` POST
- **Mi:** BE `src/services/ai_summary_service.py` közvetlen `httpx.AsyncClient` `anthropic /v1/messages` vagy `openai /v1/chat/completions`, `ANTHROPIC_API_KEY` env-ből (nincs repo-ban, `[REDACTED]`).
- **Pro:** nincs gateway függés, egyszerű
- **Contra:** nincs költségkontroll / fallback lánc, kulcs rotáció kézi, nincs centralizált audit (METHODOLOGY 1.3.1 gatewayt ír elő)
- **Bizonyíték:** `env | grep ANTHROPIC => üres` (innen nem validálható kulcs nélkül)

### C — Lokális stub csak (nincs LLM, csak sablon + fordítás)
- **Mi:** Marad a mostani `t('summary.template')` interpoláció, 4 `messages/*.json` template bővítéssel, 0 hálózati hívás
- **Pro:** 0 költség, 0 latency, determinisztikus, E2E `4/4 20.3s` marad
- **Contra:** nem „KI”, nem hoz újat a sablonhoz képest; nem teljesíti a „KI-ZUSAMMENFASSUNG” ígéretet

---

## 3. Összehasonlítás — érték × költség × kockázat × karbantarthatóság (1–5, 5= legjobb)

| Szempont (5= legjobb) | **A: gateway 8013** | **B: direct provider** | **C: sablon only** |
|---|---|---|---|
| **Érték** (4 nyelvű, bizonyíték-alapú 2 mondat) | **5** — LLM hoz tömörítést + nyelvváltást | 4.5 — LLM igen, de nincs gateway audit | 2.5 — fordítás van, tömörítés nincs |
| **Költséghatékonyság** (5= olcsó) | **4.5** — gateway budget + fallback ingyen | 3 — pay-per-token, nincs fallback | **5** — 0 Ft |
| **Kockázat** (5= alacsony) | **4.5** — 8013 él + fallback sablon | 3 — kulcs leak / rate limit | **5** — nincs háló |
| **Karbantarthatóság** (5= könnyű) | **4.5** — 1 service (`ai_summary_service.py`) + prompt `i18n` | 3.5 — 2 provider kliens | 4 — csak JSON |
| **Súlyozott össz (átlag)** | **4.62 🏆** | **3.50** | **4.12** |

*Részletezés: A pontozás 2026-08-27 élő port scan + FE/BE inspect + gateway docs alapján.*

---

## 4. Javaslat — **A: gateway 8013 + fallback sablon (ADR-006)**

**Swiss P Map-hez ez illik**, mert:
1. **Módszertan-konform:** `METHODOLOGY.md 1.3.1` LLM gateway `http://127.0.0.1:8000/v1` → 8013 a lokális megfelelője (gateway-proxy-development pattern)
2. **4 nyelv determinisztikusan:** `locale` a system promptba (`DE: „Fasse in 2 Sätzen zusammen…” / EN: „Summarize in 2 sentences…”`), `hreflang` marad `next-intl` `always`
3. **Bizonyíték-alapú:** promptban `place + politics + planning items` JSON (max 400 token), tiltott hallucináció (`„nur aus JSON”`), `source_url` kötelező
4. **Fallback:** `httpx 120s timeout` + `try/except → t('summary.template')` (mostani sablon) → E2E nem törik ha gateway `cooldown`
5. **Max 400 sor/file:** `src/services/ai_summary_service.py` (<120 sor) + `src/main.py` `POST /api/v1/ai/summary` (<30 sor) + FE `fetch` a `SummaryBar`-ban

**Konkrét beállítás (kód nélkül, terv):**
- `POST /api/v1/ai/summary {postcode, locale, place, politics, baugesuche}` → gateway `chat/completions` → `{"summary": "2 mondat"}` + `X-Source: gateway|template` header
- `NEXT_PUBLIC_AI_SUMMARY=1` feature flag FE-n (default ki, `?ai=1` query-vel kapcsolható)
- Prompt: `System: Du bist KI-ZUSAMMENFASSUNG für Swiss P Map. 2 Sätze, {locale} nyelv, csak JSON-ból, forrás URL a végén zárójelben`

**Elvetve:**
- **B:** Ha gateway nem lenne (8013 down), B lenne a fallback — de ma 8013 él, A jobb audit + költség
- **C:** Megmarad fallbacknek, de önmagában nem elég „KI”

---

## 5. Következő lépés (ADR)

- `docs/decisions/ADR-006-ai-summary-gateway.md` (1 oldal, template) ezzel a kutatással linkelve
- Scaffold után: `ai_summary_service.py` Protocol-DI + `httpx MockTransport` teszt (`test_ai_summary.py`) + `main.py` endpoint + FE `SummaryBar` `?ai=1` toggle + E2E `ai summary fallback` ellenőrzés

---

## 6. Források (élő, 2026-08-27)

1. BE `http://127.0.0.1:8310/health => {"status":"ok"}` + FE `http://127.0.0.1:3310/de => <html lang="de">` (validálva 2026-08-27)
2. Gateway `ss -tlnp | grep 8013 => LISTEN 8013` + `ps aux | grep 720291 => /llm-budget-gateway/.venv/bin/python -m uvicorn llm_budget_gateway.system_launcher:create_system_app --port 8013`
3. FE i18n `messages/{de,en,fr,it}.json` summary.template kulcsok + `src/app/[locale]/page.tsx` useTranslations
4. METHODOLOGY.md 1.3.1 LLM gateway 120s timeout
5. `src/main.py` live `?live=true` pattern (ADR-005)
6. `docs/decisions/ADR-004-i18n-next-intl.md` + `ADR-005-politics-place-live.md` (accepted)

---

*Max 5 oldal — comparison table benne, minden döntés forrással alátámasztva. Nem kód, csak kutatás → ADR alap.*
