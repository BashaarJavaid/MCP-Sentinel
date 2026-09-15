"""Verify failed-attempt retention, exact restoration and the unapproved new contract."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v64-shared-discovery-sampling';ASSETS=BASE/'v62-shared-tool-discovery'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['authorization','owned-initial','implementation','equivalence','equivalence-corrected','restoration','assessment-proposal','compatible-reuse','reconciliation','review-summary','compatibility-clarification','final-docs','final-artifacts','final-build','final-distributions','owned-final']
commands={n:read(BASE/('v65-'+n+'.json')) for n in checks}
for n,r in commands.items():
 assert r['exit_code']==(1 if n in {'equivalence','equivalence-corrected'} else 0),n
 assert sha(BASE/('v65-'+n+'.patch'))==r['diff_sha256'];assert sha(BASE/('v65-'+n+'.untracked.tar.gz'))==r['untracked_source_sha256']
a=read(OUT/'assessment.json');v=read(OUT/'equivalence.json');r=read(OUT/'restoration.json');p=read(OUT/'optimization-proposal.json');old=read(OLD/'audit.json');audit=read(OUT/'audit.json')
assert r['restored'] and r['remaining']==0 and r['budget_closed'] and not v['passed'] and v['ordinary_comparisons']==256
assert [c['control'] for c in v['controls'] if not c['equivalent']]==['alias','shrink']
assert sha(OUT/'candidate-typescript-path-flow.py')==v['candidate_sha256'] and sha(OUT/'baseline/src/sentinel/static/typescript_path_flow.py')==v['baseline_sha256']
for n,d in read(ASSETS/'local-checks.json')['candidate_engineering_files_sha256'].items():assert sha(ROOT/n)==sha(Path(p['frozen_checkout'])/n)==d,n
binding=read(OLD/'documentation-binding.json')
for field in ['user_files_sha256','additional_normative_docs_sha256']:
 for n,d in binding[field].items():assert sha(ROOT/n)==d,n
for n,d in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/n)==d,n
for n,d in p['source_files_sha256'].items():assert sha(ROOT/n)==d,n
prior=read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior.items():assert sha(ROOT/n)==d,n
assert p['status']=='prepared_not_approved_not_started' and not (BASE/'v66-invalidation-contract').exists()
assert p['bounds']=={'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0}
assert audit['requirements']==old['requirements'] and len(audit['additional_scope_requirements'])==276 and len(audit['current_requirement_interpretations'])==358
for before,after in zip(old['additional_scope_requirements'],audit['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert next(x for x in audit['additional_scope_requirements'] if x['id']=='V65-EQUIVALENCE')['disposition']=='unresolved'
assert not audit['prospective_contract_revision_approved'] and not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not subprocess.check_output(['git','diff','1948bf9','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
subprocess.run(['git','diff','--check'],check=True);subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
failed={f.stem:read(f)['exit_code'] for f in BASE.glob('v65-*.json') if 'exit_code' in read(f) and read(f)['exit_code']!=0};assert failed=={'v65-equivalence':1,'v65-equivalence-corrected':1},failed
write('check-failure-assessment.json',{'failed_wrapper_checks':failed,'initial_helper_failure':'None synthetic deadline caused TypeError before comparisons. Finite synthetic deadline correction retained in the corrected wrapper helper archive.','actual_prerequisite_failure':'Corrected check completes256 ordinary comparisons and finds captured-arm alias and shrinking-arm deltas; error/interruption controls agree. Strict approved prerequisite fails, one attempt closes, exact tested source restored. No real-target reachability established.','preparation_failure':'Original proposal combined unconditional adversarial equivalence with an adoption algorithm requiring no exported alias/shrinking. An explicit prospective contract revision is prepared, not accepted.','prose_correction':'Initial compatibility text incorrectly said no changes during the attempt. Exact candidate/restore evidence and initial receipt/audit/summary are preserved; corrected prose and302byte recheck are explicit.','paid_calls':0})
for f in OUT.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
write('command-provenance.json',{'wrapper_commands':commands,'helper_sources_sha256':{str(f.relative_to(ROOT)):sha(f) for f in OUT.glob('*.py')},'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':a['scanner'],'engineering_files_verified':302,'prior_evidence_files_verified':len(prior),'requirements':365,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(BASE/('v65-'+n+'.json')) for n in checks},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'failed_attempts':1,'remaining':0,'budget_closed':True,'exact_tested_source_restored':True,'new_corpus_observations':0,'new_profiles':0,'paid_calls':0,'prospective_contract_revision_approved':False,'technical_acceptance_received':False,'phase22_complete':False})
print('365-row failure/restoration/source/package checks pass; explicit revised contract remains unapproved.')
