ROLE: test-author. Update ONE existing contract test to the new, deliberate contract. Do NOT
implement product code.

REPO: /home/zoltan/swiss_p_map.
CONTEXT: SPEC-056b wired the live VoteInfo OGD fetch. On a SUCCESSFUL live refresh the served
proposal set is now ONLY the live result(s) — the four 2024 fixture proposals are no longer served,
because `trust_state` is per-response and a response cannot honestly be both "official_publication"
and "embedded fixture". That is the point of the slice (SPEC-056b FR-02 "replaces the served
proposals"; §0b.4 "fixtures must never be presented as live").
On FAILURE the fixtures are STILL served but labelled `trust_state: "stale"` — unchanged.
This is a deliberate contract change, not a regression.

CURRENTLY FAILING (measured by the orchestrator, this run):
```
$ .venv/bin/python -m pytest tests/unit/test_vote_service.py -q
1 failed, 3 passed
tests/unit/test_vote_service.py:89
    assert len(items) >= 4
    AssertionError: assert 1 >= 4
    where 1 = len([{'proposal_id': 6880, 'date': '2026-09-27', ...}])
```
Live measurement behind it (real uvicorn, 127.0.0.1:8311):
`GET /api/v1/politics/votes/list` -> 1 item, proposal_id 6880, trust_state official_publication.

MEASURED FACT you must respect: the live OGD publication for vote day 20260927 genuinely carries
ONE proposal. Serving one item is honest; the number 4 came from this repo's own fixture constants.

YOUR TASK — edit `tests/unit/test_vote_service.py` ONLY:
1. Update `test_vote_proposals_list_and_detail` so it encodes the NEW contract. It must NOT assert
   the fixture ids (6670/6680/6690/6700) as part of the LIVE served set. Keep asserting:
   - status 200
   - the response is a list shape (`items`), and `items` is non-empty
   - the envelope carries source/fetched_at/trust_state
   - the detail endpoint still returns 200 with `national_yes_percent` reachable
2. Keep the fixture ids meaningful: if they are still part of any honest path (the failure/stale
   path), assert them THERE, not on the success path.
3. Add the REGRESSION ASSERTION the binding gate asked for — the one that would have caught the
   blocking defect: on a successful refresh the served set contains ONLY live ids, i.e. none of the
   four fixture ids appears under `trust_state == "official_publication"`. If that needs a service-
   level test with the committed fixture via `httpx.MockTransport`, add it to
   `tests/unit/test_spec056b_live_wiring.py` instead — that file's fixture already exists at
   `tests/unit/fixtures/voteinfo_ogd_20260927_trimmed.json`. No network at test time.
4. Do NOT weaken any assertion to make it pass. If you believe an assertion must go, say why in the
   report. Do NOT delete a test.

DO NOT touch `src/`. Do NOT change parsing logic. Commit by explicit path; never `git add -A`;
never amend; never push. BUDGET 1000 s — if you run out, say "BUDGET EXHAUSTED after item N".

NUMBERED ITEMS — answer EVERY one; say NO explicitly if it does not apply:
1. `git diff --stat` for the test files you changed, plus the diff hunks.
2. Pasted post-fix output of: `pytest tests/unit/test_vote_service.py -q` and full `pytest -q`.
3. Pasted `mypy src/` and `ruff check src/`.
4. The exact regression assertion you added, and PROOF it fails against the pre-fix behaviour —
   demonstrate it by temporarily restoring the merge behaviour in a COPY of the module under /tmp
   (never by editing the real file), or by a MockTransport that yields a response the old code would
   have mixed. Paste the failing output.
5. Name every assertion you removed or changed, and justify each.
6. Did you edit anything under `src/`? YES/NO. (Expected: NO.)
7. What could still make the suite green while the served set is dishonest? Name the gap.

COMMIT by explicit path; then paste `git show --name-status --format='' HEAD`.

OUTPUT: report to BOTH
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-testauthor2.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-testauthor2.md

DONE = full suite green with the new contract encoded, the regression assertion present and proven
able to fail, and nothing weakened silently.