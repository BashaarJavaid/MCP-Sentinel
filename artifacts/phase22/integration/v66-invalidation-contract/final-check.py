"""Verify final review package, all preserved evidence and exact engineering bindings."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):
 with (out/name).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['local-checks','hosted-audit','freeze','proposal-preparation','frozen-source-validation','launcher-binding','missing-approval','reconciliation','review-summary','final-docs','final-artifacts','final-build','final-distributions','owned-final','assessment','coverage-temp-retention']
for n in checks:assert read(base/('v66-'+n+'.json'))['exit_code']==0,n
local=read(out/'local-checks.json');freeze=read(out/'freeze.json');fixed=Path(freeze['frozen_checkout'])
for n,d in local['candidate_engineering_files_sha256'].items():
 if n!='README.md':assert sha(root/n)==sha(fixed/n)==d,n
assert not subprocess.check_output(['git','diff','4145d35','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
for n,d in read(out/'authorization.json')['user_files_sha256'].items():assert sha(root/n)==d,n
for n,d in read(out/'owning-docs.json')['sha256'].items():assert sha(root/n)==d,n
prior=read(base/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior.items():assert sha(root/n)==d,n
# Retain all current prior-row evidence, beyond the original recovery map.
old=read(base/'v65-if-invalidation-accumulator/audit.json'); paths=set()
for row in old['requirements']+old['additional_scope_requirements']:
 for n in row.get('evidence',[]):
  if isinstance(n,str):
   p=root/n if (root/n).is_file() else base/n
   assert p.is_file(),n;paths.add(p)
proposal=read(out/'evaluation-proposal.json')
for n,d in proposal['files_sha256'].items():assert sha(root/n)==d,n
assert proposal['scanner']==freeze['scanner'] and len(proposal['order'])==205
assert not (out/'evaluation-authorization.json').exists() and not (out/'execution-consumed.json').exists() and not (base/'v67-invalidation-regression').exists()
a=read(out/'audit.json');assert a['requirements']==old['requirements'] and len(a['additional_scope_requirements'])==287
for p,c in zip(old['additional_scope_requirements'],a['additional_scope_requirements']):assert p==c or c.get('previous_row')==p
assert len(a['current_requirement_interpretations'])==365
assert next(r for r in a['additional_scope_requirements'] if r['id']=='V49-DIAGNOSTIC-PREPARATION')['disposition']=='unresolved'
assert next(r for r in a['additional_scope_requirements'] if r['id']=='V65-EQUIVALENCE')['disposition']=='unresolved'
assert a['prospective_contract_revision_approved'] and read(out/'optimization-budget-closed.json')['closed']
assert not a['technical_acceptance_received'] and not a['phase22_complete'] and a['current_source_corpus_observations']==0
assert read(out/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
commands={}
for p in sorted(base.glob('v66-*.json')):
 row=read(p)
 if 'exit_code' not in row:continue
 assert sha(p.with_suffix('.patch'))==row['diff_sha256']
 assert sha(p.with_suffix('.untracked.tar.gz'))==row['untracked_source_sha256']
 commands[p.stem]=row
failed={n:r['exit_code'] for n,r in commands.items() if r['exit_code']!=0}
assert failed==read(out/'check-failure-assessment.json')['failed_wrapper_checks'],failed
for helper in out.glob('*.py'):ast.parse(helper.read_text(),filename=str(helper))
write('command-provenance.json',{'wrapper_commands':commands,'helper_sources_sha256':{str(p.relative_to(root)):sha(p) for p in out.glob('*.py')},'candidate_delivery_sha256':sha(out/'candidate-delivery.json'),'quality_collector_sha256':sha(out/'retain-candidate-quality.py'),'quality_packet_sha256':sha(base/'v66-candidate-quality/packet.json'),'failure_assessment_sha256':sha(out/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':freeze['scanner'],'engineering_files_verified':len(local['candidate_engineering_files_sha256']),'prior_evidence_files_verified':len(prior),'prior_row_evidence_paths_present':len(paths),'requirements':376,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(base/('v66-'+n+'.json')) for n in checks},'evaluation_proposal_sha256':sha(out/'evaluation-proposal.json'),'owned_initial_qualification_correction':'The retained initial ownership receipt inherits a validation.json pointer. The actual source-only attempt accounting is optimization-consumed.json and optimization-budget-closed.json; the raw initial receipt is preserved.', 'optimization_attempts':1,'optimization_budget_closed':True,'current_source_corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final checks pass:376requirements, exact hosted product, zero new corpus/profile/paid calls; evaluation unapproved.')
