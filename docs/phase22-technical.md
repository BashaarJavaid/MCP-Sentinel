# Phase 22 technical expansion

## Current v15 diagnostic at `77ea21f`

The user's “okay go ahead” approved the single merge diagnostic in
`v14-next-merge-diagnostic-proposal.json`; `v15-merge-authorization.json` records
that decision. The sole Meta operator profile completed in **88.533s**
(**90.084s** including measurement setup/finalization), below 120 seconds.
All four workers have final snapshots. Its full ordered report matches the
retained native baseline after only established volatile exclusions; native JSON
and SARIF validate. The revised synthetic control passes 24 state comparisons.
The initial control-coverage assertion and documentation-binding check failures
are preserved with their corrections. No scanner code changed or optimization
was attempted. The one-profile budget is closed; zero paid calls.

Shared multi-branch value processing accounts for **17.8–21.3 instrumented
CPU-seconds** per active worker. About **85% of 19.01 million key visits** reuse
existing values. Those counts do not imply that reuse consumes 85% of the time:
the block also includes nested combining, lookups, equality and instrumentation.
URL pre-processing adds 3.79 CPU-seconds. Timings overlap where explicitly marked
and include instrumentation overhead; this is not a native performance gain.
See `v15-merge-assessment.json` and `v15-combine-source-review.json`.

Code/test/workflow/package inputs at measured `77ea21f` equal verified `592a9cd`.
The existing local and 12 hosted suites each retain 2,183 passed/36 skipped,
29 normal jobs and docs passed, production replay and Git compatibility, all at
their actual executed source. No repeated full suite or new hosted pass is
claimed. All three exposed SSRF gates remain source-compatible at `2ac39aa`.

The next `v15-next-combine-proposal.json` is **unapproved**: one counter profile,
one conditional shortcut using the existing two-value combination, up to
12 native performance observations and 30 conditional exposed regressions,
120 seconds each, zero paid calls. Its diagnostic threshold must pass before
any optimization; unused maxima close on failure. No new measurement is inferred.
Full Linux timing, fresh evaluation and final human acceptance remain unmet.
Phase 22 remains incomplete; pilots/full paid benchmark stay deferred, Phase 21
incomplete and Phase 24/15 unchanged. No merge, release, outreach or next phase.

## Historical v14 verification at `592a9cd`

Phase 22 remains incomplete. The user's “go ahead” approved the exact helper-fact
proposal in `v13-next-performance-proposal.json`; the new receipt is
`v14-performance-authorization.json`. Its one counter profile completed and
observed 3,402,980 empty-fact visits among 3,422,804 binding visits (99.42%).
One ordered-pass optimization was attempted at `e57ce95` and reverted in
`a7d7de0`. Scanner bytes again equal measured `2ac39aa` and delivered `424c443`.
The new semantic regression is retained; no detector behavior change remains.

The first operator candidate took 77.556s and 195.041848 child CPU-seconds,
exceeding baseline maxima of 75.134s and 188.048785 CPU-seconds. That irrecoverably
fails the prospectively approved per-observation retention rule. Four candidate
attempts had started when the queue was stopped: three completed, and the active
Atlassian repeat ended without a completion record. It is retained as interrupted,
not completed or timed out. Two remaining performance observations were cancelled;
the 30 conditional SSRF observations were never activated. Total usage is one
completed counter profile and ten native attempts (nine complete, one interrupted).
All ten completed ordered reports, including the profile, match their baselines.
No complete candidate pair or median performance gain is claimed. The failed
lint/format checks, queue termination, partial files and all original evidence
remain preserved. See `v14-performance-disposition.json` and
`v14-queue-stop-outcome.json` under integration evidence.

All three exposed SSRF families retain their passing v13 gates at `2ac39aa`:
five inputs twice per family, two vulnerable matches and zero matching negative
alerts per batch. Current scanner/harness bytes are identical; these results keep
their original measured revision. SearXNG's broader URL candidates and unresolved
MCP dispatch remain visible. Original misses and source assessments are preserved.

Final local and all 12 hosted quality suites pass **2,183 tests, 36 skips and
no expected failures** at corrected `592a9cd`. Local branch coverage is
**89.66%**; hosted coverage is **89.65–89.68%**. All 29 normal jobs and
docs pass ([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818910),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818938)).
Wheel/sdist source members match actual Git blobs; all 12 wheel combinations,
Docker replay, network isolation, dependencies and hooks pass. Configured strict
mypy checks all 146 files; Ruff/format, lock, schemas, notices and offline
artifacts pass. Both approved production requests regenerate and checked-replay
without new paid calls. The approved Git runtime/image bindings match; its
13 campaigns remain incomplete (312 tested, 728 remaining).

The candidate's 1,034 affected tests and semantic before/after control passed.
Initial `12748e4` CI failed all 12 quality jobs because its source-only local mypy
check missed a required test-helper annotation. The annotation is corrected;
initial failed/cancelled CI and the superseded local suite interrupted after
365 passing tests are retained. Detector source and measurements are unchanged.
The current 89-row audit records 70 passed, two explicitly user-deferred and
17 unresolved, with current test/evidence bindings. Seven additional v14 scope
requirements are mapped separately: six passed and the performance-retention
requirement remains unresolved.

The retained full Linux gate still fails at `7555a9d`: 15/25 complete, ten Meta
timeouts and both historical batches skipped. No further optimization, profile,
native/comparator measurement, full Linux retry, runner/deadline waiver or fresh
freeze/evaluation is authorized by unused maxima. The prepared `v14-next-merge-diagnostic-proposal.json` requests only one
120-second merge diagnostic on the named Meta input, with no optimization or
additional native/comparator run; it is unapproved. A new measurement scope
requires separate approval. Timing, fresh evaluation and final human
acceptance remain unmet; final acceptance is not requested. Zero paid calls.
Pilots and the paid benchmark remain deferred; Phase 21 is incomplete and
Phase 24/15 are unchanged. No merge, release, outreach or next phase.

## Historical v13 continuation at `2ac39aa`

Phase 22 remains incomplete. At scanner `2ac39aa` (source bytes equal the
SearXNG correction `523320f`), all three exposed SSRF families pass their native
repeat gates. Each family completes five inputs twice, detects both correlated
vulnerable variants and has zero condition-matched fixed/control alerts.
SearXNG takes at most 12.821s per input, fetch-mcp 5.104s and open-webSearch
65.265s. Complete ordered repeats agree except recorded volatile fields;
JSON/SARIF and source assessments pass.

The shared correction keeps TypeScript receiver invalidation local to mutually
exclusive `if` arms, then conservatively unions possible invalidations at the
join. An HTTP-arm unknown `process` effect no longer contaminates ordinary
stdio startup. No callback or unknown function is exempted. SearXNG's fixed
sources now retain the native default-loopback qualification; their broader
URL candidates and unresolved MCP dispatch remain visible. Its 23 unmatched
scorer keys per batch (20 prior HTTP candidates and three qualified negative-source
URL candidates) are all separately source-assessed. Original frozen native and
comparator 0/2 results remain unchanged; these are exposed regressions, not fresh
generalization or runtime proof.

The separately approved immutable-Value experiment used one optimization attempt,
two counter profiles and all 12 native observations. Ordered native reports all
match, but Meta operator median wall time increased 4.58% and child CPU 1.31%.
Atlassian improved 16.70% in median wall time; Meta image improved 5.35% in wall
but only 1.64% in CPU. These mixed results fail the retention rule. The
optimization at `de2a02f` is reverted in `2ac39aa`; the test, original commit,
profiles, deadline failures and all results are retained. No full Linux retry
occurred. The retained `7555a9d` Linux result still completes 15/25, with ten Meta
timeouts and both historical batches skipped.

Final-source local and all 12 hosted quality suites pass **2,182 tests, 36 skips
and no expected failures**. Local branch coverage is **89.66%**; hosted coverage
is **89.65–89.68%**. All 29 normal jobs and docs pass at `1be0650`, whose
code/test/workflow/package inputs equal measured `2ac39aa`
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664451),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664440)). Actual
wheel/sdist source members match Git. Ruff/format, strict mypy, lock, schemas,
notices, offline artifacts, dependencies, wheel smoke, Docker replay, isolation
and hook checks pass. Both approved production requests regenerate and replay
without new paid calls. The exact approved Git image/runtime bindings match;
its 13 campaigns remain incomplete (312 tested, 728 remaining).
See integration `v13-searxng-assessment/packet.json`,
`v13-exposed-assessment/packet.json`, `v13-performance-disposition.json` and
`v13-performance-revert-receipt.json`. The current SearXNG receipt consumes
31 of its maximum 32 executions: one fixed trace and 30 final observations;
the optional vulnerable trace was not needed. Both approved scopes have reached
their stopping conditions. The separate `v13-next-performance-proposal.json`
is prepared but unapproved; it does not reopen either budget.

Timing, a post-stabilization fresh freeze/evaluation and final human acceptance
remain unmet/separately gated. No final acceptance is requested. There were zero
new paid calls. Pilots and the full paid benchmark remain user-deferred; Phase 21
is incomplete and Phase 24/15 gates are unchanged. No merge, release, outreach or
next phase is authorized.

## Historical v12 follow-up at `6eb482c`

Phase 22 remains incomplete. The user's “go ahead” approved both v10 proposals;
`v11-follow-up-authorization.json` preserves their exact hashes and bounds.
One helper-context counter profile found no safely reusable result. No
optimization, native timing comparison or further full Linux retry occurred;
the retained timing failure remains authoritative.

Shared TypeScript factory/else discovery and narrow loopback/default guard
facts are implemented. The canonical finding/review contract is unchanged.
All 18 focused guard controls pass, but the full SearXNG correction gate fails:
both native batches complete 5/5 and detect 2/2 vulnerable variants, while both
fixed variants retain an unqualified SSRF alert. The public-IPv4 control also
retains a broad candidate, separately assessed outside its exact public-input
condition. That distinction does not waive the two fixed false alerts. The
new MCP dispatch surface remains unresolved. All ten authorized SearXNG runs
are consumed; original frozen native/comparator 0/2 results are preserved.

The earlier draft guard-contract stop was premature: existing URL evidence can
represent these narrow facts within the approved correction. Its correction is
recorded in `v12-scope-interpretation-correction.json`. The actual remaining
boundary is loss of that qualification in the complete source flow, not a
request for another ordinary editing approval. The exact cause is not established
by the native report; no callback or unknown effect is assumed harmless.

See `v12-searxng-assessment/packet.json` and the prepared, unapproved
`v12-next-searxng-proposal.json`. Any additional SearXNG observations, full timing
retry, new fresh freeze/evaluation or paid calls require their separate approval.
Final human acceptance is not requested. Phase 21 remains incomplete; pilots and
the full paid benchmark are user-deferred, and Phase 24/15 gates are unchanged.

Final-source verification at `6eb482c`: the local full suite and all 12 hosted
quality suites each pass **2,169 tests with 36 skips and no expected failures**.
Local branch coverage is 89.66%; hosted coverage is 89.65–89.67%.
All 29 normal hosted jobs and docs pass ([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34492040679),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34492040778)).
Wheel/sdist source members match Git; ordinary Docker replay, network isolation,
dependency checks, Ruff/format/strict mypy, schemas, notices and offline generated
artifacts pass. Both approved production review requests were regenerated and
replayed without paid calls. The approved Git environment and 13 incomplete
campaigns retain exact compatibility; no complete Git coverage is claimed.
Intermediate local socket failures and hosted dependency-download failures remain
preserved with their actual source; they are not relabeled as successful runs.

Fetch-mcp and open-webSearch each pass both five-input native regression batches:
2/2 vulnerable matches and zero matching fixed/control alerts per batch. Entire
ordered repeats match except recorded volatile fields; retained findings and
all changed diagnostics are source-assessed. SearXNG's two fixed false alerts
remain a separate failed correction gate. There is no final whole-corpus timing
pass, new fresh-source evaluation or final human acceptance.

The **89-row** current audit records **69 passed,
2 user-deferred and
18 unresolved** requirements. See
`v12-closeout-audit/packet.json`, `v12-current-source-test-bindings/packet.json`,
`v12-exposed-assessment/packet.json` and `v12-hosted-audit/packet.json`.


## Historical v10 checkpoint

**Current scanner: `7555a9d`; tested regression delivery: `bbb5fbc`. Phase 22 remains
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

The user approved the exact frozen SearXNG evaluation with “start with 1 and 2.”
All five inputs complete twice natively and once with pinned Semgrep: **both tiers
miss both correlated vulnerable variants**, with zero matching fixed/control
alerts. Maximum wall times are 11.311s/14.926s native and 20.219s comparator.
Entire ordered native reports match except recorded volatile fields; JSON/SARIF
validate. The implementation agent's source exposure after freeze is disclosed.
No new paid call, target execution, retry, source tuning or replacement occurred.

Native coverage recognizes four optional HTTP routes but misses the MCP tool
surface and its ordinary stdio factory/dispatch path. The complete URL flow also
includes structural argument validation, source defaults and casted undici fetch.
Every unrelated finding and diagnostic has a source assessment. This is a
substantive fresh detection limitation, not protection or human acceptance.
See `v9-fresh-assessment/packet.json` and `v10-fresh-review.md`; the separate
`v10-searxng-exposure-fix-proposal.json` is prepared but unapproved. Original
frozen results and manifest `275c98478617c76f92c6e0450b52c62f370a9ae22386022051b50ee792adffdd`
remain unchanged.

The current source SHA-256 is
`b7b7d4d4d5b6c0382769471249c7ea6bcc18465ac2b6d0bfcb3107b6047a089c`.
All 29 normal CI jobs and documentation pass at `bbb5fbc`. Scanner and package
bytes equal `7555a9d`; the sole test change adds a branch-guard invariant. Each of
12 hosted quality suites reports 2,141 passed and 36 skipped, with 89.63–89.66%
branch coverage. All 153 wheel and 166 sdist source/schema/fixture/capture members
match Git blobs. Full logs and 225 uploaded files are retained in
`v10-hosted-bbb5fbc/packet.json`; verification is in
`v10-final-hosted-audit/packet.json`. The local suite passes 2,141 tests with
36 skips and 89.64% branch coverage. The preceding `05309f9` hosted run also
passes and is retained separately. Pinned historical reproductions retain their
original scanner and do not replace the current timing gate. Exact unchanged
source/harness/input/capture compatibility is in `v10-source-compatibility.json`.
No additional paid call occurred. Pilots and the full paid benchmark remain
user-deferred; Phase 21 is incomplete and Phase 24/15 gates are unchanged.

The separately approved Linux diagnostic ran once as
[34446017571](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34446017571):
all four native observations and both profiles time out at 120 seconds. The job's
successful diagnostic completion is not a native timing pass. Worker profiles
show CPU-bound call/expression traversal, merging and Value allocation across
SENT-012/015/016. Missing reports remain missing; see
`v10-linux-diagnostic-assessment/packet.json` and `v10-linux-review.md`.

One bounded local experiment used eight native observations and one count profile
on the two exposed Meta inputs. Removing duplicate immutable merge inputs
preserved all ordered reports, but median wall gains of 2.29%/1.84% and CPU gains
of 2.43%/1.40% were small relative to variability, with a first operator regression.
The optimization was reverted; the useful branch-guard invariant test remains.
Scanner bytes still equal `7555a9d`. See `v10-local-performance-disposition.json`.
No full benchmark retry, deadline waiver or runner change occurred. Further
execution decisions and final human acceptance remain separate; Phase 22 stays
incomplete while the timing gate is unmet.

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
