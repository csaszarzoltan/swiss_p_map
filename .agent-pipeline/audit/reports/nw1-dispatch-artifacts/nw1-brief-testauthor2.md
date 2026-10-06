ROLE: test-author. Write ONE gate. Do NOT implement product code.

REPO: /home/zoltan/swiss_p_map @ HEAD 33aab13 (the feature is ALREADY committed).

WHAT WAS BUILT (committed, working):
The existing `VoteService.parse_voteinfo_payload` was wired to the live BFS VoteInfo OGD host
`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json` via
`BfsVoteInfoClient.fetch()` + `VoteService.refresh_from_live()`.
Verified live by the orchestrator: `GET /api/v1/politics/votes/latest` returns
`proposal_id 6880`, `source "BFS VoteInfo OGD"`, `trust_state "official_publication"`,
26 cantons, and the original payload keys stay TOP-LEVEL alongside the envelope.

YOUR JOB: write the gate that FAILS on the PRE-FIX tree.

Suggested file: `tests/unit/test_spec056b_live_wiring.py`. Do NOT edit any existing test.

THE GATE MUST PROVE (each a separate test, no network allowed — use `httpx.MockTransport` or an
injected fake client):
1. POSITIVE — a real-shaped OGD payload (top keys `abstimmtag`, `timestamp`, `spatial_reference`,
   `schweiz`; `schweiz.vorlagen[0].kantone` = 26 with `gemeinden`) reaches the parser and the
   resulting envelope names the REAL host (`source` contains `voteinfo-app.ch` or equals
   "BFS VoteInfo OGD"), with `trust_state == "official_publication"` and a non-null `fetched_at`.
   For the fixture, RECORD REAL DATA — you may fetch the live URL once while authoring, but the
   COMMITTED test must run offline. If you cannot obtain real data, say so; do not invent a payload.
2. NEGATIVE (the point of the gate) — host unreachable / HTTP 500 / non-JSON ⇒ the service does NOT
   fabricate a result: `trust_state` becomes `"stale"` (fixtures present) or `"source_pending"`
   (empty), and the 2024 fixture IDs (6670/6680/6690/6700) are never presented as live data.
3. CONTRACT — the original keys remain TOP-LEVEL (not nested under "proposal"): `proposal_id` and
   `national_yes_percent` are reachable at the top level; `GET .../votes/list` still returns `items`
   at the top level; an unknown proposal id still yields 404.

PRE-FIX BASELINE (orchestrator-measured — use as your expected pre-fix numbers):
```
grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l                  -> PRE-FIX 1  | NOW 4
grep -c "AsyncClient" src/services/connectors/bfs_voteinfo_client.py   -> PRE-FIX 0  | NOW >=1
grep -c "trust_state" src/main.py                                      -> PRE-FIX 4
pytest -q                                                              -> PRE-FIX 250 passed, 1 skipped
```

PROVE THE GATE FAILS PRE-FIX, and paste it. To get the pre-fix code WITHOUT disturbing the working
tree, use a git worktree or a temp copy — e.g.
`git worktree add /tmp/prefix 33aab13~1` then run the gate there, then `git worktree remove /tmp/prefix`.
NEVER `git checkout` / `git restore` / `git reset` a path in the main worktree.
Also describe WHY each assertion cannot pass pre-fix, naming the assertion.

HARD RULES: no product-code changes; no edits to existing tests; commit by explicit path only
(never `git add -A`); never amend; never push; budget 1200 s — if you run out, say
"BUDGET EXHAUSTED after item N" and stop.

NUMBERED ITEMS — answer EVERY one; say NO explicitly if it does not apply:
1. The gate file path + `git diff --stat` for it.
2. Pasted output of the POSITIVE test.
3. Pasted output of the NEGATIVE test.
4. Pasted PRE-FIX failure output + which assertion fails and why it cannot pass pre-fix.
5. Pasted full `pytest -q` (whole suite count), `mypy src/`, `ruff check src/`.
6. Does your gate make either known-vacuous test redundant
   (`tests/unit/test_spec046_055_060_contract.py:106`, `tests/unit/test_phase3_civic_services.py:13`)?
   State honestly; do NOT delete them.
7. What could make your gate pass while the live production path is still broken? Name the gap.
8. If `git worktree` was unavailable or failed, say so and describe the alternative you used.

OUTPUT: report to BOTH /home/zoltan/.hermes/cache/scratch/dispatch/nw1-testauthor.md and
/home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-testauthor.md

DONE = gate committed, fails on the pre-fix tree with pasted proof, and the full suite green.