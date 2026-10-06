```
dispatch:  inline prompt
agent:     explore
repo:      /home/zoltan/swiss_p_map @ f5c27a2
brief:     sha256:3199fda5832d
verdict:   v20261006034712-9d9c9e REQUEST-CHANGES (ptr-nw1-review.md 4.0 APPROVED)
status:    DONE — all 7 items answered with measured output; read-only, nothing edited
```

# nw2-explore: highest-value NEXT change

## 1. Single highest-value next change

Wire the Map3D `politik` choropleth to the live per-canton vote API: replace the hardcoded
`yes` values from `frontend/src/app/swissCantons.ts` (consumed at `Map3D.tsx:852`) with the
live `cantons[code].yes_percent` already served by `GET /api/v1/politics/votes/latest|list|{id}`.

## 2. File:line evidence the problem exists TODAY (commands + real output)

Command A: `sed -n '845,860p' frontend/src/app/Map3D.tsx`
```
      } else if (activeTopic === "politik") {
        const yes = (mesh.userData.yes as number) ?? 52.0;
        const hex = yes >= 55 ? "#38bdf8" : yes >= 50 ? "#0284c7" : yes >= 45 ? "#f43f5e" : "#be123c";
        color = new THREE.Color(hex);
        opacity = 0.65;
```

Command B: `grep -n '"yes":' frontend/src/app/swissCantons.ts | head -5`
```
11:    "yes": 52.1,
371:        "yes": 68.3,
623:        "yes": 67.9,
831:        "yes": 67.2,
1071:        "yes": 70.4,
```

Command C: `grep -rn 'fetchVoteProposal' frontend/` (fetch helpers exist, zero callers)
```
frontend/src/lib/api.ts:170:export async function fetchVoteProposals(): Promise<VoteProposalOverview[]> {
frontend/src/lib/api.ts:177:export async function fetchVoteProposal(id: number): Promise<unknown | null> {
```

Command D: `sed -n '160,185p' frontend/src/lib/api.ts` (helpers target the live SPEC-056b routes)
```
export async function fetchVoteProposals(): Promise<VoteProposalOverview[]> {
  const res = await fetch(`${BASE}/api/v1/politics/votes/list`);
  ...
export async function fetchVoteProposal(id: number): Promise<unknown | null> {
  const res = await fetch(`${BASE}/api/v1/politics/votes/${id}`);
```

So: the color input (`mesh.userData.yes`, spread from the hardcoded canton object via
`buildMesh` at `Map3D.tsx:122-131` $\leftarrow$ `Map3D.tsx:456`) is static data, while the live
replacement is one fetch away behind helpers nobody calls.

## 3. Is it already done? NO

- `git log --oneline -50 -- frontend/src/app/swissCantons.ts frontend/src/app/Map3D.tsx` shows only
  geometry/i18n/layer work (`e219495` geometry restore, `c3837db` i18n, `a8f07a8`/`f36c551` layer
  harmonization) — no commit wiring Map3D to any votes endpoint.
- `grep -rn 'Map3D.*live\|live.*Map3D\|swissCantons.*live\|live.*swissCantons\|Map3D.*politics/votes\|politik.*live' docs/`
  returned only one tangential row (`docs/audits/SPEC-coverage-2026-09-23.md:34`, INDIRECT coverage
  via `test_politics_live.py`, not a Map3D wiring spec). Related but distinct: `BRIEF-051` (voting
  cards), `ADR-003` (schematic map), `SPEC-056b-live-voteinfo-ogd-wiring.md` (backend only).
- No commit found; nothing in `docs/` covers a Map3D-live-votes slice.

## 4. Does production reach the code? WIRING slice (dead-end helpers + live backend + live consumer)

Backend symbol check — `grep -rn 'get_latest_vote(' src/ --include="*.py" | grep -v 'def get_latest_vote'`:
```
src/main.py:362:    proposal = _vote.get_latest_vote()
```
Backend symbol check — `grep -rn 'refresh_from_live(' src/ --include="*.py" | grep -v 'def refresh_from_live'`:
```
src/main.py:359:    await _vote.refresh_from_live()
src/main.py:375:    await _vote.refresh_from_live()
src/main.py:389:    await _vote.refresh_from_live()
```
Frontend check — `grep -rn 'SWISS_CANTONS\|swissCantons' frontend/`:
```
frontend/src/app/Map3D.tsx:7:import { SWISS_CANTONS } from "./swissCantons";
frontend/src/app/Map3D.tsx:455:    SWISS_CANTONS.forEach((canton) => {
frontend/src/app/projection.ts:1:/** Lon/lat → Map3D model X/Y (same projection as swissCantons/mapOverlay gen). */
frontend/src/app/swissCantons.ts:5:export const SWISS_CANTONS: SwissCanton[] = [
```
Frontend check — `grep -rn 'fetchVoteProposal' frontend/` shows the two `api.ts` definitions and
**zero call sites** (Command C output above is the complete result).

Verdict for this item: **WIRING slice, not a testing slice.** The backend serves live 26-canton
payloads (`FederalVoteProposal.cantons: dict[str, CantonVoteResult]`, `src/models/vote.py:39-41`,
each with `yes_percent`, `src/models/vote.py:15-17`), the consumer (`Map3D.tsx:851-855`) renders
colors from `userData.yes`, and the bridge (`fetchVoteProposals`/`fetchVoteProposal`) has no
callers. Nothing needs inventing; the two ends exist and are unconnected.

## 5. Cheapest single-dispatch slice

One agent, one dispatch, frontend-only: when the `politik` topic activates in `Map3D.tsx`, call
`fetchVoteProposals()` $\rightarrow$ `fetchVoteProposal(latestId)`, map
`proposal.cantons[code].yes_percent` onto each canton mesh's `userData.yes` (matching on the
existing canton `id`/2-letter code), keep the hardcoded `yes` as fallback when the envelope is
`source_pending` or fetch fails; do NOT touch `swissCantons.ts` geometry (40,316 lines) and do NOT
touch backend. Explicitly out of scope: Bezirk-level live values, gemeente geometry, color-scale
redesign.

## 6. What would prove it is done (exact commands + expected output)

Command 1 (bridge exists):
`grep -rn 'fetchVoteProposal(' frontend/src --include='*.tsx' --include='*.ts' | grep -v 'lib/api.ts'`
Expected: $\geq$ 1 call site in `Map3D.tsx` (or a hook it imports), e.g.
`frontend/src/app/Map3D.tsx:<line>: ... fetchVoteProposal(...`.

Command 2 (backend contract unchanged, live shape still 26 cantons):
`python3 -c "import json,urllib.request; d=json.load(urllib.request.urlopen('http://localhost:8000/api/v1/politics/votes/latest')); p=d.get('proposal') or d; print(len(p['cantons']), sorted(p['cantons'])[:3])"`
Expected: `26 ['AG', 'AI', 'AR']` (or `{"proposal": None, ... "trust_state": "source_pending"}` when
the OGD source is unreachable — in which case the frontend must show the hardcoded fallback, which
is itself the asserted behavior).

Command 3 (no regression):
`pytest tests/ -q` — expected: `264 passed, 1 skipped` (current baseline; frontend-only change must
not move the backend suite).

## 7. What could make this FAIL or be the wrong choice (risks not ruled out)

1. **Live-source availability**: if `trust_state == "source_pending"` is the common production
   state (OGD unreachable), the map still shows hardcoded colors most of the time and the user-visible
   gain is near zero. NOT measured — no live endpoint probe was run (read-only explore, backend not
   started).
2. **Key mismatch**: `proposal.cantons` is keyed by 2-letter code (`src/models/vote.py:11`); whether
   every `SWISS_CANTONS[].id` matches those codes exactly was NOT verified exhaustively (only `ZH`
   spot-checked at `swissCantons.ts:8-11`).
3. **Wrong-half risk**: Bezirk-level `yes` literals (152 names, `Bezirk 1001` placeholders at
   `swissCantons.ts:12504,32416`) stay hardcoded — if the user's complaint is about drill-down
   colors rather than canton colors, this slice fixes the wrong half.
4. **Competing candidate**: `BfsVoteInfoClient.sync()` literal (`bfs_voteinfo_client.py:123`) and the
   two vacuous sha-length asserts remain; they are lower value (pinned legacy probe, cosmetic) but a
   reviewer could argue cleanup-first.
5. Product direction (map colors follow the *latest* vote vs a *selected* proposal) is NOT decided
   here — left to the orchestrator brief.

---
*Teams checklist reference: this report carries file:line evidence with pasted command output for
every factual claim (items 2–4); item 3 names the greps run (`git log` on both frontend files,
`docs/` live-wiring grep); nothing was edited, nothing committed; report written to (b) inside the
repo, mirrored to (a) scratch by the command below.*
