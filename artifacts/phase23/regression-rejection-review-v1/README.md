# Deliberate regression rejection — execution review

Prepared, not approved or executed: **one additional observation**, on the
originally missed `minimized-vulnerable` input of GHSA-3q26-f695-pp76.
[proposal.json](proposal.json) binds exact current identities and the command;
the final checkpoint index binds its hash after local engineering completes.

```bash
.venv/bin/python -I artifacts/phase23/regression-rejection-review-v1/run.py
```

## Exact source change and proof

[reverse-fix.patch](reverse-fix.patch) removes only the approved
`util.promisify` factory-result binding block from
`src/sentinel/static/typescript_path_flow.py`. Export resolution, callback and Zod
metadata fixes remain. Start from a disposable archive checkout, overlay the exact
current candidate source, require identical scanner trees, and then verify that
this one file is the only change. Keep the permanent workspace untouched.

The existing bounded `_observe` helper runs the production CLI. Its interpreter
bootstrap inserts only the disposable scanner checkout and asserts the actual
scanner import path before invoking the CLI. It uses the existing installed
dependencies; no target package is installed, imported or executed. Retain the
actual command, candidate/reversed source hashes, complete JSON and offline SARIF,
configuration, diagnostics, timings and cleanup evidence.

The observation must complete and miss the selected source condition, causing the
same routine-CI assertion to raise `CI source-matched shell condition failed`.
Retain that failed assertion. A timeout, incomplete report, different error or
cleanup failure does not establish rejection. No automatic retry.

Limits: 1,800-second input, 10-second Semgrep, 15-second cleanup, maximum four
workers, 35-minute outer cap plus 15 seconds outer cleanup. Dispose of the scanner
checkout after the attempt; retain the patch and outputs. Zero paid calls.

## Preparation checks are not the observation

The missing-approval boundary is checked before checkout/output/budget changes.
Synthetic orchestration checks inject a retained baseline report instead of
starting a scanner. They verify reverse-only copying, the failed assertion,
cleanup, and rejection of incomplete/cleanup-failed outcomes. See
[synthetic-supervision.json](synthetic-supervision.json) and
[failure-controls.json](failure-controls.json). They establish zero new native
observations; the actual deliberate-regression proof remains pending.
