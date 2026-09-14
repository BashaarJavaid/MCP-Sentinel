"""Retain every historical requirement and expose the new unmeasured candidate."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];prior=base/'v70-uncapped-four-results'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
 with (out/name).open('x') as f:json.dump(data,f,indent=2);f.write('\n')
old=read(prior/'audit.json');local=read(out/'local-checks.json');freeze=read(out/'freeze.json');proposal=read(out/'evaluation-proposal.json')
assert read(prior/'delivery-verification.json')['passed']
assert read(base/'v72-approval-boundary.json')['exit_code']==0
assert local['candidate']==proposal['scanner']['revision']==freeze['scanner']['revision']
assert not (out/'evaluation-authorization.json').exists() and not (out/'execution-consumed.json').exists()
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id']=='V70-DELIVERY':
  row['previous_row']=copy.deepcopy(row)
  row.update(disposition='passed',evidence=[str((prior/'delivery-verification.json').relative_to(root)),str((prior/'delivery-approval-review.json').relative_to(root))],assessment='Actual93fb7a5 delivery to the existing OPEN DRAFT PR37 is verified. Initial automatic review rejection was resolved using the explicit protected user-prompt authority for this exact destination/payload; the unchanged helper then passed. No human technical acceptance was received.')
new=[
 ('V71-PROTOTYPE-FAILURE','Retain the failing prototype-property control and source-established special-assignment bypass without claiming a corpus result','passed',[base/'v71-prototype-property-control.json',out/'source-assessment.json']),
 ('V71-INITIAL-ENGINEERING','Preserve interrupted initial local engineering and cancelled hosted CI; require new complete engineering on corrected source','passed',[base/'v71-full-suite.json',base/'v71-candidate-quality/packet.json',out/'source-assessment.json']),
 ('V72-SOURCE','Complete ordinary approved-contract constructor parameter-property and initial URL guard correctness recovery','passed',[out/'intake.json',out/'source-assessment.json',out/'candidate-commit.json']),
 ('V72-SYNTHETIC','Preserve actual first failures and prove the corrected source with receiver/default/guard/identity/ordered-state/worker controls','passed',[out/'source-assessment.json',base/'v72-focused.json']),
 ('V72-ENGINEERING','Complete exact-candidate full local and hosted engineering, coverage, packages, zero-call production requests and runtime bindings','passed',[out/'local-checks.json',base/'v72-candidate-quality-audit/packet.json',out/'checkout-binding.json',out/'compatibility.json']),
 ('V72-PREPARATION','Freeze tested source and bind an unapproved24-observation corrected four-repository proposal with unchanged input/rubric and tested approval/cleanup boundaries','passed',[out/'freeze.json',out/'evaluation-proposal.json',out/'launcher-binding.json',out/'boundary-checks.json',out/'synthetic-equivalence.json',base/'v72-approval-boundary.json']),
 ('V72-CURRENT-REGRESSION','Obtain exact new approval and establish actual corrected-source four-repository support/discrimination and affected earlier-language compatibility','unresolved',[out/'evaluation-proposal.json',prior/'final-assessment/assessment.json']),
 ('V72-DELIVERY','Preserve all requirements and failures, seal candidate evidence and verify current existing-draft delivery','unresolved',[]),
]
for identity,requirement,disposition,paths in new:
 rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str(p.relative_to(root)) for p in paths],'assessment':'Ordinary correctness atcec0322 passes scanner-owned and full engineering checks. No current-source corpus observation/profile exists. A new24-observation uncapped four-repository-first proposal is unapproved;181earlier-language observations remain outside it. Original fresh failures, prior exposed results, seven native timeouts, profiles, strict-equivalence failures and six unaccepted historical closure proposals retain their actual sources. No speedup, accepted limitation or technical acceptance is inferred.'})
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==310 and len(rows)==318
for before,after in zip(old['additional_scope_requirements'],rows):assert before==after or after.get('previous_row')==before
p=copy.deepcopy(old)
p['historical_v70_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements','current_requirement_interpretations'} and not k.startswith('historical_')}
p.update(recorded_at=datetime.now(timezone.utc).isoformat(),source=local['candidate'],scanner_identity=freeze['scanner'],candidate_scanner=freeze['scanner'],additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((prior/'audit.json').relative_to(root)),'sha256':sha(prior/'audit.json')},engineering_passed=True,hosted_quality='v72-candidate-quality-audit/packet.json',source_recovery_approved=True,prospective_contract_revision_approved=False,regression_prepared=True,regression_approved=False,regression_executed=False,current_regression_prepared=True,current_regression_approved=False,current_regression_executed=False,proposed_native_observations=24,current_source_corpus_observations=0,current_source_completed_observations=0,current_source_incomplete_observations=0,valid_current_source_profiles=0,current_diagnostic_prepared=False,current_diagnostic_approved=False,current_diagnostic_executed=False,diagnostic_attempts=0,diagnostic_remaining=0,execution_gate_passed=False,current_four_repository_gate_passed=False,current_four_repository_gates_passed=0,current_earlier_language_compatibility_established=False,budget_closed=False,unstarted_closed=0,remaining=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,status='Ordinary constructor parameter-property and initial URL guard correctness atcec0322 passes engineering. All current-source corpus gates remain unmeasured. New24-observation uncapped four-repository-first proposal is unapproved;181prior-language observations remain excluded. Phase22incomplete pending actual gates, separate explicit human acceptance and accepted closeout.')
p['current_budget_interpretation']='No measurement budget opened at correctedcec0322:0attempts and0authorizedremaining. Prepared24-observation proposal is unapproved/unexecuted. V70and every previous budget remain closed and source-bound. Normal shared1800-second deadline unchanged; the proposed uncapped policy needs new approval. V68performance optimization stays unapproved/unimplemented.'
p['current_source_input_accounting']={'total_attempted_inputs':0,'native_attempts_total':0,'sampled_attempts_total':0,'authorized_remaining':0,'proposal_observations':24,'proposal_approved':False,'qualification':'No current-source input or profile. Historical26inputs at4145d35 remain in historical_v70_status_fields without any overwrite or pooling.'}
p['experimental_timeout_policy']={**old['experimental_timeout_policy'],'proposal_sha256':sha(out/'evaluation-proposal.json'),'approved':False,'executed':False}
p['current_optimization_prepared']=False
p['retained_unapproved_optimization']={'source':'4145d3559c5300a5003ca8e3368c8da49fb51f91','proposal_sha256':'fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6','status':'Original V68proposal remains unapproved/unimplemented and source-bound; no new candidate-bound performance proposal was prepared.'}
p['current_contract_interpretation']='No new private-state or acceptance-contract revision. The prospective_contract_revision_approved false field refers to this ordinary correctness continuation; the explicitly approved V66 revision remains applicable historical product behavior and is retained in historical_v70_status_fields.'
for row in p['requirements']+rows:
 entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(row['id'],{}))
 entry.update(requirement=row['requirement'],historical_disposition=row['disposition'],current_execution_interpretation='Currentcec0322 correction passes full engineering but has zero corpus observations. Historical original/exposed/profile/equivalence outcomes remain source-bound; no old pass is current-source detection or compatibility proof. Separate exact evaluation approval and human technical acceptance remain required.',current_execution_evidence={'source_assessment_sha256':sha(out/'source-assessment.json'),'local_engineering_sha256':sha(out/'local-checks.json'),'proposal_sha256':sha(out/'evaluation-proposal.json')})
 p['current_requirement_interpretations'][row['id']]=entry
assert len(p['current_requirement_interpretations'])==407
assert p['additional_scope_dispositions']=={'passed':290,'unresolved':22,'proposed documented limitation awaiting decision':6},p['additional_scope_dispositions']
p['current_evidence']={str(path.relative_to(out)):sha(path) for path in [out/'source-assessment.json',out/'local-checks.json',out/'freeze.json',out/'evaluation-proposal.json',out/'compatibility.json']}
write('audit.json',p)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(prior/'audit.json'),'retained_prior_rows':399,'total_rows':407,'updated_rows':['V70-DELIVERY'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
cov=local['coverage_totals']
status=f'''## Current v72 correctness recovery: engineering passed, regression pending

Ordinary approved-contract recovery is verified at **`cec0322`**. Supported
TypeScript constructor parameter properties retain actual argument/default and
receiver identity; Python initial URL guard qualification survives only proved
trailing-slash/path-suffix derivation. Wrong/escaped receivers, ambiguous field
initialization, hostname fallbacks, formatting and authority changes remain
conservative, including rejection of prototype-mutating `__proto__` properties.
The first candidate `42d6c7c` failed that additional control; its local suite was
interrupted after 1,408 passes/36 skips and CI 34845266890 cancelled. Initial five
synthetic failures, subset-coverage configuration and helper-normalization failure
also remain retained with their corrections; no partial suite becomes a pass.

Local and all 12 hosted suites pass **2,450 tests / 36 skips**; all 29 normal CI
jobs and docs pass in **34846514312 / 34846514328**. Combined coverage is
**{cov['percent_covered']:.2f}%**, branch-only **{cov['percent_branches_covered']:.2f}%**.
Exact checkout/package bindings, six unchanged zero-call production requests and
19 approved runtime component bindings pass. No speedup is established.

The new **24-observation corrected four-repository proposal is unapproved and
unexecuted**: 12 inputs twice, 12 entire ordered pairs, 18 non-FAF observations
then six FAF. It proposes the previously tested experiment-only uncapped policy,
with finite 15-second cleanup and unchanged normal **1,800-second** deadline.
All 10 complete synthetic policy comparisons and cancellation/approval boundaries
pass. **181 earlier Python/TypeScript observations remain outside this proposal.**

The completed V70 experiment at `4145d35` remains unchanged: 24/24 complete,
12/12 ordered pairs equal, FAF 2,212.22–2,341.48 seconds; no-bash/Engram narrow
passes, FAF detection/support and Lightning negative-qualification failures.
Those results do not establish current-source gates. All **407 requirements
(89 original + 318 added)**, original fresh failures and six unaccepted historical
closure proposals remain. V68 performance optimization stays unapproved and
unimplemented. No new corpus/profile/comparator/target execution or paid call.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete with
728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15
unchanged. No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading='## Current v70 uncapped experiment: complete run, two failed gates'
docs=list(read(prior/'documentation-binding.json')['owning_docs_sha256']);assert len(docs)==16
for name in docs:
 path=root/name;text=path.read_text();assert text.count(heading)==1,name
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{name:sha(root/name) for name in docs}})
with (out/'status.md').open('x') as f:f.write(status)
print('Preserved399 prior rows;407 total. Current-source evaluation and human acceptance remain unresolved.')
