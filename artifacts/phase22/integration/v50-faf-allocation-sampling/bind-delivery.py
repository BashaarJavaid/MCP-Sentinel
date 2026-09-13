"""Bind stopped-budget review and documentation after evidence seal78."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v49-allocation-regression'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(BASE/'evidence-v78.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v50-faf-allocation-sampling/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; this completion receipt is supplemental.'})
path=BASE/'README.md';text=path.read_text().replace('batches 1–77','batches 1–78',1);first,rest=text.split('\n',1)
block=f'''
## Diagnostic binding correction evidence seal 78

[Seal 78](evidence-v78.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 77 earlier archives and every member
verified. This retains the invalid interrupted profile caused by the stale worker import root,
all 259 audit rows including the corrected preparation disposition, the corrected
unapproved profile with worker identity guards, synthetic rejection and approval
boundary checks, final docs/packages, and supplemental v49 delivery/approval receipts.
Restore after seals 1–77 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and delivery
readback are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(OUT/'pr-body.md').read_text()+f'\n[Seal 78]({url}evidence-v78.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 77 earlier archives and every member verified. Final docs/package checks pass with code identical to hosted `6e4fd67`; post-seal documentation and readback are supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:stream.write(body)
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('2933d39493b8cf7d52bfb8e1ffdca879d20d5c1d' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['assessment.json','source-correction.json','audit.json','diagnostic-proposal.json','sampler-selfcheck/packet.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','prior-row-preservation.json','seal-execution.json','../v49-allocation-regression/diagnostic-authorization.json','../v49-allocation-regression/diagnostic-consumed.json','../v49-allocation-regression/diagnostic-preflight.json','../v49-allocation-regression/authorize-diagnostic.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'2933d39493b8cf7d52bfb8e1ffdca879d20d5c1d','corrected_scanner':read(OUT/'assessment.json')['scanner_expected'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/name).resolve().relative_to(ROOT)):sha(OUT/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v78.json','index_sha256':sha(BASE/'evidence-v78.json'),'archive_sha256':seal['sha256']},'diagnostic_proposal_sha256':sha(OUT/'diagnostic-proposal.json'),'invalid_profile_budget':{'planned':1,'attempted':1,'completed':0,'invalid':1,'remaining':0,'closed':True},'invalid_profile_attempts':1,'corrected_profile_executions':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/test/schema/lock/workflow bytes remain engineering-tested6e4fd67; current README package metadata separately verified. Actual draft delivery requires separate supplemental readback.'})
print('Bound16owning docs and unexecuted current-source diagnostic after seal78.')
