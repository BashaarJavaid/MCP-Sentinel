# Integration evidence, batches 1–51 and closeout audit

## Current v22 historical assessment refresh

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

Historical v10 closeout: `v10-closeout-audit/packet.json` preserves all 88 requirements:
**71 passed, two user-deferred and 15 unresolved**. The prior v9 audit is
unchanged. Fresh measurement completion does not accept the actual 0/2 detection
result. Linux diagnostics and the reverted local experiment remain separate
from failed whole development/historical timing gates. Both v10 follow-up
proposals are prepared and unapproved; no automatic dispatch is authorized.

## Evidence archives

Batch 51 is sealed: **1,141 files**, 372,792,245 raw bytes and 19,136,410 compressed
bytes. SHA-256: `f807e90d33215b8956b11c527eab0c516e1a368326a6dbe72920549988dd58b3`.
Restore after batches 1–50 using the unchanged verified restoration procedure.
Every member and all 50 preceding archive hashes were checked.

The authoritative result is `v22-refresh-disposition-corrected.json`: 98/98
complete and both historical batches pass. The earlier aggregation ran before
its local second-batch assessment finished and incorrectly reported only 53
observations; `v22-aggregate-correction.json` preserves and corrects that error.
Setup and audit-helper failures are retained separately in
`v22-check-failure-assessment.json` and `v22-quality-audit-label-correction.json`.
None was a native observation or a benchmark retry. Both raw Linux jobs passed.

Batch 50 is sealed: **693 files**, SHA-256
`d714c5b9de7f29eac09d9d5ec55a077027af414aa791a9b562237e2cc8802b62`. Every member and all 49 prior archives were verified. Restore
after batches 1–49 in separate staging using `evidence-v50.json`; require existing
destinations to match identical bytes or their recorded prior hash. Stop on
unexpected conflict. Raw sequence/CI outputs, failed attempts, assessments,
authorization, source verification and helper sources are retained. The new
replacement-v4 source packet and final audit/docs/delivery bindings are tracked
directly; no evaluation of the proposed fresh inputs has run.

Batch 49 is sealed: **338 files**, SHA-256
`d3351afdfaf9ba5df51b9bbc34e335a8ea0b791f18e63d9a4dde03e69fed15e0`. Every member and all 48 prior archives were verified. Restore
after batches 1–48 in separate staging using `evidence-v49.json`; require existing
destinations to match identical bytes or the recorded prior hash, and stop on
unexpected conflict. This batch retains diagnostic approval/dispatch, supervisor
and selfchecks, raw Linux reports/environment/logs, independent assessment, fresh
normal hosted verification, full-sequence proposal and helper sources. Final
audit/documentation/delivery bindings are tracked directly after sealing.

Batch 48 is sealed: **356 files**, SHA-256
`595aee05cda6debf4aab85accae532156a1e830b4c6f0272e21ec2a1a19015e9`. Every member and all 47 prior archives are verified. Restore
after batches 1–47 in separate staging using `evidence-v48.json`, requiring existing
destinations to match identical bytes or their recorded previous hash. Stop on
unexpected conflicts. This batch retains the policy approval, candidate, all
local/hosted checks and artifacts, original regression failures and corrections,
production replay/runtime compatibility, prepared diagnostic and helper sources.
Final audit/documentation/delivery bindings are tracked directly after sealing.

Batch 47 is sealed: **446 files**, SHA-256
`8b458443e193d91b1780c252877107e38392dac05683b58fbac21b167ef678d6`. Every member and all 46 prior archive hashes are verified.
Restore after batches 1–46 in separate staging using `evidence-v47.json`; existing
destinations must match identical bytes or a recorded previous hash. Stop on
unexpected conflicts. This batch retains Stage0 approval/implementation, all raw
observations and logs, fresh CI/docs artifacts, the failed premise, verification,
preparation failures/corrections and helper sources. Final audit/docs/delivery
bindings are tracked directly after the seal.


Batch 46 is sealed: **64 files**, SHA-256
`9ea5341776dddd494c9d9c160e9b587bc385a930b385b3268a00dfa30a43e0a5`. Every member and all 45 prior archive hashes are verified.
Restore after batches 1–45 in separate staging using `evidence-v46.json`; existing
destinations must match identical bytes or a recorded previous hash. Stop on
unexpected conflicts. The batch retains approval, synthetic controls, the single
profile, raw stack catalogs/counts, complete reports, assessment, source review,
verification, the initial permission failure and helpers. Final audit/docs/delivery
bindings are tracked directly after the seal.


Batch 45 is sealed: **78 files**, SHA-256
`923f542472430152287db7ac9bdaaeb2c60fa467f7bd7aeaacad5e7ed19ec114`. Every member and all 44 prior archive hashes are verified.
Restore after batches 1–44 in separate staging using `evidence-v45.json`; existing
destinations must match identical bytes or a recorded previous hash. Stop on
unexpected conflicts. The batch retains approval, the one diagnostic, raw worker
snapshots, report comparison/validation, synthetic controls, source verification,
helpers and the unapproved next sampling proposal. Final audit/docs/delivery
bindings are tracked directly after the seal.


Batch 44 is sealed: **98 files**, SHA-256
`5e18b9a2849c35166040a8d7df28be4b32beb3793888fa887d995a4a60bbe629`. Every new member and all 43 prior archive hashes are verified.
Restore after batches 1–43 in separate staging using `evidence-v44.json`; existing
destinations must match identical bytes or a recorded previous hash. Stop on
unexpected conflicts. This batch retains the one profile, source-bound comparison,
synthetic control and check failures/corrections, exact approval, helpers and
unapproved next proposal. Final audit/docs/delivery bindings are tracked directly
after the seal.


Batch 43 is sealed: **805 files**, 77,193,273 raw bytes and
8,064,825 compressed bytes, SHA-256
`e1fb4a263829dc1438995ec7126c94c90bb1c830906ef3dc97a959d8044af656`. Every member was read back and all 42 prior numbered archive
hashes reverified after native/test/collector writers stopped.
Restore after batches 1–42 into separate staging; verify archive/member hashes
against `evidence-v43.json`. Existing destinations must match identical bytes or
their recorded previous hashes; stop on unexpected conflicts.

This batch retains the approved v14 diagnostic and reverted attempt, all ten
completed reports and the interrupted native attempt, cancelled-run accounting,
initial type failures and partial local suite, corrected final local/hosted
verification, distributions, production replay, Git compatibility, commands and
helper sources. The next merge diagnostic is prepared but unapproved. Final
89-row/added-scope audit, docs and delivery bindings are tracked directly after
the seal (`v14-closeout-audit/packet.json`, `v14-final-documentation-binding.json`,
`v14-delivery-verification.json`, `v14-closeout-draft-body.md`). No timing pass,
fresh evaluation or Phase 22 acceptance is implied.


Batch 42 is sealed: **791 files**, 127,451,625 raw bytes and
7,933,120 compressed bytes, SHA-256
`c1f7e5660af1b617fb6e0802d4ef73c9c2844ce51b963387997c04a527b62763`.
Every member was read back and all 41 prior numbered archive hashes reverified
after native/test/collector writers stopped. Restore after batches 1–41 into
separate staging; validate the archive and each member against `evidence-v42.json`
before copying. Existing destinations must match identical bytes or their prior
numbered-manifest hashes; stop on unexpected conflicts.

This batch preserves the passing three-family exposed gates, the one fixed
trace, the attempted/reverted performance change and all 14 observations,
current local/hosted checks, production replay and Git compatibility, full
reports, failed attempts, commands and helper sources. Final audit, docs and
delivery bindings are directly tracked after the seal, including
`v13-closeout-audit/packet.json`, `v13-final-documentation-binding.json`,
`v13-delivery-verification.json` and `v13-closeout-draft-body.md`.
The archive is evidence delivery, not a timing pass or Phase 22 acceptance.


Batch 41 is sealed: **1,002 files**, 103,057,714 raw bytes and
10,920,410 compressed bytes, SHA-256
`ac47a7684f21db98175ddf5fe909e7a18eef1a5399b10c20431230d597032c91`.
Every member was read back and all 40 previous archive hashes reverified after
measurement, check and collector writers stopped. Restore after batches 1–40
into separate staging; validate the archive and each member against
`evidence-v41.json` before copying. Existing destinations must match identical
bytes or their prior numbered-manifest hashes; stop on unexpected conflicts.
Current source/test/hosted proofs, approved bounded follow-ups, one counter profile, exposed regression runs,
source assessments and the failed SearXNG fixed discrimination and unapproved next diagnostic/run budget are retained.
Final documentation/delivery bindings are also retained directly in Git. This
seal is evidence delivery, not a timing pass or final technical acceptance.

Batch 40 is sealed: **794 files**, 66,259,015 raw bytes and
10,545,389 compressed bytes, SHA-256
`a65cfd1dd40d21ef1d02b22386dda21790018a1da7c2558433319d9f342a2cd0`.
Every member was read back and all 39 previous archive hashes reverified after
measurement, check and collector writers stopped. Restore after batches 1–39
into separate staging; validate the archive and each member against
`evidence-v40.json` before copying. Existing destinations must match identical
bytes or their prior numbered-manifest hashes; stop on unexpected conflicts.
Current source/test/hosted proofs, approved evaluation and diagnostic results,
reverted experiment, source assessments and unapproved follow-ups are retained.
Final documentation/delivery bindings are also retained directly in Git. This
seal is evidence delivery, not a timing pass or final technical acceptance.

Batch 39 is sealed: **349 files**, 17,110,992 raw bytes and
4,292,118 compressed bytes, SHA-256
`f90b9340484df2fc8c0f68644f5e2526382691f77b25caf17fe88b3dd6396b41`.
Every member was read back and all 38 prior archive hashes reverified after
included measurement, check and collector writers stopped. Restore batch 39
after batches 1–38 into separate staging; validate its archive and each member
against `evidence-v39.json` before copying. Existing destinations must match
identical bytes or their prior numbered-manifest hashes; stop on unexpected
conflicts. The final owning-document binding and readable proposal assets are
also retained directly in Git. This is a completed evidence delivery, not a
passed timing gate or final technical acceptance.

Current assessments: `v9-fetchmcp-assessment-v2/packet.json`,
`v9-openwebsearch-assessment/packet.json`, and
`v9-compatible-evidence-binding/packet.json`. Batch 38 is sealed: **747 files**, 257,549,935 raw bytes and 11,587,567
compressed bytes, SHA-256
`95040f0cb196f39345d606a7ee6fbf5bc4e7294e985be62ce4a5801d8c4ef4d7`.
Every member and all prior numbered archive hashes were verified. The v8 audit
below is historical; current source/test bindings cover all 86 original rows plus
R87/R88 in `v9-current-source-test-bindings/packet.json`.

Restore batch 38 after batches 1–37 into separate staging, validating its archive
and every member against `evidence-v38.json` before copying. An existing destination
must match identical bytes or its prior numbered-manifest hash; stop on unexpected
conflicts. The new corpus proposal and runnable Linux gate files are tracked
separately. Batch 38 predates the final Linux/hosted outcomes retained in batch 39;
neither seal is a timing pass or final technical acceptance.

## Historical v8 closeout and preserved archive index

Batch 37 retains **407 files**, 25,706,836 raw bytes and 4,530,755 compressed bytes;
SHA-256 `93f938ce36d3b32e44601f2e8b183cd0f5adbea9e39f4fa4af53311050a713b6`. Every archived member was read back and matched,
and every previous numbered archive hash was verified. The current audit records
**78 passed, 2 user-deferred and 6 unresolved** requirements.

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

See [the current 86-row audit](v8-closeout-audit/packet.json), [Linux assessment](v8-linux-assessment/packet.json), and [fresh assessment](v8-fresh-assessment/packet.json).

Restore batch 37 after batches 1–36, verifying its archive and every member with `evidence-v37.json` before copying. Existing destinations must match identical bytes or the prior numbered-manifest hash; stop on any unexpected conflict.

## Previous closeout and preserved archive index


Current candidate is `62987a6`; implementation bytes equal `e87b7c9`. The
final exposed SSRF measurements at `62987a6` pass 2/2 vulnerable variants twice,
with no matching fixed/control alerts and unchanged ordered reports except
documented volatile fields. The `e87b7c9` historical attempt completes 43/45 inputs but
retains two native timeouts and one end-to-end overrun. A subsequent copy-skipping
experiment completes only 2/6 and is reverted; its code, tests and failures remain
in history. The strict two-whole-batch gate is not passed.

The [revised bounded Linux runner proposal](v7-native-runner-proposal-v3/packet.json)
awaits the explicit execution decision required by final prompt §4. Its preflight
verifies exact source/workflow compatibility and accepts/rejects retained known
passing/failing historical and development batches. It supersedes v2 after
development completes 24/25 with a new Meta fixed-mutation timeout at 120.063s.
Original held-out states remain 10 completed/10 unsupported/5 incomplete.
No workflow has been applied or dispatched. The restored
source passes 2,121 tests / 36 skips with 89.64% branch coverage, local quality,
package and current Docker replay checks. Draft PR #37 points to `62987a6`;
all 29 jobs in CI 34416723981 and docs 34416723960 pass. See
[progress](progress.md) and the [86-row checklist](requirements.md).

Batch 33 seals the completed local continuation and prior `10103ad` hosted
evidence: **1,565 files**, 622,679,966 raw bytes, 28,760,427 compressed bytes;
SHA-256 `cdc56f134bbb3b50fbf924e32f8dcf79034b13476b77acf5e62453d6ea137fd5`.
All members were read back and all 32 prior archive hashes reverified. Current
`62987a6` hosted jobs were excluded while running and are retained in batch 34.
Batches 1–32 remain unchanged. The records below preserve historical claims for
their named sources.

Batch 34 adds the completed current hosted collection, package/source audit,
strict owning-docs build and delivery-input proof: **327 files**, 11,810,249 raw
bytes, 4,657,887 compressed bytes; SHA-256
`e2176fbd5a193a06d24ca7149a3b12aae01a7f7201174476108a117a8a00bb92`.
Every member and prior archive hash is verified. The current
[86-row closeout audit](v7-closeout-audit/packet.json) records 76 passed,
2 user-deferred and 8 unresolved rows. Batch 35 retains that audit and the
reviewable final draft body: **7 files**, 564,639 raw bytes, 348,844 compressed
bytes; SHA-256
`4eb3e95a1349b835277dd62874b1965fe6cd8ba35378fd0634d6d08a8cee8e06`.
Every member and prior archive hash is verified. No final technical acceptance
is inferred. The documentation/evidence delivery preserves tested `62987a6`
implementation/package inputs and uses `[skip ci]`; it does not claim another
hosted pass for the later documentation commit.

Batch 36 retains the final owning-document status binding and successful strict
docs recheck: **8 files**, 850,006 raw bytes, 470,337 compressed bytes; SHA-256
`7553fa95b69c442df618805937cb0faec3cba1ef3bead947656023c583697c7a`.
It changes no audit disposition or tested package input. The
[final documentation binding](v7-closeout-audit/final-documentation-binding.json)
records the final owning-document hashes; every member and prior seal is verified.
The superseded fresh `10103ad` proposal and current `checkpoint-62987a6.json`
remain unapproved and unevaluated. No new
paid call occurred. Exact fresh freeze/evaluation
and human technical acceptance remain separate. Phase 22 is incomplete.

Restore batch 33 after batches 1–32, using `evidence-v33.json` for archive and
member verification, then apply batches 34–36 using their respective manifests.
For an existing checkout, extract each batch into a separate
empty staging directory first; verify all members before copying. At an existing
destination, require either identical bytes or the exact prior numbered-manifest
hash before applying a recorded newer version. Stop on any other conflict.
The `diagnostics-v33.tar.gz` member retains the task's temporary Python harnesses;
their actual source/command identities and failures remain in the command records.

## Retained batch history

Batch 32 retains the bounded TypeScript follow-up at `68bdf83`. All 29 hosted
jobs pass; each of 12 full suites records 2,057 passed, 36 skipped and
89.50–89.53% branch coverage. Both approved captures replay with exact request
identities and no new paid calls. Canonical package source members match the
current implementation; installed-wheel, Docker, isolation and docs checks pass.
The complete CI/docs archives and 225 uploaded artifact files are retained.

The exposed SSRF replacements remain 0/2 vulnerable detections, with no named
alerts on three fixed/safe cases. All 70 unrelated findings are unchanged.
Historical batches complete 44/45, 45/45 and 41/45; five timeouts and one extra
native-completed wall-time overrun remain. Every historical input has at least
two identical completed observations under 120 seconds, but the handoff's
requirement for two complete whole batches **has not passed**. The complete pass
retains 20 vulnerable detections and zero named fixed/safe alerts. Development
completes 25/25 with unchanged findings and the approved Meta erratum. Original
held-out results retain 10 completed, 10 unsupported and 5 incomplete inputs.
Mastra's changed logger diagnostics have source-bound explanations; findings
and recognized surface counts are unchanged.

The 86-requirement audit checks 97 mapped files, 14 completed command records
and all 31 prior archive identities. Failures, the earlier local coverage
checkpoint, source traces and corrected evidence-script errors remain preserved.
The [scope proposal](../completion-scope-v1/follow-up-proposal.json) and
[fresh replacement freeze](../corpus-replacement-v2/README.md) require user
decisions. Neither is approved; the five fresh cases have not been evaluated.
Paid benchmark review and external pilots remain user-deferred/nonblocking.
Phase 22 is not marked complete.

Batch 32 seals **1,139 files**, 530,447,230 raw bytes and 21,551,082 compressed
bytes. Archive SHA-256:
`de862c63dbb10c8c3d27a1ceee93538f015808c6b4ba47fbb307eb7001c9eed4`.
Apply `evidence-v32.tar.gz` after batch 31 and verify `evidence-v32.json`.
The proposals and owning documents are separately tracked in Git. This final
update changes documentation/evidence only and uses `[skip ci]`; the measured
passing CI source is `68bdf83`, with identical implementation/package inputs.
The main worktree remains clean at `4cd5759`; this integration is delivered
through the existing draft PR #37. Earlier batches below remain historical records.


Batch31 retains the green technical audit at ee9721f: all29 hosted jobs pass,
including12 full suites with2024 passed/36 skipped and89.46–89.49% branch coverage.
All12 wheel jobs, Docker/onboarding/baseline/validation, isolation and docs pass.
The complete CI/docs archives contain484/12 verified members;225 uploaded artifact
files and byte-identical canonical distributions are retained. All86 requirements,
historical reference/command identities and all30 prior archive hashes were audited.
No additional failing technical gate was found.

The user deferred the full396-request paid benchmark and removed external pilots
as a Phase22 completion prerequisite. Neither is counted as passed. See the
separately tracked `../completion-scope-v1/decision.json`. Known replacement misses
and unresolved registrations await user disposition; no detector change or paid
call occurred. Phase22 is not yet marked complete. Later adoption/launch gates
remain unchanged.

Batch31 seals 248 completed files with verified member readback.
Archive SHA-256: `17ab6a3dad8003809372d745754b0400dd6635263d9e4107b607a962795d8493`.
Apply `evidence-v31.tar.gz` after batch30 and verify `evidence-v31.json`.
This documentation/evidence-only delivery uses `[skip ci]`; green hosted checks
belong to ee9721f, whose implementation bytes remain unchanged. A skipped head is
not a new hosted pass. All prior evidence, failures and worktrees remain.

Batch 30 retains the approved replacement evaluation and Meta erratum evidence.
Both native and pinned comparator scans complete 5/5 replacements, detecting 0/2
vulnerable variants and no named condition on the three fixed/safe inputs. Native
repeat is stable. All 70 native and 33 comparator unrelated warnings have source
assessments; six computed MCP tool names remain unresolved. No detector tuning,
target execution or additional paid calls occurred.

The Meta erratum is separately tracked under `../meta-fixed-label-erratum-v1/`.
It preserves original labels/raw scores and distinguishes two affected fixed
cases from 13 valid clean controls with zero named condition false alarms.
The bounded approval runner passes 21 tests, lint/format, strict typing and docs.
Hosted capture-update Docker/docs pass; its full matrix is still in progress.
The new runner revision will receive its own normal PR checks.

Batch 30 seals 125 completed files with verified SHA-256 readback.
Archive SHA-256: `71aa1f75cddc27b05bcd6778c98f1b0fd23c6ca97f024b0e34e10090c7bca0ae`.
Apply `evidence-v30.tar.gz` after batch 29 and verify `evidence-v30.json`.
All older seals, failures, worktrees, proposals and source identities remain.

Batch 29 adds the approved smoke/demo capture verification: both requests accepted
for $0.071799 total under the $0.400100 cap, unchanged TypeScript regression PASS,
and actual Docker replay PASS with 20/20 attempts and 14 reviewed candidates.
Wheel/sdist capture bytes and strict documentation pass. Earlier failed replay
and build attempts remain. Approval, exact captures and ledgers are tracked in
`../paid-evaluation-v2/`. No benchmark paid review or replacement evaluation ran.

Batch 29 seals 52 completed files with verified member readback.
Archive SHA-256: `73bab180d174747dbe3d2fbd1d1ca9cf0e9da132a02169341c01780e40f7ee18`.
Apply `evidence-v29.tar.gz` after batch 28 and verify `evidence-v29.json`.
All preceding hosted results refer to their named source; hosted verification
for the new captures is pending. Meta and replacement decisions remain open.

These batches preserve implementation, failures and source-specific measurements.
Batch 28 adds completed draft delivery and the hosted matrix at `1e7c16a` to
batch 27’s `6e68331` native verification and `d7184d3` local checks. Raw failed
suites and capture-dependent demos remain preserved. **This is not final technical acceptance.**
[requirements.md](requirements.md) lists the complete outstanding contract;
[progress.md](progress.md) explains source-specific results and limitations.

Batch 27 contains 680 added/changed files, 403,378,236 raw bytes and 15,105,086
compressed bytes. Every member was read back against its original SHA-256.
Archive SHA-256:
`83bfc17cdf1b267332f4e11685bf1467eb2ee7eeee1d6bf4320063f0c802721f`.
Apply `evidence-v27.tar.gz` after batch 26 and verify `evidence-v27.json`.
All included commands finished before sealing; all previous seals and failures
remain. The exact paid packet/request bundle and replacement-corpus proposal
are separately tracked in Git under `artifacts/phase22/`.

The pre-delivery `v2-local-acceptance-index-d7184d3/packet.json` maps all 86 local
dispositions to source/test/report hashes and 24 completed command records.
Historical native verification completes 45/45 twice, development 25/25, and
the original held-out repeat retains 10 completed/10 unsupported/5 incomplete.
All independent local quality/install/isolation/Docker/onboarding/baseline and
pre-commit gates pass. The raw full suite is still failed; its stale cost
expectation has a passing targeted correction, while the unchanged TypeScript
replay test needs a compatible capture. The actual demo tests 20/20 attempts
and validates reports but exits 3 for missing dynamic review.

The validated [paid proposal](../paid-evaluation-v2/README.md) requests explicit
approval for at most 398 new requests / $66.321920, with 20 historical requests
reused. No paid calls occurred. The Meta decision, replacement freeze, reviewed
evaluation and human/pilot gates remain pending. Draft PR #37 is delivered against
PR #36, exact parent `8b6b0dd`. The final hosted disposition is retained in
`v2-final-technical-disposition-1e7c16a/packet.json` for all 86 obligations.

All 29 CI jobs finished: 12/12 wheel jobs pass; all 12 quality suites report
2022 passed, one TypeScript capture failure and 36 skipped (89.48–89.51% branch).
Hosted isolation and strict docs pass. The Docker demo completes 20/20 attempts
and fails its missing dynamic review. Later steps skipped after these failures
remain distinguished from passing local counterparts. Both pinned Phase 20
reproductions retain their historical 32-completed/13-incomplete states.
Canonical hosted binaries match the locally verified builds byte for byte.
The measured source stays `1e7c16a`; evidence-only bookkeeping uses `[skip ci]`
and does not satisfy required checks or establish merge readiness.


Batch 28 contains 397 completed added/changed files, 8,615,381 raw bytes and
2,857,199 compressed bytes. Every member was read back against its SHA-256.
Archive SHA-256:
`fdd0ce31c17f9f1a99181e8cf6edf5cb1cbf66d413c8dbc495ab795156ed4480`.
Apply `evidence-v28.tar.gz` after batch 27 and verify `evidence-v28.json`.
This retains draft delivery, all completed hosted outcomes, 419/12 full CI/docs
log members, canonical distributions, historical reproductions, the final
86-requirement disposition and strict documentation verification. All previous
seals, raw failures and worktrees remain. No paid evaluation was performed.

The first batch covers `536bb69`; subsequent numbered batches extend it.
Batch 23 retains 923 added/changed files through `734aa8c`, including the
immutable `7071a26` full suite (1,959 passed, 36 skipped, 89.41% branch coverage),
quality/build/audit and installed distributions, successful installed onboarding
and baseline controls, and Linux network-none isolation. The pinned comparator
completed 40/45 historical inputs and 25/25 development inputs; five historical
rule timeouts remain incomplete. All failures and stopped commands are retained.
The auth qualification regression discovered during source review is corrected
at `734aa8c`, with 383 affected passes, final prefix controls, strict typing and
restored source-specific qualifications. Final historical repeats, fresh holdout,
reviewed evaluation, hosted matrix and external acceptance remain open.

All 149,332,686 raw bytes were read back against their hashes. The archive is
5,570,931 bytes; SHA-256:
`ac3d5b820a33f616b55c9bc3f201a5202e8fee64cedcba263f372e1b9770d9a0`.
Apply `evidence-v23.tar.gz` after batch 22 and verify `evidence-v23.json`.
All included commands finished before sealing; the queued historical sequence
was terminated before it scanned an input. Earlier seals and worktrees remain.

Batch 22 retains 340 added/changed files through fd9320b: full quality
and installed distributions at 5f6bb9a, all 36 Docker controls, the incomplete
42/45 historical run, uncaptured demo dynamic review, session credential corrections
and exact Python/TypeScript retained-request equivalence. Every member was read
back against its hash. Archive size: 5,141,177 bytes; SHA-256
`6fabd73b363f7a3de18b12e05f9fc161b6530210d7608261f68ce0e51c6ba127`. Apply `evidence-v22.tar.gz` after batch 21 and verify
`evidence-v22.json`. All included checks finished before sealing. Final candidate
benchmarks and paid/hosted/external gates remain open.

Batch 21 retains 194 added/changed files through 5f6bb9a: approved Git campaigns
and native consumers, bounded production static workers, complete Meta development
inputs, exact Mobile native serial/worker equivalence, wheel smoke extension and
SDK context binding corrections. All 29,216,392 raw bytes were read back against
member hashes; the archive is 1,149,566 bytes, SHA-256
`e80849c1c12f75590c844d72d6fb0daf0fc74bb2358efa8ea0922ee8e1709136`.
Apply `evidence-v21.tar.gz` after batch 20 and verify `evidence-v21.json`. All
included checks finished before sealing. The later complete historical benchmark
run is outside this seal. The Meta frozen-label decision and final gates remain open.
Batch 20 retains 226 added/changed files through 394bb8a: the 3e1faac full
milestone (1882 passed, 36 skipped, 89.27% branch coverage), HTTP/MCP entry
corrections, TypeScript location/deadline checks, workspace exclusion/source
audit, completed Mobile originals and unchanged condition semantics, and Meta
profiling plus the four-rule concurrency feasibility diagnostic. All 7,525,787
raw bytes were read back against their member hashes; the archive is 1,090,315
bytes, SHA-256 `275ceab22136b1e9e441120e0fe596ac61c2e0713fa8d84544f06c804b71dcd7`.
Apply `evidence-v20.tar.gz` after batch 19 and verify `evidence-v20.json` before
later packets. All commands had finished before sealing. The prepared new Git
drivers have not run in this packet. No production parallel implementation,
final benchmark acceptance or paid calls are claimed.
Batch 19 retains 358 added/changed files through c75e876: equivalent/binary
state checks, the 32/45 historical diagnostic and all 13 timeouts, Meta 0/5 at
65ba622, corrected unsupported-schema campaign completion, consumer/artifact
and installed-distribution audits, Git Path-presence counterexamples, shallow
record serialization and every intermediate failure. All 69,092,685 raw bytes
were read back against their member hashes; the archive is 3,323,497 bytes,
SHA-256 `264172df072d0fa7e649b8ade8a0cdb4f57d1de75c9fb2b87cd713af34a27021`.
Apply `evidence-v19.tar.gz` after batch 18 and verify `evidence-v19.json` before
later packets. All included commands had finished before sealing. Final native
completion, condition adjudication, full quality/hosted gates and the Meta label
decision remain open; prior evidence and historical artifacts are preserved.
Batch 18 retains 307 added/changed files: crowded source contexts, TypeScript
record/client and factory metadata flow, checked Python shell APIs, offline corpus
treatments, the 941-test source-flow and 79-test native/campaign audits, exact-state
profiles, and all newer Meta attempts. Meta completes 1/5 at 59e9fc5, 2/5 at
6a3a4a2 and 0/5 at d5e02e9. Selected-rule profiles are not all-rule condition gates.
All 13,585,250 raw bytes were read back against their member hashes; the archive is
984,124 bytes, SHA-256
`19d45e5aa661860a908b0edfc25ec93fe315193d50510cfc77fe82bf59ce1286`.
Apply `evidence-v18.tar.gz` after batch 17 and verify `evidence-v18.json` before
applying any later packet. All included commands had finished before sealing;
all prior archives and the pending Meta fixed-label decision are preserved.
Batch 17 retains 233 added/changed files: grouped startup and its command-precheck
correction; the f2ea709 full milestone (1,775 passed, 36 skipped, 89.11% branch
coverage); Express middleware, module/factory and inventory controls; returned-helper
source anchors; and immutable credential-default profiles with exact state comparison.
The first Meta input completes once at f2ea709; all five c6234a0 inputs time out.
Initial failures and the still-pending fixed-label decision remain explicit.
All 5,820,999 raw bytes were read back against their member hashes; the archive is
849,986 bytes, SHA-256
`6aa9aa1c0ad0a600ccfed42a807cde42b07e8b8ced03ae1ac8214e29e67e8771`.
Extract and verify batch 16 before applying `evidence-v17.tar.gz`, then verify
against `evidence-v17.json`. All included commands had finished before sealing.
Batch 16 retains 450 added/changed files: bounded list and SDK/provider work,
source launch evidence, Express factory callbacks, middleware validation caching,
startup-path correction, all completed native reruns and the pending Meta fixed-label
decision packet. Upload at `6da955e` completes all five inputs across run plus retry,
with two vulnerable condition hits and no fixed/safe condition alerts. Meta remains
incomplete at the unchanged deadline; the source timing diagnostic is included.
All 53,642,525 raw bytes were read back against their member hashes; the archive is
2,071,944 bytes, SHA-256
`e3fc89468182de5530c48b1b9d5d5c25f3c6387b662df7760c343da668cc110a`.
Extract and verify batch 15 before applying `evidence-v16.tar.gz`, then verify
against `evidence-v16.json`. No active commands were included while still running.
Batch 15 adds completed post-v14 evidence, HTTP dispatch/import/module/forward-
declaration corrections and profiling. The `1840f13` upload run completed 3/5
inputs; two timed out. The ongoing `6da955e` upload rerun is excluded. All member
hashes are verified by readback; prior seals and recovery snapshots are preserved.
Batch 6 (`evidence-v6.tar.gz`, `evidence-v6.json`) adds 251 files through
`5065f16`, including the exact `f12e891` full-suite milestone, its coverage
database, the 18-input incomplete development run, TypeScript HTTP regressions,
and the five-input Kubernetes measurement/adjudication. Extract batches in
numeric order into the same evidence directory. Verify each batch immediately
after extraction using its own manifest before applying the next batch; later
versions may retain newer bytes at a shared diagnostic path. Sealed archives
are unchanged. Source-specific limits and failed attempts are in `progress.md`.

`evidence-v1.tar.gz` is lossless. `evidence-v1.json` records its SHA-256 and the
size and SHA-256 of every member. Every archived member was read back and checked
against its original bytes. Expanded files remain locally available but are
ignored by Git; fresh checkouts recover them from the archive.

```sh
mkdir -p /tmp/phase22-evidence
tar -xzf artifacts/phase22/integration/evidence-v1.tar.gz -C /tmp/phase22-evidence
```

Verify extracted files with the standard library:

```python
import hashlib
import json
from pathlib import Path

packet = Path("artifacts/phase22/integration")
manifest = json.loads((packet / "evidence-v1.json").read_text())
assert hashlib.sha256((packet / manifest["archive"]).read_bytes()).hexdigest() == manifest["sha256"]
for item in manifest["files"]:
    data = (Path("/tmp/phase22-evidence") / item["path"]).read_bytes()
    assert len(data) == item["bytes"]
    assert hashlib.sha256(data).hexdigest() == item["sha256"]
```

Each command record includes its arguments, working directory, environment
overrides, source commit, tracked-diff hash, exit code and raw log. Later records
also retain the tracked patch. The earliest records did not preserve untracked
source bytes; their final implementation commits and failure logs are retained,
but they are not exact intermediate-source reconstruction packets. The updated
runner additionally archives untracked source/tests before future commands.
`diagnostic-sources.tar.gz` and `diagnostics-current.tar.gz` preserve diagnostic
scripts; their adjacent JSON files give per-file hashes. Diagnostics were never
used as substitutes for production measurements.

Measurements use the existing locked root environment and the active worktree's
`PYTHONPATH=src`. Restore the recorded source commit in a separate worktree and
run the command in its JSON record with that environment. The Phase 22 records
bind the unchanged frozen manifest, scanner source, harness, configuration and
report hashes. Reproduction requires the original corpus archives already
referenced by that manifest. The per-input static deadline remains 120 seconds.

The two final development commands in this batch select only
`dbt-option-selection` and `meta-image-ssrf`, using the existing
`scripts.phase20_measurements.measure` runner and authorized
`scripts.phase22_corpus.frozen()` validation. They make no model calls and do not
execute target code. Their source revision is `536bb69`; their results are scored
separately in [development-conditions.json](development-conditions.json).
The earlier dbt source review is retained in
[dbt-adjudication.json](dbt-adjudication.json). Historical Phase 20 source,
results, captures, costs and the unadjudicated 70-warning backlog are unchanged.

The milestone full suite belongs to `192296d`, not the later candidate.
Focused checks after later changes do not replace the final full quality gate,
45-input deterministic repeats, frozen holdout, competitor run, Docker campaigns,
installed-wheel/Action/isolation/hosted OS matrix or reviewed-tier evaluation.
Concurrent timings are verification latency, not isolated throughput.

No paid approval packet or consolidated final PR is ready. Paid calls, merge,
publication, human acceptance and external pilot evidence remain separate
checkpoints; substantial authorized implementation also remains.


The second packet, `evidence-v2.tar.gz`, adds source-flow regressions through
`d259126`, including recorded failures and corrections, command/source patches,
untracked regression-source snapshots, and the exposed Atlassian profiling run.
Its 237 files were read back and checked against `evidence-v2.json`. Extract it
after version 1 into the same directory. It excludes the still-running second
full-milestone records; those remain expanded until their result is available.

```sh
tar -xzf artifacts/phase22/integration/evidence-v2.tar.gz \
  -C /tmp/phase22-evidence
```

The Atlassian profile completed its harness command but the selected input was
**incomplete**: the 120-second static deadline expired. Profiling and concurrent
verification add overhead; this is not an isolated-throughput result. The raw
profile identifies repeated HTTP-scope and tool-discovery traversals for correction.


`evidence-v3.tar.gz` adds 111 files through `de1af5a`, including the completed
second milestone, its original mypy/cache failures, the subsequent corrections,
SDK HTTP caller/CLI regressions, and the repeated exposed Atlassian profile.
Every member was read back and checked against `evidence-v3.json`.

```sh
tar -xzf artifacts/phase22/integration/evidence-v3.tar.gz -C /tmp/phase22-evidence
```

The second full milestone passed 1010 tests, 36 skipped, with 87.38% branch
coverage at `d259126`. At `aaa759a`, the repeated instrumented Atlassian run
completed (84.2 seconds in static analysis, 93.2 seconds including reporting).
It reported 90 SENT-003 candidates and one SENT-012 candidate, and **no SENT-016
condition hit**. Completion does not establish detection of the labeled fallback.
The subsequent SDK HTTP source changes pass 201 affected regressions but have
not been measured against that condition yet. No final repeated benchmark,
fresh holdout, runtime campaign, paid review or acceptance gate is implied.

Batch 4 adds `evidence-v4.tar.gz` / `evidence-v4.json`: 437 files through
`9d396a4`, covering the preserved constructor work, campaign migration, Docker
failures/recovery, failed full milestone, corrections and bounded lifespan flow.
Every member was read back against its hash. Extract after batches 1–3 and run
the same verification snippet with `evidence-v4.json`:

```sh
tar -xzf artifacts/phase22/integration/evidence-v4.tar.gz -C /tmp/phase22-evidence
```

The full milestone failed and overlapped subsequent edits; its coverage output
is not evidence for a fixed source revision. The exposed Atlassian condition
still misses. See the batch-4 section in `progress.md` for exact limits, retained
failed attempts and diagnostic-source reconstruction limitations.


Batch 5 adds `evidence-v5.tar.gz` / `evidence-v5.json`: 439 files through
`4d88844`, including source-established service construction, client credential
sinks, interpretation profiles, incomplete Atlassian runs, regressions and their
failed/corrected checks. Each archived member was read back against its SHA-256.
Extract after batches 1–4 and use the existing verification snippet with
`evidence-v5.json`:

```sh
tar -xzf artifacts/phase22/integration/evidence-v5.tar.gz -C /tmp/phase22-evidence
```

The packaging command was the locked environment's Python running
`/private/tmp/phase22-package-evidence-v5.py` (exit 0). The script is retained in
`diagnostics-v5.tar.gz` inside the packet; it refuses to overwrite the sealed
version-5 archive/index. The archive holds 2,892,761 raw bytes in 589,041 compressed
bytes. Per-command JSON records link exact commands, source patches, diagnostic
snapshots and exit codes. Later documentation bookkeeping is recorded in Git.
The input deadline and the frozen credential-fallback condition remain unmet;
four incidental single-tool client candidates are not condition hits.

Batches 6 and 7 extend that history without replacing the earlier seals. Batch 6
contains 251 files through `5065f16`, including the fixed `f12e891` full-suite
milestone, eighteen exposed gap measurements and Kubernetes development scoring.
Batch 7 contains 531 added/changed files through `2a332f2`, including the original
dirty September 8 handoff/recovery archive, corrected registration and containment
flows, the fixed `4dfd24c` full suite and coverage, Excel/mobile/Meta/Mastra
measurements, revised unrelated-finding adjudication and all failed regressions.
Every member was read back against its per-file SHA-256. Batch 7 is 121,265,808 raw
bytes in 3,563,339 compressed bytes; archive SHA-256:
`68cdc015de92912b4dd746000f28ca6a5b1521ab9bc4f74d6e78a7ec434837f6`.

Extract in order, verifying each batch against its own manifest before extracting
the next batch, because later batches can retain newer diagnostic files at the
same relative path:

```sh
tar -xzf artifacts/phase22/integration/evidence-v6.tar.gz -C /tmp/phase22-evidence
# Run the verification snippet above with evidence-v6.json before continuing.
tar -xzf artifacts/phase22/integration/evidence-v7.tar.gz -C /tmp/phase22-evidence
# Run the verification snippet above with evidence-v7.json.
```

The batch-7 packaging command and script are recorded in `evidence-v7.json` and
its nested `diagnostics-v7.tar.gz`. The command refuses existing output seals.
`continuation-4dfd24c-full-suite` passed 1,215 tests, 36 skipped, at 88.27% branch
coverage; the original combined database was copied, and the older detached
checkout/database remain untouched. Later commits have separate focused evidence.
These packets do not establish the final Phase 22 benchmark, reviewed, runtime,
hosted or delivery gates; see the full requirement map and progress history.

Batch 8 retains 235 added/changed files through `ecdf579`: Mastra's actual
fallback-loop measurements, 13 fixed-source Git campaigns, the Git native/SARIF
orchestrator check, exact review-source corrections and retained failures. Every
member was read back against its hash. The archive contains 17,250,782 raw bytes
in 711,609 compressed bytes; SHA-256:
`15e833494a8fb0293e8517fad40645e6bc1b42721c5484905ed046a5ca0c3fd8`.
After verifying batch 7, extract `evidence-v8.tar.gz` into the same directory and
run the verification snippet with `evidence-v8.json`. Its packaging script is
retained in `diagnostics-v8.tar.gz`.

`git-campaigns-80bd278/verification.json` validates every raw result hash and
canonical campaign summary. All 13 analyses are incomplete: 312 total tested
attempts showed no violation and 728 remain untested. `git-native-80bd278/`
preserves native JSON, SARIF, console and their checksums for a production
orchestrator run on the same fixed source. Model calls were disabled. These are
bounded execution/consumer measurements; they do not establish Git defenses or
the final integrated source gate.

Batch 9 retains 485 added/changed files through `e2b6345`: credential branch
corrections, presence/receiver regressions, static profiles, all failed auth
deadlines, and the unfinished TypeScript class tests captured with commands.
Every member was read back against its hash. The archive contains 4,146,993 raw
bytes in 450,155 compressed bytes; SHA-256:
`20a66027e1c736102f8e23149894d8467bcda47b211b923386d32f4c660a378c`.
After verifying batch 8, extract `evidence-v9.tar.gz` into the same directory and
verify it with `evidence-v9.json`. Its exact packaging script is retained in
`diagnostics-v9.tar.gz`. All earlier seals and coverage databases remain unchanged.
The 331-test focused result does not replace final full-suite or benchmark gates;
auth still exceeds the deadline and the TypeScript class implementation is open.

Batch 10 retains 385 added/changed files through `2066ca7`, including Python
branch/field corrections, all intermediate failures, the immutable `34220b7`
four-input authentication measurement and its condition adjudication, TypeScript
class/receiver controls and the actual mobile spawn trace. All four auth inputs
complete, with two vulnerable condition hits and zero fixed-condition alerts;
eight fixed nondefault candidates remain explicitly qualified. This is exposed
source adjudication, not final repeated, held-out, reviewed or runtime evidence.

Every member was read back against its SHA-256. The archive contains 50,599,629
raw bytes in 1,941,930 compressed bytes; SHA-256:
`d5e418d9b4ac1ef0a3a4cf63673481936336794cbe9f8e3b7ef1a83f9dab3997`.
After verifying batch 9, extract `evidence-v10.tar.gz` and verify it against
`evidence-v10.json` before applying any later batch. The exact packaging script
is retained in `diagnostics-v10.tar.gz`. Earlier seals, the original handoff
recovery packet and all detached checkouts/coverage databases remain preserved.
The first 366-test TypeScript run overlapped formatting; the packet verifies
identical before/after ASTs for all changed scanner/test files. Mobile recording
output/command semantics and the rest of the authorized scope remain unfinished.

Batch 11 retains 170 added/changed files through `b51aee1`, including ordered
TypeScript argv, optional output guards, mobile recording source traces, all
regression failures and the five-input native mobile measurement/adjudication.
All five inputs complete with both vulnerable screenshot/recording conditions
recognized and zero fixed/control condition-matched alerts. Each input adds one
recording candidate; existing candidate content is unchanged. Fixed physical-path
uncertainty and unrelated existing candidates remain separate from the named gate.

Every member was read back against its SHA-256. The archive contains 4,282,281 raw
bytes in 378,003 compressed bytes; SHA-256:
`9b20ec89321f4e6e763d30ccea59f6d21b13a6ae10f61cb9b99df07c39dac7dc`.
After verifying batch 10, extract `evidence-v11.tar.gz` and verify against
`evidence-v11.json` before later batches. The packaging script is retained in
`diagnostics-v11.tar.gz`; all earlier seals and coverage remain untouched.
The initial Meta source-identity diagnostic selected zero records from the wrong
manifest and proves no identity; its corrected development-only check is retained
separately after this seal. Fresh holdout source remains outside tuning.

Batch 12 retains 293 added/changed files through `bfc6a7c`: shared Python HTTP
client identity and evaluation order, source-defined tool decorators, request-local
ContextVar/reset state, bounded Atlassian SDK URL requests, corrected source
inventory checks and all intermediate failures. The Atlassian fixed trace still
alerts because middleware state is not attached to the tool request; this packet
does not establish a passing condition or final technical gate.

Every member was read back against its SHA-256. The archive contains 1,245,896 raw
bytes in 129,337 compressed bytes; SHA-256:
`5f48d05b48cf3e33926e83aac6360a0813c3d2cc19e62c414665af38029837db`.
After verifying batch 11, extract `evidence-v12.tar.gz` and verify it against
`evidence-v12.json` before applying later batches. The packaging script is retained
in `diagnostics-v12.tar.gz`. Earlier seals, the original recovery packet and
detached checkouts/coverage databases remain unchanged.

Batch 13 retains 313 added/changed files through `3a2a276`: current HTTP request
identity, source-established ASGI middleware and ordered request state, optional
mapping/URL facts, metadata caching, focused vulnerable/fixed traces and every
intermediate failure. The corrected affected suite passes 606 tests; these traces
do not establish whole-input native or final benchmark acceptance.

Every member was read back against its SHA-256. The archive contains 2,040,449 raw
bytes in 577,270 compressed bytes; SHA-256:
`d2bfffadaf65fd3a3f8438209d0a3b058441665d32f21a44997faa174e63ccb9`.
After verifying batch 12, extract `evidence-v13.tar.gz` and verify it against
`evidence-v13.json` before applying later batches. Its script is retained in
`diagnostics-v13.tar.gz`. The running `continuation-atlassian-asgi-nine-native`
command and `atlassian-asgi-3a2-development/` directory are excluded until finished.
The first driver stopped at its incorrect eight-input count before scanning;
the corrected selection includes the ninth input, the historical upload safe
control. That failed driver and its exact bytes remain in this seal.
Earlier seals, recovery, detached checkouts and coverage remain unchanged.

Batch 14 retains 251 added/changed files through `18e385f`, including the finished
3a2a276 native run (four SSRF inputs complete, five upload timeouts), nested source
decorators, request caches, alternative service fields, checked URL paths, the
af67e21 timeout profile and all failed/corrected controls. Source-specific traces
do not replace native completion or final benchmark gates.

Every member was read back against its SHA-256. The archive contains 29,906,489
raw bytes in 1,085,395 compressed bytes; SHA-256:
`b602ea8e884350005a4210bae8abcb7ff4b95e83e04884443c066d17edddd2a8`.
After verifying batch 13, extract `evidence-v14.tar.gz` and verify against
`evidence-v14.json` before later batches. Its script is in `diagnostics-v14.tar.gz`.
The active `continuation-upload-native-18e` command and `upload-native-18e/`
directory are excluded until finished. Earlier seals, original recovery, detached
checkouts and coverage databases remain unchanged.


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


### Historical scoring and parent evidence through dcb965f

At immutable `8bcaded`, the first historical run completes 45/45 and source
adjudication detects all 20 vulnerable conditions. Three Excel fixed/control
parent-directory findings are conservatively scored as false alarms because
reported transport evidence did not retain the check on the requested filename.
The second run completes 43/45: the fixed Atlassian upload mutation and vulnerable
Mobile original time out at the unchanged 120-second deadline. All 43 completed
stable reports match the first run. These failures remain preserved; repeatability
and the zero-condition-false-alarm gate have not passed at that source.

`v2-historical-unrelated-ledger-8bcaded/packet.json` records all 1,484 new unrelated
instances, including explicit framework, parser and policy uncertainties. The
70 historical unrelated instances keep their original unadjudicated decisions.
The three Excel warnings stay in the condition score, not this unrelated ledger.
These are correlated warning occurrences and implementation-agent assessments,
not independent human acceptance or a measure of overall precision.

`6be3344` preserves original-path checks on visible, unresolved parent access,
including per-transport qualification that requires every observed alternative.
`dcb965f` reuses immutable TypeScript merge values and their existing metadata;
the retained Mobile profile covers byte-identical TypeScript source before this
change. Together they pass 996 shared regressions, strict 146-file typing,
lint/format and strict docs. Original counterexample and ledger-script failures
remain. Native remeasurement and final verification remain required.

Batch 25 retains 396 completed new/changed files (323,987,859 raw bytes), with
archive SHA-256 `e9df7b19f3a5e92da4f2674bea990a61dc10f42c7424d7351e9dde4dc02015b4`.
Every member was read back and hashed. Both stopped full-suite waiting queues
remain recorded; neither started a suite. The corrected immutable checkout is
`/private/tmp/mcp-phase22-verify-v2-parent-evidence`. Fresh holdout remains
unopened; Meta's fixed-condition decision, paid review, hosted verification,
human acceptance and deferred external pilot gates remain open.


### Completed benchmark evidence in batch 26

Extract and verify `evidence-v26.tar.gz` after batches 1–25 using the same
per-member procedure. Batch 26 contains 1,255 added/changed completed files
(391,561,198 raw bytes), SHA-256
`4e4521bc7d05d4e65054b117b6faa1334c69ff7cb95096e6ee882e3742b02ce6`.
It retains the dcb965f historical/full-suite gates, development and first frozen
held-out measurements, all pinned comparator scopes and source assessments,
plus coordinate failures/corrections and exact offline smoke requests. All
earlier results and failures remain. Active 6e68331 and coordinate queue records
are excluded until complete. This archive is evidence preservation, not full
Phase 22 acceptance, reviewed evaluation or hosted verification.

`evidence-v26-scope.json` clarifies the inherited manifest source label: dcb965f
is the completed benchmark/full-suite source; later coordinate diagnostics keep
their own recorded revisions and patches. The sealed archive and manifest hashes
are unchanged.
