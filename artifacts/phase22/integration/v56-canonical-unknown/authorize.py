"""Bind the single approved source-only attempt before any product edit."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

out = Path(__file__).resolve().parent
old = out.parent / 'v55-singleton-combine'
proposal = old / 'optimization-proposal.json'
source = Path('src/sentinel/static/path_flow.py')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(proposal) == '2ff8d58ed4b5f082ffffc6f05fd31ada841dce7cf2bd165347dc627d251f77b9'
assert sha(source) == '7db58122b8b5dd11e20e2624d2dada031357fc8393e03e973c2bf8a2c26fd80d'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert head == '8df485e7e2dfbea964f8b71db39403f8f3ce17ad'
assert not subprocess.check_output(['git', 'diff', 'HEAD'])
binding = json.loads((old / 'documentation-binding.json').read_text())
for name, expected in binding['user_files_sha256'].items():
    assert sha(Path(name)) == expected, name
with (out / 'baseline-path-flow.py').open('xb') as stream:
    stream.write(source.read_bytes())
receipt = {
    'decision': 'approved',
    'interpretation': 'Approval of the exact single source-only canonical UNKNOWN_VALUE cache bypass delivered at8df485e; no corpus/profile/paid/acceptance approval.',
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
