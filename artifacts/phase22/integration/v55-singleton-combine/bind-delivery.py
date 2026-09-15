"""Bind final owning docs and review files after the failed-attempt evidence seal."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v54-faf-fastpath-sampling'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(BASE/'evidence-v83.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v55-singleton-combine/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct seal execution after writers stopped. Supplemental completion receipt.'})
path=BASE/'README.md';text=path.read_text().replace('batches 1–82','batches 1–83',1);first,rest=text.split('\n',1)
block=f'''
## Failed singleton attempt evidence seal 83

[Seal 83](evidence-v83.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 82 preceding archives and every member
verified. The approved broad singleton attempt failed its synthetic environment
equivalence prerequisite and was reverted. Candidate/baseline, initial helper
defect, structural reassessment, all 290 audit rows and one unapproved canonical
UNKNOWN_VALUE-only proposal are preserved. Final docs/packages and supplemental
v54 delivery records are retained. Restore seals 1–83 in order into safe separate
staging; verify hashes and reject unsafe paths or unexplained conflicts. Prior
v73 correction remains retained. Post-seal docs/delivery receipts are supplemental.
**Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(OUT/'pr-body.md').read_text()+f'\n[Seal 83]({url}evidence-v83.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 82 earlier archives verified. Final docs/packages pass with restored code identical to hosted `a36f696`; post-seal readback is supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:stream.write(body)
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('029bef12f71fd507be168fc7731b3b63d20b3ae5' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['authorization.json','assessment.json','identity-validation.json','optimization-budget-closed.json','audit.json','optimization-proposal.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','prior-row-preservation.json','seal-execution.json']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'029bef12f71fd507be168fc7731b3b63d20b3ae5','corrected_scanner':read(OUT/'optimization-proposal.json')['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/name).relative_to(ROOT)):sha(OUT/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v83.json','index_sha256':sha(BASE/'evidence-v83.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'optimization_budget':{'planned':1,'attempted':1,'failed':1,'remaining':0,'closed':True},'next_optimization_approved':False,'next_optimization_attempts':0,'candidate_reverted':True,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal docs binding. Source restored exactly to engineering-tested a36f696. Failed candidate has no claimed engineering pass. Final README metadata independently built/verified; draft delivery needs actual readback.'})
print('Bound16owning docs and unapproved canonical UNKNOWN_VALUE proposal after seal83.')
