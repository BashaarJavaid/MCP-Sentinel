"""Bind failed strict-equivalence evidence and the prospective decision after seal93."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent;OLD=BASE/'v64-shared-discovery-sampling'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v93.json');assert sha(BASE/seal['archive'])==seal['sha256']
save('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; supplemental completion receipt.'})
p=BASE/'README.md';s=p.read_text();assert s.count('batches 1–92')==1;s=s.replace('batches 1–92','batches 1–93',1);first,rest=s.split('\n',1)
block=f'''
## Failed If accumulator attempt evidence seal 93

[Seal 93](evidence-v93.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 92 earlier archives and every member verified.
The approved candidate,256ordinary comparisons, two failed adversarial controls,
helper correction, exact1948bf9 restoration,365-row audit, unapproved explicit
contract revision, final checks/packages and supplemental v64 delivery are preserved.
Restore after seals1–92 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal93]({url}evidence-v93.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all92earlier archives verified. Final docs/packages pass with exact restored tested1948bf9 product bytes.\n')
old=read(OLD/'documentation-binding.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(s):return {b.splitlines()[0].removeprefix('worktree '):next(l[5:] for l in b.splitlines() if l.startswith('HEAD ')) for b in s.strip().split('\n\n')}
actual,expected=parse(worktrees),parse(old['worktrees']);assert set(actual)==set(expected)
for n,h in expected.items():assert actual[n]==('0f36867a037dbb13dc19e504b9ebceab2b75b407' if n==str(ROOT) else h),n
for n,d in old['user_files_sha256'].items():assert sha(ROOT/n)==d,n
review=['authorization.json','optimization-consumed.json','assessment.json','equivalence.json','restoration.json','optimization-budget-closed.json','candidate-typescript-path-flow.py','candidate.patch','compatible-reuse.json','audit.json','prior-row-preservation.json','optimization-proposal.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-initial.json','owned-final.json','seal-execution.json','../v64-shared-discovery-sampling/delivery-verification.json','../v64-shared-discovery-sampling/metadata-response.json']
save('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'0f36867a037dbb13dc19e504b9ebceab2b75b407','corrected_scanner':read(OUT/'assessment.json')['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/n).resolve().relative_to(ROOT)):sha(OUT/n) for n in review},'additional_normative_docs_sha256':old['additional_normative_docs_sha256'],'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v93.json','index_sha256':sha(BASE/'evidence-v93.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'corpus_budget':old['corpus_budget'],'historical_profile_budget':old['profile_budget'],'source_only_budget':read(OUT/'optimization-budget-closed.json'),'new_corpus_observations':0,'profiles':0,'optimization_attempts':1,'prospective_contract_revision_approved':False,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. One failed source-only attempt closed and exact1948bf9 restored; no new corpus/profile run. Existing native/profile budgets stay closed. Prospective domain revision is unapproved. Final README metadata rebuilt; exact draft readback still required.'})
print('Bound16owning docs,365-row failed attempt and exact unapproved contract revision afterseal93.')
