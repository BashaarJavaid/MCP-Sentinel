# Phase 22 technical expansion

**Current scanner: `7555a9d`; workflow delivery: `a4766a9`. Phase 22 remains
incomplete.** Both exposed SSRF families complete five inputs twice, detect both
correlated vulnerable variants and have zero matching fixed/control alerts.
Their original frozen misses and source-assessed residual uncertainty remain.
The final Linux sequence failed: **15/25 completed, ten Meta timeouts**, with
both historical batches correctly skipped. No retry or timing waiver occurred.
Final human technical acceptance is unavailable while this gate is unmet.

Linux run [34435283462](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34435283462)
detects six of ten vulnerable inputs; nine of thirteen valid negatives complete
with zero matching alerts. Both raw Meta erratum negatives are incomplete,
leaving nine of fifteen raw negatives completed. The two vulnerable operator
variants newly time out compared with the prior Linux run. All 15 completed
reports equal current local entire ordered reports except recorded volatile
fields. See `v9-linux-assessment/packet.json` and `v9-linux-execution-delta.json`.

The next fresh SearXNG proposal is frozen against scanner `7555a9d` and manifest
`275c98478617c76f92c6e0450b52c62f370a9ae22386022051b50ee792adffdd`.
Its narrow condition is default initial-request rejection of caller loopback IPv4;
curation by the implementation agent occurred after the scanner freeze and is
disclosed. Explicit evaluation approval is pending; it has not been scanned or
used for tuning. The proposed two native five-input runs and one pinned Semgrep
five-input run use no models or target execution.

The current source SHA-256 is
`b7b7d4d4d5b6c0382769471249c7ea6bcc18465ac2b6d0bfcb3107b6047a089c`.
All 29 normal CI jobs and documentation pass at `a4766a9`, with scanner/test/
package inputs identical to `7555a9d`. Every hosted quality suite reports 2,140
passed and 36 skipped; branch coverage is 89.63–89.66%. All 153 wheel and 166
sdist source/schema/fixture/capture members match Git blobs. Complete logs and
283 uploaded files are retained in `v9-hosted-a4766a9/packet.json`; detailed
verification is in `v9-current-hosted-audit/packet.json`. Local coverage is 89.64%.
The pinned historical reproduction jobs each retain 32 completed/13 incomplete
on their original scanner, not the current integration timing gate. No additional
paid call occurred. Pilots and the full paid benchmark remain user-deferred;
Phase 21 is incomplete and Phase 24/15 gates are unchanged.

Further execution needs a decision after the failed final sequence. The unapproved
`v9-next-execution-proposal.json` proposes one diagnostic-only standard Linux job:
two already exposed Meta inputs, two native repeats and one worker profile each,
120 seconds per input and a 30-minute job ceiling. It permits no detector edit,
fresh evaluation, full benchmark retry or gate exception. Alternatively, further
performance work can remain deferred with Phase 22 incomplete.

See [implementation status](phase22-implementation-status.md) for the complete current evidence and limitations.

## Historical v8 checkpoint at scanner `62987a6`

**Current scanner: `62987a6`; workflow delivery: `88a559e`. Phase 22 remains
incomplete pending execution reliability and final human technical acceptance.** The user approved both the revised Linux execution and exact
fresh-corpus checkpoint with “go ahead with these two”. Their separate decision
records preserve the exact proposal/manifest hashes and stopping conditions.

Linux development fails its gate: 17/25 inputs complete and eight time out;
maximum end-to-end time is 120.043s. Eight of ten vulnerable inputs complete and
are detected. Nine of thirteen valid negatives complete with zero matching alerts.
Both raw Meta erratum inputs are incomplete, so the raw negative denominator is
nine completed out of fifteen. Both historical batches are skipped after this failure.

The Linux run is 34421737148. No retry, pooling or deadline waiver occurred.
Earlier local historical 43/45 and development 24/25 failures remain preserved.
Seven Linux timeouts are new versus that local development run; one persists.
All 17 completed Linux reports match the prior entire ordered reports except
documented volatile fields. The next bounded Meta performance proposal is
prepared in `v8-next-performance-proposal.json` and remains unapproved.
The approved Meta erratum remains separate from raw scores and execution status.

The fresh fetch-mcp evaluation completes all five inputs twice natively and once
with Semgrep 1.176.0. Both tiers miss both correlated vulnerable variants and
have zero condition-matched alerts on the three fixed/safe inputs. Native reports
match in full except documented volatile fields; maximum wall times are 5.771s
and 5.075s (Semgrep: 16.374s). Native dispatch/schema/class flows remain unresolved.
All 50 unrelated Semgrep JQuery alerts have source-bound false-positive
assessments. No detector tuning or fresh accuracy threshold is introduced;
curation exposure remains disclosed.

The exposed open-webSearch regression remains 2/2 detections in both final runs,
with zero matching negative alerts. Its original 0/2 results are unchanged.
Original held-out evidence remains 10 completed/10 unsupported/5 incomplete,
with zero detections among four completed vulnerable variants. The original
historical 70-warning unadjudicated backlog remains distinct from source-assessed
exposed-regression warnings. Native full-report comparisons and all new finding/
coverage assessments are retained in the v8 evidence.

All 29 normal CI jobs pass at workflow delivery `88a559e`, with the optional benchmark job skipped in ordinary CI; documentation also passes. The 12 quality suites each report 2,121 passed and 36 skipped, with 89.63–89.65% branch coverage. Complete logs/artifacts and source-verified distributions are retained.

The full paid benchmark and external pilots remain explicitly user-deferred,
not passed. No additional paid model calls or target execution occurred in these
two evaluations. Compatible capture/Docker/Git evidence remains bound to the
unchanged scanner. Final human acceptance is separate; Phase 21, Phase 24 and
Phase 15 gates remain unchanged. No merge, release, outreach or next phase.

The user subsequently authorized the bounded offline
[replacement SSRF follow-up](phase22-ssrf-follow-up.md). Those five inputs are now
exposed regressions; their original frozen measurements remain unchanged.

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

The deterministic tier must complete all 45 historical inputs, detect all 20
vulnerable conditions and produce no condition-matched fixed/safe alerts in two
entire batches under the unchanged 120-second native and end-to-end input limit.
Earlier complete measurements are historical evidence; the final implementation
must pass this gate without pooling successes from failed batches. The original requirement for the reviewed tier to match
that completion and retain correct candidates is explicitly deferred for cost,
not passed. Accepted captures verify recorded review compatibility only. Any
future reviewed comparison must count `needs_review`, suppressions and abstentions.
Report holdout results separately without an invented accuracy threshold. Keep
unrelated warnings explicitly unadjudicated unless reviewed. Repeat deterministic
measurements. Pilots are no longer a Phase 22 completion prerequisite.

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

The frozen-corpus runner supports source-only rules, offline request preparation
(`prepare-live`), checked replay and the pinned local Semgrep comparator. Preparation
uses a recording reviewer and replay uses checked cassettes; neither makes live
model calls. Phase 22 replay reads its separate `artifacts/phase22/captures` ledger.
The separately approved replacement manifest is supplied through an explicit
`phase22_approval` file. The runner validates the exact manifest hash, unchanged
metadata and selected input records, and enforces the approval's five-input and
`rules`/`semgrep` limits. Results retain both manifest and authorization hashes.
The original approval remains the default; it cannot authorize replacement inputs.
New paid capture still requires the exact bounded approval packet after offline
gates. The source-only corpus runner rejects dynamic treatments; the separately
approved Git runtime environment retains its own verification path.

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
