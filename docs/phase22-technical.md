# Phase 22 technical expansion

Status: implementation in progress; technical acceptance and external pilot
acceptance are pending. This is the user-approved target contract, not a claim
that every capability below is implemented. Phase 21 recruitment remains deferred.

The [execution correction record](phase22-execution.md) describes the implemented
first increment. The complete [independent corpus proposal](phase22-corpus-review.md)
was approved by the user's subsequent “continue” instruction. The exact manifest
and tested Git environment are bound in `artifacts/phase22/authorization.json`;
the original proposals remain unchanged. Detector development now uses exposed
Phase 20 cases and approved development cases. Fresh holdout source remains
separate from tuning.

The [description-poisoning increment](phase22-description-poisoning.md) records
SENT-013 implementation and its bounded development measurement.

## Evidence and acceptance

Preserve all Phase 20 source, configurations, labels, captures, costs and results.
Its 45 inputs are exposed regression evidence, including the historical held-out
split; improvement on them is not fresh held-out performance. Record Phase 22
measurements separately under `artifacts/phase22/` using the existing archive,
provenance, condition scorer, capture ledger and report infrastructure.

Before freezing new evidence, independently review ten vulnerable/fixed pairs
(one development and one separate held-out repository per new rule), ten safe
controls and paired structural mutations. Approval binds exact revisions,
licenses, conditions and repository split. Keep holdout source out of tuning;
exposing a case requires relabeling it and replacement holdout evidence.

Both static tiers must complete all 45 historical inputs, detect all 20 vulnerable
conditions, and produce no condition-matched alerts on fixed/safe inputs. GPT
must retain correct candidates; count `needs_review`. Report fresh holdout results
separately without an invented accuracy threshold. Keep unrelated warnings
explicitly unadjudicated unless reviewed. Repeat deterministic measurements.

## Rule contracts

| Rule | Meaning | OWASP | Impact |
| --- | --- | --- | --- |
| SENT-012 | Path containment failure | ASI02:2026 | High |
| SENT-013 | Tool-description poisoning | ASI01:2026 | High |
| SENT-014 | Command-option injection | ASI05:2026 | Critical |
| SENT-015 | Server-side request forgery | ASI02:2026 | High |
| SENT-016 | Operator-credential fallback across a caller boundary | ASI03:2026 | High |

Enable these rules by default when implemented. Preserve selection, suppression,
baseline identity, severity calculation and candidate-bound Finding provenance.
SENT-002 retains its execution meaning, including Kubernetes shell construction.
Each new rule needs independent pairs, applicable Python/TypeScript controls,
remediation, OWASP justification and the existing rule acceptance checklist.

Containment requires a relevant input/boundary/sink relationship, including
traversal, absolute paths, prefix collisions and source-supported symlink failures.
Poisoning requires explicit instruction override, secret exfiltration or cross-tool
redirection in statically recoverable tool/parameter descriptions; ordinary
imperatives, suspicious vocabulary and quoted security warnings are controls.
Option injection follows caller values into supported command-specific positions,
starting with Git references; recognize enforced rejection and safe argument
handling. SSRF follows service URLs into requests and covers prohibited schemes
and literal private/loopback destinations, without claiming DNS-rebinding coverage.
Credential fallback must establish an unauthorized caller/operator boundary;
nearby middleware or unrelated checks are insufficient.

## Compatibility and execution contract

Reuse the current parsers and Semgrep. Support imported handlers/schemas, local
aliases/re-exports, statically bound helpers/methods, cross-file guards/sinks,
low-level registration/dispatch, and declared uv/npm/pnpm workspaces. Resolve local
package exports and TypeScript aliases inside the repository boundary. An aggregate
static scan includes both languages with per-member coverage and root configuration;
disclose nested configurations not applied. Individual package scans use their own
configuration. Dynamic scanning still selects one Python stdio package in Docker.

Unresolved dynamic imports, reflection, ambiguous dispatch, unsupported schemas,
and inaccessible members stay visible. Never follow symlinks, import target code,
render charts or execute target tooling during static analysis.

Recognized Helm chart templates keep their original bytes for text/secret checks;
disclose omission of structured YAML analysis. Ordinary YAML and Sentinel
configuration remain strict. Profile the failing snapshots at the unchanged
120-second deadline before removing repeated work; do not exclude relevant source
or disable detectors. A separate Git benchmark environment needs an exact tested
SDK pin and dependency packet approved before adoption. Preserve original upstream
source and Phase 20 environment; prove startup/discovery inside Docker.

## Review, campaigns and schema specification

Review stays candidate-bound. Supply repository-relative resolved flow blocks
inside the existing 160-line total, validate references against supplied blocks,
retain redaction and disclose omissions. Invalidate changed request/cache identities;
reuse captures only after request compatibility verification.

Expand only SENT-008 through SENT-011. Enumerate supported probe/tool/argument/
mutation combinations and schedule deterministic round-robin coverage with GPT
priorities inside that schedule. Defaults: 24 attempts or 120 seconds, whichever
comes first. Every attempt has separate fresh baseline and attack containers.
`--max-probe-attempts` and `--campaign-timeout-seconds`, matching `SENTINEL_*`
variables and `[sandbox]` settings accept positive integers with CLI > environment
> file precedence. Rules-only bypasses runtime settings. Action uses repository
configuration. Preserve baseline validity, schema checks, observable effects,
isolation, interruption cleanup and runtime-proof protection.

The integration's native schema 1.7.0 adds workspace coverage and one `probe_outcomes` record per
planned attempt, stable attempt IDs and campaign budget/coverage totals. Record all
untested remainders; exhausting a budget with eligible work remaining returns 3.
Migrate 1.3–1.6 reports/baselines without changing Finding identities, suppression,
nullable reviews or runtime proof; old outcomes become legacy attempts without
invented historical coverage. SARIF stays 2.1.0. This integration emits 1.7.0;
final migration/consumer verification and technical acceptance remain pending.
Historical native reports retain their recorded schema versions.

## Delivery and outstanding decisions

The [implementation status map](phase22-implementation-status.md) separates
verified draft increments from the still-unfinished full technical plan.

The [filesystem condition follow-up](phase22-containment-conditions.md) records
enforced collection/parent guards and four exposed-input adjudications.

The [shared containment follow-up](phase22-shared-containment.md) records
bounded caller/context and helper identity fixes; full discovery remains pending.

The [workspace increment](phase22-workspaces.md) records aggregate scanning,
parent corrections, verification evidence and the remaining technical gates.

The [Python containment increment](phase22-python-containment.md) records its
implementation, repeated exposed-input measurements and remaining technical gates.
The [TypeScript containment increment](phase22-typescript-containment.md) records
parser-backed bindings, repeated completion checks and unresolved fixed guards.

The user approved consolidated delivery on September 7, 2026 to reduce repeated
CI and PR overhead. Preserve existing draft PRs as checkpoints and complete the
remaining work on `phase22/integration`, with separate reviewable commits in
contract/evidence, execution, containment/shared discovery, remaining
detectors/compatibility, review/campaign, report/acceptance order. Do not create
or update a PR for each increment. Batch delivery when the integrated candidate
is ready; branch consolidation does not imply implementation acceptance.

During implementation, run focused regressions and applicable lint/type checks.
Run full local checks at substantial integration milestones and the complete
benchmark and hosted OS matrix on the final candidate. Rerun affected checks
after fixes or newly identified risks. Retain raw commands, exit codes, logs and
commit identities as work proceeds; batch evidence packaging and delivery docs.
Existing CI workflows and final acceptance requirements remain unchanged: Ruff,
format, strict mypy, schemas, the full branch-coverage suite, dependency and
notices checks, strict docs, and applicable Docker/CI checks. Report completion,
support, recall, retained findings, abstentions, incorrect suppressions, false
alarms, timing and cost. Rerun comparable pinned Semgrep measurements; Snyk/Cisco
performance stays unmeasured.

The corpus freeze, Git SDK environment and paid evaluation require concrete
approval packets. Paid packets name requests, purpose, model, request/dollar caps
and stopping conditions; offline checks precede them. Merge and publication await
user decision. No new parser, language, remote runtime, independent AI discovery,
stateful exploitation, telemetry or outreach is authorized. Technical acceptance
does not satisfy pilot, adoption or whole-repository safety gates.
