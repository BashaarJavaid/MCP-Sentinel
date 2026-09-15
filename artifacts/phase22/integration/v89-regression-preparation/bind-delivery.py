"""Bind seal104 and the concrete regression proposal to the existing draft destination."""
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];ENG=BASE/'v88-literal-metadata-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,p):
 with (OUT/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v104.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
p=read(OUT/'evaluation-proposal.json');assert p['status']=='proposed_not_approved_not_executed'
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
head='5142a3fbd5bcff63719df6cce3a30543214e7d27';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True);assert worktrees==read(ENG/'freeze.json')['worktrees_after']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all103prior archives and every new member verified. Supplemental receipt outside its own seal.'})
readme=BASE/'README.md';text=readme.read_text();assert text.count('batches 1–103')==1;text=text.replace('batches 1–103','batches 1–104',1).replace('## Current Python-correction proposal evidence seal 103','## Historical Python-correction proposal evidence seal 103',1)
first,rest=text.split('\n',1)
block=f'''
## Current literal metadata correction and regression evidence seal 104

[Seal 104](evidence-v104.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 103 previous archives and every new member were verified.
The closed V87 collection has 111 observations / 48 equal ordered pairs at `884d376`, with Proxmox still failing.
The literal metadata correction passes 2,596 tests / 36 skips locally and all 12 hosted suites,
29 normal jobs/docs, six zero-call production requests and 19 approved runtime bindings.
The exact six-observation Proxmox follow-up is prepared, unapproved and unexecuted.
All 479 requirements and 28 unaccepted limitation proposals retain their history.

Restore after seals 1–103 in numeric order into separate staging; verify every member,
reject unsafe paths and stop on unexplained conflicts. Post-seal documentation and actual
draft-delivery receipts remain supplemental. **Phase 22 incomplete; zero new paid calls.**
'''
readme.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal 104]({url}evidence-v104.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 103 prior archives and every new member verified.\n')
previous=read(BASE/'v86-regression-preparation/documentation-binding.json');protected=read(BASE/'v82-python-module-dispatch/intake-and-authorization.json')['protected_user_files_sha256']
assert len(protected)==11
for name,digest in protected.items():assert sha(ROOT/name)==digest,name
review=[path for path in OUT.iterdir() if path.is_file() and path.suffix in {'.py','.json','.md'}]
extra=[ENG/name for name in ['candidate-commit.json','source-assessment.json','intake.json','local-checks.json','compatibility.json','freeze.json','checkout-binding.json','candidate-distributions.json']]
extra.extend([BASE/'v88-candidate-quality-audit/packet.json',BASE/'v88-candidate-quality/packet.json',BASE/'v88-production-capture-revalidation/packet.json',BASE/'v82-python-module-dispatch/intake-and-authorization.json',BASE/'v82-python-module-dispatch/receiver-mutation-controls.json',BASE/'v80-unseen-results/final-assessment/assessment.json',BASE/'v86-regression-preparation/delivery-verification.json',BASE/'v87-regression-results/final-assessment/assessment.json',BASE/'v87-regression-results/completion-verification.json',BASE/'v87-regression-results/metadata-entry-source-inventory.json'])
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':p['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in read(OUT/'owning-docs.json')['sha256']},'review_packet_sha256':{str(path.relative_to(ROOT)):sha(path) for path in review+extra},'additional_normative_docs_sha256':previous['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v104.json','index_sha256':sha(BASE/'evidence-v104.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(OUT/'evaluation-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_observations':0,'proposed_observations':6,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal proposal/source/worktree binding. Exact draft delivery and separate numerical approval remain; no corpus or human technical acceptance inferred.'})
print('Bound seal104, exact6-observation proposal,17owningdocs and11protected documents for draft delivery.')
