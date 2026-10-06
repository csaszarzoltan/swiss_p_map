dispatch:  brief-inline (explore: highest-value NEXT change)
agent:     explore
repo:      /home/zoltan/swiss_p_map @ adc0093
brief:     sha256:not attempted - no brief file supplied, task arrived inline
verdict:   v20261004163958-cc7419 | REQUEST-CHANGES | commit=adc0093 (prior nw1-reviewer findings (a) 23-line BFS VoteInfo stub, (b) hardcoded map vote data taken as given, re-verified below)
status:    DONE - all 7 items answered with live command output

# Highest-value NEXT change: wire the VoteInfo OGD fetch (the parser exists, nobody calls it)

## 1. The single highest-value next change

**Wire `BfsVoteInfoClient.sync()` / `VoteService` to actually fetch the live VoteInfo OGD host
`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json` and serve it
through the existing `/api/v1/politics/votes/*` endpoints, replacing the 2024 hardcoded fixtures.**

Why this one and not the alternatives:
- The parser (`VoteService.parse_voteinfo_payload`, `src/services/vote_service.py:311`) already
  understands the live payload (verified item 2, command D) — the only missing piece is the fetch.
- The sync boundary (`BfsVoteInfoClient.sync()`, `src/services/connectors/bfs_voteinfo_client.py:12-16`)
  is a 5-line stub that never opens a socket, and its tests are vacuous (assert hash length of a
  constant) — the highest green-suite-over-mocked-boundary risk in the repo per CLAUDE 3d.
- The user-facing symptom is stale data: every vote since 2024-11-24 is ignored while the frontend
  presents 2024 fixtures as results (IDs 6670/6680/6690/6700, `vote_service.py:223-272`).
- Competing stubs exist (politics ZH-pilot STUB, OEREB source_pending, weather fallbacks) but those
  have live paths with fallback semantics; the vote path has NO live path at all — `parse_voteinfo_payload`
  has zero callers repo-wide.

## 2. File:line evidence the problem exists TODAY (commands + real output)

Command A — the sync boundary never touches the network:
```
$ cat src/services/connectors/bfs_voteinfo_client.py
"""BFS VoteInfo synchronization boundary (SPEC-056)."""
...
class BfsVoteInfoClient:
    def sync(self) -> VoteSync:
        rows = [{"id": 6670, "yes": 58.2}]
        raw = json.dumps(rows, sort_keys=True).encode()
        return VoteSync(count=len(rows), sha256=hashlib.sha256(raw).hexdigest())
```
(`src/services/connectors/bfs_voteinfo_client.py:12-16`; no import of httpx/urllib anywhere in the file.)

Command B — the parser exists but has zero callers in src/ and tests/:
```
$ grep -rn "parse_voteinfo_payload(" src/ tests/ --include="*.py" | grep -v "def parse_voteinfo"
(no output)
$ grep -rn "get_latest_vote(" src/ --include="*.py" | grep -v "def get_latest"
src/main.py:344:    return _vote.get_latest_vote().model_dump()
```
`get_latest_vote()` (`src/services/vote_service.py:287-289`) returns `self._proposals[6670]` —
a hardcoded 2024 fixture (`_all_default_proposals`, `vote_service.py:223`), served at
`GET /api/v1/politics/votes/latest` (`src/main.py:341-344`).

Command C — the host the code never calls is live (run 2026-10-05):
```
$ curl -s -o /dev/null -w "HTTP %{http_code} size=%{size_download} time=%{time_total}s\n" --max-time 25 \
  "https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20240922-eidgAbstimmung.json"
HTTP 200 size=1977268 time=0.244913s
```
Plus date sweep (same run): 20241124 HTTP 200 (3.9 MB), 20250928 HTTP 200, 20251130 HTTP 200,
20260308 HTTP 200 (6.1 MB), 20260927 HTTP 200 (2.0 MB); 20250302 HTTP 403 (no federal vote that day —
expected, not an outage).

Command D — the repo's own parser already handles the live payload (run 2026-10-05):
```
$ PYTHONPATH=. .venv/bin/python -c "...urllib fetch live 20240922... VoteService().parse_voteinfo_payload(d)..."
parsed: 6710 | cantons: 26 | national_yes: 36.96
```
Payload shape: top keys `['abstimmtag', 'timestamp', 'spatial_reference', 'schweiz']`,
`schweiz.vorlagen[0].kantone` = 26, `kantone[0].gemeinden` = 161 with per-Gemeinde
`resultat.jaStimmenInProzent` — municipality granularity, BFS-geoLevelnummer-keyed.

Command E — the newest research report never mentions the host:
```
$ grep -n "ogd-static\|voteinfo-app" docs/research/2026-10-04-events-elections-data-sources.md; echo "exit=$?"
exit=1
$ grep -c "ogd-static.voteinfo-app.ch" docs/research/2026-10-04-events-elections-data-sources.md
0
```
Only prior art is `docs/research/2026-08-27-bfs-vote-data.md:13` (documents the URL template).

## 3. Is it already done? NO.

```
$ git log --oneline -50 | grep -i "vote\|voteinfo\|ogd\|056" ; echo "hits=$?"
hits: exit=1 (zero hits in last 50 commits)
$ grep -rn "ogd-static\|voteinfo-app" docs/specs/ docs/decisions/ 2>&1
(no output)
$ grep -n "status\|implementationStatus" docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md
status: SPEC_READY
implementationStatus: PENDING_DEV
```
- No commit in the last 50 implements the fetch; HEAD is `adc0093 docs(research): ...` (research only).
- SPEC-056 itself is `SPEC_READY / PENDING_DEV` and contains no host URL (only the phrase
  "élő OGD integráció", line 18).
- The prior review verdict `v20261004163958-cc7419` flags honesty/verification gaps but not this
  wiring gap; nothing under `docs/audits/` or `.agent-pipeline/` tracks it as a defect.

## 4. Does production reach the code involved? YES — serving slice (not a wiring-only stub).

Caller sweep (run 2026-10-05):
```
$ grep -rn "parse_voteinfo_payload(" src/ tests/ --include="*.py" | grep -v "def parse_voteinfo"
(no output — parser is DEAD code)
$ grep -rn "get_latest_vote(" src/ --include="*.py" | grep -v "def get_latest"
src/main.py:344:    return _vote.get_latest_vote().model_dump()
$ grep -rn "\.sync(" src/ --include="*.py"
src/main.py:734:    return _voteinfo_connector.sync().model_dump()
```
Frontend equivalent:
```
frontend/src/lib/api.ts:171:  const res = await fetch(`${BASE}/api/v1/politics/votes/list`);
frontend/src/lib/api.ts:120:  civicVoteProposals: () => getJson<...>(`/api/v1/votes/proposals`),
frontend/src/components/civic/VotingVisualCard.tsx:25:    fetch(`${API}/api/v1/votes/proposals`, ...)
src/main.py:341:@app.get("/api/v1/politics/votes/latest")
src/main.py:347:@app.get("/api/v1/politics/votes/list")
src/main.py:635:@app.get("/api/v1/votes/proposals")
```
This is a **serving slice with dead parser code**: the HTTP endpoints ARE reachable from the
frontend (`fetchVoteProposals` → `/api/v1/politics/votes/list`), but they serve only the 2024
fixtures while the live-capable parser sits uncalled. Fixing it changes what production returns,
not just internal wiring.

## 5. Cheapest single-dispatch slice

One agent, backend-only, no frontend change:
1. In `src/services/connectors/bfs_voteinfo_client.py`: implement `sync(date: YYYYMMDD)` to
   `GET https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{date}-eidgAbstimmung.json`
   (allowlisted host const, timeout ~25 s, `httpx`, `source_pending`/stale semantics per
   SPEC-056 REQ-056-003 on non-200 incl. 403-for-no-vote-day; fall back to embedded fixtures).
2. In `src/services/vote_service.py`: call `parse_voteinfo_payload` on the fetched document inside
   the refresh path (or add a `refresh_from_ogd(date)` used by the `/connectors/voteinfo/sync`
   endpoint at `src/main.py:734`); keep `get_latest_vote()` signature.
3. Add ONE non-vacuous test: recorded OGD fixture (≤50 KB trimmed: 1 abstimmtag, 2 cantons with
   gemeinden) → `parse_voteinfo_payload` asserts `len(cantons)==2`,
   `national_yes_percent == <value from fixture>`, plus a contract test that the HTTP call targets
   the allowlisted `ogd-static.voteinfo-app.ch` host (must fail if fetch is deleted or host changes).
4. Do NOT touch: frontend, SPEC-056 text (or amend to WILL_NOT_DO with rationale — orchestrator decides),
   any other connector. Explicit non-goal: municipality UI, caching layer, multi-date history.

## 6. What would prove it is done (exact command + expected output)

```
$ .venv/bin/pytest tests/unit/test_politics_live.py tests/unit/test_spec046_055_060_contract.py -q
4 passed (existing 1 + 3, plus the new fixture test = 5 passed)
$ PYTHONPATH=. .venv/bin/python -c "
from src.services.connectors.bfs_voteinfo_client import BfsVoteInfoClient, OGD_HOST
assert OGD_HOST == 'ogd-static.voteinfo-app.ch', OGD_HOST
r = BfsVoteInfoClient().sync('20240922')
assert r.count >= 1 and len(r.sha256) == 64 and r.trust_state in ('official_publication','source_pending'), r
print('LIVE FETCH OK:', r.count, r.trust_state, OGD_HOST)"
LIVE FETCH OK: <count>=1> source_pending|official_publication ogd-static.voteinfo-app.ch
$ grep -rn "ogd-static.voteinfo-app.ch" src/ --include="*.py"
src/services/connectors/bfs_voteinfo_client.py:<line>: OGD_HOST = "ogd-static.voteinfo-app.ch" (or equivalent const)
```
Negative control (must fail before the fix, pass after): delete the fetch call → the new contract
test turns red; restore → green.

## 7. What could make this FAIL or be the wrong choice (risks not ruled out)

1. **No "latest vote" discovery endpoint (not established).** The OGD URL requires the vote date
   (`{YYYYMMDD}`) in the path; no index/latest-redirect was probed. If BFS publishes no machine-readable
   calendar, "latest" needs a hardcoded date list or a scrape of `voteinfo.bfs.admin.ch` — the slice
   could stall on date discovery. Mitigation in slice: accept `date` param, default to last known.
2. **Payload size (measured 2–6 MB).** Fetching full municipality JSON per request without cache would
   be slow; the slice must fetch on sync/admin trigger, not per page view. A per-request fetch would be
   the wrong architecture (not ruled out by load test — not attempted).
3. **Wrong-choice risk: stale-data tolerance.** If the product decision is "2024 fixtures are acceptable
   demo data", wiring live OGD is wasted work — but that decision is nowhere recorded (SPEC-056 says
   PENDING_DEV, no WILL_NOT_DO). The orchestrator must confirm the product direction before dispatch.
4. **Schema drift (partially ruled out).** 20240922 parses today (26 cantons, id 6710); 2025/2026
   payloads return HTTP 200 with similar sizes but were NOT parsed field-by-field (not attempted for
   each date) — a schema change in a newer abstimmtag could break the parser silently.

---
Evidence durability: all commands read-only; no repo file modified (`git status --short` shows only
pre-existing untracked `.agent-pipeline/`). Cwd reset to /tmp. Prior verdict quoted in header.
BUDGET: not exhausted (all 7 items answered within budget).
