"""Retain every audit row and reconcile the actual stopped regression."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];oldpath=base/'v66-invalidation-contract'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=read(out/'assessment.json');old=read(oldpath/'audit.json')
assert a['source_assessment_complete_for_retained_outputs'] and a['budget']['closed']
assert read(base/'v67-diagnostic-boundary.json')['exit_code']==0 and read(base/'v67-compatible-reuse-corrected.json')['exit_code']==0
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V66-DELIVERY','V66-REGRESSION-DECISION'}:
  row['previous_row']=copy.deepcopy(row)
  name='delivery-verification.json' if row['id']=='V66-DELIVERY' else 'evaluation-authorization.json'
  row.update(disposition='passed',evidence=[str((oldpath/name).relative_to(root))],assessment='Actual da75570 draft delivery verified.' if name.startswith('delivery') else 'User approved the exact 205-observation proposal. One native timeout and 204 unstarted observations are now closed. This approval is not technical acceptance.')
new=[('AUTH','Bind exact 205-observation approval, frozen scanner, one-use budget and launch preflight','passed',['../v66-invalidation-contract/evaluation-authorization.json','../v66-invalidation-contract/execution-preflight.json','launch.json']),('VALIDATION','Validate actual timeout, absent reports, closed 204 remainder and cleanup','passed',['validation.json','budget-closed.json','owned-work.json']),('ASSESSMENT','Assess all retained outputs and preserve engineering bindings without inventing findings or compatibility','passed',['assessment.json','compatible-reuse.json']),('DIAGNOSTIC-PREPARATION','Prepare one bounded parent-and-worker profile with source identity, timer and missing-approval controls','passed',['diagnostic-proposal.json','sampler-selfcheck/packet.json','parent-sampler-selfcheck/packet.json','../v67-diagnostic-boundary.json']),('DIAGNOSTIC-DECISION','Obtain separate exact approval before a new sampled diagnostic execution','unresolved',['diagnostic-proposal.json']),('REGRESSION-GATE','Complete current-source four-repository and prior-language gates or obtain an explicit applicable disposition of this actual failure','unresolved',['assessment.json']),('DELIVERY','Seal stopped execution, preserve the complete audit and verify delivery of the concrete next decision to the existing draft','unresolved',[])]
for identity,requirement,disposition,evidence in new:
 rows.append({'id':'V67-'+identity,'requirement':requirement,'disposition':disposition,'evidence':[str((out/n).resolve().relative_to(root)) for n in evidence],'assessment':'First FAF input timed out at 4145d35 without a report; 204 unstarted observations closed. No current detection, compatibility or speedup pass. One parent-and-worker profile is prepared, unapproved and unexecuted. Earlier failures and human acceptance remain unresolved.'})
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==287 and len(rows)==294
for before,after in zip(old['additional_scope_requirements'],rows):assert before==after or after.get('previous_row')==before
audit=copy.deepcopy(old)
audit['historical_v66_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((oldpath/'audit.json').relative_to(root)),'sha256':sha(oldpath/'audit.json')},regression_approved=True,regression_executed=True,current_regression_approved=True,current_regression_executed=True,current_source_corpus_observations=1,current_source_completed_observations=0,current_source_incomplete_observations=1,unstarted_closed=204,remaining=0,budget_closed=True,execution_gate_passed=False,current_diagnostic_prepared=True,current_diagnostic_approved=False,current_diagnostic_executed=False,valid_current_source_profiles=0,diagnostic_attempts=0,diagnostic_remaining=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='Approved regression stopped on first FAF input at 4145d35 after 1800.008716 seconds; no report, 204 unstarted closed. One parent-and-worker diagnostic is prepared, unapproved and unexecuted. Current-source gates remain unresolved.')
audit['current_source_input_accounting']={'native_regression':{'attempts':1,'complete':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'budget_closed':True},'sampled_diagnostic':{'attempts':0,'approved':False,'proposed':1},'total_attempted_inputs':1}
audit['current_budget_interpretation']='The approved 205-observation sequence is closed after one native timeout and 204 unstarted observations. A new parent-and-worker sampled input requires separate approval. No previous budget is reopened.'
for row in old['requirements']+old['additional_scope_requirements']:
 entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(row['id'],{}))
 entry.update(requirement=row['requirement'],historical_disposition=row['disposition'],current_execution_interpretation='Engineering at 4145d35 remains verified. First FAF native input timed out without a report; all 204 remaining observations closed. No current-source detection, fixed/control support, compatibility, native speedup or accepted limitation follows. Prior source-bound evidence and judgments remain unchanged.',current_execution_evidence={'assessment_sha256':sha(out/'assessment.json'),'compatibility_sha256':sha(out/'compatible-reuse.json')})
 audit['current_requirement_interpretations'][row['id']]=entry
assert len(audit['current_requirement_interpretations'])==376
assert audit['additional_scope_dispositions']=={'passed':269,'unresolved':19,'proposed documented limitation awaiting decision':6},audit['additional_scope_dispositions']
audit['current_evidence']={n:sha(out/n) for n in ['assessment.json','validation.json','budget-closed.json','diagnostic-proposal.json','compatible-reuse.json','owned-work.json']}
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(oldpath/'audit.json'),'retained_prior_rows':376,'total_rows':383,'updated_rows':['V66-DELIVERY','V66-REGRESSION-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
status=f'''## Current v67 invalidation regression: timed out, budget closed

The approved 205-observation sequence at frozen **`4145d35`** stopped on its first
FAF vulnerable input after **{a['whole_seconds']:.6f} seconds** whole-input time.
**One incomplete, zero reports, 204 unstarted closed, zero remaining.** Cleanup
passed within its separate 15-second allowance. Findings, detection, fixed/control
support and ordered repeats remain unknown. No retry, profile or paid call ran.

`v67-invalidation-regression/diagnostic-proposal.json` prepares **one unapproved,
unexecuted parent-and-worker sampled FAF input**, maximum 1800 seconds plus
15 seconds cleanup. It reuses the existing sampler and worker layout with actual
source identities verified before timers/target access. Synthetic identity,
completion/interruption, timer and missing-approval controls pass. The older
`1948bf9` parent profile cannot establish residual costs after the accumulator
change. No optimization, resource/deadline revision or native speedup is included.

All **383 requirements (89 original + 294 added)** remain, including seven native
timeouts, five valid partial profiles, invalid stale-root preparation, both
singleton failures, the original strict invalidation failure and six unaccepted
historical closure proposals. Product retains tested `4145d35`: **2,419 tests /
36 skips** locally and all 12 hosted suites, 29 normal CI jobs and docs passed.
Combined coverage is 90.08%, branch-only 85.92%; six zero-call production replays
and approved runtime/image bindings remain compatible. This continuation adds
outcome, preparation and docs/package checks, not another hosted code pass.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete, with
728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15
unchanged. No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v66 invalidation contract: engineering passed, regression approval pending'
docs=list(read(oldpath/'documentation-binding.json')['owning_docs_sha256'])
assert len(docs)==16
for name in docs:
 path=root/name;text=path.read_text();assert text.count(heading)==1,name
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in docs}})
(out/'status.md').write_text(status)
print('Preserved 376 prior rows, 383 total; reconciled 16 owning docs. Diagnostic remains unapproved.')
