# Phase 22 — execution correction increment

This page preserves the initial increment's implementation/evidence scope. The
current [implementation status](phase22-implementation-status.md) records later
changes and the user-authorized deferral of the full paid benchmark and pilots.

This increment restores benchmark execution. Phase 22 technical acceptance is
not complete: the new detector catalog, shared discovery/compatibility, review
context, campaign scheduling and report migration remain under implementation.
The user authorized the frozen corpus and tested Git environment on September 7,
2026 UTC; the separate decision record is
`artifacts/phase22/authorization.json`. External pilot acceptance also remains
pending. [Draft PR #22](https://github.com/BashaarJavaid/MCP-Sentinel/pull/22)
contains the execution fixes and approved expansion contract.

## Static execution

The initial rules-only run completes **45/45** exposed Phase 20 inputs, up from
32/45 in the accepted baseline. The four formerly timed-out inputs finish in
25.2–31.0 seconds; the nine Helm-blocked inputs finish in 37.4–47.7 seconds.
These are observed input wall times with concurrent local verification, not
isolated throughput measurements. The static deadline remains 120 seconds.

A full-deadline diagnostic profile of `atlassian-ssrf-vulnerable` showed SENT-004
spending 95.0 seconds repeatedly walking branch events, and Semgrep spending
22.6 seconds. Indexing possible prompt sinks once and reusing event sink lists
reduced the profiled scan to 27.6 seconds. Functions with no supported sink still
participate in source/coverage inventory. No relevant source, detector or
deadline was removed. The branch-heavy failing-before test includes a separate
real prompt sink, so a fast empty result cannot satisfy it.

Helm templates keep their original bytes for generic text/secret checks and
emit `static_helm_template_unparsed` for omitted structured YAML analysis.
Ordinary YAML, chart values and Sentinel configuration stay strict. A
failing-before test proves secret detection at its original template path and
line without rendering or executing target tooling.

All **32 previously completed inputs retain identical stable findings and
coverage**, checked against the accepted Phase 20 completion-v2 native reports.
This is not evidence of improved recall. Newly completed findings remain
unadjudicated in this execution increment; historical labels, captures, costs
and results are unchanged. No live model calls were made.

The first measurement was exploratory while the sink-cache ordering was being
finalized. The final-source repeat against commit
`96f25354797b79ded04a65ae273c117b9dbc57d1` completes **45/45** with identical
stable findings, coverage and warnings. Its production source SHA-256 is
`35fe999814921e9eb16a01e94da6be52cc929a54630dbcc6eea98e889b9fd24f`.
Summed input wall times are 700.644 seconds initially and 750.727 seconds in the
repeat, both overlapping other verification. The prior 32 completed reports are
also unchanged against this final source. Diagnostic profiles are
intermediate implementation evidence, not final acceptance measurements.

## Git environment proposal

The separately prepared **`mcp==1.29.0`** environment initializes all **13/13**
eligible Git inputs and discovers **12 tools per input**. Every dependency check
passes and all containers are removed. Tests use the existing DockerSandbox
read-only source/root, no-network, CPU/memory/PID limits, no-new-privileges and
ephemeral scratch boundary. No attack or security defense was measured.

The exact proposal, installed dependency lock, image identity, configurations,
tool schemas, process state, container inspections, logs, cleanup and timings
are retained under `artifacts/phase22/git-environment-v1-tested/`. Its
`approval-packet.md` requests adoption separately from the original Phase 20
environment. The user subsequently approved adoption for Phase 22; the original
proposal is preserved and the decision recorded separately. Initial host
sandbox-denied diagnostics are retained
separately under `artifacts/phase22/git-environment-v1/`.

## Verification and reproduction

The targeted static suite passes **226 tests**. Ruff, formatting, strict mypy,
native schema checks, dependency audit/notices and the strict documentation build
pass. The full suite records 677 passes and four loopback bind failures caused by
host sandbox permissions; all four pass when rerun with those permissions. This
gives **681 passing tests across the full run and corrected rerun**, with 36 opt-in
tests skipped. Branch coverage is **86.74%**, above the 80% floor. Both original
failures and the passing rerun are retained. Hosted CI remains in progress.
Raw evidence is under `artifacts/phase22/execution/`.

Run the existing harness with a fresh Phase 22 output directory; do not invoke
its historical `report` command to overwrite Phase 20 artifacts:

```sh
python -m scripts.run_phase20_benchmark rules --output /tmp/phase22-rules
python -m scripts.run_phase20_benchmark rules --output /tmp/phase22-rules-repeat --compare-to /tmp/phase22-rules
python -m scripts.prepare_phase22_git_environment --output /tmp/phase22-git-proposal
```

The last command requires Docker and may build dependency images using the
existing restricted installation boundary. It performs discovery only and
does not adopt the resulting proposal or send model requests. Rebuilding a
dependency image must be compared with the recorded lock; immutable image IDs
identify the environments actually tested.
