"""Bind reviewed engineering and pending regression documents after evidence seal90."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
seal=read(base/'evidence-v90.json');assert sha(base/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python',str(out/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; supplemental completion receipt.'})
p=base/'README.md';s=p.read_text();assert s.count('batches 1–89')==1;s=s.replace('batches 1–89','batches 1–90',1);first,rest=s.split('\n',1)
block=f'''
## Shared discovery evidence seal 90

[Seal 90](evidence-v90.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 89 earlier archives and every member verified.
The approved `1948bf9` source-only discovery change, complete synthetic/local/hosted
engineering, six zero-call replays, all 345 audit rows, exact unapproved regression
proposal, final docs/packages and supplemental v61 delivery receipts are preserved.
Restore after seals 1–89 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(out/'pr-body-delivery.md').write_text((out/'pr-body.md').read_text()+f'\n[Seal 90]({url}evidence-v90.json):{len(seal["files"])} members,SHA-256 `{seal["sha256"]}`; all89 earlier archives verified. Final docs/package checks pass with product bytes identical to tested `1948bf9`.\n')
a=read(out/'authorization.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(v):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in v.strip().split('\n\n')}
actual=parse(worktrees);expected=parse(a['worktrees']);rev='1948bf942babce155b701f5b22ed941eb16d99d0'
for n,h in expected.items():assert actual[n]==(rev if n==str(root) else h),n
assert set(actual)-set(expected)=={'/private/tmp/mcp-phase22-frozen-1948bf9'}
assert actual['/private/tmp/mcp-phase22-frozen-1948bf9']==rev
for n,d in a['user_files_sha256'].items():assert sha(root/n)==d,n
review=['authorization.json','source-checkpoint.json','candidate-commit.json','source-proof.json','discovery-equivalence.json','local-checks.json','compatibility.json','freeze.json','frozen-source-validation.json','audit.json','prior-row-preservation.json','evaluation-proposal.json','scoring-rubric.json','launcher-binding.json','runner-boundaries.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-final.json','seal-execution.json','../v61-faf-long-timeout-sampling/delivery-verification.json']
docs=read(base/'v61-faf-long-timeout-sampling/documentation-binding.json')['owning_docs_sha256']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':rev,'corrected_scanner':read(out/'freeze.json')['scanner'],'owning_docs_sha256':{n:sha(root/n) for n in docs},'review_packet_sha256':{str((out/n).resolve().relative_to(root)):sha(out/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(root/'docs/architecture.md')},'user_files_sha256':a['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v90.json','index_sha256':sha(base/'evidence-v90.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(out/'evaluation-proposal.json'),'corpus_budget':{'approved':False,'proposed_observations':205,'attempted':0,'all_prior_budgets_closed':True},'profiles':0,'optimization_attempts':1,'optimization_budget_closed':True,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema remain tested1948bf9; final README metadata rebuilt. Exact205-observation regression unapproved/unexecuted. Draft delivery requires exact supplemental readback.'})
print('Bound16 owning docs and exact unapproved regression proposal after seal90.')
