ROLE: explore. ONE narrow question. Read-only — do not modify, do not commit, do not decide.

REPO: /home/zoltan/swiss_p_map @ HEAD adc0093 (clean tree, 1 commit ahead of origin).
State: backend pytest 250 passed / 1 skipped. Frontend Next.js 14 + Three.js 3D map.
Deliberately not shipped: nothing; the last commit was a research report only.

THE QUESTION
What is the highest-value NEXT change in this repository, and what is the evidence?

Work item numbered list — answer EVERY item. If an item's answer is NO or "nothing", say NO
explicitly and name what you checked to establish it. An unexamined NO is not an answer.

1. Name the single highest-value next change. One item, not a survey.
2. Give the file:line evidence that the problem exists TODAY. Paste the command you ran and its
   real output. If you did not run a command, answer "not established" for this item.
3. Is it already done? Check `git log --oneline -50` and the docs/ tree for a spec or report
   covering it. Name what you grepped. If it is already done, say so and name the commit.
4. Does production actually reach the code involved? Run, and paste output:
   grep -rn '<symbol>(' src/ --include=*.py | grep -v 'def <symbol>'
   and the frontend equivalent if the change is in frontend/. Zero callers means the item is a
   WIRING slice, not a testing slice — say which one this is.
5. What is the cheapest possible slice of it that a single agent could finish in one dispatch?
6. What would prove it is done? Give the exact command and the exact output you would expect.
7. What could make this FAIL or be the wrong choice? Name the risk you cannot rule out.

BUDGET: 900 seconds of wall clock. If you run out, say "BUDGET EXHAUSTED after item N" and stop —
a partial answer labelled partial is worth more than a guess.

TARGET FILES: none. This is a read-only question. Do NOT decide the product direction; do NOT
write a spec; do NOT start implementing. Your answer is input to an orchestrator that verifies it.

OUTPUT
Write your report to BOTH destinations, so it survives the temp cleanup:
  (a) /home/zoltan/.hermes/cache/scratch/dispatch/nw1-explore.md
  (b) /home/zoltan/swiss_p_map/.agent-pipeline/audit/reports/nw1-explore.md
Do NOT commit. The orchestrator commits after verifying.

ACCEPTANCE: items 1-7 each individually answered; every factual claim carries a command and its
output; any item you could not establish is marked "not established" rather than inferred.
Also print, as your final message, the one-line answer to item 1 only.