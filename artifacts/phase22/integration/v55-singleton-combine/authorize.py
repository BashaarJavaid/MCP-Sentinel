"""Bind the single approved source-only attempt before any product edit."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

out = Path(__file__).resolve().parent
old = out.parent / 'v54-faf-fastpath-sampling'
proposal = old / 'optimization-proposal.json'
source = Path('src/sentinel/static/path_flow.py')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(proposal) == '94c740f84b0e3478ad75124b426ed9e914ff8789f076733dba21e5df6c0f9a81'
assert sha(source) == '7db58122b8b5dd11e20e2624d2dada031357fc8393e03e973c2bf8a2c26fd80d'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert head == '029bef12f71fd507be168fc7731b3b63d20b3ae5'
assert not subprocess.check_output(['git', 'diff', 'HEAD'])
binding = json.loads((old / 'documentation-binding.json').read_text())
for name, expected in binding['user_files_sha256'].items():
    assert sha(Path(name)) == expected, name
with (out / 'baseline-path-flow.py').open('xb') as stream:
    stream.write(source.read_bytes())
receipt = {
    'decision': 'approved.',
    'interpretation': 'Approval of the exact single source-only singleton cache bypass delivered at029bef1; no corpus/profile/paid/acceptance approval.',
    'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'proposal': str(proposal), 'proposal_sha256': sha(proposal),
    'starting_delivery': head, 'baseline_source_sha256': sha(source),
    'bounds': json.loads(proposal.read_text())['bounds'],
    'user_files_sha256': binding['user_files_sha256'],
    'technical_acceptance_received': False, 'phase22_complete': False,
}
with (out / 'authorization.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print('One source-only attempt authorized; exact baseline preserved.')
