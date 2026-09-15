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
assert sha(ASSETS/'diagnostic-proposal.json') == '9c20d0ce8365dc18188854c8417598ab8936243b5405e179d887df3479f022fb'
assert not (ASSETS/'diagnostic-authorization.json').exists()
assert not (ASSETS/'diagnostic-consumed.json').exists()
assert not (ASSETS.parent/'v68-invalidation-sampling').exists()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == 'c60b7a858497c355326044b959d9f6ad8d755a80'
assert not subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT)
binding = read(ASSETS/'documentation-binding.json')
delivery = read(ASSETS/'delivery-verification.json')
assert delivery['passed'] and delivery['head'] == 'c60b7a858497c355326044b959d9f6ad8d755a80' and delivery['diagnostic_proposal_sha256'] == sha(ASSETS/'diagnostic-proposal.json')
remote = json.loads(subprocess.check_output(['gh','pr','view','37','--json','state,isDraft,headRefName,headRefOid,baseRefName,title,body'],cwd=ROOT,text=True))
assert remote['state'] == 'OPEN' and remote['isDraft'] and remote['headRefName'] == 'phase22/integration' and remote['baseRefName'] == 'phase22/description-poisoning'
assert remote['headRefOid'] == 'c60b7a858497c355326044b959d9f6ad8d755a80'
assert remote['title'] == 'Phase 22: invalidation regression timed out; diagnostic pending' and remote['body'] == (ASSETS/'pr-body-delivery.md').read_text()
assert subprocess.check_output(['gh','api','repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration','--jq','.commit.sha'],cwd=ROOT,text=True).strip() == remote['headRefOid']
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=main)
for name,digest in read(ASSETS.parent/'v66-invalidation-contract/local-checks.json')['candidate_engineering_files_sha256'].items():
    if name != 'README.md': assert sha(ROOT/name) == digest, name
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
markers = ['v68-', 'v67-', 'v66-', 'v65-', 'v64-', 'v63-', 'v62-', 'v61-', 'v60-', 'v59-', 'v58-', 'v57-', 'v56-', 'v55-', 'v54-', 'v53-', 'v52-', 'v51-', 'v50-', 'v49-', 'v48-', 'v47-', 'v46-', 'v45-', 'v44-', 'v43-', 'phase22-check.py', 'mcp-phase22-four-fresh-']
assert not [pid for pid, (_, command) in rows.items() if pid not in ancestors and any(m in command for m in markers)]
for selector in ['label=com.securemcp.sentinel=true', 'name=sentinel']:
    assert not subprocess.check_output(['docker', 'ps', '-aq', '--filter', selector])
spec = importlib.util.spec_from_file_location('diagnostic', ASSETS/'diagnostic.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert runner.verify()[0] == proposal
assert not subprocess.check_output(['git', 'status', '--porcelain'])
receipt = {'approved': True, 'user_decision': 'approved', 'recorded_at': datetime.now(timezone.utc).isoformat(),
    'decision_context': 'User approved the exact one parent-and-worker CPU-sampled FAF rules-only diagnostic delivered at c60b7a8, frozen scanner4145d35, 1800-second whole-input maximum and15-second cleanup, at most one parent and four existing workers. Zero optimization, uninstrumented observations, retries, comparators, paid calls, hosted dispatches or target execution. All earlier budgets stay closed. Each attributed process requires verified actual source identity. This is neither technical acceptance nor final closeout acceptance.',
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
