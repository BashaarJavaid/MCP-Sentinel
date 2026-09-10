# Phase 22 implementation status

## Current continuation at `2ac39aa`

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

Final-source local verification passes: **2,182 tests, 36 skips and no expected
failures**, with **89.66% branch coverage**. Ruff/format, strict mypy, lock,
schemas, notices and offline artifacts pass. Both approved production requests
are regenerated and checked-replayed through the owned Docker demo with zero
new calls. Hosted verification for this source is pending; the older `6eb482c`
hosted passes below retain their historical source.
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

The final local development measurement completes 22/25. Meta operator-fallback
fixed, fixed-mutation and safe inputs time out at 120.041s, 120.084s and 120.091s.
All ten vulnerable conditions are detected; 12/13 valid negatives complete with
zero matching alerts. Both raw erratum negatives are incomplete, so this is
12/15 completed raw negatives, not an improvement in false-alarm scoring.
The original held-out result remains 10 completed/10 unsupported/5 incomplete,
with zero detections among four completed vulnerable inputs out of ten total.
All report changes have source assessments. The failed final Linux sequence is
retained separately; no local or hosted retry is inferred.
See `v9-final-corpus-assessment/packet.json` and `v9-linux-assessment/packet.json`.

The current local suite passes 2,141 tests with 36 Docker skips and 89.64% branch
coverage. Strict docs and final hosted checks have their own delivery records.

The fetch-mcp correction follows genuine imported schema field flow and async
static class helpers. SENT-015 distinguishes an enforced `private-ip` check of
the same URL hostname from checking the whole URL, an unrelated value, an ignored
result or a URL object escaped to unknown code. It credits only the initial
private-IPv4 restriction. Fixed/control reports still retain scoped uncertainty
about schemes, DNS, redirects and broader IPv6; zero matching alerts does not
mean zero raw findings or complete SSRF protection. All changed diagnostics and
residual findings have source-bound assessments in
`v9-fetchmcp-assessment-v2/packet.json`; the unchanged open-webSearch reports reuse
their source judgments through `v9-openwebsearch-assessment/packet.json`.

Three finite performance iterations are retained. An AST cache was reverted;
a hash-based guard cache caused historical timeouts and was replaced. The final
per-flow immutable guard snapshot reuses pure aggregate facts while reading the
current branch environment. On two repeated slow inputs, full ordered reports
match the baseline except recorded identities/clocks. Meta fixed-mutation wall
times are 57.428s/63.351s and upload-fixed 87.987s/87.005s. These focused results
are not a whole-corpus timing pass; see `v9-iteration3-disposition.json`.

Earlier corrected worker profiles locate substantial cost in shared expression/
call traversal, branch merging and Value allocation across SENT-012/015/016.
They predate scanner7555a9d and remain historical diagnostic evidence. The final
whole-batch Linux job has no profiles; the later separately approved v10 diagnostic
now records current partial worker profiles. Those profiles and the reverted
local merge experiment are described above; neither passes the timing gate.

Current production request construction accepts the two existing captures and
six replay batches without new model calls. The controlled Docker demo completes
20/20 attempts with 14 findings. All 13 Git catalog/campaign/configuration rows
and 19 runtime components match retained approved-environment evidence: 1,040
planned, 312 tested and 728 remaining, all 13 campaigns incomplete with exit 3.
Wheel/sdist bytes match current source and pip/pipx/uv installation smoke passes.
See `v9-compatible-evidence-binding/packet.json` and the `v9-final-*` check records.
Current hosted checks name delivery `bbb5fbc`; all prior checks remain bound to
their original source and are not relabeled.

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

## Previous closeout checkpoint before the two approvals

**Current candidate: `62987a6`; implementation bytes equal `e87b7c9`.**
The exposed SSRF condition passes both final native five-input runs at `62987a6`:
two correlated vulnerable variants detected, with no matching fixed/control
alerts. Changed findings and coverage have source-bound assessments. Original
misses remain preserved; this is exposed regression evidence, not fresh accuracy.
Both entire ordered report sets match the prior source assessment except recorded
volatile fields. Maximum per-input wall times are 75.042s and 71.837s.

The first complete historical attempt at `e87b7c9` finishes 43/45 inputs. Both
fixed-upload variants time out; the fixed-authentication mutation completes
natively but takes 123.156 seconds end to end. All 20 vulnerable conditions are
detected, with no matching alerts on the 23 completed negative inputs. The strict
two-whole-batch gate remains failed. Focused successes are not pooled into a pass.

A subsequent credential-copy experiment at `3cbc329` completes only two of six
slow inputs and is reverted at `62987a6`; its raw results and added guard tests
remain. A bounded Linux CI execution proposal is prepared and awaiting the
explicit decision required by the final continuation prompt §4. It preserves
the original deadline and conditions and permits at most two entire batches.
The revised `v7-native-runner-proposal-v3` includes one original development
batch after that local measurement completes 24/25: the Meta operator-fallback
fixed mutation times out at 120.063 seconds. The approved label erratum does
not make the missing execution a pass. All 10 vulnerable conditions are detected;
13 valid negatives have zero matching alerts. Raw scoring retains one alert on
14 completed negatives, with the second erratum input incomplete. No workflow
change or dispatch occurred.

Original held-out measurement retains 10 completed, 10 unsupported and 5
incomplete inputs, with unchanged findings in completed reports. IntegSec's
development diagnostic changes are source-bound to newly resolved literal
imports; findings remain unchanged. Warning-order differences are retained.

The restored candidate passes 2,121 tests with 36 skips and 89.64% branch coverage.
Lint, formatting, strict typing, schemas, lock, notices, dependency audit, offline
artifacts, strict docs and installed-wheel checks pass; local distributions match
current source bytes. Current production capture replay completes the Docker
demo's 20 attempts with 14 findings and zero remainder, without new paid calls.
Draft PR #37 now points to `62987a6`; all 29 jobs in CI 34416723981 pass, as does
documentation run 34416723960. All 12 hosted quality suites report 2,121 passed,
36 skipped and 89.63–89.65% branch coverage. Complete logs and 225 artifact files
are retained; both distributions match the exact source/schema/fixture/capture
bytes. The earlier 29 hosted passes remain bound to `10103ad`.

Remaining requirements include execution reliability, the exact fresh freeze
and evaluation, and explicit human
technical acceptance. The `10103ad` fresh checkpoint is superseded and unevaluated;
`checkpoint-62987a6.json` is prepared and awaits explicit approval. The paid benchmark and
pilots remain user-deferred, not passed. Phase 22 is incomplete; Phase 21 and the
later adoption/launch gates are unchanged.


## Historical source-specific records

**Bounded SSRF follow-up implemented at `68bdf83`; hosted verification passes.**
The user approved offline investigation after the completed `ee9721f` audit.
The shared TypeScript flow now follows supported schema-bearing legacy tool
registrations, retains object methods, separates factory captures and preserves
ordinary versus lexical `this`. The shared regression selection passes 933 tests.
All 29 hosted jobs pass; each of 12 full suites records 2,057 passed, 36 skipped
and 89.50–89.53% branch coverage. Installed-wheel, Docker replay, isolation,
documentation and capture reuse pass. See the
[follow-up and remaining boundary](phase22-ssrf-follow-up.md).

All five exposed open-webSearch cases complete twice with identical reports.
Both vulnerable variants remain missed, with zero named-condition alerts on the
three fixed/safe cases. All 70 unrelated findings are unchanged. Coverage retains
13 recognized HTTP surfaces, one unresolved HTTP surface and 26 unresolved tool
registration contexts; contexts are not distinct tool counts. The source startup
and optional service-binding chain remains unresolved. No detection gain or
runtime confirmation is claimed for these cases.

Historical batches complete 44/45, 45/45 and 41/45 inputs. All 45 inputs have at
least two matching completed observations with total wall time at most 120 seconds;
all completed reports match the prior stable results. Five timeouts and one extra
native-completed report taking 123.8 seconds remain preserved. The handoff's
requirement for two whole completed batches **has not passed**. The proposed
casewise acceptance and residual-SSRF disposition are explicitly unapproved in
`artifacts/phase22/completion-scope-v1/follow-up-proposal.json`.

All 25 development inputs complete with unchanged findings: ten vulnerable
condition detections and the two preserved Meta fixed-label errata. The valid
negative denominator remains 13 with zero matching alerts; the original raw
labels and scores remain unchanged. The original held-out run retains ten
completed, ten unsupported and five incomplete inputs, with zero detections among
four completed vulnerable variants. Mastra's only report change is the movement
of unresolved logger calls into the now-recognized method bodies; its findings
and recognized surface counts are unchanged.

The separate `artifacts/phase22/corpus-replacement-v2/` proposal contains five
fresh fetch-mcp inputs and 45 unchanged records. Source/hash/lineage validation
passes. The detector froze before curation; no scanner or comparator evaluation
has run. The handoff requires explicit approval of this exact replacement
manifest before benchmarking cases prepared after an exposed case informed a fix.

The user deferred the 396-request paid comparison and removed external pilots
as a Phase 22 completion prerequisite. Neither is claimed passed. Phase 21 and
later adoption/launch evidence remain separate. No additional paid calls were
made. Final technical acceptance and disposition of the residual limitation
remain pending; Phase 22 is not marked complete. Earlier source-specific records
below preserve their original failures and pending gates. The previous `ee9721f`
engineering audit passed all 29 hosted jobs; that is not a hosted pass for the
later implementation.

The first historical run at `8bcaded` completes 45/45 inputs and source
adjudication detects all 20 vulnerable input conditions. Its conservative scoring
also records three Excel fixed/control false alarms: a parent-directory warning
lost the distinction from the already checked requested filename. That failed
gate is preserved. The second run completes 43/45, with timeouts on the fixed
Atlassian upload mutation and vulnerable Mobile original; all 43 completed
reports match their first-run stable content. Repeatability has not passed.
A separate ledger assesses all 1,484 new unrelated instances,
including explicit uncertainty, and preserves the 70 original unadjudicated
instances unchanged. These counts do not establish overall precision or
independent human acceptance. `6be3344` retains original-path checks on visible parent
access, and `dcb965f` reuses immutable TypeScript merge values. Together they pass
996 shared regressions, strict typing, style/format and strict docs; native
remeasurement and final verification remain required. Evidence batch 25 preserves
the commands, failures, source identities and ledger.

The latest immutable full milestone is `7071a26`: 1,959 passed, 36 skipped,
89.41% branch coverage, with passing quality, build, audit and installed distribution
checks. Linux network-none wheel isolation and installed onboarding/baseline checks
also pass after preserving and correcting their harness/workflow failures. The pinned
comparator completed 40/45 historical and 25/25 development inputs; rule timeouts
remain incomplete. `734aa8c` subsequently corrects exception-path credential
conditions exposed by actual-source review; 383 affected tests, strict types and
source-specific qualification traces pass. Final historical repeats, fresh holdout,
reviewed evaluation, hosted verification and the pending Meta label/configuration
decision remain separate gates. Evidence batch 23 retains these results.

At `2837d59`, bounded static workers complete all five Meta development inputs
within the unchanged 120-second deadline (59.5–68.1 seconds). The two Mobile
originals preserve exact native findings, coverage and ordered warnings against
the serial engine. Meta's frozen fixed-configuration decision remains pending;
completion does not settle that condition. `5f6bb9a` corrects SDK context
impersonation, lexical shadowing and Annotated lifespan binding, with 196 focused
and 388 HTTP-related regression passes. All 13 approved Git runtime campaigns
were remeasured at `394bb8a`: 24/80 attempts tested per input, exit 3, clean cleanup;
312 observations without a violation and 728 untested attempts establish no defense.
The earlier full immutable milestone is `5f6bb9a`: 1,910 passed, 36 skipped,
89.25% branch coverage. All 36 Docker controls and installed distributions pass
at that source. Its historical first run completes 42/45 with three retained
timeouts under competing verification. Session credentials and aiohttp origin
constraints through `fd9320b` pass 831 shared and 42 final focused regressions
plus strict types/style; final integrated measurements remain pending. The replay
demo needs an approved new dynamic-review capture and exits 3. Integration batch
22 preserves these commands, failures and identities.

The earlier full fixed-source milestone, `f2ea709`, passed 1,775 tests with 36 skips
and 89.11% branch coverage. Later TypeScript middleware work at `0491f32` passed
292 affected tests; helper-source evidence at `c6234a0` passed 49 context/review
tests. These later edits still require final integrated verification. The first
Meta vulnerable input at `f2ea709` completed in 119,405 ms with 49 findings;
the five-input condition gate and a frozen fixed-label decision remain open.

At `6a3a4a2`, two of five Meta inputs complete: vulnerable in 116,315 ms and its
mutation in 119,602 ms, with 49 findings each. The fixed pair and safe control time
out. Later TypeScript client-record work (`be6349d`) and discarded Python member
allocation reduction (`ab0e13c`) pass 941 affected regressions and strict types/lint.
The independent report/campaign audit passes 79 tests. These are additional
integration checks; they do not close the full benchmark, holdout, Docker or
external acceptance gates.

The equivalent-state and binary-combination changes (`4f2f81c`, `3ff455e`)
each pass 942 affected regressions. The binary implementation matches the prior
combination semantics across 287,144 differential cases. The all-rule fixed Meta
scan at `4f2f81c` still times out at 120,073 ms; performance acceptance remains
open. `65ba622` corrects campaign completion when a runtime schema or local
reference cannot be enumerated, retaining supported attempts and explicit gaps.
Its 158 campaign, argument, native report and migration checks pass, with strict
types and lint. Schema consistency, notices and offline retained-artifact checks
pass at that source. These checks use no paid model calls or target execution
outside controlled Docker; synthetic campaign tests are not runtime proof.

Earlier `4dfd24c` passed 1,215 tests with 36 skips and 88.27% branch coverage.
Subsequent Python branch/record corrections passed 425
affected regressions. At fixed source `34220b7`, all four exposed Atlassian
authentication inputs completed: two vulnerable condition hits and no
fixed-condition alerts. The eight fixed candidates explicitly qualify the
nondefault operator opt-in path. Earlier deadlines and incidental alerts remain
preserved. TypeScript class/receiver work has 366 affected regression passes and
reaches the mobile recording spawn's caller-derived arguments; ordered command
and output semantics remain open. These are source-specific increments, not the
final historical repeat, fresh holdout, reviewed evaluation or technical acceptance.

## Active delivery workflow

The user approved one integration branch with batched PR/CI delivery on
September 7, 2026. Continue in `phase22/integration`, currently checked out at
`/private/tmp/mcp-phase22-options`. Existing draft PRs remain checkpoints;
do not maintain the old branch stack for each subsequent change.

The integration branch incorporates the unfinished SENT-014 checkpoint and the
preserved report/review draft, including delivered parents through PR #36.
The original two TypeScript argument-identity failures are fixed in `37f2190`.
Nested Python registration/mutable command flow, shared caller evidence, and
conditional-value corrections are committed through `355f0f7`. A full milestone
suite at `192296d` passed **891 tests, 36 skipped, 86.84% branch coverage**; this
is not final-candidate evidence for later source changes.

Subsequent work adds line-preserving multiline credential redaction (`da52eb3`),
SENT-015 caller URL/destination flow (`d3fcf79`), fixed JSON argument positions
(`dbb2464`) and fixed public URL prefixes (`536bb69`). The review/context/proof
suite passed 71 tests with loopback permission; the first SSRF affected suite
passed 201 tests. The dbt five-input measurement at `355f0f7` completed with two
vulnerable selector hits and zero fixed/control selector alerts. Its 13 unrelated
candidates are separately classified in `artifacts/phase22/integration/v2-recovered-early-adjudications/dbt-adjudication.json`.
Five codegen candidates were false positives; their correction is in `dbb2464`.
Eight other candidates remain uncertain after implementation-agent source review.
These correlated development inputs do not establish held-out accuracy.

The first Meta SSRF pair was incomplete because of multiline redaction. After
correction both scans complete: three image-request candidates in the vulnerable
snapshot and none at those sinks in the fixed snapshot. Unrelated candidates
remain separate. The subsequent ten-input development run at `536bb69` completes both five-input
families: each has two vulnerable condition hits and zero fixed/control condition
alerts. Five dbt codegen false positives are removed; the Meta reports retain 240
unrelated candidate instances needing adjudication. All historical conditions, campaigns,
the complete report migration and final hosted verification remain open. Source,
commands, failures and logs are retained in `artifacts/phase22/integration/`.

Use focused checks while coding, full checks at substantial integration
milestones, and the complete final benchmark/OS matrix before acceptance. Retain
raw evidence now and package it in batches. Existing workflow YAML is unchanged.

## Delivered draft stack

| Increment | Source / delivery | Verification and limits |
| --- | --- | --- |
| Execution and Python containment | PRs #22 and #23, unchanged | All 30 applicable checks pass on each. Preserve PR #23's narrower four vulnerable Git inputs and four fixed partners; no expanded accuracy claim. |
| TypeScript coordinate correction | `3fc7ce3`, PR #24 | 743 tests, 86.73% branch coverage; all 30 applicable checks pass, including Windows 3.10–3.13. LF/CRLF and UTF-8 regressions cover imported handlers and finding/registration locations. |
| Workspace correction and delivery | `756b57e` source, `9098975` evidence, PR #33 | 758 tests, 86.69% coverage. Two 45/45 rules-only runs have identical stable findings/coverage. All 30 applicable hosted checks pass. |
| Bounded shared containment | `cee0283` source, PR #34 | 776 tests, 86.86% coverage; 71 focused regressions. Two 45/45 runs agree and have no changed findings relative to workspace source. Constructor correction `e67365a` passes 780 full-suite tests and 75 focused tests; all 30 applicable hosted checks pass on `6ec5201`. |
| Filesystem condition follow-up | `276722a` source, successor to PR #34 | 798 tests, 86.88% coverage; 102 focused tests. Four-input subset: 2/2 vulnerable hits, 0/2 fixed condition alerts; eight unrelated candidates separately reviewed. Full Phase 22 gates remain pending. |
| Preserved report/review draft | `229d50e` checkpoint, `phase22/report-campaign` | Original 18 modified/untracked files were archived and committed before updating parents. The branch includes parent corrections but remains an unaccepted draft. |
| Description poisoning | `fe40322` source, successor to PR #35 | 823 tests, 86.74% coverage. Five approved development inputs complete: 2/2 vulnerable condition hits and 0/3 fixed/safe condition alerts. All 26 unrelated candidate instances separately reviewed. |

PRs remain drafts. No PR merge, release, site publication, outreach or paid model
calls occurred. Exact commands, exits, source and harness digests, logs and failed
runs are retained in the linked increment records:
[TypeScript](phase22-typescript-containment.md), [workspaces](phase22-workspaces.md),
and [shared containment](phase22-shared-containment.md), plus
[description poisoning](phase22-description-poisoning.md).

The integration now also includes returned-error URL validation (`86ac2dd`),
initial direct HTTP credential-fallback detection (`6d9bee9`), shared Python
member state (`e2b0346`), HTTP URL entry points (`e1b23b8`), and source-bound record
callbacks (`d259126`). Focused regression sets pass, including custom-constructor,
replaced-guard and unrelated/replaced-value controls. These changes do not yet
establish the approved Atlassian middleware/service-factory conditions, complete
TypeScript support for new rules, or final condition-level acceptance. The second full
milestone at `d259126` passed **1010 tests, 36 skipped, 87.38% branch coverage**.
An exposed Atlassian profiling run hit the unchanged 120-second static deadline.
Its repeated discovery traversals motivated `aaa759a`; 195 affected regressions
and whole-project mypy/Ruff/format checks pass after that correction. This is not
the final historical measurement or a claim that Atlassian conditions pass. The repeated
profile at `aaa759a` completes within the static deadline but has no SENT-016
condition hit. SDK HTTP caller tracking (`de1af5a`) subsequently passes 201 affected
regressions, including stdio and local SDK-impersonation controls; SENT-016 CLI
selection/suppression/baseline/severity checks also pass. These do not yet establish
Atlassian or Meta operator-fallback acceptance. The integration evidence is retained
losslessly in `artifacts/phase22/integration/evidence-v1.json`, `evidence-v2.json`
and `evidence-v3.json` and their checksummed archives.

## Requirement map

| Requested work | Current implementation / evidence | Remaining work |
| --- | --- | --- |
| Preserve unfinished work and repair the existing stack | Checkpoint `229d50e`; `artifacts/phase22/typescript-correction/verification.json`; PRs #22–#24 checks | Keep the report/review draft at the proper delivery point. |
| Strict JSON diagnostic and four loopback tests | `workspaces.py`; `corrected-pytest.log`; four focused loopback tests pass with socket permission | No parser weakening. Earlier five failures remain in `workspaces/pytest.log`. |
| Reproducible workspace repeat | `workspaces/verification.json`, `reproducibility.json`, checksummed `measurements.tar.gz` | The older 41-input repeat remains incomplete and preserved. Final integrated measurements must use the eventual complete implementation. |
| Imported handlers/schemas, aliases, re-exports and methods | `discovery.py`, `typescript_discovery.py`, `typescript_modules.py`; discovery/module regressions | Complete all required SDK forms and feed all relevant detectors through the shared support. Inventory recognition is not detector support. |
| Cross-file caller/guard/sink relationships | `path_flow.py`, `typescript_path_flow.py`, SENT-012 tests | Complete approved Atlassian service factories/uploads, filesystem collection/symlink branches, Mastra security-failure flags and fallback, and all condition-level adjudications. |
| SDK-injected context and bounded factories | PR #34 regressions cover imported Context, rebinding, simple local factory objects, inherited/replaced methods and annotation-only controls | Arbitrary factories, reflection, custom construction and dynamic instance state are not established by these tests. |
| All ten exposed benchmark families | Existing SENT-012 increments plus retained Phase 20 inputs | Condition-correct detection of all 20 vulnerable inputs and clean fixed/control behavior is not established. Remaining Git option, filesystem, Atlassian, Excel, mobile and Kubernetes conditions need implementation/adjudication. |
| SENT-013/014/015/016 and Kubernetes SENT-002 | SENT-013 delivered; SENT-014 nested command flows and SENT-015 request flows now have local controls and development measurements | Complete SENT-014/015/016 and Kubernetes, remaining detector support and final rule acceptance. SENT-013 holdout and reviewed retention remain pending. |
| uv/npm/pnpm membership, local exports, aliases and inherited compiler settings | Workspace/module tests; aggregate root and individual-package configuration checks | Complete structured member coverage, unsupported/inaccessible counts, all negative compatibility cases and detector integration. Dynamic scans still select one Python package. |
| Candidate-bound 160-line review context | Integrated draft carries merged flow locations and context blocks; multiline redaction/context/proof regressions pass | Complete deduplication, omission/redaction/boundary/reference checks, request/cache compatibility and runtime-proof preservation. Prepare replacements only for changed requests. |
| Bounded ordered campaigns | Local `3f75327` implements ordered attempts, stable IDs, fair rounds, 24-start/120-second budgets and linked outcomes; reference Docker campaigns passed | Complete final candidate audit, Git corpus campaigns, full suite and hosted verification; discovery and failed attacks do not establish exploitation or defense. |
| Native 1.7.0 and consumers | Report/migration draft incorporated into integration; native 1.7 is not yet verified | Complete attempt/discovery/outcome references and invariants, legacy 1.3–1.6 migrations, workspace consistency, Finding/report schemas, console/JSON/SARIF and owning documentation. |
| Independent evidence and held-out evaluation | Existing corpus authorization and Git environment preserved unchanged | Finish development-condition measurements before evaluating fresh holdout source. Held-out performance has not been measured here. |
| Unrelated findings and competitor measurement | `shared-containment/finding-delta.json` compares 45 inputs; unchanged historical backlog remains unadjudicated | Adjudicate any later new/changed unrelated findings. Rerun the pinned comparable Semgrep measurements; Snyk/Cisco performance remains unmeasured. |
| Git runtime and paid reviewed comparison | Authorized `mcp==1.29.0` environment and earlier startup/discovery proof retained | Integrate campaign evidence; after offline gates pass, prepare exact paid requests/model/capture reuse/token/dollar ceilings and obtain approval. Reviewed completion/retention for all 45 inputs remains pending. |
| Final quality and technical acceptance packet | Increment-level Ruff, format, mypy, schemas, pytest, audit, notices, docs and CI evidence retained | Run all required checks and final repeated measurements on the complete integrated implementation; collect campaign/wheel/Action/isolation/OS evidence and requirement-level technical acceptance. |
| External acceptance | No external maintainer outcomes added | External workflows remain deferred under Phase21; the user has removed pilots as a Phase22 completion prerequisite. No external validation is claimed. |

## Evidence handling

The workspace packet retains all four measurements, including the earlier
incomplete repeat, in a lossless archive with per-file SHA-256 hashes. Archive
contents were checked byte-for-byte after creation. Expanded reports remain
available in the working checkout; the documentation includes the extraction
command for a fresh checkout.

Local measurements overlapped test and documentation work, so their wall times
are verification latency rather than isolated throughput comparisons. No code
coverage percentage is presented as detection accuracy, and no approval packet
for paid evaluation is claimed ready while offline condition gates remain unmet.

## Local integration through registered lifespan flow

Local commits `fec9215`, `3f75327`, `a9c097e` and `9d396a4` preserve the
constructor handoff, implement ordered bounded runtime attempts and linked
native 1.7 consumers, correct orchestration test proof, and connect registered
Python lifespan state through SDK context. These commits have not received
consolidated draft delivery or final technical acceptance.

Reproducible commands, failures, patches and diagnostics are retained in
`artifacts/phase22/integration/evidence-v4.tar.gz` with a per-file hash manifest.
The full integration run failed (1073 passes, 36 skips, two corrected test-fixture
failures); its coverage report overlapped source edits and is not clean evidence
for a fixed revision. The two real reference Docker campaigns passed native JSON
and SARIF validation; the required Git corpus campaigns remain unmeasured.

The exposed Atlassian source establishes the registered lifespan-to-context
relationship, but SENT-016 still misses its credential-fallback condition.
The later `c71e43e` supports source-established mixin construction; HTTP middleware enforcement, other required static conditions,
final offline/reviewed measurements, all final quality gates and draft delivery
remain open. Paid calls, human acceptance and external pilots remain separate
checkpoints. The complete requirement/evidence map and source-specific limits
are in the integration packet's `requirements.md` and `progress.md`.


Local source through `ee6c9f5` adds exact mixin forwarding, direct
Jira/Confluence credential arguments, an import-aware command precheck and URL
facts derived from the actual expression evaluation. The combined focused gate
passed 301 tests plus Ruff, formatting and strict mypy. The exposed Atlassian
authentication input still exceeds 120 seconds before all rules finish; its
latest instrumented run is incomplete. These corrections do not satisfy that
condition or the final technical gate. Commands, patches and failures remain
under `artifacts/phase22/integration/`; see the service-construction section of
`progress.md` for source-specific measurements.


`4d88844` adds bounded dataclass replacement/type-inspection and literal selector
branch controls; 314 focused regressions, Ruff, formatting and strict mypy pass
at their retained patches. Batch 5 contains 439 further evidence files, each
verified after archive creation. It preserves all incomplete measurements and
incidental-candidate limits; it is not a final technical acceptance packet.

### September 8 containment continuation (local integration)

`96712f3` preserves the dirty workbook/TypeScript work and corrects wrapped
registration origins, escaped SDK instances and successful void-helper guard
facts. The subsequent containment change interprets explicit parameterless
FastMCP launch functions and their global assignments, keeping transport-specific
source evidence. Unresolved launches retain an unconfigured analysis and warning.
It recognizes enforced realpath/commonpath boolean helpers and source-bound
openpyxl workbook loads and saves; unknown/replaced workbook receivers remain
unsupported. TypeScript inventory associates wrapped calls with their internal
SDK registration without inventing an extra tool.

For TypeScript output checks, lexical normalization and enforced relative-path
checks remain distinct from physical containment. A candidate whose lexical
boundary is established reports the remaining symlink uncertainty explicitly;
it is not silently suppressed or described as a demonstrated bypass.
The exposed Excel/mobile development measurements are retained under
`artifacts/phase22/integration/`, with exact source patches. These are development
results, not final repeated accuracy, held-out, runtime or reviewed-tier evidence.
Recording/device-command coverage and the other unmet conditions remain open.
The full Phase 22 technical scope and consolidated draft are still unfinished.

The fixed `4dfd24c` integration milestone passed 1,215 tests with 36 skips and
88.27% branch coverage, plus schema/notices checks. Its ten exposed Excel/mobile
inputs completed with four vulnerable condition hits and no fixed/control
condition-matched alerts. Separate stdio-policy and symlink candidates remain;
this does not establish whole-repository cleanliness or recording coverage.
Subsequent URL-composition and replaced-launch corrections have 338 affected
regression passes and whole-project style/type checks. Exact source-specific
results, original failures and remaining requirements are in the integration
packet. Final repeated benchmarks, unresolved conditions, paid review, hosted
verification and consolidated draft delivery remain unfinished.


The subsequent TypeScript recording continuation preserves ordered argv and
recognizes the source-selected mobilecli recording output contract at the actual
Node process sink. Traces now reach both optional time-limit layouts in the exposed
vulnerable and fixed repositories. The fixed recording candidate distinguishes
its lexical boundary from physical symlink uncertainty. Source-specific native
measurement, final repeated evaluation and remaining families still require
verification; traces and synthetic controls alone do not pass those gates.

At `b51aee1`, the five exposed mobile inputs complete through the native pipeline:
two vulnerable condition hits covering screenshot and recording, zero fixed/safe
condition alerts, with physical symlink uncertainty retained separately. Every
existing candidate retains its earlier content; each input adds one recording
candidate. Batch 11 retains exact commands, native reports, scoring and failures.
Remaining families and final integrated gates stay open.

The v2 continuation adds bounded SDK startup/provider/middleware interpretation,
source branch evidence, source module replacement, list iteration and Express
factory callbacks. Source-specific shared tests pass; this does not complete the
remaining TypeScript middleware/client contract. Upload at `6da955e` completes four
of five inputs; its safe control timed out. Meta at both `a2940e2` and `d2ba110`
completes zero of five inputs within 120 seconds. Later source-validation caching
has regression and component-equivalence evidence, not a passing native gate.
The frozen Meta fixed-label configuration conflict awaits an explicit versioned
decision; original labels and evidence are unchanged. See the integration progress
ledger and `meta-fixed-label-review-v1/` packet. Final technical verification,
reviewed evaluation, draft delivery and pilot-dependent acceptance remain open.

A separate safe-control retry completes at `6da955e` in 99.8 seconds. Across that
retry and the original run, all five upload-family reports complete, with two
source-adjudicated vulnerable Confluence condition hits and zero fixed/safe alerts.
Two page-content candidates remain policy-uncertain. Meta still times out on its
first input at `0eb39b5`; repeated startup interpretation remains a measured cost.
Evidence batch 16 preserves these results, failures and pending decisions. They do
not substitute for final integrated repeats or independent acceptance.


### Prepared-client qualification correction at 8bcaded

`8bcaded` preserves the caller-absence selection and required operator setting
through helper returns, prepared configuration and stored credential fields.
It reuses shared Atlassian client/session construction without evaluating arguments
twice and follows source-defined `get` methods. Original failures remain retained.
The shared controls passed 995 tests before the final sink-only correction; the
final credential/HTTP run passed 407 tests, with strict typing, style/format and
docs passing. The full fixed-source SENT-016 diagnostic completed and all six
visible candidates now retain the `ALLOW_GLOBAL_CRED_FALLBACK` default qualifier,
including the two downstream request findings. This is source evidence, not
runtime proof or the final all-rule condition gate.

Batch 24 retains 235 completed new/changed files (23,442,399 raw bytes); archive
SHA-256 `efd494495167c814cb4af3706a6e5c30d9d06f86967b8efc7e3c8143067b3a25`.
Every member was read back and hashed. All previous seals, failures and worktrees
remain preserved. The immutable checkout is
`/private/tmp/mcp-phase22-verify-v2-prepared-clients`; its historical repeat pair
is prepared with the unchanged 120-second budget. The fresh holdout is still
unopened. Meta's fixed-condition decision, paid review, hosted verification,
human acceptance and deferred external pilot gates remain separate and open.


### Immutable historical and full-suite gates at dcb965f

Both historical deterministic runs complete 45/45 under the unchanged 120-second
static deadline, with identical stable reports. The source-condition assessment
records 20/20 exposed vulnerable conditions and zero named fixed/safe alerts.
All 1,487 new unrelated instances have source assessments; the 70 original
unrelated instances retain their unadjudicated decisions. The three Excel parent
warnings remain visible with the established remote filename-check qualification
and separate parent-policy uncertainty. Their earlier failed score is preserved.
These are exposed, correlated cases and implementation-agent judgments, not fresh
accuracy, model retention, runtime proof or independent human acceptance.

At the same immutable source, the full suite passes 2,007 tests with 36 Docker
skips and 89.47% branch coverage in 1,213.21 seconds. The exact detached checkout,
scanner import, empty final source diff, log and coverage database are retained in
`v2-full-suite-dcb965f`. The separate actual Docker suite and installed-package
checks are queued. The three compatibility/workspace/consumer source audits are
bound to current file hashes and explicit delta reviews; all 13 approved Git
campaign/catalog configurations match retained execution evidence and the approved
linux/arm64 image identity was rechecked. Their 312 observations and 728 untested
attempts establish bounded incomplete coverage, not a defense.

The 25-input development run has started. Fresh held-out evaluation and all three
pinned comparator scopes follow sequentially; held-out source remains outside
implementation tuning. The Meta fixed-label decision, paid evaluation, hosted
matrix, consolidated draft, human acceptance and deferred external pilot gate
remain outstanding. Current results after batch 25 are expanded local evidence,
not yet covered by the next numbered seal.


### First held-out evaluation and source-coordinate correction

At immutable `dcb965f`, all 25 development inputs complete. Source assessment
finds all ten vulnerable conditions; the unchanged Meta labels yield two disputed
fixed-condition alerts, pending the explicit configuration/label decision. All
554 unmatched development warning instances have source assessments with explicit
uncertainties. No model calls or target execution were used for adjudication.

The first frozen held-out run completes 10/25 inputs, with ten unsupported and
five incomplete. None of the four completed vulnerable variants has a named
condition detection; six other vulnerable variants are unavailable, not completed
misses. The failures retain their exact reasons: unsupported dependency layout,
a supported file over 1 MiB, and strict YAML rejection of CloudFormation !Sub.
No scope limit, source, label or prerequisite was relaxed. The pinned comparator completes 45/45 historical and 25/25 development inputs.
Held-out completion is 20/25; all five Solver inputs retain parser errors despite
zero process exit codes. All three named-condition assessments record zero matches;
generic sink audits remain separate from evidence of the frozen failed guard.

The holdout's ten unrelated SENT-003 warnings expose incorrect TypeScript source
coordinates. `v2-heldout-first-assessment-dcb965f/` retains the complete score,
unrelated assessments and an exposure record for all five auth-fetch inputs,
written before implementation changes. Subsequent auth-fetch results are exposed
regressions; a separately approved replacement corpus is required before claiming
new fresh performance for that slot. Other holdout misses/support failures are
retained evaluation results and have not been used for detector tuning.

`b163d7c` fixes the shared legacy tool-finding coordinate calculation from retained
original source; handler locations no longer start at registration metadata.
Permission findings without an operation use the registration. Sixteen failing
inline/named/Unicode/LF/CRLF controls are retained and now pass, as do lint and
whole-project typing. The broader immutable check passes 300 tests and fails two:
one test expected the old incorrect end column and is corrected in `6e68331`;
the unchanged TypeScript smoke replay test requires a compatible capture. Its
exact replacement request is retained offline; no capture was fabricated or
rebound. The current full suite and two historical runs use immutable `6e68331`. The three old
quality/installed/request-preparation queues were stopped before starting checks;
the active immutable comparator sequence was preserved. No paid calls, pushes,
new draft, publication, merge or outreach have occurred. Batch 26 seals 1,255 completed post-v25 files, including the dcb965f full suite,
both historical runs, development/first-held-out measurements, comparator results
and source assessments. Its archive SHA-256 is
`4e4521bc7d05d4e65054b117b6faa1334c69ff7cb95096e6ee882e3742b02ce6`.
Every member was read back and hashed; active 6e68331 and coordinate queue records
remain outside this seal. No current-source full-suite pass is claimed.


### Corrected historical gate and replacement proposal at 6e68331

Both immutable historical runs complete 45/45 under the unchanged 120-second
deadline. All stable reports also match dcb965f, preserving all 20 exposed
vulnerable detections, zero named fixed/safe alerts, 1487 unrelated source
assessments and the original 70 unadjudicated instances. The gate packet verifies
actual raw report hashes and recomputed stable hashes before reusing those
assessments. This is historical exposed-condition evidence, not fresh accuracy.

The current compatibility/workspace/consumer source bindings, all 13 approved Git
catalog/campaign/sandbox comparisons, and pinned comparator harness/corpus
bindings pass. Git execution remains 312 tested observations, 728 untested and
no demonstrated violation; no new runtime execution is inferred from reuse.
The immutable 6e68331 full suite finished with 2021 passed, two failed and 36
skipped, at 89.49% branch coverage. One failure was a stale Phase 12 dry-run
cost expectation: the corrected TypeScript source coordinates add one serialized
request byte, changing the existing calculation from $0.130736 to $0.130740.
Commit d7184d3 changes only that test literal; both capture dry-run tests pass.
Scanner code, requests, caps and calculation are unchanged. The other failure,
the unchanged TypeScript smoke replay test, still needs a compatible capture.
The raw full suite remains failed. Original Phase 22 repeats are running, with
delivery checks queued against the immutable d7184d3 checkout.

A separate replacement corpus proposal is committed under
`artifacts/phase22/corpus-replacement-v1/`. It replaces only the five exposed
auth-fetch inputs with an upstream open-webSearch pair, paired predicate-renaming
mutations and a public-literal control. All 45 other input records and all original
source/results remain unchanged. The complete source archives and Apache-2.0
licenses are retained. Existing corpus validation passes. Manifest SHA-256
`159278d40a7d6fe2faa1c240a26f51009b37cdca30c862d5e9df1d66a6fed0da`
awaits explicit user freeze approval. The implementation agent read advisory
excerpts and source only after code froze at 6e68331; no detector changed and no
scanner/model/comparator/target evaluation ran on these inputs. This does not
reset the original held-out evaluation or create a fresh 25-input measurement.

### Completed independent local checks and paid checkpoint at d7184d3

The corrected scanner's 25 development reports are all stable-identical to
dcb965f: 574 findings, ten vulnerable condition detections and the same two
disputed Meta fixed-label alerts. All 554 unmatched instances retain their
source assessments. Original held-out completion remains 10/25, with ten
unsupported and five incomplete inputs. Five completed reports are unchanged;
the other five differ only in ten source-coordinate corrections, verified
against original source bytes and bound to the earlier unrelated judgments.
No new detection or fresh held-out accuracy is claimed.

At immutable d7184d3, Ruff/format, strict typing, generated schemas, notices,
offline judge artifacts, strict docs, lock checks, dependency audit, wheel/sdist
builds, pip/pipx/uv installation, public pre-commit and both offline smoke plans
pass. All 36 real Docker tests pass. All 12 installed Linux rules-only cases pass
with networking disabled. Installed onboarding and the initial/unchanged/changed
baseline workflow pass, with validated native reports and expected exits 1/0/1
for the baseline sequence. These checks preserve the main locked environment.

The actual demo completes all 20 eligible runtime attempts with zero remainder.
Four packaged historical captures review seven static findings. Seven dynamic
findings retain their proof but lack a compatible capture, so the demo exits 3;
its native JSON and SARIF both validate. That failure and the raw full-suite
failure remain visible.

Exact native request preparation covers all 95 original inputs with unavailable
states preserved. It produces 412 distinct benchmark requests: 16 pass accepted
ledger/request/semantic replay checks and 396 need new captures. The concrete
`artifacts/phase22/paid-evaluation-v2/packet.json` additionally includes the
TypeScript smoke and actual demo requests, for **398 new requests / $66.321920**,
with 20 historical requests reused. The packet and default validation-only
executor pass offline checks; no paid call has been made. The explicit approval
request names SHA-256
`9fbe33de0f3dda4ccaa2e3a058d96d6c43d0cb7518eeb72547c1c30cf78ef3c1`.
It excludes the pending replacement corpus. Source/configuration/environment,
per-request token/dollar ceilings and stop-on-first-failure policy are retained.

`v2-local-acceptance-index-d7184d3/packet.json` records the current local
disposition of all 86 requirements and hashes 24 completed verification commands.
Grouped regression results are separate from source conditions, reviewed
retention, hosted execution and human acceptance. Evidence sealing, the authorized
single consolidated draft and hosted matrix are next. Meta/replacement/paid
approvals and the deferred external pilot remain separate; Phase 22 is incomplete.

Evidence batch 27 now preserves 680 completed files, 403,378,236 raw bytes, with
verified member readback and archive SHA-256
`83bfc17cdf1b267332f4e11685bf1467eb2ee7eeee1d6bf4320063f0c802721f`.
The separate exact paid packet and replacement proposal are tracked directly.
The local acceptance index predates this seal and the remaining draft/hosted work.

### Consolidated draft and completed hosted matrix

[Draft PR #37](https://github.com/BashaarJavaid/MCP-Sentinel/pull/37) is delivered
against `phase22/description-poisoning`, exact PR #36 parent
`8b6b0ddf1d6f6cf5a8da3ab9421471865b801455`. The measured head is
`1e7c16a8ef92916c2f429d903b7decd7bff03c2b`; GitHub test-merge `a638bff` has the
identical tree. Existing drafts, implementation, worktrees and evidence remain.

All 29 jobs in [CI run 34348251747](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34348251747)
have completed. All 12 wheel jobs pass across Linux/macOS/Windows and Python
3.10–3.13. Each of the 12 full quality suites reports 2022 passed, one unchanged
TypeScript capture failure and 36 skipped, with 89.48–89.51% branch coverage.
No additional platform regression was found; the suites are still failed.
Later quality steps after pytest are skipped on GitHub, with their passing local
counterparts retained. Hosted network isolation and strict documentation pass.
The hosted wheel and source distribution are byte-identical to local d7184d3.

The hosted Docker demo tests all 20 attempts but fails the exact missing dynamic
capture named in the paid packet. Its later onboarding/baseline/validation steps
are skipped; the equivalent local installed workflows passed. Both hosted Phase20
jobs reproduce their pinned historical scanner's 32 completed/13 incomplete
inputs. They do not replace current Phase22 detector measurements.

`v2-hosted-matrix-34348251747/packet.json` records all job outcomes and individual
quality logs. Complete CI/documentation log archives contain 419/12 verified
members. Canonical binaries and both historical reproduction trees are retained.
`v2-final-technical-disposition-1e7c16a/packet.json` reconciles all 86 obligations.
Evidence-only final bookkeeping preserves measured implementation bytes and uses
`[skip ci]` to avoid duplicate CI as directed. GitHub can leave required checks
pending on that bookkeeping head; this is not a passing gate or merge readiness.
See [GitHub's skip behavior](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).

Independent implementation, local verification, draft delivery and hosted
execution are finished. Paid-reviewed evaluation and capture-dependent checks,
replacement evaluation after explicit freeze, the Meta label/configuration
decision, human technical acceptance and deferred external pilots remain pending.
No new paid calls have been made, and Phase22 remains incomplete.

Evidence batch 28 seals 397 completed files (8,615,381 raw bytes), with every
member read back and archive SHA-256
`fdd0ce31c17f9f1a99181e8cf6edf5cb1cbf66d413c8dbc495ab795156ed4480`.
All 27 prior seals and their original failures remain preserved.


### Approved smoke and demo captures

The user approved only two exact requests from the existing paid packet, capped
at $0.400100. Both succeeded without retries: TypeScript $0.016947, dynamic demo
$0.054852, total **$0.071799**. The separate approval, accepted capture ledgers,
exact request hashes and raw responses are retained in
`artifacts/phase22/paid-evaluation-v2/`. All benchmark paid review remains unapproved.

Both captures pass exact production replay with accepted-ledger validation.
The unchanged TypeScript smoke regression now passes. The actual Docker demo
exits 0 with all 20 attempts tested and all seven static/seven dynamic candidates
reviewed; native JSON and SARIF validate. New captures are additive in the
TypeScript and active `phase17` packaged sets. All older files and manifest
entries remain. The initial replay using the legacy demo directory and build
environment failures are preserved; corrected active-directory replay and uv
wheel/sdist builds pass. Both distributions contain the exact capture bytes.

Previous hosted failures at 1e7c16a remain historical evidence. New hosted checks
have not yet established a passing matrix for the capture update. Replacement
freeze and Meta condition/erratum decisions remain pending; no evaluation or
label amendment was performed. Full reviewed benchmarks, human acceptance and
external pilot gates remain incomplete.


### Approved replacement evaluation and Meta erratum

The recommended decisions are now explicitly approved. The separately authorized
five open-webSearch replacements complete 5/5 for both native rules and pinned
Semgrep 1.176.0 at runner `052379c`, with detector implementation unchanged from
`6e68331`. Both treatments detect 0/2 vulnerable variants and report zero named
condition alerts on the three fixed/safe inputs. Native repeat completes 5/5 with
identical stable reports. All 70 native and 33 comparator unrelated warnings have
source-bound scope assessments; their separate risk is not validated. Every native
input retains 13 recognized HTTP surfaces and seven unresolved surfaces, including
six computed MCP tool names. No fresh whole-holdout or full-handler-coverage claim
is made. No detector tuning, target execution or additional paid call occurred.

The approved Meta erratum preserves the original condition, labels and raw scores.
Two nominal fixed cases (four matched finding instances) remain visible as source
counterexamples for the alternate response configuration. The adjusted clean-case
gate has 13 valid fixed/safe inputs and zero condition false alarms, with two
erratum cases reported separately. Original raw scoring still shows two alerts
among 15 nominal fixed/safe cases. The ten vulnerable detections and their original
denominator remain unchanged; no runtime confirmation is claimed.

The bounded runner amendment passes 21 affected tests, lint/format, project-wide
strict typing and strict docs. It rejects mismatched approvals, replacement inputs
under the original approval, expanded input selection and unapproved treatments.
The capture-update hosted Docker job passes, including onboarding, baseline and
native/SARIF validation. The full OS/Python quality matrix remains in progress.
Further paid-reviewed benchmark runs require new explicit approval. Human
verification and deferred external pilots remain unmet; Phase 22 is incomplete.
