ROLE: developer. FINISH one spec. The previous dispatch was killed mid-work; its code IS on disk.

REPO: /home/zoltan/swiss_p_map 
SPEC (authoritative, read in full): docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md

STATE: A previous `developer` dispatch implemented the feature but was killed before committing, and
left the tree RED and UNCOMMITTED. Its work is real and good — you are CONTINUING it, not restarting.
Run `git diff` first and read what is already there. Do not discard it.

Uncommitted files (3 files, +279/-13):
  src/main.py                                    (+52)
  src/services/connectors/bfs_voteinfo_client.py (+105)
  src/services/vote_service.py                   (+135)

MEASURED GATE STATUS (orchestrator ran these, this run):
  $ .venv/bin/python -m pytest -q
    -> 2 failed, 248 passed, 1 skipped      [baseline before this work: 250 passed, 1 skipped]
  $ .venv/bin/python -m mypy src/
    -> Success: no issues found in 50 source files      (KEEP THIS)
  $ .venv/bin/python -m ruff check src/
    -> 2 errors:
       src/services/vote_service.py:393:16 BLE001 Do not catch blind exception: `Exception`
       src/services/vote_service.py:411:41 UP017 Use `datetime.UTC` alias (auto-fixable)

THE TWO FAILING TESTS (pre-existing tests — do NOT edit them; make the CODE satisfy them):
  tests/unit/test_vote_service.py::TestVoteService::test_vote_endpoint_returns_200
    asserts `"proposal_id" in data` for GET /api/v1/politics/votes/latest
    ...but the route now returns {"proposal": {...}, "source": ..., "fetched_at": ..., "trust_state": ...}
    so proposal_id is one level deeper than the test expects.
  tests/unit/test_vote_service.py::TestVoteService::test_vote_proposals_list_and_detail
    reads `data["national_yes_percent"]` from GET /api/v1/politics/votes/{id}
    ...same nesting change; also asserts the four fixture IDs 6670/6680/6690/6700 are present.

THE READ THAT MATTERS — the live fetch is WORKING. Do not undo it:
The route returned a real live proposal 6880 with `trust_state: "official_publication"` and a real
`fetched_at`. The four 2024 fixture IDs your sibling test expects are simply no longer the served
set, because the fixture set is now correctly replaced by live data. The failure is a response-SHAPE
and fixture-expectation conflict, not a broken fetch.

REQUIRED OUTCOME — resolve the conflict without lying and without weakening the feature:
- `GET /api/v1/politics/votes/{id}` must keep working for the fixture IDs (6670/6680/6690/6700) —
  they are legitimate seed data. A caller asking for a known fixture proposal must still get it,
  with `national_yes_percent` reachable as the test expects.
- The honest envelope must remain (source / fetched_at / trust_state) and live data must still win
  when the live fetch succeeds.
- Choose the cleanest option that satisfies BOTH: e.g. keep the documented payload at the top level
  the existing contract uses, and add the envelope as ADDITIVE top-level keys
  (`{"proposal_id": ..., ..., "source": ..., "fetched_at": ..., "trust_state": ...}`) rather than
  nesting the payload under "proposal". Nested-under-"proposal" breaks the documented contract for a
  cosmetic gain — prefer the additive shape unless you can prove nesting is required.
- If you conclude instead that the tests encode a stale contract and SHOULD change, do NOT change
  them: that is a PLAN-level decision. Write your case in the report and leave them failing, clearly
  flagged. Do not silently weaken an assertion.
- Fix both ruff errors. `UP017` may be auto-fixed; `BLE001` needs a justified
  `# noqa: BLE001` with a comment explaining the defensive catch, or a narrower exception.

ALSO MUST STILL HOLD (the point of the slice):
- `grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l` >= 2 (pre-fix: 1)
- unreachable host ⇒ labelled `source_pending`/`stale`, HTTP 200, never a fabricated result, never 500
- no new dependency; injected httpx seam so tests need no network

BUDGET: 1200 seconds. If you run out, say "BUDGET EXHAUSTED after item N" and stop — leave the tree
recoverable and state exactly what is incomplete.

Work item numbered list — answer EVERY item. If an item does not apply, say NO explicitly.
1. `git diff --stat` at the START (prove you read the existing work) and at the END.
2. The exact change you made to resolve the coupling, with the diff hunk pasted.
3. Paste post-fix: `pytest -q` (full count), `pytest tests/unit/test_vote_service.py -q`, `mypy src/`,
   `ruff check src/`. All four must be green, with the real numbers.
4. Paste the command proving the parser is now wired, with the pre-fix number next to the post-fix.
5. Paste proof of the honest-failure path: what is returned when the host fails, and the exact JSON.
6. Did you edit any file outside the spec's allowlist? Answer YES/NO with `git status --short` pasted.
7. Did you modify any test file? Answer YES/NO. (Expected: NO.)
8. What is still not done?

COMMIT RULE
Commit your own work by explicit path only (`git add <path>`), never `git add -A`/`git add .`/
`git commit -a`. Never amend. Never push. After committing paste
`git show --name-status --format='' HEAD` so the commit's real contents are on the record.
Grep every identifier you name in the commit message before writing it.

OUTPUT: report to BOTH:
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-dev2.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-dev2.md

ACCEPTANCE: the four gates green with pasted real output, the parser-wiring count >= 2, the honest
failure path demonstrated, the allowlist respected, and the commit verified by name-status.