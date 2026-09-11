# Replacement SSRF follow-up

## Current constructor-scope correction and regression checkpoint

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
