"""Bind verified engineering and the unapproved regression after evidence seal94."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v65-if-invalidation-accumulator'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v94.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; supplemental completion receipt.'})
p=BASE/'README.md';s=p.read_text();assert s.count('batches 1–93')==1;s=s.replace('batches 1–93','batches 1–94',1);first,rest=s.split('\n',1)
block=f'''
## Verified private invalidation contract evidence seal 94

[Seal 94](evidence-v94.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 93 earlier archives and every member verified.
The explicit revision, exact candidate, source/alias proof, complete comparisons,
full local/hosted engineering at4145d35, six zero-call requests,376-row audit,
unapproved regression, final checks/packages and supplemental v65 delivery remain.
The original strict failure and both exact injected negative-control deltas remain.
Restore after seals1–93 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify all hashes and stop on unexplained conflicts. The v73 log
correction remains preserved. Post-seal documentation and draft readback are
supplemental. **Phase22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal94]({url}evidence-v94.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all93earlier archives verified. Final docs/packages pass with exact tested4145d35 product bytes.\n')
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(s):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in s.strip().split('\n\n')}
actual,expected=parse(worktrees),parse(old['worktrees']);freeze=read(OUT/'freeze.json');head=freeze['scanner']['revision']
assert set(actual)==set(expected)|{freeze['frozen_checkout']}
for n,h in expected.items():assert actual[n]==(head if n==str(ROOT) else h),n
assert actual[freeze['frozen_checkout']]==head
for n,d in old['user_files_sha256'].items():assert sha(ROOT/n)==d,n
review=['authorization.json','optimization-consumed.json','assessment.json','source-proof.json','production-domain-proof.json','equivalence.json','production-flow-equivalence.json','production-boundaries.json','report-equivalence.json','five-rule-report-equivalence.json','discovery-equivalence.json','guard-validation.json','helper-control-result.json','optimization-budget-closed.json','candidate-typescript-path-flow.py','candidate.patch','local-checks.json','compatibility.json','freeze.json','frozen-source-validation.json','audit.json','prior-row-preservation.json','evaluation-proposal.json','scoring-rubric.json','launcher-binding.json','runner-boundaries.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-initial.json','owned-final.json','seal-execution.json','checkout-binding.json','candidate-commit.json','candidate-delivery.json','../v65-if-invalidation-accumulator/delivery-verification.json','../v66-candidate-quality/packet.json','../v66-candidate-quality-audit/packet.json','../v66-production-capture-revalidation/packet.json']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':head,'corrected_scanner':freeze['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/n).resolve().relative_to(ROOT)):sha(OUT/n) for n in review},'additional_normative_docs_sha256':old['additional_normative_docs_sha256'],'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v94.json','index_sha256':sha(BASE/'evidence-v94.json'),'archive_sha256':seal['sha256']},'evaluation_proposal_sha256':sha(OUT/'evaluation-proposal.json'),'corpus_budget':{'approved':False,'attempts':0,'proposed_observations':205,'open_budget':False},'historical_corpus_budget':old['corpus_budget'],'profile_budget':{'approved':False,'attempts':0,'open_budget':False},'historical_profile_budget':old['historical_profile_budget'],'source_only_budget':read(OUT/'optimization-budget-closed.json'),'new_corpus_observations':0,'profiles':0,'optimization_attempts':1,'prospective_contract_revision_approved':True,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. One source-only attempt passed full engineering and closed. Earlier strict failure and exact two negative-control deltas remain retained. New205-observation regression is unapproved/unexecuted. Final README metadata rebuilt; exact draft readback still required.'})
print('Bound16 owning docs,376-row audit, exact frozen scanner and unapproved regression afterseal94.')
