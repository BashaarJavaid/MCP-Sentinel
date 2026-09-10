# Replacement SSRF follow-up

## Current bounded follow-up at `a7d7de0`

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

The candidate's 1,034 affected tests, semantic before/after check, lint, format and
strict mypy pass. Final local/hosted verification including the retained new test
is pending; earlier full-suite and hosted results retain their actual sources.
The prior 89-row audit remains 70 passed, two explicitly user-deferred and
17 unresolved, pending its current verification bindings.

The retained full Linux gate still fails at `7555a9d`: 15/25 complete, ten Meta
timeouts and both historical batches skipped. No further optimization, profile,
native/comparator measurement, full Linux retry, runner/deadline waiver or fresh
freeze/evaluation is authorized by unused maxima. A new concrete measurement
scope requires separate approval. Timing, fresh evaluation and final human
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

## Previous closeout checkpoint before the two approvals

## Current correction and verification

The normal rules-only pipeline detects the exposed condition after the shared
startup/default-dependency correction and source-bound literal-IP guard fix at
`c233521`. Both final five-input passes at `62987a6` complete: two correlated vulnerable variants
are detected, with zero condition-matched alerts on the two fixed variants and
public-IP control. The original frozen 0/2 results remain unchanged. This is
exposed regression evidence, not fresh holdout accuracy or runtime proof. The
maximum wall times are 75.042s and 71.837s; entire ordered reports match the prior
source assessment except documented volatile fields.

The shared flow follows source-established local startup imports, conditional
runtime construction and optional default fetchers. Unknown imports, injected
or replaced dependencies, computed registrations and unsupported schemas remain
explicitly unresolved. SENT-015 preserves the parsed URL/hostname relationship
through supported normalization and requires enforcement of the actual IP
classification result. Unrelated, ignored and non-rejecting checks remain
positive controls; bracket normalization and valid source-bound classification
are negative controls. DNS, redirects and production network behavior are outside
the measured condition.

The exposed assessment binds all changed findings and diagnostics to retained
source. It preserves 70 unchanged authentication findings and separately assesses
13 additional out-of-condition SSRF instances. Coverage reports 13 recognized
surfaces and 87 unresolved contexts per input; these contexts are not distinct
tool counts. The fixed request helper also retains an unresolved replaceable
axios binding, so silence alone is not evidence of protection.

The Python credential-flow optimization at `10103ad` retains branch values
while indexing guard-marker names. Six slow historical cases produce identical
full reports except documented run identities and clocks; aggregate wall time
decreases 7.5% in the recorded shared-host comparison. Its full historical batch
nevertheless completes only 38/45 inputs. The seven native timeouts are preserved.

The `e87b7c9` TypeScript merge correction removes measured repeated combination
of unchanged branch values while preserving guard and safety semantics. All
1,092 affected tests pass. The seven previously timed-out inputs complete in a
focused native run at 83.5–101.7 seconds, but the subsequent entire historical
batch completes only 43/45. Two fixed-upload inputs time out; a completed
fixed-authentication mutation exceeds the end-to-end limit at 123.156 seconds.
All 20 vulnerable conditions are detected; zero matching alerts are observed on
23 completed negatives. The strict two-whole-batch gate remains failed.

A later credential-copy experiment at `3cbc329` completes only two of six slow
inputs and is reverted at `62987a6`, retaining its raw failures and added guard
controls. Current implementation bytes equal `e87b7c9`. A bounded Linux runner
proposal awaits the genuine execution decision required by final prompt §4;
its v3 revision includes the original development batch, which now completes
24/25 after a Meta fixed-mutation timeout at 120.063 seconds. This is a new
execution regression, separate from the approved Meta label erratum. Original
held-out results remain 10 completed/10 unsupported/5 incomplete. Proposal
preparation does not authorize execution or change the gate. Final-source exposed
repeats now pass; execution reliability and human acceptance remain unresolved. The restored source passes
2,121 local tests / 36 skips with 89.64% branch coverage and current package/Docker
replay checks. Draft PR #37 now delivers `62987a6`; all 29 required hosted jobs
and docs pass. All 29 earlier hosted passes remain bound to `10103ad`.

The pending fresh proposal at
`artifacts/phase22/corpus-replacement-v2/checkpoint-10103ad.json` is superseded
for the new detector, as recorded in its versioned status file. No approval or
fresh evaluation is claimed. The new `checkpoint-62987a6.json` is prepared and
awaits explicit approval before evaluation. No new paid calls occurred. The earlier residual-SSRF and
timing waiver proposals were never approved and do not satisfy the current gate.

The sections below preserve the earlier implementation and measurement chronology.


## Historical authorization and corrections

The user authorized a bounded offline investigation and fix after the completed
technical audit. The five open-webSearch replacements are exposed regression
cases from that decision forward. The original manifest, first measurements,
labels, source archives and paid ledgers remain unchanged. The separate decision
is `artifacts/phase22/corpus-replacement-v1/exposure-and-fix-authorization.json`.

## Registration correction

The shared TypeScript flow followed factory-created `registerTool` callbacks but
ignored legacy `.tool(...)` registrations. Both discovery and rule interpretation
now route the supported schema-bearing legacy forms through the existing
registration path. Captured helpers and caller arguments reach the request sink;
a helper that fetches a fixed public destination remains a negative control.
Computed names remain unresolved. The existing Zod reader distinguishes supported
schemas from annotation objects and unknown metadata; unsupported overloads are
reported as unresolved rather than interpreting their callback context as tool
arguments.

The regression reproduced eight missing legacy registrations while four
`registerTool` controls passed. The correction also covers six unsupported-layout
controls. Focused discovery, SSRF and containment checks pass 353 tests. The
legacy-registration checkpoint `4f46dc6` passes the full suite: 2,042 tests, 36
skips and 89.50% branch coverage. Its raw coverage and source patch are retained;
that checkpoint does not establish a pass for subsequent method changes.

The follow-up trace also found that object-literal methods were discarded and
separate returned functions could overwrite captured fetchers. The shared flow
now retains ordinary/async methods and arrow properties, separates captures by
source call context, and preserves ordinary versus lexical `this` for dot and
literal-key calls. Replacement, borrowing, extraction and escape controls remain
covered; accessors stay explicitly unresolved. The shared regression selection
passes 933 tests. Final source-bound benchmark and hosted checks are recorded
separately in the integration evidence.

## Historical unresolved boundary at 68bdf83

The initial exposed-case diagnostic still produces no SENT-015 candidate for the
named IPv4-mapped loopback condition. It reaches the MCP callbacks and reports
`runtime.services.fetchWeb.execute` as unresolved. With an evaluator-supplied
source runtime, the method correction resolves `execute` and reaches the next
unresolved boundary, the optional default `fetcher`. The source registration factory
receives an injected runtime argument; the actual startup selects that dependency
through a local dynamic import, conditional initialization and optional dependency
factories. Recognizing a registration alone does not bind that service.

A complete follow-up must establish that source chain and preserve the distinction
between the vulnerable URL/IP predicate and the fixed bracket normalization,
address classification and request filtering. A helper's name is not a defense;
broadly flagging both revisions would not demonstrate the required distinction.
Any evaluator-assisted source trace is diagnostic evidence, not a native benchmark
hit or runtime confirmation. No upstream target is executed on the host.

More paid review is not a remedy for this missing candidate: the current review
stage is candidate-bound. The 396 deferred requests and external pilots remain
nonblocking under the user's revised completion scope, without being counted as
passed. Final technical acceptance and disposition of the residual limitation
remain with the user; Phase 22 is not marked complete by this correction.

## Historical exposed-case remeasurement and fresh proposal

All five original replacements complete twice on `68bdf83`; stable reports and
outcomes match. Both vulnerable variants remain misses, and no fixed/safe case
has a matching SSRF alert. All 70 authentication findings equal the first
measurement after excluding run identities and clocks. Their retained source
assessments remain applicable. The unchanged comparator's original 33 warnings
are reused as separately identified evidence; no new comparator run is claimed.

Each report has 13 recognized HTTP surfaces, one unresolved HTTP surface and
26 unresolved tool registration contexts. Following more factory/test contexts
increases diagnostic records; it does not mean 26 distinct tools were discovered.
The six underlying computed-name SDK callbacks remain unresolved. In the original
Mastra development cases, object-method support replaces unresolved logger calls
with the remaining unresolved operations inside those methods. Findings and
recognized surface counts are unchanged; diagnostic movement is not a detection
gain or evidence of protection.

Because the exposed cases informed these fixes, the original handoff requires a
replacement through the freeze process. The new proposal is retained in
`artifacts/phase22/corpus-replacement-v2/`, with five fetch-mcp cases, complete
MIT-licensed source archives, reversible helper-name mutations and a public IPv4
classification control. Its exact manifest is
`a587427f0c40cbff512f00c8024e454a11255e34a13c10f9d8748bbc4aa9bae2`.
The detector froze at `68bdf83` before advisory/source curation. No scanner,
comparator, upstream test or target execution has run on these cases. Explicit
freeze approval is required for the proposed offline evaluation; it includes no
paid calls. The narrow source-backed labels do not claim complete SSRF protection.

## Historical verification and unapproved disposition

All 29 hosted CI jobs pass at `68bdf83`: 12 full quality suites each report 2,057
passed, 36 skipped and 89.50–89.53% branch coverage. The complete CI/docs logs and
225 uploaded artifact files are retained. The canonical wheel and sdist contain
the exact current source, schema, fixture and approved capture bytes. Current
production capture replay accepts both original approved requests with no new
model calls; hosted Docker replay and network isolation pass.

The three historical batch attempts report 44/45, 45/45 and41/45 native
completions. Every input has at least two completed reports with recorded total
wall time at most 120 seconds; all completed reports match the prior stable content.
The complete pass retains 20 vulnerable condition hits and zero named fixed/safe
alerts. Five timeouts remain. One additional native-completed report has 123.8
seconds of total wall time and is excluded from the under 120-second count. These
per-input comparisons do not silently satisfy the original requirement for two
whole completed batches. Shared-host resource observations do not establish the
cause of the timing variance or an isolated-throughput claim.

The recommendation is to retain the bounded TypeScript corrections and accept
the residual service-binding limitation and measured timing variance for Phase 22,
using the explicitly reported per-input repeatability evidence. This is a
**proposal, not an approved gate change**; see
`artifacts/phase22/completion-scope-v1/follow-up-proposal.json`. The fresh five-case
manifest needs separate freeze approval before its offline evaluation. Paid review
remains deferred: the absent SSRF candidate gives candidate-bound review no new
condition to assess. Phase 22 remains incomplete pending the required decisions and
final technical acceptance.

The final original development measurement completes all 25 inputs with unchanged
findings: 10 vulnerable detections, the two preserved Meta fixed-label errata and
554 unmatched source-assessed findings. The original held-out run retains 10
completed/10 unsupported/5 incomplete inputs, with 0/4 completed vulnerable
variants detected. All canonical findings equal the prior measurements. The five
Mastra cases replace 80 unresolved logger-call diagnostics with 10 unresolved
operations inside those methods per input; their findings and recognized surface
counts are unchanged. Existing source assessments and pinned comparator results
are reused with exact identities, without claiming a new comparator execution.
