"""Bind seal103 and the concrete regression proposal to the existing draft destination."""
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];ENG=BASE/'v85-class-call-boundary'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,p):
 with (OUT/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v103.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
p=read(OUT/'evaluation-proposal.json');assert p['status']=='proposed_not_approved_not_executed'
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
head='884d3763d8d63786e1726932951fd859cb6071c2';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True);assert worktrees==read(ENG/'freeze.json')['worktrees_after']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all102prior archives and every new member verified. Supplemental receipt outside its own seal.'})
readme=BASE/'README.md';text=readme.read_text();assert text.count('batches 1–102')==1;text=text.replace('batches 1–102','batches 1–103',1).replace('## Current unseen-review evidence seal 102','## Historical unseen-review evidence seal 102',1)
first,rest=text.split('\n',1)
block=f'''
## Current Python-correction proposal evidence seal 103

[Seal 103](evidence-v103.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 102 prior archives and every new member were verified.
It preserves failed `8f0639f`, corrected `884d376`, 2,553 tests / 36 skips locally and all
12 hosted suites, 29 normal jobs/docs, six zero-call requests and 19 runtime bindings.
The exact 111-observation exposed regression is prepared, unapproved and unexecuted.
All 463 requirements and 26 unaccepted limitation proposals remain, including original
unseen failures, ordinary FAF timing and unopened V68. No human acceptance has occurred.

Restore after seals 1–102 in numeric order into separate staging; reject unsafe paths,
verify every member and stop on unexplained conflicts. Post-seal documentation and
actual draft-delivery receipts are supplemental. **Phase 22 incomplete; zero new paid calls.**
'''
readme.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal 103]({url}evidence-v103.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 102 prior archives and every new member verified.\n')
previous=read(BASE/'v81-technical-acceptance/documentation-binding.json');protected=read(BASE/'v82-python-module-dispatch/intake-and-authorization.json')['protected_user_files_sha256']
assert len(protected)==11
for name,digest in protected.items():assert sha(ROOT/name)==digest,name
review=[path for path in OUT.iterdir() if path.is_file() and path.suffix in {'.py','.json','.md'}]
extra=[ENG/name for name in ['candidate-commit.json','source-assessment.json','intake.json','local-checks.json','compatibility.json','freeze.json','checkout-binding.json','candidate-distributions.json','class-call-control.json']]
extra.extend([BASE/'v85-candidate-quality-audit/packet.json',BASE/'v85-candidate-quality/packet.json',BASE/'v85-production-capture-revalidation/packet.json',BASE/'v82-python-module-dispatch/intake-and-authorization.json',BASE/'v82-python-module-dispatch/receiver-mutation-controls.json',BASE/'v80-unseen-results/final-assessment/assessment.json',BASE/'v81-technical-acceptance/delivery-verification.json'])
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':p['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in read(OUT/'owning-docs.json')['sha256']},'review_packet_sha256':{str(path.relative_to(ROOT)):sha(path) for path in review+extra},'additional_normative_docs_sha256':previous['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v103.json','index_sha256':sha(BASE/'evidence-v103.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(OUT/'evaluation-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_observations':0,'proposed_observations':111,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal proposal/source/worktree binding. Exact draft delivery and separate numerical approval remain; no corpus or human technical acceptance inferred.'})
print('Bound seal103, exact111-observation proposal,17owningdocs and11protected documents for draft delivery.')
