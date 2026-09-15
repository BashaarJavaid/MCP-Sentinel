"""Commit only the authorized source candidate, guard and change record."""
import hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *a:subprocess.check_output(a,cwd=ROOT,text=True).strip()
old='f5f1faa706969d4581cc32eb040fdf28884287c8';assert run('git','rev-parse','HEAD')==old
for n in ['production-domain-proof','equivalence','production-flow-equivalence','report-equivalence','discovery-equivalence','guard-validation']:assert json.loads((OUT/(n+'.json')).read_text())['passed'],n
for n in ['final-lint','final-format','final-types']:assert json.loads((OUT.parent/('v66-'+n+'.json')).read_text())['exit_code']==0,n
files=['CHANGELOG.md','src/sentinel/static/typescript_path_flow.py','tests/test_typescript_invalidation_contract.py']
assert set(run('git','diff','--name-only').splitlines())==set(files[:2])
assert sha(ROOT/files[1])=='376b9ba27bddc3add96bfa88fab4d231850b0737daa465ce5db098c85a83e18a'
run('git','add','--',*files)
assert set(run('git','diff','--cached','--name-only').splitlines())==set(files)
print(run('git','commit','-m','Reuse monotone TypeScript branch invalidation accumulator'))
head=run('git','rev-parse','HEAD')
(OUT/'candidate-commit.json').write_text(json.dumps({'source':head,'parent':old,'files_sha256':{n:sha(ROOT/n) for n in files},'full_engineering':'pending','paid_calls':0},indent=2)+'\n')
print(head)
