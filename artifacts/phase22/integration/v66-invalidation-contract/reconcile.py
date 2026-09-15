"""Preserve every prior row and reconcile completed engineering and pending evaluation."""
import copy,hashlib,json,xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent; base=out.parent; root=out.parents[3]; olddir=base/'v65-if-invalidation-accumulator'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (out/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
local=read(out/'local-checks.json'); quality=read(base/'v66-candidate-quality-audit/packet.json'); freeze=read(out/'freeze.json'); proposal=read(out/'evaluation-proposal.json')
assert local['states']=={'passed':2419,'skipped':36} and len(quality['quality'])==12
assert read(base/'v66-missing-approval.json')['exit_code']==0 and read(out/'frozen-source-validation.json')['new_corpus_observations']==0
assert not (out/'evaluation-authorization.json').exists() and not (base/'v67-invalidation-regression').exists()
old=read(olddir/'audit.json'); rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V65-DELIVERY','V65-REVISION-DECISION'}:
  row['previous_row']=copy.deepcopy(row)
  row.update(disposition='passed',evidence=[str((olddir/'delivery-verification.json' if row['id']=='V65-DELIVERY' else out/'authorization.json').relative_to(root))],assessment='Exact draft delivery readback retained.' if row['id']=='V65-DELIVERY' else 'User explicitly approved the prospective private mutation-domain revision and one new source-only attempt. Only the two named injected controls are classified outside that prospective domain; the prior strict failure remains unresolved. No corpus/profile or technical acceptance is inferred.')
new=[
 ('AUTH','Bind the exact prospective contract revision and single source-only approval','passed',['authorization.json']),
 ('CONTRACT','Prove all shipped invalidation writers/readers, aliases, subclasses and entry paths obey the expressly revised private-set domain','passed',['production-domain-proof.json','guard-validation.json','authorization.json']),
 ('SOURCE','Reapply only the exact preserved lazy If accumulator and preserve the inverse baseline proof','passed',['source-proof.json']),
 ('SYNTHETIC','Prove full flow/error/alias state, ordered discovery and complete serial/parallel reports while retaining both exact negative-control deltas','passed',['equivalence.json','production-flow-equivalence.json','production-boundaries.json','discovery-equivalence.json','report-equivalence.json','five-rule-report-equivalence.json']),
 ('ENGINEERING','Pass complete current-source local and hosted engineering, package and strict quality gates','passed',['local-checks.json','../v66-candidate-quality-audit/packet.json','candidate-distributions.json']),
 ('RUNTIME','Bind six identical production request replays and approved runtime/image components with zero paid calls','passed',['compatibility.json','../v66-production-capture-revalidation/packet.json']),
 ('FREEZE','Freeze exact tested source and validate selected source records without executing targets or scans','passed',['freeze.json','frozen-source-validation.json']),
 ('REGRESSION-PREPARATION','Prepare unchanged-source 205-observation regression with original labels, order, support and deadline/cleanup gates','passed',['evaluation-proposal.json','scoring-rubric.json','launcher-binding.json','runner-boundaries.json','../v66-missing-approval.json']),
 ('REGRESSION-DECISION','Obtain separate exact numerical authorization before any current-source regression observation','unresolved',['evaluation-proposal.json']),
 ('FAILURE-RETENTION','Retain all 365 prior rows, source-bound failures, closed budgets and initial helper/check failures','passed',['check-failure-assessment.json']),
 ('DELIVERY','Seal and verify this complete engineering/proposal packet on existing open draft PR37','unresolved',[]),
]
for identity,requirement,disposition,evidence in new:
 rows.append(dict(id='V66-'+identity,requirement=requirement,disposition=disposition,evidence=[str((out/n).resolve().relative_to(root)) for n in evidence],assessment='Engineering evidence binds4145d35. No current-source corpus/profile observation, native speedup, compatibility gate, accepted limitation or human technical acceptance is inferred.'))
assert len(old['requirements'])==89 and len(rows)==287 and len({r['id'] for r in old['requirements']+rows})==376
for prior,current in zip(old['requirements']+old['additional_scope_requirements'],old['requirements']+rows):assert prior==current or current.get('previous_row')==prior
# Historical status is explicit rather than inherited into a new-source current field.
audit={k:copy.deepcopy(v) for k,v in old.items() if k.startswith('historical_')}
audit['historical_v65_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),source=freeze['scanner']['revision'],scanner_identity=freeze['scanner'],candidate_scanner=freeze['scanner'],requirements=copy.deepcopy(old['requirements']),additional_scope_requirements=rows,dispositions=old['dispositions'],additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((olddir/'audit.json').relative_to(root)),'sha256':sha(olddir/'audit.json')},source_recovery_approved=True,engineering_passed=True,hosted_quality='v66-candidate-quality-audit/packet.json',optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=True,optimization_budget_closed=True,optimization_remaining=0,prospective_contract_revision_approved=True,original_strict_failure_remains_unresolved=True,budget_closed=True,candidate_retained_in_product=True,current_optimization_approved=True,current_optimization_attempts=1,regression_prepared=True,regression_approved=False,regression_executed=False,current_regression_prepared=True,current_regression_approved=False,current_regression_executed=False,proposed_native_observations=205,current_source_corpus_observations=0,current_source_completed_observations=0,current_source_incomplete_observations=0,valid_current_source_profiles=0,current_diagnostic_prepared=False,current_diagnostic_approved=False,current_diagnostic_executed=False,execution_gate_passed=False,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,corpus_target_executions=0,first_frozen_four_repository_gates_passed=0,first_frozen_observations_unchanged=24,current_timeout_policy_seconds=1800,timeout_policy_retained=True,target_seconds=120,target_is_informational=True,status='The explicitly revised private invalidation accumulator at4145d35 passes full-state comparisons and local/hosted engineering. Exact205-observation regression prepared, unapproved and unexecuted. All earlier failures remain source-bound; Phase22 incomplete.')
audit['current_budget_interpretation']='One source-only attempt consumed and closed. Only the two exact previously failed injected callbacks are prospectively outside the approved domain; their original strict-equivalence failure remains unresolved. No native/profile budget is open. Proposed205 observations require separate explicit approval. Every older incomplete attempt and unstarted remainder remains closed at its original source.'
audit['current_source_input_accounting']={'native_regression':{'attempts':0,'complete':0,'incomplete':0,'approved':False,'proposed':205},'sampled_diagnostic':{'attempts':0,'approved':False},'total_attempted_inputs':0}
tests={}
for node in ET.parse(base/'v66-full-suite-loopback-access-junit.xml').getroot().iter('testcase'):
 name=node.attrib['classname'].replace('.','/')+'.py';count=tests.setdefault(name,Counter());count['failed' if node.find('failure') is not None or node.find('error') is not None else 'skipped' if node.find('skipped') is not None else 'passed']+=1
interpretations={}
for row in old['requirements']+old['additional_scope_requirements']:
 files=row.get('source_and_test_files',[])
 interpretations[row['id']]={'requirement':row['requirement'],'historical_disposition':row['disposition'],'prior_row_sha256':hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),'current_source_files':{n:{'sha256':sha(root/n),'changed_from_1948bf9':n in read(out/'source-proof.json')['changed_engineering_files']} for n in files if (root/n).is_file()},'current_tests':{n:dict(tests[n]) for n in files if n in tests},'current_interpretation':'All original evidence, source judgments, failed gates, proposed limitations and user deferrals remain exactly source-bound. Current engineering is verified by local-checks and hosted audit; prior corpus results do not establish4145d35 native completion, detection, negative-path support, compatibility or unseen-source generalization. Current production/runtime reuse is separately bound by compatibility.json. Human acceptance remains unresolved.','previous_interpretation':old.get('current_requirement_interpretations',{}).get(row['id'])}
audit['current_requirement_interpretations']=interpretations
audit['current_evidence']={n:sha(out/n) for n in ['authorization.json','source-proof.json','local-checks.json','compatibility.json','freeze.json','evaluation-proposal.json','runner-boundaries.json','frozen-source-validation.json','check-failure-assessment.json']}
assert audit['additional_scope_dispositions']=={'passed':263,'unresolved':18,'proposed documented limitation awaiting decision':6}
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(olddir/'audit.json'),'retained_prior_rows':365,'total_rows':376,'updated_rows':['V65-DELIVERY','V65-REVISION-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
coverage=local['coverage_totals']; combined=coverage['percent_covered']; branch=100*coverage['covered_branches']/coverage['num_branches']
status=f'''## Current v66 invalidation contract: engineering passed, regression approval pending

The explicitly approved private mutation-domain revision and one source-only If
accumulator attempt are verified at **`4145d35`**, source
`{freeze['scanner']['source_sha256']}`. All seven shipped flow classes preserve
monotone private invalidations and independent arm baselines. The candidate reuses
the first completed arm; all guard, statement and conservative union work remains.
The source-bound guard rejects removal/export/reflection mutations. Verification
passes 256 ordinary, 766 complete production-flow and 252 production-boundary
comparisons, 125 ordered discovery comparisons and six complete serial/parallel
results. Only the two explicitly named injected scanner callbacks are outside the
prospective domain; their exact deltas and **v65 strict failure remain retained**.
No other failure is excluded; no native speedup or 1800-second completion is proved.

Local and all 12 hosted suites pass **2,419 tests / 36 skips**; all **29 normal CI
jobs** and docs pass in **34808261686 / 34808261635**. Combined coverage is
**{combined:.2f}%**, branch-only **{branch:.2f}%**. Six complete production requests
replay identically with zero model calls; approved runtime/image bindings remain.
Verification-helper failures and their actual corrections remain preserved.

`v66-invalidation-contract/evaluation-proposal.json` prepares **205 exposed
observations on 110 inputs / 95 ordered pairs**, **unapproved and unexecuted**:
24 four-source, 94 TypeScript and 87 Python. Bounds remain 1800 seconds per input,
15 seconds cleanup and a 6275-minute worst-case outer cap, not an estimate.
No retry/profile/comparator, new repository, target execution or paid call.

All **376 requirements (89 original + 287 added)** retain every prior failed gate,
six native timeouts, five separately bound partial profiles, invalid stale-root
preparation, both singleton failures, the strict accumulator failure and six
unaccepted historical closure proposals. **Phase 22 remains incomplete**, pending
current-source gates, explicit human technical acceptance and accepted closeout.
Git stays 312/1,040 incomplete, 728 deferred; paid benchmark/pilots deferred,
Phase 21 incomplete and Phase 24/15 unchanged. No merge, ready-state, release,
outreach or Phase 23 is authorized.

'''
heading='## Current v65 invalidation attempt: strict-equivalence failure retained'
docs=list(read(olddir/'documentation-binding.json')['owning_docs_sha256']);assert len(docs)==16
for n in docs:
 p=root/n;s=p.read_text();assert s.count(heading)==1,n;p.write_text(s.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in docs}})
(out/'status.md').write_text(status)
print('Retained365 prior rows;376 total; reconciled16 owning documents. Evaluation remains unapproved.')
