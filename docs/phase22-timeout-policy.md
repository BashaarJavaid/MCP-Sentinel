# Phase 22 static timing policy

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
