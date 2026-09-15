"""Commit only the approved joint candidate after its prerequisite checks."""
import datetime,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
git=lambda *args:subprocess.check_output(['git',*args],text=True).strip()
assert git('rev-parse','HEAD')=='9b2585d3a6cc7e1a3584eff1d9dcbf16a41cffbc'
assert git('branch','--show-current')=='phase22/integration' and not git('diff','--cached','--name-only')
allowed=['CHANGELOG.md','src/sentinel/static/path_flow.py','src/sentinel/static/rules/sent016.py','tests/test_credential_fallback.py']
assert set(git('diff','--name-only').splitlines())==set(allowed)
for name in ['correction','correction-tests','synthetic-corrected','affected','lint-corrected','format-corrected','mypy']:assert read(BASE/('v57-'+name+'.json'))['exit_code']==0,name
auth=read(OUT/'authorization.json')
for name,digest in auth['user_files_sha256'].items():assert sha(ROOT/name)==digest and not git('ls-files','--',name)
correction=read(OUT/'correction-validation.json');bypass=read(OUT/'synthetic-validation.json')
assert correction['passed'] and correction['cases']==4050 and bypass['passed'] and bypass['semantic_cases']==2430
expected=(OUT/'baseline-sent016.py').read_text().replace('            if all(branch.get(name, empty) is first for branch in branches[1:]):','            if all(\n                (other := branch.get(name, empty)) is first or other == first\n                for branch in branches[1:]\n            ):',1)
assert (ROOT/'src/sentinel/static/rules/sent016.py').read_text()==expected
expected=(OUT/'baseline-path-flow.py').read_text().replace('    return _combine(tuple(values), key)','    if len(values) == 1 and values[0] is UNKNOWN_VALUE and not key:\n        return UNKNOWN_VALUE\n    return _combine(tuple(values), key)',1)
assert (ROOT/'src/sentinel/static/path_flow.py').read_text()==expected
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'approved joint candidate implemented; full local and hosted engineering pending','authorization_sha256':sha(OUT/'authorization.json'),'correction_validation_sha256':sha(OUT/'correction-validation.json'),'synthetic_validation_sha256':sha(OUT/'synthetic-validation.json'),'files_sha256':{name:sha(ROOT/name) for name in allowed},'correction_cases':4050,'intentional_marker_deltas':len(correction['intended_marker_deltas']),'derived_guard_cache_input_deltas':len(correction['downstream_guard_cache_deltas']),'bypass_full_state_cases':2430,'eviction_cases':2,'contract':'Equal marker joining is a deliberate approved internal-state correction. Canonical bypass is fully equivalent to the retained correction-only reference. Original a36f696 failures remain source-bound. No corpus result or speedup claim.','corpus_observations':0,'profiles':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (OUT/'source-checkpoint.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
subprocess.run(['git','add','--',*allowed],check=True)
selected=[str((OUT/name).relative_to(ROOT)) for name in ['authorization.json','source-checkpoint.json']]
subprocess.run(['git','add','-f','--',*selected],check=True)
assert set(git('diff','--cached','--name-only').splitlines())==set(allowed+selected)
subprocess.run(['git','diff','--cached','--check'],check=True)
subprocess.run(['git','commit','-m','Make equal credential joins independent of value interning'],check=True)
assert not git('diff','--name-only')
with (OUT/'candidate-commit.json').open('x') as stream:json.dump({'source':git('rev-parse','HEAD'),'parent':auth['starting_delivery'],'files_sha256':{name:sha(ROOT/name) for name in allowed+selected},'full_engineering':'pending','corpus_observations':0,'profiles':0,'paid_calls':0},stream,indent=2);stream.write('\n')
print(git('rev-parse','HEAD'))
