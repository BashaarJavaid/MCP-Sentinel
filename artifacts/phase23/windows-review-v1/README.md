# Windows supervision typing and frozen-byte checkout correction

The second hosted attempt at `f42df80` passed the seven-input isolated regression
and retained its complete evidence. All seven native/SARIF reports validate and
agree with the human-reviewed complete reference reports: three vulnerable
matches, four supported negatives, 31 findings and 4,377 warnings. The measured
stage took 91.592541 seconds. This is the same correlated advisory case, not seven
new vulnerabilities. The first attempt's missing reports remain missing.

The four Windows quality jobs stopped at **24 type errors** before their tests.
The type checker evaluates POSIX-only signal/process APIs in helper bodies even
though normal execution is POSIX-only. A pytest skip decorator also does not hide
the test body from type checking. Original failures are retained under
`../hosted-verification-v2/`; all 127 local observations remain unstarted.

## Correction

- Five explicit Windows rejection guards protect the POSIX supervision functions.
  Portable source validators and report comparisons remain available on Windows.
- The existing POSIX-only synthetic test has an explicit body guard, and one new
  test checks all five rejected paths leave no output or consumed approval.
- `/tests/evals/phase23/** -text` extends the existing frozen-byte checkout policy.
  A forced-CRLF checkout reproduced source-byte drift before this change and
  preserves every one of the 56 corpus files afterward. This is a separate
  reproduced checkout condition, not a claim about the failed hosted jobs' Git
  settings; those jobs stopped at type checking.
- Separate revised proposal/approval/binding filenames retain all earlier packets
  and bind the exact current helper/test bytes. Counts, source bytes, reviewed
  conditions, ordering, comparison exclusions and resource limits are unchanged.

`semantic-verification.json` proves the POSIX helper syntax tree is identical after
removing only the five new Windows guards. No detector or public report contract,
dependency, timeout, retry policy or lint/type gate is changed. Windows-targeted
mypy passes all 154 configured files. All 49 focused checks pass. Full local `make check` passed **2,766 tests /
36 skips** in 1,327.48 seconds of pytest time, with **90.52% combined / 86.58%
branch coverage**. Lint, format, typing, schemas, audit, notices and strict docs
pass. This is a local check, not a new native Windows hosted pass.

## Execution boundary

No automatic retry or local corpus observation occurred. A separate exact
execution proposal will bind the finished local correction commit, one new full
hosted attempt, and the same 14 + 1 + 112 local observations only if all hosted
gates pass. Any unexpected failure stops subsequent stages for review. Final
technical acceptance, merge/ready-state changes, release version/publication,
paid calls and advisory-target execution remain outside that approval.
