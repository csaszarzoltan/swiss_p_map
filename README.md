# Swiss P Map

Új projekt — svájci P-térkép. Induló állapot: stratégiai dokumentumok + módszertan, kód még nincs.

## Mi van most
- `AGENTS.md` — agent context (bármelyik LLM olvassa)
- `METHODOLOGY.md` — általános fejlesztési szabályok
- `workflows/principles.md` — munkaelvek, szerepek
- `docs/decisions/ADR-000-template.md` — döntés-sablon
- `docs/research/`, `docs/competitor/` — kutatási keret

## Következő lépések (javasolt sorrend)
1. **Kickoff research** → `docs/research/YYYY-MM-DD-kickoff.md`: mit is építünk pontosan? 3 opció comparison table-lel (pl. web app / mobil / API-first)
2. **ADR-001** → stack + architektúra döntés (1 oldal)
3. Scaffold a döntés alapján (tests + src keret)
4. CI (GitHub Actions) az ADR-ben választott tesztfuttatóval
5. Heti scout cron + nightly teszt cron bekötése (Hermes cron, mint az AI_prod_engine-nél)

## Módszertan
A módszertan LLM-független: bármelyik agent (Claude, GPT, Gemini, Hermes...) dolgozhat itt. Kötelező minimum: **dokumentálj** (`docs/research` + `docs/decisions`) és **tesztelj** mielőtt késznek mondod. Részletek: `workflows/principles.md`.

## Requirements
Még nincs futtatási környezet — az ADR-001 dönt róla.
