# Phase 23 — remaining historical observations review

**23 evaluations completed; the next evaluation failed on stale scoring metadata.**
The sequence stopped, cleanup passed, and all remaining budget closed.
This packet proposes the exact remaining 89 observations using the 23 completed
first reports as repeat references.

## Retained failure and reports

The approved historical attempt ran for 808.998028 seconds inside the supervisor
(810.378468 seconds including outer launch work). It completed 23 evaluations,
then calculator observation 24 produced a complete scan report but failed with
`ValueError: adjudication candidate identity drift`. There are **23 completed
evaluations, one incomplete evaluation, 88 unstarted closed and zero repeat pairs**.
The incomplete evaluation remains failed; its report is evidence, not a passed slot.

[The partial assessment](../compatibility-partial-assessment-v1/summary.json)
verifies all **24 native JSON and canonical offline SARIF reports**, their scanner,
source/configuration bindings and cleanup. All **139 ordered findings and 550
registration surfaces** match the frozen historical references. Reports retain
27,165 warnings and 13,440 unresolved-flow occurrences; these counts overlap.

The first 23 reports add 235 unresolved-binding warning occurrences across
memory-keeper, SearXNG, Fetch MCP and Open WebSearch. No protection is inferred from
those unknown values. Their complete findings and coverage remain unchanged.
Five Lighthouse reports equal their entire references under the existing exclusions.
The calculator report removes six SDK-receiver warnings and the corresponding six
coverage occurrences at `src/server.ts:71,92,142,153,176,186`. These source locations
are SDK request-handler registrations. No sanitizer or broader safety claim follows
from those removals; the selected metadata condition and all findings are unchanged.
Every diagnostic change, ordered diff and 28 deduplicated source contexts is retained.

## Root cause and exact correction

The prepared proposal combined **v21 calculator candidate identities** with **v75
reference reports**. Those newer reports include two additional, separately
source-assessed findings outside the calculator metadata condition: shell execution
at `src/tools/command-executor.ts:37` and file access at
`src/tools/file-reader.ts:48`. The scorer correctly rejected the stale identity.

The accepted Phase 22
[v75 assessment](../../phase22/integration/v75-prior-language-results/ts-development-assessment/assessment.json)
already contains the correct map for each of the five calculator inputs.
[assessment-binding-corrections.json](assessment-binding-corrections.json) copies
those exact maps, with their report hashes and unchanged selected matching keys.
No label, finding disposition, detector, historical validator or raw measurement
changes. The original failed proposal and evaluation remain intact.

All **39 records with scoring assessments** have been audited against their actual
reference finding sets. Only the five calculator bindings were stale. The other
17 inputs retain their separately reviewed source-condition handling.

## Proposed execution

[execution-proposal.json](execution-proposal.json), SHA-256:

`5bfba4ea113adc0380636c6fadc395075220586a72e000f01f276e1d292b63de`

```sh
.venv/bin/python -I artifacts/phase23/compatibility-metadata-review-v1/launch.py
```

Run through `exec_command` with `sandbox_permissions=require_escalated`, as in the
previous approved attempt, for the existing hardware/process inspection and
supervisor. Rules-only scanning and the forbidden model transport remain unchanged.
No advisory code is installed, imported or executed.

- **Retain 23 completed first passes**, with exact report hashes checked before
  launch. Their scanner/source/configuration identities and actual timings remain
  attached to the old run. Reuse does not rewrite its failed overall result.
- **Run the remaining 89 observations**, beginning with the calculator input whose
  previous evaluation failed. The order is the exact old schedule after its first
  23 entries. This supplies the remaining 33 first passes and all 56 repeats.
- Seed the existing ordered comparator with those 23 reports. If complete, the
  retained 23 plus new 89 form **56 entire ordered pairs across 56 inputs**.
  A mismatch still stops execution. No finding or diagnostic exclusion is added.
- Write to `../compatibility-v3/`, using a separate `authorization.json` and
  one-use consumption receipt. All previous approvals and outputs stay untouched.

Limits remain **1,800 seconds per input, 10 seconds Semgrep, 15 seconds cleanup,
maximum four workers and one input at a time**. The existing 3,520-minute outer cap
plus 15-second cleanup is unchanged; it is a worst-case bound, not an estimate.
FAF's six observations remain last, with no deadline exception or optimization.
An incomplete input, cleanup failure or complete ordered-repeat mismatch closes
all remaining budget. No automatic retry.

## Verification and approval

[checks.json](checks.json) binds source/proposal validation, all 39 scoring checks,
the missing-approval boundary, lint and formatting. [check.py](check.py) executes
the actual runner's seed assignment without launching it: 23 retained reports plus
the unchanged remaining order form 56 pairs. It rejects synthetic diagnostic drift
and a retained-report hash change. These checks run **zero corpus observations**.

Approve the five exact accepted assessment bindings, retention of the 23 completed
first reports and one 89-observation execution attempt above. The previously
approved policy requires a review after an unexpected incomplete stage; it does
not authorize an automatic retry. This proposal remains unexecuted.

All 30 hosted CI jobs and documentation, all 12 platform suites, 14 original-advisory
compatibility observations and the deliberate regression-rejection proof remain
passed at the unchanged scanner source. Earlier failures remain retained.
No new hosted run, push, merge, ready-state change, version/tag/publication, Action
alias, paid call, target execution, Proxmox recovery, FAF optimization, pilot or
deferred benchmark is included. Final human technical acceptance and the reviewed
release remain pending; Phase 22 acceptance and Phase 24/15 remain unchanged.
