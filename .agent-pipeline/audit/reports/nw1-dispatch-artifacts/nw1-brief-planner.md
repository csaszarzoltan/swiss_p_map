ROLE: planner. Produce ONE narrow spec. Do NOT implement. Do NOT decide product direction
beyond the scope stated here — the scope is already decided and measured.

REPO: /home/zoltan/swiss_p_map @ HEAD adc0093 (clean tree).

MEASURED FACTS (verified by the orchestrator with live commands — treat as given, do not re-derive,
but you MAY verify):
- `BfsVoteInfoClient.sync()` (src/services/connectors/bfs_voteinfo_client.py:12-16) is a stub:
  `rows = [{"id": 6670, "yes": 58.2}]` — never opens a socket. No httpx/urllib import.
- `VoteService.parse_voteinfo_payload` (src/services/vote_service.py:311) EXISTS and correctly
  parses the real payload. Measured: fed a live payload it returned `proposal 6710 | cantons 26 |
  national_yes 36.96`.
- That parser has ZERO callers: `grep -rn "parse_voteinfo_payload" src/ tests/` returns exactly one
  hit — its own `def`. This is a wiring defect, not a testing gap.
- The live OGD host is REAL and was never called by this repo:
  `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`
  Measured HTTP 200, 1 977 268 bytes, top keys `['abstimmtag','timestamp','spatial_reference','schweiz']`,
  `schweiz.vorlagen[0].kantone[0].gemeinden` = **161 municipalities**, 26 cantons, each gemeinde keyed by
  `geoLevelnummer` (BFS) with `resultat.jaStimmenInProzent` etc.
- The host is already documented in the repo's OWN earlier research:
  `docs/research/2026-08-27-bfs-vote-data.md:13`.
- The currently-served data is 4 hardcoded 2024 fixtures (IDs 6670/6680/6690/6700,
  `vote_service.py:223-272`), served at `GET /api/v1/politics/votes/latest` (src/main.py:341-344).
- SPEC-056 exists and is `implementationStatus: PENDING_DEV` —
  `docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md`. It names NO host/URL.
- Repo gates: pytest 250 passed / 1 skipped; mypy strict; ruff.

THE ITEM (single, narrow — do not widen it):
Wire the EXISTING parser to the LIVE host so the votes endpoints serve real federal data instead of
2024 fixtures, with honest `source` / `fetched_at` / `trust_state` metadata, and fail to a clearly
labelled `source_pending` state rather than fabricating a result when the host is unreachable.

Scope decisions already made by the orchestrator — do NOT reopen them, but DO state them in the spec:
- BACKEND ONLY for this slice. Do not touch frontend/ in this slice; the map's hardcoded canton
  colours are a SEPARATE, later slice.
- The live fetch must be behind the existing dependency-injection seam (httpx client injected), so
  tests need no network.
- No new external dependency. httpx is already a dependency.

Work item numbered list — answer EVERY item. If an item does not apply, say NO explicitly.
1. Exact Target Files allowlist (line-level where possible). Keep it as small as the change allows.
2. The functional requirements, each numbered and individually testable.
3. The API contract for any endpoint whose behaviour changes: method, path, status codes, and the
   exact JSON shape including the metadata fields. State what is UNCHANGED.
4. Acceptance criteria as RUNNABLE commands — one per criterion, each a single command whose output
   is unambiguous. Include the exact expected output. Every command you give MUST be one you actually
   executed in this repo during planning; mark any you did not run as "not run".
5. The NEGATIVE acceptance: the exact command that proves the fix is wired (e.g. a grep that now
   finds a caller, or a test that fails on the pre-fix tree). State how it FAILS pre-fix — the
   pre-fix expected output.
6. The STOP command for this item: the single command whose output means this item is done.
7. Risks and the honest limits: what could make the live fetch fail in production (host down,
   schema drift, date format, caching), and what the code must do in each case. Name anything you
   could not determine.
8. What is explicitly OUT of scope for this slice.

BUDGET: 900 seconds of wall clock. If you run out, write "BUDGET EXHAUSTED after item N" and stop.

TARGET FILES: you may CREATE/EDIT only the spec file named below. Do NOT edit product code, do NOT
edit any test, do NOT commit.

OUTPUT
Write the spec to BOTH destinations, so it survives the temp cleanup:
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-spec.md
  (b) /home/zoltan/swiss_p_map/docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md
Do NOT commit. The orchestrator commits after the gate.

ACCEPTANCE: all 8 items individually answered; every acceptance command carries the output you
actually observed (or is marked "not run"); the allowlist is explicit; the negative/pre-fix
behaviour is stated. Also print, as your final message, item 6 (the stop command) only.