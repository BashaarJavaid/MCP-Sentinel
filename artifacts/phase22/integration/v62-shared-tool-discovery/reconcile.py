"""Preserve every prior row and reconcile completed engineering and pending evaluation."""
import copy,hashlib,json,xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent; base=out.parent; root=out.parents[3]; olddir=base/'v61-faf-long-timeout-sampling'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (out/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
local=read(out/'local-checks.json'); quality=read(base/'v62-candidate-quality-audit/packet.json'); freeze=read(out/'freeze.json'); proposal=read(out/'evaluation-proposal.json')
assert local['states']=={'passed':2418,'skipped':36} and len(quality['quality'])==12
assert read(base/'v62-missing-approval.json')['exit_code']==0 and read(out/'frozen-source-validation.json')['new_corpus_observations']==0
assert not (out/'evaluation-authorization.json').exists() and not (base/'v63-shared-discovery-regression').exists()
old=read(olddir/'audit.json'); rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V61-DELIVERY','V61-OPT-DECISION'}:
  row['previous_row']=copy.deepcopy(row)
  row.update(disposition='passed',evidence=[str((olddir/'delivery-verification.json' if row['id']=='V61-DELIVERY' else out/'authorization.json').relative_to(root))],assessment='Exact draft delivery readback retained.' if row['id']=='V61-DELIVERY' else 'User explicitly approved the one source-only discovery-reuse attempt. No corpus, profile or technical acceptance is inferred.')
new=[
 ('AUTH','Bind the exact single source-only discovery-reuse approval','passed',['authorization.json']),
 ('SOURCE','Preserve original registration traversal and restrict changes to completed discovery reuse','passed',['source-proof.json']),
 ('SYNTHETIC','Prove complete discovery, warning, alias, rule-state and serial/parallel report equivalence with one producer and all detectors','passed',['discovery-equivalence.json','source-checkpoint.json']),
 ('ENGINEERING','Pass complete current-source local and hosted engineering, package and strict quality gates','passed',['local-checks.json','../v62-candidate-quality-audit/packet.json','candidate-distributions.json']),
 ('RUNTIME','Bind six identical production request replays and approved runtime/image components with zero paid calls','passed',['compatibility.json','../v62-production-capture-revalidation/packet.json']),
 ('FREEZE','Freeze exact tested source and validate selected source records without executing targets or scans','passed',['freeze.json','frozen-source-validation.json']),
 ('REGRESSION-PREPARATION','Prepare unchanged-source 205-observation regression with original labels, order, support and deadline/cleanup gates','passed',['evaluation-proposal.json','scoring-rubric.json','launcher-binding.json','runner-boundaries.json','../v62-missing-approval.json']),
 ('REGRESSION-DECISION','Obtain separate exact numerical authorization before any current-source regression observation','unresolved',['evaluation-proposal.json']),
 ('FAILURE-RETENTION','Retain all 335 prior rows, source-bound failures, closed budgets and initial helper/check failures','passed',['check-failure-assessment.json']),
 ('DELIVERY','Seal and verify this complete engineering/proposal packet on existing open draft PR37','unresolved',[]),
]
for identity,requirement,disposition,evidence in new:
 rows.append(dict(id='V62-'+identity,requirement=requirement,disposition=disposition,evidence=[str((out/n).resolve().relative_to(root)) for n in evidence],assessment='Engineering evidence binds1948bf9. No current-source corpus/profile observation, native speedup, compatibility gate, accepted limitation or human technical acceptance is inferred.'))
assert len(old['requirements'])==89 and len(rows)==256 and len({r['id'] for r in old['requirements']+rows})==345
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],old['requirements']+rows):assert prior==current or current.get('previous_row')==prior
# Historical status is explicit rather than inherited into a new-source current field.
audit={k:copy.deepcopy(v) for k,v in old.items() if k.startswith('historical_')}
audit['historical_v61_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),source=freeze['scanner']['revision'],scanner_identity=freeze['scanner'],candidate_scanner=freeze['scanner'],requirements=copy.deepcopy(old['requirements']),additional_scope_requirements=rows,dispositions=old['dispositions'],additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((olddir/'audit.json').relative_to(root)),'sha256':sha(olddir/'audit.json')},source_recovery_approved=True,engineering_passed=True,hosted_quality='v62-candidate-quality-audit/packet.json',optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=True,optimization_budget_closed=True,optimization_remaining=0,candidate_retained_in_product=True,current_optimization_approved=True,current_optimization_attempts=1,regression_prepared=True,regression_approved=False,regression_executed=False,current_regression_prepared=True,current_regression_approved=False,current_regression_executed=False,proposed_native_observations=205,current_source_corpus_observations=0,current_source_completed_observations=0,current_source_incomplete_observations=0,valid_current_source_profiles=0,current_diagnostic_prepared=False,current_diagnostic_approved=False,current_diagnostic_executed=False,execution_gate_passed=False,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,corpus_target_executions=0,first_frozen_four_repository_gates_passed=0,first_frozen_observations_unchanged=24,current_timeout_policy_seconds=1800,timeout_policy_retained=True,target_seconds=120,target_is_informational=True,status='Completed discovery reuse at1948bf9 passes synthetic and full local/hosted engineering. Exact205-observation regression prepared, unapproved and unexecuted. All earlier failures remain source-bound; Phase22 incomplete.')
audit['current_budget_interpretation']='One source-only attempt consumed and closed. No native/profile budget is open. Proposed205 observations require separate explicit approval. Every older incomplete attempt and unstarted remainder remains closed at its original source.'
audit['current_source_input_accounting']={'native_regression':{'attempts':0,'complete':0,'incomplete':0,'approved':False,'proposed':205},'sampled_diagnostic':{'attempts':0,'approved':False},'total_attempted_inputs':0}
tests={}
for node in ET.parse(base/'v62-full-suite-junit.xml').getroot().iter('testcase'):
 name=node.attrib['classname'].replace('.','/')+'.py';count=tests.setdefault(name,Counter());count['failed' if node.find('failure') is not None or node.find('error') is not None else 'skipped' if node.find('skipped') is not None else 'passed']+=1
interpretations={}
for row in old['requirements']+old['additional_scope_requirements']:
 files=row.get('source_and_test_files',[])
 interpretations[row['id']]={'requirement':row['requirement'],'historical_disposition':row['disposition'],'prior_row_sha256':hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),'current_source_files':{n:{'sha256':sha(root/n),'changed_from_7bf4c6e':n in read(out/'source-proof.json')['changed_engineering_files']} for n in files if (root/n).is_file()},'current_tests':{n:dict(tests[n]) for n in files if n in tests},'current_interpretation':'All original evidence, source judgments, failed gates, proposed limitations and user deferrals remain exactly source-bound. Current engineering is verified by local-checks and hosted audit; prior corpus results do not establish1948bf9 native completion, detection, negative-path support, compatibility or unseen-source generalization. Current production/runtime reuse is separately bound by compatibility.json. Human acceptance remains unresolved.','previous_interpretation':old.get('current_requirement_interpretations',{}).get(row['id'])}
audit['current_requirement_interpretations']=interpretations
audit['current_evidence']={n:sha(out/n) for n in ['authorization.json','source-proof.json','local-checks.json','compatibility.json','freeze.json','evaluation-proposal.json','runner-boundaries.json','frozen-source-validation.json','check-failure-assessment.json']}
assert audit['additional_scope_dispositions']=={'passed':234,'unresolved':16,'proposed documented limitation awaiting decision':6}
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(olddir/'audit.json'),'retained_prior_rows':335,'total_rows':345,'updated_rows':['V61-DELIVERY','V61-OPT-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
coverage=local['coverage_totals']; combined=coverage['percent_covered']; branch=100*coverage['covered_branches']/coverage['num_branches']
status=f'''## Current v62 shared discovery: engineering passed, regression approval pending

The approved single source-only discovery-reuse attempt is engineering-verified at
**`1948bf9`**, source `{freeze['scanner']['source_sha256']}`.
The original traversal is preserved; completed TypeScript registration discovery is
shared through the existing four-worker IPC and parent coverage. Ordered warnings,
source-node aliases, option effects and all rule-specific analyses remain intact.
Synthetic checks include 125 complete baseline comparisons, complete worker reports,
empty/failed/deadline cases and one producer with every detector still invoked.
No native speedup or 1800-second completion has been established.

Local and all 12 hosted suites pass **2,418 tests / 36 skips**; all **29 normal CI
jobs** and docs pass in **34793663094 / 34793663105**. Combined statement/branch
coverage is **{combined:.2f}%**, branch-only **{branch:.2f}%**. Six complete production
requests replay identically with zero paid calls; approved runtime/image bindings
remain compatible. Initial fixture/import/format check errors retain their corrections.

`v62-shared-tool-discovery/evaluation-proposal.json` prepares **205 exposed observations,
110 inputs and 95 entire ordered pairs**, **unapproved and unexecuted**: 24 four-source,
94 TypeScript and 87 Python. The shared 1800-second input limit, 15-second cleanup,
120-second informational target and 6275-minute outer cap remain unchanged. The outer
cap is a worst-case bound, not a duration estimate. No retry/profile/comparator,
new repository, target execution or paid call is included.

All **345 requirements (89 original + 256 added)** retain every earlier failed gate,
five native timeouts, four valid partial profiles, invalid stale-root preparation,
both singleton failures and six unaccepted historical closure proposals. No old budget
is reopened. **Phase 22 remains incomplete**, pending current-source gates, separate
explicit human technical acceptance and accepted closeout. Git stays **312/1,040
incomplete**, 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and
Phase 24/15 unchanged. No merge, ready-state, release, outreach or Phase 23.

'''
heading='## Current v61 thirty-minute profile: source-only decision pending'
docs=list(read(olddir/'documentation-binding.json')['owning_docs_sha256']);assert len(docs)==16
for n in docs:
 p=root/n;s=p.read_text();assert s.count(heading)==1,n;p.write_text(s.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in docs}})
(out/'status.md').write_text(status)
print('Retained335 prior rows;345 total; reconciled16 owning documents. Evaluation remains unapproved.')
