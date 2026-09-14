"""Create and verify a complete immutable scanner checkout using COW artifacts."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
fixed=Path('/private/tmp/mcp-phase22-frozen-4145d35');revision='4145d3559c5300a5003ca8e3368c8da49fb51f91';assert not fixed.exists()
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==revision
assert not subprocess.check_output(['git','diff','HEAD'])
assert json.loads((OUT.parent/'v66-full-suite-loopback-access.json').read_text())['exit_code']==0
quality=json.loads((OUT.parent/'v66-candidate-quality/packet.json').read_text());assert quality['engineering_passed'] and quality['source']==revision
audit=json.loads((OUT.parent/'v66-candidate-quality-audit/packet.json').read_text());assert audit['source']==revision and len(audit['quality'])==12
assert json.loads((OUT/'compatibility.json').read_text())['scanner']==revision
subprocess.run(['git','worktree','add','--no-checkout','--detach',str(fixed),revision],check=True)
subprocess.run(['/bin/cp','-cR','/private/tmp/mcp-phase22-frozen-2e0efb2/artifacts',str(fixed/'artifacts')],check=True)
subprocess.run(['git','checkout','HEAD','--','.',':!artifacts'],cwd=fixed,check=True)
changed=subprocess.check_output(['git','diff','--name-only','2e0efb2',revision,'--','artifacts'],text=True).splitlines()
if changed:subprocess.run(['git','checkout','HEAD','--',*changed],cwd=fixed,check=True)
subprocess.run(['git','reset','--mixed','HEAD'],cwd=fixed,check=True)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=fixed)
env={**os.environ,'PYTHONPATH':'src:.'}
identity=json.loads(subprocess.check_output([sys.executable,'-c','import json;from scripts.phase20_measurements import scanner_identity;print(json.dumps(scanner_identity()))'],cwd=fixed,env=env,text=True))
assert identity['revision']==revision
p={'scanner':identity,'frozen_checkout':str(fixed),'tracked_clean':True,'untracked_clean':True,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'harness_and_lock_sha256':{n:hashlib.sha256((fixed/n).read_bytes()).hexdigest() for n in ['uv.lock','scripts/phase20_corpus.py','scripts/phase22_corpus.py','scripts/phase20_measurements.py','scripts/phase20_scoring.py']},'source_exposure':'All four new repositories and earlier compatibility inputs were exposed before this correction. Original four fresh gates failed at2e0efb2 and remain failed. Required local and hosted engineering has passed before this freeze; no corrected-scanner corpus observation is authorized or performed.','storage':'Complete clean Git tree with copy-on-write artifact clones; source and tests checked out at actual4145d35.','new_corpus_observations':0,'paid_calls':0}
path=OUT/'freeze.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(identity))
