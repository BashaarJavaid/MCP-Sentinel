"""Commit the ordinary correctness candidate under the existing user scope."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent; root=out.parents[3]; base=out.parent
run=lambda *args:subprocess.check_output(args,cwd=root,text=True).strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
intake=json.loads((out/'intake.json').read_text())
assert run('git','rev-parse','HEAD')==intake['baseline_delivery']
assert run('git','branch','--show-current')=='phase22/integration'
assert not run('git','diff','--cached')
files=['src/sentinel/static/typescript_path_flow.py','tests/test_typescript_classes.py']
assert set(run('git','diff','--name-only').splitlines())==set(files)
for name,digest in intake['protected_user_files_sha256'].items(): assert sha(root/name)==digest,name
labels=['v72-focused','v72-final-lint','v72-final-format','v72-final-types']
for label in labels: assert json.loads((base/(label+'.json')).read_text())['exit_code']==0,label
previous=json.loads((base/'v66-invalidation-contract/local-checks.json').read_text())['candidate_engineering_files_sha256']
current={name:sha(root/name) for name in previous}
changed={name:{'before':previous[name],'after':digest} for name,digest in current.items() if digest!=previous[name]}
assert set(changed)==set(json.loads((base/'v71-four-source-correctness/candidate-commit.json').read_text())['changes_from_prior_engineering']),set(changed)
with (out/'candidate.patch').open('x') as f:f.write(run('git','diff','HEAD')+'\n')
run('git','add','--',*files)
assert set(run('git','diff','--cached','--name-only').splitlines())==set(files)
print(run('git','commit','-m','Reject prototype-mutating TypeScript constructor parameter properties'))
head=run('git','rev-parse','HEAD')
for name,digest in current.items():assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+name],cwd=root)).hexdigest()==digest,name
record={'source':head,'parent':intake['baseline_delivery'],'recorded_at':datetime.now(timezone.utc).isoformat(),'files_sha256':{name:sha(root/name) for name in files},'candidate_engineering_files_sha256':current,'changes_from_prior_engineering':changed,'intake_sha256':sha(out/'intake.json'),'focused_checks':{label:sha(base/(label+'.json')) for label in labels},'full_engineering':'pending','corpus_observations':0,'paid_calls':0,'phase22_complete':False}
with (out/'candidate-commit.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(head)
