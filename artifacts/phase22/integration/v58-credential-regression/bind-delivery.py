"""Bind stopped-budget review and documentation after evidence seal86."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v57-credential-merge'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(BASE/'evidence-v86.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v58-credential-regression/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; this completion receipt is supplemental.'})
path=BASE/'README.md';text=path.read_text().replace('batches 1–85','batches 1–86',1);first,rest=text.split('\n',1)
block=f'''
## Credential regression evidence seal 86

[Seal 86](evidence-v86.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 85 earlier archives and every member
verified. This retains the approved first-input timeout at `dc73715`, 204 closed
unstarted observations, all 314 audit rows, the unapproved current-source profile,
synthetic worker identity and approval-boundary checks, final docs/packages,
and supplemental v57 delivery/approval receipts. All earlier failures remain retained.
Restore after seals 1–85 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and delivery
readback are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(OUT/'pr-body.md').read_text()+f'\n[Seal 86]({url}evidence-v86.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 85 earlier archives and every member verified. Final docs/package checks pass with code identical to hosted `dc73715`; post-seal documentation and readback are supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:stream.write(body)
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('53d3045b3927ffe3163f4016b98f563b2ed87096' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['assessment.json','audit.json','validation.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','owned-final.json','prior-row-preservation.json','seal-execution.json','budget-closed.json','diagnostic.py','corrected-sampling-worker.py','sampler-selfcheck.py','../v57-credential-merge/evaluation-authorization.json','../v57-credential-merge/execution-consumed.json','../v57-credential-merge/execution-preflight.json','../v57-credential-merge/authorize-regression.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'53d3045b3927ffe3163f4016b98f563b2ed87096','corrected_scanner':read(OUT/'assessment.json')['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/name).resolve().relative_to(ROOT)):sha(OUT/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v86.json','index_sha256':sha(BASE/'evidence-v86.json'),'archive_sha256':seal['sha256']},'diagnostic_proposal_sha256':sha(OUT/'diagnostic-proposal.json'),'corpus_budget':read(OUT/'assessment.json')['budget'],'diagnostic_executions':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/test/schema/lock/workflow bytes remain engineering-testeddc73715; current README package metadata separately verified. Actual draft delivery requires separate supplemental readback.'})
print('Bound16owning docs and unexecuted current-source diagnostic after seal86.')
