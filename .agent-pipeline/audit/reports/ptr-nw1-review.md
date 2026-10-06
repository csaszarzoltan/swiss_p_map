```
REPO:            /home/zoltan/swiss_p_map
COMMIT(S):       3d21fe5 5bec959 aebfafe 2904f21 2579c21 cf5c4ed 6947f8f
DISPATCHES:      11 mine (nw1-*) · LEDGER: ~/.cache/claude-queue/dispatch-log/dispatch-ledger.log
ARTIFACTS:       7/7 reports IN GIT · 29 dispatch artifacts remain scratch-only

SCORES:  brief 3 · target 5 · verification 4 · scope 5 · honesty 3 · evidence 4
AVERAGE: 4.0   VERDICT: APPROVED (at threshold — three findings below)
```

## CONFIRMED — with the evidence that held up

**PART 0 — my own briefs were strong, and the one gap matches the skill's measured pattern.**
```
brief                       bytes  budget  report-each  do-not-decide
nw1-brief-dev3.md            2549      yes        NO           yes     <- the ONLY miss
nw1-brief-dev2.md            5655      yes        yes          NO
nw1-brief-dev.md             4967      yes        yes          NO
(all 12 briefs)               --     12/12      11/12       5/12
```
Budget clause 12/12, "report each even if NO" 11/12. **The single miss is the shortest brief of the
run** — the exact pattern this skill records ("the two that lacked it were the longest and the
shortest brief of the run"). Writing the rule down did not protect the short brief.

**PART 1d — the target was load-bearing, and the wiring slice was real.**
```
pre-fix:  grep -rn 'parse_voteinfo_payload' src/ tests/ | wc -l   -> 1    (its own def)
post-fix: same grep                                              -> 4
call chain (measured): src/main.py:359,375,389  await _vote.refresh_from_live()
                       -> vote_service.py:403   self.parse_voteinfo_payload(payload)
                       -> vote_service.py:459   def parse_voteinfo_payload
```
Not a zero-caller case, and not a testing slice dressed as work. **This is the check the review
exists to run, and it passes.**

**PART 3 — the gate can fail, proven in place (not on a /tmp copy).** I mutated the real file:
```
mutated src/services/vote_service.py:427
  self._live_proposals = {parsed.proposal_id: parsed}
    -> self._proposals[parsed.proposal_id] = parsed  # MUTANT
result: 2 failed, 16 passed
  FAILED test_spec056b_live_wiring.py::test_regression_success_serves_only_live_ids
  FAILED test_vote_service.py::TestVoteService::test_vote_proposals_list_and_detail
restore: sha256sum -c -> OK;  git status --short -> empty;  pytest -q -> 264 passed, 1 skipped
```
Two tests die, not one. **My earlier figure in the loop record said "10 of 12 fail pre-fix" via an
import fallback; that measured the collection error. The in-place mutation is the stronger evidence
and it is the one I publish.**

**Scope discipline confirmed by diff, not by prose.**
```
33aab13  3 files, 277 insertions, 13 deletions   <- exactly the allowlist
aebfafe  2 files, 314 insertions                 <- 2 test paths only
2904f21  3 files, 30 insertions, 10 deletions
2579c21  3 files, 260 insertions, 19 deletions
git diff --stat 2904f21..2579c21 -- src/ | wc -l -> 0   (the test commit touched no src/)
```
Every commit is authored `Zoltan Csaszar` — no agent identity is recoverable from git. That is a
property of this host, not a defect of the loop.

**Relocated assertions were genuinely preserved, not deleted.** The test-author removed
`len(items) >= 4` and the four fixture-id membership assertions from the *success* path and pinned
them on the *stale* path (`test_vote_service.py:163-186`, BVG `32.9`, ZH `34.8`, all four ids). The
gate's claim holds under measurement.

## NOT ESTABLISHED

- **No developer report exists for any of the four developer dispatches.**
  `ls .agent-pipeline/audit/reports/` → explore, gate, gate2, reviewer, testauthor2. **No `nw1-dev*.md`,
  and no report at either brief-named output path.** Q1, Q2, Q5 of this review are `not established`
  from the agent side by construction.
- **Q5 (unmeasured assumptions)** — the agent answered `not established` and declined to reconstruct
  intent. Correct behaviour; the answer cannot exist.
- **The agent's own cause-of-death** — `not established`. Wall times did not reach the brief budgets
  (1269 < 1500, 634 < 1200, 53 < 700), and the 81-byte banner is present on successful dispatches too.

## PROCESS FINDINGS — what about the method was wrong

### 1. A mandated role never ran: `tester` (PART 1e)
```
my loop's dispatches (nw1-* briefs):  developer 4 · reviewer 3 · test-author 2 · planner 1 · explore 1
last agent=tester row anywhere:       2026-10-05 11:04:48   — 7 hours BEFORE this loop started (18:19)
roles the method names:               explore, reviewer, planner, developer, tester, test-author
missing:                              tester
```
The verification was carried by the orchestrator (live endpoint) and `test-author` (the gate), both
real. But **the method named the role and I contracted it out silently** — the duty transferred to the
gate, which cannot say *"that test cannot fail."* It is the exact class this skill names, and the one
`grep` that catches it would have caught it before I dispatched the gate.

### 2. `developer` dies mid-task and writes nothing — 4 of 4 dispatches
```
ticket 181  wall 1269s  artifact  99B  "waiting on my refresh to resolve before I commit anything"
ticket 186  wall  634s  artifact 123B  "Now implementing."
ticket 187  wall   53s  artifact  44B  "Fixes applied - running verification now."
ticket 198  wall  995s  artifact 101B  "Committing - first the message convention check"
```
Every artifact is a real partial report, none is the stall banner, and in all four cases **the work
was already on disk**. The rule that saved this loop three times is the one that says *diff the target
files before concluding anything* — without it, three dispatches would have been re-run.

**The defect is the ordering, not the crash.** All four died *after* editing and *before* committing
or reporting. The agent proposed the fix itself (Q8): commit the smallest working slice and write the
report skeleton *before* running verification. That is a role-boundary rule and it belongs in the
agent description, not in this skill.

### 3. A brief delegated a design decision inside a build task
`nw1-brief-dev2.md` carried *"Choose the cleanest option that satisfies BOTH … prefer the additive
shape unless you can prove nesting is required"*, and one dispatch carried two items (envelope
restructure **and** ruff fixes). The agent named it as the brief to interpret (Q9) and the *"unless you
can prove"* branch was never argued anywhere — because no report was written. `dev3`, at 2549 B and
one item, was named the clearest brief and is the one whose fix landed.

### 4. False-open defect: SPEC-056b still says the re-gate is pending
```
docs/specs/SPEC-056b-live-voteinfo-ogd-wiring.md:8
| Status | IMPLEMENTED (pending re-gate: FR-02 honesty fix ...) |
```
Written by `2904f21` **before** the re-gate; the re-gate completed at `cf5c4ed` (21:00) with
**APPROVE 5.0**, and nothing closed the loop. A status file is closed in the same commit as the fix it
describes — this one was not. Consequence: the next agent reading it re-runs a gate that already
passed. **This is `honesty` + `evidence`, and it is one line.** I did not fix it: this review is
read-only.

### 5. A wrong number in my own record
The loop record says `33aab13 … +279/−13`. Measured: `3 files changed, 277 insertions(+), 13
deletions(-)`. I published 279 → **277**, corrected here. Same defect class the skill names: a number
carried forward without a command behind it in that same finding.

### 6. Evidence: reports survive, artifacts do not
7/7 reports are `IN-GIT` (`git ls-files --error-unmatch` succeeds for each). But **29 dispatch
artifacts live only in scratch**, including the four developer partial artifacts that are the *only*
evidence for finding 2. The reports that explain the work are durable; the fragments that prove how it
died are on a 72-hour lease.

## THE FIX — in the order the skill requires

**1. The brief clause (highest leverage — fixes every future run of this kind).**
`~/.hermes/cache/scratch/dispatch/nw1-brief-dev*.md`, for the next dispatch of this task type. Replace
the delegated-choice sentence with a mandated outcome plus a checkable criterion:
> The response shape is FIXED: spread the original payload's own keys at the top level and add
> `source`/`fetched_at`/`trust_state` alongside them — do NOT nest under `"proposal"`. Prove it with
> `grep -n 'return {' src/main.py` and paste the output. If you believe nesting is required, say so
> and STOP; do not choose.

And carry one item per dispatch. Measured basis: the two-item, choose-your-own-shape brief (`dev2`,
5655 B) produced a 123-byte artifact and no report; the one-item, mandated-shape brief (`dev3`,
2549 B) produced the fix that shipped. Add clause 3 to the short briefs specifically — `dev3` was the
only brief of twelve without it, and it was the shortest.

**2. The agent description (`developer`) — the ordering rule.**
`~/.claude/agents/developer.md`:
> Commit the smallest working slice and write your report skeleton to the OUTPUT path **before** you
> run verification. If your process ends mid-task, the committed work and the report must already
> exist. Measured: four dispatches on `swiss_p_map` (2026-10-05) applied their edits, died at
> 44–123 bytes, and left no report and no commit — the work was recoverable only because the
> orchestrator diffed the tree.

Also: quote no identifier in a commit message you have not greped — that rule held perfectly here and
should stay.

**3. `~/.claude/CLAUDE.md` — the universal rule.**
> A brief that asks an agent to *choose* or *judge* a design decision inside a build task has
> delegated the plan, not the work. Mandate the outcome and give a checkable command; if the decision
> is genuinely open, that is a `planner` dispatch, not a `developer` one.

**4. This skill — the two gaps the review itself hit.**
- **PART 2 should name the gate role the loop actually used.** It says dispatch `developer` **and
  `tester`**. This loop had no `tester`; it had `test-author`, which is the role its governing method
  names for the gate. As written, PART 2 would have sent me to dispatch a role the method never asked
  for. Replace with: *"dispatch the two roles that carried the work — for a next-work-loop that is
  `developer` and `test-author`; for a classic pipeline it is `developer` and `tester`."*
- **PART 1e should be run before the gate is dispatched, not during the review.** The check is one
  `grep` and it would have caught the missing `tester` while the loop could still act on it.

**5. `researcher` agent description (carried from the previous review, still open).**
A `Commands run` section and a `Not covered` section on research reports. `verdict
v20261004163958-cc7419` raised both and I closed it on the *substantive* fix; these two are method
changes it never got. Named here so they are not lost.
