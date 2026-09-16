# Review the CI reference reports

Approve [proposal.json](proposal.json), SHA-256 **`a953a9fab75e8054853ffecae868891b0de720078230509fd0214e1fda8b9d49`**.

The [candidate assessment](../candidate-assessment-v2/README.md) reports a narrow
shell gate pass: six vulnerable detections, eight supported negatives and seven
equal ordered pairs. Review its source-support judgments and all 62 findings.
Retain the 56 unrelated findings as `needs_review`, with exploitability unestablished.

Seven exact complete [reference reports](reports/) are bound by hash. Routine CI
will scan the current candidate once per input and compare every nonvolatile field
and array order. Use only the existing eight clock/UUID exclusions. Additionally,
set the expected `sentinel_version` to the installed candidate version and require
the actual value to match; this permits a reviewed release version change without
silently ignoring scanner-version errors. Historical repeat exclusions stay unchanged.
Any finding, warning, support, stage, schema or ordering drift fails for review.

The code will reuse the bounded helper and existing Linux network isolation after
dependency installation. Seven observations once, 1,800/10/15-second limits,
four-worker maximum, 220-minute outer cap plus active cleanup; no retries,
credentials, live feeds, target execution or new dependency.

This checkpoint approves the source judgments and adoption of the exact CI
references and comparison rule. It does not approve final technical acceptance,
historical or deliberate-regression observations, hosted publication or a release.
