# nw2 tester report — SPEC-056c honest sync probe

```
dispatch:  inline prompt (tester brief, no brief file path supplied)
agent:     tester
repo:      /home/zoltan/swiss_p_map @ b3ee2bd
brief:     sha256:5818d1cef597
verdict:   none - first pass
status:    DONE — all 6 items answered with pasted output; tree clean after restore
```

Role note: read-only verification. The only write was the mandated in-place
mutation probe (item 2), restored byte-identical via sha256sum -c. No commit
per brief instruction ("Do NOT commit — orchestrator commits after verifying").

## Item 1 — 6-stage STOP command (SPEC-056c §8), run stage by stage

Stages 1-2:

```
$ grep -F -c 'rows = [{"id"' src/services/connectors/bfs_voteinfo_client.py || true
0
$ .venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient as C; s=C().sync(); ...; print('PROBE OK', s.model_dump())"
PROBE OK {'count': 0, 'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', 'source': 'BFS VoteInfo', 'trust_state': 'source_pending', 'fetched_at': None, 'poll_interval_seconds': 60}
```

Stages 3-6:

```
$ .venv/bin/python -m pytest -q 2>&1 | tail -1
264 passed, 1 skipped, 52 warnings in 8.31s
$ .venv/bin/mypy src/ 2>&1 | tail -1
Success: no issues found in 50 source files
$ .venv/bin/ruff check src/ 2>&1 | tail -1
All checks passed!
$ .venv/bin/python docs/specs/validate_specs.py 2>&1 | tail -3
PASS specs=60 requirements=324 acceptance=264 coverage=100%
```

Done-line comparison (§8): `0` / `PROBE OK {count:0,…,source_pending}` /
`264 passed, 1 skipped` / `Success: no issues` / `All checks passed!` /
`PASS specs=60` — all six match. (Note: stage 1 run as `grep -F -c ... || true`
since grep exits 1 on count 0; the count compared is `0`.)

## Item 2 — mutation probe (gate is non-vacuous)

Backup: `cp src/services/connectors/bfs_voteinfo_client.py /tmp/bak_bfs.py`,
both sha256 `4b876ae444...` (identical).

Mutation (real file, in place): `sync()` body replaced with the fabricated
variant — `rows = [{"id": 6670, "yes": 58.2}]`, `count=1`,
`trust_state="official_publication"`.

Subset result on mutated tree:

```
$ .venv/bin/python -m pytest tests/unit/test_spec046_055_060_contract.py tests/e2e/test_phase3_civic_api.py -q
FAILED tests/unit/test_spec046_055_060_contract.py::test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash
FAILED tests/unit/test_spec046_055_060_contract.py::test_spec_056_req_056_002_ac_056_001_sync_trust_metadata
FAILED tests/unit/test_spec046_055_060_contract.py::test_spec_056_req_056_001_ac_056_001_sync_api_contract
FAILED tests/e2e/test_phase3_civic_api.py::test_spec_056_req_056_001_ac_056_001_vote_sync_api
4 failed, 26 passed, 1 warning in 2.41s
```

Exactly the 4 failures the brief requires (T1, T2, T3, T4).

Restore:

```
$ cp /tmp/bak_bfs.py src/services/connectors/bfs_voteinfo_client.py
$ echo "4b876ae444...  src/services/connectors/bfs_voteinfo_client.py" | sha256sum -c
src/services/connectors/bfs_voteinfo_client.py: OK
$ .venv/bin/python -m pytest tests/unit/test_spec046_055_060_contract.py tests/e2e/test_phase3_civic_api.py -q
30 passed, 1 warning in 2.45s
```

Byte-identical restore confirmed; subset green again.

## Item 3 — full suite unchanged

```
$ .venv/bin/python -m pytest -q 2>&1 | tail -3
264 passed, 1 skipped, 52 warnings in 8.51s
```

`264 passed, 1 skipped` — matches.

## Item 4 — three strict gates (tail -1 each)

```
mypy:  Success: no issues found in 50 source files
ruff:  All checks passed!
validate_specs: PASS specs=60 requirements=324 acceptance=264 coverage=100%
```

All pasted verbatim in item 1; repeated here as the item-4 answer.

## Item 5 — honest-probe unit check (AC-02) + route TestClient check (AC-03)

AC-02 is stage 2 above (`PROBE OK {...}` — asserts `trust_state=='source_pending'`,
`count==0`, `fetched_at is None`, sha256 `4f53cda1…`, determinism via double call).
AC-03:

```
$ .venv/bin/python -c "from fastapi.testclient import TestClient; from src.main import app; r=TestClient(app).post('/api/v1/connectors/voteinfo/sync'); ..."
OK {'count': 0, 'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', 'source': 'BFS VoteInfo', 'trust_state': 'source_pending', 'fetched_at': None, 'poll_interval_seconds': 60}
```

(status 200 asserted in-process; body is the exact §4.1 shape. TestClient runs the
real FastAPI route against `src/main.py:766-768` — no mock in this path. The only
warning is the known Starlette `httpx` deprecation notice from `fastapi/testclient.py:1`.)

Supporting ACs also measured: AC-04 no-I/O grep `0`; AC-05 `open conflict` `0`;
AC-06 `SPEC-056c` in SPEC-056b `4` (≥2); AC-08 three-file subset `36 passed`;
AC-12 model defaults `source_pending None`.

## Item 6 — verdict

All green. Mutation proved: restoring `count=1` / `official_publication` in
`src/services/connectors/bfs_voteinfo_client.py:113-123` (`sync()`) fails exactly
T1/T2/T3/T4 and nothing else; restore is byte-identical and green.

No file left dirty: final `git status --short` output empty (exit 0) at `b3ee2bd`.
Live-surface note: the change performs no I/O by construction (FR-03, AC-04 `0`
matches for `httpx|urlopen|client\.get|requests\.` in the `sync()` body), so there
is no live endpoint to drive beyond the real TestClient route check above; no mock
stands in the verified path. No defect filed — nothing failed.

Model-alive proof: read `docs/specs/SPEC-056c-honest-sync-probe.md` in full (547
lines) plus `src/services/connectors/bfs_voteinfo_client.py:1-60,110-135` to locate
the `sync()` body for the mutation; all pasted outputs above are from this run's
own commands, not quoted counts.
