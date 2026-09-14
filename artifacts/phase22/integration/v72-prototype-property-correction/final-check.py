"""Verify current engineering/preparation and all retained failed-source evidence."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];old=base/'v70-uncapped-four-results';initial=base/'v71-four-source-correctness'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,p):
 with (out/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
checks=['v72-local-checks','v72-hosted-audit','v72-freeze','v72-preparation','v72-approval-boundary','v72-reconciliation','v72-review-summary','v72-final-docs','v72-final-artifacts','v72-final-build','v72-final-distributions','v72-owned-final','v72-coverage-temp-retention']
for name in checks:assert read(base/(name+'.json'))['exit_code']==0,name
p=read(out/'evaluation-proposal.json');a=read(out/'audit.json');previous=read(old/'audit.json');local=read(out/'local-checks.json')
assert p['scanner']==a['scanner_identity']==read(out/'freeze.json')['scanner']
assert local['candidate']==p['scanner']['revision']=='cec0322e904bbf63c33cd95796e7289101a93e5d'
assert p['status']=='prospective_exposed_correctness_regression_not_approved'
assert len(p['order'])==24 and len({r['input_id'] for r in p['order']})==12
assert p['bounds']['ordered_repeat_pairs']==12 and p['bounds']['native_and_whole_input_maximum_seconds'] is None
assert p['bounds']['cleanup_maximum_seconds_per_input']==15 and p['bounds']['paid_calls']==0
assert not any((out/n).exists() for n in ['evaluation-authorization.json','execution-consumed.json'])
assert not (base/'v73-corrected-four-results').exists()
for n,d in p['files_sha256'].items():assert sha(root/n)==d,n
for n,d in local['candidate_engineering_files_sha256'].items():assert sha(root/n)==sha(Path(p['frozen_checkout'])/n)==d,n
protected=read(out/'intake.json')['protected_user_files_sha256'];assert len(protected)==9
for n,d in protected.items():assert sha(root/n)==d,n
for n,d in read(out/'owning-docs.json')['sha256'].items():assert sha(root/n)==d,n
for n,d in read(old/'documentation-binding.json')['additional_normative_docs_sha256'].items():assert sha(root/n)==d,n
prior_evidence=read(base/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior_evidence.items():assert sha(root/n)==d,n
v70=read(old/'final-assessment/assessment.json');assert v70['completed']==24 and v70['entire_ordered_pairs_equal']==12 and v70['repository_gates_passed']==2
for n,d in read(old/'raw/packet.json')['files_sha256'].items():assert sha(old/'raw'/n)==d,n
assert a['requirements']==previous['requirements'] and len(a['additional_scope_requirements'])==318
for before,after in zip(previous['additional_scope_requirements'],a['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert len(a['current_requirement_interpretations'])==407
for identity in ['V49-DIAGNOSTIC-PREPARATION','V55-EQUIVALENCE','V56-EQUIVALENCE','V65-EQUIVALENCE','V67-REGRESSION-GATE','V68-OPT-DECISION','V70-FOUR-GATE','V70-PRIOR-LANGUAGES','V72-CURRENT-REGRESSION']:
 assert next(r for r in a['additional_scope_requirements'] if r['id']==identity)['disposition']=='unresolved',identity
for key in ['optimization_approved','optimization_synthetic_verified','optimization_budget_closed','current_optimization_approved','regression_approved','regression_executed','technical_acceptance_received','phase22_complete','acceptance_packet_ready']:assert not a[key],key
assert a['current_source_input_accounting']['total_attempted_inputs']==0 and a['current_timeout_policy_seconds']==1800
pending=base/'v68-invalidation-sampling/optimization-proposal.json';assert sha(pending)=='fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6'
assert read(pending)['status']=='prepared_not_approved_not_started' and not (base/'v69-ts-literal-key-reuse').exists()
assert read(out/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not read(out/'owned-final.json')['owned_processes']
assert not subprocess.check_output(['git','diff',local['candidate'],'--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
assert not subprocess.check_output(['git','ls-files','--deleted'])
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
commands={p.stem:read(p) for prefix in ('v71-','v72-') for p in base.glob(prefix+'*.json') if 'exit_code' in read(p)}
for name,r in commands.items():assert sha(base/(name+'.patch'))==r['diff_sha256'] and sha(base/r['untracked_source_archive'])==r['untracked_source_sha256'],name
failed={name:r['exit_code'] for name,r in commands.items() if r['exit_code']!=0}
assert failed=={'v71-baseline-synthetic':1,'v71-correction-synthetic':1,'v71-prototype-property-control':1,'v71-full-suite':2,'v72-source-assessment':1},failed
write('check-failure-assessment.json',{'failed_wrapper_checks':failed,'source_assessment_sha256':sha(out/'source-assessment.json'),'initial_hosted_ci':'34845266890 cancelled after prototype control failed; docs34845266900passed. No complete initial engineering pass.','current_full_engineering':'cec0322 only; original tests/failures and obsolete unexecuted V71preparation remain preserved.','read_only_and_preparation_errors':'Retired helper restored from verified archive; guessed file paths and case-sensitive process filter failed without mutation. The missing interrupted-run coverage assumption was corrected explicitly. No current-source corpus or paid call.','paid_calls':0})
helpers={str(p.relative_to(root)):sha(p) for folder in (initial,out) for p in folder.glob('*.py')}
for name in helpers:ast.parse((root/name).read_text(),filename=name)
write('command-provenance.json',{'wrapper_commands':commands,'helper_sources_sha256':helpers,'failure_assessment_sha256':sha(out/'check-failure-assessment.json'),'qualification':'Exact wrapper commands/logs/patches/helper archives retained. Initial interrupted local/cancelled hosted engineering is preserved; final current-source complete engineering is separately bound. Prepared freeze/launcher/delivery helpers are not extra corpus observations.','paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'engineering_files_verified':303,'prior_evidence_files_verified':len(prior_evidence),'requirements':407,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{name:sha(base/(name+'.json')) for name in checks},'current_source_observations':0,'proposed_observations':24,'proposal_approved':False,'earlier_language_observations_excluded':181,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final407-row source/engineering/package/preparation checks pass; actual corpus gates and technical acceptance remain pending.')
