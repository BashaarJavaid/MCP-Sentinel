# SARIF

Generate a SARIF 2.1.0 report without mixing diagnostics into stdout:

```bash
sentinel scan . --rules-only --format sarif --output results.sarif
```

Both completed exit codes (`0` and `1`) produce a report. Exit `1` means a
finding reached `--fail-on`; it does not mean report generation failed.

## Offline validation

Sentinel validates SARIF before writing it. Validate an existing file against
the vendored official OASIS schema with:

```bash
python -m sentinel.report.validate_sarif results.sarif
```

Success is silent with exit `0`; invalid SARIF is an infrastructure failure.

## Provenance

The SARIF driver keeps the stable `MCP Sentinel` identity used by existing code
scanning integrations and uses `PortunusMCP Sentinel build-time MCP security
scanner` as its public full name. Results retain rule ID, OWASP category,
severity, status, confidence, remediation, evidence references, static/dynamic
provenance, and GPT review mode. Host-absolute paths and endpoint URLs are not
serialized.

Inline suppressions use native SARIF `inSource` suppressions while preserving
their reason and directive location in result properties. Baseline-matched
findings remain results with `baselineMatched: true`; they are not removed.

Native report 1.7.0 places every planned attempt outcome in
`invocations[].properties.dynamicAnalysis`. Unsupported, untested, or inconclusive
probes set `analysisComplete: false` and exit 3 while retaining partial findings.
`executionSuccessful` describes infrastructure health. Finding properties retain
typed runtime proof, `reviewDisagrees`, and independent GPT judgments; model
suppression cannot suppress a verified host observation.

Rules-only exports existing stages in `invocations[].properties.stages`: GPT
and dynamic stages are skipped with `rules-only scan requested`. Finding review
and GPT summary properties are null. Older SARIF without stage properties is
still accepted by the Action adapter.

## Coverage and review activity (native 1.7.0)

`staticAnalysis.coverage` lists observed tool, prompt, and route registrations,
locations, recognition gaps, and the rules that actually visited each surface.
`evaluated` describes a rule's execution, not complete recognition of every
implementation. Configuration-excluded IDs and execution skips stay separate.
The total possible static surface is unknown.

`dynamicAnalysis.coverage.discovery` keeps campaign discovery and each baseline/attack
`tools/list` response separate. It records tool names, schema hashes, explicit
nested field paths, unresolved field space, and whether more pages exist. Only
an unpaginated complete returned catalog establishes that session's tool total.
Probe outcomes record `baseline_attempted` and `attack_attempted` at the call
boundary. Planned bindings and baseline-only calls are not adversarial coverage.
The campaign schedules bounded rounds across supported tools and arguments;
`attempt_id` distinguishes mutations under the same rule. `started` includes
startup failures. Campaign totals must agree with records, and eligible
unstarted remainders cause exit 3. Empty discovery does not invent attempts. Permission sidecars describe intended grants; they do not enforce
runtime resource boundaries.

`reviewActivity.static` and `.dynamic` record `not_requested`, `not_reached`,
`no_candidates`, `all_suppressed`, `completed`, or `incomplete`, with candidate,
excluded, selected, reviewed, and unreviewed counts and actual modes. Accepted
abstention is reviewed work with a visible `needs_review` judgment. Aggregate
GPT mode `not_run` means enabled review had no reviewable candidates. Rules-only
retains null GPT summaries. Empty stages do not add live/replay/mixed activity.

Native 1.3–1.6 baselines migrate in memory to 1.7; original bytes are preserved.
Version 1.6 retains its recorded coverage, activity and sent-call flags; older
versions keep these fields null rather than inferring them from prepared requests.
Legacy attempts have unknown mutation, eligibility, started state and campaign
totals. Consumers must accept these nulls. Canonical findings, baseline-v2
identities, and accepted model payloads remain unchanged.

Default result messages share the console's concise evidence and repair direction.
They distinguish static suspicion, model corroboration, runtime observation, and
verified effects, including merged runtime proof. Source excerpts stop at three
lines / 480 characters; runtime excerpts stop at three concise facts. Omissions
are explicit, and full canonical evidence and review records remain in result
properties. A completed zero-finding scan does not establish that unresolved
handlers were examined. Baseline `resolved` means not observed in this scan.

## GitHub code scanning

The [composite Action](github-action.md) validates SARIF before upload. GitHub
creates alerts from visible results and preserves stable `SENT-xxx` rule IDs.
Fork pull requests run without repository secrets and therefore skip upload;
non-fork runs remain fail-closed if required analysis or upload fails.

`artifacts/example.sarif` is retained as historical evidence and is not
regenerated for a documentation-only change.

## Ordered attempts and workspaces (native 1.7.0)

This is the Phase 22 integration contract, with final verification pending.
Planned bindings, baseline/attack snapshots and outcomes join by unique attempt
ID; a campaign discovery snapshot has no attempt ID. IDs use probe, tool,
argument path and mutation, independent of schema fingerprints and timings.
Totals enforce `tested <= started <= eligible <= planned`, the started attempt
budget, and `remaining_eligible_attempts = eligible_attempts - started_attempts`.
Unsupported or unavailable information remains explicit. Historical outcomes
become legacy attempts without invented eligibility, mutation or started counts.

Workspace coverage records declarations, unique member paths, per-member source
and surface counts, unavailable members and unapplied nested configuration.
Surface counts agree with the observed inventory; shared files belong to the
most specific member and are not double-counted. Native validation checks these
relationships in addition to JSON Schema. Repeated runtime proofs remain in
finding provenance, native output, SARIF and candidate-bound review context.
