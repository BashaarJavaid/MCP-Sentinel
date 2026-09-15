"""Bind assessed profile and pending source-only decision after seal92."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OLD = BASE/'v63-shared-discovery-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
seal = read(BASE/'evidence-v92.json')
assert sha(BASE/seal['archive']) == seal['sha256']
save('seal-execution.json', {'command':['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python','-I',str(OUT/'seal.py')],'exit_code':0,'members':len(seal['files']),'raw_bytes':sum(r['bytes'] for r in seal['files']),'archive_sha256':seal['sha256'],'qualification':'Direct execution after writers stopped; supplemental completion receipt.'})
p = BASE/'README.md'
text = p.read_text()
assert text.count('batches 1–91') == 1
text = text.replace('batches 1–91','batches 1–92',1)
first, rest = text.split('\n',1)
block = f'''
## Parent-and-worker profile evidence seal 92

[Seal 92](evidence-v92.json) retains **{len(seal['files'])} members / {sum(r['bytes'] for r in seal['files']):,} raw bytes**,
archive SHA-256 `{seal['sha256']}`. All 91 earlier archives and every member verified.
The approved `1948bf9` sampled timeout, actual process identities and partial samples,
closed budget, complete 358-row audit, unapproved invalidation proposal, final checks
and packages, and supplemental v63 delivery/diagnostic approval receipts are preserved.
Restore after seals 1–91 in numeric order into safe separate staging; reject unsafe
paths/symlinks, verify archive/member hashes and stop on unexplained conflicts.
The v73 log correction remains preserved. Post-seal documentation and draft readback
are supplemental. **Phase 22 remains incomplete.**
'''
p.write_text(first+'\n'+block+rest)
url = 'https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/'
(OUT/'pr-body-delivery.md').write_text((OUT/'pr-body.md').read_text()+f'\n[Seal 92]({url}evidence-v92.json): {len(seal["files"])} members, SHA-256 `{seal["sha256"]}`; all 91 earlier archives verified. Final docs/packages pass with unchanged tested `1948bf9` product bytes.\n')
old = read(OLD/'documentation-binding.json')
worktrees = subprocess.check_output(['git','worktree','list','--porcelain'],text=True)
def parse(value):
    return {block.splitlines()[0].removeprefix('worktree '):next(line[5:] for line in block.splitlines() if line.startswith('HEAD ')) for block in value.strip().split('\n\n')}
actual, expected = parse(worktrees), parse(old['worktrees'])
assert set(actual) == set(expected)
for name, head in expected.items(): assert actual[name] == ('7d6e01a0e8c9e4e5f81a8fd195599dac6b7aa8ab' if name==str(ROOT) else head), name
for name, digest in old['user_files_sha256'].items(): assert sha(ROOT/name) == digest, name
review = ['assessment.json','validation.json','budget-closed.json','sample-attribution.json','source-assessment.json','frame-source-bindings.json','frame-contexts.json','compatible-reuse.json','audit.json','prior-row-preservation.json','optimization-proposal.json','summary.md','pr-body-delivery.md','final-checks.json','final-distributions.json','command-provenance.json','check-failure-assessment.json','owned-work.json','owned-final.json','seal-execution.json','execution.json','attempt.json','../v63-shared-discovery-regression/delivery-verification.json','../v63-shared-discovery-regression/diagnostic-authorization.json','../v63-shared-discovery-regression/diagnostic-consumed.json','../v63-shared-discovery-regression/diagnostic-preflight.json','../v63-shared-discovery-regression/authorize-diagnostic.py']
a = read(OUT/'assessment.json')
save('documentation-binding.json', {'recorded_at':datetime.now(timezone.utc).isoformat(),'baseline_delivery':'7d6e01a0e8c9e4e5f81a8fd195599dac6b7aa8ab','corrected_scanner':a['scanner'],'owning_docs_sha256':{n:sha(ROOT/n) for n in old['owning_docs_sha256']},'review_packet_sha256':{str((OUT/n).resolve().relative_to(ROOT)):sha(OUT/n) for n in review},'additional_normative_docs_sha256':{'docs/architecture.md':sha(ROOT/'docs/architecture.md')},'user_files_sha256':old['user_files_sha256'],'worktrees':worktrees,'evidence_seal':{'index':'artifacts/phase22/integration/evidence-v92.json','index_sha256':sha(BASE/'evidence-v92.json'),'archive_sha256':seal['sha256']},'optimization_proposal_sha256':sha(OUT/'optimization-proposal.json'),'corpus_budget':old['corpus_budget'],'profile_budget':{'attempted':1,'completed':0,'incomplete':1,'remaining':0,'closed':True},'profiles':1,'diagnostic_approved':True,'sampled_processes':[r['rule'] for r in a['sample_rows']],'samples':a['samples'],'optimization_approved':False,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'qualification':'Post-seal binding. Product/tests/workflows/lock/schema retain tested1948bf9; final README metadata rebuilt. One If invalidation-accumulator proposal is unapproved/unimplemented. Exact supplemental draft readback remains required.'})
print('Bound16 owning docs and exact unapproved invalidation proposal after seal92.')
