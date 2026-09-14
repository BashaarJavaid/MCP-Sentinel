"""Bind the exact approved discovery-reuse attempt before product edits."""
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
head = '637a25cbb5f5bc6fcf8b3a7b30b4274aa8ea44fb'
assert git('rev-parse', 'HEAD') == head
assert git('branch', '--show-current') == 'phase22/integration'
assert not git('diff', 'HEAD') and not git('diff', '--cached')
proposal_path = BASE / 'v61-faf-long-timeout-sampling/optimization-proposal.json'
proposal = json.loads(proposal_path.read_text())
assert sha(proposal_path) == '2f32e71cf4a90b43c33cdea253cdffac1296ab9308086c352c90bbcf6e75619c'
intake = json.loads((BASE / 'shared-discovery-intake-20260914/intake.json').read_text())
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
    'decision_context': 'The user approved the immediately preceding exact one-attempt discovery-reuse proposal, with full synthetic/engineering verification and zero corpus/profile/paid calls; the 1800-second deadline is unchanged.',
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
print('Exact discovery-reuse approval recorded; ten source/test baselines preserved.')
