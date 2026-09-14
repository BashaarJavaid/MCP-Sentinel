"""Bind stopped-regression evidence and the pending diagnostic after seal91."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;assets=base/'v62-shared-tool-discovery';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
seal=read(base/'evidence-v91.json');assert sha(base/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; supplemental completion receipt.'})
p=base/'README.md';s=p.read_text();assert s.count('batches 1–90')==1;s=s.replace('batches 1–90','batches 1–91',1);first,rest=s.split('\n',1)
block=f'''
## Shared-discovery timeout evidence seal 91

[Seal 91](evidence-v91.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 90 earlier archives and every member verified.
The approved `1948bf9` native timeout, closed 204-input remainder, all 352 audit rows,
unapproved parent-and-worker diagnostic, source/timer/approval controls, final
checks/packages and supplemental v62 delivery/approval receipts are preserved.
Restore after seals 1–90 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(out/'pr-body-delivery.md').write_text((out/'pr-body.md').read_text()+f'\n[Seal 91]({url}evidence-v91.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 90 earlier archives verified. Final docs/packages pass with unchanged tested `1948bf9` product bytes.\n')
old=read(assets/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(v):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in v.strip().split('\n\n')}
actual=parse(worktrees);expected=parse(old['worktrees']);assert set(actual)==set(expected)
for n,h in expected.items():assert actual[n]==('c7b20a30f2a061c00eb8a6ffcc1413a211c01fff' if n==str(root) else h),n
for n,d in old['user_files_sha256'].items():assert sha(root/n)==d,n
review=['assessment.json','validation.json','budget-closed.json','compatible-reuse.json','audit.json','prior-row-preservation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','parent-sampler-selfcheck/packet.json','../v63-diagnostic-boundary.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','owned-final.json','seal-execution.json','execution.json','launch.json','../v62-shared-tool-discovery/delivery-verification.json','../v62-shared-tool-discovery/evaluation-authorization.json','../v62-shared-tool-discovery/execution-consumed.json','../v62-shared-tool-discovery/execution-preflight.json','../v62-shared-tool-discovery/authorize-regression.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'c7b20a30f2a061c00eb8a6ffcc1413a211c01fff','corrected_scanner':read(out/'assessment.json')['scanner'],'owning_docs_sha256':{n:sha(root/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((out/n).resolve().relative_to(root)):sha(out/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(root/'docs/architecture.md')},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v91.json','index_sha256':sha(base/'evidence-v91.json'),'archive_sha256':seal['sha256']},'diagnostic_proposal_sha256':sha(out/'diagnostic-proposal.json'),'corpus_budget':read(out/'assessment.json')['budget'],'profiles':0,'diagnostic_approved':False,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema retain tested1948bf9; final README metadata rebuilt. One parent-and-worker profile is unapproved/unexecuted. Exact supplemental draft readback is still required.'})
print('Bound16 owning docs and exact unapproved diagnostic after seal91.')
