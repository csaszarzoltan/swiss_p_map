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

## Session elveszett? Nem baj
Minden tudás git-ben. Session = beszélgetés history, nem storage.
