"""Bind sealed candidate engineering, pending evaluation and protected worktrees."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent;prior=base/'v70-uncapped-four-results'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,p):
 with (out/name).open('x') as f:json.dump(p,f,indent=2);f.write('\n')
seal=read(base/'evidence-v98.json');assert sha(base/seal['archive'])==seal['sha256']
assert read(out/'final-checks.json')['passed']
write('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(out/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after all writers stopped; supplemental completion receipt. All97priorarchives and every new member verified. Delivery helper sources were prepared before sealing.'})
p=base/'README.md';text=p.read_text();assert text.count('batches 1–97')==1
text=text.replace('batches 1–97','batches 1–98',1).replace('## Current uncapped four-repository evidence seal 97','## Historical uncapped four-repository evidence seal 97',1)
first,rest=text.split('\n',1)
block=f'''
## Current correctness-recovery evidence seal 98

[Seal 98](evidence-v98.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 97 earlier archives and every new member verified.
It retains ordinary constructor/URL recovery and the prototype-property correction,
all first failures, interrupted/cancelled initial engineering, complete `cec0322`
engineering, 407 audit rows and the unapproved 24-observation uncapped proposal.
Supplemental V70 delivery and resolved automatic-approval-review receipts remain.
Restore after seals 1–97 in numeric order into separate staging; reject unsafe
paths/symlinks, verify hashes and stop on unexplained conflicts. The historical
v73 log correction is preserved. Post-seal documentation/delivery readbacks are
supplemental. **Phase 22 remains incomplete; zero new corpus or paid calls.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (out/'pr-body-delivery.md').open('x') as f:f.write((out/'pr-body.md').read_text()+f'\n[Seal 98]({url}evidence-v98.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 97 earlier archives verified. Final documentation/package metadata passes with exact hosted `cec0322` product bytes.\n')
old=read(prior/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(s):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in s.strip().split('\n\n')}
actual,expected=parse(worktrees),parse(old['worktrees']);freeze=read(out/'freeze.json');head=freeze['scanner']['revision']
assert set(actual)==set(expected)|{freeze['frozen_checkout']}
for name,revision in expected.items():assert actual[name]==(head if name==str(root) else revision),name
assert actual[freeze['frozen_checkout']]==head
protected=read(out/'intake.json')['protected_user_files_sha256']
for name,d in protected.items():assert sha(root/name)==d,name
review=['intake.json','source-assessment.json','candidate-commit.json','candidate-delivery.json','local-checks.json','checkout-binding.json','compatibility.json','freeze.json','evaluation-proposal.json','launcher-binding.json','scoring-rubric.json','boundary-checks.json','synthetic-equivalence.json','audit.json','prior-row-preservation.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-final.json','coverage-temp-retention.json','seal-execution.json']
extra=[base/'v72-candidate-quality-audit/packet.json',base/'v72-candidate-quality/packet.json',base/'v72-production-capture-revalidation/packet.json',base/'v71-four-source-correctness/source-assessment.json',base/'v71-four-source-correctness/prototype-engineering-stop.json',base/'v71-candidate-quality/packet.json',prior/'delivery-verification.json',prior/'delivery-approval-review.json',base/'v68-invalidation-sampling/optimization-proposal.json']
paths=[out/n for n in review]+extra
write('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':freeze['scanner'],'owning_docs_sha256':{n:sha(root/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str(p.relative_to(root)):sha(p) for p in paths},'additional_normative_docs_sha256':{'docs/architecture.md':sha(root/'docs/architecture.md')},'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v98.json','index_sha256':sha(base/'evidence-v98.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(out/'evaluation-proposal.json'),'evaluation_authorization_sha256':None,'pending_optimization_proposal_sha256':sha(base/'v68-invalidation-sampling/optimization-proposal.json'),'experiment_budget':{'approved':False,'opened':False,'attempts':0,'remaining':0,'proposed':24},'current_source_input_accounting':read(out/'audit.json')['current_source_input_accounting'],'repository_gates_passed':0,'profiles_in_this_continuation':0,'optimization_approved':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding of finalcec0322engineering and a separate unapproved24-observation proposal. All407rows and original failures remain. The normal1800-second policy stays;181earlier-language observations excluded. Exact supplemental draft readback remains required.'})
print('Bound16owning docs, protected worktrees and full corrected-source review afterseal98.')
