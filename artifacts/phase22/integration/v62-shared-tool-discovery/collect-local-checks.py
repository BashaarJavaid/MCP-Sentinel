"""Retain completed engineering, with current source and unchanged runtime bindings."""
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
out=Path(__file__).resolve().parent; base=out.parent; root=Path.cwd()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
head='1948bf942babce155b701f5b22ed941eb16d99d0'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','diff','HEAD'])
states=Counter('failed' if node.find('failure') is not None or node.find('error') is not None else 'skipped' if node.find('skipped') is not None else 'passed' for node in ET.parse(base/'v62-full-suite-junit.xml').getroot().iter('testcase'))
assert states=={'passed':2418,'skipped':36},states
coverage=read(base/'v62-full-suite-coverage.json')
assert coverage['meta']['branch_coverage'] and coverage['totals']['percent_covered']>=80 and 100*coverage['totals']['covered_branches']/coverage['totals']['num_branches']>=80
labels=['source-proof','lint-corrected','format','source-types','affected','discovery-equivalence','full-suite','lock','schema','notices','artifacts','candidate-docs','build','candidate-distributions','runtime-requirements','dependency-audit','production-capture','runtime-reuse','demo-validation']
checks={}
for label in labels:
    name='v62-'+label
    row=read(base/(name+'.json'));assert row['exit_code']==0,name
    assert sha(base/(name+'.patch'))==row['diff_sha256']
    assert sha(base/(name+'.untracked.tar.gz'))==row['untracked_source_sha256']
    checks[name]={'command':row['command'],'source_commit':row['source_commit'],'receipt_sha256':sha(base/(name+'.json')),'log_sha256':sha(base/(name+'.log')),'diff_sha256':row['diff_sha256']}
old=read(base/'v59-timeout-policy/local-checks.json')['candidate_engineering_files_sha256']
sources={name:sha(root/name) for name in old}
changed={name:{'previous_sha256':old[name],'candidate_sha256':digest} for name,digest in sources.items() if old[name]!=digest}
assert set(changed)=={'CHANGELOG.md','src/sentinel/static/typescript_discovery.py','src/sentinel/static/model.py','src/sentinel/static/workers.py','tests/test_typescript_discovery.py','tests/test_static_workers.py'}
for name in sources:assert subprocess.check_output(['git','show',head+':'+name])==(root/name).read_bytes(),name
replay=read(base/'v62-production-capture-revalidation/packet.json')
assert replay['source']==head and replay['model_calls']==0 and len(replay['requests'])==6 and all(r['accepted'] for r in replay['requests'])
packet={'candidate':head,'states':dict(states),'coverage_totals':coverage['totals'],'coverage_metric':'percent_covered is configured combined statement/branch coverage; percent_branches_covered is branch-only. Do not call the combined total branch-only.','junit_sha256':sha(base/'v62-full-suite-junit.xml'),'coverage_sha256':sha(base/'v62-full-suite-coverage.json'),'checks':checks,'candidate_engineering_files_sha256':sources,'changes_from_prior_engineering':changed,'precommit_checks':'Focused discovery/worker tests, complete baseline discovery AST proof, lint/format and strict mypy bind exact precommit patches. The committed product/test bytes are checked here; full suite and hosted matrix bind the actual candidate. Rule-specific analysis remains unchanged; completed discovery is shared.','candidate_commit_receipt_sha256':sha(out/'candidate-commit.json'),'python':sys.version,'packages':{name:importlib.metadata.version(name) for name in ['semgrep','mcp','pytest','pydantic']},'runtime_binding_sha256':sha(out/'compatibility.json'),'production_replay_sha256':sha(base/'v62-production-capture-revalidation/packet.json'),'hosted_engineering':'Separate retained matrix/job/log/package audit.','new_corpus_observations':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (out/'local-checks.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
print('Bound2418passes,36skips,302engineering files and6zero-call production requests.')
