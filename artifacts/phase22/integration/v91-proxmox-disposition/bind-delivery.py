"""Bind the verified evidence seal and exact failed-gate decision to draft delivery."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];OLD=BASE/'v89-regression-preparation';ENG=BASE/'v88-literal-metadata-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,p):
 with (OUT/n).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v105.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
p=read(OUT/'decision-proposal.json');assert not p['limitation_disposition_received'] and not p['technical_acceptance_received']
head='0c8888a3fe89030d02bff32beac32faaf0966e45';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head
previous=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)
assert worktrees==previous['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+previous['baseline_delivery'],'worktree '+str(ROOT)+'\nHEAD '+head,1)
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all104prior archives and every new member verified. Supplemental receipt outside its own seal.'})
readme=BASE/'README.md';text=readme.read_text();assert text.count('batches 1–104')==1;text=text.replace('batches 1–104','batches 1–105',1).replace('## Current literal metadata correction and regression evidence seal 104','## Historical literal metadata correction and regression evidence seal 104',1)
first,rest=text.split('\n',1)
block=f'''
## Current failed Proxmox regression and disposition evidence seal 105

[Seal 105](evidence-v105.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 104 previous archives and every new member were verified.
V90 completed six observations / three equal ordered pairs at `5142a3f`, with Proxmox still failing
two vulnerable detections and all four negative support checks. Complete reports, source assessments,
closed budget and cleanup remain. Unchanged engineering retains 2,596 tests / 36 skips locally and
all 12 hosted suites. All 486 requirements and 30 unaccepted limitations are preserved.

Restore after seals 1–104 in numeric order into separate staging; verify every member, reject unsafe
paths and stop on unexplained conflicts. Post-seal documentation and actual draft-delivery receipts
remain supplemental. **Failed-gate disposition and technical acceptance remain pending;
Phase 22 incomplete; zero new paid calls.**
'''
readme.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal 105]({url}evidence-v105.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 104 prior archives and every new member verified.\n')
protected=previous['user_files_sha256'];assert len(protected)==11
for n,h in protected.items():assert sha(ROOT/n)==h,n
review=[path for path in OUT.iterdir() if path.is_file() and path.suffix in {'.py','.json','.md'}]
extra=[BASE/'v90-regression-results'/n for n in ['summary.md','final-assessment/assessment.json','final-assessment/validation.json','completion-verification.json','remaining-source-boundary.json','execution.json']]
extra.extend([ENG/n for n in ['local-checks.json','compatibility.json','source-assessment.json']]);extra.extend([OLD/'delivery-verification.json',OLD/'evaluation-authorization.json',OLD/'execution-preflight.json',BASE/'v88-candidate-quality-audit/packet.json'])
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':p['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in read(OUT/'owning-docs.json')['sha256']},'review_packet_sha256':{str(path.relative_to(ROOT)):sha(path) for path in review+extra},'additional_normative_docs_sha256':previous['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v105.json','index_sha256':sha(BASE/'evidence-v105.json'),'archive_sha256':seal['sha256']},'decision_proposal_sha256':sha(OUT/'decision-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_observations':6,'proposed_observations':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal decision/source/worktree binding. Exact draft delivery, failed-gate disposition, technical acceptance and actual accepted closeout remain.'})
print('Bound seal105, exact failed-gate decision,17owning docs and11protected documents for draft delivery.')
