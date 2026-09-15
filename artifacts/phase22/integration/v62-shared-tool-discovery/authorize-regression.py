"""Record the user's exact approval after read-only launch preflight."""
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
proposal = read(ASSETS/'evaluation-proposal.json')
binding = read(ASSETS/'launcher-binding.json')
assert sha(ASSETS/'evaluation-proposal.json') == 'c1407c3a8cb7ee78ebf4346ab1e36e112dcb1e830e4c8270c563d780f2861a9b'
assert sha(ASSETS/'launcher-binding.json') == '00b05ff30f0b2076bce8cb9a5df13a65edc6e2a5bfc7dbca09bf40846f6f4297'
assert not (ASSETS/'evaluation-authorization.json').exists()
assert not (ASSETS/'execution-consumed.json').exists()
assert not (ASSETS.parent/'v63-shared-discovery-regression').exists()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == 'c7b20a30f2a061c00eb8a6ffcc1413a211c01fff'
assert not subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT)
delivery = read(ASSETS/'delivery-verification.json')
assert delivery['passed'] and delivery['head'] == 'c7b20a30f2a061c00eb8a6ffcc1413a211c01fff' and delivery['evaluation_proposal_sha256'] == sha(ASSETS/'evaluation-proposal.json')
for field in ['owning_docs_sha256', 'review_packet_sha256', 'user_files_sha256', 'additional_normative_docs_sha256']:
    for name, digest in read(ASSETS/'documentation-binding.json')[field].items():
        assert sha(ROOT/name) == digest, name
rows = {}
for line in subprocess.check_output(['ps', '-axo', 'pid=,ppid=,command='], text=True).splitlines():
    parts = line.strip().split(None, 2)
    if len(parts) == 3:
        rows[int(parts[0])] = (int(parts[1]), parts[2])
ancestors = set()
pid = os.getpid()
while pid in rows and pid not in ancestors:
    ancestors.add(pid)
    pid = rows[pid][0]
markers = ['v63-', 'v62-', 'v61-', 'v60-', 'v59-', 'v58-', 'v57-', 'v56-', 'v55-', 'v54-', 'v53-', 'v52-', 'v51-', 'v50-', 'v49-', 'v48-', 'v47-', 'v45-', 'v46-', 'v43-', 'v44-', 'phase22-check.py', 'mcp-phase22-four-fresh-', 'v42-', 'v41-', 'v40-fresh-v7/', 'v38-guard-regression/']
owned = [pid for pid, (_, command) in rows.items() if pid not in ancestors and any(m in command for m in markers)]
assert not owned, owned
for args in [['label=com.securemcp.sentinel=true'], ['name=sentinel']]:
    assert not subprocess.check_output(['docker', 'ps', '-aq', '--filter', *args])
os.chdir(proposal['frozen_checkout'])
assert not subprocess.check_output(['git', 'status', '--porcelain'])
sys.path[:0] = [str(Path.cwd()/'src'), str(Path.cwd())]
from scripts.phase20_measurements import scanner_identity
import sentinel
assert scanner_identity() == proposal['scanner']
assert sha(Path.cwd()/'uv.lock') == proposal['lock_sha256']
assert Path(sentinel.__file__).resolve().is_relative_to(Path.cwd()/'src')
for name, digest in proposal['files_sha256'].items():
    assert sha(ROOT/name) == digest, name
receipt = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'approved': True,
           'user_decision': 'approved', 'decision_context': 'User approved the exact 205-observation proposal presented after verified draft delivery c7b20a3: 30 minutes per input, 15-second cleanup and 104h35m worst-case sequence cap; zero retries/profiles/comparators/target executions/paid calls. This is evaluation approval only; technical acceptance remains separate.',
           'proposal_sha256': sha(ASSETS/'evaluation-proposal.json'), 'launcher_binding_sha256': sha(ASSETS/'launcher-binding.json'),
           'scanner': proposal['scanner'], 'bounds': proposal['bounds'], 'order': proposal['order'],
           'rubric_sha256': sha(ASSETS/'scoring-rubric.json'), 'source_recovery_authorization_sha256': sha(ASSETS/'authorization.json'),
           'delivery_verification_sha256': sha(ASSETS/'delivery-verification.json'),
           'technical_acceptance_received': False, 'phase22_complete': False}
with (ASSETS/'evaluation-authorization.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
spec = importlib.util.spec_from_file_location('approved_launcher', ASSETS/'launch.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)
assert launcher.preflight() == proposal
with (ASSETS/'execution-preflight.json').open('x') as stream:
    json.dump({'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'approval_sha256': sha(ASSETS/'evaluation-authorization.json'),
               'scanner': proposal['scanner'], 'import_path': sentinel.__file__, 'python': sys.version,
               'versions': {n: importlib.metadata.version(n) for n in ['semgrep', 'mcp', 'pytest', 'pydantic']},
               'owned_processes': [], 'owned_containers': [], 'frozen_checkout_clean': True,
               'paid_calls': 0, 'observations_started': 0, 'launch_token_consumed': False}, stream, indent=2)
    stream.write('\n')
print('Exact 205-observation approval recorded; frozen source and one-use launcher preflight passed. Zero observations started.')
