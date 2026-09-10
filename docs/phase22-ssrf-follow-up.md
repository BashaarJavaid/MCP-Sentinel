# Replacement SSRF follow-up

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
