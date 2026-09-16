# Hosted failure and correction review

Draft [PR #40](https://github.com/BashaarJavaid/MCP-Sentinel/pull/40) delivered
`f015c005` at the approved source tree. Its original CI run failed: **17 jobs
passed, 13 failed, four optional jobs skipped**. Documentation passed.

## Retained failures

All 12 quality jobs stopped at the same **89 lint errors in four review scripts**,
before their test suites. The earlier local lint pass did not cover the final
script bytes; the same failure was reproduced locally. The original local test
suite remains evidence for its actual tested files, not a hosted platform pass.

The seven-input isolated scan step succeeded, but root-owned mode-0600 atomic JSON
files caused artifact upload to fail with EACCES. **No Phase23 report artifact was
retained.** A successful step exit does not replace those missing reports. The
job remains failed; no findings, support judgments or raw timings are inferred
from missing output. The 127 local observations never started. No retry occurred.

[Original evidence](../hosted-verification-v1/summary.json) retains all completed
job logs, exact head/merge/tree bindings and four hash-verified available archives.

## Local correction

[Exact patch](implemented-correction.patch):

- Format the four scripts; remove three unused imports. Imports after the explicit
  isolated-interpreter source-path bootstrap carry narrowly scoped E402 comments.
- Correct the launch receipt's count from 111 to the already-approved 112. Actual
  schedule, enforcement, inputs and budget are unchanged.
- Add one `always()` workflow step that restores ownership of the known regression
  output directory to the runner before upload. Private file modes stay unchanged.
- Select separate revised proposal/authorization/binding filenames. Original
  approved JSON packets remain byte-for-byte unchanged. Original runner bytes are
  retained here as `*.before.txt` and in immutable commit `f015c005`.

The detector, bounded Phase23 helper, tests, dependencies, reviewed references,
matching rules, support judgments, exclusions and time/resource limits are
unchanged. No lint gate or report comparison is weakened.

[Local checks](local-checks.json): repository lint and formatting pass; all 48
helper tests pass; both missing-approval boundaries reject execution; all 56
historical source/configuration bindings validate; strict docs and diff checks
pass. A synthetic network-disabled Ubuntu container reproduced the unreadable
private file and verified ownership recovery, mode retention and absent-output
handling. It ran no scanner or target code. Original full-suite evidence retains
its 2,765/36 result and final portability qualification; this correction does not
claim another full suite or hosted pass.

## Next approval

The accompanying `execution-proposal.json` binds the exact local correction commit,
creation-independent fast-forward push, PR description and revised execution
packets. It requests **one new normal CI/docs attempt**, with seven routine
Phase23 observations, then the same **14 + 1 + 112 local observations** only after
all hosted gates pass. Original failure stays failed. Any new unexpected failure
stops later stages for review. No automatic retry, deadline extension, merge,
ready-state change, release, paid call or target execution is included.
