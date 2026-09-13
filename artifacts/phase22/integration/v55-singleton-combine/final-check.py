"""Verify the rejected candidate, exact restoration and docs-only review packet."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent; BASE=OUT.parent; OLD=BASE/'v54-faf-fastpath-sampling'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
checks=['v55-authorization','v55-assessment','v55-owned-cleanup','v55-reconciliation-corrected','v55-final-docs','v55-final-build','v55-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
failed={p.stem:read(p)['exit_code'] for p in BASE.glob('v55-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0}
assert failed=={'v55-identity':1,'v55-reconciliation':1},failed
assert read(OUT/'optimization-budget-closed.json')['remaining']==0
assessment=read(OUT/'assessment.json')
assert assessment['assessment_passed'] and not assessment['candidate_equivalence_passed']
assert not assessment['cases'][1]['environment_equal'] and all(r['full_flow_equal'] for r in assessment['cases'])
assert sha(ROOT/'src/sentinel/static/path_flow.py')==sha(OUT/'baseline-path-flow.py')==assessment['baseline_sha256']
assert sha(OUT/'candidate-path-flow.py')==assessment['candidate_sha256']
assert sha(OUT/'optimization-proposal.json')=='2ff8d58ed4b5f082ffffc6f05fd31ada841dce7cf2bd165347dc627d251f77b9'
proposal=read(OUT/'optimization-proposal.json')
assert proposal['status']=='prepared_not_approved_not_started'
assert proposal['failure_assessment_sha256']==sha(OUT/'assessment.json')
assert not (OUT/'next-authorization.json').exists() and not (BASE/'v56-canonical-unknown').exists()
engineering=read(BASE/'v52-merge-fastpath/local-checks.json')['candidate_engineering_files_sha256']
for name,digest in engineering.items():assert sha(ROOT/name)==sha(Path('/private/tmp/mcp-phase22-frozen-a36f696')/name)==digest,name
oldbinding=read(OLD/'documentation-binding.json')
for name,digest in oldbinding['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/name)==digest,name
prior=read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name,digest in prior.items():assert sha(ROOT/name)==digest,name
audit=read(OUT/'audit.json'); oldaudit=read(OLD/'audit.json')
assert audit['requirements']==oldaudit['requirements'] and len(audit['additional_scope_requirements'])==201
for old,new in zip(oldaudit['additional_scope_requirements'],audit['additional_scope_requirements']):assert old==new or new.get('previous_row')==old
assert not audit['technical_acceptance_received'] and not audit['phase22_complete'] and not audit['next_optimization_approved']
assert read(OUT/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert read(OUT/'owned-work.json')['owned_processes']==[]
assert not subprocess.check_output(['git','diff','a36f696','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md'])
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
save('check-failure-assessment.json',{'failed_checks':failed,'identity':'Synthetic environment difference verified. Initial direct vars(flow) comparison falsely flagged independent helper identities; structural assessment corrects those flags while retaining the environment mismatch. Real-target reachability is not established. Original source/receipt retained; one attempt closed and reverted.','reconciliation':'Initial assertion used an incorrect spelling for the existing historical disposition label. It failed before writing audit/docs. Corrected only that literal, preserved reconcile-first.py and initial failed receipt, then passed with all283old rows retained.','optimization_attempts':1,'remaining':0,'profiles':0,'corpus_observations':0,'paid_calls':0})
save('command-provenance.json',{'wrapper_commands':{name:read(BASE/(name+'.json')) for name in checks+list(failed)},'candidate_patch_sha256':sha(OUT/'candidate.patch'),'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
save('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':proposal['scanner'],'engineering_files_verified':len(engineering),'prior_evidence_files_verified':len(prior),'requirements':290,'protected_user_files':8,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{name:sha(BASE/(name+'.json')) for name in checks},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'closed_failed_optimization_attempts':1,'candidate_reverted':True,'next_optimization_attempts':0,'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Verified290requirements,302restored engineering files,failed attempt retained and closed; next proposal unapproved.')
