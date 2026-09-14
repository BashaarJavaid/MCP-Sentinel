"""Bind the exact approved If invalidation-accumulator attempt before product edits."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
BASE = OUT.parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
head = 'f5f1faa706969d4581cc32eb040fdf28884287c8'
assert git('rev-parse', 'HEAD') == head
assert git('branch', '--show-current') == 'phase22/integration'
assert not git('diff', 'HEAD') and not git('diff', '--cached')
proposal_path = BASE / 'v65-if-invalidation-accumulator/optimization-proposal.json'
proposal = json.loads(proposal_path.read_text())
assert sha(proposal_path) == '9e3d3691a0c7efa584d7cfcab24a5ad4cc2ab6b89aebaea7ee699840356650a7'
intake = json.loads((BASE / 'v65-if-invalidation-accumulator/documentation-binding.json').read_text())
for field in ['owning_docs_sha256','review_packet_sha256','additional_normative_docs_sha256']:
    for name,digest in intake[field].items(): assert sha(ROOT/name)==digest,name
remote=json.loads(subprocess.check_output(['gh','pr','view','37','--json','state,isDraft,headRefOid,headRefName,baseRefName,title,body'],cwd=ROOT,text=True))
assert remote['state']=='OPEN' and remote['isDraft'] and remote['headRefOid']==head and remote['headRefName']=='phase22/integration' and remote['baseRefName']=='phase22/description-poisoning'
assert remote['title']=='Phase 22: invalidation attempt failed; contract revision pending' and remote['body']==(BASE/'v65-if-invalidation-accumulator/pr-body-delivery.md').read_text()
assert subprocess.check_output(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha'],cwd=ROOT,text=True).strip()==head
main=Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()=='4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=proposal['frozen_checkout'])
for name,digest in json.loads((BASE/'v62-shared-tool-discovery/local-checks.json').read_text())['candidate_engineering_files_sha256'].items():assert sha(ROOT/name)==digest,name
for name, digest in intake['user_files_sha256'].items():
    assert sha(ROOT / name) == digest and not git('ls-files', '--', name), name
for name, digest in proposal['source_files_sha256'].items():
    assert sha(ROOT / name) == digest, name
    destination = OUT / 'baseline' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write((ROOT / name).read_bytes())
record = {
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'decision': 'approved',
    'prospective_contract_revision': proposal['prospective_contract_revision'],
    'prior_strict_failure_retained': True,
    'decision_context': 'The user explicitly approved the private-interpreter mutation-domain contract revision and only the two named injected negative-control classifications in the immediately preceding exact one-attempt If invalidation-accumulator proposal, with full synthetic/engineering verification and zero corpus/profile/paid calls; the 1800-second deadline is unchanged.',
    'proposal': str(proposal_path.relative_to(ROOT)),
    'proposal_sha256': sha(proposal_path), 'starting_delivery': head,
    'scanner': proposal['scanner'], 'lock_sha256': sha(ROOT / 'uv.lock'),
    'baseline_files_sha256': proposal['source_files_sha256'],
    'bounds': proposal['bounds'], 'user_files_sha256': intake['user_files_sha256'],
    'worktrees': git('worktree', 'list', '--porcelain'),
    'verification': proposal['verification'],
    'technical_acceptance_received': False, 'phase22_complete': False,
}
with (OUT / 'authorization.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print('Exact If invalidation-accumulator approval recorded; source/test baselines preserved.')
