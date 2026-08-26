# Swiss P Map — Agent Context

> Ezt olvassa minden agent belépéskor (Hermes, Gemini CLI, Claude, GPT, Codex, agy...). Rövid — 30 sor.

## Mi ez
**Swiss P Map** — svájci P-térkép projekt (induló: stratégia + docs; a stack a kickoff ADR-ben dől el). Még nincs kód — az első research → ADR → scaffold lánc hozza létre.

## Állapot
2026-08-25: bootstrap. Template módszertan átmásolva AI_prod_engine-ből. Első feladat: `docs/research/` kickoff + `ADR-001`.

## Hol mi van
- `METHODOLOGY.md` — kódolási/API/git/teszt/doc szabályok (általános, érvényes)
- `workflows/principles.md` — workdir, validációs scope, szerepek
- `docs/decisions/ADR-*.md` — minden döntés 1 oldal (template: ADR-000-template.md)
- `docs/research/` — kutatások (max 5 oldal, comparison table)
- `docs/competitor/` — heti scout output
- `tests/` — tesztek (keretrendszer: amit az első ADR választ)

## Szabályok (röviden)
- Döntés nélkül ne kódolj: research → ADR → utána scaffold
- Minden feature: előbb teszt-ötlet, aztán kód (RED→GREEN bármilyen kerettel)
- Max 400 sor/file; type hints + docstring ahol értelmes
- Commit: `<scope>: <leírás>` formátum (lásd METHODOLOGY 4. fejezet)

## Tudás forrása (prioritás)
1. `workflows/principles.md` + ez a file
2. `docs/decisions/ADR-*.md`
3. Kódgráf (ha indexelve) / `git log`

## LLM-függetlenség
A módszertan bármelyik LLM-mel megy. A szerepek funkciók, nem eszközök. Kötelező minimum: dokumentálj (`docs/`) + tesztelj. Több részlet: `AGENTS.md` az AI_prod_engine-ben minta.
