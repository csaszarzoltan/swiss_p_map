Refusal + hand-off: the brief asks me to write two report files; the reviewer role is read-only and my tool grant has no Write/Edit, so I will not write either destination. The verdict/report text below is the deliverable — orchestrator to land it at `/home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw2-reviewer.md` (and scratch copy if needed) and commit after verifying.

Proved alive by reading: `src/main.py:351-389`, `src/services/vote_service.py:361-431 + 459-520`, `src/services/connectors/bfs_voteinfo_client.py:58-124`, `docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md:70-76`.

HEAD measured: `f5c27a2 docs(nw1): close the false-open spec status and preserve the loop's dispatch artifacts` (tree clean per `git status --short` empty at start of run).

---
1. Single most concrete gap the last change left:
`BfsVoteInfoClient.sync()` still returns hardcoded `[{"id": 6670, "yes": 58.2}]` labelled `trust_state="official_publication"`, served unauthenticated on reachable `POST /api/v1/connectors/voteinfo/sync` — in direct violation of SPEC-056b FR-01 ("No hardcoded rows remain on any code path"). The last change (`f5c27a2`, docs-only) did not touch it.

2. Command + real output proving it TODAY (all run at HEAD `f5c27a2`):
```
$ grep -n 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py
123:        rows = [{"id": 6670, "yes": 58.2}]

$ sed -n '766,768p' src/main.py
@app.post("/api/v1/connectors/voteinfo/sync")
def connector_voteinfo_sync() -> dict[str, object]:
    return _voteinfo_connector.sync().model_dump()

$ sed -n '36,44p' src/services/connectors/bfs_voteinfo_client.py
    count: int
    sha256: str
    source: str = "BFS VoteInfo"
    trust_state: str = "official_publication"
    poll_interval_seconds: int = 60

$ .venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient; s=BfsVoteInfoClient().sync(); print(s.model_dump())"
{'count': 1, 'sha256': '8c154363199ba8172033b7e119d991ba0231be27d6b2a7ab5a9c094dd0a9d5b5', 'source': 'BFS VoteInfo', 'trust_state': 'official_publication', 'poll_interval_seconds': 60}

$ sed -n '70,76p' docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md
- **FR-01 [MUST]:** `BfsVoteInfoClient` performs a real HTTPS GET against
  `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`
  for a caller-supplied vote date (`YYYYMMDD`), using an injected `httpx.AsyncClient`
  (optional param, default `None` → create-per-call with `timeout=10`), and returns the
  raw JSON bytes/dict. No hardcoded rows remain on any code path.
```
No inference: the stub bytes, the route serving it, the `official_publication` label, and the FR-01 sentence it contradicts were each read/ran above.

3. Does a test already cover the gap? NO — the existing tests pin the stub as correct instead of failing it.
```
$ .venv/bin/python -m pytest tests/unit/test_vote_service.py tests/unit/test_spec056b_live_wiring.py tests/unit/test_spec046_055_060_contract.py tests/unit/test_phase3_civic_services.py -q
48 passed, 52 warnings in 4.28s
```
Covering tests that assert the defective behavior (all green above, so the gap is unguarded): `tests/unit/test_spec046_055_060_contract.py:105` (`sync_deterministic_hash`), `:111` (`sync_trust_metadata` asserts `trust_state == "official_publication"`), `:118` (`sync_api_contract` asserts `POST .../sync` returns `count==1`), and `tests/unit/test_phase3_civic_services.py:13` (asserts `len(sync().sha256)==64`). None feeds a live/MockTransport payload through `sync()`; none can fail if the OGD fetch is deleted.

4. Is the gap already recorded somewhere? YES — recorded as open, not closed.
```
$ grep -rn "VoteSync\|connectors/voteinfo/sync\|hardcoded rows" .agent-pipeline/audit/reports/ analysis/next-moves.md docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md src/services/connectors/bfs_voteinfo_client.py
.agent-pipeline/audit/reports/nw1-gate.md:132: *"No hardcoded rows remain on any code path"*, and allowlist item 1 says *"Replace stub `sync()`"*.
.agent-pipeline/audit/reports/nw1-gate.md:188: `POST /api/v1/connectors/voteinfo/sync` still serves a fabricated `count: 1`.
.agent-pipeline/audit/reports/nw1-gate.md:211: - **FR-01 "No hardcoded rows remain on any code path"** - VIOLATED. `sync()` returns ...
analysis/next-moves.md:105: **Also left behind:** the legacy stub `BfsVoteInfoClient.sync()` still returns the `6670/58.2` ...
docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md:74: raw JSON bytes/dict. No hardcoded rows remain on any code path.
src/services/connectors/bfs_voteinfo_client.py:118: the out-of-scope ``POST /api/v1/connectors/voteinfo/sync`` route.
```
It is NOT recorded in `docs/audits/` (`grep` there returned no hits for `VoteSync|voteinfo/sync`) and NOT closed by `f5c27a2` (`git show --stat HEAD` is docs/artifacts only, no `src/` touch). So: known-open, still unfixed.

5. Vacuous coverage (at most 2)? YES, 2 — both pin the stub in item 3 and cannot fail on a broken OGD contract:
- `tests/unit/test_phase3_civic_services.py:13` — `assert len(BfsVoteInfoClient().sync().sha256) == 64`. Why vacuous: `sync()` hashes a constant (`json.dumps([{"id":6670,"yes":58.2}])`); any constant has a 64-char sha256. Deleting the entire `fetch()`/OGD path, inverting it to raise, or replacing the body with `return VoteSync(count=1, sha256="0"*64)` keeps it green. Never opens a socket (cf. CLAUDE.md §3d).
- `tests/unit/test_spec046_055_060_contract.py:105` — `a, b = sync(), sync(); assert a.sha256 == b.sha256; assert len==64`. Why vacuous: determinism-of-a-constant; same three mutants above keep it green. Checked by reading both test bodies (`sed -n '95,125p'` contract file, `sed -n '1,30p'` phase3 file) plus the `sync()` body at `bfs_voteinfo_client.py:110-124`.
Not claimed: the SPEC-056b gate tests (`test_spec056b_live_wiring.py`, `test_vote_service.py:163-186`) are NOT vacuous — the post-task review proved in-place mutation `vote_service.py:427` fails 2 of them.

6. Risk of NOT fixing (one sentence): Any consumer or downstream agent calling `POST /api/v1/connectors/voteinfo/sync` receives fabricated vote `6670/58.2` mislabelled `official_publication` as if it were a certified federal count, re-creating exactly the fabricated-official defect SPEC-056b was shipped to kill.

7. What would satisfy me (exact command + expected output):
```
$ .venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient; print(BfsVoteInfoClient().sync().model_dump())" && grep -rn '6670.*58.2\|rows = \[{"id"' src/ | wc -l && .venv/bin/python -m pytest tests/unit/test_spec046_055_060_contract.py tests/unit/test_phase3_civic_services.py -q
```
Expected when closed (one of): either `sync()` is removed/rewired so the command shows live-derived `count`/`sha256` with honest `trust_state` (not `official_publication` on a constant) or the route returns a labelled non-official probe; AND `grep ... | wc -l` prints `0`; AND the two pinning tests are updated to assert the new honest behavior and the suite prints `all passed` (currently `48 passed` with the defect pinned — that count must be re-measured post-fix, not carried forward).

`git log --oneline -1` seen: `f5c27a2 docs(nw1): close the false-open spec status and preserve the loop's dispatch artifacts`. Test command + counts run: `.venv/bin/python -m pytest tests/unit/test_vote_service.py tests/unit/test_spec056b_live_wiring.py tests/unit/test_spec046_055_060_contract.py tests/unit/test_phase3_civic_services.py -q` → `48 passed`. No file modified by my commands (read-only; no restore needed). Could not write destination (b) — no Write/Edit grant; orchestrator to write this text to `.agent-pipeline/audit/reports/nw2-reviewer.md`.

BfsVoteInfoClient.sync() still serves hardcoded 6670/58.2 as official_publication on POST /api/v1/connectors/voteinfo/sync, violating SPEC-056b FR-01.
