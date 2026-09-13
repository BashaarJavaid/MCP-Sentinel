"""Bind the verified candidate proposal and owning documentation after seal80."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (out/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
seal=read(base/'evidence-v80.json')
assert sha(base/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','artifacts/phase22/integration/v52-merge-fastpath/seal.py'],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Executed directly after all writers stopped. No active wrapper log included; completion receipt is supplemental.'})
path=base/'README.md';text=path.read_text().replace('batches 1–79','batches 1–80',1);first,rest=text.split('\n',1)
block=f'''\n## Equal-value fast-path candidate evidence seal 80

[Seal 80](evidence-v80.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 79 prior archives and every member
verified. This retains the approved source-only equal-value fast-path attempt, baseline,
synthetic equivalence and avoided-work checks, local/hosted engineering, source-bound
packages and zero-call replays, all 271 audit rows, the unapproved native proposal
and the initial formatting failure with its correction. Supplemental v51 delivery receipts
are included. Restore after seals 1–79 in numeric order into safe separate staging;
reject unsafe paths/symlinks, verify archive/member hashes, and stop on unexplained
conflicts. The prior v73 log correction remains preserved. Post-seal documentation
and delivery readback are supplemental. **Phase 22 remains incomplete.**
'''
path.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
body=(out/'pr-body.md').read_text()+f'\n[Seal 80]({url}evidence-v80.json) retains {len(seal["files"])} members / {sum(r["bytes"] for r in seal["files"]):,} raw bytes; SHA-256 `{seal["sha256"]}`. All 79 earlier archives and every member verified. Final docs/package checks pass with code identical to hosteda36f696; post-seal documentation/readback are supplemental.\n'
(out/'pr-body-delivery.md').write_text(body)
old=read(base/'v51-faf-bound-sampling/documentation-binding.json')
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in value.strip().split('\n\n')}
for name,head in parse(old['worktrees']).items():assert parse(worktrees)[name]==('a36f696c504e4e8d1f90de5dc84e8942d06316ca' if name==str(root) else head),name
for name,digest in old['user_files_sha256'].items():assert sha(root/name)==digest,name
review=['optimization-budget-closed.json','authorization.json','source-checkpoint.json','source-recovery-assessment.json','synthetic-validation.json','baseline-merge.py','audit.json','evaluation-proposal.json','scoring-rubric.json','launcher-binding.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','local-checks.json','freeze.json','frozen-source-validation.json','compatibility.json','command-provenance.json','check-failure-assessment.json','owned-work.json','prior-row-preservation.json','seal-execution.json','checkout-binding.json','candidate-commit.json','evaluate.py','launch.py','prepare-regression.py','check-synthetic.py']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'a36f696c504e4e8d1f90de5dc84e8942d06316ca','corrected_scanner':read(out/'freeze.json')['scanner'],'owning_docs_sha256':{name:sha(root/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str((out/name).relative_to(root)):sha(out/name) for name in review},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v80.json','index_sha256':sha(base/'evidence-v80.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(out/'evaluation-proposal.json'),'launcher_binding_sha256':sha(out/'launcher-binding.json'),'optimization_attempts':1,'native_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/test/schema/lock/workflow bytes remain engineering-testeda36f696; final README package metadata separately verified. Actual draft delivery remains a separate supplemental readback.'})
print('Bound16owning docs and exact unapproved native proposal after seal80.')
