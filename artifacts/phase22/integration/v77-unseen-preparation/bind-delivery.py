"""Bind sealed technical review to protected files and the existing draft destination."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v100.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
assert read(OUT/'evaluation-proposal.json')['status']=='prepared_not_approved_not_executed'
intake=read(OUT/'scope-and-precuration-freeze.json');inventory=read(OUT/'workspace-inventory.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True);assert worktrees==inventory['worktrees']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==intake['delivery_head']
write('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all99prior archives and every new member verified. Supplemental receipt outside its own seal.'})
p=BASE/'README.md';text=p.read_text();assert text.count('batches 1–99')==1;text=text.replace('batches 1–99','batches 1–100',1).replace('## Current technical-review evidence seal 99','## Historical technical-review evidence seal 99',1)
first,rest=text.split('\n',1)
block=f'''
## Current unseen-preparation evidence seal 100

[Seal 100](evidence-v100.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 99 prior archives and every new member were verified.
It preserves the pre-curation freeze, novelty/source research and complete upstream pairs,
the unapproved twelve-observation proposal, synthetic controls and corrections, affected checks,
all 435 requirements and supplemental V76 delivery. Zero new corpus observations or paid calls.

Restore after seals 1–99 in numeric order into separate staging, rejecting unsafe paths/symlinks,
checking every member hash and stopping on unexplained conflicts. The six-input corpus packet is
also directly tracked. Post-seal documentation and actual draft delivery receipts are supplemental.
**Phase 22 remains incomplete; numerical approval and later technical acceptance are separate.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT/'pr-body-delivery.md').open('x') as f:f.write((OUT/'pr-body.md').read_text()+f'\n[Seal 100]({url}evidence-v100.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 99 prior archives and every new member verified.\n')
old=read(BASE/'v72-prototype-property-correction/documentation-binding.json');protected=intake['protected_files_sha256'];assert len(protected)==11
for name,d in protected.items():assert sha(ROOT/name)==d,name
review=['audit.json','summary.md','evaluation-proposal.json','scoring-rubric.json','selection-record.json','prior-row-preservation.json','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-final.json','pr-body-delivery.md','seal-execution.json','final-runner-verification.json','staging-and-boundary-verification.json','launcher-binding.json']
paths=[OUT/name for name in review]+[p for p in (ROOT/'artifacts/phase22/corpus-unseen-v1').rglob('*') if p.is_file()]
write('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':intake['delivery_head'],'corrected_scanner':read(OUT/'audit.json')['scanner_identity'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'additional_normative_docs_sha256':old['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v100.json','index_sha256':sha(BASE/'evidence-v100.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(OUT/'evaluation-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_input_accounting':read(OUT/'audit.json')['current_source_input_accounting'],'repository_gates_passed':4,'profiles_in_this_continuation':0,'optimization_approved':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding of numerical proposal to current source and protected worktrees. Exact existing-draft delivery and separate human technical acceptance remain required.'})
print('Bound exact numerical proposal,16owning docs and11protected user documents afterseal100.')
