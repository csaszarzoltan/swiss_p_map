ROLE: test-author. Write ONE gate that FAILS on the pre-fix tree. Do not implement product code.

REPO: /home/zoltan/swiss_p_map.
SPEC: docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md (authoritative).
A `developer` dispatch is implementing the product slice right now. Your job is the GATE ONLY.

THE ITEM:
Wire the existing `VoteService.parse_voteinfo_payload` to the live VoteInfo OGD host
`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`, with honest
`source` / `fetched_at` / `trust_state` metadata, and an explicit `source_pending` state when the
host is unreachable — never a fabricated result.

THE GATE MUST
1. Be a new test file (suggested: `tests/unit/test_spec056b_live_wiring.py`). Do NOT edit existing
   tests in this slice.
2. Use `httpx.MockTransport` (or an injected fake client) so the gate needs NO network.
3. Include a positive case: feed a REAL-SHAPED payload (top keys `abstimmtag`, `timestamp`,
   `spatial_reference`, `schweiz`; `schweiz.vorlagen[0].kantone` = 26 with `gemeinden` arrays) and
   assert the parser path is reached and the envelope carries a real `source` naming the OGD host.
   For the fixture, RECORD REAL DATA — a live fetch is acceptable while authoring, but the committed
   test must run offline. Do not invent a plausible payload; if you cannot obtain a real one, say so.
4. Include the NEGATIVE case that is the whole point of the gate: host unreachable/failing ⇒
   HTTP 200 with `trust_state == "source_pending"` and NO fabricated proposal rows. Assert the
   absence explicitly (e.g. the fixture 2024 IDs 6670/6680/6690/6700 do not appear as live data).
5. FAIL ON THE PRE-FIX TREE. You must demonstrate this and paste it: run your gate against the
   pre-fix code (`git stash` the developer's changes, or check out the pre-fix file into a temp
   copy — NEVER `git checkout`/`git restore` a path another agent is editing, see the rule below)
   and paste the failing output. A gate that passes pre-fix proves nothing.
6. Reuse the existing literal `source_pending`; invent no new vocabulary.

MEASURED PRE-FIX BASELINE (orchestrator-verified, use as your expected pre-fix numbers):
  $ grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l                  -> 1
  $ grep -c "AsyncClient" src/services/connectors/bfs_voteinfo_client.py   -> 0
  $ grep -c "trust_state" src/main.py                                      -> 4
  $ .venv/bin/python -m pytest tests/unit/test_vote_service.py -q           -> 4 passed

HARD RULES
- If `developer` has files in flight, do NOT `git checkout`, `git restore` or `git reset` any path you
  did not write. To prove pre-fix failure, copy the pre-fix version from git into a temp path
  (`git show <rev>:<path> > /tmp/prefix.py`) and import from there, or use a stash you created.
- Commit your own work by explicit path only (`git add <path>`); never `git add -A`/`git add .`/`git commit -a`.
  Never amend. Never push. After committing paste `git show --name-status --format='' HEAD`.
- Budget: 1500 seconds. If you run out, say "BUDGET EXHAUSTED after item N" and stop.

Work item numbered list — answer EVERY item. If an item does not apply, say NO explicitly.
1. The test file path and `git diff --stat` for it.
2. Paste the POSITIVE test run output (real counts).
3. Paste the NEGATIVE (`source_pending`) test run output (real counts).
4. Paste the PRE-FIX failure output, and name exactly which assertion fails and why it cannot pass pre-fix.
5. Paste full `pytest -q` — the whole suite count, plus `mypy` and `ruff check` output.
6. Which of the two vacuous tests identified earlier
   (`tests/unit/test_spec046_055_060_contract.py:106`, `tests/unit/test_phase3_civic_services.py:13`)
   does your gate supersede or make redundant? State it honestly; do NOT delete them in this slice.
   If your gate does not make either redundant, say NO.
7. What could make your gate pass while the production path is still broken? Name the gap.

OUTPUT: report to BOTH:
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-testauthor.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-testauthor.md

ACCEPTANCE: items 1-7 answered, the pre-fix failure pasted as real output, the suite green with its
count, and the gate genuinely able to fail.