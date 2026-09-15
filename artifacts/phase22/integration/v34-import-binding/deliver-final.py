"""Deliver only verified owning docs and evidence to the existing authorized draft."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
run=lambda args:subprocess.run(args,cwd=ROOT,check=True)
b=json.loads((OUT/'documentation-binding.json').read_text())
assert not subprocess.check_output(['git','diff','--cached'])
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='phase22/integration'
for n,d in b['owning_docs_sha256'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==d,n
paths=list(b['owning_docs_sha256'])
run(['git','add','--',*paths])
extra=[str(p.relative_to(ROOT)) for p in [BASE/'evidence-v61.json',BASE/'evidence-v61.tar.gz',OUT/'documentation-binding.json',OUT/'post-seal-binding-correction.json',OUT/'bind-delivery-final.py',OUT/'deliver-final.py']]
run(['git','add','-f','--',*extra])
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths+extra)
run(['git','commit','-m','Verify Phase 22 prepared-request correction and propose exact regression [skip ci]'])
run(['git','push','origin','phase22/integration'])
run(['gh','pr','edit','37','--body-file',str(OUT/'pr-body.md')])
run([sys.executable,str(OUT/'verify-delivery.py')])
print('Authorized draft delivery and exact remote readback complete; no evaluation dispatch.')
