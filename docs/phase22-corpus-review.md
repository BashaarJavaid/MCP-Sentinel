# Phase 22 independent corpus freeze packet

## Current v34 correction and regression approval checkpoint

The DDG fixed-request correction is implemented at **`a50e9b7`**. SENT-015
follows source-established HTTPX `build_request` → `send`, retaining a narrow
initial shared-space (`100.64.0.0/10`) rejection qualification on the same caller
URL. Removing/bypassing the guard or replacing/escaping the request loses that
qualification in synthetic controls. Known IP type inspection preserves valid
facts; local module/package shadows, replaced classes/imported attributes and
unknown mutation stay conservative.
The old six negative IP flags alone no longer establish CGNAT rejection. Broader
destinations, subsequent transformations, DNS, redirects and IPv6 remain unproven.

Current engineering passes at **`8a3db58`**: **2,280 tests / 36 skips** locally
and in all **12 supported hosted suites**, **89.87%** local branch coverage,
all **29 normal CI jobs** and docs. Ruff/format/strict mypy, lock/schema/notices,
offline artifacts, installed-wheel/Docker/isolation/hooks and exact package-source
checks pass. All **six production requests regenerate and replay with zero paid
calls**. The initial candidate's full-suite failure, failed/cancelled CI jobs,
additional replacement control, disk exhaustion and interrupted verification are
retained, including the local-module identity failure after the earlier full pass.
The final import-binding correction passes a new full suite and hosted matrix.

**Actual corrected DDG coverage is not yet evaluated.** The exact proposal at
`artifacts/phase22/integration/v34-import-binding/evaluation-proposal.json`
requires separate approval: **87 native observations**, one serial local macOS
sequence, **zero comparator runs, retries, profiles, paid calls or corpus target
executions**. The five unchanged DDG inputs run twice (10), 15 Python development
inputs once, and 31 Python historical inputs twice (62). The target is 120 seconds,
the uniform native/whole-input maximum 300 seconds, cleanup at most 15 seconds,
and sequence maximum 480 minutes. Execution/identity/schema/cleanup/timing/repeat
failure closes all unused observations; detector outcomes are retained for source
assessment. No old budget is reopened.

The gate requires actual fixed-source `send` coverage with initial CGNAT rejection
evidence, both vulnerable detections per DDG batch, unchanged Python named
conditions and **36 entire ordered repeats**. Source-sensitive synthetic controls
are separate engineering evidence. All changed findings and diagnostics require
source assessment. Preserve the two nominal fixed Meta operator erratum inputs,
each with its retained two matched keys, separately from the seven valid Python
development negatives. The unchanged TypeScript paths support reuse of the prior
54-observation compatibility and ten-observation Lighthouse results at `f85a90f`.
Historical whole 25 + 45 + 45 Linux timing remains measured at `1f3f72f`; these
partial checks will not be pooled into a new whole-batch result.

The original **DDG fresh detection at `f85a90f` remains immutable**: two correlated
vulnerable hits in each native batch, zero matching negative alerts and five
ordered repeats; fixed request/guard recognition was unresolved. The correction
follows source exposure and is an exposed regression, not another unseen success.
Original Lighthouse fresh misses, original held-out misses and all earlier failed
attempts remain preserved. Git campaigns stay **312/1,040 incomplete**, as requested.
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.

The current audit accounts for **89 original requirements** (69 passed, two
user-deferred, 18 pending current-source regression/acceptance) and **94 added
rows** (87 passed, five historical proposed limitations, two unresolved). The
pending original rows converge on this regression and its assessments. **Phase 22
remains incomplete** until the actual remaining gates, explicit human technical
acceptance and verified final closeout delivery. No merge, ready-state, release,
outreach or Phase 23 is authorized.


## Historical v33 fresh detection and acceptance checkpoint

The approved **replacement-v6 fresh evaluation passes its frozen output gate**
at scanner **`f85a90f`**, selected before source curation. The new repository is
**isyuricunha/mcp-ddg-research**, absent from seven prior manifests and 96 unique
source trees. Both native batches detect **2/2 correlated vulnerable variants**
and produce **zero matching alerts on three fixed/control inputs**. All **five
entire ordered repeats agree**. All **15 observations** completed: 10 native and
five pinned Semgrep; Semgrep detected **0/2** vulnerable variants. The native
maximum is **8.452 seconds**, comparator maximum **21.079 seconds**, and local
sequence **201.977 seconds**. Zero retries, target execution or paid calls; the
budget is closed. This is one repository and one narrow vulnerability, not broad
accuracy, independent human review or runtime proof.

**Fixed guard recognition is not established.** The native finding identifies the
registered `web_fetch` caller URL reaching `client.get` without sufficient destination
restriction, which includes the missing `100.64.0.0/10` rejection. Upstream also
changed fixed HTTP access to `build_request`/`send`, which Sentinel explicitly
reports as unresolved. Zero fixed alerts therefore establish the measured output
contrast, not recognition of the CGNAT fix or complete fixed-path coverage. This
limitation is prominently proposed for explicit human acceptance, never silently
accepted. All **80 findings, 3,308 warnings, 3,058 unresolved-flow occurrences and
60 recognized surface occurrences** are source-assessed. The 76 unmatched findings
include framework-validation and hashed-cache-path false positives under stated
source prerequisites; raw findings and unresolved coverage remain visible.

Current exposed Lighthouse and the three prior SSRF repeat gates remain passed.
The existing 54-observation compatibility packet and historical whole 25 + 45 + 45
Linux evidence retain their actual source bindings; no new whole-batch timing
claim is made. Product/test/package/workflow bytes equal tested **`439c3fe`**:
**2,242 tests / 36 skips**, **89.76%** local branch coverage, all **29 normal CI
jobs** and docs passed. Six production-request replays retain zero-call evidence.
Git campaigns remain **312/1,040 incomplete**, as the user instructed.

Original fresh Lighthouse misses at `1f3f72f` and original held-out failures remain
unchanged; later Lighthouse passes are exposed regressions. All earlier failed
optimizations, stale-assessment stops, invalid v4 novelty and corrective attempts
remain preserved with closed budgets. The audit contains **89 original rows:
86 passed, two user-deferred and one pending acceptance**, plus **88 added rows:
82 passed and six proposed documented limitations awaiting decision**.
**Phase 22 remains incomplete** until explicit human technical acceptance and
verified closeout delivery. Paid benchmark/pilots remain deferred; Phase 21 stays
incomplete and Phase 24/15 gates are unchanged. No merge, ready-state, release,
outreach or Phase 23 is authorized.

## Historical v32 fresh preparation checkpoint

The user requires **detection on another previously unused repository before
Phase 22 technical acceptance**. Git runtime campaigns stay incomplete at
**312/1,040** as the retained limitation; no additional Git work is planned.
The earlier v31 acceptance packet is preserved and its readiness is superseded.

Replacement-v6 prepares **isyuricunha/mcp-ddg-research** at immutable scanner
**`f85a90f`**, frozen before new source research. Novelty checks cover seven prior
manifests and **96 unique source trees**, with no matching source files. The
upstream pair changes initial rejection of `http://100.100.200.200/` in shared
address space. Complete source archives, prerequisites, two correlated helper
renames and a fixed-tree public control are retained. Source review is by the
same implementation agent after freeze; no independent human review is claimed.

`artifacts/phase22/integration/v32-fresh-v6/evaluation-proposal.json` is
**unapproved and unexecuted**: one local macOS sequence, **10 native + 5 Semgrep
observations**, 120-second target, 300-second whole-input maximum, 90-minute
sequence cap, no retries, target execution or paid calls. The prospective native
gate requires both vulnerable hits and zero matching alerts on three negatives
in each five-input batch, plus all five ordered repeats. A later repair on this
same source cannot become an unseen-source success. Existing measurements and
all original failures remain unchanged.

The audit is **84 passed, two user-deferred and three unresolved**, plus
86 added rows: **80 passed, five proposed historical limitations awaiting
decision and one unresolved**. **Phase 22 remains incomplete**. Exact evaluation
approval, actual detection/source assessment, explicit human acceptance and
verified closeout delivery remain. Paid benchmark/pilots stay deferred;
Phase 21 remains incomplete and Phase 24/15 gates are unchanged.

## Historical v31 technical acceptance checkpoint

All current Phase 22 technical gates are ready for **explicit human acceptance**.
**Phase 22 remains incomplete** until that decision and subsequent closeout delivery.

At frozen scanner **`f85a90f`**, the approved local compatibility sequence passes
**54/54 observations**: each of SearXNG, fetch-mcp and open-webSearch completes two
whole five-input batches with two correlated vulnerable hits and zero matching
condition alerts on three negatives per batch. All **15 entire ordered repeats**
agree after only the established 11 volatile exclusions. The ten development and
14 historical TypeScript inputs each complete once with unchanged ordered findings
and named-condition outcomes: **4/4** and **6/6** vulnerable hits, respectively,
and zero matching alerts on six and eight negatives. These are partial compatibility
checks, never a pooled whole-batch execution claim.

All 54 observations meet the **120-second target**, with a longest whole input of
**114.274 seconds**, within the uniform 300-second maximum. The single serial
sequence took **2,363.732 seconds**. JSON/SARIF and owned process cleanup validate.
All **3,216 changed diagnostic occurrences** are individually source-assessed:
1,080 warnings and 2,126 unresolved flows added; five warnings and five flows removed.
Unchanged findings retain their exact source-assessed references. Diagnostic removal
does not prove runtime safety; unresolved coverage and raw unmatched scorer keys remain
visible. **One sequence and all 54 observations consumed; zero budget remains.**

The separately approved Lighthouse regression passes **10/10** at the same scanner,
workflow `75142f0`, run
[34648036083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34648036083).
Both whole batches detect two correlated vulnerable variants and preserve the narrow
IPv4 link-local qualifier on fixed/control sources; all five ordered repeats agree.
Its 10 findings, 974 warnings, 624 unresolved-flow occurrences and 20 unresolved
surfaces are source-assessed. Broader SSRF candidates remain visible.

The accepted whole **25 development + 45 historical + 45 historical** Linux gate
retains measured scanner **`1f3f72f`**. The 98-observation refresh completed all inputs:
72 within 120 seconds, 26 using extended time, maximum **176.032 seconds**.
Each whole historical batch has 20/20 vulnerable hits and zero matching alerts on
25 negatives. Whole development reuse retains ten vulnerable hits, two raw Meta
operator erratum alerts and zero matching alerts on 13 valid negatives. Source-only
AST/configuration proof establishes unchanged Python paths for 15 development and
31 historical inputs. Current TypeScript compatibility does not relabel old timing
or establish a new whole-batch Linux performance result.

Product, tests, packages and workflows still equal verified **`439c3fe`**: local
and all 12 hosted suites pass **2,242 tests / 36 skips**, local branch coverage
**89.76%**, all **29 normal jobs** and docs pass. Packaging, installed-wheel/Docker/
isolation, Ruff/format/strict mypy, lock/schema/notices/offline artifacts and six
production-request replays retain their exact source bindings. **Zero additional
paid calls.** Git runtime/image are unchanged; 13 campaigns remain incomplete at
**312/1,040** tested attempts.

The proposed acceptance explicitly retains the original fresh-source result at
`1f3f72f`: **15 completed observations, 0/2 vulnerable hits in each native batch and
comparator**. The later corrections and passes are exposed regressions, not fresh
generalization or independent human review. The original held-out result remains
ten completed, ten unsupported and five incomplete, with zero hits among four
completed vulnerable inputs out of ten vulnerable inputs total. All earlier failed
optimizations, stopped sequences and invalid v4 novelty are preserved with their
superseding evidence; no failed attempt is turned into a pass or reopened budget.

The audit contains **89 original rows: 84 passed, two user-deferred, two proposed
documented limitations and one pending human acceptance**. Its **83 added rows**
contain 78 passed and five proposed dispositions of superseded historical failures.
Those dispositions require the actual acceptance decision; no new limitation is
accepted in advance. Pilots/full paid benchmark remain deferred and nonblocking;
Phase 21 remains incomplete and Phase 24/15 gates are unchanged. No merge, ready-state,
release, outreach, participant source sharing or Phase 23 is authorized.

## Historical v30 Lighthouse regression checkpoint

The approved Lighthouse regression **passes all 10 observations** at scanner
**`f85a90f`**, workflow **`75142f0`**, run
[34648036083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34648036083).
Both whole five-input batches detect both correlated vulnerable variants and retain
the required narrow IPv4 link-local rejection qualifier on both fixed variants and
the public control. Broader SSRF candidates remain visible. All five entire ordered
reports repeat equally after only the established 11 volatile exclusions.
Whole-input times are **11.992–14.300 seconds**, all within the 120-second target
and 300-second maximum. JSON/SARIF and owned process cleanup validate.
**Ten observations and one dispatch consumed; zero budget remains.**
All **10 findings, 974 warnings, 624 unresolved-flow occurrences and 20 unresolved
surfaces** are individually source-assessed, with zero unassessed entries.
Dispatch remains incompletely resolved; this is no runtime proof or complete coverage.

This is an **exposed regression pass**. The original independent-source evaluation
at `1f3f72f` remains 15 completed observations with **0/2 vulnerable hits per native
batch and comparator**. The stopped `6db3858` vulnerable miss and `4a2359d` fixed
qualification failure retain their closed nine- and seven-observation remainders.
No earlier failure is replaced, and no fresh generalization or independent human
review is claimed. The original held-out result remains 10 completed, 10 unsupported
and five incomplete, with zero hits among four completed vulnerable inputs out of
ten vulnerable inputs total.

Product, test, package and workflow bytes still equal verified `439c3fe`: local and
all 12 hosted suites pass **2,242 tests / 36 skips**, local branch coverage **89.76%**,
all **29 normal CI jobs** and docs pass. Packaging, installed-wheel/Docker/isolation,
Ruff/format/strict mypy, lock/schema/notices/offline artifacts and six production
request replays retain their actual source bindings. **Zero additional paid calls.**
Git runtime/image remain unchanged; 13 campaigns are incomplete, **312/1,040** tested.

The next exact proposal is **unapproved**:
`artifacts/phase22/integration/v30-compatibility-proposal/evaluation-proposal.json`.
It requests **54 serial local macOS rules-only observations** at immutable `f85a90f`:
three earlier exposed SSRF families twice each (30), followed by the 10 development
and 14 historical TypeScript inputs once (24). Bounds are 120 seconds as target,
300 seconds per whole input, 15 seconds cleanup, one 300-minute sequence, zero
retries, profiles, comparators, target executions or paid calls. Stop at the first
incomplete, late, identity/schema/cleanup, ordered-finding/condition or repeat failure;
close every unstarted observation. Every other report delta requires source assessment.
No new compatibility observation has run. Source-only AST/configuration checks bind
unchanged Python analysis for the other 15 development and 31 historical inputs.
The accepted whole 25 + 45 + 45 Linux timing/condition results retain measured scanner
`1f3f72f`; partial compatibility observations will not be called a new whole batch.

The audit contains **89 original rows: 82 passed, two user-deferred, five unresolved**,
and **81 added rows: 75 passed, six unresolved**, including closed historical failed
gates. Earlier TypeScript compatibility, the explicit disposition of fresh-result
limitations and final human technical acceptance remain open. **Phase 22 remains
incomplete.** Pilots and the full paid benchmark remain deferred; Phase 21 is
incomplete and Phase 24/15 gates are unchanged. No merge, release, outreach or Phase 23.

## Historical v29 loopback qualification checkpoint

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


## Historical v22 checkpoint

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


This page preserves the original proposal. The user subsequently authorized its
corpus and tested Git environment in `artifacts/phase22/authorization.json`.
Its first measurements and source limitations remain unchanged. The three later
SSRF replacement families are now exposed regressions; all three pass their
bounded native correction gates at `2ac39aa`. A new post-stabilization fresh
freeze/evaluation remains separately gated. See the
[current implementation status](phase22-implementation-status.md).

The four approved Meta diagnostic observations at `1f3f72f` pass within the
300-second maximum with ordered report equality. These are existing development
inputs. Full 25 + 45 + 45 and a new fresh evaluation remain separately gated.

The replacement-v4 source packet is prepared after freezing `1f3f72f`, with
no detector/comparator execution. Its exact checkpoint and bounded proposal are
in `artifacts/phase22/corpus-replacement-v4/`; explicit evaluation approval remains
pending. All v1/v2/v3 original results and exposed regressions are preserved.

## Historical proposal

**Status: prepared and independently source-reviewed; user freeze approval pending.**
The packet contains **ten independent vulnerable/fixed pairs, ten safe controls,
and 20 paired structural mutation inputs: 50 static inputs across nine repositories**.
There is one development pair and one pair from a separate held-out repository
for each of `SENT-012`–`SENT-016`. Eight pairs use upstream fixes. Two poisoning
pairs use explicitly evaluator-authored benign-description overlays for the
user to approve. No detector, model, or runtime results informed selection,
labels, fixes, controls, or mutations.

The concrete manifest is `artifacts/phase22/corpus-review/manifest.json`.
Its SHA-256 is **a5ea6930e9cd5522f9420bef57875fea5d44d1d1c45fb5136a02a7c0292a9c67**. The independent reviewer prepared and
inspected all ten source-condition records under `review/`; the machine-checked
provenance inventory is `artifacts/phase22/corpus-review/inventory.json`.

## Exact selected sources

| Rule / split | Repository | Vulnerable → fixed source | Revision-specific license |
|---|---|---|---|
| SENT-012 / development | [mastra-ai/mastra](https://github.com/mastra-ai/mastra/tree/9e4abde7cef33e3f5cb1e71bee70c6556ef394cd) | `9e4abde7cef33e3f5cb1e71bee70c6556ef394cd` → `7f2b528ba82db512d68832d2f8ad6cbc8bb46cd4` | Apache-2.0 |
| SENT-012 / held_out | [ruvnet/sublinear-time-solver](https://github.com/ruvnet/sublinear-time-solver/tree/ea9a212b69e4449ec443fe088a7aec7546f70b4a) | `ea9a212b69e4449ec443fe088a7aec7546f70b4a` → `a701296e363192be863e79d788fa268095e3d229` | MIT (nested license files retained) |
| SENT-013 / development | [IntegSec/VulnerableMCP](https://github.com/IntegSec/VulnerableMCP/tree/4cfe46227ceb56e1cbaf36233f8e9ce4ac7fbca1) | `4cfe46227ceb56e1cbaf36233f8e9ce4ac7fbca1` + proposed description overlay | MIT |
| SENT-013 / held_out | [eyemnv/mcp-tool-poisoning-toolkit](https://github.com/eyemnv/mcp-tool-poisoning-toolkit/tree/c3615352e272be735dedc22c67caf290888cf0e7) | `c3615352e272be735dedc22c67caf290888cf0e7` + proposed description overlay | MIT |
| SENT-014 / development | [dbt-labs/dbt-mcp](https://github.com/dbt-labs/dbt-mcp/tree/733bf6cc4bb0df9ef3d030e6f6610b0ef442d8b8) | `733bf6cc4bb0df9ef3d030e6f6610b0ef442d8b8` → `291ddd1baedeacd86d36c5fab470b2ad2958a67d` | Apache-2.0 |
| SENT-014 / held_out | [tumf/mcp-shell-server](https://github.com/tumf/mcp-shell-server/tree/b070bc32ed7b7884c3f0f8221e6d0d28b7554d41) | `b070bc32ed7b7884c3f0f8221e6d0d28b7554d41` → `a8e71630865332250f616631d8eb0ea4c5df1916` | MIT declaration before; full LICENSE after |
| SENT-015 / development | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp/tree/95e852793b7ff8604a8132e85d5facd08c91a36e) | `95e852793b7ff8604a8132e85d5facd08c91a36e` → `7d9926336bbdac6285a988d043c4ccfe126c94c5` | BSL-1.1; Apache-2.0 change date 2029-01-01 |
| SENT-015 / held_out | [ymw0407/auth-fetch-mcp](https://github.com/ymw0407/auth-fetch-mcp/tree/98f381d1298b6b7e7ff29d7a7851f18ea5f2364c) | `98f381d1298b6b7e7ff29d7a7851f18ea5f2364c` → `d4dedaf55c1d39228dbed58807ea1f9fac1328e1` | MIT |
| SENT-016 / development | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp/tree/9cbd8aa4c5235a5ae2f01c60eaf464c0b60ccf6a) | `9cbd8aa4c5235a5ae2f01c60eaf464c0b60ccf6a` → `14d7371d4ed77b1e9bb04ff1d00e94e00eba32a7` | BSL-1.1; Apache-2.0 change date 2029-01-01 |
| SENT-016 / held_out | [Labs64/NetLicensing-MCP](https://github.com/Labs64/NetLicensing-MCP/tree/e826d695df5a08d250dc88e9d8843ff0042ce35a) | `e826d695df5a08d250dc88e9d8843ff0042ce35a` → `fbbb1d5ff88eb5400ec933a84e75601ebee48927` | Apache-2.0 |

The manifest binds all 18 source archives, complete retained file inventories,
revision-specific license paths, source-condition references, controls, overlays,
provenance, and the repository split by hash. Repository identity comes from
retained GitHub repository metadata. The validator normalizes aliases and
checks the split across the **whole** corpus, including controls and mutations.
Meta Ads appears twice, both in development; none of the five held-out
repositories appears in development. All selected repositories are outside the
five-repository Phase 20 population.

The accepted [Phase 20 measurement](phase20-completion-v2.md), original 45
inputs, historical split, labels, costs, captures, and acceptance are unchanged.
Those inputs remain exposed regression evidence. Public historical sources
cannot establish absence of prior model exposure, even when the repository is
held out from this detector-development effort.

## Decisions in this exact freeze packet

1. **Poisoning counterparts.** Approve or reject the two concrete
   evaluator-authored fixes in `review/integsec-calculator-poisoning-proposed-fix.patch`
   and `review/eyemnv-docs-poisoning-proposed-fix.patch`. Each removes only the
   attached malicious description and retains the tool's ordinary task
   description and original handler. Their upstream snapshots remain intact.
   These are proposed benchmark fixes, not upstream security releases. Attack
   comments, unrelated vulnerabilities, and detached strings remain in source;
   only the stated metadata condition is labeled fixed.
2. **Source scope.** Mastra is a complete `packages/mcp-docs-server` snapshot
   plus root license, README and package/workspace declarations. The original
   repository archive exceeds the existing 32 MiB ceiling. The solver snapshot
   retains its entire repository except the 26,923,866-byte generated
   `data/emergence/session_memory.json` dataset, which exceeds the 16 MiB member
   ceiling. Both scope decisions are explicit in four `*-projection.json`
   records with original archive hashes, selected-file hashes, and every
   omitted path/size. Relevant target source bytes were preserved. The existing
   archive ceilings were not changed. These are new-corpus scope choices,
   independent of detector results; no existing Phase 20 source was excluded.
3. **License details.** Meta Ads remains BSL 1.1 today, with its exact terms and
   2029 change date retained. It is not Apache-2.0 today. The earlier shell
   snapshot declares MIT in `pyproject.toml` and README but has no LICENSE file;
   those exact declarations are retained, together with the later upstream
   revision's full MIT text. Nested solver license/notice files are retained.
   The proposed use is a source-only, non-production benchmark; this packet
   does not authorize product publication or change upstream terms.

Invariant's unlicensed candidate was **not selected**. NYIT's direct-poisoning
example substantially reproduces Invariant text and was also excluded from the
final pair selection. Earlier investigative metadata remains in `provenance/`
for traceability but is not an input. The selected poisoning implementations
come from separate MIT-licensed repositories with different implementations
and descriptions; they are not two files or forks of one selected source.

## Source review and condition limits

Every pair has a source review in `review/<pair>.json`, cited complete source
files, prerequisites, an exact matching condition, a safe-control condition,
and mutation instructions. Findings qualify by the described boundary and
relevant evidence, not merely rule ID or overlapping lines. Unrelated warnings
remain separately adjudicated or explicitly unadjudicated.

- **Containment:** Mastra's condition is the directory-suggestion fallback after
  rejection, excluding colliding prefixes and symlinks. The solver condition
  concerns a caller-selected vector destination and its basename/directory
  restriction; operator-controlled ordinary ancestors are prerequisites.
- **Poisoning:** the attached descriptions explicitly demand secrets or
  unrelated behavior. The fixes remove the attached requests while retaining
  functional handlers. Model obedience and exploit success are not inferred.
- **Options:** dbt's selector tokens and the shell server's Git external-alias
  option are separate argument semantics. A shell-free argument list is not
  itself a defense. The Git label does not claim all execution-capable Git
  configuration keys are fixed.
- **SSRF:** labeled flows concern literal private/loopback URLs and prohibited
  schemes, including a separate literal canonicalization case. No DNS-rebinding
  coverage is claimed.
- **Credentials:** each condition concerns an HTTP request with no caller
  credential reaching an operator credential fallback. The fixed labels do not
  generalize to invalid-but-present credentials or all tenant-isolation paths.

Controls use ordinary permitted source paths/values or benign tool metadata,
with their own non-contradictory prerequisites. They reuse the paired fixed
source revision (or the same original source for an unrelated benign tool),
so they are **correlated source-conditioned controls**, not ten additional
independent repositories or whole-repository safety labels. Paired structural
mutations rename internal identifiers consistently on both vulnerable and fixed
sides. Python mutations use identifier tokens, preserving strings/comments;
TypeScript changes target bounded identifiers. No renamed identifier is an
attribute name, and affected imports/call sites are preserved. Exact effective
file and tree hashes bind the resulting variants. Mutations are not additional
independent pairs.

This packet is a **static treatment**. TypeScript runtime execution remains
unsupported. The Python source conditions require host-model behavior, HTTP
services, or command-specific environments that this packet does not supply
to the existing four runtime templates. In its inherited input format,
`runtime_applicability: unsupported` denotes that targeted runtime treatment;
startup and discovery for these new inputs remain explicitly **untested**.
It does not claim their Python stdio transports are unsupported in general.
Existing Phase 20 Git startup/discovery evidence is measured separately.

## Verification and handling

The Phase 22 validator reuses Phase 20 archive, artifact, source/evidence,
overlay and tree-hash validation without modifying the historical validator.
It checks all 50 inputs, exact population, per-rule split, global repository
aliases, licenses, source roots, and mutation lineage, and cannot mark itself
approved. The targeted regression test rejects forged approval, repository
alias leakage, escaping scan roots, and invalid mutation parents. Ruff,
formatting and strict mypy passed for the validator/test; its test passed.

Reproduce the checks without importing or running any upstream server:

```bash
python -m scripts.phase22_corpus
PYTHONPATH=. python artifacts/phase22/corpus-review/prepare_packet.py
pytest tests/test_phase22_corpus.py --no-cov -q
```

The generator regenerates exact overlays and labels from the retained source
archives and reviewed case records. Approval applies to the final manifest and
bound bytes, not to future regeneration with changed records. An explicit
user approval record is still required before freezing or evaluating held-out
inputs. The main implementation agent has not inspected held-out source or
used it for detector tuning. Keep `artifacts/phase22/corpus-review` review-only.
If source/results later inform a fix, mark the affected repository exposed and
prepare a replacement holdout before claiming fresh performance.

**No scan accuracy, paid evaluation, runtime execution, external validation,
or Phase 22 pilot acceptance is established by this packet.**

## Approved replacement freeze and Meta erratum

The original proposal and approval remain unchanged. The user separately approved
`artifacts/phase22/corpus-replacement-v1/manifest.json`, SHA-256
`159278d40a7d6fe2faa1c240a26f51009b37cdca30c862d5e9df1d66a6fed0da`,
for source-only deterministic and pinned comparator evaluation of its five
open-webSearch replacements. The other 45 records are unchanged. This is not a
fresh entire holdout; prior exposure and original measurements remain visible.
The additive authorization restricts input IDs and treatments. No target execution,
new detector tuning or paid model evaluation is approved by this freeze.

The user also approved `artifacts/phase22/meta-fixed-label-erratum-v1/packet.json`:
retain the frozen Meta condition and all original labels/results, with an erratum
for the alternate SSE-response configuration. The two affected fixed cases remain
visible as source counterexamples. The valid fixed/safe denominator is 13 with
zero condition false alarms; two erratum cases are reported separately. Original
raw scoring still shows two alerts among 15 nominal fixed/safe cases. This is not
runtime confirmation, a newly enlarged vulnerable denominator or human validation.
