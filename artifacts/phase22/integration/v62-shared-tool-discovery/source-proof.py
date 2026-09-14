"""Bind the narrow source change, preserved traversal and unchanged engineering inputs."""
import ast,hashlib,json,subprocess
from pathlib import Path
root=Path.cwd(); out=Path(__file__).resolve().parent; base=out.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rev='1948bf942babce155b701f5b22ed941eb16d99d0'
a=read(out/'authorization.json'); old=a['scanner']['revision']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==rev
assert not subprocess.check_output(['git','diff','HEAD'])
expected={'src/sentinel/static/typescript_discovery.py','src/sentinel/static/model.py','src/sentinel/static/workers.py','tests/test_typescript_discovery.py','tests/test_static_workers.py','CHANGELOG.md'}
changed=set(subprocess.check_output(['git','diff','--name-only',old,rev,'--','src','tests','scripts','pyproject.toml','uv.lock','CHANGELOG.md','.github','action.yml','Dockerfile'],text=True).splitlines())
assert changed==expected,changed
baseline=read(base/'v59-timeout-policy/local-checks.json')['candidate_engineering_files_sha256']
current={name:sha(root/name) for name in baseline}
assert {n for n in current if current[n]!=baseline[n]}==expected
for name in current:assert subprocess.check_output(['git','show',rev+':'+name])==(root/name).read_bytes()
for name,digest in a['baseline_files_sha256'].items():assert sha(out/'baseline'/name)==digest
path='src/sentinel/static/typescript_discovery.py'
prior=ast.parse((out/'baseline'/path).read_text()); now=ast.parse((root/path).read_text())
def method(tree,name):
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptProgram')
 return next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
original=method(prior,'tools'); candidate=method(now,'_discover_tools');candidate.name='tools'
assert ast.dump(original,include_attributes=False)==ast.dump(candidate,include_attributes=False)
for name in a['user_files_sha256']:assert sha(root/name)==a['user_files_sha256'][name]
assert read(out/'discovery-equivalence.json')['passed']
packet={'passed':True,'baseline_scanner':a['scanner'],'candidate':rev,'authorization_sha256':sha(out/'authorization.json'),'changed_engineering_files':sorted(changed),'candidate_engineering_files_sha256':current,'original_discovery_traversal_ast_identical':True,'scope':'Completed TypeScript registration discovery reused in one StaticContext and the existing four-worker IPC graph. Source files/trees/synthetic bindings share aliases; identity indexes rebuild. Ordered warnings and option-cache effects apply at consumption. All per-rule analysis and coverage still execute. Failed, expired or interrupted discovery never installs a completed result. No HTTP discovery cache, pruning, dependency, worker-count, resource or timeout change.','synthetic_equivalence_sha256':sha(out/'discovery-equivalence.json'),'static_timeout_seconds':1800,'speedup_established':False,'current_source_corpus_compatibility_established':False,'corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False}
with (out/'source-proof.json').open('x') as f:json.dump(packet,f,indent=2);f.write('\n')
print('Original traversal AST preserved; six engineering files changed, all other mapped inputs unchanged.')
