ROLE: developer. Implement ONE spec. Do not redesign it; do not widen its scope.

REPO: /home/zoltan/swiss_p_map @ HEAD adc0093.
SPEC TO IMPLEMENT (read it in full, it is authoritative):
  docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md

The spec's §1 allowlist is binding. In this slice you may CREATE/EDIT only:
  - src/services/connectors/bfs_voteinfo_client.py
  - src/services/vote_service.py
  - src/main.py
  - src/models/vote.py (additive only, and only if genuinely needed)
You may NOT touch: frontend/**, any test file, requirements.txt, pyproject.toml, SPEC-056.
If the implementation proves the allowlist wrong, STOP and say so in your report — do not widen it
silently.

PRE-FIX BASELINE, measured by the orchestrator this run (your work must change these):
  $ grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l      -> 1   (only its own def)
  $ grep -c "AsyncClient" src/services/connectors/bfs_voteinfo_client.py -> 0
  $ grep -c "trust_state" src/main.py                          -> 4
  $ grep -n "httpx\|urllib\|AsyncClient" src/services/connectors/bfs_voteinfo_client.py -> (empty, exit 1)
  $ .venv/bin/python -m pytest tests/unit/test_vote_service.py -q -> 4 passed
  Repo gates to preserve: pytest 250 passed / 1 skipped, mypy strict, ruff clean.

THE ITEM (one narrow change):
Wire the EXISTING, already-correct `VoteService.parse_voteinfo_payload`
(src/services/vote_service.py:311 — do NOT change its parsing logic) to the LIVE VoteInfo OGD host
`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`, so the three
votes routes serve real federal data instead of the four hardcoded 2024 fixtures, with honest
`source` / `fetched_at` / `trust_state` metadata. If the host is unreachable, the response must be an
explicitly labelled `source_pending` state — never a fabricated result.

MEASURED FACTS you can rely on (orchestrator-verified, live):
  - Host returns HTTP 200, 1 977 268 bytes, top keys ['abstimmtag','timestamp','spatial_reference','schweiz'].
  - `schweiz.vorlagen[0].kantone` = 26; `kantone[0].gemeinden` = 161; each gemeinde keyed by BFS
    `geoLevelnummer` with `resultat.jaStimmenInProzent`, `jaStimmenAbsolut`, `stimmbeteiligungInProzent`.
  - Fed the live payload, the existing parser returns: proposal 6710 | cantons 26 | national_yes 36.96.
  - httpx 0.28.1 is already installed and is an existing dependency. Do NOT add a new dependency.

MANDATORY CONSTRAINTS
1. The live fetch must sit behind the existing injected-httpx seam so tests need no network.
2. `source` must name the real host, not a generic label.
3. Unreachable/invalid host ⇒ `trust_state: "source_pending"`, HTTP 200, no fabricated rows. Reuse the
   literal `source_pending` already used at src/main.py lines ~610/666/680 — invent no new vocabulary.
4. Validate the date strictly (`^\d{8}$`); the host is a constant, never user-controlled.
5. Wall-clock budget: 1500 seconds. If you run out, say "BUDGET EXHAUSTED after item N" and stop —
   leave the tree in a state where your partial work is recoverable and SAY what is incomplete.

Work item numbered list — answer EVERY item. If an item does not apply, say NO explicitly.
1. List every file you changed, with `git diff --stat` output pasted.
2. Paste the actual output of each of these, post-fix: the four pre-fix baseline commands above,
   plus `pytest tests/unit/test_vote_service.py -q`, full `pytest -q`, `mypy`, `ruff check`.
3. Proof the fetch is really wired: paste the command that shows the parser now has a caller, and
   its output. State the pre-fix value next to the post-fix value.
4. Prove the NOT-wired case honestly: show what the code returns when the host fails (a mocked
   failure), and the exact JSON. Paste the test or command output.
5. Did you change the parser's parsing logic? Answer YES/NO and prove it with a diff of that function.
6. Did you touch anything outside the allowlist? Answer YES/NO with `git status --short` pasted.
7. What did you assume without measuring? Name each assumption.
8. What is NOT done that the spec asked for?

COMMIT RULE
Commit your own work, by explicit path only (`git add <path>`), before you report — never
`git add -A`, never `git add .`, never `git commit -a`. Never amend. Never push.
After committing, run `git show --name-status --format='' HEAD` and paste it, so the commit's real
contents are on the record rather than the message's claim about them. The commit message must name
only identifiers that exist — grep each one before writing it.

OUTPUT: write your report to BOTH:
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-dev.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-dev.md
Place it there with the commit; do NOT commit the report if it would sweep unrelated paths.

ACCEPTANCE: every item answered, every claim carrying pasted command output, the allowlist respected,
and the four gates green with their real counts in the report.