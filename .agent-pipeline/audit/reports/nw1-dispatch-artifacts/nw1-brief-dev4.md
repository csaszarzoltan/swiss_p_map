ROLE: developer. ONE narrow correctness fix, named by the binding gate. Do NOT redesign.

REPO: /home/zoltan/swiss_p_map @ HEAD aebfafe.

THE BLOCKING DEFECT (reviewer-scored REQUEST-CHANGES 3.4, and independently reproduced by the
orchestrator against the live server):

`src/services/vote_service.py:408` MERGES the live proposal into a store that was seeded with
fixtures, instead of REPLACING it:

```python
321:  self._proposals: dict[int, FederalVoteProposal] = _all_default_proposals()   # 4 fixture ids
408:  self._proposals[parsed.proposal_id] = parsed                                # INSERT, never clears
409:  self._source = "BFS VoteInfo OGD"
412:  self._trust_state = "official_publication"
```

Nothing clears the fixture ids (6670/6680/6690/6700 — constants in this repo, values that exist
nowhere in the federal publication). So on a SUCCESSFUL live refresh, `/votes/list` serves
`[6880, 6690, 6680, 6700, 6670]` — all five under `trust_state: "official_publication"` and
`source: "BFS VoteInfo OGD"` with a fresh timestamp. A consumer cannot tell a repo constant from a
real federal result. This defeats the entire purpose of the slice.

Orchestrator-verified live against 127.0.0.1:8311:
```
GET /api/v1/politics/votes/list
  trust_state: official_publication | source: BFS VoteInfo OGD
    6880: Volksinitiative «Wahrung der schweizerischen Neutralität»   <- REAL
    6690: Ausbauschritt 2023 der Nationalstrassen                      <- FIXTURE
    6680: Reform der beruflichen Vorsorge (BVG)                        <- FIXTURE
    6700: Bundesgesetz über eine sichere Stromversorgung               <- FIXTURE
    6670: Initiative für eine 13. AHV-Rente                            <- FIXTURE
```

Contradicts SPEC-056b FR-02 ("replaces the served proposals with the live result") and §0b.4
("Fixtures stay as fallback seed data; they must never be presented as live").

THE FIX (one item — do exactly this, nothing else):
On a SUCCESSFUL live refresh, the served proposal store must contain ONLY the live result(s).
Keep the fixtures as fallback for the FAILURE path exactly as today (failure => fixtures served
but `trust_state: "stale"`; empty store => `"source_pending"`). The cleanest shape is a separate
attribute for the live result (e.g. `self._live_proposals`) that the read methods prefer when
`trust_state == "official_publication"`, with the fixture dict left untouched as the fallback —
but any approach that makes the served set honest is acceptable. Do NOT change
`parse_voteinfo_payload`'s parsing logic.

ALSO FIX (three small honesty defects the gate named — still the same commit's scope):
1. `src/services/vote_service.py:6` module docstring says "the served proposals are replaced" —
   make it true (or reword to match the new behaviour).
2. `src/services/connectors/bfs_voteinfo_client.py:120` cites "the SPEC-056b implementation report"
   which DOES NOT EXIST. Remove the citation or replace it with the real artifact name.
3. Update SPEC-056b's status line if the fix changes implementation status.

DO NOT: touch any test file; add a dependency; touch frontend/; change the parser's logic; amend;
push. If you think the fix belongs in a different file than the allowlist permits, STOP and say so.

IMPORTANT — a test must be able to catch this regression, but tests are `test-author`'s job:
do NOT write tests. Instead, state in your report the exact assertion that would fail if the
fixtures reappeared on success, so the next test-author dispatch can write it.

BUDGET: 900 seconds. If you run out, say "BUDGET EXHAUSTED after item N" and stop.

NUMBERED ITEMS — answer EVERY one; say NO explicitly if it does not apply:
1. `git diff --stat` after your change, and the diff hunk of the store-selection logic.
2. Paste post-fix: `pytest -q`, `pytest tests/unit/test_spec056b_live_wiring.py -q`, `mypy src/`,
   `ruff check src/`. All must be green with real counts.
3. PROVE the honesty fix with a real run: drive the live path (uvicorn on 127.0.0.1:8311 or an
   in-process call with a MockTransport fixture) and paste the served proposal ids + trust_state.
   Expected: only live ids under `official_publication`; fixtures absent.
4. PROVE the fallback still works: host failure => fixtures served with `trust_state: "stale"`.
   Paste the output.
5. State the exact one-line assertion that would catch this regression, for the test-author.
6. Did you edit any test file? YES/NO. (Expected: NO.)
7. Anything the gate named that you did NOT fix, and why.

COMMIT by explicit path; grep every identifier you name in the message before writing it. After
committing paste `git show --name-status --format='' HEAD`.

OUTPUT: report to BOTH
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-dev4.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-dev4.md

DONE = the served set on success contains only live proposals, fixtures still serve on failure
under `stale`, all four gates green, committed.