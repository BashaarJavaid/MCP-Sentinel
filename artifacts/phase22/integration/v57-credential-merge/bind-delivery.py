"""Bind final owning docs and review files after the successful engineering evidence seal."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v56-canonical-unknown'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(BASE/'evidence-v85.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v57-credential-merge/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct seal execution after writers stopped. Supplemental completion receipt.'})
path=BASE/'README.md';text=path.read_text().replace('batches 1–84','batches 1–85',1);first,rest=text.split('\n',1)
block=f'''
## Credential correction and regression proposal: evidence seal 85

[Seal 85](evidence-v85.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 84 preceding archives and every member
verified. The approved credential join correction and canonical unknown bypass
pass engineering at `dc73715`: 2,399 tests / 36 skips locally and in all 12 hosted
suites, all 29 normal CI jobs and docs. All 308 audit rows, both original singleton
failures and the separate unapproved 205-observation proposal are preserved.
Restore seals 1–85 in order into safe separate staging; verify hashes and reject
unsafe paths or unexplained conflicts. Prior v73 correction remains retained.
Post-seal docs/delivery receipts are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(OUT/'pr-body.md').read_text()+f'\n[Seal 85]({url}evidence-v85.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 84 earlier archives verified. Final docs/packages pass with product bytes identical to hosted `dc73715`; post-seal readback is supplemental.\n'
with (OUT/'pr-body-delivery.md').open('x') as stream:stream.write(body)
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('dc7371513a065457af566f4b589b9ed147130d64' if name==str(ROOT) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(ROOT/name)==digest,name
review=['authorization.json','source-recovery-assessment.json','correction-validation.json','synthetic-validation.json','synthetic-reports.json','local-checks.json','compatibility.json','freeze.json','launcher-binding.json','scoring-rubric.json','optimization-budget-closed.json','audit.json','evaluation-proposal.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','prior-row-preservation.json','seal-execution.json']
assert parse(worktrees)[read(OUT/'freeze.json')['frozen_checkout']]=='dc7371513a065457af566f4b589b9ed147130d64'
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'9b2585d3a6cc7e1a3584eff1d9dcbf16a41cffbc','candidate_delivery':'dc7371513a065457af566f4b589b9ed147130d64','corrected_scanner':read(OUT/'evaluation-proposal.json')['scanner'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/name).relative_to(ROOT)):sha(OUT/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v85.json','index_sha256':sha(BASE/'evidence-v85.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(OUT/'evaluation-proposal.json'),'optimization_budget':{'planned':1,'attempted':1,'passed':1,'remaining':0,'closed':True},'regression_approved':False,'regression_observations':0,'candidate_reverted':False,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal docs binding. Product bytes remain identical to engineering-tested dc73715. Final README metadata independently built/verified; draft delivery requires actual readback. No corpus authorization is implied.'})
print('Bound 16 owning docs and unapproved regression proposal after seal 85.')
