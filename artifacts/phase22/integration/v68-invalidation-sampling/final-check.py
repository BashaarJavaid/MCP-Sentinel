"""Verify current profile, recovery, unapproved source proposal and unchanged engineering."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;assets=base/'v66-invalidation-contract';prev=base/'v67-invalidation-regression'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['attribution','owned-work','source-assessment','compatible-reuse','optimization-proposal','recovery-assessment','reconciliation','review-summary','final-docs','final-artifacts','final-build','final-distributions','owned-final']
for n in checks:assert read(base/('v68-'+n+'.json'))['exit_code']==0,n
p=read(out/'optimization-proposal.json');a=read(out/'assessment.json');v=read(out/'validation.json');local=read(assets/'local-checks.json')
for n,d in local['candidate_engineering_files_sha256'].items():assert sha(root/n)==sha(Path(p['frozen_checkout'])/n)==d,n
binding=read(prev/'documentation-binding.json')
for key in ['user_files_sha256','additional_normative_docs_sha256']:
 for n,d in binding[key].items():assert sha(root/n)==d,n
for n,d in read(out/'owning-docs.json')['sha256'].items():assert sha(root/n)==d,n
prior=read(base/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for n,d in prior.items():assert sha(root/n)==d,n
for n,d in p['source_files_sha256'].items():assert sha(root/n)==d,n
assert p['bounds']=={'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0}
assert p['status']=='prepared_not_approved_not_started' and not (base/'v69-ts-literal-key-reuse').exists()
assert a['report_count']==0 and a['samples']==148001 and a['budget_closed'] and a['remaining']==0
assert v['passed'] and v['sample_snapshots']==1 and v['worker_identities']=={} and v['timing']['cleanup_verified']
assert not a['sample_rows'][0]['final_worker_snapshot'] and not a['sample_rows'][0]['signal_and_timer_state_restored']
for n,d in v['raw_sha256'].items():assert sha(out/n)==d,n
for n,d in a['assessment_sha256'].items():assert sha(out/n)==d,n
assert len(read(out/'source-assessment.json')['retained_snapshot_files'])==1
assert read(out/'recovery-assessment.json')['passed']
assert read(prev/'restored-launch-preflight.json')['profile_attempts']==0
assert read(prev/'diagnostic-consumed.json') and read(out/'budget-closed.json')
audit=read(out/'audit.json');old=read(prev/'audit.json');assert audit['requirements']==old['requirements'] and len(audit['additional_scope_requirements'])==302
for before,after in zip(old['additional_scope_requirements'],audit['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert len(audit['current_requirement_interpretations'])==383
for identity in ['V49-DIAGNOSTIC-PREPARATION','V65-EQUIVALENCE','V67-REGRESSION-GATE','V68-OPT-DECISION']:
 assert next(r for r in audit['additional_scope_requirements'] if r['id']==identity)['disposition']=='unresolved',identity
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert read(out/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert not subprocess.check_output(['git','diff','4145d35','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md','docs/architecture.md'])
assert not subprocess.check_output(['git','ls-files','--deleted'])
subprocess.run(['git','diff','--check'],check=True);subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a';assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
commands={n:read(base/('v68-'+n+'.json')) for n in checks}
for n,r in commands.items():
 assert sha(base/('v68-'+n+'.patch'))==r['diff_sha256'];assert sha(base/('v68-'+n+'.untracked.tar.gz'))==r['untracked_source_sha256']
failed={p.stem:read(p)['exit_code'] for p in base.glob('v68-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0};assert not failed,failed
write('check-failure-assessment.json',{'profile_outcome':'One actual approved1800-second sampled timeout, no report,148001periodic parent samples. Forced teardown/return-9; final snapshot and timer restoration unconfirmed. Budget closed; no retry.','failed_wrapper_checks':failed,'preflight_failure':read(prev/'launch-preflight-failure.json'),'recovery_helper_failures':read(out/'recovery-assessment.json')['helper_failures'],'qualification':'Exact original failed unused image-cleanup guard helper and corrected helper both retained; initial failure occurred before mutation. Original v67 compatible-reuse helper failure and all earlier failures remain in their packets. No historical failed artifact was overwritten. Guessed analysis/static path and absent tmp glob checks in current review were read-only lookup errors; actual source and snapshot inventory then verified.','paid_calls':0})
for helper in out.glob('*.py'):ast.parse(helper.read_text(),filename=str(helper))
direct=[{'kind':'initial read-only failed launcher','command':read(prev/'launch-preflight-failure.json')['launch_command'],'exit_code':1,'receipt':'../v67-invalidation-regression/launch-preflight-failure.json','attempt_consumed':False},{'kind':'actual resumed single profile','command':read(prev/'launch-preflight-failure.json')['launch_command'],'exit_code':247,'receipt':'execution.json','attempt_consumed':True}]
for name,receipt in [('authorize-diagnostic.py','diagnostic-preflight.json'),('inventory-restoration.py','worktree-restoration-plan.json'),('restore-worktrees.py','worktree-restoration.json'),('restore-sealed-evidence.py','sealed-evidence-restoration.json'),('cleanup-sentinel-cache.py','docker-cleanup.json'),('cleanup-unused-base-images.py','base-image-cleanup.json'),('verify-restored-launch.py','restored-launch-preflight.json')]:
 direct.append({'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(prev/name)],'exit_code':0,'receipt':'../v67-invalidation-regression/'+receipt,'qualification':'Direct helper execution retained by helper and result receipt; no wrapper/raw full terminal log was captured. Actual Docker subcommands and stdout are in cleanup receipts.'})
write('command-provenance.json',{'wrapper_commands':{p.stem:read(p) for p in base.glob('v68-*.json') if 'exit_code' in read(p)},'direct_commands':direct,'user_document_recovery':'Exact creation text extracted from local session records, hash-verified and exclusively written. Individual provenance receipts retained; raw private session records and original command execution are not part of delivery.','helper_sources_sha256':{str(p.relative_to(root)):sha(p) for p in [*out.glob('*.py'),*prev.glob('*.py')]},'failure_assessment_sha256':sha(out/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'engineering_files_verified':303,'prior_evidence_files_verified':len(prior),'requirements':391,'protected_user_files':9,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(base/('v68-'+n+'.json')) for n in checks},'optimization_proposal_sha256':sha(out/'optimization-proposal.json'),'profiles':1,'profile_samples':148001,'reports':0,'budget_closed':True,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final391-row/source/package/recovery/profile checks pass; source-only optimization remains unapproved.')
