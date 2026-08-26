# Swiss P Map — Munkaelvek (Principles)

> Minden agent ezt olvassa belépéskor. Rövid, verifikálható.

## Workdir
- Root: `~/swiss_p_map`
- Stack: **még nincs eldöntve** — az ADR-001 dönt (kickoff research alapján)
- Teszt: az ADR-001 választja (pytest / vitest / go test...); amíg nincs kód: `docs/*.md` → példa-ellenőrzés

## Validációs scope
| Változás | Mit kell futtatni |
|---|---|
| `src/**/*.py` | pytest (ha Python lesz) |
| `src/**/*.ts` | vitest/jest + tsc (ha TS lesz) |
| `docs/*.md` | példa-ellenőrzés, nem teszt |
| Bármelyik | commit előtt `git diff --stat` ellenőrzés |

## Szerepek (funkciók, bármelyik LLM eljátszhatja)
- researcher: kutatás → `docs/research/YYYY-MM-DD-*.md` (max 5 oldal, comparison table)
- analyst: szintézis → `docs/decisions/ADR-*.md` (max 1 oldal)
- developer: max 3 file/kártya, RED→GREEN bizonyítás
- tester: teljes suite zöld mielőtt "kész"
- release-manager: CHANGELOG + tag
- documenter: docs frissítés minden feature-rel

## Tudás forrása (prioritás)
1. Ez a file + `AGENTS.md` + `METHODOLOGY.md`
2. `docs/decisions/ADR-*.md`
3. Kódgráf / `git log`

## Állj meg emberi döntésig ha
- ADR-nélküli nagy döntés (stack, architektúra)
- Több mint 3 file-t érintene a változtatás
- Teszt piros és nem világos miért

## Eszköz-függetlenség
A fentiek **funkciók**, nem szoftverek. "Állj meg" = issue/comment/üzenet bárhol. RED→GREEN = bármilyen teszt-keretrendszer. Az LLM válassza meg a saját eszközét — a kimenet számít: **docs + tesztek + git history**.


## Deep research mód (mély kutatás — VOC + konkurencia + feature-siker)

Mély kutatásnál a „keress rá” nem elég — **bányássz + bizonyíts** (verbatim idézet + URL + dátum).

### Forrásmix (ICP szerint — ne csak Google)
| ICP / projekt | Kötelező watering hole-ok |
|---|---|
| B2C / SMB (swiss_p_map, mealmind, receipts-lens) | Reddit (releváns subok), App Store / Play 1-3★, Trustpilot / G2 / Capterra, Product Hunt, YouTube komment, IndieHackers |
| Tech / B2B | HackerNews (Algolia), r/devops / r/programming, LinkedIn, job postingok (trigger events), Stack Overflow |
| Hír / trend | `agent-reach` RSS + `competitor-news-monitor` heti cron + Google News + defuddle |

Minden idézet: `Forrás | Verbatim (szó szerint, "...") | Kontextus | Dátum | URL | Érzelem | Téma (pain/trigger/desired_outcome/alternative/praise/complaint/JTBD)`. Nincs parafrázis — ha nincs pontos idézet: `no source found`.

### Forrás-hűség (grounded-citations — kötelező)
- Minden külső tényhez `scripts/sources.py` ledger: `reset` → `add <url>` → írás közben `[n]` per mondat (max 3) → `render --cited-in draft.md` → `verify` (és `--evidence` + `quote --from` ha fact-check).
- Ledger párhuzamos subagenteknél: közös `--ledger` path (különben ID-ütközés).
- Keresési snippet ≠ forrás — csak `web_extract` / `defuddle` utáni oldalra hivatkozz.

### Feature-siker rubrika (1-5, minden vizsgált feature-re)
| Dimenzió | Jel | Forrás |
|---|---|---|
| Kereslet | hányan kérik / panaszkodnak rá (freq × intensity) | Reddit/HN verbatim gyakoriság |
| Elégedettség | G2/Capterra rating + 1-3★ arány | scraped reviews |
| Organikus vonzerő | traffic becslés | DataForSEO / SimilarWeb free / site: keresés |
| Árazási validáció | melyik tierben van, van-e felár | pricing page |
| Fejlesztési tempó | changelog commits / hó | changelog scrape |
Átlag = feature siker-score. Az ADR „Elvetve” táblája mellé tedd — onnantól szám, nem vélemény.

### Orchestration (párhuzamos külső agentek)
```
Hermes koordinátor (ledger reset)
 ├─ gemini #1: Reddit + HN  (párhuzamos, GEMINI_CLI_TRUST_WORKSPACE=true)
 ├─ gemini #2: Twitter/X + Product Hunt + App Store  (párhuzamos)
 ├─ gemini #3: News/RSS + V2EX  (párhuzamos)
 └─ (gyűjtés után) agy: competitor scrape + szintézis  (SZEKVENCIÁLISAN — egyszerre 1, kvóta!)
→ analyst (Hermes): JTBD + Top Themes (freq×intensity) + competitor matrix
→ docs/research/YYYY-MM-DD-deep-dive.md (Sources + evidence quotes)
→ docs/decisions/ADR-NNN.md
```
Prompt-sablonok: `docs/research/prompts/gemini-miner.md` (VOC bányász) + `docs/research/prompts/agy-scorer.md` (competitor/feature scorer).


## Session elveszett? Nem baj
Minden tudás git-ben. Session = beszélgetés history, nem storage.
