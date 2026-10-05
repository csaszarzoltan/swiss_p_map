# next-work-loop — queue and record

Loop: `next-work-loop /home/zoltan/swiss_p_map`, started 2026-10-05.
Lock holder: `claude-loop-lock ~/swiss_p_map` (released on every exit path).

## ORIENT (measured this run, not assumed)

- HEAD `adc0093`, tree clean. Was **1 commit ahead of origin** → pushed this run
  (`ee0acf0..adc0093`), now in sync with `origin/master`.
- Suite: **250 passed, 1 skipped** (`.venv/bin/python -m pytest -q`).
- Version agreement: `pyproject.toml` 0.3.0, `frontend/package.json` 0.3.0, tag `v0.3.0`,
  `git describe` = `v0.3.0-7-gadc0093`. All agree. CHANGELOG has an `[Unreleased]` section
  describing the A1/A2/A3 work; its counts were not re-measured this run.
- Stale status files: none found. `git ls-files | grep -Ei 'BLOCKED|STATUS|TODO|KNOWN-ISSUES'`
  returns only `frontend/src/components/PwaStatus.tsx` (a component, not a status file).
- `analysis/` does not exist in this repo; `docs/audits/` is the nearest equivalent.
- Open verdict at ORIENT: `v20261004163958-cc7419` (REQUEST-CHANGES, commit `adc0093`).

## Load-bearingness (ORIENT requirement)

All three vote paths ARE reachable in production — this is not a zero-caller case:
- `BfsVoteInfoClient` → `src/main.py:105`
- `VoteService` → `src/main.py:93` → `GET /api/v1/politics/votes/latest` (`src/main.py:341-344`)
- `SWISS_CANTONS` → `Map3D.tsx:455` ← `next page.tsx:291`

The defect is that a reachable path serves fabricated values *labelled* official.

## STEP 2 ASK — two agents, both untrusted

| dispatch | agent | brief_sha | artifact | bytes |
|---|---|---|---|---|
| ticket 170 | reviewer | 6c8e492edec6 | `.agent-pipeline/audit/reports/nw1-reviewer.md` | 12159 |
| ticket 174 | explore  | (inline)     | `.agent-pipeline/audit/reports/nw1-explore.md`  | 10546 |

**They CONVERGED on the same item** — high confidence, not a disagreement to exploit:
> Wire the existing `VoteService.parse_voteinfo_payload` to the live VoteInfo OGD host
> `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`.

Both also flag **two vacuous tests** (they would pass if the code were deleted):
- `tests/unit/test_spec046_055_060_contract.py:106` — asserts sha length of a constant
- `tests/unit/test_phase3_civic_services.py:13` — same stub, weaker assertion

## STEP 3 REFUTE — every claim re-measured by the orchestrator

Checks run (not inherited from the agents):

1. **Host live:** `curl … sd-t-17-02-20240922 …` → `HTTP 200 | 1977268 bytes | 0.25s`
2. **Municipality granularity real:** `kantone 26`, `gemeinden 161` for canton 0, `bezirke 13`,
   gemeinde keyed by BFS `geoLevelnummer`, fields `jaStimmenInProzent/Absolut`, `stimmbeteiligungInProzent`.
3. **Parser already works:** fed the live payload → `parsed proposal 6710 | cantons 26 | national_yes 36.96`.
4. **Zero callers:** `grep -rn "parse_voteinfo_payload" src/ tests/` → exactly one hit, its own `def`.
   → **wiring slice, not a testing slice.**
5. **Host already known to the repo:** `docs/research/2026-08-27-bfs-vote-data.md:13`.
6. **Not already done:** no commit wired it; the only commit touching the connector is the original
   `90ce630` Phase-3 implementation.
7. **SPEC-056 exists at `PENDING_DEV`** and names no host.

**Consequence — a corrective item, not a new feature.** The report committed as `adc0093` asserts at
line 191: *"Federal per-municipality results, programmatic → **NOT AVAILABLE as an API** … there is
nothing to call."* That is **false**, measured: HTTP 200, 161 gemeinden per canton. The report drew
its negative from `voteinfo.bfs.admin.ch`/`abstimmungen.bfs.admin.ch` (both HTTP 000) and never
fetched the canonical OGD host that this repo has documented since 2026-08-27. The orchestrator
caught this only via the reviewer — it is the same "negative declared without the right probe"
failure the post-task-review of `adc0093` already flagged.

**REFUTE verdict: item ACCEPTED.** All checks passed; none of the rejection criteria apply.

## STEP 4 PLAN

- dispatch ticket (planner) — brief `nw1-brief-planner.md`, spec to
  `docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md`. Scope fixed by the orchestrator:
  **backend only**, live fetch behind the existing injected-httpx seam, honest
  `source`/`fetched_at`/`trust_state`, unreachable host ⇒ labelled `source_pending`, never a
  fabricated result. The map's hardcoded canton colours are explicitly a SEPARATE later slice.

## Carried forward (do not redo)

- `v20261004163958-cc7419` is OPEN and names `adc0093`, which **has already shipped and been pushed**.
  Its two process asks (a `Commands run` section, a `Not covered` section) are documentation gaps in a
  committed file. Its `verification 3/5` is consistent with the measured history rather than stale.
  Decision: fold the `Commands run` / `Not covered` requirement into the SPEC-056b spec's doc duty so
  it lands with the corrective slice, then close the verdict on that measurement. Do **not** re-dispatch
  the research report on its account.
- The report's false line 191 must be corrected (superseded, not appended next to) as part of the
  corrective slice, and the file grepped for the refuted phrasing afterwards.
