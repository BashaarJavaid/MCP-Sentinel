"""Commit the authorized shared-deadline revision after focused verification."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
BASE=OUT.parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
auth=read(OUT/'authorization.json')
assert git('rev-parse','HEAD')==auth['starting_delivery']
assert git('branch','--show-current')=='phase22/integration' and not git('diff','--cached')
allowed=['src/sentinel/static/engine.py','tests/test_static_engine.py','CHANGELOG.md','README.md','ARCHITECTURE.md','docs/architecture.md','docs/phase22-timeout-policy.md']
assert set(git('diff','--name-only').splitlines())==set(allowed)
for label in ['affected','lint','format','mypy','source-proof']:
    assert read(BASE/('v59-'+label+'.json'))['exit_code']==0,label
proof=read(OUT/'source-proof.json')
assert proof['passed'] and proof['new_deadline_seconds']==1800
assert sha(ROOT/'src/sentinel/static/engine.py')==proof['changed_engineering_files']['src/sentinel/static/engine.py']['current']
for name,digest in auth['user_files_sha256'].items():
    assert sha(ROOT/name)==digest and not git('ls-files','--',name)
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'authorization_sha256':sha(OUT/'authorization.json'),'source_proof_sha256':sha(OUT/'source-proof.json'),'files_sha256':{n:sha(ROOT/n) for n in allowed},'scope':'One shared timeout constant changes from 300 to 1800 seconds, with existing boundary tests and active documentation updated. Detector logic and cleanup unchanged. Full local and hosted engineering pending.','corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'source-checkpoint.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
selected=[str((OUT/n).relative_to(ROOT)) for n in ['authorization.json','source-checkpoint.json']]
subprocess.run(['git','add','--',*allowed],cwd=ROOT,check=True)
subprocess.run(['git','add','-f','--',*selected],cwd=ROOT,check=True)
assert set(git('diff','--cached','--name-only').splitlines())==set(allowed+selected)
subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','Allow a thirty-minute shared static analysis deadline'],cwd=ROOT,check=True)
assert not git('diff','HEAD')
with (OUT/'candidate-commit.json').open('x') as stream:json.dump({'source':git('rev-parse','HEAD'),'parent':auth['starting_delivery'],'files_sha256':{n:sha(ROOT/n) for n in allowed+selected},'full_engineering':'pending','corpus_observations':0,'profiles':0,'paid_calls':0},stream,indent=2);stream.write('\n')
print(git('rev-parse','HEAD'))
