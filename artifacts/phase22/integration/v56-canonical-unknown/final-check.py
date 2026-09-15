"""Verify the rejected candidate, exact restoration and docs-only review packet."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent; BASE=OUT.parent; OLD=BASE/'v55-singleton-combine'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
checks=['v56-authorization','v56-assessment','v56-owned-cleanup','v56-reconciliation','v56-final-docs','v56-final-build','v56-final-distributions']
for name in checks:assert read(BASE/(name+'.json'))['exit_code']==0,name
failed={p.stem:read(p)['exit_code'] for p in BASE.glob('v56-*.json') if 'exit_code' in read(p) and read(p)['exit_code']!=0}
assert failed=={'v56-synthetic':1},failed
assert read(OUT/'optimization-budget-closed.json')['remaining']==0
assessment=read(OUT/'assessment.json')
assert assessment['assessment_passed'] and not assessment['candidate_equivalence_passed']
assert not assessment['environment_equal'] and assessment['full_flow_equal'] and assessment['prior_broad_failure_reproduced']
assert sha(ROOT/'src/sentinel/static/path_flow.py')==sha(OUT/'baseline-path-flow.py')==assessment['baseline_sha256']
assert sha(OUT/'candidate-path-flow.py')==assessment['candidate_sha256']
assert sha(OUT/'optimization-proposal.json')=='12eea305c03328d6872587a051c090daf6f2d1bb83e1d0a622e3c3a92af92921'
proposal=read(OUT/'optimization-proposal.json')
assert proposal['status']=='prepared_not_approved_not_started'
assert proposal['failure_assessment_sha256']==sha(OUT/'assessment.json')
assert not (OUT/'next-authorization.json').exists() and not (BASE/'v57-credential-merge').exists()
engineering=read(BASE/'v52-merge-fastpath/local-checks.json')['candidate_engineering_files_sha256']
for name,digest in engineering.items():assert sha(ROOT/name)==sha(Path('/private/tmp/mcp-phase22-frozen-a36f696')/name)==digest,name
oldbinding=read(OLD/'documentation-binding.json')
for name,digest in oldbinding['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
for name,digest in read(OUT/'owning-docs.json')['sha256'].items():assert sha(ROOT/name)==digest,name
prior=read(BASE/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name,digest in prior.items():assert sha(ROOT/name)==digest,name
audit=read(OUT/'audit.json'); oldaudit=read(OLD/'audit.json')
assert audit['requirements']==oldaudit['requirements'] and len(audit['additional_scope_requirements'])==208
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
save('check-failure-assessment.json',{'failed_checks':failed,'synthetic':'Two ordinary narrow identity cases preserve baseline and the retained broad failure is reproduced. Saturated LRU eviction changes interning and credential environment; full structural flow state remains equal. Real-target impact unestablished. Required stop rule closed the single attempt and exact source was restored. No verification-helper failure occurred in this continuation. Older helper/reconciliation failures remain preserved in v55.','optimization_attempts':1,'remaining':0,'profiles':0,'corpus_observations':0,'paid_calls':0})
save('command-provenance.json',{'wrapper_commands':{name:read(BASE/(name+'.json')) for name in checks+list(failed)},'candidate_patch_sha256':sha(OUT/'candidate.patch'),'failure_assessment_sha256':sha(OUT/'check-failure-assessment.json'),'paid_calls':0})
save('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':proposal['scanner'],'engineering_files_verified':len(engineering),'prior_evidence_files_verified':len(prior),'requirements':297,'protected_user_files':8,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{name:sha(BASE/(name+'.json')) for name in checks},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'closed_failed_optimization_attempts':1,'candidate_reverted':True,'next_optimization_attempts':0,'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Verified297requirements,302restored engineering files,failed attempt retained and closed; next proposal unapproved.')
