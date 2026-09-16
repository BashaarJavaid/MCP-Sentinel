# Phase 23 — historical execution replacement review

**Hosted verification, original-advisory compatibility and deliberate regression
rejection passed. The historical launcher failed before its first observation.**
This packet requests one replacement historical attempt only.

## Completed evidence

- Draft revision `4bc28d050bdbfcbf675bb0cf0c77c82f855acd7f` passed
  [CI 35026207558](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/35026207558)
  and [documentation](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/35026207535).
  All30 normal CI jobs passed; four optional historical jobs skipped. All eight
  Linux/macOS suites passed 2,766 tests / 36 skips; all four Windows suites passed 2,744 tests / 58 skips.
  The tested merge tree equals the approved tree. Both earlier failed attempts
  remain failed. [Complete hosted evidence](../hosted-verification-v3/summary.json).
- Seven network-isolated advisory reports match the reviewed references:
  three vulnerable detections/four supported negatives, 31 findings / 4,377 warnings.
  Their native JSON and canonical offline SARIF validate. Wheel/sdist match all 134
  scanner files; 20 bundled wheel schema/fixture files also match.
- Original-advisory compatibility completed 14 observations in 85.32034 seconds,
  with 7 equal complete ordered pairs, 6 detections / 8 supported negatives.
  All 22 findings and complete static coverage are unchanged. Full-source reports
  add 17 unresolved warnings each, 68 occurrences across both passes, concerning
  other schemas, JSON metadata, container bookkeeping and test variables.
  [Every change and its source assessment](../compatibility-advisory-assessment-v1/summary.json)
  is retained. Sixteen unrelated finding occurrences remain `needs_review`.
- [The one deliberate regression](../regression-rejection-v1/verification.json)
  completed in 4.519437 seconds after reversing only the approved promisify factory
  block in a disposable checkout. The real CI assertion raised
  `ValueError: CI source-matched shell condition failed`. JSON/SARIF and cleanup
  passed; the permanent scanner is unchanged. This is one additional observation.

These results establish no release or final human technical acceptance.

## Failed launch and cause

The historical launcher was mistakenly started inside the restricted sandbox.
Its existing read-only `sysctl hw.ncpu hw.memsize` query failed with
`Operation not permitted`, before packet construction, synthetic supervisor checks,
budget-consumption receipt or any scanner observation. The outer supervisor
verified cleanup after 1.160527 seconds. **Zero observations started; all 112 slots
are closed unstarted.** The missing consumption receipt does not leave reusable
approval. [Exact failed launch](failed-launch.json) and
[unchanged raw execution](../compatibility-v1/execution.json) remain retained.

The same read-only hardware query and process inspection succeed outside the
sandbox. The existing supervisor's inert-process checks also pass there. No
detector change, timeout adjustment or further corpus scan was needed to diagnose
the launch failure.

## Exact proposed replacement

[execution-proposal.json](execution-proposal.json), SHA-256:

`d9633bb730ad73ccf0a73030405821de142a47e9aeced6266f3ef8ce04a09315`

```sh
.venv/bin/python -I artifacts/phase23/compatibility-recovery-review-v1/launch.py
```

Run through `exec_command` with `sandbox_permissions=require_escalated` so the
existing hardware/process inspection and process-group supervision can operate.
The scanner remains rules-only with model transport forbidden; advisory source
is never installed, imported or executed.

The copied existing runners change only proposal, approval, binding and output
paths. Their ASTs equal the previous runners after reversing those filename
changes. Source/hash checks, missing-approval rejection, inert supervision,
lint and formatting pass; [checks.json](checks.json) binds the evidence.
The new approval is `authorization.json`; output is `../compatibility-v2/`.
Original packets, approval and failed output remain untouched.

Exactly 56 existing inputs / 112 observations / 56 complete ordered pairs, with the
same reviewed labels, configurations, 11 historical exclusions and source support
requirements. First 53 inputs then their repeats; FAF vulnerable/fixed/safe and
their repeats last. Limits remain 1,800 seconds/input, 10 seconds Semgrep, 15 seconds
cleanup, maximum 4 workers, one input at a time, 3,520 minutes outer plus 15 seconds
cleanup. The outer cap is a worst-case bound, not an estimate. No retry or extension.
An incomplete result or failed cleanup/repeat closes the remaining budget.
Historical FAF completion under normal 1,800-second limits remains unestablished.

## Required decision

Approve the exact replacement 112-observation attempt above. The original approved
plan requires: **“Any unexpected gate failure or incomplete stage stops later
stages for review; no automatic retry or deadline extension.”** This launch failed,
so the replacement remains unexecuted pending that decision.

No new hosted run, push, merge, ready-state change, version/tag/publication, Action
alias, paid call, target execution, Proxmox recovery, FAF optimization, pilot or
deferred benchmark is included. Phase 22 accepted closeout and Phase 24/15 stay intact.
