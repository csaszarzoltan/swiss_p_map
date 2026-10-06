dispatch:  inline reviewer brief (gate review of SPEC-056b live VoteInfo OGD wiring, 3 commits)
agent:     reviewer
repo:      /home/zoltan/swiss_p_map @ aebfafe
brief:     sha256:not attempted - no brief file path was supplied, the task arrived inline
verdict:   v20261004163958-cc7419 | REQUEST-CHANGES | from=reviewer | commit=adc0093 (prior round; the two nw1 findings it raised - the 23-line VoteInfo stub and the "no API" negative - are the ones THIS change closes, and I re-verified both closed)
status:    DONE - all 6 items answered; one reproducible FR-02/FR-03 honesty defect blocks

# Gate review - SPEC-056b live VoteInfo OGD wiring (33aab13, 3d21fe5, aebfafe)

`git log --oneline -1` I actually saw:

```
aebfafe016794e0eafe5d0952dfef0d9231a4e69 test(votes): gate the live VoteInfo OGD wiring (SPEC-056b)
```

Commands I ran and their real output (venv at `/home/zoltan/swiss_p_map/.venv`):

```
$ .venv/bin/pytest tests/unit/test_spec056b_live_wiring.py -q
12 passed, 34 warnings in 2.57s
$ .venv/bin/pytest -q
262 passed, 1 skipped, 34 warnings in 8.89s
$ .venv/bin/python -m mypy src/
Success: no issues found in 50 source files
$ .venv/bin/python -m ruff check src/
All checks passed!
```

## THE BLOCKING DEFECT (measured, reproducible)

On a successful live refresh the code **merges** the live proposal into the fixture store
instead of **replacing** it, and then labels the whole response `official_publication` /
`source="BFS VoteInfo OGD"` / `fetched_at=<now>`.

`src/services/vote_service.py:408-412` (verified by `grep -n`):

```
408:        self._proposals[parsed.proposal_id] = parsed
409:        self._source = "BFS VoteInfo OGD"
412:        self._trust_state = "official_publication"
```

Line 408 is an insert keyed by the new id. Nothing clears the fixture ids. Measured with the
committed fixture through the real service path:

```
$ .venv/bin/python -c "...MockTransport returning the committed 141900-byte OGD fixture..."
ok True trust official_publication source BFS VoteInfo OGD
served ids: [6880, 6690, 6680, 6700, 6670]
```

So four hardcoded 2024 fixtures (6670/6680/6690/6700 - values that exist nowhere in the BFS
publication; they are `_all_default_proposals()` constants) are served **under the official
trust label and a fresh timestamp**. A consumer of `/votes/list` cannot tell 6670 (a constant
in this repo) from 6880 (a real federal result).

This contradicts three things in the repo's own text:

- SPEC-056b FR-02 [MUST]: *"replaces the served proposals with the live result"*.
- SPEC-056b §0b.4: *"Fixtures stay as fallback seed data; they must never be presented as live."*
- SPEC-056b FR-03: the trust vocabulary is per-response, so one response cannot honestly be both.

Note this defect is **already visible in the orchestrator's own measured fact** and was not
flagged: `GET /api/v1/politics/votes/list -> items 5 at top level`. Five items = 1 live + 4
fixtures, all inside the `official_publication` envelope. "Items 5" was read as success; it is
the symptom.

The gate does not catch it. The negative test asserts the fixtures are not labelled live
**on failure** (`test_negative_fixture_ids_never_labelled_live`, line 246), and
`FIXTURE_IDS` is used only at lines 181 and 201 - both inside the failure-path tests. **No
test asserts the fixtures are gone on success.** `grep -n FIXTURE_IDS` -> `[38, 181, 201]`.

## The five scores

| # | Dimension | Score | Evidence |
|---|---|---|---|
| 1 | Target choice | 3 | Right target, half-built. `grep -rn parse_voteinfo_payload src/ tests/` pre-fix = 1 hit (the `def` only, zero callers), post-fix = 4. Choosing the live OGD host over the frontend canton colours or the sync stub was correct and beats both alternatives. But FR-02 required *replace* and the code merges, so the honesty goal the slice exists for is only half-delivered. |
| 2 | Verification | 3 | 12 new tests, green; **gate is genuinely load-bearing** (I reproduced the pre-fix failure independently - see below). But the suite is blind to the one defect that matters, and the 2 pre-fix passers are correct invariants, not gaps. |
| 3 | Scope discipline | 5 | Exactly the allowlist. Dev commit touches 3 of the 4 allowlisted files; `src/models/vote.py` correctly untouched (`git diff 33aab13~1..aebfafe --name-only | grep -c src/models/vote.py` -> 0). No frontend, no dep manifest, no SPEC-056 edit. |
| 4 | Process honesty | 3 | Every identifier in every commit message greps true (below). The research doc's refutation is correct and properly sourced. But `vote_service.py:6` says *"the served proposals are replaced"* - false against line 408 - and `bfs_voteinfo_client.py:120` cites an implementation report that does not exist. |
| 5 | Evidence survival | 3 | Fixture committed and will still verify in a month (`git cat-file -s aebfafe:tests/unit/fixtures/voteinfo_ogd_20260927_trimmed.json` -> 141900). Spec, gate test, research doc all committed. But no implementation report exists anywhere, one file cites a missing one, and SPEC-056b still reads `Status: SPEC_READY / PENDING_DEV`. |

**Weighted/plain average: (3+3+5+3+3)/5 = 3.4/5.**

### Score 2 detail - I did not take the gate claim on trust

The brief reported "10 of 12 fail pre-fix". I rebuilt the pre-fix tree from `git archive
33aab13~1` into `/tmp/pre056b` (repo untouched), copied in the gate test + fixture, and
neutralised the post-fix-only import **by a different mechanism than the orchestrator used**
(defined `OGD_HOST`/`OGD_URL_TEMPLATE` inline in the copied test instead of patching the import):

```
$ cd /tmp/pre056b && .venv/bin/pytest tests/unit/test_spec056b_live_wiring.py -v
... 10 failed, 2 passed
```

Independently reproduced. The two pre-fix passers, named:
- `test_fixture_is_real_recorded_shape_not_invention` - reads only the fixture JSON (which I
  copied in). It asserts the *recorded data* is real, not the code. Correctly invariant.
- `test_contract_unknown_proposal_404` - 404 for unknown id predates this change. A
  regression guard, which is exactly what it should be.

**This does not weaken the gate.** A gate whose 10 load-bearing tests fail pre-fix is sound;
the 2 passers assert invariants that are supposed to hold on both trees.

### Score 4 detail - identifiers named in commits, all verified present

```
$ grep -rn parse_voteinfo_payload src/ tests/     -> 4 hits (was 1)
$ grep -rn refresh_from_live src/ tests/          -> 13 hits
$ grep -n "OGD_HOST|OGD_URL_TEMPLATE|VoteInfoFetchError" src/  -> defined at :24,:25,:43
$ grep -n "6880" tests/unit/test_spec056b_live_wiring.py -> LIVE_IDS = [6880], the value the
  commit message claims the live path returned
```

Commit message arithmetic also checks out: 33aab13 claims `pytest 250 passed / 1 skipped`
(the pre-change baseline), aebfafe claims `262 passed / 1 skipped` (what I measured).

The research-doc correction (3d21fe5) is honest and I verified its citation:
`docs/research/2026-08-27-bfs-vote-data.md:13` does contain the OGD URL template it claims.
The refuted negative is struck through with the corrective measurement and its date, in both
places (table row 50 and section 3(a) line 191). **No surviving false VoteInfo claim** - the
one remaining "no API" at line 300 is about `www.alert.swiss/faq`, a different source, and is
correct.

## Item 2 - `BfsVoteInfoClient.sync()` still returning `6670/58.2`

**Yes, confirmed.** `src/services/connectors/bfs_voteinfo_client.py:122`:
`rows = [{"id": 6670, "yes": 58.2}]`.

**It is a defect that should block, not an acceptable deferral.** SPEC-056b FR-01 [MUST] says
*"No hardcoded rows remain on any code path"*, and allowlist item 1 says *"Replace stub `sync()`"*.
The developer kept it and documented why in the docstring - the stated blocker is three
pre-existing tests pinning it. But that reasoning inverts the dependency: the three tests are
vacuous (item 4), so they are not a constraint to respect, they are the thing to delete. The
docstring calls the result "an open conflict" and points at an implementation report that
does not exist, so the conflict is recorded nowhere a reader will find it.

## Item 3 - does the honest-failure path avoid fabricating data?

**Yes, on the failure path.** Quoting `src/services/vote_service.py:385-398`:

```
        except (VoteInfoFetchError, httpx.HTTPError) as exc:
            logger.warning("VoteInfo OGD fetch failed for %s: %s", use_date, exc)
            self._trust_state = "stale" if self._proposals else "source_pending"
            return False
        except Exception as exc:  # noqa: BLE001 - defensive guard ...
            logger.error("VoteInfo OGD parse crashed for %s: %s", use_date, exc)
            self._trust_state = "stale" if self._proposals else "source_pending"
            return False
```

plus the partial-parse guard at 399-406 (`parsed is None or parsed.proposal_id <= 0 or
len(parsed.cantons) != 26`). On any failure the caller keeps the fixture set labelled
`stale` + `embedded-fixture`, or `source_pending` on an empty store; `_source` is never set
to the live label off a failure. No fabrication, no raw 500, no traceback. That path is
correct and I could not break it.

**The failure path is honest; the success path is not** (see the blocking defect above).

## Item 4 - the two known-vacuous tests: measured, not guessed

```
$ .venv/bin/pytest tests/unit/test_spec046_055_060_contract.py tests/unit/test_phase3_civic_services.py -q
30 passed, 1 warning in 1.09s
```

- `tests/unit/test_spec046_055_060_contract.py:106` `test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash`
  - `a, b = BfsVoteInfoClient().sync(), BfsVoteInfoClient().sync(); assert a.count == 1 and len(a.sha256) == 64; assert a.sha256 == b.sha256`
  - **Still vacuous, and still load-bearing in the harmful sense.** It hashes a hardcoded
    constant and asserts its own length. `a.sha256 == b.sha256` compares two literals. It
    pins the `6670/58.2` stub in place, which is precisely why FR-01 was not met. Not
    superseded.
- `tests/unit/test_phase3_civic_services.py:13` `test_spec_056_req_056_001_ac_056_001_voteinfo_hash`
  - `assert len(BfsVoteInfoClient().sync().sha256) == 64`
  - **Still vacuous, still load-bearing.** The textbook case from CLAUDE.md: asserting the
    length of a hex digest the code just computed from a constant.
- Neither is superseded. And the neighbour at
  `test_spec046_055_060_contract.py:114` asserts
  `s.trust_state == "official_publication"` **on that fabricated constant** - a test that pins
  a lie, and one that contradicts the new honest-envelope vocabulary.

## Item 5 - concrete gaps a next iteration must close

1. **FR-02 replace-vs-merge** (`vote_service.py:408`) - the blocking defect.
2. **FR-01 stub survives** (`bfs_voteinfo_client.py:122`) plus the three tests that pin it;
   `POST /api/v1/connectors/voteinfo/sync` still serves a fabricated `count: 1`.
3. **No caching**: `src/main.py:359,375,389` call `await _vote.refresh_from_live()` on
   **every** request. No TTL, no memo. Each hit re-downloads a ~2 MB document and can block
   for the full 10 s budget - three concurrent votes requests, three downloads. Not required
   by the spec, so not a violation, but it is a production hazard the next slice should not
   inherit.
4. **`LATEST_VOTE_DATE = "20260927"`** (`vote_service.py:39`) is a hardcoded date, so this
   serves 2026-09-27 forever and will never advance to the next vote Sunday without a code
   change. It carries a `TODO(SPEC-056b-R3)` and the spec anticipated it, but it should be
   the top item next.
5. **Dangling citation** `bfs_voteinfo_client.py:120` -> "the SPEC-056b implementation report",
   which does not exist in the repo or under `.agent-pipeline/audit/reports/`.
   `ls .agent-pipeline/audit/reports/` -> `nw1-explore.md`, `nw1-reviewer.md` only. A reader
   follows that pointer and finds nothing.
6. **Stale status fields**: SPEC-056b still says `Status: SPEC_READY / PENDING_DEV` and
   SPEC-056 still says `implementationStatus: PENDING_DEV`, both now false.

Also for the orchestrator, not the developer: `analysis/next-moves.md` is **dirty and
uncommitted** (103 insertions). It is not part of these three commits, so it swept nothing -
   but per CLAUDE.md 3e, commit or stash it before the next dispatch.

## Item 6 - spec items the implementation did NOT do

- **FR-01 "No hardcoded rows remain on any code path"** - VIOLATED. `sync()` returns
  `6670/58.2` at `bfs_voteinfo_client.py:122`.
- **FR-02 "replaces the served proposals with the live result"** - VIOLATED. Merges instead
  (`vote_service.py:408`); measured served ids `[6880, 6690, 6680, 6700, 6670]`.
- **§0b.4 "Fixtures ... must never be presented as live"** - VIOLATED on the success path.
- Everything else in the spec was done: FR-03 (envelope keys, verified live), FR-04 (no
  fabrication, no 500 on failure), FR-05 (`MockTransport`-injectable, confirmed by the
  12-test gate), FR-06 (frontend/SPEC-056/manifests untouched, parser call sites 1 -> 4),
  FR-07 (10 s budget, `OGD_TIMEOUT_SECONDS = 10.0`), and the `src/models/vote.py` allowlist
  item was correctly declined as unnecessary.
- AC-04 asked for the three routes at lines 341-357; they moved to 350-393. Present and
  correct - not a violation.

## Where this report lives

Written to both required paths:
- `/home/zoltan/.hermes/cache/scratch/dispatch/nw1-gate.md` (queue copy)
- `/home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-gate.md` (durable, inside the repo)

**I did not commit it, deliberately.** The reviewer role is read-only and hands the verdict
back for the orchestrator to record via `claude-verdict` and commit after the gate. The durable
copy will therefore not survive until the orchestrator commits that path - that is the one
thing I am asking for here.

Score table and verdict are above. Every number in this report came from a command shown
above; the pre-fix gate run happened in `/tmp/pre056b`, a throwaway copy, and the repo was
never modified.

VERDICT: REQUEST-CHANGES 3.4
