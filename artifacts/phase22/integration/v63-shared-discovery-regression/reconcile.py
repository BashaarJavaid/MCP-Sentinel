"""Preserve every requirement and reconcile the stopped regression and pending diagnostic."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];oldpath=base/'v62-shared-tool-discovery';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=read(out/'assessment.json');old=read(oldpath/'audit.json');p=read(out/'diagnostic-proposal.json');assert a['source_assessment_complete_for_retained_outputs'] and a['budget']['closed']
assert read(base/'v63-diagnostic-boundary.json')['exit_code']==0 and read(base/'v63-compatible-reuse.json')['exit_code']==0
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V62-DELIVERY','V62-REGRESSION-DECISION'}:
  row['previous_row']=copy.deepcopy(row);row.update(disposition='passed',evidence=[str((oldpath/('delivery-verification.json' if row['id']=='V62-DELIVERY' else 'evaluation-authorization.json')).relative_to(root))],assessment='Actual c7b20a3 draft delivery verified.' if row['id']=='V62-DELIVERY' else 'User explicitly approved the exact205-observation proposal. Its first-input timeout and closed remainder remain failures; no technical acceptance inferred.')
new=[('AUTH','Bind exact205-observation approval, frozen source, one-use budget and launch preflight','passed',['../v62-shared-tool-discovery/evaluation-authorization.json','../v62-shared-tool-discovery/execution-preflight.json','launch.json']),('VALIDATION','Validate actual timeout, zero reports, closed204remainder and cleanup','passed',['validation.json','budget-closed.json','owned-work.json']),('ASSESSMENT','Assess all retained outputs without inventing findings, costs or compatibility','passed',['assessment.json','compatible-reuse.json']),('DIAGNOSTIC-PREPARATION','Prepare a single bounded parent-and-worker profile with source identity, timer and missing-approval checks','passed',['diagnostic-proposal.json','sampler-selfcheck/packet.json','parent-sampler-selfcheck/packet.json','../v63-diagnostic-boundary.json']),('DIAGNOSTIC-DECISION','Obtain separate exact approval before any parent-and-worker diagnostic execution','unresolved',['diagnostic-proposal.json']),('REGRESSION-GATE','Complete current-source four-repository and prior-language gates or obtain an explicit applicable disposition of this actual failure','unresolved',['assessment.json']),('DELIVERY','Seal stopped execution, preserve complete audit and verify the concrete next decision on the existing draft','unresolved',[])]
for identity,requirement,disposition,evidence in new:rows.append({'id':'V63-'+identity,'requirement':requirement,'disposition':disposition,'evidence':[str((out/n).resolve().relative_to(root)) for n in evidence],'assessment':'One1800-second native timeout at1948bf9; no report,204unstarted closed,zero remaining. No current detection/compatibility or speedup pass. One parent-and-worker profile is prepared,unapproved and unexecuted. All prior failures and human acceptance remain unresolved.'})
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==256 and len(rows)==263
for before,after in zip(old['requirements']+old['additional_scope_requirements'],old['requirements']+rows):assert before==after or after.get('previous_row')==before
audit=copy.deepcopy(old);audit['historical_v62_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((oldpath/'audit.json').relative_to(root)),'sha256':sha(oldpath/'audit.json')},regression_approved=True,regression_executed=True,current_regression_approved=True,current_regression_executed=True,current_source_corpus_observations=1,current_source_completed_observations=0,current_source_incomplete_observations=1,unstarted_closed=204,remaining=0,budget_closed=True,execution_gate_passed=False,current_diagnostic_prepared=True,current_diagnostic_approved=False,current_diagnostic_executed=False,valid_current_source_profiles=0,diagnostic_attempts=0,diagnostic_remaining=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='Approved205-observation regression stopped on first FAF input at1948bf9 after1800.010893seconds; no report,204unstarted closed. Parent-and-worker diagnostic prepared,unapproved and unexecuted; no current-source gate or speedup pass.')
audit['current_source_input_accounting']={'native_regression':{'attempts':1,'complete':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'budget_closed':True},'sampled_diagnostic':{'attempts':0,'approved':False,'proposed':1},'total_attempted_inputs':1}
audit['current_budget_interpretation']='The approved205-observation sequence is closed after one native timeout and204unstarted observations. One new parent-and-worker sampled input requires separate approval. No previous budget is reopened.'
for row in old['requirements']+old['additional_scope_requirements']:
 entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(row['id'],{}));entry.update(requirement=row['requirement'],historical_disposition=row['disposition'],current_execution_interpretation='Current1948bf9 engineering remains verified. The first FAF native input timed out without a report; all204remaining observations are closed. No current-source detection, fixed/control support, compatibility, native speedup or accepted limitation follows. Original source-bound evidence and judgments remain unchanged.',current_execution_evidence={'assessment_sha256':sha(out/'assessment.json'),'compatibility_sha256':sha(out/'compatible-reuse.json')});audit['current_requirement_interpretations'][row['id']]=entry
assert len(audit['current_requirement_interpretations'])==345
assert audit['additional_scope_dispositions']=={'passed':240,'unresolved':17,'proposed documented limitation awaiting decision':6}
audit['current_evidence']={n:sha(out/n) for n in ['assessment.json','validation.json','budget-closed.json','diagnostic-proposal.json','compatible-reuse.json','owned-work.json']}
write('audit.json',audit);write('prior-row-preservation.json',{'prior_audit_sha256':sha(oldpath/'audit.json'),'retained_prior_rows':345,'total_rows':352,'updated_rows':['V62-DELIVERY','V62-REGRESSION-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
status=f'''## Current v63 shared-discovery regression: timed out, budget closed

The approved205-observation sequence at frozen **`1948bf9`** stopped on its first
FAF vulnerable input after **{a['whole_seconds']:.6f} seconds** whole-input time.
**One incomplete,zero reports,204unstarted closed,zero remaining.** Cleanup passed
in its separate15-second allowance. Detection,findings,fixed/control support and
ordered repeats remain unknown. No retry,profile,target execution or paid call ran.

`v63-shared-discovery-regression/diagnostic-proposal.json` prepares **one unapproved,
unexecuted parent-and-worker sampled FAF input**, maximum1800seconds plus15seconds
cleanup. Completed discovery now runs in the parent before worker dispatch; old
worker-only samples cannot establish current costs. Reuse the same CPU-timer sampler
in the parent and existing workers,with actual source identities verified before
timers/target access. Six-vector,stale-root,parent completion/interruption and
missing-approval controls pass. Sampling overhead and incomplete intervals remain
explicit; no optimization,resource/deadline change or speedup claim is included.

All **352 requirements (89original+263added)** remain,including six native timeouts,
four valid partial profiles,invalid stale-root preparation,both singleton failures
and six unaccepted historical closure proposals. Product retains tested1948bf9:
**2,418tests/36skips** locally and all12hosted suites,29normal CI jobs and docs passed;
combined coverage90.08%,branch-only85.92%. Six zero-call production replays and
approved runtime/image bindings remain compatible; this adds outcome/preparation
and final docs/package checks,not another hosted code pass.

**Phase22 remains incomplete**,pending actual current-source gates,explicit human
technical acceptance and accepted closeout. Git stays312/1,040incomplete,728deferred;
paid benchmark/pilots deferred,Phase21 incomplete,Phase24/15 unchanged. No merge,
ready-state,release,outreach or Phase23 is authorized.

'''
# Use ordinary spacing in user-facing status prose.
import re
status=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',status)
status=status.replace('Phase 22','Phase 22').replace(',',', ')
# Keep source hashes and version/file identifiers intact by restoring the fixed heading/path.
status=status.replace('v 63','v63').replace('`1948 bf 9`','`1948bf9`').replace('tested1948 bf 9','tested `1948bf9`').replace('tested 1948 bf 9','tested `1948bf9`')
status=status.replace('1, 040','1,040').replace('2, 418','2,418')
heading='## Current v62 shared discovery: engineering passed, regression approval pending';docs=list(read(oldpath/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
 path=root/name;text=path.read_text();assert text.count(heading)==1,name;path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in docs}});(out/'status.md').write_text(status)
print('Preserved345 prior rows,352total; reconciled16owning docs. Diagnostic remains unapproved.')
