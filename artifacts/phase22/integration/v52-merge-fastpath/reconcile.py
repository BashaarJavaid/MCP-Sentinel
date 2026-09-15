"""Preserve all 265 prior rows and reconcile the one approved source-only attempt."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

out=Path(__file__).resolve().parent; base=out.parent; root=Path.cwd(); olddir=base/'v51-faf-bound-sampling'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (out/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
old=read(olddir/'audit.json'); audit=copy.deepcopy(old)
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==176
rows=audit['additional_scope_requirements']
assert read(olddir/'delivery-verification.json')['passed']
for row in rows:
    if row['id'] in {'V51-DELIVERY','V51-OPT-DECISION'}:
        row['previous_row']=copy.deepcopy(row);row['disposition']='passed'
        row['evidence']=[str((olddir/'delivery-verification.json' if row['id']=='V51-DELIVERY' else out/'authorization.json').relative_to(root))]
        row['assessment']='Exact previous draft delivery was verified; user then approved the single source-only fast-path attempt. This is no corpus/profile budget or human technical acceptance.'
new=[
 ('V52-AUTH','Bind the exact single source-only approval and preserve its baseline','passed',['authorization.json','baseline-merge.py']),
 ('V52-SOURCE','Apply only the approved equal-value fast path and verify complete-state equivalence and avoided fallback preparation','passed',['source-recovery-assessment.json','synthetic-validation.json']),
 ('V52-ENGINEERING','Verify current-source local and hosted engineering, packages, zero-call production requests and runtime compatibility','passed',['local-checks.json','../v52-candidate-quality-audit/packet.json','compatibility.json']),
 ('V52-PREPARATION','Freeze the engineering-tested scanner and prepare an exact separately approved native regression','passed',['freeze.json','evaluation-proposal.json','launcher-binding.json','frozen-source-validation.json']),
 ('V52-REGRESSION','Obtain exact approval, execute and source-assess the corrected candidate before claiming performance, detection or compatibility','unresolved',['evaluation-proposal.json']),
 ('V52-DELIVERY','Seal this attempt, retain every prior row and verify delivery to existing draft PR37','unresolved',[]),
]
for identity,requirement,disposition,evidence in new:
    rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((out/n).resolve().relative_to(root)) for n in evidence],'assessment':'The approved source-only fast-path attempt has synthetic and engineering verification only. New205-observation proposal remains unapproved and unexecuted; no historical failure is waived.'})
assert len(rows)==182 and len({r['id'] for r in audit['requirements']+rows})==271
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):
    assert prior==current or current.get('previous_row')==prior
local=read(out/'local-checks.json'); quality=read(base/'v52-candidate-quality/packet.json')
assert quality['engineering_passed'] and local['states']=={'passed':2386,'skipped':36}
p=read(out/'evaluation-proposal.json');assert len(p['order'])==205
assert read(out/'frozen-source-validation.json')['new_corpus_observations']==0
assert not (out/'evaluation-authorization.json').exists() and not (base/'v53-fastpath-regression').exists()
audit['historical_v51_status_fields']={k:v for k,v in old.items() if k not in {'requirements','additional_scope_requirements','current_requirement_interpretations'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),source=p['scanner']['revision'],scanner_identity=p['scanner'],prior_audit={'path':str((olddir/'audit.json').relative_to(root)),'sha256':sha(olddir/'audit.json')},additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),candidate_scanner=p['scanner'],engineering_passed=True,hosted_quality='v52-candidate-quality-audit/packet.json',optimization_prepared=True,optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=True,current_optimization_prepared=True,current_optimization_approved=True,current_optimization_attempts=1,current_regression_prepared=True,current_regression_approved=False,current_regression_executed=False,regression_prepared=True,regression_approved=False,regression_executed=False,proposed_native_observations=205,current_source_corpus_observations=0,current_source_completed_observations=0,current_source_incomplete_observations=0,unstarted_closed=0,remaining=0,budget_closed=True,execution_gate_passed=False,diagnostic_prepared=False,diagnostic_approved=False,diagnostic_executed=False,diagnostic_attempts=0,diagnostic_completed_inputs=0,diagnostic_budget_closed=True,diagnostic_remaining=0,valid_current_source_profiles=0,current_diagnostic_prepared=False,current_diagnostic_approved=False,current_diagnostic_executed=False,new_paid_calls=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='One approved equal-value fast-path reorder implemented at a36f696; 10,944 complete-state synthetic comparisons and 2,386 local/all12-hosted passes with36skips. New205-observation proposal prepared,unapproved,unexecuted. All earlier native/profile failures and original fresh failures remain unchanged; corrected corpus gates and human acceptance remain unresolved.')
audit['current_budget_interpretation']='One source-only optimization consumed/closed; zero approved current-source corpus or profile budget. The205 observations are proposed, not a remaining permission. All earlier measurements remain in their source-bound historical records.'
audit['current_evidence']={n:sha(out/n) for n in ['authorization.json','source-recovery-assessment.json','synthetic-validation.json','local-checks.json','freeze.json','evaluation-proposal.json','launcher-binding.json','frozen-source-validation.json']}
for identity in ['R66','R88']:
    audit['current_requirement_interpretations'][identity]='Original24first-frozen observations and all4failed fresh gates remain at2e0efb2. Native regressions at17b4784 and6e4fd67 each stopped at1incomplete/204unstarted closed. Their partial sampled timeouts, invalid interrupted v50 preparation and valid v51 partial profile retain their actual identities. The approved a36f696 fast path has synthetic/engineering verification only. New205-observation proposal is unapproved; no native speedup, corrected detection, current compatibility or accepted limitation is established.'
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(olddir/'audit.json'),'retained_prior_rows':265,'updated_rows':['V51-DELIVERY','V51-OPT-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
write('optimization-budget-closed.json',{'approved_attempts':1,'consumed_attempts':1,'remaining_attempts':0,'closed':True,'scanner':p['scanner'],'local_and_hosted_engineering_passed':True,'new_corpus_observations':0,'profiles':0,'paid_calls':0,'qualification':'This source-only attempt is complete. The separately prepared205-observation proposal remains unapproved and cannot reuse any older closed budget.'})
cov=local['coverage_totals']; checkout=read(out/'checkout-binding.json')
summary=f'''# Equal-value fast path verified; native regression approval pending

**The single approved source-only attempt is engineering-verified at `a36f696`. Phase 22 remains incomplete. The new 205-observation regression is prepared, unapproved and unexecuted.**

The [authorization](authorization.json) binds `appproved` to proposal SHA `{read(out/'authorization.json')['proposal_sha256']}`. The exact baseline was preserved before editing. [Source assessment](source-recovery-assessment.json) verifies that `TypeScriptPathFlow.merge` now recognizes an eligible equal value present in every branch before record-fallback preparation. Missing/unequal values, guard markers, source-free safety stripping, ordered combination and all metadata retain their conservative behavior. No cache, dependency, traversal pruning, deadline or resource change was introduced.

[10,944 synthetic comparisons](synthetic-validation.json) preserve the result environment, every flow attribute and input dictionaries. Eight shared/distinct-equal cases across one/two/three/eight branches avoid the baseline record-registry lookup; all 13 needed fallback allocations remain. Two added durable tests cover shared and distinct-equal instances, alongside retained missing-first/middle/last and guard controls. The **516 affected tests** pass. These checks establish no native speedup or 300-second completion; eligible-case prevalence remains unmeasured.

Full local and all **12 hosted suites pass 2,386 tests / 36 skips**. Local configured combined statement/branch coverage is **{cov['percent_covered']:.2f}%**; branch-only coverage is **{cov['percent_branches_covered']:.2f}%**. All **29 normal CI jobs** and docs pass in [34767417083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417083) / [34767417081](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34767417081). Hosted merge `{checkout['synthetic_merge']}` has the complete candidate tree `{checkout['tree']}`. Four optional corpus jobs stay skipped; normal historical reproductions retain pinned `8824014`, not the current scanner.

Local/hosted wheel and sdist source members match candidate Git blobs. Ruff/format/strict mypy, lock, schema, notices, offline artifacts, dependency advisory and docs checks pass. The initial formatting failure and corrected pass remain retained. A preparation syntax check initially treated the preserved indented baseline method as a standalone module; compiling its dedented check input passed without changing the baseline or product. Six actual production requests regenerate and checked-replay with unchanged fingerprints and full-request hashes, **zero model calls**. The authorized owned Docker fixture completes 20/20 attempts with 14 findings and cleanup. Nineteen unchanged runtime components and the approved Git image remain bound. Earlier file/worktree restoration and selective Docker cleanup remain preserved; no new cleanup or new Git campaign was needed.

The [new regression proposal](evaluation-proposal.json), SHA-256 `{sha(out/'evaluation-proposal.json')}`, freezes scanner `{p['scanner']['revision']}`, source `{p['scanner']['source_sha256']}`, harness `{p['scanner']['harness_sha256']}`. Its [launcher binding](launcher-binding.json), SHA-256 `{sha(out/'launcher-binding.json')}`, retains the existing supervisor and refuses missing approval before output or budget mutation. All 110 selected records and their full manifests/archives validate at the frozen checkout without scanning.

One serial locked local macOS sequence proposes **205 native observations: 24 four-repository + 94 TypeScript + 87 Python**, on **110 exposed inputs with 95 entire ordered pairs**. FAF and no-bash remain the two TypeScript repositories; Lightning and Engram remain the two Python repositories. The first input is FAF vulnerable. Fifteen Python development records run once. Although this change is TypeScript-only, the earlier `17b4784` recovery changed both languages and neither later native sequence completed even its first input. Both compatibility schedules remain necessary. Original source labels, configurations, prerequisites, narrow qualifiers and complete-report references stay bound; quiet unsupported paths cannot pass. Language subsets are never pooled into a new whole Linux batch.

Bounds remain **120-second target, 300-second native/whole maximum, 15-second cleanup**, one **1,150-minute outer sequence** with 1,149-minute internal stop. Execution, identity, timeout, schema, cleanup or ordered-repeat failure stops and closes all unstarted observations. Detection/negative-support failures remain results under the unchanged collection policy and require source assessment. All 95 whole ordered pairs must agree after only the established 11 volatile exclusions. Assess every four-repository finding/diagnostic/surface and every earlier report delta. **Zero retries, profiles, comparators, target execution, new repositories or paid calls.** No new evaluation approval or launch token exists.

The native `17b4784` and `6e4fd67` attempts remain one incomplete input each at **300.002159** and **300.004111 seconds**, each with 204 unstarted closed. The `17b4784` profile remains incomplete at **300.001970 seconds**, with four partial snapshots/86,659 samples. The invalid v50 attempt reused stale worker source and was interrupted; it has no usable samples or report and no exact whole/cleanup timing. Its agent preparation error remains unresolved in V49-DIAGNOSTIC-PREPARATION. The corrected v51 `6e4fd67` profile remains incomplete at **300.006563 seconds**, with four verified worker identities and **79,307 partial samples**, no final/restored-state snapshot and no report. Overlapping sample shares are not absolute speedup estimates. All budgets remain closed; this candidate rewrites none of these failures.

The original four-source fresh result stays **24 complete observations, 12 equal pairs and all four fresh gates failed at `2e0efb2`**: FAF's actual read unsupported, no-bash one vulnerable hit plus two negative false alerts per batch, Lightning's client get unresolved, Engram's named manifest write unresolved. Later corrections on these exposed sources cannot establish unseen-source success.

The [audit](audit.json) retains every **265 prior row** and adds six, **271 total: 89 original + 182 added**. Original rows remain 84 passed, two user-deferred, two proposed documented limitations and one pending human acceptance. Added rows contain {audit['additional_scope_dispositions']['passed']} passed, six unaccepted historical closure proposals and {audit['additional_scope_dispositions']['unresolved']} unresolved before the separate delivery readback. No failed attempt becomes a historical pass or an accepted limitation. Corrected corpus gates and explicit human technical acceptance remain unresolved.

Memory-keeper's original fresh fixed/control false alerts, DDG's initially unsupported fixed send and erroneous TypeScript manifest label despite actual Python execution, Lighthouse's original misses and all earlier failures remain source-bound. TS94 at `2e0efb2`, Python87 at `8c62567`, and whole 25 development reuse plus 45+45 Linux at `1f3f72f` remain historical passes with the Meta operator erratum. The original held-out result stays 10 complete, 10 unsupported, five incomplete, with zero hits among four completed vulnerable inputs out of ten vulnerable total. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git campaigns remain **312/1,040 incomplete**, 728 deferred. Paid benchmark and pilots stay deferred; Phase 21 incomplete, Phase 24/15 gates unchanged. Historical two paid calls cost $0.071799; this continuation adds zero. No merge, ready-state change, release, outreach or Phase 23 is authorized. Exact regression approval, execution/assessment, explicit human technical acceptance and accepted final closeout remain separate checkpoints.
'''
(out/'summary.md').write_text(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v52-merge-fastpath/'
body=summary
for n in ['authorization.json','source-recovery-assessment.json','synthetic-validation.json','evaluation-proposal.json','launcher-binding.json','audit.json']:body=body.replace('('+n+')','('+url+n+')')
(out/'pr-body.md').write_text(body)
heading='## Current v51 bound profile: source-only decision pending'
status=f'''## Current v52 equal-value fast path: regression approval pending

The one approved source-only merge reorder is engineering-verified at **`a36f696`**.
It checks eligible equal values actually present in every branch before preparing
record fallbacks. **10,944 synthetic comparisons** preserve environment, complete
flow state and inputs; eight intended cases skip the registry lookup and all 13
needed defaults remain. No native speedup or 300-second completion is established.
Full local and all 12 hosted suites pass **2,386 tests / 36 skips**; local combined
statement/branch coverage **{cov['percent_covered']:.2f}%**, branch-only **{cov['percent_branches_covered']:.2f}%**. All 29 normal CI jobs
and docs pass in **34767417083 / 34767417081**, with exact checkout/package bindings.
Six unchanged production requests checked-replay with zero model calls. No new
corpus observation, profile or Git campaign ran.

The **205-observation exposed regression** is prepared, **unapproved and unexecuted**:
24 four-source + 94 TypeScript + 87 Python, 110 inputs and 95 whole ordered pairs.
Bounds: 120-second target, 300-second native/whole maximum, 15-second cleanup, one
1,150-minute serial local sequence. No retries, profiles, comparators, new repository,
target execution or paid calls. See `v52-merge-fastpath/evaluation-proposal.json`
and `launcher-binding.json`. Earlier shared recovery still lacks completed corpus
validation, so both language schedules remain necessary; they are no new whole
Linux batch. Every original label, qualifier and source-support condition remains.

Both earlier native timeouts/204 closed remainders, sampled timeouts, invalid stale
worker preparation and all original fresh failures remain preserved. The corrected
v51 partial profile does not erase the invalid attempt or establish a native pass.
All **271 requirements (89 original + 182 added)** remain; six historical closure
proposals, corrected gates and human technical acceptance are unresolved.
**Phase 22 remains incomplete.** Git stays 312/1,040 incomplete with 728 deferred;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
oldbinding=read(olddir/'documentation-binding.json')
for name in oldbinding['owning_docs_sha256']:
    path=root/name;text=path.read_text();assert text.count(heading)==1,(name,heading)
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in oldbinding['owning_docs_sha256']}})
print('Preserved265prior rows;271total; reconciled16docs; new205 proposal remains unapproved.')
