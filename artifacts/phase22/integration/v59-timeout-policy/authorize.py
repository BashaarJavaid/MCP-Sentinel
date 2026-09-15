"""Bind the user's timeout-policy revision before editing the tested source."""
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
BASE = OUT.parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
head = 'b168738236d9f0b637fa8764f1ad0f3bbcae50d8'
assert git('rev-parse', 'HEAD') == head and git('branch', '--show-current') == 'phase22/integration'
assert not git('diff', 'HEAD') and not git('diff', '--cached')
prior = read(BASE/'v58-credential-regression/documentation-binding.json')
for name, digest in prior['user_files_sha256'].items():
    assert sha(ROOT/name) == digest and not git('ls-files', '--', name), name
for name, digest in read(BASE/'v57-credential-merge/local-checks.json')['candidate_engineering_files_sha256'].items():
    assert sha(ROOT/name) == digest, name
assert read(BASE/'v58-credential-regression/delivery-verification.json')['head'] == head
rows = {}
for line in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines():
    fields = line.strip().split(None,2)
    if len(fields)==3: rows[int(fields[0])] = (int(fields[1]),fields[2])
ancestors=set(); pid=os.getpid()
while pid in rows and pid not in ancestors:
    ancestors.add(pid); pid=rows[pid][0]
owned=[pid for pid,(_,command) in rows.items() if pid not in ancestors and any(marker in command for marker in ['v59-','v58-','v57-','phase22-check.py'])]
assert not owned, owned
for marker in ['label=com.securemcp.sentinel=true','name=sentinel']:
    assert not subprocess.check_output(['docker','ps','-aq','--filter',marker])
for name in ['src/sentinel/static/engine.py','tests/test_static_engine.py']:
    with (OUT/('baseline-'+Path(name).name)).open('xb') as stream: stream.write((ROOT/name).read_bytes())
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'decision':'yes do that.','decision_context':'After asking why scan duration mattered, the user accepted revising the timeout policy and evaluating completed results under a longer supported limit. This prospectively revises the timing constraint; it does not accept earlier failed measurements or Phase 22.','initial_deadline_seconds':1800,'deadline_choice':'30-minute finite limit selected and stated as the initial implementation assumption; an optional preference question offered 15/30/60 minutes.','normal_target_seconds':120,'starting_delivery':head,'tested_scanner':'dc7371513a065457af566f4b589b9ed147130d64','source_scope':'Change the single shared static timeout constant and its existing boundary tests, current documentation, required ordinary engineering, frozen-source proof and exact new regression preparation. Detector logic, configuration, worker count, reports, cleanup and earlier evidence remain unchanged.','superseded_unexecuted_diagnostic':{'path':'artifacts/phase22/integration/v58-credential-regression/diagnostic-proposal.json','sha256':sha(BASE/'v58-credential-regression/diagnostic-proposal.json'),'approved':False,'executed':False},'user_files_sha256':prior['user_files_sha256'],'baseline_files_sha256':{n:sha(ROOT/n) for n in ['src/sentinel/static/engine.py','tests/test_static_engine.py']},'worktrees':git('worktree','list','--porcelain'),'owned_processes':owned,'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False,'measurement_boundary':'Prepare and deliver the exact frozen scanner/runner/order/bounds before requesting a new numerical evaluation authorization, as required by the original Phase 22 prompt. No old closed budget is reused.'}
with (OUT/'authorization.json').open('x') as stream: json.dump(record,stream,indent=2); stream.write('\n')
print('Bound authorized timeout-policy revision; source intact and no evaluation started.')
