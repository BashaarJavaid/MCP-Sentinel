"""Validate completed candidate/proposal evidence before sealing and delivery."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
out=Path(__file__).resolve().parent; base=out.parent; root=Path.cwd()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (out/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
checks=['v57-local-checks','v57-quality-audit','v57-frozen-validation','v57-launcher-check','v57-reconciliation','v57-final-docs','v57-final-build','v57-final-distributions','v57-check-failure-assessment','v57-owned-cleanup']
for name in checks:assert read(base/(name+'.json'))['exit_code']==0,name
local=read(out/'local-checks.json'); frozen=Path(read(out/'freeze.json')['frozen_checkout'])
for name,digest in local['candidate_engineering_files_sha256'].items():assert sha(root/name)==sha(frozen/name)==digest,name
old=read(base/'v56-canonical-unknown/documentation-binding.json')
for name,digest in old['user_files_sha256'].items():assert sha(root/name)==digest,name
for name,digest in read(out/'owning-docs.json')['sha256'].items():assert sha(root/name)==digest,name
prior=read(base/'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name,digest in prior.items():assert sha(root/name)==digest,name
assert read(out/'optimization-budget-closed.json')['remaining_attempts']==0
p=read(out/'evaluation-proposal.json')
for name,digest in p['files_sha256'].items():assert sha(root/name)==digest,name
assert p['bounds']['native_observations']==205 and len(p['order'])==205
assert not (out/'evaluation-authorization.json').exists() and not (out/'execution-consumed.json').exists() and not (base/'v58-credential-regression').exists()
assert read(out/'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
audit=read(out/'audit.json');assert len(audit['requirements'])==89 and len(audit['additional_scope_requirements'])==219
assert audit['requirements']==read(base/'v56-canonical-unknown/audit.json')['requirements']
assert not audit['technical_acceptance_received'] and not audit['phase22_complete']
assert not subprocess.check_output(['git','diff','dc73715','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md'])
subprocess.run(['git','diff','--check'],check=True)
subprocess.run(['git','merge-base','--is-ancestor','8b6b0ddf1d6f6cf5a8da3ab9421471865b801455','HEAD'],check=True)
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
write('command-provenance.json',{'wrapper_commands':{p.stem:read(p) for p in sorted(base.glob('v57-*.json')) if 'command' in read(p)},'direct_commands':['authorize.py preserved baseline before editing','ruff format tests/test_credential_fallback.py','Reused evaluate.py byte-identically and changed only supervisor output path','explicit candidate push dc73715 to existing draft branch, normal CI34779741236/docs34779741226'],'failure_assessment_sha256':sha(out/'check-failure-assessment.json'),'paid_calls':0})
write('final-checks.json',{'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'engineering_files_verified':len(local['candidate_engineering_files_sha256']),'prior_evidence_files_verified':len(prior),'requirements':308,'protected_user_files':8,'owning_docs':16,'main_and_parent_preserved':True,'checks_sha256':{n:sha(base/(n+'.json')) for n in checks},'evaluation_proposal_sha256':sha(out/'evaluation-proposal.json'),'launcher_binding_sha256':sha(out/'launcher-binding.json'),'optimization_attempts':1,'native_observations':0,'profiles':0,'old_budgets_closed':True,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
print('Final checks passed:302engineering files,308 requirements,16docs,unapproved205-observation proposal.')
