"""Preserve all prior requirements and reconcile the assessed current-source profile."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=OUT.parents[3]
OLD=BASE/'v60-long-timeout-regression'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
a=read(OUT/'assessment.json')
assert a['validation_passed'] and a['report_count']==0 and a['incomplete_inputs']==1
assert a['source_assessment_complete_for_retained_outputs'] and a['budget_closed']
old=read(OLD/'audit.json')
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id']=='V60-DELIVERY':
        row['previous_row']=copy.deepcopy(row)
        row.update(disposition='passed',evidence=['artifacts/phase22/integration/v60-long-timeout-regression/delivery-verification.json'],assessment='Actual 777c752 draft head/base/title/body readback passed; no native failure or technical acceptance was accepted.')
new=[
 ('V61-AUTH','Bind the exact one-use 1800-second profile approval to the delivered proposal and frozen scanner','passed',['../v60-long-timeout-regression/diagnostic-authorization.json','../v60-long-timeout-regression/diagnostic-preflight.json']),
 ('V61-PROFILE-VALIDATION','Validate worker identities, every retained sample/frame count, actual output and cleanup with the profile budget closed','passed',['validation.json','owned-work.json']),
 ('V61-SOURCE-ASSESSMENT','Assess all retained source/frame attribution and distinguish sampled costs from source-established duplicate discovery','passed',['assessment.json','source-assessment.json','frame-contexts.json','sample-attribution.json']),
 ('V61-OPT-PREPARATION','Prepare one bounded source-only shared tool-discovery reuse proposal with no implementation or new measurement','passed',['optimization-proposal.json']),
 ('V61-OPT-DECISION','Obtain a separate exact decision before the source-only optimization attempt','unresolved',['optimization-proposal.json']),
 ('V61-DELIVERY','Seal the assessed profile and complete audit, then verify delivery to the existing draft','unresolved',[]),
]
for identity,requirement,disposition,evidence in new:
    rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence],'assessment':'One sampled timeout with verified current-source worker identities, no report and zero remaining budget. No native completion, corrected discrimination, compatibility, speedup or technical acceptance follows. The source-only reuse proposal remains unapproved.'})
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==240 and len(rows)==246
assert len({r['id'] for r in old['requirements']+rows})==335
audit=copy.deepcopy(old)
audit['historical_v60_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},diagnostic_approved=True,diagnostic_executed=True,diagnostic_attempts=1,diagnostic_completed_inputs=0,diagnostic_budget_closed=True,diagnostic_remaining=0,valid_current_source_profiles=1,current_diagnostic_approved=True,current_diagnostic_executed=True,optimization_prepared=True,optimization_approved=False,optimization_attempts=0,optimization_synthetic_verified=False,current_optimization_prepared=True,current_optimization_approved=False,current_optimization_attempts=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,status=f'One approved profile at 7bf4c6e timed out after {a["timing"]["elapsed_seconds"]:.6f} seconds with four verified worker identities and {a["samples"]} partial samples. No report; budget closed. One source-only shared tool-discovery reuse attempt is prepared, unapproved and unstarted. All native/fresh failures remain unchanged.')
audit['current_source_input_accounting']={'native_regression':{'attempts':1,'complete':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'budget_closed':True},'sampled_diagnostic':{'attempts':1,'complete':0,'incomplete':1,'remaining':0,'budget_closed':True},'total_attempted_inputs':2,'qualification':'The inherited current_source_corpus_observations field counts the one native regression attempt. This profile is accounted separately; it is no native repeat or compatibility observation.'}
audit['current_budget_interpretation']='The 205-observation native budget stopped after one input and closed 204 unstarted. The separately approved single sampled input is now also consumed and closed. One new source-only optimization is proposed, unapproved and unstarted; all old budgets stay closed.'
audit['current_evidence']={n:sha(OUT/n) for n in ['assessment.json','validation.json','source-assessment.json','sample-attribution.json','optimization-proposal.json','compatible-reuse.json','owned-work.json']}
assert audit['additional_scope_dispositions']=={'passed':224,'unresolved':16,'proposed documented limitation awaiting decision':6}
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):assert prior==current or current.get('previous_row')==prior
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':329,'total_rows':335,'updated_rows':['V60-DELIVERY'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
metrics=a['sample_rows']
low=min(r['registration_inclusive_percent'] for r in metrics)
high=max(r['registration_inclusive_percent'] for r in metrics)
table='\n'.join(f"| {r['rule']} | {r['samples']:,} | {r['snapshot_worker_cpu_seconds']:.3f} | {r['registration_inclusive_percent']:.2f}% | {r['merge_inclusive_percent']:.2f}% | {r['leaf_percent'].get('json_encoder',0):.2f}% |" for r in metrics)
flags='; '.join(f"{r['rule']}: final={r['final_worker_snapshot']}, restored={r['signal_and_timer_state_restored']}" for r in metrics)
summary=f'''# Thirty-minute profile assessed; shared discovery proposal pending

**The approved single FAF profile at `7bf4c6e` retained four verified worker identities and {a['samples']:,} partial samples, then timed out without a report. The one-use profile budget is closed. Phase 22 remains incomplete.**

The exact `approved` decision binds [authorization](../v60-long-timeout-regression/diagnostic-authorization.json) to proposal `bf32e8dcd11870afcb2aa4ebe99085bc3f04433fba929501ba758441401801d5`, delivered at `777c752`. Frozen scanner: `{a['scanner']['revision']}`; source SHA-256: `{a['scanner']['source_sha256']}`. All four actual worker/flow imports and scanner/source/harness identities verified before timer setup or target snapshot access. Source, configuration, original condition and sampler match the approved proposal.

[Validation](validation.json) records **{a['timing']['elapsed_seconds']:.9f} seconds** whole-input time and **{a['timing']['elapsed_including_cleanup_seconds']:.9f} seconds** including cleanup. Cleanup passed within its separate 15-second allowance; remaining-group kill: `{a['timing']['remaining_group_killed']}`. No owned process or container remains. The harness interval is {a['harness_outcome']['wall_duration_ms']:,} ms, incomplete with its retained reason. The scanner's shared 1800-second policy remains in place.

**No JSON/SARIF report exists. Findings, warnings, surfaces, vulnerable detection and fixed/control discrimination remain unknown.** This is one sampled input, not a native retry, ordered repeat or compatibility pass. The separate native 205-observation budget remains one incomplete plus 204 unstarted closed. No optimization, extra profile, comparator, target execution or paid call occurred.

[Sample attribution](sample-attribution.json), [frame contexts](frame-contexts.json) and [source assessment](source-assessment.json) retain every sample count, recorded frame reference, leaf/inclusive attribution and source hash. Each row describes its worker's last valid periodic snapshot:

| Worker | Samples | Snapshot CPU seconds | Registration inclusive | Merge inclusive | JSON encoder leaf |
| --- | ---: | ---: | ---: | ---: | ---: |
{table}

Snapshot flags: {flags}. Partial snapshots may omit the final interval and restoration receipt when mandatory cleanup stops workers. Any unfinished atomic `.tmp` files are retained as non-authoritative output, never substituted for complete snapshots. Snapshot CPU intervals include worker startup and sampling overhead and differ from whole-input wall time. Inclusive percentages overlap; they cannot be added as independent costs. Generated/interpreter frames lack source bytes and remain explicitly labeled. JSON encoder caller attribution distinguishes scanner serialization from frames without a scanner caller.

TypeScript registration/factory traversal appears in **{low:.2f}–{high:.2f}%** of each retained worker snapshot. The source shows that `run_flow_rules` parses TypeScript once but then creates four separate worker contexts; each computes `tools()` and `factory_tools()` before its own security analysis. Parent coverage later requests `tools()` again. These are source-established repeated discovery paths. The profile has not measured a single producer's completion time or the complete later rule-specific/HTTP/coverage work. Signal/GIL/native-code delivery, snapshot-thread overhead, unprofiled parent stages and differing partial intervals limit attribution; no savings percentage or native speedup is claimed.

[The exact next proposal](optimization-proposal.json), SHA-256 `{sha(OUT/'optimization-proposal.json')}`, requests **one source-only implementation attempt**, currently **unapproved and unstarted**, to reuse completed TypeScript MCP tool discovery within one immutable source context and through the existing private worker IPC. It targets `typescript_discovery.py`, `model.py` and `workers.py`; use existing caching/IPC patterns, with no new dependency, global/cross-scan cache, HTTP-result cache, general interpreter memoization, pruning, worker-count/resource change or timeout revision.

The same pickle graph must carry parsed trees/files and bindings so symbols refer to the same reloaded objects. Rebuild identity-keyed indexes; never transport stale integer `id()` keys. Preserve every ordered binding, factory/SDK registration, warning and source range, including module option-cache warning effects, pre-existing warnings and repeated-call deduplication. Replay warnings at their original consumption point. Empty completed discovery differs from missing data; incomplete or failed discovery cannot become a cached success. Every rule-specific detector and coverage interpretation must still execute fully.

Required synthetic checks compare complete binding/alias identities, rule state and whole ordered reports before/after reuse and across IPC. They cover constructors/setters/imports/workspaces, unsupported/rebound/empty registrations, warning order, context separation, small/selected-rule/Python/mixed paths, deadline failures and cleanup. Invocation accounting must establish avoided duplicate producer work while all security analyses still run. Any equivalence or avoided-work failure closes this one attempt without switching target. If successful, complete full local/hosted engineering, package/schema/lock/docs and zero-call production/runtime verification, then freeze and prepare a separate native regression proposal. **Zero corpus observations, profiles, retries, comparators, target executions, runtime campaigns or paid calls are authorized by this proposed source-only scope.** Reuse may still fail to bring FAF within 30 minutes.

All five native timeouts remain at their actual sources: `17b4784`, `6e4fd67`, `a36f696`, `dc73715` and `7bf4c6e`, each one incomplete with 204 unstarted closed. Earlier valid partial profiles retain 86,659 / 79,307 / 78,769 samples at the first three sources; this fourth valid profile is separately bound to `7bf4c6e`. The invalid v50 stale-root attempt remains unusable and V49-DIAGNOSTIC-PREPARATION unresolved. Both failed singleton attempts and the later explicit credential correction retain their individual facts, as do all six unaccepted historical closure proposals. No historical failure becomes a pass or accepted limitation.

The original fresh four-repository result remains **24 completed observations, 12 equal pairs and all four gates failed at `2e0efb2`**: FAF actual read unsupported; no-bash one vulnerable hit and two fixed/control false alerts per batch; Lightning actual client-get and Engram named manifest-write unresolved. Later source corrections and measurements are exposed regression, not clean unseen-source discrimination.

[Compatible reuse](compatible-reuse.json) binds all **302 engineering inputs** to tested `7bf4c6e`: **2,403 tests / 36 skips locally and in all 12 hosted suites**, all 29 normal CI jobs and docs passed in [34784085204](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085204) / [34784085193](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34784085193), actual hosted merge `aa28ae250a411ba1773e919ad39fc656de842b8c`. Combined statement/branch coverage is 89.98%, branch-only 85.86%. Six zero-call production replays and 19 approved Git runtime component bindings remain compatible. This continuation adds profiling/source assessment and final docs/package checks, not a new hosted code pass. File/worktree restoration and selective Docker cleanup remain preserved.

One reused evidence helper initially expected a native regression `raw/packet.json`, absent from the profile layout. It failed before writing a result; checking the actual profile `budget-closed.json` passed under a new label. Both sources, logs and receipts are retained. No scanner change or additional observation occurred.

The [audit](audit.json) preserves all **329 prior requirements** and adds six: **335 total, 89 original + 246 added**. Original rows remain 84 passed, two user-deferred, two proposed limitations and one unresolved human acceptance. Added rows have 224 passed, six historical closure proposals and 16 unresolved before supplemental delivery. V60 delivery is updated only with its actual readback and previous row retained. Current-source discrimination, compatibility and technical acceptance remain unresolved.

TS 94 at `2e0efb2`, Python 87 at `8c62567` and whole 25 development reuse plus 45+45 Linux at `1f3f72f` retain actual evidence and Meta operator erratum. Language subsets are never pooled into a new whole batch. Original memory-keeper false alerts, DDG initially unsupported fixed send and incorrect TypeScript metadata despite Python execution, Lighthouse misses and the held-out 10 complete/10 unsupported/5 incomplete with zero hits among four completed vulnerable inputs out of ten vulnerable total remain unchanged. Same-agent review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git stays **312/1,040 incomplete**, 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. Explicit human technical acceptance and verified accepted closeout remain pending. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'summary.md').open('x') as f:f.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v61-faf-long-timeout-sampling/'
body=f'''The approved single FAF profile at `7bf4c6e` timed out after {a['timing']['elapsed_seconds']:.3f} seconds without a report. Four verified workers retained {a['samples']:,} partial samples; cleanup passed and the one-use budget is closed. Registration discovery appears in {low:.2f}–{high:.2f}% of each worker's samples. These are overlapping partial shares, not a measured speedup.

[Review packet]({url}summary.md) · [335-row audit]({url}audit.json) · [source-only reuse proposal]({url}optimization-proposal.json)

The next proposal is unapproved and unstarted: one implementation attempt to reuse completed TypeScript tool discovery across the existing workers and coverage, preserving ordered warnings and source-node identity. Every rule-specific analysis still runs. Full verification is required; no corpus/profile/retry/comparator, target execution or paid call is included. Earlier failures and closed budgets remain preserved.

Product/tests/workflows remain tested `7bf4c6e`: 2,403 tests / 36 skips locally and all 12 hosted suites, 29 normal CI jobs and docs passed. Six production replays retain zero-call evidence. This delivery adds evidence/docs, not a new hosted code pass.

Phase 22 remains incomplete pending current-source gates, explicit human technical acceptance and accepted closeout. Git stays 312/1,040 incomplete; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged. No merge, ready-state change, release, outreach or Phase 23 is authorized.
'''
with (OUT/'pr-body.md').open('x') as f:f.write(body)
status=f'''## Current v61 thirty-minute profile: source-only decision pending

The approved FAF profile at frozen **`7bf4c6e`** timed out after
**{a['timing']['elapsed_seconds']:.6f} seconds**, retaining **four verified worker identities
and {a['samples']:,} partial samples**. Cleanup passed; no report exists and the
one-use budget is closed. Registration discovery appears in **{low:.2f}–{high:.2f}%**
of each worker's retained samples. These overlapping partial shares do not prove
native speedup, removable-cost fraction, detection or compatibility.

`v61-faf-long-timeout-sampling/optimization-proposal.json` prepares **one unapproved
source-only attempt** to reuse completed TypeScript tool discovery across the
existing workers and coverage. Preserve ordered warnings and source-node identity;
all rule-specific analysis still executes. Full synthetic/engineering verification
is required. No implementation, corpus/profile/retry/comparator, target execution,
paid call, resource change or timeout revision is included in current approval.
The shared 1800-second policy remains in place.

All **335 requirements (89 original + 246 added)** and every earlier failed gate
remain. Product/tests retain verified `7bf4c6e`: **2,403 tests / 36 skips** locally
and in all 12 hosted suites, 29 normal CI jobs and docs passed. Combined coverage
is 89.98%, branch-only 85.86%; six zero-call replays and approved runtime bindings
remain compatible. This continuation adds profile assessment and docs/package checks.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v60 thirty-minute regression: timed out, budget closed'
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
assert len(docs)==16
for name in docs:
    path=ROOT/name
    text=path.read_text()
    assert text.count(heading)==1,name
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in docs}})
print('Preserved 329 prior rows, 335 total; reconciled 16 docs and unapproved source-only proposal.')
