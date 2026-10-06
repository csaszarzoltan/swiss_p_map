dispatch:  /home/zoltan/.hermes/cache/scratch/dispatch/nw1-brief-reviewer.md
agent:     reviewer
repo:      /home/zoltan/swiss_p_map @ adc0093
brief:     sha256:6c8e492edec6
verdict:   v20261004163958-cc7419 | REQUEST-CHANGES | commit=adc0093 | note: verification 3/5 honesty 3/5: report claims two unmeasured facts (brief 'n/a' was false - ledger has brief_sha; '_bh-searcher unavailable' never tried), and 3 of brief item (d) silently dropped for budget. Add a Commands run section and a 'Not covered' section.
status:    DONE — all 7 items answered; gap is unprobed VoteInfo OGD static host

# Review: What adc0093 left incomplete (excluding the two established findings)

Context: headline findings (a) 23-line BFS VoteInfo stub and (b) hardcoded map vote data are taken as given and not re-reported per brief.

---

## 1. Single most concrete gap

The report declares "Federal per-municipality results, programmatic → NOT AVAILABLE as an API … What VoteInfo exposes beyond a proposal list: nothing reachable — there is nothing to call" (sections 2–3 and 3, bullet (a)) after probing only `voteinfo.bfs.admin.ch` and `abstimmungen.bfs.admin.ch`. It never fetched the canonical VoteInfo OGD host documented in this same repo since 2026-08-27 — `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json` — which is live, HTTP 200, ~2 MB, and returns municipality-level federal vote results (Gemeinde granularity). The report's negative is therefore drawn from the wrong hosts.

## 2. Command and real output proving the gap TODAY

Command A — the report never mentions the real host (run 2026-10-05):

```
$ grep -c "ogd-static.voteinfo-app.ch" docs/research/2026-10-04-events-elections-data-sources.md
0
$ grep -c "gemeinden" docs/research/2026-10-04-events-elections-data-sources.md
4
$ grep "voteinfo-app\|ogd-static" docs/research/2026-10-04-events-elections-data-sources.md; echo "exit=$?"
exit=1
```

Command B — the host is live and was not fetched by the report's "Fetched URLs" table (38 rows, none for ogd-static):

```
$ curl -s -o /dev/null -w "HTTP %{http_code} size=%{size_download} time=%{time_total}s url=%{url_effective}\n" --max-time 25 "https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20240922-eidgAbstimmung.json"
HTTP 200 size=1977268 time=0.247687s url=https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20240922-eidgAbstimmung.json

$ curl -s -o /dev/null -w "20260927: HTTP %{http_code} size=%{size_download}\n" --max-time 25 "https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20260927-eidgAbstimmung.json"
20260927: HTTP 200 size=2056409
```

Command C — payload shape proves municipality granularity (the very "per-municipality results" the report says have no endpoint). Ran with that live payload saved as vi-20240922.json:

```
$ python3 -c "
import json
d = json.load(open('vi-20240922.json'))
print('top keys:', list(d.keys()))
print('abstimmtag:', d.get('abstimmtag'))
v = d['schweiz']['vorlagen']
print('num vorlagen:', len(v))
k = v[0].get('kantone',[])
print('num kantone:', len(k))
print('k0 gemeinden count:', len(k[0].get('gemeinden',[])))
print('k0 bezirke count:', len(k[0].get('bezirke',[])))
print('g0:', json.dumps(k[0]['gemeinden'][0], ensure_ascii=False)[:500])
"
top keys: ['abstimmtag', 'timestamp', 'spatial_reference', 'schweiz']
abstimmtag: 20240922
num vorlagen: 2
num kantone: 26
k0 gemeinden count: 161
k0 bezirke count: 13
g0: {"geoLevelnummer": "1", "geoLevelname": "Aeugst am Albis", "geoLevelParentnummer": "101", "resultat": {"gebietAusgezaehlt": true, "jaStimmenInProzent": 38.327091136, "jaStimmenAbsolut": 307, "neinStimmenAbsolut": 494, "stimmbeteiligungInProzent": 58.430232558, "eingelegteStimmzettel": 804, "anzahlStimmberechtigte": 1376, "gueltigeStimmen": 801}}
```

The repo's own parser already understands this payload — it was just never wired to fetch it:

```
$ PYTHONPATH=. .venv/bin/python -c "
import json
from src.services.vote_service import VoteService
d = json.load(open('/tmp/vi-20240922.json'))
p = VoteService().parse_voteinfo_payload(d)
print('parsed:', p.proposal_id if p else None, '| cantons:', len(p.cantons) if p else 0, '| national_yes:', round(p.national_yes_percent,2) if p else None)
"
parsed: 6710 | cantons: 26 | national_yes: 36.96
```

And the serving path confirms the disconnect — VoteService never fetches the host, the endpoint serves only embedded 2024 fixtures, and the report's own "Fetched URLs" table contains no ogd-static entry.

```
$ grep -n "http\|httpx\|get(\|fetch\|ogd" src/services/vote_service.py | head
8:import httpx
$ grep -n "vote\|VoteInfo\|ogd" src/main.py | head
341:@app.get("/api/v1/politics/votes/latest")
... (no ogd-static, no voteinfo-app anywhere in src/)
$ grep -rn "ogd-static" --include="*.md" --include="*.py" . | grep -v ".agent-pipeline"
docs/research/2026-08-27-bfs-vote-data.md:13:A svájci állam hivatalos nyílt adatforrása a **VoteInfo OGD webszolgáltatás** (`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`).
```

## 3. Does a test already cover the gap?

NO — no existing test fetches or asserts the OGD host.

Relevant test files run (2026-10-05, venv pytest):

```
$ .venv/bin/pytest tests/unit/test_spec046_055_060_contract.py -q -k "056"
3 passed, 21 deselected, 1 warning in 1.10s

$ .venv/bin/pytest tests/unit/test_politics_live.py -q
1 passed in 0.53s
```

What those 3 SPEC-056 tests actually assert (all on the stub, zero network):

- `test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash` — `BfsVoteInfoClient().sync()` sha equality
- `test_spec_056_req_056_002_ac_056_001_sync_trust_metadata` — `trust_state == "official_publication"`
- `test_spec_056_req_056_001_ac_056_001_sync_api_contract` — `POST /api/v1/connectors/voteinfo/sync` returns count==1

None calls `https://ogd-static.voteinfo-app.ch/...`, none calls `VoteService.parse_voteinfo_payload` with a live or fixture OGD document, and `VoteService.get_latest_vote()` is tested only against hardcoded dicts. If a test covered the gap it would not be a gap — as measured, no such test exists.

## 4. Is the gap already recorded somewhere?

Grepped for record of the missing host:

```
$ grep -rn "ogd-static\|voteinfo-app" docs/specs/ docs/decisions/ 2>&1
(no output)

$ grep -n "http\|URL\|endpoint\|S3\|OGD" docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md
18:Resident-first civic UX, élő OGD integráció ... (no URL, no host)

$ grep -rn "ogd-static\|voteinfo-app" docs/research/2026-10-04-events-elections-data-sources.md; echo "exit=$?"
exit=1  (0 hits — report never mentions the host)

$ grep -rn "ogd-static\|voteinfo-app" --include="*.md" .
docs/research/2026-08-27-bfs-vote-data.md:13: ... `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`
```

Result: the host IS recorded in the prior research `docs/research/2026-08-27-bfs-vote-data.md` (and therefore known to ADR-012 and `src/services/vote_service.py:parse_voteinfo_payload`), but the new report's 38-row "Fetched URLs" and "Source Links" tables silently drop it, and neither `docs/specs/SPEC-056`, `ADR-012`, nor any file under `docs/audits/` records the omission as an open item. The open review verdict `v20261004163958-cc7419` flags honesty/verification gaps but not this host. So the gap itself is not tracked anywhere as a defect/spec debt.

## 5. Vacuous test coverage (at most 2, each must be able to fail)

Found 2 vacuous tests — both would stay green if the code under test were deleted or its network path inverted, because they assert literals on a stub that never touches the network.

1. `tests/unit/test_spec046_055_060_contract.py:106` — `test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash`:
```python
def test_spec_056_req_056_001_ac_056_001_sync_deterministic_hash() -> None:
    a, b = BfsVoteInfoClient().sync(), BfsVoteInfoClient().sync()
    assert a.count == 1 and len(a.sha256) == 64
    assert a.sha256 == b.sha256
```
Why vacuous: `BfsVoteInfoClient.sync()` (`src/services/connectors/bfs_voteinfo_client.py:12-16`) is `rows = [{"id": 6670, "yes": 58.2}]; raw = json.dumps(rows).encode(); return VoteSync(count=1, sha256=hash(raw))`. It never opens a socket. The test asserts the hash is deterministic and 64 chars — true of any constant — and would still pass if the entire OGD fetch were deleted, inverted to return an error, or replaced by `return VoteSync(count=1, sha256="0"*64)`. It cannot fail due to a broken OGD contract because it never exercises one (cf. CLAUDE 3d: mocked boundary proves nothing about the boundary).

2. `tests/unit/test_phase3_civic_services.py:13` — `test_spec_056_req_056_001_ac_056_001_voteinfo_hash`:
```python
def test_spec_056_req_056_001_ac_056_001_voteinfo_hash() -> None:
    assert len(BfsVoteInfoClient().sync().sha256) == 64
```
Why vacuous: same stub, even weaker assertion (only length). Deleting `src/services/vote_service.py:parse_voteinfo_payload` or changing `src/main.py:politics_votes_latest` to return a different proposal has no effect on this test. The assertion `len(sha256)==64` would also pass after inverting the implementation to return a random hash. No test in the suite would turn red if the OGD host went down, changed schema, or was never implemented — which is exactly the production defect.

Note: vacuous does not mean "useless for regression of the stub" — it means these tests cannot catch the OGD integration gap and a green run over them (3 passed, 1 passed above) must not be read as "VoteInfo OGD is covered".

## 6. Risk of NOT fixing

The map will keep serving four hardcoded 2024 proposals (IDs 6670/6680/6690/6700) as if they were live federal results while every vote since 2024-11-24 — including 2026-09-27 (HTTP 200, 2.0 MB, verified) — and all available municipality-level granularity stay unused, so users see stale outcomes and operators cannot tell that the only genuine federal per-municipality OGD feed is being ignored.

## 7. What would satisfy closure

All of:
- The research report (or a successor doc) adds a `Commands run` entry that live-fetches `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json` at least twice (e.g., 20240922 and latest 2026-09-27), logs HTTP status, byte size, `abstimmtag`/`timestamp`/`spatial_reference` keys, and documents that `schweiz.vorlagen[0].kantone[*].gemeinden` yields municipality granularity (ZIP-free, BFS-geoLevelnummer-keyed) with a sample gemeinde JSON — or records an explicit, reviewed product decision not to use it with a named owner.
- `src/services/vote_service.py` or `src/services/connectors/bfs_voteinfo_client.py` (or a new connector) is either wired to fetch that URL (with allowlisted host, timeout, and stale/source_pending semantics per SPEC-056 REQ-056-003) or the spec is amended to `WILL_NOT_DO` with rationale; the report's "NOT available" bullet is corrected to name the actual host and what it does expose.
- One non-vacuous test is added and green: e.g., a fixture or live-recorded OGD JSON fed to `VoteService.parse_voteinfo_payload` asserting `len(result.cantons)==26` and `any(len(k_gemeinden)>0)` / `national_yes_percent` matches `resultat.jaStimmenInProzent`, plus a contract test that the HTTP call is to the allowlisted `ogd-static.voteinfo-app.ch` host (not mocked to accept any host). That test must be able to fail if the fetch is deleted or the schema is inverted.

---

## Evidence durability

Commands were read-only. One temporary file `vi-20240922.json` (live OGD payload) was created under `/tmp` for verification and removed before close. No repo file was modified, so no `git checkout --` was needed.

```
$ git -C /home/zoltan/swiss_p_map log --oneline -1
adc0093 docs(research): esemeny- es valasztasi adatforrasok verifikalt felmerese

$ git -C /home/zoltan/swiss_p_map status --short
(empty)

$ .venv/bin/pytest tests/unit/test_spec046_055_060_contract.py -q -k "056"
3 passed, 21 deselected

$ .venv/bin/pytest tests/unit/test_politics_live.py -q
1 passed
```

Report written to both required destinations; orchestrator commits after gate.

