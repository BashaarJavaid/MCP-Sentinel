"""Bind the assessed profile and review documents after seal 89."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
OLD=BASE/'v60-long-timeout-regression'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v89.json')
assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v61-faf-long-timeout-sampling/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; supplemental completion receipt.'})
path=BASE/'README.md'
text=path.read_text()
assert text.count('batches 1–88')==1
text=text.replace('batches 1–88','batches 1–89',1)
first,rest=text.split('\n',1)
block=f'''
## Thirty-minute profile evidence seal 89

[Seal 89](evidence-v89.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 88 earlier archives and every member verified.
The approved `7bf4c6e` profile, partial samples and frame/source assessment, closed
one-use budget, all 335 audit rows, unapproved discovery-reuse proposal, final
docs/packages and supplemental v60 delivery/approval receipts are preserved.
Restore after seals 1–88 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT/'pr-body-delivery.md').open('x') as f:
    f.write((OUT/'pr-body.md').read_text()+f'\n[Seal 89]({url}evidence-v89.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 88 earlier archives verified. Final docs/package checks pass with product bytes identical to tested `7bf4c6e`.\n')
old=read(OLD/'documentation-binding.json')
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):
    return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():
    assert parse(worktrees)[name]==('777c7526f18733b7ca4b49e3caf690f02d25adf6' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['assessment.json','audit.json','validation.json','optimization-proposal.json','source-assessment.json','sample-attribution.json','frame-source-bindings.json','frame-contexts.json','compatible-reuse.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','owned-final.json','prior-row-preservation.json','seal-execution.json','budget-closed.json','../v60-long-timeout-regression/diagnostic-authorization.json','../v60-long-timeout-regression/diagnostic-consumed.json','../v60-long-timeout-regression/diagnostic-preflight.json','../v60-long-timeout-regression/authorize-diagnostic.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'777c7526f18733b7ca4b49e3caf690f02d25adf6','corrected_scanner':read(OUT/'assessment.json')['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/n).resolve().relative_to(ROOT)):sha(OUT/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(ROOT/'docs/architecture.md')},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v89.json','index_sha256':sha(BASE/'evidence-v89.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'corpus_budget':read(OLD/'assessment.json')['budget'],'diagnostic_budget':read(OUT/'budget-closed.json'),'profiles':1,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema remain tested 7bf4c6e; final README metadata separately rebuilt. One source-only discovery-reuse attempt is unapproved/unstarted. Draft delivery requires exact supplemental readback.'})
print('Bound 16 owning docs and unapproved source-only reuse proposal after seal 89.')
