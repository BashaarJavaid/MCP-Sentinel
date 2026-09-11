# Phase 22 static timing policy

## Current loopback qualification correction and regression checkpoint

The approved Lighthouse regression at scanner **`4a2359d`**, workflow **`b53581d`**,
run **34641101185**, detects both correlated vulnerable variants, then **fails**
the first fixed-input condition: its finding lacks the required initial link-local
rejection qualifier. All **three observations complete within 120 seconds**
(12.500–14.805 seconds whole input), with valid JSON/SARIF and verified cleanup.
**Seven unstarted observations are closed; zero budget remains.** No complete
five-input batch, control or repeat was observed. All three findings, 261 warnings,
164 unresolved-flow occurrences and six unresolved surfaces are source-assessed.

The minimal correction at **`f85a90f`** preserves the narrow IPv4 link-local fact
on a helper's IPv6 loopback equality return. It adds two shared URL-analysis lines;
broader SSRF candidates remain visible. Six synthetic checks cover loopback and
unsafe literal exceptions, compound range iteration, URL parsing and DNS branches.
All **518 affected tests pass**. Full local and all 12 hosted suites pass
**2,242 tests / 36 skips**, with **89.76%** local branch coverage and
**89.75–89.78%** hosted coverage. All **29 normal jobs** and documentation
pass at workflow **`439c3fe`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059839),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059977)).
Wheel/sdist source members match actual Git blobs. Ruff/format/strict mypy,
lock/schema/notices/offline artifact checks pass. Six production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and zero paid calls.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git runtime/image bindings remain unchanged; its campaigns remain incomplete.
No corpus observation has occurred at this corrected scanner.

The next exact proposal is **unapproved**:
`artifacts/phase22/integration/v29-loopback-fix/evaluation-proposal.json`,
SHA-256 `db93996f070f824b72b9bf2383e82efcde5d674c16e37d339ab7d521b7ace016`.
It retains the same five exposed sources twice: **ten native observations**, one
standard Linux job capped at **60 minutes**, 120-second target / 300-second
whole-input maximum and 15-second cleanup cap. Stop on the first execution,
condition or complete ordered-repeat failure and close the remainder. Zero retries,
profiles, comparators, target executions or paid calls. Normal CI skips this job.

The original fresh `1f3f72f` result remains 15 completed with 0/2 vulnerable hits
per native batch and comparator. The stopped `6db3858` result remains one completed
miss and nine unstarted closed. These later exposed corrections cannot establish
fresh generalization or independent human review. Earlier historical timing and
three exposed-family passes retain their actual `1f3f72f` / `2ac39aa` sources;
current-source compatibility and fresh-result disposition remain unresolved.

The **89 original rows remain 82 passed, two user-deferred and five unresolved**.
The **78 added rows are 71 passed and seven unresolved**, including five closed
historical failed gates. No stopped budget is reopened. The original held-out result
remains 10 completed, 10 unsupported and five incomplete, with zero hits among
four completed vulnerable inputs out of ten vulnerable inputs total.

**Phase 22 remains incomplete**, pending the remaining technical gates and explicit
human technical acceptance. Pilots and the full paid benchmark remain user-deferred;
Git campaigns remain incomplete (312/1,040 attempts), Phase 21 incomplete and
Phase 24/15 unchanged. Zero additional paid calls. No merge, ready-state, release,
outreach or Phase 23. The evidence labels v28/v29 do not change phase numbering.

## Historical v27 constructor-scope checkpoint

The approved exposed Lighthouse regression **fails** at scanner **`6db3858`**,
workflow **`fc3a49a`**, run **34621524649**. The first vulnerable input completes
in **9.835 seconds** whole-input time (**2.071 seconds** native) but produces zero
findings and no matching sink candidate. Its JSON/SARIF and cleanup pass.
**One observation completed; nine unstarted observations are closed; zero budget
remains.** No fixed/control or ordered-repeat result exists. All 21 warnings and
six unresolved-flow occurrences are source-assessed. No retry or paid call occurred.

The constructor-scope correction is verified at scanner **`4a2359d`**.
Constructor eligibility now excludes returns owned by nested callbacks/functions/
classes; a constructor's own returned object remains unsupported. Five synthetic
counterexamples fail at `6db3858`; all 81 class/SDK tests and 315 affected tests
pass with the correction. No current-source corpus observation has occurred.

Full local and all 12 Linux/macOS/Windows × Python 3.10–3.13 suites pass
**2,236 tests / 36 skips**. Local branch coverage is **89.76%**; hosted
coverage is **89.75–89.78%**. All **29 normal jobs** and documentation
pass at workflow **`2998b79`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34622991759),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34622991696)).
Wheel/sdist sources match actual Git blobs. Ruff/format/strict mypy, lock, schemas,
notices and offline artifacts pass. Six actual production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and **zero paid calls**.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git's unchanged runtime/image retains 13 incomplete campaigns, 312/1,040 attempts.
The earlier 2,230-test pass remains bound to `6db3858`.

The new exact **unapproved** proposal is
`artifacts/phase22/integration/v27-constructor-fix/evaluation-proposal.json`
(SHA-256 `3ee50c9d652f1cd4d897348a1b77ecf2efb60d78c2b56beb163b286623f6fd8b`): the same five exposed inputs twice, ten native observations,
one standard Linux job capped at 60 minutes, 120-second target / 300-second
whole-input maximum, 15-second cleanup cap, zero retries/profiles/comparators/
target execution/paid calls. Stop on the first execution, condition or ordered-repeat
failure and close the unstarted remainder. The optional workflow remains disabled
in normal CI. No corpus observation has occurred at `4a2359d`.

The **89-row audit remains 82 passed, two user-deferred and five unresolved**.
The 72 added rows are 66 passed and six unresolved, including four closed historical
failure rows. No failed measurement is relabeled as accepted or reopened.
The original held-out baseline remains10 completed,10 unsupported and5 incomplete,
with0 hits among4 completed vulnerable inputs out of10 vulnerable inputs total.

Both the original fresh `1f3f72f` miss (15 completed, 0/2 vulnerable hits per batch)
and this later failed exposed regression remain preserved. The existing fix-it
instruction authorizes the root-cause source correction and ordinary engineering;
the measurement approval does not reopen a stopped budget. Earlier timing and
three exposed-family gates retain `1f3f72f` / `2ac39aa`; current-source compatibility,
fresh-result disposition and final human technical acceptance remain unresolved.
**Phase 22 is incomplete.** Paid benchmark/pilots remain deferred, Git campaigns
incomplete (312/1,040), Phase 21 incomplete and Phase 24/15 unchanged. No merge,
ready-state, release, outreach or Phase 23 work. v26/v27 identify evidence only.

## Historical v25 Lighthouse correction checkpoint

The requested Lighthouse source correction is implemented at **`6db3858`**.
It follows actual module class construction and saved SDK setter forwarding,
recognizes Lighthouse URL sinks, and retains narrow initial link-local IPv4
rejection evidence. Replaced/escaped methods, wrong receivers, callback changes,
unknown array aliases and ineffective guards remain conservative. A qualified
finding still leaves other destinations, DNS, redirects and IPv6 unresolved.

The initial `b830027` candidate passed 2,229 tests locally and in all 12 suites,
but a later synthetic import-alias counterexample found another binding gap.
Canonical SDK identity invalidation corrects it at `6db3858`. That counterexample,
the original successful engineering results and both unexecuted proposals are
preserved; no corpus observation was consumed during this correction.

Verification passes **2,230 tests / 36 skips** locally and in all 12 hosted
Linux/macOS/Windows × Python 3.10–3.13 suites. Local branch coverage is **89.76%**;
hosted coverage is **89.75–89.78%**. All **29 normal CI jobs**
and documentation pass at workflow **`51fd2cb`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835606),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835565)).
Wheel/sdist sources are byte-verified. Six actual production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and **zero paid
calls**. The owned Docker demo completes 20/20 attempts with 14 findings and
cleanup; the unchanged approved Git runtime retains 13 incomplete campaigns,
312/1,040 attempts. This demo is separate from corpus evaluation.

The exact **unapproved** proposal is
`artifacts/phase22/integration/v25-lighthouse-fix/evaluation-proposal-final.json`
(SHA-256 `26ac27d01740faa0ac664a13963ef7a4d91f199818bba29d9a257d98f1f4206a`). It requests the same five exposed Lighthouse inputs twice:
**ten native observations**, one standard Linux job capped at **60 minutes**,
120-second target / 300-second whole-input maximum, 15-second cleanup cap,
**zero retries, profiles, comparator runs, target execution or paid calls**.
Stop at the first execution, named-condition or ordered-repeat failure and close
all unstarted observations. All four optional corpus jobs are disabled in normal
CI. No corrected-source corpus observation has occurred.

The first fresh result stays **0/2 vulnerable hits** per native batch and in
Semgrep at frozen **`1f3f72f`**: all 15 observations completed, all five ordered
native repeats equal, zero findings, unknown tool coverage and 232 source-assessed
diagnostics. Its budget is closed. The user chose correction rather than accepting
the limitation-only proposal. Any corrected Lighthouse result is an exposed
regression, not fresh generalization or independent human review.

The **89-row audit is 82 passed, two user-deferred and five unresolved**;
66 added rows are 61 passed and five unresolved, including three closed historical
failures. Current-source compatibility of the three earlier exposed SSRF families
and whole timing/condition gates remains to be established after the TypeScript
changes. Their passes retain measured `2ac39aa` / `1f3f72f`; no pooled or new
whole-batch claim, silent waiver or reopened budget. R66/R88 and explicit final
human technical acceptance remain open. **Phase 22 is incomplete.** Paid benchmark
and pilots remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge,
release, ready-state, outreach or Phase 23 work. “v25” names evidence only.

## Historical v24 replacement-v5 result and proposed disposition

The approved replacement-v5 evaluation completed **15/15 observations** in
[run 34605934302](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34605934302),
workflow **`86cbdc9`**, immutable scanner **`1f3f72f`**. All ten native observations
and five pinned Semgrep observations completed within 120 seconds; maximum whole
input was **10.437 seconds native / 22.052 seconds comparator**. All five entire
ordered native repeats match after only the established 11 volatile exclusions.
Native JSON/SARIF, input/configuration identities and owned-child cleanup pass.
The single dispatch and all 15 observations are consumed; no remaining budget,
retry, profile, paid call or target execution.

**The fresh detection result is 0/2 vulnerable hits in each native batch and
0/2 for Semgrep.** Both tools emit zero findings on all five correlated inputs.
The two fixed variants and public control also have zero matching alerts; this
silence does not establish discrimination because vulnerable inputs are silent too.
Sentinel reports no discovered MCP surfaces, an unknown total surface count,
and 19 binding warnings on each vulnerable input versus 26 on each fixed/control.
All **232 native diagnostic occurrences** are individually source-assessed.
The upstream SDK prototype patch makes the scanner's binding resolution ambiguous;
its TypeScript request-sink list also does not include Lighthouse. Neither gate
has been bypassed or changed. Completed analysis is not proof of handler coverage,
detection accuracy, safe navigation or runtime protection.

The novel repository/source pair was curated by the implementation agent after
scanner freeze, with source exposure and correlated variants disclosed. This is
one narrow link-local-before-Chrome condition, not five independent vulnerabilities,
independent human review or unseen-source evidence. Loopback remains intentionally
allowed upstream; DNS/redirects/IPv6 and actual startup/navigation are outside labels.
First frozen misses, source archives and the disqualified replacement-v4 proposal
remain preserved. No scanner tuning, case substitution or new evaluation is authorized.

The concrete limitation proposal is
`artifacts/phase22/integration/v24-fresh-v5/limitation-proposal.json`.
Its assessment, all 15 outcome rows, diagnostic source references, audit and review
summary are in the same directory. **The limitation is proposed, not accepted.**
The original 89 rows are 84 passed, two user-deferred, two proposed documented
limitations awaiting decision (R66/R88), and one unresolved human acceptance (R84).
The 60 added rows are 56 passed, three historical unresolved checkpoints with
closed scopes, and one proposed limitation disposition. Phase 22 remains incomplete;
final technical acceptance is a separate decision after the fresh disposition.

Unchanged product/workflow bytes retain CI **34578515990** and docs **34578515965**
at **`e1ab15c`**: all 29 normal jobs and all 12 suites **2,194 passed / 36 skipped**,
89.67–89.69% hosted branch coverage, and byte-verified wheel/sdist sources. This is
compatible reuse, not a new full-suite pass at the evidence-only delivery. The
whole 25 development reuse and 45 + 45 historical gates remain passed under their
actual approval, as do the three exposed SSRF families at measured `2ac39aa`.
Original held-out misses/failures, the Meta erratum and separate Kubernetes
suspicion remain visible. Git campaigns remain incomplete (312/1,040 attempts);
six production requests retain zero-call replay bindings. Paid benchmark/pilots
remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, release,
ready-state, outreach or Phase 23 work is authorized. “v24” names evidence only.

## Historical v23 source-novelty checkpoint

Replacement-v4 **fails the independent-fresh-source checkpoint before execution**.
Its vulnerable 21-file extracted tree is byte-identical to the original held-out
`auth-fetch-mcp` tree. All fixed `src/` files are also identical; only package
version/dependency metadata differs. Those earlier inputs already completed
native and Semgrep evaluation on September 9. Different Git revisions and new
helper renames do not establish fresh independent sources.

The comparison and original report hashes are retained in
`artifacts/phase22/integration/v23-freshness-assessment.json`. Earlier v4
preparation/hash checks and proposals remain preserved; they did not check
novelty against the original corpus. The prepared v4 runner was delivered for
review but remains unapproved and undispatched. No new native/comparator
observations, target execution or paid calls occurred; its proposed 15-run
budget was never authorized.

R66, R88 and R84 remain unresolved; the 89 original rows remain 84 passed and
two user-deferred. Historical whole-batch timing and all three exposed SSRF
regressions retain their passing source-bound evidence. Phase 22 remains
incomplete. The user approved source-only recovery; the exact receipt is
`artifacts/phase22/integration/v23-source-only-recovery-authorization.json`.
Replacement-v5 is prepared in `artifacts/phase22/corpus-replacement-v5/`: one
Lighthouse MCP source pair outside all prior repositories and 92 effective trees,
with no matching source-file hashes. All 12 files per revision and MIT license
are retained. The narrow condition is literal link-local rejection before Chrome
launch through `run_audit`; two reversible predicate renames and a public control
are correlated variants. Upstream intentionally permits loopback; DNS/redirects,
IPv6, successful navigation and runtime exploit proof are outside these labels.
The same agent curated after scanner `1f3f72f` froze; no independent human or
unseen-source claim. The Git command-injection research candidate was rejected
because it cannot fill the unchanged SENT-015 slot. The new exact evaluation
proposal is **unapproved and unevaluated**: 10 native plus five Semgrep observations,
one standard Linux 90-minute job, 120-second target/300-second whole-input maximum,
zero retries, target executions or paid calls. No v4 or historical budget transfers.

Current preparation CI **34578515990** and docs **34578515965** pass at
**`e1ab15c`**: all **29 normal jobs**, all **12 quality suites with
2,194 passed / 36 skipped**, and three optional measurement jobs skipped.
CI checkout is synthetic merge `c044a1a`, whose complete tree equals `e1ab15c`.
Hosted branch coverage is **89.67–89.69%**; wheel/sdist source members
are byte-verified against that Git revision. The earlier `1942760` CI
retains 28 successful jobs and one cancelled final hook job; all its
12 test suites completed, but it is **not** a whole CI pass.
The new 56-row added-scope audit retains three historical failed checkpoints
with budgets closed or never approved; its other 53 rows pass. The original 89-row audit
remains 84 passed, two user-deferred and three unresolved. Zero fresh
observations or additional paid calls. Exact source-only preparation,
novelty, approval and execution-proposal bindings are retained; evaluation
and technical acceptance remain unapproved.

Final human technical acceptance has not been requested. Paid benchmark/pilots
remain deferred, Phase 21 incomplete and Phase 24/15 unchanged.


The user approved this policy with “okay go ahead with this.” on 2026-09-10.
It replaces the 120-second hard timing requirement prospectively. It does not
change the outcome of any earlier measurement or establish a speed improvement.

## Target and maximum

Deterministic static analysis has a **120-second normal performance target** and
a **300-second shared deadline**. The same policy applies to every input, on
every supported platform. A fast scan returns as soon as it finishes. A slow
scan continues in the same execution after 120 seconds; it is not killed and
restarted. The caller may supply an earlier deadline but cannot extend the
engine beyond 300 seconds.

The engine, source-flow workers, Semgrep batches and TypeScript parser use the
remaining shared deadline. Coverage/report assembly must also finish before
the deadline. Expiry is an infrastructure failure, never a completed clean scan;
worker failure and interruption retain termination and reaping of all children.
Checks inside Python analysis are cooperative. The proposed Linux measurement
supervisor additionally enforces the whole-input wall-clock limit and reaps the
process group; cleanup and evidence upload have a separate job reserve.

This is the deterministic static budget. It is not a five-minute cap on a full
static + model review + dynamic invocation. Model review, dynamic campaign and
Semgrep's existing per-rule/per-file safety limits keep their own budgets.
The native Finding/report schema and detector semantics are unchanged.

## Measurement and reporting

New timing assessments retain both native scan duration and whole-input elapsed
time, alongside completion, findings, coverage, warnings and source identities.
Whole-input time includes source materialization, configuration, scan, report
validation and writing. The supervisor has a 300-second limit from the start
of that input; it does not grant a fresh 300 seconds after setup.

| Classification | Requirement |
| --- | --- |
| `completed_within_target` | Complete analysis and both native and whole-input times at most 120 seconds |
| `completed_using_extended_time` | Complete analysis and both times at most 300 seconds, with at least one above 120 seconds |
| `incomplete` | Deadline expiry, interruption, invalid report or another incomplete execution |

Retain the underlying incomplete reason; do not describe every failure as a
timeout. A complete report written after the whole-input cap is retained as raw
evidence but does not pass the timing gate. No rounding tolerance silently turns
an over-limit duration into a pass. Classification is assessment metadata;
the existing static `duration_ms` and raw reports remain available without
adding timing-dependent findings or changing warning order.

## Historical v20 diagnostic checkpoint

The original standard-Linux run at `7555a9d` completed 15 of 25 development
inputs under 120 seconds; all ten Meta inputs timed out and both historical
batches were skipped. Those results remain unchanged. The successful Stage 0
probe at `0b71a29` failed its prospective throughput premise; no partitioning
or micro-optimization is included in this policy change.

The approved diagnostic covered the two named slow Meta inputs, each twice:
`meta-image-ssrf-vulnerable` and `meta-operator-fallback-fixed-mutation`.
Run 34550284556 completed all four native observations within 300 seconds in one
standard Linux job; 0/4 met 120 seconds. Reports matched retained references
and repeats in their entirety and order. Zero paid calls, profiles, target
execution or retries occurred. The approval and budget are consumed; this
document does not authorize additional runs.

After this diagnostic pass, the entire 25 + 45 + 45 sequence remains a separately
approved gate, with its original detection conditions and repeat equivalence.
Its revised timing requirement is completion within 300 seconds per input,
with the count meeting the 120-second target reported separately. The former
240-minute total job budget cannot simply be reused for the larger input cap;
the next proposal must bound each sequential job and the total run budget.

Fresh evaluation after stabilization, final human acceptance, and complete
evidence/draft delivery remain required. Phase 22 is not complete. The policy
approval does not authorize new paid calls, a runner upgrade, merge or release.

## Historical v20 candidate verification

Candidate `1f3f72f` passes the local full suite (2,194 passed, 36 skipped), all 29
normal hosted CI jobs and docs. Workflow candidate `71906a7` also passes fresh normal
CI/docs; its scanner bytes equal `1f3f72f`. The four-observation diagnostic passes,
while the full 115-observation proposal is unapproved and unexecuted. See the [integration evidence index](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/README.md).

## Current full-sequence result

The approved **98-observation assessment refresh passes** at
scanner **`1f3f72f`**, final workflow **`61b19ae`**, run **34566835295**.
It consumed **98/98** observations; **98** completed.
**72** completed within the 120-second target and
**26** used extended time within the 300-second maximum.
The longest whole-input execution took **176.032 seconds**.
All consumed attempts and any closed remainder are retained in `v22-refresh-disposition-corrected.json`.

Both whole historical batches pass **45/45**, each with **20/20 vulnerable
condition hits** and **zero matching alerts on 25 negatives**. All 45 entire ordered
reports match across the pair, excluding only the established volatile fields.
The previously passed whole **25-input development batch** at identical scanner
bytes is reused under the user's explicit scope amendment: 10 vulnerable hits,
exactly two raw Meta operator erratum alerts, and zero matching alerts on 13 valid
negatives. These results measure completion under the approved timing policy.

The eight preparatory observations completed, and all 45 historical assessments
were frozen before the final dispatch. The retained 37 plus new eight reports
were used only for source assessment, never presented as a whole-batch execution
pass. Five preparatory report deltas include 1,191 individually source-assessed
diagnostic changes. The additional `kubectl_logs` command-injection suspicion is
separate from the unchanged `kubectl_get` benchmark condition; it remains visible,
without claiming runtime proof. Final reports have no new canonical deltas.

The original **15/25** Linux result at `7555a9d`, its ten 120-second Meta timeouts,
and the later **62-attempt stale-assessment stop** in run 34555414891 remain
preserved failures. Neither result is relabeled or its closed budget reopened.
No detector, condition label, prerequisite, deadline or target source changed.
No paid calls, profiles, benchmark retries or target execution occurred.

Final CI **34566768988** passes all **29 normal jobs** and documentation
**34566768974** passes. All 12 quality suites pass **2,194 tests with 36 skips**.
The wheel and sdist retain byte-verified source bindings. Local coverage, six
zero-call production replays and Git runtime compatibility retain their exact
source evidence. Git's 13 campaigns remain incomplete (312/1,040 attempts);
the three exposed SSRF families retain their passing regressions at `2ac39aa`.

The next separate checkpoint is **replacement-v4 freeze/evaluation**, prepared
but **unapproved and unevaluated** in `artifacts/phase22/corpus-replacement-v4/`:
10 native and five Semgrep observations, one standard Linux job, 300 seconds per
whole input, a 90-minute job limit and zero paid calls. Its independent repository
pair was curated after the immutable scanner freeze; source exposure and
correlated variants are disclosed. No independent human or unseen-source review
is claimed.

The 89-row audit is **84 passed, two user-deferred and 3 unresolved**.
**Phase 22 remains incomplete** pending actual remaining gates and explicit final
human technical acceptance. The original held-out result remains 10 completed,
10 unsupported and five incomplete, with zero hits among four completed vulnerable
inputs out of ten vulnerable inputs total. Paid benchmark and pilots remain
deferred; Phase 21 stays incomplete, and Phase 24/15 gates are unchanged.
No merge, release, outreach or Phase 23 work is authorized.

### Historical v21 sequence and proposal checkpoint

The approved full Linux sequence at scanner **`1f3f72f`**, workflow **`e7131f0`**,
run **34555414891**, **does not pass**. It consumed
**62/115 native observations**: **40** completed within
the 120-second target and **22** used extended time within the uniform
300-second native/whole-input maximum. Raw durations, cleanup, reports, condition
scores and source-assessed deltas are retained in `v21-sequence-assessment/` and
`v21-source-delta-assessment/`. The dispatch budget is closed; no retry, profile,
source tuning, target execution or paid call occurred.

Development passes **25/25**. All **37 attempted** historical inputs also complete within
300 seconds; there are **zero timeouts among 62 attempts**. The run stops on
`kubernetes-shell-vulnerable` because the old assessment expects 24 findings and
the current scanner produces 25. Source review confirms the added `kubectl_logs`
cronjob command-injection suspicion is separate from the named `kubectl_get`
condition, whose existing hit remains. Post-run source review records **19/19**
observed vulnerable condition hits and **0 matching alerts on 18 observed** negatives.
The original gate stays failed, **8 inputs** in the first historical batch remain
unstarted, and the entire 45-input repeat is skipped. All **53 unused** observations
are closed; these are not timeout failures or permission to resume.

The next exact proposal is **unapproved**:
`v21-historical-assessment-refresh-proposal.json`. It requests **98 new native
observations**, two dispatches: 8 preparatory inputs to freeze complete source-bound
assessments, then two **whole 45-input historical batches**. It explicitly asks
to reuse the already passed whole 25-input development batch at identical `1f3f72f`
bytes. The 37 + 8 preparatory reports never count as a whole 45-input execution pass. The
limits remain 300 seconds per whole input and 120 seconds as the target, with
60/245/245-minute job limits, zero retries, profiles, comparators or paid calls, and
no detector/label change. A failing or unresolved preparatory condition closes
the 90-run final budget. Strict identity and ordered-repeat checks remain in the
final pair. See the disposition for exact source evidence and timing.

This is a completion result under the approved timing policy, not a speedup.
The original Linux result at `7555a9d` remains **15/25 complete, ten Meta timeouts
at 120 seconds and both historical batches skipped**. Scanner/test/package bytes
remain `1f3f72f`. Fresh CI **34555415861** passes all **29 normal jobs**; every one
of 12 quality suites passes **2,194 tests with 36 skips**. Docs **34555415860**
passes. Prior local coverage, six zero-call production replays and Git runtime
compatibility retain their exact source bindings. Git campaigns remain incomplete;
all three exposed SSRF families retain their passing regressions at `2ac39aa`.

A later separate checkpoint is the **unapproved replacement-v4 freeze/evaluation** in
`artifacts/phase22/corpus-replacement-v4/`. Its independent auth-fetch-mcp source
pair was curated after the scanner freeze, without running a detector/comparator.
The proposal permits **10 native and 5 Semgrep observations** in one standard
Linux job, 300 seconds per whole input, 75 nominal input-minutes, a 90-minute job
limit and zero paid calls. Source exposure and correlated variants are disclosed;
there is no independent human or unseen-source review claim.

All 89 original requirements are **72 passed, 2 user-deferred,
15 unresolved**. **Phase 22 remains incomplete** pending the
remaining gates and explicit final human acceptance. The original held-out result
remains 10 completed, 10 unsupported, 5 incomplete, with 0 hits among 4 completed
vulnerable inputs out of 10 vulnerable inputs total. Paid benchmark/pilots remain
deferred; Phase 21 incomplete and Phase 24/15 unchanged. No merge/release/outreach.
