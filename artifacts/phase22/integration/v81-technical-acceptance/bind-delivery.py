"""Bind sealed technical review to protected files and the existing draft destination."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v102.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
assert read(OUT/'acceptance-proposal.json')['technical_acceptance_received'] is False
intake=read(BASE/'v77-unseen-preparation/scope-and-precuration-freeze.json');previous=read(BASE/'v79-unseen-metadata-correction/documentation-binding.json');head='2453698eb65eed83b121f2661a4004319617693f';intake['head']=head;intake['worktrees']=previous['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+previous['baseline_delivery'],'worktree '+str(ROOT)+'\nHEAD '+head,1);intake['protected_user_files_sha256']=intake['protected_files_sha256'];worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True);assert worktrees==intake['worktrees']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==intake['head']
write('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all101prior archives and every new member verified. Supplemental receipt outside its own seal.'})
p=BASE/'README.md';text=p.read_text();assert text.count('batches 1–101')==1;text=text.replace('batches 1–101','batches 1–102',1).replace('## Current metadata-correction evidence seal 101','## Historical metadata-correction evidence seal 101',1)
first,rest=text.split('\n',1)
block=f'''
## Current unseen-review evidence seal 102

[Seal 102](evidence-v102.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 101 prior archives and every new member were verified.
It includes the approved V80 twelve-observation run, six equal ordered pairs, complete source
assessment, the initial V78 metadata failure, all 448 requirements and 26 proposed limitation
rows. Taskwarrior passes narrowly; Proxmox's vulnerable read and negative support fail.
Ordinary FAF timing and V68 remain explicitly qualified. No human acceptance has occurred.

Restore after seals 1–101 in numeric order into separate staging, rejecting unsafe paths/symlinks,
checking every member hash and stopping on unexplained conflicts. Post-seal documentation and
actual draft delivery receipts are supplemental. **Phase 22 remains incomplete; zero new paid calls.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT/'pr-body-delivery.md').open('x') as f:f.write((OUT/'pr-body.md').read_text()+f'\n[Seal 102]({url}evidence-v102.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 101 prior archives and every new member verified.\n')
old=read(BASE/'v72-prototype-property-correction/documentation-binding.json');protected=intake['protected_user_files_sha256'];assert len(protected)==11
for name,d in protected.items():assert sha(ROOT/name)==d,name
review=['audit.json','summary.md','acceptance-limits.md','acceptance-proposal.json','prior-row-preservation.json','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-final.json','status.md','pr-body-delivery.md','seal-execution.json']
extra=[BASE/'v73-corrected-four-results/summary.md',BASE/'v73-corrected-four-results/final-assessment/assessment.json',BASE/'v73-corrected-four-results/completion-verification.json',BASE/'v73-corrected-four-results/execution.json',BASE/'v75-prior-language-results/final-assessment/assessment.json',BASE/'v75-prior-language-results/completion-verification.json',BASE/'v75-prior-language-results/execution.json',BASE/'v74-prior-language-preparation/evaluation-proposal.json',BASE/'v74-prior-language-preparation/evaluation-authorization.json',BASE/'v72-prototype-property-correction/evaluation-authorization.json',BASE/'v72-prototype-property-correction/delivery-verification.json']
paths=[OUT/name for name in review]+extra+[BASE/'v80-unseen-results/final-assessment/assessment.json',BASE/'v80-unseen-results/completion-verification.json',BASE/'v78-unseen-results/stop-assessment.json']
write('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':intake['head'],'corrected_scanner':read(OUT/'audit.json')['scanner_identity'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'additional_normative_docs_sha256':old['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v102.json','index_sha256':sha(BASE/'evidence-v102.json'),'archive_sha256':seal['sha256']},'acceptance_proposal_sha256':sha(OUT/'acceptance-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_input_accounting':read(OUT/'audit.json')['current_source_input_accounting'],'repository_gates_passed':4,'profiles_in_this_continuation':0,'optimization_approved':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding of final review to current source and protected worktrees. Exact existing-draft delivery and separate human technical acceptance remain required.'})
print('Bound complete technical review,16owning docs and11protected user documents afterseal102.')
