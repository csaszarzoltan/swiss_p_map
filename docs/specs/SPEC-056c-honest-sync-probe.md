# SPEC-056c — Honest network-free probe for `POST /api/v1/connectors/voteinfo/sync`

| Field | Value |
|---|---|
| ID | SPEC-056c |
| Parent | SPEC-056 (`docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md`, `implementationStatus: PENDING_DEV` — still true, see §5.2) and SPEC-056b (`docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md`, FR-01 status note, see §5.1) |
| Scope | Backend only — remove the fabricated vote row from `BfsVoteInfoClient.sync()`, retarget the served contract to an honest probe |
| Status | SPEC_READY (for developer dispatch) |
| Date | 2026-10-06 |
| Repo | `/home/zoltan/swiss_p_map` @ `f5c27a2` |
| Brief | `dispatch/nw2-brief-planner.md`, sha256:`ea083bcda27f` (equals `$CLAUDE_BRIEF_SHA`, verified by `sha256sum`) |
| Research | `no-live-validation` for every claim about the live OGD host — this spec's chosen path performs **no I/O**, so no live-host claim is load-bearing (see §10) |

## 0. Measured facts (planner-run, 2026-10-06, HEAD `f5c27a2`)

Every command below was executed by the planner during planning; outputs are pasted verbatim.

**0.1 The fabrication and its label**

```
$ grep -n 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py
123:        rows = [{"id": 6670, "yes": 58.2}]

$ .venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient; print(BfsVoteInfoClient().sync().model_dump())"
{'count': 1, 'sha256': '8c154363199ba8172033b7e119d991ba0231be27d6b2a7ab5a9c094dd0a9d5b5',
 'source': 'BFS VoteInfo', 'trust_state': 'official_publication', 'poll_interval_seconds': 60}
```

Note the `VoteSync` model default itself (`src/services/connectors/bfs_voteinfo_client.py:38`):
`trust_state: str = "official_publication"` — the dishonest value is baked into the type default,
not only into `sync()`.

**0.2 Reachability — one production caller, no frontend consumer**

```
$ grep -rn '\.sync()' src/ --include="*.py"
src/main.py:768:    return _voteinfo_connector.sync().model_dump()

$ grep -rn 'connectors/voteinfo' frontend/ ; echo "grep-exit=$?"
grep-exit=1                      # no match anywhere in frontend/

$ grep -rn 'voteinfo/sync' . 2>/dev/null | grep -v '\.git/' | grep -v '\.venv' | grep -v node_modules
tests/unit/test_spec046_055_060_contract.py:119: ... c.post("/api/v1/connectors/voteinfo/sync") ...
tests/e2e/test_phase3_civic_api.py:13: ... c.post("/api/v1/connectors/voteinfo/sync") ...
analysis/next-moves.md:48,83,94   (orchestrator's loop record — documents the defect)
docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md:48  (SPEC-056 §8 names the route)
docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md:128,212        (out-of-scope mentions)
.agent-pipeline/audit/reports/*.md                              (review/gate reports)
src/main.py:766: ... @app.post("/api/v1/connectors/voteinfo/sync") ...
src/services/connectors/bfs_voteinfo_client.py:118: ... docstring ...
```

No script, runbook, or code path in this repo consumes the route's *data* other than the tests.

**0.3 The three pinning tests (grep, planner-run)**

```
$ grep -rn 'voteinfo/sync\|BfsVoteInfoClient().sync()' tests/ --include="*.py"
tests/e2e/test_phase3_civic_api.py:13        assert c.post("/api/v1/connectors/voteinfo/sync").json()["count"] == 1
tests/unit/test_phase3_civic_services.py:14  assert len(BfsVoteInfoClient().sync().sha256) == 64
tests/unit/test_spec046_055_060_contract.py:106,112,119
```

**0.4 The live path already exists and must not be touched (verified)**

```
$ grep -n 'refresh_from_live\|parse_voteinfo_payload' src/main.py src/services/vote_service.py | head
src/main.py:359:    await _vote.refresh_from_live()
src/main.py:375:    await _vote.refresh_from_live()
src/main.py:389:    await _vote.refresh_from_live()
src/services/vote_service.py:361:    async def refresh_from_live(self, vote_date: str | None = None) -> bool:
src/services/vote_service.py:459:    def parse_voteinfo_payload(
```

`refresh_from_live()` already implements the honest-state machine for the real data path:
success → `official_publication` (`vote_service.py:431`), failure →
`stale`/`source_pending` (`:408,:412,:422`), never 500.

**0.5 Closed trust vocabulary already in the repo**

```
$ grep -n 'source_pending\|"stale"' src/services/weather_climate_service.py | head
src/services/weather_climate_service.py:27:    "official_publication",
src/services/weather_climate_service.py:29:    "stale",
src/services/weather_climate_service.py:30:    "source_pending",
```

(also SPEC-056b §3: *"`trust_state` vocabulary (closed): `official_publication` | `stale` | `source_pending`"*, line 106.)

**0.6 Baseline gates (all three run by the planner, pre-fix)**

```
$ .venv/bin/python -m pytest -q  | tail -1
264 passed, 1 skipped, 52 warnings in 13.52s
$ .venv/bin/mypy src/  | tail -1
Success: no issues found in 50 source files
$ .venv/bin/ruff check src/  | tail -1
All checks passed!
$ .venv/bin/python docs/specs/validate_specs.py
PASS specs=60 requirements=324 acceptance=264 coverage=100%
$ .venv/bin/python -m pytest tests/unit/test_spec046_055_060_contract.py tests/e2e/test_phase3_civic_api.py tests/unit/test_phase3_civic_services.py -q | tail -1
36 passed, 1 warning in 5.63s
```

**0.7 Pre-fix failure of the post-fix assertions (the negative acceptance, measured)**

```
$ .venv/bin/python -c "
from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient
s = BfsVoteInfoClient().sync()
print('observed trust_state =', repr(s.trust_state), 'count =', s.count)
assert s.trust_state == 'source_pending' and s.count == 0
"
observed trust_state = 'official_publication' count = 1
AssertionError: trust_state/count != source_pending/0  <-- pre-fix failure

$ .venv/bin/python -c "
from fastapi.testclient import TestClient
from src.main import app
r = TestClient(app).post('/api/v1/connectors/voteinfo/sync')
print('status', r.status_code); b = r.json(); print('body', b)
assert b['count'] == 0 and b['trust_state'] == 'source_pending' and b['fetched_at'] is None
"
status 200
body {'count': 1, 'sha256': '8c154363199ba8172033b7e119d991ba0231be27d6b2a7ab5a9c094dd0a9d5b5', 'source': 'BFS VoteInfo', 'trust_state': 'official_publication', 'poll_interval_seconds': 60}
pre-fix failure: AssertionError
```

**0.8 SPEC status claims checked**

```
$ grep -n 'No hardcoded rows' docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md
74:  raw JSON bytes/dict. No hardcoded rows remain on any code path.        <- FALSE at HEAD

$ sed -n '128,129p' docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md
  SPEC-056 §8 do NOT exist in this tree — NOT introduced here (out of scope, §8).
                                                                            <- also FALSE: both exist
$ grep -n '"/api/v1/votes/proposals"\|connectors/voteinfo/sync' src/main.py
669:@app.get("/api/v1/votes/proposals")
766:@app.post("/api/v1/connectors/voteinfo/sync")

$ grep -n 'implementationStatus' docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md
6:implementationStatus: PENDING_DEV
$ grep -rn 'feature056' frontend/ ; echo "grep-exit=$?"
grep-exit=1                     # SPEC-056 §11 i18n namespace phase3.feature056.* absent
```

`implementationStatus: PENDING_DEV` is **still true** (SPEC-056 §9/§11 frontend work is absent) →
SPEC-056 itself is NOT edited by this slice.

## 1. The decision: Option 1 — retarget the route, keep a deterministic probe

**Item 1 (one sentence):** I choose **Option 1** — `sync()` becomes an honest, network-free probe
returning `count=0` and `trust_state="source_pending"` — because the measurement
`grep -rn 'connectors/voteinfo' frontend/ → exit 1` plus `grep -rn '\.sync()' src/ → exactly one
caller (the route itself)` shows the route has **zero data consumers**, while a working live path
(`VoteService.refresh_from_live()`, three routes) already serves real data, so Option 2 would
duplicate that path *and* force either an out-of-scope date parameter or the out-of-scope
`LATEST_VOTE_DATE` constant (the route accepts no body today), and Option 3 would delete an
endpoint that SPEC-056 §8 mandates (`docs/specs/SPEC-056-...md:48`: *"`POST
/api/v1/connectors/voteinfo/sync; GET /api/v1/votes/proposals"`*) and that measurably exists
(`src/main.py:766`).

Why the other two lose, in one line each:

- **Option 2** — `sync()` is a synchronous `def` (`bfs_voteinfo_client.py:110`); making it fetch
  means `async def` + a vote date the route does not accept (`main.py:766-768` takes no body) +
  a second live-data path beside `refresh_from_live()` which the brief forbids touching. It
  serves nobody (0.2: no consumer).
- **Option 3** — SPEC-056 §8 names the route as an API contract of the parent spec; deleting it
  would require re-authoring SPEC-056 (out of allowlist) and breaks `36 passed` on the three
  test files (0.6) for no consumer benefit.

The probe still satisfies SPEC-056 REQ-056-001 (*"típusos, determinisztikus sikeres választ"* —
a typed, deterministic success response) and REQ-056-006's idempotency half; what it stops doing
is claiming to carry official data it never fetched (REQ-056-005, SPEC-056b FR-03).

## 2. Target Files allowlist (developer may CREATE/EDIT only these)

| # | File | Change |
|---|---|---|
| 1 | `src/services/connectors/bfs_voteinfo_client.py` | Rewrite `VoteSync` defaults/type (line 35-40) and `sync()` (lines 110-125) per §3; remove the fabricated row |
| 2 | `tests/unit/test_spec046_055_060_contract.py` | Update the three tests at lines 105-121 to the assertions in §4 (T1-T3) |
| 3 | `tests/e2e/test_phase3_civic_api.py` | Update the test at lines 12-13 to the assertion in §4 (T4) |
| 4 | `docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md` | Append the exact status note under FR-01 (after line 74) and the exact correction under §3 (replacing lines 128-129), wording dictated in §5.1 |

**Explicitly NOT in the allowlist (and why):**

- `src/main.py` — the route body `return _voteinfo_connector.sync().model_dump()` (line 768)
  already forwards every `VoteSync` field, including the new `fetched_at`; zero edits needed.
- `tests/unit/test_phase3_civic_services.py` — the vacuous sha-length test (line 14) is
  explicitly out of scope (§8) and keeps passing untouched.
- `src/services/vote_service.py` and the three `/api/v1/politics/votes*` routes — the live data
  path, forbidden by the brief (0.4).
- `docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md` — `PENDING_DEV` remains true
  (0.8); no edit.
- `docs/specs/index.json`, `docs/specs/validate_specs.py` — `SPEC-056c-*.md` does NOT match the
  validator glob `SPEC-[0-9][0-9][0-9]-*.md` (`validate_specs.py:7`), same as `SPEC-056b-…`;
  measured baseline `PASS specs=60` (0.6) is preserved without index changes.
- `frontend/**` (canton colours are a separate queued item), `analysis/next-moves.md` and
  `.agent-pipeline/**` (currently dirty/untracked with orchestrator and reviewer files — see
  §9; never staged by the developer), `requirements.txt` / `pyproject.toml` (no new deps —
  only `typing.Literal`, stdlib).

## 3. Functional requirements (each numbered, individually testable)

- **FR-01 [MUST]:** `BfsVoteInfoClient.sync()` returns a `VoteSync` built from an **empty** row
  set. Mandated body (exact — do not redesign):

  ```python
  def sync(self) -> VoteSync:
      """Network-free probe for POST /api/v1/connectors/voteinfo/sync (SPEC-056c).

      Carries no vote rows and performs no I/O, so the response is a
      deterministic ``count=0`` with ``trust_state="source_pending"`` and
      ``fetched_at=None``. The live data path is
      ``VoteService.refresh_from_live()`` (SPEC-056b), not this method.
      """
      raw = json.dumps([], sort_keys=True).encode()
      return VoteSync(count=0, sha256=hashlib.sha256(raw).hexdigest())
  ```

  Check: `grep -c 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py` → `0`.

- **FR-02 [MUST]:** `VoteSync` (line 35-40) changes to exactly these field semantics:

  ```python
  class VoteSync(BaseModel):
      count: int
      sha256: str
      source: str = "BFS VoteInfo"
      trust_state: Literal["official_publication", "stale", "source_pending"] = "source_pending"
      fetched_at: str | None = None
      poll_interval_seconds: int = 60
  ```

  (add `from typing import Literal`). The type-level default moves OFF
  `official_publication`; no new vocabulary token is introduced. `source` keeps its value
  `"BFS VoteInfo"` — it names the connector's upstream, not a data claim; the no-data facts are
  carried by `count=0`, `trust_state="source_pending"`, `fetched_at=null` (§4 contract).

- **FR-03 [MUST]:** `sync()` performs **no I/O**: no socket, no `httpx` call, no URL building.
  The `awk '/def sync/,0'` body of the method contains zero matches for
  `httpx|urlopen|client\.get|requests\.` (AC-04). This is what makes the probe deterministic
  (SPEC-056 REQ-056-001) and makes the unreachable-host case trivially honest (§4.3).

- **FR-04 [MUST]:** `trust_state` selection rule for this path: **no fetch occurs ⇒
  `source_pending`**, always. `official_publication` requires a successful live parse
  (SPEC-056b FR-03); `stale` requires previously fetched data (none exists here). The probe
  therefore never returns either, and `official_publication` must be unreachable from
  `sync()` and from `POST /api/v1/connectors/voteinfo/sync` — enforced by the `Literal` type
  (FR-02) and by tests T2/T3/T4 (§4).

- **FR-05 [MUST]:** `sha256` = SHA-256 of the byte string `b"[]"` (the JSON of the empty row
  set, `json.dumps([], sort_keys=True)`), i.e. exactly
  `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
  (planner-measured: `.venv/bin/python -c "import hashlib,json; print(hashlib.sha256(json.dumps([], sort_keys=True).encode()).hexdigest())"`).
  Two calls return equal digests (idempotency, REQ-056-006). The old digest `8c154363…`
  disappears from `src/` — it only ever hashed the fabricated row; repo-wide
  `grep -rn '8c15436'` found it only inside `analysis/next-moves.md` and
  `.agent-pipeline/audit/reports/nw2-reviewer.md` (reports, not code, not edited here).

- **FR-06 [MUST]:** The `sync()` docstring no longer contains the "legacy probe / pinned by
  three pre-existing tests / open conflict" text (lines 112-123 today) — it is superseded by
  FR-01's docstring. Grep check: `grep -c 'open conflict' src/services/connectors/bfs_voteinfo_client.py` → `0`.

- **FR-07 [MUST]:** The four tests in §4 are updated to the exact assertions given there; no
  other test file is touched; **no test is added and no test is deleted** — the suite count
  stays `264 passed, 1 skipped`, and the three-file subset stays `36 passed`.

- **FR-08 [MUST]:** The two dictated status notes are added to SPEC-056b with the wording in
  §5.1 (documentation closure, CLAUDE.md §4b — a spec sentence that measurably contradicts the
  tree must be corrected in the same change that fixes the tree).

## 4. API contract — `POST /api/v1/connectors/voteinfo/sync`

### 4.1 Exact response (the only success shape)

Status: **200** always (see 4.3). Body:

```json
{
  "count": 0,
  "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
  "source": "BFS VoteInfo",
  "trust_state": "source_pending",
  "fetched_at": null,
  "poll_interval_seconds": 60
}
```

Field meanings: `count` = vote rows carried by **this** response (always 0 — it is a probe, not
a data feed); `sha256` = digest of the empty row set (FR-05); `source` = connector's upstream
identity; `trust_state` = `source_pending` per FR-04; `fetched_at` = `null` because this path
fetches nothing; `poll_interval_seconds` = 60, unchanged legacy metadata (its semantics are out
of scope, §8).

### 4.2 Request

No parameters, no body, no auth — unchanged from today (`main.py:766-768`). Any request body
sent is ignored. The route handler itself is **not edited** (§2).

### 4.3 Unreachable-host case

Because FR-03 forbids all I/O in `sync()`, the OGD host being down, timing out, or returning
500 is **observationally identical** to it being up: HTTP 200 + the byte-identical JSON of 4.1.
Consequences, all mandated:

- never HTTP 500 from host state (there is no call to fail),
- never a fabricated row,
- never `official_publication`/`official_measurement` (SPEC-056 REQ-056-004/005, SPEC-056b
  FR-04 — this slice satisfies them on this route by construction, not by error handling).

The real live path's unreachable-host behaviour (fixtures as `stale`, else `source_pending`,
HTTP 200) lives in `VoteService.refresh_from_live()` and is untouched here (0.4).

### 4.4 trust_state decision table (closed vocabulary, no new tokens)

| Situation on this route | `trust_state` | Why |
|---|---|---|
| Any call, any host state (no fetch ever runs) | `source_pending` | No official data obtained; `stale` needs a prior fetch, `official_publication` needs a successful parse |
| (Not reachable on this route) successful fetch | — | That state exists only on `/api/v1/politics/votes*` via `refresh_from_live()` |

## 5. Which existing tests change, and the two spec status notes

### 5.1 Spec status notes (allowlist item 4 — exact wording, no paraphrase)

**(a)** In `docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md`, immediately **after line 74**
(the FR-01 sentence *"No hardcoded rows remain on any code path."*), append:

```markdown
> **Status note (SPEC-056c, 2026-10-06):** this second sentence was FALSE from `adc0093` through
> `f5c27a2` — `BfsVoteInfoClient.sync()` kept a hardcoded row `{"id": 6670, "yes": 58.2}`
> labelled `trust_state="official_publication"` on `POST /api/v1/connectors/voteinfo/sync`
> (measured: `grep -n 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py` →
> line 123 pre-fix). Closed by SPEC-056c
> (`docs/specs/SPEC-056c-honest-sync-probe.md`): `sync()` is now a network-free probe with
> `count=0`, `fetched_at=null`, `trust_state="source_pending"`.
```

**(b)** Replace lines **128-129** (the §3 "UNCHANGED" claim *"`POST
/api/v1/connectors/voteinfo/sync` and `GET /api/v1/votes/proposals` named in SPEC-056 §8 do NOT
exist in this tree"*) with:

```markdown
- Correction (SPEC-056c, 2026-10-06): the claim that `POST /api/v1/connectors/voteinfo/sync` and
  `GET /api/v1/votes/proposals` "do NOT exist in this tree" was false — both exist
  (`src/main.py:766` and `src/main.py:669`; the latter is SPEC-051's surface,
  `tests/unit/test_spec051_voting_contract.py:1`). Neither was *introduced by SPEC-056b*, which
  is what this out-of-scope note meant.
```

SPEC-056's `implementationStatus: PENDING_DEV` (line 6) is **still true** (0.8) and is NOT
edited: `grep -rn 'feature056' frontend/` → no matches (SPEC-056 §11 i18n namespace absent), so
the frontend half of SPEC-056 remains unimplemented.

### 5.2 The three pinning tests + the e2e — which lines, which new assertion

The assertions marked **WRONG** pin a fabricated value as correct and are themselves defects
(CLAUDE.md §3d/§3i) — they are corrected, not preserved.

**T1 — `tests/unit/test_spec046_055_060_contract.py:105-108`**
`test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash`

```python
def test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash() -> None:
    a, b = BfsVoteInfoClient().sync(), BfsVoteInfoClient().sync()
    assert a.count == 0 and len(a.sha256) == 64          # was count == 1  [WRONG: fabricated row]
    assert a.sha256 == b.sha256                           # unchanged (idempotency, REQ-056-006)
```

**T2 — `tests/unit/test_spec046_055_060_contract.py:111-115`**
`test_spec_056_req_056_002_ac_056_001_sync_trust_metadata`

```python
def test_spec_056_req_056_002_ac_056_001_sync_trust_metadata() -> None:
    s = BfsVoteInfoClient().sync()
    assert s.source == "BFS VoteInfo"                     # unchanged
    assert s.trust_state == "source_pending"              # was "official_publication"  [WRONG: pins the LIE]
    assert s.fetched_at is None                           # new honesty assertion
    assert s.poll_interval_seconds == 60                  # unchanged
```

**T3 — `tests/unit/test_spec046_055_060_contract.py:118-121`**
`test_spec_056_req_056_001_ac_056_001_sync_api_contract`

```python
def test_spec_056_req_056_001_ac_056_001_sync_api_contract() -> None:
    body = c.post("/api/v1/connectors/voteinfo/sync").json()
    assert body["count"] == 0 and len(body["sha256"]) == 64   # was count == 1  [WRONG]
    assert body["trust_state"] == "source_pending"            # was "official_publication"  [WRONG]
    assert body["fetched_at"] is None                         # new
```

**T4 — `tests/e2e/test_phase3_civic_api.py:12-13`**
`test_spec_056_req_056_001_ac_056_001_vote_sync_api`

```python
def test_spec_056_req_056_001_ac_056_001_vote_sync_api() -> None:
    r = c.post("/api/v1/connectors/voteinfo/sync")
    assert r.status_code == 200                                # new (contract §4.1/4.3)
    assert r.json()["count"] == 0                              # was == 1  [WRONG]
    assert r.json()["trust_state"] == "source_pending"         # new
```

**NOT changed:** `tests/unit/test_phase3_civic_services.py:13-14`
(`assert len(BfsVoteInfoClient().sync().sha256) == 64`) — vacuous (it would pass on any
constant) but out of scope by the brief (§8); it keeps passing because `sha256` stays 64 hex
chars.

**No test is deleted.** Zero tests are added; zero are removed. Expected counts: full suite
`264 passed, 1 skipped` (unchanged from 0.6); the three touched files together
`36 passed` (unchanged from 0.6).

## 6. Acceptance criteria — runnable commands (all run by the planner pre-fix unless marked)

| # | Command (cwd `/home/zoltan/swiss_p_map`) | Pre-fix output (measured) | Post-fix pass = |
|---|---|---|---|
| AC-01 | `grep -c 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py` | `1` | `0` |
| AC-02 | `.venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient as C; s=C().sync(); assert s.trust_state=='source_pending' and s.count==0 and s.fetched_at is None, s.model_dump(); assert s.sha256=='4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', s.sha256; assert C().sync().model_dump()==C().sync().model_dump(), 'not deterministic'; print('OK', s.model_dump())"` | `AssertionError` (0.7) | prints `OK {'count': 0, … 'trust_state': 'source_pending', 'fetched_at': None …}` |
| AC-03 | `.venv/bin/python -c "from fastapi.testclient import TestClient; from src.main import app; r=TestClient(app).post('/api/v1/connectors/voteinfo/sync'); b=r.json(); assert r.status_code==200 and b['count']==0 and b['trust_state']=='source_pending' and b['fetched_at'] is None and b['source']=='BFS VoteInfo' and b['poll_interval_seconds']==60 and len(b['sha256'])==64, b; print('OK', b)"` | `pre-fix failure: AssertionError` with the 4.1 shape violated (0.7) | prints `OK {'count': 0, …}` |
| AC-04 | `awk '/def sync/,0' src/services/connectors/bfs_voteinfo_client.py \| grep -cE 'httpx\|urlopen\|client\.get\|requests\.'` | (pre-fix `sync()` also has 0 — this AC proves FR-03 post-fix, paired with AC-02's determinism) | `0` |
| AC-05 | `grep -c 'open conflict' src/services/connectors/bfs_voteinfo_client.py` | `1` (docstring line 122-123 region: *"the conflict is tracked by the reviewer gate"*) | `0` |
| AC-06 | `grep -c 'SPEC-056c' docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md` | `0` (measured) | `≥ 2` (both notes of §5.1) |
| AC-07 | `.venv/bin/python -m pytest -q \| tail -1` | `264 passed, 1 skipped, 52 warnings in 13.52s` | same `264 passed, 1 skipped` (count reported: 0 tests added/removed, FR-07) |
| AC-08 | `.venv/bin/python -m pytest tests/unit/test_spec046_055_060_contract.py tests/e2e/test_phase3_civic_api.py tests/unit/test_phase3_civic_services.py -q \| tail -1` | `36 passed, 1 warning in 5.63s` | `36 passed` |
| AC-09 | `.venv/bin/mypy src/ \| tail -1` | `Success: no issues found in 50 source files` | unchanged |
| AC-10 | `.venv/bin/ruff check src/ \| tail -1` | `All checks passed!` | unchanged |
| AC-11 | `.venv/bin/python docs/specs/validate_specs.py` | `PASS specs=60 requirements=324 acceptance=264 coverage=100%` | unchanged (SPEC-056c file name outside the validator glob — see §2) |
| AC-12 | `.venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import VoteSync; v=VoteSync(count=0, sha256='x'); print(v.trust_state, v.fetched_at)"` | (post-fix constructible; pre-fix the model has no `fetched_at` field → `TypeError`/`ValidationError` when passed — not run pre-fix, **not attempted** for the failure branch) | `source_pending None` |

**Marked not run by the planner:** every AC was executed pre-fix by the planner EXCEPT the
post-fix pass column (no code was written — planner is read-only) and AC-12's pre-fix failure
branch. Post-fix execution belongs to the developer + reviewer gates.

## 7. NEGATIVE acceptance — which test fails pre-fix and why

A gate that only runs green on the post-fix tree proves nothing. Two independent pre-fix
failures, both **measured by the planner** (0.7):

1. **Behavioural (code, not tests):**
   `.venv/bin/python -c "…assert s.trust_state == 'source_pending' and s.count == 0…"` on the
   pre-fix tree → observed `trust_state = 'official_publication' count = 1` then
   **`AssertionError`**. Post-fix it prints `OK`. This fails pre-fix because `sync()`
   unconditionally returns the fabricated `count=1` labelled `official_publication`.
2. **Route-level (the e2e contract):** the same assertion against
   `TestClient(app).post('/api/v1/connectors/voteinfo/sync')` on the pre-fix tree →
   **`AssertionError`** with body `{'count': 1, … 'trust_state': 'official_publication', …}`
   (no `fetched_at` key at all pre-fix, so `b['fetched_at']` raises **`KeyError`** in AC-03's
   full form — measured as `AssertionError` in the planner's shortened probe; the KeyError
   branch is *not attempted*). So **T4** (`test_spec_056_req_056_001_ac_056_001_vote_sync_api`)
   as rewritten in §5.2 fails on the pre-fix tree at `count == 0`, and **T2** fails at
   `trust_state == "source_pending"` — these are the named tests that fail pre-fix *because*
   the pre-fix code fabricates the row and claims official status.
3. **Structural:** `grep -c 'rows = \[{"id"' …` pre-fix `1` → post-fix `0` (AC-01). A tree where
   only the tests were changed but the constant remained cannot reach `0`.

## 8. STOP command (item 7)

```sh
cd /home/zoltan/swiss_p_map && \
grep -c 'rows = \[{"id"' src/services/connectors/bfs_voteinfo_client.py && \
.venv/bin/python -c "from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient as C; s=C().sync(); assert s.trust_state=='source_pending' and s.count==0 and s.fetched_at is None, s.model_dump(); assert s.sha256=='4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', s.sha256; print('PROBE OK', s.model_dump())" && \
.venv/bin/python -m pytest -q 2>&1 | tail -1 && \
.venv/bin/mypy src/ 2>&1 | tail -1 && \
.venv/bin/ruff check src/ 2>&1 | tail -1 && \
.venv/bin/python docs/specs/validate_specs.py
```

**Done =** the six outputs are, in order:

```
0
PROBE OK {'count': 0, 'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', 'source': 'BFS VoteInfo', 'trust_state': 'source_pending', 'fetched_at': None, 'poll_interval_seconds': 60}
264 passed, 1 skipped, …
Success: no issues found in 50 source files
All checks passed!
PASS specs=60 requirements=324 acceptance=264 coverage=100%
```

(any warnings-count suffix on the pytest line is acceptable; `264 passed, 1 skipped` is not).
**Not done if** the first number is `1`, the probe line raises, or any count/gate differs.

## 9. Risks and honest limits

| # | Risk / limit | Required handling in this slice | Could not determine |
|---|---|---|---|
| R-1 | Some consumer outside this repo depends on `count==1`/`official_publication` | In-repo consumers are only the tests (0.2, exhaustive grep of `src/ tests/ frontend/ analysis/ .agent-pipeline/`); old digest pinned nowhere in code (`grep -rn '8c15436'` → reports only) | **Could not determine:** anything outside this repository (no external runbooks/monitoring searchable from here). Reported, not guessed |
| R-2 | A reviewer may have preferred Option 2 ("make it really sync") | Option chosen with the §1 measurements; the route path and SPEC-056 §8 name are preserved, so Option 2 remains a possible *future* slice without rework of this one | **Could not determine:** the nw2 reviewer report identifies the defect but prescribes no option (`grep -i 'option\|recommend'` on `.agent-pipeline/audit/reports/nw2-reviewer.md` matched only unrelated lines) |
| R-3 | `Literal[...]` narrowing on `VoteSync.trust_state` surprises a later caller | Only `sync()` constructs `VoteSync` (grep: `bfs_voteinfo_client.py:125` is the sole constructor); dict output unchanged in shape | — |
| R-4 | Spec brief asked only about FR-01's note; §5.1(b) also corrects SPEC-056b:128-129 | Brief gap **reported**: the second false sentence was found by planner measurement (0.8) and is corrected with dictated wording; if the orchestrator wants it out, drop allowlist item 4(b) — nothing else depends on it | **Could not determine:** whether SPEC-056b:211-212's softer §8 phrasing ("New endpoints … not introduced here") is also to be corrected — left as-is (true about *authorship*, misleading about *existence*) |
| R-5 | "The two vacuous sha-length tests" (brief item 9) | `grep -rn 'len(.*sha256' tests/` → **3 hits** (`test_spec046_055_060_contract.py:107`, `:120`, `test_phase3_civic_services.py:14`). Interpretation used: `test_phase3_civic_services.py:14` is untouched; the `len(…)==64` *sub-assertions* inside T1/T3 are kept verbatim (only their `count`/`trust_state` partners change) | **Could not determine:** which exact two the brief meant; both readings are satisfied by the above |
| R-6 | Post-fix tree has never been run (planner writes specs, not code) | Every post-fix number above is a prediction from measured pre-fix values; the developer/reviewer must run §8's STOP command | Post-fix outputs: **not attempted** by construction |
| R-7 | Tree is dirty at planning time: `analysis/next-moves.md` (M), `.agent-pipeline/audit/reports/nw2-explore.md` (??), `.agent-pipeline/audit/reports/nw2-reviewer.md` (??) — measured via `git status --short` | None of them are mine; the developer must stage **only** allowlist paths and name anything else dirty in its report (CLAUDE.md §3e) | — |

## 10. Research grounding (citations, not paraphrase)

- **Brief (primary, this dispatch):** `dispatch/nw2-brief-planner.md`, sha256:`ea083bcda27f`
  (= `$CLAUDE_BRIEF_SHA`, verified). Its orchestrator-measured block (the `rows = [{"id"` grep,
  the `sync().model_dump()` output, the one-caller grep, the three pinning tests, the
  `frontend/` no-consumer grep) was **re-run by the planner** — all outputs pasted in §0; the
  brief's facts and my measurements agree line for line.
- **Researcher brief `nw2-explore.md` (brief_sha `3199fda5832d`, 2026-10-06)** carries no primary
  snippet for this item's key FC (it argues the Map3D wiring item instead). Its only relevant
  sentence, verbatim: *"Competing candidate: `BfsVoteInfoClient.sync()` literal
  (`bfs_voteinfo_client.py:123`) and the two vacuous sha-length asserts remain; they are lower
  value (pinned legacy probe, cosmetic) but a reviewer could argue cleanup-first."* → per the
  handoff rule this SPEC is marked **`no-live-validation`** for every claim about the live OGD
  host; none is load-bearing, because FR-03 forbids I/O on this path entirely (§4.3).
- **Repo research (context only):** `docs/research/2026-08-27-bfs-vote-data.md:13`, quoted inside
  SPEC-056b §0: *"A svájci állam hivatalos nyílt adatforrása a **VoteInfo OGD
  webszolgáltatás** (`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`)"*
  (dated 2026-08-27) — establishes the real host exists; untouched by this slice.
- **Repo research (primary snippet for the defect):**
  `docs/research/2026-10-04-events-elections-data-sources.md:16,321` (dated 2026-10-04) records
  the stub verbatim: *"`rows = [{"id": 6670, "yes": 58.2}]` … no HTTP call"* and classifies it
  *"repo-local"*. This slice closes that row's defect class on the `sync()` path; the research
  file itself is not edited (out of allowlist).
- **Parent specs:** SPEC-056 REQ-056-001/004/005/006 + §6 ("nyers 500 részlet tiltott") +
  §7 ("Literal status") + §8 (route named); SPEC-056b FR-01 (line 74), FR-03/FR-04, §3 closed
  vocabulary (line 106).

## 11. Out of scope (explicitly NOT this slice) — item 9

1. **Frontend canton colours** (`frontend/src/app/Map3D.tsx`, `swissCantons.ts` — the queued
   explore item); all of `frontend/**`.
2. **Gemeente/municipality-level geometry or serving** (161 gemeenden stay unexposed).
3. **Vote-date auto-discovery** — `LATEST_VOTE_DATE` / `TODO(SPEC-056b-R3)` in
   `vote_service.py` stays as-is; this slice's probe takes no date at all.
4. **Caching / TTL / `poll_interval_seconds` semantics** — the value 60 is kept verbatim, not
   re-derived, not enforced.
5. **The vacuous sha-length tests** — `tests/unit/test_phase3_civic_services.py:13-14`
   untouched, and the `len(…)==64` sub-assertions inside T1/T3 kept (see R-5).
6. **The live data path**: `VoteService.refresh_from_live`, `parse_voteinfo_payload`, and the
   three `/api/v1/politics/votes*` routes — untouched.
7. **`GET /api/v1/votes/proposals`** (SPEC-051's surface) — untouched.
8. **SPEC-056 text/status** (`PENDING_DEV` remains true), `docs/specs/index.json`,
   `validate_specs.py`.
9. **Route rename/removal**, auth on the route, SPEC-056 REQ-056-004 notification dedup, §9/§11
   frontend + i18n (`phase3.feature056.*`), WCAG work — later slices.

---
*Planner artifact, 2026-10-06. Zero production code written. Mirrored to
`/home/zoltan/.hermes/cache/scratch/dispatch/nw2-spec.md`. Not committed — the brief instructs
"Do NOT commit"; the orchestrator commits after verifying (global rule's commit duty is dropped
here by explicit brief instruction and this note records the drop).*
