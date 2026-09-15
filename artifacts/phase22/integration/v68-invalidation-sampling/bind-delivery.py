"""Bind the sealed current profile and unapproved literal serialization proposal."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;previous=base/'v67-invalidation-regression'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
seal=read(base/'evidence-v96.json');assert sha(base/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; supplemental completion receipt. Delivery helpers were prepared before sealing and are archive members.'})
p=base/'README.md';s=p.read_text();assert s.count('batches 1–95')==1;s=s.replace('batches 1–95','batches 1–96',1);first,rest=s.split('\n',1)
block=f'''
## Current profile and recovery evidence seal 96

[Seal 96](evidence-v96.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 95 earlier archives and every member verified.
The approved `4145d35` partial parent profile, closed budget, all 391 audit rows,
exact missing-file recovery and selective authorized Docker cleanup, unapproved
literal serialization proposal, final checks/packages and supplemental v67
approval/delivery receipts are preserved. Restore after seals 1–95 in numeric
order into safe separate staging; reject unsafe paths/symlinks, verify all hashes
and stop on unexplained conflicts. The v73 log correction remains preserved.
Post-seal documentation and exact draft readback are supplemental.
**Phase 22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(out/'pr-body-delivery.md').write_text((out/'pr-body.md').read_text()+f'\n[Seal 96]({url}evidence-v96.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 95 earlier archives verified. Final docs/packages pass with unchanged tested `4145d35` product bytes.\n')
old=read(previous/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(v):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in v.strip().split('\n\n')}
actual=parse(worktrees);expected=parse(old['worktrees']);assert set(actual)==set(expected)
for n,h in expected.items():assert actual[n]==('c60b7a858497c355326044b959d9f6ad8d755a80' if n==str(root) else h),n
for n,d in old['user_files_sha256'].items():assert sha(root/n)==d,n
review=['assessment.json','validation.json','budget-closed.json','compatible-reuse.json','audit.json','prior-row-preservation.json','optimization-proposal.json','source-assessment.json','frame-source-bindings.json','frame-contexts.json','sample-attribution.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','command-provenance-qualification.json','check-failure-assessment.json','recovery-assessment.json','owned-work.json','owned-final.json','seal-execution.json','execution.json','attempt.json','../v67-invalidation-regression/delivery-verification.json','../v67-invalidation-regression/diagnostic-authorization.json','../v67-invalidation-regression/diagnostic-consumed.json','../v67-invalidation-regression/diagnostic-preflight.json','../v67-invalidation-regression/authorize-diagnostic.py','../v67-invalidation-regression/restored-launch-preflight.json','../v67-invalidation-regression/launch-preflight-failure.json','../v67-invalidation-regression/worktree-restoration.json','../v67-invalidation-regression/sealed-evidence-restoration.json','../v67-invalidation-regression/user-document-restoration-detection.json','../v67-invalidation-regression/user-document-restoration-final.json','../v67-invalidation-regression/docker-cleanup.json','../v67-invalidation-regression/base-image-cleanup.json']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'c60b7a858497c355326044b959d9f6ad8d755a80','corrected_scanner':read(out/'assessment.json')['scanner'],'owning_docs_sha256':{n:sha(root/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((out/n).resolve().relative_to(root)):sha(out/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(root/'docs/architecture.md')},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v96.json','index_sha256':sha(base/'evidence-v96.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(out/'optimization-proposal.json'),'corpus_budget':read(previous/'assessment.json')['budget'],'profile_budget':{'attempts':1,'completed':0,'incomplete':1,'reports':0,'samples':148001,'remaining':0,'closed':True},'profiles':1,'diagnostic_approved':True,'optimization_approved':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema retain tested4145d35; final README metadata rebuilt. One literal serialization reuse source-only proposal remains unapproved and unimplemented. File recovery and Docker cleanup retain actual outcomes and unknown deletion cause. Exact supplemental draft readback remains required.'})
print('Bound16owning docs and exact pending source proposal after seal96.')
