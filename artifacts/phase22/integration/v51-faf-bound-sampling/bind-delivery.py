"""Bind stopped-budget review and documentation after evidence seal79."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v50-faf-allocation-sampling'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(BASE/'evidence-v79.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v51-faf-bound-sampling/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; this completion receipt is supplemental.'})
path=BASE/'README.md';text=path.read_text().replace('batches 1–78','batches 1–79',1);first,rest=text.split('\n',1)
block=f'''
## Current-source partial profile evidence seal 79

[Seal 79](evidence-v79.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 78 earlier archives and every member
verified. This retains the current-source sampled timeout, four verified worker identities and
79,307 partial samples, complete frame/source attribution, all 265 audit rows,
and one unapproved source-only merge fast-path optimization proposal. Final
docs/packages and supplemental v50 delivery/approval receipts are retained.
Restore after seals 1–78 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and delivery
readback are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(OUT/'pr-body.md').read_text()+f'\n[Seal 79]({url}evidence-v79.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 78 earlier archives and every member verified. Final docs/package checks pass with code identical to hosted `6e4fd67`; post-seal documentation and readback are supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:stream.write(body)
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('cd5e9aea889053cc5ba9ea25997b273805635241' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['assessment.json','validation.json','source-assessment.json','sample-attribution.json','frame-source-bindings.json','audit.json','optimization-proposal.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','prior-row-preservation.json','seal-execution.json','../v50-faf-allocation-sampling/diagnostic-authorization.json','../v50-faf-allocation-sampling/diagnostic-consumed.json','../v50-faf-allocation-sampling/diagnostic-preflight.json','../v50-faf-allocation-sampling/authorize-diagnostic.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'cd5e9aea889053cc5ba9ea25997b273805635241','corrected_scanner':read(OUT/'assessment.json')['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/name).resolve().relative_to(ROOT)):sha(OUT/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v79.json','index_sha256':sha(BASE/'evidence-v79.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'profile_budget':{'planned':1,'attempted':1,'completed':0,'incomplete':1,'remaining':0,'closed':True},'current_source_profile_attempts':1,'valid_partial_profiles':1,'current_optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/test/schema/lock/workflow bytes remain engineering-tested6e4fd67; current README package metadata separately verified. Actual draft delivery requires separate supplemental readback.'})
print('Bound16owning docs and unapproved source-only optimization after seal79.')
