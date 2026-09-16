# Maintained feedback and regression releases

BashaarJavaid owns maintenance, source labels, detector review, publication
approval, and final technical acceptance. Phase 23 uses a public advisory and
offline static analysis. Pilots remain deferred; Phase 21 is incomplete and
Phase 24 adoption and Phase 15 launch gates are unchanged. Phase 22's accepted
closeout and all historical failures remain intact. Proxmox recovery, FAF
optimization, and deferred benchmarks are outside this work.

## Submit reproducible feedback

Use separate [false-positive, missed-vulnerability, and rule-proposal
forms](https://github.com/BashaarJavaid/MCP-Sentinel/issues/new/choose).
Include the Sentinel version or commit, language/SDK versions, exact command,
sanitized configuration (including rule selection, ignores, baselines and
suppressions), complete sanitized JSON/SARIF diagnostics, source revision and
paths, and minimal vulnerable/fixed examples when available. State what you
expect and why; reporter expectations are proposals until reviewed.

Remove secrets, personal data, internal endpoints, and private source from
public submissions. Report sensitive Sentinel vulnerabilities through the
existing [private security advisory
channel](https://github.com/BashaarJavaid/MCP-Sentinel/security/advisories/new).
Report third-party vulnerabilities through that project's security policy;
do not disclose an unpatched upstream issue in a public Sentinel issue.

Example reuse consent is separate and optional. Public submission alone is not
permission to incorporate source into the corpus. Retain the applicable license
and attribution, or obtain permission before incorporation. Without either,
request a shareable replacement or leave the example outside the corpus.
Never upload private repositories to a model or external analysis service.

## From report to release

1. Record intake separately from advisory publication. Triage the evidence,
   disclosure route, source rights, supported scope and reporter expectation.
2. Trace the registration-to-sink path by source inspection. Prepare exact
   vulnerable/fixed snapshots, minimized cases and controls with source hashes.
   Review labels, matching conditions, mutations, ordering and manifest before
   freezing or scanning. Static analysis never imports or executes target code.
3. Obtain approval for exact baseline commands, scanner/configuration identities,
   exclusions and execution bounds. Preserve complete reports and failures.
   If the baseline passes, retain it and request another candidate; do not
   manufacture a detector change.
4. For a failed gate, trace the root cause and affected callers. Review the
   smallest proposed fix, compatibility implications, tests and exact historical
   regression list before implementation. Contract expansion requires a decision.
5. After approval, implement the correction, run approved evaluations, and retain
   all findings, diagnostics, support judgments, timings and repeat differences.
   Unknown support, incomplete analysis and timeouts cannot pass negative gates.
6. Retain the accepted case in offline CI against the current candidate. Run it
   once per routine PR/release run after dependency installation, inside the
   existing Linux network isolation boundary. Keep the full platform matrix,
   package, replay, isolation, documentation and dependency checks. Prove rejection
   by reversing only the approved fix in a disposable checkout and rerunning one
   originally failing input. Retain the patch, report and failed assertion.
7. Obtain human review of the results and every changed finding/support judgment.
   AI-assisted test and rule drafts receive the same review; neither generated
   rules nor reporter labels are promoted automatically. Offline rules change
   only through reviewed, versioned releases, without a live rule feed.
8. Prepare and approve the exact release contents and version, then publish and
   verify through the existing release path. Final acceptance follows verified
   release evidence and delivered contribution guidance.

The first case, [GHSA-5w57-2ccq-8w95](https://github.com/alfonsograziano/node-code-sandbox-mcp/security/advisories/GHSA-5w57-2ccq-8w95),
covered `sandbox_stop.container_id` shell injection. Its approved baseline already
passed by source assessment, so it remains a compatibility control.
The approved replacement is [GHSA-3q26-f695-pp76](https://github.com/cyanheads/git-mcp-server/security/advisories/GHSA-3q26-f695-pp76),
bounded to `git_init.initialBranch` shell injection through promisified execution.
Its baseline missed all three vulnerable inputs and left all four negatives
unsupported. The approved corrections, callback boundary and composed Zod
metadata support now pass the reviewed narrow shell gate: six vulnerable
detections, eight supported negative observations and seven equal ordered pairs.
The 56 unrelated findings remain `needs_review`; their exploitability is
unestablished. Each case has seven correlated
inputs: full vulnerable/fixed revisions, minimized vulnerable/fixed reproductions,
a safe literal-command control, and identifier-renamed vulnerable/fixed
reproductions. Report these groups separately; they are one advisory per case.

### Current-candidate CI gate

The `Phase 23 current-candidate regression` job runs the seven replacement-case
inputs once in a Linux network namespace after locked dependency installation.
The release workflow invokes the same CI workflow. The helper command is
`python -m scripts.phase23_regression ci --output <new-evidence-directory>`.
It requires the explicit reference approval, verifies frozen source and report
hashes, and retains complete JSON, offline-validated SARIF, diagnostics and timing.

Every nonvolatile field and array order must match the human-reviewed reference
report, including unresolved warnings and unrelated findings. Only the existing
eight clock/UUID exclusions apply. The expected scanner version is set to the
installed candidate version; the actual report must match it. This approved CI
version rule does not change historical repeat comparisons. Any other drift
fails for review; the helper never updates its own expected reports.

The usual 1,800-second input, 10-second Semgrep, 15-second cleanup and four-worker
limits apply, with a 220-minute outer cap plus active cleanup. An incomplete
observation or changed report closes remaining slots without retry. Complete
reference equality preserves the reviewed source-support judgment; recognizing
a handler or producing an empty report alone cannot pass a negative input.

Baseline and corrected-candidate packets each propose seven inputs twice,
14 observations, with 1,800 seconds per input, 10 seconds for Semgrep,
15 seconds cleanup and at most four workers. Exact commands and outer caps
require separate approval; there are no automatic retries or timeout extensions.
The case gate requires source-matched SENT-002 findings on all three vulnerable
inputs, no matching shell-injection finding with established support on all four
negative inputs, and agreement of entire ordered reports across completed passes
under explicitly approved volatile exclusions. Unrelated findings remain visible
and assessed. No paid calls or advisory-target execution are allowed.

## Weekly maintenance checklist

Review each Monday at **09:00 America/Los_Angeles**, using the local timezone's
daylight-saving offset when recording UTC. This is a maintainer checklist,
without a response-time promise or automatic scan, reminder or publication job.

- Record the scheduled local date/time, timezone and corresponding UTC time.
- Check official [Python SDK releases](https://github.com/modelcontextprotocol/python-sdk/releases),
  [TypeScript SDK releases](https://github.com/modelcontextprotocol/typescript-sdk/releases),
  and their security advisory pages. Review the
  [GitHub Advisory Database](https://github.com/advisories) for the SDKs and
  maintained MCP server cases; record exact queries/URLs, versions or revisions,
  actual check times, and evidence. A checked page does not imply exhaustive coverage.
- Review incoming reports, disclosure status, source permission, pending labels,
  regression failures, dependency alerts and release decisions.
- Record each decision, rationale, owner and linked follow-up or explicit no action.
- Record actual start/completion times. Retain a missed review as `missed` with
  its reason (or `unknown`); link any catch-up separately. Do not backdate a review.
- Start cadence records at adoption; do not invent retrospective completed or
  missed reviews before the schedule takes effect.

## Lifecycle records

Keep versioned JSON and readable evidence summaries in `artifacts/phase23/`.
Use the following fields; this is a bounded file format, not a service.

| Field | Meaning |
| --- | --- |
| `schema_version`, `case_id`, `status`, `owner` | Record version, advisory/report identity, actual lifecycle state and responsible maintainer. |
| `advisory` | `url`, separately sourced `published_at_utc`, and `publication_evidence`. Public disclosure time is not intake time. |
| `intake` | `received_at_utc`, `recorded_at_utc`, `evidence`, `channel`, `scope`, and proposed vulnerable/fixed revision bindings. Late recording does not establish earlier receipt. |
| `source_rights` | `status`, `license`, `consent`, `evidence`, `reviewed_by`, `reviewed_at_utc`. Consent is null until known; preserve license notices. |
| `reporter_expectation` | Unreviewed rule/condition/expected behavior and evidence. |
| `reviewed_labels` | Per-input label, source condition, matching rule/path/location, support requirement, rationale, evidence, reviewer and actual review time. Empty until reviewed. |
| `identities` | Corpus version, manifest hash, source inventory hashes, scanner revision/tree hash, rule tree hash, helper hash and configuration hash. Unknown values remain null. |
| `milestones` | Append events with `event`, actual `occurred_at_utc`, `recorded_at_utc`, `actor`, `status`, evidence and bound identities. Include triage, reproduction, fix verification, human review, publication approval, TestPyPI publication/verification, PyPI publication/verification, GitHub release, Action alias verification, released regression verification and final acceptance. Failures remain events. |
| `waiting_intervals` | `reason`, `owner`, start/end UTC, evidence and elapsed seconds. An open interval has null end and elapsed duration. |
| `elapsed_seconds` | Advisory-to-intake and intake-to-triage/reproduction/fix verification/human review/publication durations. Derive from recorded event times; null if either endpoint is unknown. Wall elapsed includes waiting; do not label it active engineering time. |
| `evaluations` | Stage, approval evidence/hash, exact command, identities, input order, exclusions, limits, per-observation outcome/report/diagnostics/timing/cleanup evidence and ordered comparison evidence. Preserve unstarted, failed, unsupported and incomplete states. |
| `release` | Chosen version, reviewed contents and revision, package hashes/pins, Action exact pin/alias, approvals, workflow/assets/provenance, rollback and released-regression evidence. Unknown until performed. |

Use ISO 8601 UTC timestamps ending in `Z`. Null means unknown or not yet observed;
the associated status explains which. Never infer a milestone from a commit time,
advisory publication, planned schedule or approval of a future action. Preserve
old records; corrections append evidence rather than rewriting failures.

Weekly records use `schema_version`, `owner`, `scheduled_local`, `timezone`,
`scheduled_at_utc`, `status` (`scheduled`, `completed`, or `missed`),
`started_at_utc`, `completed_at_utc`, `sources_checked` (URL/query, revision/version,
actual check time and evidence), `decisions` (rationale, owner, follow-up),
`missed_reason`, and `catch_up_record`. Template schedules and times remain null
until adoption. A partial check is recorded as evidence without claiming a
completed review; a missed slot remains missed if a later catch-up occurs.

## Release review and verification

Keep the existing [release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/.github/workflows/release.yml)
and its full checks. The maintainer chooses the release number at review, after
seeing all applicable accepted changes already on main, compatibility assessment,
Unreleased notes, meaningful coverage changes and limitations. Bind the packet
to the exact revision, rule/corpus identities, package hashes, Action pins,
rollback instructions and commands. Approval must name merge, tag and publication
actions; technical acceptance alone does not authorize them.

After approval, verify the SSH-signed annotated version tag on the reviewed main
revision, TestPyPI artifacts and provenance, public PyPI hashes/provenance and
installs, GitHub release assets, exact Action pin and compatible `v1` alias.
Record actual publication and verification milestones separately. Reproduce the
accepted regression using the released detector. Preserve immutable historical
version tags and artifacts. Roll back by selecting a previously verified exact
package version and Action commit; record the loss of newer fixes. Moving the
mutable `v1` alias back requires an explicit reviewed action.

Phase 23 remains incomplete until the reviewed advisory loop reaches a verified
release, offline CI rejects the deliberate regression, contribution guidance is
delivered, and the maintainer explicitly accepts the final evidence.
