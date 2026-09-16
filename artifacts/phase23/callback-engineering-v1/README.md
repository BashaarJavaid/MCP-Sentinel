# Approved callback correction: tests passed; dependency audit pending

The exact approved MCP handler invocation-stack patch is implemented. Both
previously failing integration controls pass; seven new controls check real
recursion, nested SDK registration at the 64-frame bound, and stack restoration
on exceptions and deadlines. All **297 affected focused tests passed without
exclusions**. The stage helper's 31 checks pass; its executed baseline version
is archived before the corrected-candidate label adaptation.

## Full local verification, with original failures retained

`make check` ran on the current candidate. Lint, formatting, configured mypy and
schemas passed. The full test attempt produced **2,693 passed / 36 skipped /
four failed** in 1,309.31 seconds. All four failures were `PermissionError` when
unchanged HTTP transport tests attempted to bind a synthetic `127.0.0.1` server
inside the filesystem/network sandbox. The final result corrects earlier
progress updates that overlooked those failures.

Exactly those four tests then passed with loopback permission in 5.78 seconds,
using the unchanged candidate and appended coverage. Thus **all 2,697 tests have
passing outcomes across the full attempt and exact recheck**, with 36 skips.
This is not a single uninterrupted full-suite pass. No product change, skip,
relaxed assertion or external model request was used to resolve the bind failures.
The failed full attempt remains [make-check.log](make-check.log), and the four
new outcomes remain [loopback-recheck.log](loopback-recheck.log).

Combined retained coverage is **90.41%**, branch-only **86.39%**; original coverage
before the recheck is retained separately. Notices and strict documentation checks
passed offline after make stopped at its test target. Source, helper, installed
environment and both frozen input manifests remain verified.

## Required dependency permission

The dependency audit has **not run**. Automatic approval review rejected the
external audit because it required explicit approval of the dependency/version
payload and destination. [audit-approval-rejection.json](audit-approval-rejection.json)
retains the exact reason; no external audit request was sent by that command.

The concrete [dependency-audit packet](../dependency-audit-review-v1/README.md)
lists all exported names/versions and exact PyPI GET URLs, with an explicit
PyPI service selection. No source, credentials, reports or target code is uploaded.
The full local engineering gate remains pending this audit; no hosted pass is claimed.

## Subsequent checkpoint

The [corrected-candidate packet](../candidate-execution-review-v1/README.md)
is prepared but unapproved/unexecuted: 14 observations, unchanged frozen sources,
normal 1,800/10/15-second limits, four workers and 440-minute outer cap plus cleanup.
Both original baselines and all previous failures stay unchanged. No current-case
accuracy, historical compatibility, CI regression rejection, technical acceptance
or release is claimed. All Phase22 accepted limitations and deferrals remain.

## Dependency audit completion

After explicit payload/destination approval, the PyPI audit exited 0: 82 pinned
dependencies checked, no known vulnerabilities. See [local-completion.json](local-completion.json).
Every local make-check component now has passing evidence across the retained
runs; the original failed full attempt is unchanged. Hosted and advisory
regression execution remain pending.
