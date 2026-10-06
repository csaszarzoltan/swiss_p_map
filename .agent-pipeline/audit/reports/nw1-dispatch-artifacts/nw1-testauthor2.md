dispatch:  test-author nw1-testauthor2 (role brief inline, no brief file)
agent:     test-author
repo:      /home/zoltan/swiss_p_map @ 2904f21
brief:     sha256:n/a - no brief file was supplied (role+task arrived inline in the dispatch prompt)
verdict:   none - first pass
status:    DONE — new live-only contract encoded, regression assertion added and proven able to fail, full suite green, nothing under src/ touched

Slice claimed: tests/unit/test_vote_service.py, tests/unit/test_spec056b_live_wiring.py.

1. git diff --stat for the test files changed, plus the diff hunks.

```
$ git diff --stat
 tests/unit/test_spec056b_live_wiring.py |  47 +++++++++++++
 tests/unit/test_vote_service.py         | 118 +++++++++++++++++++++++++++-----
 2 files changed, 146 insertions(+), 19 deletions(-)
```

test_vote_service.py — rewrote `test_vote_proposals_list_and_detail` to the new
contract (status 200; `items` list non-empty; envelope source/fetched_at/trust_state
on list AND detail; detail `national_yes_percent` reachable for the first
LIVE-served id; 404 unchanged) + extracted the fixture-id assertions into a new
failure-path test `test_vote_list_failure_path_serves_fixtures_as_stale`
(MockTransport 500 → ok False, trust_state stale, all four fixture ids served,
BVG fixture content 32.9 / ZH 34.8 pinned there). Added VERITAS markers
TEST-VOTE-001..005 (extra @pytest.mark.asyncio placed FIRST, above the three
required markers, per the measured gate trap).

test_spec056b_live_wiring.py — appended TEST-SPEC056B-012 regression:
success via MockTransport + recorded fixture ⇒ served set ⊆ {6880}, no fixture
id in list_proposals, get_proposal_by_id(fid) is None under official_publication.

2. Post-fix output.

```
$ .venv/bin/python -m pytest tests/unit/test_vote_service.py -q
5 passed in 2.04s            (4 pre-existing incl. rewritten + 1 new failure-path)
$ .venv/bin/python -m pytest tests/unit/test_vote_service.py tests/unit/test_spec056b_live_wiring.py -q
18 passed in 2.65s
$ .venv/bin/python -m pytest -q
264 passed, 1 skipped in 7.94s
```

3. mypy / ruff.

```
$ .venv/bin/python -m mypy src/
Success: no issues found in 50 source files
$ .venv/bin/python -m ruff check src/
All checks passed!
```

4. Regression assertion + proof it fails against pre-fix behaviour.

The assertion (TEST-SPEC056B-012 body):
```python
served_ids = [p["proposal_id"] for p in svc.list_proposals()]
assert set(served_ids) <= set(LIVE_IDS)          # LIVE_IDS = [6880]
for fid in FIXTURE_IDS:                           # [6670, 6680, 6690, 6700]
    assert fid not in served_ids
    assert svc.get_proposal_by_id(fid) is None
```
Proof: copied src/services/vote_service.py to /tmp/old_vote_service.py and
restored the pre-fix merge lines in the COPY only
(`self._proposals[parsed.proposal_id] = parsed`; `_served_proposals → return
self._proposals`). Real file untouched. Ran the assertion body against it:
```
ok = True | trust_state = official_publication | served = [6880, 6690, 6680, 6700, 6670]
EXPECTED FAILURE — regression assertion fails against pre-fix merge
```
The old code serves FIVE ids under official_publication — exactly the blocking
defect. The assertion catches it.

5. Assertions removed or changed, with justification.

- `assert len(items) >= 4` → `assert len(items) >= 1` non-empty. The 4 came
  from this repo's own fixture constants; the live 20260927 publication
  genuinely carries ONE proposal (measured live: 1 item, id 6880). Asserting 4
  on the success path pins the fixture count, not honesty. NOT a weakening:
  the count is replaced by the strictly stronger live-only exclusion below.
- `assert 6670/6680/6690/6700 in ids` on the SUCCESS path → REMOVED there and
  moved to the failure-path test (`test_vote_list_failure_path_serves_fixtures_as_stale`)
  plus pre-existing TEST-SPEC056B-004/005/008. Fixture ids are honest only
  under stale; asserting them under official_publication is the defect itself.
- BVG content asserts (`national_yes_percent == 32.9`, `ZH yes_percent == 34.8`)
  moved from the success-path detail lookup to the failure-path fixture lookup
  (same values, same object, honest label). The success detail now asserts
  `national_yes_percent` reachable on the first live-served id (id-agnostic —
  it does not hard-code 6880, so a second live proposal 6890 would not break it).
- No test deleted. Nothing else removed.

6. Did you edit anything under src/? NO. `git diff --stat` shows only the two
test files. No product line touched.

7. What could still make the suite green while the served set is dishonest?

- The HTTP-level tests (incl. the rewritten list/detail test) hit the real
  `src.main._vote` singleton, whose `refresh_from_live()` performs a REAL
  network fetch. If the live host is unreachable in CI, the app degrades to
  stale-with-fixtures and the `if trust_state == "official_publication"`
  regression branch is SKIPPED — green without ever exercising the live-only
  set. The MockTransport regression test (TEST-SPEC056B-012) closes this at
  service level, but nothing at HTTP level forces `trust_state ==
  official_publication` without network. A dependency-injection hook (or a
  route-level override of `_vote._client`) would let the HTTP test pin the
  live-only set deterministically.
- `set(served) <= {6880}` pins the recorded single-proposal shape. If OGD
  later publishes a second proposal (6890 exists live but is NOT in the
  trimmed fixture), the service would honestly serve {6880, 6890} and this
  assertion would fail closed — a maintenance trip, not a dishonesty hole,
  but it should be revisited when the fixture is re-recorded.
- Live ZH municipality trimming is pinned only in the fixture-shape test
  (161 municipalities); a future re-trim could silently drop cantons down to
  (but not below) the 26-canton parse gate without failing.
