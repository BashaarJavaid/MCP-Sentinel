"""Stage only approved-for-preparation immutable sources; no numerical authorization."""
import hashlib,importlib.util,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
p=read(OUT/'evaluation-proposal.json');frozen=Path(p['frozen_checkout']);manifest=read(ROOT/p['manifest']['path'])
paths={p['manifest']['path']}|{x['path'] for x in manifest['packet']}|{s['archive']['path'] for s in manifest['snapshots']}
for name in sorted(paths):
 relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts and name.startswith('artifacts/phase22/')
 source=ROOT/name;dest=frozen/name;assert sha(source)==p['files_sha256'][name]
 assert not source.is_symlink() and not dest.is_symlink() and not any(q.is_symlink() for q in dest.parents)
 if dest.exists():assert sha(dest)==sha(source),name
 else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
os.chdir(frozen);sys.path[:0]=[str(frozen/'src'),str(frozen)]
spec=importlib.util.spec_from_file_location('unseen_corpus',OUT/'corpus.py');c=importlib.util.module_from_spec(spec);sys.modules['unseen_corpus']=c;spec.loader.exec_module(c)
m=c.validate(frozen/p['manifest']['path']);assert len(m.inputs)==6
from scripts.phase20_measurements import scanner_identity
assert scanner_identity()==p['scanner']
commands=[[sys.executable,'-I',str(OUT/'evaluate.py'),'check'],[sys.executable,'-I',str(OUT/'launch.py'),'check']]
for command in commands:subprocess.run(command,check=True,cwd=frozen)
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'source-freeze-authorization.json').exists() and not (OUT/'execution-consumed.json').exists() and not (OUT.parent/'v78-unseen-results').exists()
with (OUT/'staging-and-boundary-verification.json').open('x') as f:json.dump({'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'scanner':p['scanner'],'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'staged_files_sha256':{n:sha(frozen/n) for n in sorted(paths)},'commands':commands,'approval_absent_rejected_before_launch':True,'corpus_observations':0,'paid_calls':0,'target_execution':False},f,indent=2);f.write('\n')
print('Exact frozen staging/source validation and missing numerical approval rejection pass; zero observations.')
