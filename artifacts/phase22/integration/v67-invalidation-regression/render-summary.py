"""Render actual outcome, retained evidence and the exact pending decision."""
import hashlib,json
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(out/'assessment.json');p=read(out/'diagnostic-proposal.json');digest=sha(out/'diagnostic-proposal.json')
summary=f'''# Invalidation regression timed out; bounded diagnostic proposed

**The approved regression at `4145d35` stopped on the first FAF vulnerable input after {a['whole_seconds']:.9f} seconds. One incomplete input, no reports, 204 unstarted observations closed, zero remaining. Phase 22 remains incomplete.**

The exact `approved` decision binds [authorization](../v66-invalidation-contract/evaluation-authorization.json) to the delivered 205-observation proposal `a925c4e396b328e2c49f84669fb710f09c58f3490956d868e70a58786ae3c2bf` at `da7557076b122611dbfedd3587450796073af288`. [Preflight](../v66-invalidation-contract/execution-preflight.json) verified the frozen scanner, intended imports, protected state and absent conflicting work before launch. Scanner `{a['scanner']['revision']}`, source `{a['scanner']['source_sha256']}`, harness `{a['scanner']['harness_sha256']}`, lock `{p['lock_sha256']}`. Original source/configuration, rules-only treatment, numerical bounds and complete schedule matched approval. The later `continue` instruction continues assessment/delivery; it does not approve the new profile or technically accept Phase 22.

## Actual outcome and assessment

[Validation](validation.json), [assessment](assessment.json), [raw packet](raw/packet.json) and [execution](execution.json) retain {a['whole_seconds']:.9f} seconds whole-input time and {a['whole_including_cleanup_seconds']:.9f} seconds including cleanup. Cleanup used {a['whole_including_cleanup_seconds']-a['whole_seconds']:.3f} seconds of its separate 15-second allowance, without a remaining-group kill. The outer sequence took {a['sequence_seconds']:.9f} seconds and did not itself time out. The measurement harness retained an incomplete outcome at {a['harness_wall_duration_ms']:,} ms, null reason, no requests and zero model calls. The supervisor's termination raises SystemExit, which bypasses the harness's `except Exception` while its finally writer preserves the incomplete result. The evaluator then fails its completion assertion. These retain their distinct timing and error meanings.

**No native JSON/SARIF report exists. Finding, warning and surface counts are unknown, not zero.** Named detection, fixed/control support and ordered-repeat equality are unmeasured. All remaining 23 four-repository and 181 prior-language observations are unstarted and closed. The original labels, source prerequisites and old reports remain unchanged. No output inventory is represented as a measured zero-diagnostic result.

No stack or stage trace identifies current residual costs. Source still computes completed TypeScript discovery in the parent before existing worker dispatch and reuses it for worker consumers/coverage. The prior `1948bf9` profile predates the approved accumulator change. Its 148,764 parent samples, absent worker snapshots/report and forced teardown after a final restored-timer snapshot remain source-bound; the later teardown delay's cause is unestablished. Earlier overlapping profile shares are not current costs or removable fractions. Child resource totals include descendants and cannot establish stage costs or worker launch history. **Native speedup and 1800-second completion remain unestablished.**

[Owned-work verification](owned-work.json) confirms no remaining owned process or Sentinel container. The [budget receipt](budget-closed.json) closes this sequence. No retry, profile, comparator, target execution, new repository, resource/deadline change or paid call occurred.

## Exact next diagnostic — unapproved and unexecuted

[Proposal](diagnostic-proposal.json), SHA-256 **`{digest}`**: **one sampled FAF vulnerable input at frozen `4145d35`, 1800-second whole-input maximum plus 15-second cleanup**. The 120-second target stays informational. No uninstrumented observation or optimization attempt is included.

The existing parent/worker sampler is reused: the five sampling functions are AST-identical, with 100 Hz CPU timers, 1024-frame cap and atomic 15-second snapshots. It surrounds parent `measure()` and wraps each existing worker entry: one parent and at most four existing flow workers, without changing scanner methods or worker count. Actual parent/worker/flow/discovery import paths and full source/harness identity are checked before source access and timer/snapshot access. The attempted-input timer begins before child imports/preflight and includes configuration, materialization, analysis, reports and sampling overhead; cleanup is separately bounded. Read-only launcher provenance preflight precedes consumption and performs no scan.

[Worker controls](sampler-selfcheck/packet.json) preserve six synthetic combination vectors and scanner methods, validate sample/frame references and restore timer/signal state; the stale-root control rejects before sampling/target access. [Parent controls](parent-sampler-selfcheck/packet.json) exercise actual wrapping with completed/interrupted synthetic work, restore timer/worker entry and reject stale parent identity before input access. [Missing-approval validation](../v67-diagnostic-boundary.json) rejects before output/token creation. These are synthetic checks, with zero corpus/profile executions.

Sampling has native-code/GIL signal-delivery, snapshot-thread and serialization biases. Parent and worker denominators are separate; inclusive stacks overlap and are not additive savings. Parent sampling excludes pre-measure provenance CPU but that child overhead remains inside whole-input accounting. Legacy `worker_cpu_seconds` / `final_worker_snapshot` fields describe the parent when `rule=parent`. Missing/mismatched identity invalidates attribution; absent worker snapshots alone do not prove workers never started. Retain periodic/incomplete temporary outputs if cleanup prevents a final receipt; do not extend cleanup. A completed report would require JSON/SARIF validation, complete ordered comparison to original `2e0efb2` with only the established 11 volatile exclusions and assessment of every change. A profile is not a native regression pass.

**One attempt only, including timeout/interruption/identity failure; zero retries, comparators, hosted dispatches, target execution, paid calls, optimizations or resource/deadline changes.** No diagnostic authorization, consumed token or `v68-invalidation-sampling` output exists. Execution requires a separate decision on this exact proposal.

## Engineering, failures and acceptance

[Compatible reuse](compatible-reuse.json) verifies all **303 engineering inputs** against frozen `4145d35`: **2,419 passed / 36 skipped** locally and all **12 hosted suites**, **29 normal CI jobs** and docs passed in [34808261686](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34808261686) / [34808261635](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34808261635). Actual hosted merge `90eb6e874eed01d15d23decb2980fd91238aae26`, tree `d78c8dff1394348242d1332df8439f45011450dc`, matches the candidate tree. Combined statement/branch coverage **90.08%**, branch-only **85.92%**. Six full zero-call production request replays and approved runtime/image bindings remain compatible. This continuation adds outcome/preparation and docs/package checks, not another hosted code run or production capture.

The explicit v66 private mutation-domain revision, full production proof/comparisons and source-only budget remain in the [prior packet](../v66-invalidation-contract/summary.md). The original v65 strict-equivalence failure and both exact injected negative-control deltas remain unresolved as historical measurements. v55/v56 singleton failures remain unaccepted. No contract change has been inferred from this timeout.

The [audit](audit.json) preserves all **376 prior rows** and adds seven: **383 total = 89 original + 294 added**. V66 delivery/evaluation-decision changes retain full prior rows and actual receipts. Original dispositions remain 84 passed, two user-deferred, two proposed limitations and one unresolved human acceptance. Added dispositions before supplemental delivery are 269 passed, six proposed historical closures and 19 unresolved. Each prior requirement retains source-specific evidence/current interpretation, with the complete old status preserved. The six unaccepted closure IDs remain V14-RETENTION, V21-SEQUENCE, V21-FRESH-PROPOSAL, V25-EXPOSED-REGRESSION, V27-REGRESSION and V39-EVALUATION.

All seven native timeouts remain at `17b4784`, `6e4fd67`, `a36f696`, `dc73715`, `7bf4c6e`, `1948bf9` and now `4145d35`, each one incomplete and 204 unstarted closed. Five valid partial profiles retain their actual sources and separate denominators: four earlier worker samples 86,659 / 79,307 / 78,769 / 432,756 and the later 148,764 parent samples. Invalid stale-worker preparation and V49-DIAGNOSTIC-PREPARATION remain unresolved. Original four-repository result remains **24 complete observations, 12 equal pairs, all four gates failed at `2e0efb2`**: FAF, Lightning Python and Engram missed named vulnerable sinks; no-bash falsely alerted on fixed/control inputs. Quiet unsupported negatives do not pass.

Earlier TS94/47 pairs at `2e0efb2`, Python87/36 pairs at `8c62567`, whole25 development reuse and 45+45 Linux at `1f3f72f` retain source bindings and Meta operator errata. No subsets become new whole Linux batches. Original memory-keeper false alerts, DDG unsupported fixed send and language-metadata erratum, Lighthouse misses, held-out 10 complete/10 unsupported/5 incomplete and zero hits among four completed vulnerable inputs out of ten vulnerable total remain visible in the full audit. Same-agent review is not independent validation, training-data novelty, broad accuracy or runtime safety proof.

The evidence-reuse helper initially referenced nonexistent `v66-shared-tool-discovery`, failing before source verification or output; its archived helper/log are retained. Correcting only that path passes the complete 303-input/replay proof. A discovery-receipt name was corrected from a source listing during unexecuted preparation. Neither is a scanner counterexample or extra corpus attempt. Full command/failure provenance retains all actual failures.

Git stays **312/1,040 incomplete**, 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls remain **$0.071799 total**, with zero added. **Phase 22 is incomplete**, pending actual current-source gates or an explicit applicable user disposition, then separate human technical acceptance and verified accepted closeout. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
(out/'summary.md').write_text(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v67-invalidation-regression/'
body=f'''The approved regression at `4145d35` timed out on its first FAF input after {a['whole_seconds']:.6f} seconds. No report exists; cleanup passed and all 204 unstarted observations are closed. Detection and compatibility remain unestablished.

[Review packet]({url}summary.md) · [383-row audit]({url}audit.json) · [exact diagnostic proposal]({url}diagnostic-proposal.json)

The next proposal is unapproved and unexecuted: one sampled FAF input, 1800-second maximum plus 15-second cleanup, using the existing parent and up to four existing worker samplers. Current source identities, stale-root, completion/interruption, timer and missing-approval controls pass. No optimization, retry, comparator, target execution, resource/deadline change or paid call is included. Proposal SHA-256: `{digest}`.

Product retains engineering-tested `4145d35`: 2,419 tests / 36 skips locally and all 12 hosted suites, 29 normal CI jobs and docs passed. Six full production requests retain zero-call replay evidence. All earlier failures, including the original strict invalidation equivalence failure, remain preserved; no native speedup is established.

Phase 22 remains incomplete pending current-source gates, explicit human technical acceptance and accepted closeout. Git 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge, ready-state change, release, outreach or Phase 23.
'''
(out/'pr-body.md').write_text(body)
print('Rendered actual outcome, 383-row audit and exact unapproved diagnostic.')
