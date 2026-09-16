# Phase 23 technical review

**Decision requested:** accept the delivered technical result and source-support
judgments, retaining the current FAF timeout as a failed observation and current
FAF detection/support/repeat compatibility as **unestablished**. Keep the five
unstarted FAF observations closed and recovery/optimization deferred. This is an
explicit limitation proposal, not a passed complete historical gate.

The exact decision and evidence bindings are in `proposal.json`. It also retains
all earlier failures, unrelated finding dispositions and Phase 22 limitations.
This checkpoint grants no release version, push, merge, tag, publication or alias
action. Phase 23 remains open until the separately reviewed release is verified.

## Delivered engineering

The candidate fixes source-established TypeScript star exports, immutable
promisify(exec/execFile) wrappers, independent registered-handler invocation stacks,
and proved Zod description/extension/shape metadata. It retains ambiguity,
mutation/escape, recursion and source-root boundaries. Public Finding/report
interfaces and existing rule meanings remain unchanged. There is one bounded
regression helper, existing pytest tooling, and no new dependency/service.

Scanner SHA-256:
`2fa09818900817337863f90c41b71ab6d9e27458f11b8b1d80e1b882682c051d`.
The hosted draft revision is `4bc28d050bdbfcbf675bb0cf0c77c82f855acd7f`;
tested merge `2fa81d05107c6cc4b5b5367d18b4510fdcbbe843` has the same tree.
PR #40 remains draft. Later continuation evidence and changelog preparation have
not been pushed; source identity is unchanged.

| Verification | Result and retained evidence |
| --- | --- |
| Full local engineering | `windows-review-v1/local-checks.json`: 2,766 passed / 36 skips; 90.52% combined / 86.58% branch coverage; required checks passed. |
| Full hosted gates | `hosted-verification-v3/summary.json`: all 30 normal CI jobs and documentation passed. Eight Linux/macOS suites: 2,766 / 36. Four Windows suites: 2,744 / 58. Packaging, replay, isolation and dependency gates retained. |
| Reviewed advisory | `candidate-assessment-v2/`: GHSA-3q26-f695-pp76, 14 complete reports / seven equal pairs, six vulnerable detections and eight source-supported negatives. 56 unrelated findings remain `needs_review`; exploitability is unestablished. |
| Actual offline CI | Seven current-candidate reports in Linux network isolation equal the reviewed references: three vulnerable detections and four supported negatives. Full JSON/SARIF and source/configuration hashes retained. |
| Deliberate regression rejection | `regression-rejection-v1/verification.json`: one completed minimized vulnerable observation, reversing only the approved promisify block in a disposable checkout. The actual CI assertion rejects it: `CI source-matched shell condition failed`. Patch, report, failed assertion and verified cleanup retained. |
| Original advisory compatibility | `compatibility-advisory-assessment-v1/summary.json`: 14 reports / seven equal pairs; six vulnerable detections / eight supported negatives. All findings and coverage unchanged; all 68 added warning occurrences assessed. |
| Historical non-FAF compatibility | `compatibility-non-faf-assessment-v1/summary.json`: 106 reports / 53 equal pairs, including 23 explicitly retained first reports. 42 vulnerable observations / 64 qualified supported negatives. Every report validates; cleanup passed. |
| FAF | `compatibility-v3/assessment.json`: vulnerable input timed out after 1,800.011759 seconds; no native report. Cleanup completed within 3.943 additional seconds. Five unstarted observations closed, zero remaining budget. Current detection/support/repeat compatibility is unestablished. |
| Contribution guidance | Separate false-positive, missed-vulnerability and rule-proposal forms; current SENT-001–016 catalog; reproducible evidence, reporter/reviewer distinction, required sanitization, optional MIT reuse consent and source-rights checks; private/upstream routing, AI-draft review and no automatic promotion. |
| Maintenance | Manual Monday 09:00 America/Los_Angeles review; next record is 2026-09-21. No scheduled review is claimed completed and no response-time promise is added. Lifecycle records distinguish advisory publication from actual intake/triage/fix/review/publication, leaving unknown times unknown. |

## Changed historical diagnostics and support

All 742 findings and 1,856 registration surfaces across the 106 non-FAF reports
are unchanged from their historical references. Both repeats include 91,458
warnings and 49,314 unresolved-flow occurrences. No occurrence is hidden.

The first-pass source assessment records 1,214 added warnings, 50 removed warnings,
1,760 added unresolved-flow occurrences and 30 removed flow occurrences. These
counts double across the equal repeats. Complete ordered diffs and every changed
occurrence are in `compatibility-first53-assessment-v1/`; the narrow source-support
judgments and accepted-reference bindings are in `compatibility-support-review-v1/`.

Mobile's added warnings concern unproved Zod metadata. The selected case is
output-path containment: handler argument taint is seeded independently of schema
metadata and the fixed output guard still precedes the sink. Its Linux,
valid-extension, ordinary-parent and toolchain prerequisites remain. No schema,
physical-containment or executable-integrity assurance is inferred. Calculator's
removed SDK diagnostics concern actual callback registrations, not a new sanitizer.
Kubernetes's removed catalog warnings follow local exported type/schema definitions;
its shell findings and protections are unchanged. All other binding warnings stay
unknown with their source contexts retained.

Taskwarrior and no-bash preserve entire accepted source-bound reports. Their narrow
conditions are assessed separately from raw provisional null gate fields, which
remain unchanged. Unresolved dispatch, unrelated findings, lexical/physical
qualifications and historical source limitations remain visible.

## Failures retained

- The first selected advisory already passed its baseline. No detector change was
  manufactured; the user approved selecting the replacement case. Both frozen
  seven-input sets and licenses remain intact. They are correlated examples of
  their respective advisory, not seven independent vulnerabilities.
- The replacement baseline missed all six vulnerable observations and left all
  eight negatives unsupported. The first corrected full-source candidate still
  failed; the reviewed metadata correction produced the accepted narrow gate.
- Hosted attempt one failed lint and artifact upload; its raw reports are unavailable.
  Hosted attempt two failed four Windows type checks. Successful later evidence
  does not replace either failed run.
- Historical launch one failed its sandboxed hardware preflight before any scan:
  112 unstarted slots closed. The separately approved replacement completed 23
  evaluations, then failed calculator scoring metadata; one incomplete evaluation
  retained a complete native report, and 88 unstarted slots closed.
- The current separately approved packet copies five exact accepted calculator
  assessment maps, reuses only the 23 completed first reports as repeat references,
  and starts the failed calculator input again. It changes no label, matching key,
  source, detector, scan limit or historical raw result.
- The current FAF vulnerable observation timed out under the unchanged normal
  deadline, with no report. The stage stopped: 83 new evaluations completed,
  23 first reports were retained, one was incomplete and five were closed unstarted.
  All input and outer cleanup checks passed. The 106 non-FAF reports form 53
  equal pairs; the complete 56-pair historical gate did not pass. Phase 22's
  original failures and uncapped measurements remain bound to their actual sources.
  This proposal asks to retain the new limitation; it is not yet accepted.

## Boundaries and remaining release work

Phase 22's accepted v93 closeout, 493-row audit, 30 accepted limitations, Proxmox
unsupported status and deferred recovery remain unchanged. FAF optimization and
V68, pilots, paid benchmark and Git's deferred measurements remain outside scope.
Phase 21 is incomplete; Phase 24/15 gates remain unchanged. Zero new paid calls
and zero advisory-target executions occurred.

Technical acceptance is a separate checkpoint from release approval. The prepared
`release-inventory-v1/` includes all applicable accepted main changes since 1.3.0:
Phase 19 schema/coverage, Phase 20 execution corrections, five Phase 22 rule
additions and bounded flow support, plus Phase 23 maintenance/regression work.
The Unreleased notes now include the five rules and correct the stale Phase 19
pending-acceptance sentence. Strict documentation passes. The release inventory
retains its preparation-time status; the final FAF outcome is recorded here and
in `compatibility-v3/assessment.json`.

The maintainer must still choose the release version and approve exact contents,
revision and required merge/tag/publication actions. After that, the existing
signed-tag → TestPyPI → PyPI/provenance path, GitHub assets, exact Action pin and
compatible `v1` alias must be verified, followed by a released-detector regression
and explicit final acceptance. **Phase 23 is not closed by this technical review.**
