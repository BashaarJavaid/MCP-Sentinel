"""Bind stopped-regression evidence and the pending diagnostic after seal95."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;assets=base/'v66-invalidation-contract';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
assert read(out/'seal-postwrite-verification.json')['passed']
seal=read(base/'evidence-v95.json');assert sha(base/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; supplemental completion receipt.'})
p=base/'README.md';s=p.read_text();assert s.count('batches 1–94')==1;s=s.replace('batches 1–94','batches 1–95',1);first,rest=s.split('\n',1)
block=f'''
## Invalidation regression timeout evidence seal 95

[Seal 95](evidence-v95.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 94 earlier archives and every member verified.
The approved `4145d35` native timeout, closed 204-input remainder, all 383 audit rows,
unapproved parent-and-worker diagnostic, source/timer/approval controls, final
checks/packages and supplemental v66 delivery/approval receipts are preserved.
Restore after seals 1–94 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(out/'pr-body-delivery.md').write_text((out/'pr-body.md').read_text()+f'\n[Seal 95]({url}evidence-v95.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 94 earlier archives verified. Final docs/packages pass with unchanged tested `4145d35` product bytes.\n')
old=read(assets/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(v):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in v.strip().split('\n\n')}
actual=parse(worktrees);expected=parse(old['worktrees']);assert set(actual)==set(expected)
for n,h in expected.items():assert actual[n]==('da7557076b122611dbfedd3587450796073af288' if n==str(root) else h),n
for n,d in old['user_files_sha256'].items():assert sha(root/n)==d,n
review=['seal-postwrite-verification.json','assessment.json','validation.json','budget-closed.json','compatible-reuse.json','audit.json','prior-row-preservation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','parent-sampler-selfcheck/packet.json','../v67-diagnostic-boundary.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','owned-final.json','seal-execution.json','execution.json','launch.json','../v66-invalidation-contract/delivery-verification.json','../v66-invalidation-contract/evaluation-authorization.json','../v66-invalidation-contract/execution-consumed.json','../v66-invalidation-contract/execution-preflight.json','../v66-invalidation-contract/authorize-regression.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'da7557076b122611dbfedd3587450796073af288','corrected_scanner':read(out/'assessment.json')['scanner'],'owning_docs_sha256':{n:sha(root/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((out/n).resolve().relative_to(root)):sha(out/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(root/'docs/architecture.md')},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v95.json','index_sha256':sha(base/'evidence-v95.json'),'archive_sha256':seal['sha256']},'diagnostic_proposal_sha256':sha(out/'diagnostic-proposal.json'),'corpus_budget':read(out/'assessment.json')['budget'],'profiles':0,'diagnostic_approved':False,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema retain tested4145d35; final README metadata rebuilt. One parent-and-worker profile is unapproved/unexecuted. Final supplemental seal verification rechecked all95 archives after delivery-helper preparation stopped; those helpers are outside seal95 and directly tracked. Exact supplemental draft readback is still required.'})
print('Bound16 owning docs and exact unapproved diagnostic after seal95.')
