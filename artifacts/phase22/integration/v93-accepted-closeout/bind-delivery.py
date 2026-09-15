"""Bind the verified evidence seal and exact failed-gate decision to draft delivery."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3];OLD=BASE/'v92-technical-acceptance';ENG=BASE/'v88-literal-metadata-correction'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,p):
 with (OUT/n).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v107.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
p=read(OLD/'acceptance-proposal.json');assert read(OUT/'technical-acceptance.json')['approved'] and read(OUT/'technical-acceptance.json')['technical_acceptance_received']
head='792d92216c0bb7268b6757c61c5133676a1c7509';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head
previous=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)
assert worktrees==previous['worktrees'].replace('worktree '+str(ROOT)+'\nHEAD '+previous['baseline_delivery'],'worktree '+str(ROOT)+'\nHEAD '+head,1)
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all106prior archives and every new member verified. Supplemental receipt outside its own seal.'})
readme=BASE/'README.md';text=readme.read_text();assert text.count('batches 1–106')==1;text=text.replace('batches 1–106','batches 1–107',1).replace('## Current technical acceptance evidence seal 106','## Historical technical acceptance evidence seal 106',1)
first,rest=text.split('\n',1)
block=f'''
## Current accepted-closeout evidence seal 107

[Seal 107](evidence-v107.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 106 previous archives and every new member were verified.
The immutable explicit human technical acceptance receipt and 493-row accepted-closeout audit
preserve all 30 accepted limitations and two existing paid/pilot deferrals. Proxmox remains
unsupported/recovery deferred; ordinary FAF completion within 1,800 seconds remains unestablished;
V68 remains unapproved/unimplemented. Every original failed measurement remains failed.

Restore after seals 1–106 in numeric order into separate staging; verify every member, reject unsafe
paths and stop on unexplained conflicts. The final delivery-verification/final-audit receipts remain
honest supplemental post-delivery evidence outside their own seal/commit. **Phase 22 is technically
complete under the accepted revised scope; actual final delivery is separately verified. Zero new paid calls.**
'''
readme.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal 107]({url}evidence-v107.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 106 prior archives and every new member verified.\n')
protected=previous['user_files_sha256'];assert len(protected)==11
for n,h in protected.items():assert sha(ROOT/n)==h,n
review=[path for path in OUT.iterdir() if path.is_file() and path.suffix in {'.py','.json','.md'}]
extra=[BASE/'v90-regression-results'/n for n in ['summary.md','final-assessment/assessment.json','final-assessment/validation.json','completion-verification.json','remaining-source-boundary.json','execution.json']]
extra.extend([ENG/n for n in ['local-checks.json','compatibility.json','source-assessment.json']]);extra.extend([OLD/'delivery-verification.json',OUT/'technical-acceptance.json',OUT/'intake-verification.json',BASE/'v88-candidate-quality-audit/packet.json'])
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':p['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in read(OUT/'owning-docs.json')['sha256']},'review_packet_sha256':{str(path.relative_to(ROOT)):sha(path) for path in review+extra},'additional_normative_docs_sha256':previous['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v107.json','index_sha256':sha(BASE/'evidence-v107.json'),'archive_sha256':seal['sha256']},'acceptance_proposal_sha256':sha(OLD/'acceptance-proposal.json'),'technical_acceptance_receipt_sha256':sha(OUT/'technical-acceptance.json'),'closeout_plan_sha256':sha(OUT/'closeout-plan.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_observations':6,'proposed_observations':0,'paid_calls':0,'technical_acceptance_received':True,'phase22_complete':False,'qualification':'Post-seal accepted receipt/source/worktree binding. Explicit technical acceptance is recorded; actual verified accepted-closeout delivery alone remains.'})
print('Bound seal107, explicit technical acceptance receipt and accepted closeout,17owning docs and11protected documents for draft delivery.')
