# SPEC-056b — Live VoteInfo OGD Wiring (backend-only slice)

| Field | Value |
|---|---|
| ID | SPEC-056b |
| Parent | SPEC-056 (`docs/specs/SPEC-056-elo-bfs-voteinfo-szavazasi-konnektor.md`, `implementationStatus: PENDING_DEV`, names NO host/URL) |
| Scope | Backend only — wire existing parser to live OGD host |
| Status | IMPLEMENTED, RE-GATED — APPROVE 5.0 (`cf5c4ed`); FR-02 honesty fix verified: live result isolated in `_live_proposals`, fixtures fallback-only |
| Date | 2026-10-05 |
| Repo | `/home/zoltan/swiss_p_map` @ `adc0093` (clean tree) |

## 0. Measured facts (orchestrator-verified, planner re-checked 2026-10-05)

- `BfsVoteInfoClient.sync()` (`src/services/connectors/bfs_voteinfo_client.py:12-16`) is a stub:
  `rows = [{"id": 6670, "yes": 58.2}]` — never opens a socket. No `httpx`/`urllib` import
  (file imports only `hashlib`, `json`, `pydantic`).
- `VoteService.parse_voteinfo_payload` (`src/services/vote_service.py:311`) EXISTS and correctly
  parses the real payload. Measured: fed a live payload it returned
  `proposal 6710 | cantons 26 | national_yes 36.96`.
- That parser has ZERO callers. Planner re-ran during planning:
  `grep -rn "parse_voteinfo_payload" src/ tests/` → exactly one hit (its own `def`).
  **This is a wiring defect, not a testing gap.**
- Live OGD host is REAL and was never called by this repo:
  `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`
  — measured HTTP 200, 1 977 268 bytes, top keys
  `['abstimmtag','timestamp','spatial_reference','schweiz']`,
  `schweiz.vorlagen[0].kantone[0].gemeinden` = **161 municipalities**, 26 cantons, each gemeinde
  keyed by `geoLevelnummer` (BFS) with `resultat.jaStimmenInProzent` etc.
- Host already documented in the repo's own earlier research:
  `docs/research/2026-08-27-bfs-vote-data.md:13`:
  > "A svájci állam hivatalos nyílt adatforrása a **VoteInfo OGD webszolgáltatás**
  > (`https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`)."
- Currently-served data: 4 hardcoded 2024 fixtures (IDs 6670/6680/6690/6700,
  `vote_service.py:223-272` via `_all_default_proposals()`), served at
  `GET /api/v1/politics/votes/latest` (`src/main.py:341-344`).
- `VoteService.__init__` already takes `client: httpx.AsyncClient | None = None`
  (`vote_service.py`); `httpx` is already a dependency (`pyproject.toml:18`,
  `requirements.txt:4`, installed version **0.28.1** measured in venv).
- Precedent for honest empty-state metadata exists in-repo: `src/main.py:599-680`
  returns `"trust_state": "source_pending"` for empty feeds.

## 0b. Scope decisions (made by orchestrator — NOT reopened here)

1. **BACKEND ONLY.** Do not touch `frontend/`; the map's hardcoded canton colours are a
   separate, later slice.
2. **Live fetch behind the existing DI seam** (`httpx.AsyncClient` injected into
   `VoteService`), so tests need no network.
3. **No new external dependency.** `httpx` (0.28.1) is already declared and installed.
4. Fixtures stay as fallback seed data; they must never be presented as live.

---

## 1. Target Files allowlist (exact — developer may CREATE/EDIT only these)

| # | File | Change | Lines touched (approx) |
|---|---|---|---|
| 1 | `src/services/connectors/bfs_voteinfo_client.py` | Replace stub `sync()` with real async fetch of the OGD URL pattern (host + date param, injected `httpx.AsyncClient`, 10 s timeout per SPEC-056 NFR-056-001); raise typed error on failure, never fabricate rows | 1–30 (rewrite, keep `VoteSync` shape) |
| 2 | `src/services/vote_service.py` | Add `async refresh_from_live(...)` (or equivalent) that calls the connector → feeds bytes into the EXISTING `parse_voteinfo_payload` (line 311, unchanged logic) → swaps `_proposals` on success; add `source: str`, `fetched_at: str | None`, `trust_state: str` metadata carried alongside (NOT inside the `FederalVoteProposal` schema — see §3) | add ~40 lines; do NOT alter parser logic or fixture builders |
| 3 | `src/main.py` | Wrap the three votes routes (lines 341–357) response envelope with top-level `source` / `fetched_at` / `trust_state`; map unreachable-host to `trust_state: "source_pending"` with HTTP 200 + stale/empty payload (per SPEC-056 AC-056-002), never 500 with raw detail | 341–357 only |
| 4 | `src/models/vote.py` | ONLY if needed: add optional metadata model (e.g. `VoteEnvelope` or three optional fields on a wrapper — NOT required fields on `FederalVoteProposal`, to avoid breaking existing tests). Prefer no model change; a plain `dict` envelope in `main.py` is acceptable | 0–15 lines, additive only |

**Explicitly NOT in allowlist:** `frontend/**`, `SPEC-056` itself, any other service,
any test file (developer writes NO tests in this slice — `test-author` owns the gate),
`requirements.txt` / `pyproject.toml` (no new deps).

---

## 2. Functional requirements (each numbered, individually testable)

- **FR-01 [MUST]:** `BfsVoteInfoClient` performs a real HTTPS GET against
  `https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-{YYYYMMDD}-eidgAbstimmung.json`
  for a caller-supplied vote date (`YYYYMMDD`), using an injected `httpx.AsyncClient`
  (optional param, default `None` → create-per-call with `timeout=10`), and returns the
  raw JSON bytes/dict. No hardcoded rows remain on any code path.

> **Status note (SPEC-056c, 2026-10-06):** this second sentence was FALSE from `adc0093` through
> `f5c27a2` — `BfsVoteInfoClient.sync()` kept a hardcoded row `{"id": 6670, "yes": 58.2}`
> labelled `trust_state="official_publication"` on `POST /api/v1/connectors/voteinfo/sync`
> (measured: `grep -n 'rows = [{"id"' src/services/connectors/bfs_voteinfo_client.py` →
> line 123 pre-fix). Closed by SPEC-056c
> (`docs/specs/SPEC-056c-honest-sync-probe.md`): `sync()` is now a network-free probe with
> `count=0`, `fetched_at=null`, `trust_state="source_pending"`.
- **FR-02 [MUST]:** `VoteService` exposes an async refresh path that passes the fetched
  payload to the UNMODIFIED `parse_voteinfo_payload` and, on successful parse (26 cantons,
  `proposal_id > 0`), replaces the served proposals with the live result.
- **FR-03 [MUST]:** Every votes endpoint response carries top-level metadata
  `source` (e.g. `"BFS VoteInfo OGD"` for live, `"embedded-fixture"` for seed),
  `fetched_at` (ISO-8601 UTC string or `null` when never fetched), and
  `trust_state` (`"official_publication"` on live success, `"stale"` when serving
  fixtures after a failed refresh, `"source_pending"` when NO data of any kind is
  available). Per SPEC-056 REQ-056-002/REQ-056-005: a fallback MUST NOT carry
  `official_publication`/`official_measurement`.
- **FR-04 [MUST]:** When the host is unreachable / timeout / non-200 / schema-drift
  (parser returns `None`), the endpoints still answer HTTP 200 with the fixture payload
  (if present) labelled `trust_state: "stale"`, or an empty-items payload labelled
  `trust_state: "source_pending"` — never a fabricated `official_*` result, never a raw
  500 traceback (SPEC-056 §6: raw 500 detail forbidden).
- **FR-05 [MUST]:** No network in unit tests: all live-fetch code paths accept the
  injected `httpx.AsyncClient`, so `test-author` can use `httpx.MockTransport`.
- **FR-06 [MUST NOT]:** Frontend files, SPEC-056 text, dependency manifests, and the
  parser logic itself are unchanged. `grep -rn "parse_voteinfo_payload" src/` MUST show
  ≥2 hits after the fix (def + ≥1 caller) — see §5.
- **FR-07 [ALWAYS]:** Timeout ≤ 10 s on the OGD fetch (SPEC-056 NFR-056-001).

---

## 3. API contract

### Changed endpoints (behaviour + envelope; item shape UNCHANGED)

| Method | Path | Success | Failure (host down / parse fail) |
|---|---|---|---|
| `GET` | `/api/v1/politics/votes/latest` | `200` + envelope below (`official_publication` or `stale`) | `200` + envelope with `trust_state: "source_pending"` and `proposal: null` (when no fixtures either); still `200`, never 500 |
| `GET` | `/api/v1/politics/votes/list` | `200` + `{"items": [...], "source": ..., "fetched_at": ..., "trust_state": ...}` | `200` + `{"items": [], "source": ..., "fetched_at": null, "trust_state": "source_pending"}` |
| `GET` | `/api/v1/politics/votes/{proposal_id}` | `200` + envelope; unknown ID → `404 {"detail": "Proposal {id} not found"}` (UNCHANGED) | Same 404 rule UNCHANGED; `source_pending` applies only when store is empty |

Exact envelope shape for `/latest` (new top-level keys only; inner proposal schema byte-identical):

```json
{
  "proposal": { "<FederalVoteProposal model_dump — UNCHANGED>" },
  "source": "BFS VoteInfo OGD",
  "fetched_at": "2026-10-05T12:00:00Z",
  "trust_state": "official_publication"
}
```

`trust_state` vocabulary (closed): `official_publication` | `stale` | `source_pending`.
(`official_measurement` is deliberately NOT issued by this slice — publication file ≠ certified count.)

### UNCHANGED

- Inner `FederalVoteProposal` / `CantonVoteResult` JSON field names and types.
- `404` for unknown `proposal_id`.
- All non-votes routes.
- Correction (SPEC-056c, 2026-10-06): the claim that `POST /api/v1/connectors/voteinfo/sync` and
  `GET /api/v1/votes/proposals` "do NOT exist in this tree" was false — both exist
  (`src/main.py:766` and `src/main.py:669`; the latter is SPEC-051's surface,
  `tests/unit/test_spec051_voting_contract.py:1`). Neither was *introduced by SPEC-056b*, which
  is what this out-of-scope note meant.

---

## 4. Acceptance criteria — RUNNABLE commands

> Each command was actually executed in `/home/zoltan/swiss_p_map` during planning on
> 2026-10-05, and the quoted output is the observed output. Commands not run are marked
> **"not run"**. Post-fix expected outputs are stated per criterion.

- **AC-01 (stub is gone):** `grep -n "httpx\|urllib\|AsyncClient" src/services/connectors/bfs_voteinfo_client.py`
  — observed pre-fix output: *(empty — no match, exit 1)*. Post-fix pass: ≥1 match.
- **AC-02 (parser is wired):** `grep -rn "parse_voteinfo_payload" src/ tests/`
  — observed pre-fix output: `src/services/vote_service.py:311:    def parse_voteinfo_payload(`
  (exactly one hit — its own `def`). Post-fix pass: ≥2 hits (def + caller).
- **AC-03 (dependency present):** `.venv/bin/python -c "import httpx; print(httpx.__version__)"`
  — observed output: `0.28.1`. (Proves FR-07/no-new-dep implementable; no install needed.)
- **AC-04 (routes exist at known lines):** `sed -n '341,357p' src/main.py`
  — observed: the three `@app.get("/api/v1/politics/votes/...")` handlers. Post-fix pass:
  same three routes present, each returning the §3 envelope (verified by test-author's gate).
- **AC-05 (honest-state precedent reusable):** `grep -n "source_pending" src/main.py`
  — observed output includes lines `610`, `666`, `680` (`"trust_state": "source_pending"`).
  Post-fix pass: votes routes reuse the same literal, no new vocabulary invented.
- **AC-06 (gates — not run):** `pytest tests/unit/test_vote_service.py -q` — **not run**
  (planner ran no test suite; `test-author`/`tester` own verification. Baseline per brief:
  pytest 250 passed / 1 skipped; mypy strict; ruff clean — developer must preserve all three).
- **AC-07 (live fetch E2E — not run):** any live-HTTP assertion — **not run** (no network
  calls made during planning). Live validation is owned by the implementer's manual check
  + `test-author`'s `MockTransport` gate; this SPEC carries `no-live-validation` for the
  fetch path itself — the host facts in §0 are orchestrator-measured, not planner-measured.

---

## 5. NEGATIVE acceptance (proves the fix is wired)

- **Command:** `grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l`
- **Pre-fix expected output:** `1` (observed during planning — only the `def` at
  `vote_service.py:311`; zero callers).
- **Post-fix pass:** output `>= 2` (the `def` plus at least one call site in
  `vote_service.py` refresh path and/or `bfs_voteinfo_client.py` consumer).
- **How it FAILS pre-fix:** any test asserting "live payload reaches the parser" fails
  because no call edge exists — the suite can only exercise the parser in isolation or
  the fixtures. A `test-author` gate test that feeds a canned OGD payload through
  `refresh_from_live` with `MockTransport` MUST fail on the pre-fix tree (no such method)
  and pass post-fix. (Anti-brittleness: assert on the anchored call edge
  `refresh_from_live.*parse_voteinfo_payload` via `rfind`/regex in the gate test, NOT on
  bare `find("confidence_level")`-style substring distance.)

---

## 6. STOP command

```sh
cd /home/zoltan/swiss_p_map && grep -rn "parse_voteinfo_payload" src/ tests/ | wc -l && grep -c "AsyncClient" src/services/connectors/bfs_voteinfo_client.py && grep -c "trust_state" src/main.py
```

**Done = first number `>= 2`, second number `>= 1`, third number strictly greater than
pre-fix count (pre-fix: `grep -c "trust_state" src/main.py` covers lines ~599–680 only —
votes routes add new occurrences), AND `pytest tests/unit/test_vote_service.py -q`,
`mypy` (strict, repo config), and `ruff check` all green.**

---

## 7. Risks and honest limits

| # | Risk | Required behaviour | Unknown / not determined |
|---|---|---|---|
| R-1 | Host down / DNS / TLS fail / non-200 | Catch `httpx.HTTPError` + non-200 → FR-04: serve fixtures as `stale`, or `source_pending` if store empty. Log, never raise to 500. | Retry/backoff policy: NOT specified — single attempt per refresh is the narrow interpretation; document if implemented. |
| R-2 | Schema drift (new keys, renamed `jaStimmenInProzent`, missing `kantone`) | `parse_voteinfo_payload` returns `None` → treated exactly like fetch failure (FR-04). Parser logic itself is NOT hardened in this slice. | Drift detection/alerting: none in this slice — **not determined** how ops learns the parse broke; at minimum log at ERROR. |
| R-3 | Date param (`{YYYYMMDD}`): which date is "latest"? | Caller supplies the vote Sunday explicitly; `refresh_from_live(date: str)` validates `^\d{8}$`, else 422/`ValueError` — never guess. Initial wiring may hardcode the most recent known federal vote Sunday with a `TODO(SPEC-056b-R3)` comment. | Auto-discovery of latest vote date (index/source-of-truth URL): **could not determine** — no catalogue endpoint found during planning; marked `no-live-validation`. |
| R-4 | Stale cache served as fresh | `fetched_at` MUST be `null`/old and `trust_state` MUST NOT be `official_*` whenever payload did not come from a successful live parse (SPEC-056 REQ-056-005). | Cache TTL / background refresh cadence: NOT in this slice (SPEC-056 NFR-056-001 mentions provider-cycle TTL — deferred). Refresh is on-demand/process-start, not scheduled. |
| R-5 | Municipality-level data (161 gemeinden measured) silently dropped | Accepted: parser aggregates canton-level only; gemeinden are ignored by design in this slice. | Gemeinder-level endpoint: explicitly out of scope (§8). |
| R-6 | SSRF / URL injection via date param | Date strictly validated (`^\d{8}$`); host constant, no user-controlled host/path. | Full SSRF allowlist review (SPEC-056 §13): out of scope for this slice. |
| R-7 | Sync vs async mismatch (`sync()` is sync, DI seam is `AsyncClient`) | Make the fetch `async`; keep a thin sync wrapper only if existing callers need it (none found — no callers of `sync()` either). Prefer `async def fetch(...)`. | — |

Anything in the "not determined" column that the developer cannot resolve within the slice
MUST be reported as `not attempted`/`not established` in their report — not guessed into code.

---

## 8. OUT of scope (explicitly NOT this slice)

1. `frontend/**` — map colours, components, i18n keys (`phase3.feature056.*`), WCAG work.
2. New endpoints from SPEC-056 §8 (`POST /api/v1/connectors/voteinfo/sync`,
   `GET /api/v1/votes/proposals`) — not introduced here.
3. Municipality/gemeinde-level serving (161 gemeinden stay unexposed).
4. Background scheduling, cache TTL, push/email notifications, idempotency keys,
   double opt-in (SPEC-056 REQ-056-004/006, §§9–13) — later slices.
5. Parser hardening against schema drift beyond returning `None`.
6. Auto-discovery of the latest vote date.
7. New dependencies; test files (owned by `test-author`); SPEC-056 text edits.
8. `official_measurement` trust state — never issued by this slice.

---

## 9. E2E / gate sketch (for `test-author` — non-binding, informative)

- Gate test file (suggested): `tests/unit/test_spec056b_live_wiring.py` — uses
  `httpx.MockTransport` + canned minimal OGD payload (`abstimmtag`, `schweiz.vorlagen[0]`
  with 26 `kantone` entries keyed by `geoLevelnummer` 1..26).
- Assert: (a) refresh path calls `parse_voteinfo_payload` (anchored regex/`rfind`, not bare
  `find`); (b) `/api/v1/politics/votes/latest` envelope contains
  `source`/`fetched_at`/`trust_state` with `official_publication` on mocked-live success;
  (c) transport raising `httpx.ConnectError` → HTTP 200 + `trust_state in {"stale",
  "source_pending"}` and NO `official_*`; (d) malformed payload (parser → `None`) → same
  honest state; (e) every assertion fails pre-fix (no refresh method, no envelope keys).
- Full gates to preserve: `pytest` (baseline 250 passed / 1 skipped), `mypy` strict,
  `ruff check`.

---

*Research grounding: live-host facts measured by orchestrator (HTTP 200, 1 977 268 bytes,
top keys, 161 municipalities, `proposal 6710 | cantons 26 | national_yes 36.96` parse probe);
repo's own research `docs/research/2026-08-27-bfs-vote-data.md:13` (URL pattern);
SPEC-056 (`implementationStatus: PENDING_DEV`, no host/URL); in-repo precedent
`src/main.py:599-680` (`source_pending`); `httpx 0.28.1` in venv (`pyproject.toml:18`).*
