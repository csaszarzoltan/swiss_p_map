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

## STEP 5 BUILD — iteration 1, dispatch 1 (ticket 181)

`claude-dispatch: OK on attempt 1 — 99B` — a 99-byte artifact, which is **not** the stall banner
(`grep -c unrecognized_model` = 0). The artifact said only:
> "Async vote routes will need `await` — waiting on my refresh to resolve before I commit anything."

Per the loop's own rule ("a short artifact is not a stall — read it, then diff the target files"),
the diff was checked and **the work is on disk**: +279/−13 across the 3 allowlisted files
(`src/main.py` +52, `src/services/connectors/bfs_voteinfo_client.py` +105,
`src/services/vote_service.py` +135), uncommitted.

**Gates measured by the orchestrator on that uncommitted tree:**
```
pytest -q                    -> 2 failed, 248 passed, 1 skipped   (baseline: 250 passed, 1 skipped)
mypy src/                    -> Success, 50 files
ruff check src/              -> 2 errors (BLE001 vote_service.py:393, UP017 vote_service.py:411)
```

**What is good and must not be undone:** the live fetch genuinely works — the route returned real
live proposal `6880` with `trust_state: "official_publication"` and a real ISO `fetched_at`. The
connector is a clean typed boundary (`VoteInfoFetchError`, strict `^\d{8}$` date validation,
constant host, 10 s budget, injected client, **no fabricated fallback rows**).

**The real defect:** the new code nests the payload under `{"proposal": ...}` / `{"items": ...}`,
which breaks two pre-existing contract tests that read `proposal_id` and `national_yes_percent` at
the top level (`tests/unit/test_vote_service.py:76,100`). Production impact is small —
`fetchVoteProposal` in `frontend/src/lib/api.ts:180` has **no UI consumer** — but the documented
contract is broken for a cosmetic gain, so the additive shape is preferred.

**Also left behind:** the legacy stub `BfsVoteInfoClient.sync()` still returns the `6670/58.2`
literal. The developer documented it honestly as an out-of-scope legacy probe pinned by three
pre-existing tests; that is acceptable for this slice but must not be mistaken for the live path.

**Decision: the same item returns to BUILD — no new item.** Continuation brief `nw1-brief-dev2.md`
carries the measured failure output so the next agent does not have to rediscover it. The item is
NOT complete and must not be recorded as such.

## STEP 5 BUILD — iteration 1, dispatch 2 and 3

**Dispatch 2 (ticket 186)** — 123 B artifact, same mid-work death. No change to the tree.

**Diagnosis before the third attempt.** Measured across the whole host on 2026-10-05:
```
agent=developer  ... nw1-dev.out    artifact_bytes=99    brief 4967 B
agent=developer  ... nw1-dev2.out   artifact_bytes=123   brief 5655 B
agent=developer  ... loop6-dev.out  artifact_bytes=95    brief 8148 B   (another repo)
agent=developer  ... loop2-dev.out  artifact_bytes=5112  brief 4565 B   (another repo)
agent=explore/reviewer/planner      all completed normally
```
So `developer` dies mid-task across repos today while the read-only roles complete. All `.err`
sidecars carry the 81-byte `unrecognized_model` banner. My dispatch-2 brief also carried **two**
items (envelope restructure + ruff fixes), which this loop's own rule names as grounds for splitting.
**Escalation applied: `--max 1`, and a genuinely single-item brief.**

**Dispatch 3 (ticket 187)** — brief 2549 B, one item only. `artifact_bytes=44`, wall 53 s, and the
artifact read *"Fixes applied — running verification now."* → **died after applying, before verifying.**
The diff decided it: **the fix landed.**
```
ruff check src/                          -> All checks passed!
pytest tests/unit/test_vote_service.py   -> 4 passed   (was 2 failed, 2 passed)
```

**Orchestrator re-ran every gate on the recovered tree:**
```
pytest -q      -> 250 passed, 1 skipped      (no regression; 2 failures cleared)
mypy src/      -> Success, no issues in 50 source files
ruff check src/ -> All checks passed!
wiring: grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l  -> 4   (pre-fix: 1)
envelope now ADDITIVE: {**proposal.model_dump(), **envelope}   (nesting removed)
```

**Committed by the orchestrator as `33aab13`** (the developer died before its own commit):
`M src/main.py`, `M src/services/connectors/bfs_voteinfo_client.py`, `M src/services/vote_service.py`
— verified with `git show --name-status`, not `git status`. Every identifier named in the commit
message was greped first (`parse_voteinfo_payload` 4, `refresh_from_live` 5, `VoteInfoFetchError` 8,
`BfsVoteInfoClient` 6).

**LIVE end-to-end check (reserved: the change speaks a real wire protocol).** Against a real uvicorn
on 127.0.0.1:8311, not a mock:
```
GET /api/v1/politics/votes/latest -> HTTP 200 | 4783 B | 0.35 s
  proposal_id : 6880
  titles.de   : Volksinitiative «Wahrung der schweizerischen Neutralität (Neutralitätsinitiative)»
  cantons     : 26 | national_yes: 29.84
  source      : BFS VoteInfo OGD
  fetched_at  : 2026-10-05T23:20:23.695586Z
  trust_state : official_publication
  top-level keys: cantons, date, fetched_at, national_no_percent, national_turnout_percent,
                  national_yes_percent, proposal_id, source, titles, trust_state
GET /api/v1/politics/votes/list   -> items 5, trust official_publication
```
Real 2026 proposal, real timestamp, honest source label, and the original contract keys preserved at
the top level. **This is the strongest evidence in the loop so far** — it is the live path, not a mock.

## STEP 7 RECORD — correction committed as `3d21fe5`

The false negative in `docs/research/2026-10-04-events-elections-data-sources.md` was **superseded in
place, not annotated beside** — the refuted text struck through, the corrective measurement quoted
with its date. Two surfaces carried the claim, both fixed:
line 191 (§3 bullet a) and line 50 (§1 summary table, which said "app only — no API found").
Post-fix sweep for `app only|NOT AVAILABLE as an API` returns exactly one hit: the correction itself
quoting what was refuted, which is the correct outcome.

## Carried forward (do not redo)

- `v20261004163958-cc7419` is OPEN and names `adc0093`, which **has already shipped and been pushed**.
  Its two process asks (a `Commands run` section, a `Not covered` section) are documentation gaps in a
  committed file. Its `verification 3/5` is consistent with the measured history rather than stale.
  Decision: fold the `Commands run` / `Not covered` requirement into the SPEC-056b spec's doc duty so
  it lands with the corrective slice, then close the verdict on that measurement. Do **not** re-dispatch
  the research report on its account.
- The report's false line 191 must be corrected (superseded, not appended next to) as part of the
  corrective slice, and the file grepped for the refuted phrasing afterwards.
