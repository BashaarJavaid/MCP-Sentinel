"""Record the user's exact single-profile approval without running an input."""
import hashlib
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
proposal = read(ASSETS/'diagnostic-proposal.json')
assert sha(ASSETS/'diagnostic-proposal.json') == '1d29e88e926c574cb0dbfff32108b4b961966bebe259dc75e53cf2ee776b175b'
assert not (ASSETS/'diagnostic-authorization.json').exists()
assert not (ASSETS/'diagnostic-consumed.json').exists()
assert not (ASSETS.parent/'v51-faf-bound-sampling').exists()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == 'cd5e9aea889053cc5ba9ea25997b273805635241'
assert not subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT)
binding = read(ASSETS/'documentation-binding.json')
for field in ['owning_docs_sha256', 'review_packet_sha256', 'user_files_sha256']:
    for name, digest in binding[field].items():
        assert sha(ROOT/name) == digest, name
rows = {}
for line in subprocess.check_output(['ps', '-axo', 'pid=,ppid=,command='], text=True).splitlines():
    fields = line.strip().split(None, 2)
    if len(fields) == 3:
        rows[int(fields[0])] = (int(fields[1]), fields[2])
ancestors = set()
pid = os.getpid()
while pid in rows and pid not in ancestors:
    ancestors.add(pid)
    pid = rows[pid][0]
markers = ['v51-', 'v50-', 'v49-', 'v48-', 'v47-', 'v46-', 'v45-', 'v44-', 'v43-', 'phase22-check.py', 'mcp-phase22-four-fresh-']
assert not [pid for pid, (_, command) in rows.items() if pid not in ancestors and any(m in command for m in markers)]
for selector in ['label=com.securemcp.sentinel=true', 'name=sentinel']:
    assert not subprocess.check_output(['docker', 'ps', '-aq', '--filter', selector])
spec = importlib.util.spec_from_file_location('diagnostic', ASSETS/'diagnostic.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert runner.verify()[0] == proposal
assert not subprocess.check_output(['git', 'status', '--porcelain'])
receipt = {'approved': True, 'user_decision': 'approved', 'recorded_at': datetime.now(timezone.utc).isoformat(),
    'decision_context': 'User approved the exact single CPU-sampled FAF rules-only diagnostic delivered atcd5e9ae, with300-second whole-input maximum,15-second cleanup,zero optimization/retries/comparators/paid calls/target execution. The closed205-observation budget and invalid interrupted profile remain closed. This authorizes only the corrected one-use sampler with actual worker identity checks.',
    'proposal_sha256': sha(ASSETS/'diagnostic-proposal.json'), 'scanner': proposal['scanner'], 'bounds': proposal['bounds'],
    'delivery_verification_sha256': sha(ASSETS/'delivery-verification.json'), 'technical_acceptance_received': False, 'phase22_complete': False}
with (ASSETS/'diagnostic-authorization.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
assert runner.approved()[0] == proposal
with (ASSETS/'diagnostic-preflight.json').open('x') as stream:
    json.dump({'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'approval_sha256': sha(ASSETS/'diagnostic-authorization.json'),
               'frozen_checkout_clean': True, 'owned_processes': [], 'owned_containers': [], 'input_executions': 0, 'paid_calls': 0}, stream, indent=2)
    stream.write('\n')
print('Single-profile approval recorded; frozen source, sampler, cleanup and one-use bindings verified. No input started.')
