"""Bind sealed technical review to protected files and the existing draft destination."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
seal=read(BASE/'evidence-v99.json');assert sha(BASE/seal['archive'])==seal['sha256'] and read(OUT/'final-checks.json')['passed']
assert read(OUT/'acceptance-proposal.json')['technical_acceptance_received'] is False
intake=read(BASE/'v73-corrected-regression-intake.json');worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True);assert worktrees==intake['worktrees']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==intake['head']
write('seal-execution.json',{'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; all98prior archives and every new member verified. Supplemental receipt outside its own seal.'})
p=BASE/'README.md';text=p.read_text();assert text.count('batches 1–98')==1;text=text.replace('batches 1–98','batches 1–99',1).replace('## Current correctness-recovery evidence seal 98','## Historical correctness-recovery evidence seal 98',1)
first,rest=text.split('\n',1)
block=f'''\n## Current technical-review evidence seal 99

[Seal 99](evidence-v99.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**;
archive SHA-256 `{seal['sha256']}`. All 98 prior archives and every new member were verified.
It includes both approved current-source runs (24 four-source + 181 compatibility observations),
95 equal ordered pairs, complete source assessments, exact approvals/closed budgets, all initial
and corrected helpers, the complete 422-row audit and the explicit technical acceptance proposal.
Ordinary 1,800-second FAF completion remains unestablished. Historical failures and scope limits
are preserved; no human technical acceptance has been received.

Restore after seals 1–98 in numeric order into separate staging, rejecting unsafe paths/symlinks,
checking every member hash and stopping on unexplained conflicts. Post-seal documentation and
actual draft delivery receipts are supplemental. **Phase 22 remains incomplete; zero new paid calls.**
'''
p.write_text(first+'\n'+block+rest)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
with (OUT/'pr-body-delivery.md').open('x') as f:f.write((OUT/'pr-body.md').read_text()+f'\n[Seal 99]({url}evidence-v99.json): {len(seal["files"])} members; SHA-256 `{seal["sha256"]}`. All 98 prior archives and every new member verified.\n')
old=read(BASE/'v72-prototype-property-correction/documentation-binding.json');protected=intake['protected_user_files_sha256'];assert len(protected)==10
for name,d in protected.items():assert sha(ROOT/name)==d,name
review=['audit.json','summary.md','acceptance-limits.md','acceptance-proposal.json','prior-row-preservation.json','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-final.json','status.md','pr-body-delivery.md','seal-execution.json']
extra=[BASE/'v73-corrected-four-results/summary.md',BASE/'v73-corrected-four-results/final-assessment/assessment.json',BASE/'v73-corrected-four-results/completion-verification.json',BASE/'v73-corrected-four-results/execution.json',BASE/'v75-prior-language-results/final-assessment/assessment.json',BASE/'v75-prior-language-results/completion-verification.json',BASE/'v75-prior-language-results/execution.json',BASE/'v74-prior-language-preparation/evaluation-proposal.json',BASE/'v74-prior-language-preparation/evaluation-authorization.json',BASE/'v72-prototype-property-correction/evaluation-authorization.json',BASE/'v72-prototype-property-correction/delivery-verification.json']
paths=[OUT/name for name in review]+extra
write('documentation-binding.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':intake['head'],'corrected_scanner':read(OUT/'audit.json')['scanner_identity'],'owning_docs_sha256':{name:sha(ROOT/name) for name in old['owning_docs_sha256']},'review_packet_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'additional_normative_docs_sha256':old['additional_normative_docs_sha256'],'user_files_sha256':protected,'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v99.json','index_sha256':sha(BASE/'evidence-v99.json'),'archive_sha256':seal['sha256']},'acceptance_proposal_sha256':sha(OUT/'acceptance-proposal.json'),'pending_optimization_proposal_sha256':sha(BASE/'v68-invalidation-sampling/optimization-proposal.json'),'current_source_input_accounting':read(OUT/'audit.json')['current_source_input_accounting'],'repository_gates_passed':4,'profiles_in_this_continuation':0,'optimization_approved':False,'optimization_attempts':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding of final review to current source and protected worktrees. Exact existing-draft delivery and separate human technical acceptance remain required.'})
print('Bound complete technical review,16owning docs and10protected user documents afterseal99.')
