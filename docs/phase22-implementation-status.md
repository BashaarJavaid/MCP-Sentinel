# Phase 22 implementation status

## Current v38 regression pass and technical acceptance checkpoint

The separately approved **87-observation exposed regression passes** at frozen
scanner **`8c62567`**. All **87/87** inputs complete and all **36 entire ordered
repeats agree**, excluding only the established 11 volatile fields. Native JSON,
SARIF, source/configuration identities and process cleanup validate. **74**
observations finish within the **120-second target** and **13** use the approved
extended allowance. Maximum whole-input time is **157.750767 seconds**;
maximum native time is **148.514 seconds**, both within the uniform
**300-second maximum**. The single serial macOS sequence took
**3757.993 seconds**. Its **87-observation budget is closed**;
zero retries, profiles, comparators, corpus target executions or paid calls occurred.

DDG detects **both vulnerable variants in each batch**. All **six fixed/control
reports** support the actual prepared-request `client.send` and retain recognized
initial **100.64.0.0/10 rejection on the direct `web_fetch` caller route**. The
build/send calls are no longer unresolved. There are **zero matching alerts on
all three negative inputs per batch**. Broader SSRF findings remain visible;
other caller routes, later transformations, DNS, redirects, IPv6 and broader
destination protection remain unestablished. This resolves the requested actual
fixed-path coverage gate without accepting the earlier unsupported-path limitation.

Python development completes **15/15**: **six vulnerable condition hits**, **zero
matching alerts on seven valid negatives**, and the unchanged Meta operator
erratum: **two nominal fixed input cases, each with two raw matched candidate
keys**. Meta image fixed/control reports retain their narrow private-literal
qualification at all three request sinks. Each whole **31-input Python historical
batch** passes with **14 vulnerable hits and zero matching alerts on 17 negatives**.
All source labels, prerequisites and unrelated candidates remain unchanged.

Against the immediate `a50e9b7` regression, there are **15 description-only finding
changes**, individually assessed against exact retained source: six DDG direct-route
qualifications and nine Meta private-literal qualifications. No findings are added,
removed or reordered; no warnings, unresolved flows, coverage, surfaces or counters
change. Earlier source-assessed deltas against original references remain bound to
their actual reports. Raw scorer identities and unmatched broader candidates stay
visible. This is source-grounded static evidence, not runtime protection proof.

The original fresh repository **`isyuricunha/mcp-ddg-research`** remains measured
at pre-curation scanner **`f85a90f`**: **10 native + five Semgrep observations**,
two correlated vulnerable hits per native batch, zero matching negative alerts,
five whole ordered repeats, and **Semgrep 0/2**. Its original fixed-path coverage
gap remains recorded. The later `8c62567` correction is **exposed regression**;
it does not replace that first-frozen result. This is one repository and one narrow
vulnerability, curated by the implementation agent after scanner freeze, with
source exposure disclosed; no independent human review, broad accuracy or
training-data novelty is claimed.

Prior exposed TypeScript families, Lighthouse and TypeScript compatibility retain
their actual **`f85a90f` source-compatible evidence**. Historical whole Linux timing
retains **`1f3f72f`**: both whole 45-input batches pass, with the explicitly approved
reuse of the previously passed whole 25-input development batch. Current Python
and prior TypeScript subsets are **not pooled into a new whole-batch execution**.
All original misses, the failed `a50e9b7` regression, stopped experiments and closed
budgets remain preserved. No speedup or new fresh-source result is claimed.

Product, tests and workflows are unchanged from verified **`8c62567`**. Local and
all **12 hosted quality suites pass 2,283 tests / 36 skips**; local branch coverage
is **89.91%**. All **29 normal CI jobs** and docs pass at that
actual source. Package source bindings and six zero-call production replays retain
their verified source identities; final status-only documentation/package metadata
is checked separately. Existing Git runtime components/image remain compatible,
and **Git coverage stays incomplete at 312/1,040 attempts**, as the user requested.

The initial delivery preflight stopped before staging, commit or push because six
status-document hashes in the audit had not been refreshed after documentation
edits. The failed receipt and seal 65 remain preserved. Final documentation
bindings are corrected in supplemental seal 66; scanner and evaluation evidence
are unchanged.

The reconciled audit accounts for **89 original requirements: 86 passed, two
user-deferred and only R84 (human technical acceptance) unresolved**. All **108 added
scope rows** are retained: **103 passed and five historical closure dispositions
awaiting explicit acceptance**. Those five preserve the failed optimization,
stale-assessment sequence, reused-source preparation and two stopped Lighthouse
corrections; accepting their closure never converts failures into passes.

The concrete **technical acceptance proposal** is
`artifacts/phase22/integration/v38-guard-regression/acceptance-proposal-final.json`.
**Human technical acceptance has not been received; Phase 22 remains incomplete.**
Acceptance must explicitly cover the final technical scope and retained limitations,
then the authorized closeout must be delivered to existing draft PR #37. The full
paid benchmark and pilots remain user-deferred; Phase 21 remains incomplete and
Phase 24/15 gates are unchanged. No paid calls, further observations, merge,
ready-state change, release, outreach or Phase 23 is authorized by this packet.


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


## Historical v22 historical assessment refresh

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

### Historical v20 diagnostic and full-sequence proposal checkpoint

The approved Linux diagnostic **passes all four observations** at scanner
`1f3f72f`, workflow `71906a7`, run **34550284556**. Both named Meta inputs complete
twice, with valid native JSON/SARIF and **entire ordered reference/repeat equality**.
Whole-input times range from **137.833 to 144.225 seconds**;
**0/4** meet the 120-second target and **4/4** use the extended allowance.
All are within the approved 300-second maximum. Each owned process group is
reaped. Four observations and the single dispatch are consumed; no retries,
profiles, tuning, target execution or paid calls occurred. The raw fixed-label
Meta operator alert and approved source erratum remain unchanged.

Only the optional diagnostic workflow changed. Scanner/test/package bytes equal
`1f3f72f`; the prior local **2,194 passed / 36 skipped**, **89.68%** branch coverage
and six zero-call production replays remain valid source-bound evidence.
Fresh CI **34550284081** passes all **29 normal jobs**, with **2,194 passed /
36 skipped** in every one of 12 suites; docs **34550284214** passes. The unchanged
Git image/runtime evidence still describes 13 incomplete campaigns: 1,040 planned,
312 tested and 728 remaining; this is not complete Git coverage. All three
exposed SSRF families retain their passing source-bound
regressions at `2ac39aa`; they are not fresh generalization results. The original
held-out baseline remains 10 completed, 10 unsupported and 5 incomplete, with zero
hits among 4 completed vulnerable inputs out of 10 vulnerable inputs total.

This is a two-input diagnostic, **not a full corpus timing pass or a speedup**.
The original Linux gate at `7555a9d` remains **15/25 complete, ten Meta timeouts at 120 seconds,
both historical batches skipped**. The prospective policy remains a 120-second
target and uniform 300-second maximum. No earlier result is relabeled.

The next exact proposal is `v20-full-linux-sequence-proposal.json`, **unapproved**:
one 25-input development batch then two 45-input historical batches,
**115 native observations**, one
dispatch across three dependent standard Linux jobs with **145/245/245-minute**
limits (635 minutes total maximum), no retries/profiles/paid calls. The next job
starts only after its predecessor's completion and condition gate passes. Stop
on the first incomplete, late or mismatching result; do not pool attempts.
The existing condition requirements and ordered historical repeat gate remain.

All 89 requirements remain **70 passed, 2 user-deferred, 17 unresolved**.
**Phase 22 remains incomplete.** Full timing, fresh freeze/evaluation and final
human acceptance remain separate checkpoints. Paid benchmark/pilots remain
deferred; Phase 21 incomplete and Phase 24/15 unchanged. No merge/release/outreach.

### Historical v19 timeout policy and unapproved diagnostic checkpoint

The approved **120-second performance target / 300-second static maximum** is
implemented and verified at `1f3f72f`. The same deadline applies to every input;
fast scans return immediately. The TypeScript parser and source-flow workers use
the remaining shared budget, shorter caller deadlines are honored, and coverage/
report assembly checks expiry. No detector rules or model/dynamic budgets change.

Local full verification passes **2,194 tests / 36 skipped**, with **89.68%**
branch coverage. Fresh CI **34545976337** passes all **29 normal jobs**; each of
12 suites passes **2,194 / 36**. Docs **34545976336** and the final local docs build
pass. Six production requests regenerate/replay with **zero paid calls**; Git
runtime components/image remain compatible with the retained incomplete campaigns.
Initial failing deadline regressions, lint/type-check corrections and all earlier
failures are preserved. The scanner bytes now differ from `592a9cd` and `2ac39aa`;
prior exposed detections remain source-bound regressions with deadline-only
compatibility explained in `v19-source-verification.json`.

**No new corpus timing run has occurred.** The original Linux result remains
15/25 development complete, ten Meta timeouts at 120 seconds and both historical
batches skipped. The user approved revising the prospective hard timing criterion
to 300 seconds; completion within the original 120-second target must still be
reported separately. This is no speedup or completed timing-gate claim.

`v19-linux-timeout-diagnostic-proposal.json` is prepared and **unapproved**:
two named slow Meta inputs twice each, four native observations, 300 seconds each,
one 30-minute standard Linux job, no profiles/retries/paid calls. Stop at the first
incomplete or mismatching result. Full 25+45+45 verification, fresh evaluation and
human acceptance remain separate checkpoints. **Phase 22 remains incomplete.**
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.

[Timing policy](phase22-timeout-policy.md)

## Historical v18 throughput probe at `0b71a29`

The approved Stage 0 synthetic throughput probe is complete at `0b71a29`.
Run **34536965288** completed **12/12 observations** in an 88-second job;
all checksums match, all children were ready before the shared monotonic start,
and every child was reaped. No scanner or corpus input executed in the probe.

Median throughput relative to one process is **2.029× at three processes,
2.136× at four, and 2.125× at six**. Four processes add only **5.25%** over
three; six add **4.71%**. The runner reports four vCPUs, two cores and two
threads per core, with Python 3.12.14. The prospective **E3 ≥ 2.7 premise
fails**. This result does not support proceeding to the proposed partitioning
experiment; it is not proof that all scanner parallelism is ineffective.
See `v18-scaling-assessment.json` and its retained raw observations.

**One dispatch consumed; zero scanner runs, optimization attempts or paid model
calls.** Stage 1 and partitioning remain unapproved. The normal CI jobs are
structurally unchanged, but the optional workflow changed, ending workflow
equality to `592a9cd`. Fresh CI **34536886816** verifies all 29 normal jobs;
all 12 suites pass **2,183 tests / 36 skipped**. Docs **34536886750** pass.
Scanner/test/package bytes remain identical to `592a9cd`; prior local checks,
production replay and Git compatibility retain their executed sources, and the
three exposed SSRF gates retain measured `2ac39aa`. Initial probe lint issues
and an immediate post-push PR-readback assertion are preserved with corrections.

**Phase 22 remains incomplete.** The retained Linux scanner result is still
15/25 development complete, ten Meta timeouts and both historical batches
skipped. No current-source full timing pass, fresh evaluation, scope waiver or
final human acceptance is inferred. Further source-design work may investigate
reducing repeated analysis, but no safe reuse design or new experiment is
established here. Pilots/full paid benchmark remain deferred, Phase 21 incomplete,
and Phase 24/15 unchanged. No merge, release, outreach or next phase.

## Historical v17 diagnostic at `127763c`

The approved whole-worker sampling scope is complete at `127763c`:
**one Meta operator input**, **69.906s native / 71.578s outer**, 49 findings,
full ordered baseline equivalence after established volatile exclusions and valid
native JSON/SARIF. Four final snapshots restore timer/signal state. The sampler
changes no scanner methods and records no locals or target values.

Active workers retain 4,220 / 5,093 / 4,903 samples (SENT-012/015/016).
Shared merge inclusive shares are 24.81% / 19.18% / 22.58%; expression leaf
shares are 11.66% / 15.92% / 14.28%, mostly at function entry. Caller shares
overlap, signal delivery biases attribution, and no share is wholly removable
cost. **No safe larger optimization or native speedup is established.** See
`v17-sampling-assessment.json` and the source review in `v17-timing-disposition.json`.

The one-profile budget is closed: **zero optimization attempts, additional native
observations, comparator runs, full retries or paid calls**. No scanner/test code
changed. Existing local and 12 hosted suites retain 2,183 passed / 36 skipped,
29 normal jobs and docs, replay and Git compatibility at actual `592a9cd`.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.
The read-only cleanup check initially encountered sandbox Docker permission;
the authorized recheck passed and both records are retained.

**Phase 22 remains incomplete.** The Linux result remains 15/25 development
complete, ten Meta timeouts and both historical batches skipped. Retain the
timing gate; no scope revision, fresh evaluation or final acceptance is inferred.
Further performance experiments need a justified bounded proposal and approval;
this profile does not justify another speculative micro-optimization. Any timing
scope revision needs an explicit user decision and would still require fresh
evaluation and final human acceptance. Pilots/full paid benchmark remain deferred,
Phase 21 incomplete, and Phase 24/15 unchanged. No merge, release or next phase.

## Historical v16 diagnostic at `46b8786`

The user approved `v15-next-combine-proposal.json`; the exact receipt is
`v16-combine-authorization.json`. Its one Meta operator diagnostic completed in
**81.271s** (**82.947s** including measurement setup/finalization). The full
ordered report matches the retained native baseline after established volatile
exclusions. Native JSON/SARIF validate, all four workers have final snapshots,
and 24 synthetic comparisons preserve all Value fields, keys and cache behavior.

The prospective predicate **fails in all three active workers**. Eligible generic
combinations are frequent (83.72%, 85.54%, 84.47%), but their body CPU shares are
only **7.81% SENT-012, 5.34% SENT-015 and 6.81% SENT-016**, below the required
**10% in each worker**. Timing excludes classification counters but includes field
reductions/helpers and construction; it is instrumented attribution, not wholly
removable cost or a native gain. See `v16-combine-assessment.json`.

The stopping condition was enforced before optimization. **One profile used,
zero optimization attempts, zero native performance observations and zero exposed
regression observations.** All 12 performance and 30 conditional SSRF observations
are cancelled; no unused maximum remains open. No scanner/test code changed and
no reversion was needed. Zero paid calls.

Source/test/workflow/package inputs at diagnostic `46b8786` equal verified
`592a9cd`. The existing local and 12 hosted suites each retain 2,183 passed and
36 skipped; 29 normal jobs and docs, production replay and Git compatibility
retain their actual executed sources. No new full suite or hosted pass is claimed.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.

The next `v16-next-worker-sampling-proposal.json` is **unapproved**: one
120-second CPU sampling profile of the same Meta operator input, at most 100Hz
per worker, zero optimizations or additional native/comparator observations and
zero paid calls. It seeks a larger whole-worker CPU concentration before another
code proposal. No further measurement, full Linux retry or fresh evaluation is
inferred. Timing/fresh evaluation/final acceptance remain unmet; Phase 22 remains
incomplete. Pilots/full paid benchmark stay deferred, Phase 21 incomplete and
Phase 24/15 unchanged. No merge, release, outreach or next phase.

## Historical v15 diagnostic at `77ea21f`

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
