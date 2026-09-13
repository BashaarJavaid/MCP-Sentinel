"""Prove the product delta is only the shared deadline constant."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
BASE=OUT.parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=(OUT/'baseline-engine.py').read_text()
after=(ROOT/'src/sentinel/static/engine.py').read_text()
expected=before.replace('# A scan may use extended time; 120 seconds remains the performance target.\nSTATIC_TIMEOUT_SECONDS = 300','# Completion uses a 30-minute shared limit; 120 seconds is an informational target.\nSTATIC_TIMEOUT_SECONDS = 1800',1)
assert after==expected
tree=ast.parse(after)
changes=0
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STATIC_TIMEOUT_SECONDS' for t in node.targets):
        assert isinstance(node.value,ast.Constant) and node.value.value==1800
        node.value.value=300
        changes+=1
assert changes==1 and ast.dump(tree)==ast.dump(ast.parse(before))
old=read(BASE/'v57-credential-merge/local-checks.json')['candidate_engineering_files_sha256']
changed={name:{'previous':digest,'current':sha(ROOT/name)} for name,digest in old.items() if sha(ROOT/name)!=digest}
assert set(changed)=={'CHANGELOG.md','src/sentinel/static/engine.py','tests/test_static_engine.py'}
for name in ['src/sentinel/orchestrator.py','src/sentinel/static/workers.py','src/sentinel/static/semgrep_adapter.py','src/sentinel/static/typescript_discovery.py']:
    assert sha(ROOT/name)==old[name]
assert 'deadline = time.monotonic() + STATIC_TIMEOUT_SECONDS' in (ROOT/'src/sentinel/orchestrator.py').read_text()
assert 'scan_deadline = min(deadline, scan_deadline)' in after
assert 'context.deadline - time.monotonic()' in (ROOT/'src/sentinel/static/workers.py').read_text()
packet={'passed':True,'baseline_scanner':'dc7371513a065457af566f4b589b9ed147130d64','product_change':'The existing shared deadline constant changes from 300 to 1800 seconds. Replacing that one AST literal restores the entire baseline engine AST; the text delta is only the constant and its policy comment.','old_deadline_seconds':300,'new_deadline_seconds':1800,'target_seconds':120,'changed_engineering_files':changed,'unchanged_engineering_files':{n:d for n,d in old.items() if n not in changed},'callers':'The unchanged orchestrator imports the same constant; the engine takes the minimum of its own limit and any caller deadline. Workers, Semgrep and parser consume the existing remaining deadline; cleanup, rule selection, detector logic, finding/report generation and schema are unchanged.','qualification':'Prospective timing-policy revision, not a speedup or proof of current-source detection/compatibility. Reports may newly complete after 300 seconds; all previous failures retain actual scanner/limit bindings. The separate new evaluation must retain full report and source assessment requirements.','corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'source-proof.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
print('Only one product AST literal changed; all 299 other engineering files match tested dc73715.')
