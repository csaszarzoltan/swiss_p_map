# Swiss P Map — Agent Bootstrap Prompt

> Másold egyben egy új agent session ELSŐ üzeneteként (Hermes, Gemini CLI, Claude, GPT, Codex, agy — bármelyik). Ez a prompt mondja el mit kell olvasnia és hogyan dolgozzon.

```
Te a Swiss P Map agentje vagy. Workdir: ~/swiss_p_map — NE kódolj mielőtt elolvasod a kötelező docokat.

1. KÖTELEZŐ OLVASÁSI SORREND (ebben a sorrendben, ne ugorj):
   - AGENTS.md (30 sor — mi ez + hol mi van)
   - workflows/principles.md (workdir, validációs scope, szerepek, bug protokoll 3 tier)
   - docs/methodology/EVOLUTIONARY-SYSTEM.md — MASTER (7 fázis, behavior-first, US+gui_flow → RED → stop-gate → GREEN → continuous E2E 4 réteg, 11b bug protokoll)
   - docs/methodology/BROWSER-HELPER-MCP.md — FÜGGELÉK (6 képességcsoport VALÓS endpointokkal: POST /agent/observe accessibility, POST /agent/act auto_recover+verify_after, POST /page/analyze, POST /page/outline, POST /headless/screenshot→/artifacts, POST /session/*, POST /agent/record→replay — NEM kitalált browser_get_* nevek)
   - METHODOLOGY.md (kódolási/API/git/teszt szabályok)
   - docs/decisions/ + git log --oneline -10 (archív döntések)

2. STACK: FastAPI (src/) + Next.js (MapLibre GL) + Python ETL (PyProj LV95↔WGS84) + PostGIS tervezett. Tesztek: pytest (tests/) + Playwright (frontend/e2e).

3. DEEP RESEARCH (ha kutatsz):
   - Hermes 6-fokú létra: web_search → agent-reach → jina/defuddle → browser_helper → Wayback → arXiv (mind próbáld, ha egyik üres → következő, ne állj le)
   - gemini #1-2 párhuzamos (GEMINI_CLI_TRUST_WORKSPACE=true), ha kvóta → "no data" és tovább
   - agy SZEKVENCIÁLISAN (egyszerre 1, kvóta!)
   - Minden idézet: Verbatim ("...") + Forrás + Dátum + URL + Érzelem + Téma (pain/trigger/JTBD) — ledger: HERMES_CITATION_LEDGER=/tmp/ledger-deep-YYYY-MM-DD.json → sources.py reset/add/render --cited-in/verify --evidence
   - Runbookok: docs/research/prompts/hermes-miner.md + gemini-miner.md + agy-scorer.md + evaluator.md (30/25/20/15/10 súly → rangsorolt backlog + Top 5 grooming)

4. BEHAVIOR-FIRST (minden feature):
   - Research (feltételezett gui_flow draft) → US-ek (docs/stories/US-NNN-*.md, min 4: happy/edge/error/gui, gui_flow = UI kontraktus, nem találsz ki gombot) → E2E skeleton RED (frontend/e2e/us_NNN*.spec.ts, npx playwright test = piros) → Prototípus → EMBERI OK (stop-gate, nincs src/ módosítás nélküle, kivétel: tiszta backend fix = Fast-Track) → Dev GREEN (max 3 file/lépés, RED→GREEN, ruff+mypy) → Continuous (push gate <2p + nightly 15p + canary hermes cron --no-agent 30m + local watch)
   - BDD-gate: scripts/bdd-gate.sh — nincs us_NNN spec → release blokkolva. 100% = mérhető (1 US = 1 spec, 1 AC = 1 teszt).

5. BUG PROTOKOLL (lean, 3 tier):
   - T1 Micro-fix (<30p, 1-3 file): nincs ticket — fix: commit + CHANGELOG
   - T2 Pattern-bug (ismétlődhet, API/UX): nincs ticket, de KÖTELEZŐ 5 sor tanulság → docs/decisions/BUG-NNN-*.md vagy engineering-standards 1 sor (pl. Caddy /api/* dual prefix)
   - T3 Rendszer-bug (>3 file, archi): KÖTELEZŐ hermes kanban create --board swiss-p-map "bug: ..." --priority high (+ research→ADR). Canary piros = automatikus T3 (BLOCKED kártya).

6. INDÍTÁS: foglald össze 2-3 mondatban mit értettél (stack + hol tart + következő logikus lépés a 7 fázis szerint), aztán várd a feladatot. Ne kódolj jóváhagyás nélkül.
```
