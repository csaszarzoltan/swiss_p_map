ROLE: reviewer. Score ONE change. You are the BINDING gate. Read-only — do not edit, commit or fix.

REPO: /home/zoltan/swiss_p_map

THE CHANGE (3 commits):
  33aab13  feat(votes): serve live VoteInfo OGD data instead of 2024 fixtures (SPEC-056b)
  3d21fe5  docs(research): supersede the refuted VoteInfo 'no API' negative
  aebfafe  test(votes): gate the live VoteInfo OGD wiring (SPEC-056b)
Spec: docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md

WHAT IT DOES: wires the pre-existing `VoteService.parse_voteinfo_payload` to the live BFS VoteInfo
OGD host (`ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`) via
`BfsVoteInfoClient.fetch()` + `VoteService.refresh_from_live()`, so three votes routes serve real
federal data instead of four hardcoded 2024 fixtures, with an honest
source/fetched_at/trust_state envelope and a labelled degradation when the host fails.

ORCHESTRATOR-MEASURED FACTS (verify them; do not take them on trust):
```
pytest -q               -> 262 passed, 1 skipped      (before this work: 250 passed, 1 skipped)
mypy src/               -> Success, no issues in 50 files
ruff check src/         -> All checks passed
grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l   -> 4    (pre-fix: 1)
LIVE uvicorn 127.0.0.1:8311:
  GET /api/v1/politics/votes/latest -> HTTP 200, proposal_id 6880,
    titles.de "Volksinitiative «Wahrung der schweizerischen Neutralität (Neutralitätsinitiative)»",
    cantons 26, national_yes 29.84, source "BFS VoteInfo OGD",
    trust_state "official_publication", fetched_at 2026-10-05T23:20:23Z
    and proposal_id / national_yes_percent stay TOP-LEVEL (additive envelope)
  GET /api/v1/politics/votes/list -> items 5 at top level
Pre-fix gate proof: with the post-fix-only import neutralised so assertions execute,
  10 of 12 tests in tests/unit/test_spec056b_live_wiring.py FAIL on the tree at 33aab13~1.
```

SCORE these five dimensions, each 1-5 with the evidence you measured:
1. **target choice** — was the right thing built? (Is wiring the parser the highest-value item, vs
   the alternatives? The repo also has hardcoded canton vote colours in the frontend, a legacy stub
   `BfsVoteInfoClient.sync()` still returning a 6670/58.2 literal, and two known-vacuous tests.)
2. **verification** — does the suite actually prove it? Check the gate can fail. Note that 2 of the
   12 tests pass pre-fix — say which, and whether that matters.
3. **scope discipline** — did it stay inside the spec's 4-file allowlist? Diff each commit.
4. **process honesty** — does the record match reality? Check the commit messages against the code
   (`git show --name-status`, grep every identifier named), and check the corrected research doc for
   any surviving false claim.
5. **evidence survival** — will this be checkable in a month? Reports live in
   `.agent-pipeline/audit/reports/`; the fixture is committed. Name anything that lives only in /tmp.

ANSWER THESE NUMBERED ITEMS. Say NO explicitly if an item does not apply.
1. The five scores, each with the command/output that justifies it. Print the average.
2. Is the legacy `BfsVoteInfoClient.sync()` still returning `[{"id": 6670, "yes": 58.2}]` while
   documented as a legacy probe? Is that acceptable for this slice, or is it a defect that should
   block? Give your reasoning either way.
3. Does the honest-failure path actually avoid fabricating data? Read
   `src/services/vote_service.py` refresh/except handling and state what is served when the host
   fails, quoting the code.
4. Are the two known-vacuous tests
   (`tests/unit/test_spec046_055_060_contract.py:106`, `tests/unit/test_phase3_civic_services.py:13`)
   now superseded, still vacuous, or still load-bearing? Measure, do not guess.
5. Name any remaining concrete gap in this change that a next iteration should address, or say
   NONE.
6. Anything in the spec that the implementation did NOT do?

BUDGET: 900 seconds. If you run out, say "BUDGET EXHAUSTED after item N" and stop.

OUTPUT: write your report to BOTH
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-gate.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-gate.md

FINAL LINE must be exactly one of:
  VERDICT: APPROVE <average>
  VERDICT: REQUEST-CHANGES <average>