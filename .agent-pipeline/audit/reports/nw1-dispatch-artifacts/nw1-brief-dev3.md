ROLE: developer. ONE narrow change. The feature is ALREADY implemented and on disk uncommitted.

REPO: /home/zoltan/swiss_p_map

FIRST: run `git diff --stat src/` and read the existing uncommitted work. It is good — do not revert it.
+279/-13 across src/main.py, src/services/connectors/bfs_voteinfo_client.py, src/services/vote_service.py.
The live VoteInfo OGD fetch already WORKS (it returned real proposal 6880, trust_state
"official_publication"). Do NOT undo the feature.

THE ONE THING TO FIX
Two pre-existing tests fail because the new routes nest the payload:
  GET /api/v1/politics/votes/latest  returns {"proposal": {...}, "source":..., ...}
    -> tests/unit/test_vote_service.py:76 asserts `"proposal_id" in data`   (FAILS: now one level deeper)
  GET /api/v1/politics/votes/{id}    returns {"proposal": {...}, "source":..., ...}
    -> tests/unit/test_vote_service.py:100 reads data["national_yes_percent"] (FAILS: KeyError)
Also `GET .../votes/list` now returns {"items": [...]}; keep `items` at the top level (it already is).

FIX: make the envelope ADDITIVE — spread the original payload's own keys at the TOP level, then add
source / fetched_at / trust_state alongside them. Do NOT nest under "proposal". The nested shape broke
a documented contract for a cosmetic gain.

Then fix exactly these two linter errors and nothing else:
  src/services/vote_service.py:393:16  BLE001  -> narrower except, or `# noqa: BLE001` with a comment
                                                explaining the defensive parse guard
  src/services/vote_service.py:411:41  UP017   -> use `datetime.UTC`

DO NOT: touch any test file; change the parser's parsing logic; add a dependency; touch frontend/;
widen beyond these files; amend; push.

BUDGET: 700 seconds. If you run out, stop and say "BUDGET EXHAUSTED" — do not start anything new.

THEN REPORT (keep it short, paste raw output):
1. `git diff --stat src/` after your change.
2. Output of: `.venv/bin/python -m pytest -q` and `.venv/bin/python -m pytest tests/unit/test_vote_service.py -q`
3. Output of: `.venv/bin/python -m mypy src/` and `.venv/bin/python -m ruff check src/`
4. `git status --short`
5. The exact diff hunk of your envelope change.

COMMIT your work by explicit path (`git add <the files you changed>`), message naming only identifiers
that exist. Then paste `git show --name-status --format='' HEAD`.

Write your report to /home/zoltan/.hermes/cache/scratch/dispatch/nw1-dev3.md
DONE = pytest fully green (251+ passed, 0 failed), mypy clean, ruff clean, committed.