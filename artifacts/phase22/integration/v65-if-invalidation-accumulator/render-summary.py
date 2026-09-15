"""Render the actual failed attempt and prospective contract decision."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(OUT/'assessment.json');p=read(OUT/'optimization-proposal.json')
summary=f'''# If accumulator attempt failed; explicit contract revision pending

**The one approved source-only attempt failed its required adversarial equivalence prerequisite and was reverted. Exact tested `1948bf9` is restored. No corpus input, profile or paid call ran. Phase 22 remains incomplete.**

The user's exact `approved` decision binds [authorization](authorization.json) to proposal `d8b425ba9bc7546c1f8dfa0cee9172447617b28e02da25ec89af694654f5077e`, delivered at `0f36867`. Protected source/test baselines, nine user documents, main/frozen worktrees and exact OPEN DRAFT PR37 state were verified before the [single consumed attempt](optimization-consumed.json). [The candidate](candidate-typescript-path-flow.py) and [patch](candidate.patch) remain preserved; only the If invalidation accumulator changed, and only that file was restored.

## Actual verification and failure

[Complete comparison results](equivalence.json) retain **256 ordinary full-state/environment/Value comparisons**, covering zero/one/two feasible arms, nested/absent arms, terminating arms, empty/nonempty/large baseline sets and preexisting cross-field aliases. These agree. Synthetic operation accounting shows one baseline accumulator copy and one first-arm update avoided for an ordinary evaluated If; zero-arm fallback remains unchanged. This measures operation counts, not speed or target completion.

| Explicit adversarial control | Baseline | Candidate | Result |
| --- | --- | --- | --- |
| Capture first arm's private set, then evaluate second arm | Captured set remains baseline+left; final set is separate | Later union changes captured set to baseline+left+right; final set aliases it | Failed |
| First/only feasible arm clears its private set | Original baseline keys remain in final accumulator | Adopted empty set loses baseline keys | Failed |
| Synthetic error during second arm | Complete partial state retained | Same state | Agrees |
| Synthetic interruption during second arm | Complete partial state retained | Same state | Agrees |

The comparison includes the instrumentation's retained-alias field and alias relations; the failed differences were not hidden by structural equality or excluded fields. The current shipped interpreter initializes sets, adds/updates invalidations and resets/joins independent branch baselines. No production clear or branch-set export was found in the complete occurrence inventory. The counterexamples use scanner-owned synthetic leaf overrides; **real-target reachability and detection impact are unestablished**. That does not turn them into passes: the delivered proposal explicitly required adversarial alias/shrinking equivalence without excluding a failure.

The original proposal was overbroad: it demanded behavior for injected callbacks that contradict the adoption algorithm's assumptions. This is retained as an agent preparation/contract failure. The first helper run also failed before comparison because it used `deadline=None`; [original receipt](../v65-equivalence.json) and archived helper bytes remain. Correcting only that synthetic deadline produced the completed256-case check and the two independent adversarial failures in [the corrected receipt](../v65-equivalence-corrected.json). No product change or extra optimization attempt was made during that correction.

[Restoration](restoration.json) verifies exact baseline source, and [the budget](optimization-budget-closed.json) records **one failed attempt, zero remaining**. [Assessment](assessment.json) preserves source occurrences, complete deltas and limitations. Full discovery/report/local/hosted candidate gates were conditional on this prerequisite and were not run after failure. No new candidate engineering pass or native speedup is claimed.

## Exact next proposal — explicit revision, unapproved

[Proposal](optimization-proposal.json), SHA-256 **`{sha(OUT/'optimization-proposal.json')}`**, asks for **an explicit prospective private-interpreter mutation contract revision and one new source-only attempt**. It is not permission to rerun this spent attempt or accept Phase22.

The proposed valid domain is the shipped scanner interpreter: completed arms preserve preexisting invalidations, and their private sets are not exported or retained elsewhere. Before reapplying the preserved candidate, every production writer/reset/reader, subclass and entry path must prove those invariants, including indirect access, nested control flow, termination, exceptions and preexisting aliases. A source-bound regression guard must reject a newly introduced removal/export/custom mutation unless the proof and contract are explicitly revised.

**This changes the earlier strict contract.** Only the two named synthetic callbacks that clear the private set or export a completed arm's alias would become out-of-domain negative controls after explicit user approval. Their actual baseline/candidate differences and this original failed attempt remain preserved; they are not retroactive passes. No other failing state may be excluded. All source-supported target hooks, unknown calls and mutations must still receive the original conservative analysis. No target behavior is dropped from the scanner's supported analysis because of this proposed internal contract.

A new attempt must fail and close if any shipped/source-supported flow violates the revised invariant. It must keep the original independent baseline, every per-arm copy, guard, environment update, statement traversal, merge and zero-arm fallback. No further narrowing, alternate optimization, cache, memoization, pruning, dependency, worker/resource or deadline change is included.

After the complete source proof and full-state/alias/synthetic operation checks, all ordered discovery/warnings/options and five-rule serial/parallel Python/TypeScript/mixed reports must agree. A passing candidate must then complete full actual-source local and hosted engineering under prompt section8, strict whole-scope quality, schemas/lock/notices/advisories/offline artifacts, docs/packages/installed wheels, Docker/isolation/Action/hooks, six complete production request revalidations and approved runtime/image compatibility. Freeze the actual tested source and prepare any affected regression for separate approval.

**One new source-only attempt; zero corpus/profile/retry/comparator/new-repository/runtime-campaign/target-execution/paid budget.** The revised contract is unapproved and the candidate remains reverted. No new attempt or negative-control reclassification has begun. No native speedup or1800-second completion is established; the earlier union sample share includes both arms and is not wholly removable cost.

## Restored engineering, complete audit and retained gates

[Compatible reuse](compatible-reuse.json) verifies302 engineering inputs against `1948bf9`: **2,418 passed /36 skipped** locally and in all12 hosted suites, all29 normal CI jobs and docs passed in [34793663094](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34793663094) / [34793663105](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34793663105), hosted merge `a93b425c925cd2dcaa57371597656767a32ede34`. Combined statement/branch coverage90.08%, branch-only85.92%. Six complete zero-call production replays and19 approved runtime/image bindings remain compatible. This continuation adds failed-prerequisite/restoration and final docs/package checks, not new hosted code evidence.

[Audit](audit.json) preserves all358 prior rows and adds seven: **365 total,89 original+276 added**. V64 delivery and source-only decision pass only through actual receipts, with previous rows retained. Original rows remain84 passed, two user-deferred, two proposed limitations and unresolved human acceptance. Before supplemental delivery, added rows have252 passed, six historical closure proposals and18 unresolved. The new V65-EQUIVALENCE failure remains unresolved; no failed gate or limitation is accepted.

All six native timeouts remain source-bound, each one incomplete and204unstarted closed. The separate1948bf9 profile retains148,764 parent samples, no report, final/restoration flags and the subsequent cleanup group kill; missing worker evidence proves no worker cost or launch history. Four older valid worker profiles, invalid v50 attribution/unresolved V49 preparation and both singleton failures remain unchanged. Six older closure proposals remain unaccepted.

The original four fresh repository gates still failed at `2e0efb2`:24 completed observations/12 equal pairs; FAF, Lightning Python and Engram missed named vulnerable sinks, and no-bash alerted on fixed/control cases. Quiet unsupported paths do not pass. TS94/47 pairs, Python87/36 pairs, whole25 development reuse and45+45 Linux retain their original scanner bindings, Meta/DDG errata and prior exposed/fresh failures. Original held-out counts stay10 complete/10 unsupported/5 incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable total. No subset becomes a new whole batch or independent human validation.

Git remains **312/1,040 incomplete**,728 deferred; paid benchmark/pilots deferred, Phase21 incomplete and Phase24/15 unchanged. Historical two paid calls remain **$0.071799**, with zero added. **Phase22 remains incomplete**, pending actual current-source gates or explicit applicable disposition, then separate human technical acceptance and verified accepted closeout. No merge, ready-state, release, outreach or Phase23 is authorized.
'''
(OUT/'summary.md').write_text(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v65-if-invalidation-accumulator/'
body=f'''The approved If accumulator attempt passed256ordinary state comparisons but failed the explicitly required captured-arm alias and shrinking-arm controls. It was reverted; exact tested `1948bf9` is restored. One attempt closed, zero remaining, no corpus/profile or paid calls.

[Review packet]({url}summary.md) · [365-row audit]({url}audit.json) · [explicit revised-contract proposal]({url}optimization-proposal.json)

The next proposal is unapproved: revise the private-interpreter mutation contract and permit one new source-only attempt only after every shipped writer/reader/subclass proves baseline-preserving invalidations with no escaping arm-set alias. Only the two named injected callbacks would become negative controls outside that prospective domain after explicit approval. Their original failures stay failed. No source-supported target behavior or other counterexample may be excluded. Full source/state/report and local/hosted engineering remain required; no new corpus/profile, paid call, resource or timeout revision is included.

Restored1948bf9 retains2,418tests/36skips locally and all12hosted suites,29normal CI jobs and docs passed; six complete zero-call production replays remain compatible. No new candidate engineering or speedup is established.

Phase22 remains incomplete, pending current-source gates, explicit human technical acceptance and accepted closeout. Git312/1040 incomplete; paid benchmark/pilots deferred, Phase21 incomplete, Phase24/15 unchanged. No merge, ready-state, release, outreach or Phase23.
'''
(OUT/'pr-body.md').write_text(body)
print('Rendered failed strict contract and exact unapproved prospective revision.')
