"""Render measured profile coverage and the exact unapproved source-only decision."""
import hashlib
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = read(OUT/'assessment.json')
p = read(OUT/'optimization-proposal.json')
v = read(OUT/'validation.json')
t = a['timing']
metrics = '\n'.join(f"| {r['rule']} | {r['samples']:,} | {r['registration_inclusive_percent']:.4f}% | {r['literal_json_encoder_leaf_percent']:.4f}% | {r['final_worker_snapshot']} / {r['signal_and_timer_state_restored']} |" for r in a['sample_rows'])
roles = ', '.join(r['rule'] for r in a['sample_rows'])
summary = f'''# Parent-and-worker profile assessed; invalidation-accumulator decision pending

**The single approved FAF profile at frozen `1948bf9` timed out after {t['elapsed_seconds']:.9f} seconds, with {a['samples']:,} retained partial samples from {len(a['sample_rows'])} verified process snapshot(s): {roles}. No report exists; cleanup passed and the one-use budget is closed. Phase 22 remains incomplete.**

The user's exact `approved.` decision is bound in [authorization](../v63-shared-discovery-regression/diagnostic-authorization.json) to diagnostic proposal `6e8e955b82f1c17ea71110c1b348fa46dc546c127fa1588578a9a7bca932652b`, delivered at `7d6e01a`. [Preflight](../v63-shared-discovery-regression/diagnostic-preflight.json) verified actual frozen imports, protected source/docs, exact OPEN DRAFT PR37 state and no conflicting owned processes/containers. The [one-use token](../v63-shared-discovery-regression/diagnostic-consumed.json) and [attempt](attempt.json) bind the actual execution. Scanner `{a['scanner']['revision']}`, source SHA-256 `{a['scanner']['source_sha256']}`, harness `{a['scanner']['harness_sha256']}`; original FAF source/configuration/condition and lock remain unchanged.

## Actual output and attribution

[Validation](validation.json) verifies all retained process identities, frame/stack counts, source hashes, original input and configuration, actual incomplete harness output and closed budget. Whole-input time was **{t['elapsed_seconds']:.9f} seconds**; **{t['elapsed_including_cleanup_seconds']:.9f} seconds including cleanup**, within its separate 15-second allowance. Supervisor return code was `{t['returncode']}`, timeout `{t['timed_out']}`, cleanup verified `{t['cleanup_verified']}`. The harness retained one incomplete outcome with zero requests/model calls. Its actual reason and duration remain in validation, without replacing the supervisor timing. The log, periodic snapshots, any partial temporary snapshot and final/restoration flags are preserved exactly.

**Finding, warning, surface, detection, guard-support and ordered-repeat results are unknown, not zero.** There is no native JSON/SARIF report to validate or compare with the original `2e0efb2` report. This diagnostic is not an uninstrumented regression retry. All earlier 205-observation budgets remain closed, including `1948bf9`'s separate native timeout and 204 unstarted observations.

| Sampled process | Retained samples | Registration inclusive share | Literal JSON encoder leaf share | Final snapshot / timer restored |
| --- | ---: | ---: | ---: | --- |
{metrics}

Every attributed process has actual `workers`, `typescript_path_flow` and `typescript_discovery` import roots and full scanner/harness identity checked before sampling or target-source access. [Sample attribution](sample-attribution.json) partitions each process's leaf counts and preserves overlapping inclusive functions and all generated-constructor callers. [Source assessment](source-assessment.json), [frame bindings](frame-source-bindings.json) and [frame contexts](frame-contexts.json) account for all retained source locations, registration call sites, JSON encoder callers and sampled stages.

The actual snapshot/identity inventory is the extent of measured process coverage. **Missing worker snapshots do not prove that workers never launched; parent samples establish no worker cost.** Parent and worker denominators are separate and never summed as savings. Legacy `worker_cpu_seconds` and `final_worker_snapshot` fields describe the sampled process, including the parent. The retained CPU interval and start/end flags are preserved per process; missing final/restoration receipts are unknown, not synthetic passes.

The source establishes that completed TypeScript discovery runs in the parent before existing worker dispatch. `factory_tools` invokes `RegistrationFlow.initialize` for eligible module trees, using the full TypeScript flow. At each `If`, the current source makes an independent pre-arm invalidation baseline, copies it again into an accumulator, copies the original baseline before every feasible arm, and unions every evaluated arm into the accumulator. The first evaluated arm already carries its own baseline copy. The full source occurrence map of invalidation readers, updates and resets is retained in the source assessment.

| Parent leaf site | Samples | Share | Proposed treatment |
| --- | ---: | ---: | --- |
| Initial baseline copy, line 669 | 2,141 | 1.4392% | Retained |
| Accumulator baseline copy, line 670 | 3,747 | 2.5188% | Avoid where a feasible arm supplies the result |
| Per-arm baseline copy, line 676 | 7,174 | 4.8224% | Retained for isolation |
| Per-arm environment copy, line 677 | 6,873 | 4.6201% | Retained |
| Accumulator union, line 682 | 13,032 | 8.7602% | Avoid only the first-arm union; later unions remain |

These are sampled sites, not operation/cardinality counts. The union samples do not distinguish first and later arms, so **2.52% + 8.76% is not an achievable-savings estimate**. Guard evaluation, traversal, every feasible arm, environment/Value updates and all security/coverage work remain. The preliminary literal-string option and its initial assessment/helper bytes are preserved in `preliminary-literal-key`; final review selected the smaller existing-set change before any optimization proposal was executed or approved. Literal JSON serialization remains measured at4.2046% of parent leaves and is not the proposed target.

The parent snapshot records `final_worker_snapshot=true` and `signal_and_timer_state_restored=true`. The supervisor subsequently reports returncode **-9** and `remaining_group_killed=true`; shell exit247 encodes that -9 return. Cleanup finished after **{t['elapsed_including_cleanup_seconds']-t['elapsed_seconds']:.6f} seconds** of its15-second allowance. A retained final sample proves that sampler finalization point, not successful process teardown. No post-sampling teardown trace establishes why the remaining process group required a kill. The harness logged the incomplete outcome at1,794,931ms with null reason; no `child-result.json` or report exists.

Sampling remains statistical: Python main-thread signal delivery, native-code/GIL delays and snapshot-thread CPU can charge overhead to an interrupted scanner frame. Inclusive shares overlap, final intervals may be absent, and percentages are neither exact CPU fractions nor removable-cost or speedup estimates. This run does not establish native completion, a worker-launch history or detection/compatibility. No scanner method, source, worker count, timeout, dependency or resource policy changed.

## One source-only proposal, unapproved and unimplemented

[Optimization proposal](optimization-proposal.json), SHA-256 **`{sha(OUT/'optimization-proposal.json')}`**, requests **one attempt confined to the TypeScript `If` invalidation accumulator**. Keep the independent original baseline and a fresh copy for every feasible arm. Build the result lazily from the first evaluated arm, then union later evaluated arms; include terminating and absent arms exactly as before. Preserve the original fresh-copy fallback if no feasible arm ran. No first-arm invalidation may leak into the mutually exclusive arm.

Before adopting an arm's set, prove that preexisting invalidations cannot shrink on relevant production paths and that no observable retained alias can be changed by later unions. Trace every invalidation writer/reset/reader. Preserve full environments, every Value field and interning relation, all flow state/source-node aliases, ordered warnings, registrations, guard/sink support and complete reports. No baseline mutation or cross-arm state sharing is permitted.

Required synthetic comparisons cover zero/one/two feasible arms; true/false/unknown facts; absent, terminating and throwing arms; empty/nonempty/large preexisting sets; arm-specific escapes and reversed arm order; nested If/Try/loops/functions/constructors/imports; instance/credential invalidation; deadline/errors and partial-state/alias behavior. Adversarial shrinking/alias behavior must be accounted for rather than excluded. Operation accounting must show the redundant accumulator copy/first union avoided while every per-arm copy, environment copy, guard, statement, merge and state update still executes. All five rules and full ordered serial/parallel Python/TypeScript/mixed reports must remain equivalent.

The proposal changes no cache, interpreter memoization, AST, pruning, guard, traversal, merge semantics, warning, dependency, worker count, resource or deadline policy. It is not a semantic contract revision. If full equivalence, alias/monotonicity or avoided-work checks fail, preserve and close the one attempt; do not switch targets.

If that prerequisite passes, complete affected/full local and hosted engineering, strict whole-scope quality, schemas/lock/notices/advisories/offline artifacts, docs/packages/installed wheels, Docker/isolation/Action/hooks, all six complete production request revalidations and approved runtime/image compatibility. Freeze the actual tested candidate and prepare any affected regression for separate approval.

**The prospective source-only attempt includes zero corpus observations, profiles, retries, comparators, new repositories, runtime campaigns, target execution and paid calls. It is unapproved and unimplemented.** Per-arm copies and later unions still run. Real arm counts/cardinalities and achieved savings are unknown; there is no native-speedup or1800-second completion guarantee.

## Preserved engineering and requirements

[Compatible reuse](compatible-reuse.json) binds 302 engineering inputs to tested `1948bf9`: **2,418 passed / 36 skipped** locally and in all **12 hosted suites**, all **29 normal CI jobs** and docs passed in [34793663094](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34793663094) / [34793663105](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34793663105). Hosted merge `a93b425c925cd2dcaa57371597656767a32ede34` has the candidate tree. Combined statement/branch coverage is **90.08%**, branch-only **85.92%**. Six complete zero-call production replays and 19 approved runtime/image bindings remain compatible. Final README-aware packages/docs are checked separately. No new hosted code run, paid capture or Git campaign is claimed.

[Audit](audit.json) retains **all 352 prior requirements** and six new rows: **358 total, 89 original + 269 added**. V63 delivery and diagnostic decision pass only through their actual receipts, with previous rows retained. Original dispositions stay 84 passed, two explicitly user-deferred, two proposed limitations and one unresolved human acceptance. Before supplemental delivery, added rows have 246 passed, six unaccepted historical closure proposals and 17 unresolved. All prior rows have current execution interpretations preserving actual source-bound evidence. Passing this diagnostic's attribution does not waive a failed detection or compatibility gate.

All six native timeouts remain at their actual scanners (`17b4784`, `6e4fd67`, `a36f696`, `dc73715`, `7bf4c6e`, `1948bf9`), each one incomplete and 204 unstarted closed. Four older valid worker profiles retain 86,659 / 79,307 / 78,769 / 432,756 samples at their actual earlier scanners; this new partial profile has different process coverage. Invalid v50 stale-worker attribution and unresolved V49 preparation remain. Both singleton equivalence failures remain failed and unaccepted despite the later explicitly approved credential correction. The six historical closure proposals—V14-RETENTION, V21-SEQUENCE, V21-FRESH-PROPOSAL, V25-EXPOSED-REGRESSION, V27-REGRESSION, V39-EVALUATION—remain unaccepted.

Original four-repository first-frozen evidence remains **24 completed observations, 12 equal pairs, all four repository gates failed at `2e0efb2`**: FAF, Lightning's Python member and Engram missed named vulnerable sinks; no-bash falsely alerted on fixed/control inputs. Unsupported quiet paths do not pass. Earlier TS94/47 pairs at `2e0efb2`, Python87/36 pairs at `8c62567`, whole25 development reuse and45+45 Linux at `1f3f72f`, Meta/DDG language/condition errata and prior fresh misses/false alerts retain their actual bindings. Language subsets are not new whole batches. Original held-out denominators remain10 complete/10 unsupported/5 incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable total. Same-agent source assessment is not independent human validation or broad accuracy/runtime safety proof.

Git remains **312/1,040 incomplete**, 728 deferred; the396-request paid benchmark and pilots remain deferred, Phase21 incomplete and Phase24/15 unchanged. Two historical paid calls remain **$0.071799 total**, with zero added. **Phase22 remains incomplete**, pending actual current-source gates or an explicit applicable disposition, then separate human technical acceptance and verified accepted closeout. No merge, ready-state change, release, outreach or Phase23 is authorized.
'''
with (OUT/'summary.md').open('x') as stream: stream.write(summary)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v64-shared-discovery-sampling/'
body = f'''The approved FAF parent-and-worker profile at `1948bf9` timed out after {t['elapsed_seconds']:.3f} seconds, retaining {a['samples']:,} partial samples from {roles}. No report exists; cleanup passed and the one-use budget is closed. Detection and current-source compatibility remain unestablished.

[Review packet]({url}summary.md) · [358-row audit]({url}audit.json) · [exact source-only proposal]({url}optimization-proposal.json)

The next proposal is unapproved and unimplemented: one change to avoid redundant If invalidation-accumulator construction while retaining the original baseline, independent per-arm copies and all guards/traversals/merges. Complete branch-isolation, alias/state and report equivalence plus full local/hosted engineering are required. No cache or interpreter memoization is proposed. No new corpus/profile/retry, paid call, resource change or timeout revision is included. Sample shares establish no speedup or completion guarantee.

Product retains verified `1948bf9`: 2,418 tests / 36 skips locally and in all 12 hosted suites, 29 normal CI jobs and docs passed. Six complete requests retain zero-call replay evidence. All historical failed gates remain preserved; parent and worker coverage are assessed separately.

Phase 22 remains incomplete pending current-source gates, explicit human technical acceptance and accepted closeout. Git 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, ready-state, release, outreach or Phase 23.
'''
with (OUT/'pr-body.md').open('x') as stream: stream.write(body)
print('Rendered exact partial profile,358-row audit and unapproved invalidation-accumulator proposal.')
