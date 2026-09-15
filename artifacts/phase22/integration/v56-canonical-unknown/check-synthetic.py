"""Check prior identity cases and LRU eviction before broader engineering."""
import ast
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import sentinel.static.path_flow as module
import sentinel.static.rules.sent016 as credential
from sentinel.static.discovery import PythonProgram
from sentinel.static.model import RuleRunState

out = Path(__file__).resolve().parent
old = out.parent/'v55-singleton-combine'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def kernel(path):
    namespace = dict(vars(module))
    tree = ast.parse(path.read_text())
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {'combine','_combine'}]
    exec(compile(tree, str(path), 'exec'), namespace)
    return namespace

# Reuse the corrected structural comparison, without running its old experiment.
namespace = dict(globals())
tree = ast.parse((old/'assess-failure.py').read_text())
tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'state']
exec(compile(tree, str(old/'assess-failure.py'), 'exec'), namespace)
state = namespace['state']
baseline = kernel(out/'baseline-path-flow.py')
broad = kernel(old/'candidate-path-flow.py')
narrow = vars(module)
program = PythonProgram(())

def exercise(namespace, contained, eviction):
    combine, cache = namespace['combine'], namespace['_combine']
    cache.cache_clear()
    first = module.Value(key='caller', sources=frozenset({'http:caller'}), contained=contained,
                         locations=frozenset({('synthetic.py', 1)}))
    second = replace(first)
    assert first == second and first is not second
    left = combine([first])
    if eviction:
        # Exactly fill the established4096-entry cache; no timing measurement.
        for index in range(4095):
            combine([module.Value(key=f'other:{index}')])
        assert cache.cache_info().currsize == 4096
    before_unknown = cache.cache_info()._asdict()
    if eviction:
        assert combine([module.UNKNOWN_VALUE]) == module.UNKNOWN_VALUE
    after_unknown = cache.cache_info()._asdict()
    right = combine([second])
    before_merge = cache.cache_info()._asdict()
    flow = credential.CredentialFlow(program, RuleRunState(), float('inf'))
    flow.absent_markers.add('#absent:caller')
    branches = [{'#absent:caller':left},{'#absent:caller':right}]
    initial = state(branches)
    env = {}
    with patch.object(module,'combine',combine), patch.object(credential,'combine',combine):
        flow.merge(env, branches)
    assert state(branches) == initial
    return {'environment':state(env), 'flow':state(flow), 'same_result_identity':left is right,
            'before_unknown':before_unknown, 'after_unknown':after_unknown,
            'before_merge':before_merge, 'inputs_unchanged':True}

rows = []
for contained in (True,False):
    results = {name:exercise(ns,contained,False) for name,ns in [('baseline',baseline),('broad',broad),('narrow',narrow)]}
    assert results['baseline']['flow'] == results['broad']['flow'] == results['narrow']['flow']
    assert results['baseline']['environment'] == results['narrow']['environment']
    assert (results['baseline']['environment'] == results['broad']['environment']) == contained
    rows.append({'contained':contained, 'eviction':False, 'narrow_equivalent':True, 'broad_equivalent':contained, 'results':results})

# Fail closed if skipping the canonical empty entry changes later interning.
results = {name:exercise(ns,False,True) for name,ns in [('baseline',baseline),('narrow',narrow)]}
equivalent = results['baseline']['environment'] == results['narrow']['environment'] and results['baseline']['flow'] == results['narrow']['flow']
rows.append({'contained':False, 'eviction':True, 'narrow_equivalent':equivalent, 'results':results})
packet = {'passed':equivalent, 'baseline_sha256':sha(out/'baseline-path-flow.py'),
          'candidate_sha256':sha(Path(module.__file__)), 'broad_failed_candidate_sha256':sha(old/'candidate-path-flow.py'),
          'structural_comparison_source_sha256':sha(old/'assess-failure.py'), 'cases':rows,
          'complete_synthetic_matrix_executed':False,
          'qualification':'Scanner-owned synthetic Value/credential-marker states only. A4096-entry cache fill tests eviction, not performance. Real-target reachability of the tainted contained-false marker remains unestablished. Broader matrix/engineering remains unexecuted at this prerequisite.',
          'corpus_observations':0, 'profiles':0, 'paid_calls':0}
with (out/'synthetic-validation.json').open('x') as stream:
    json.dump(packet,stream,indent=2);stream.write('\n')
print(json.dumps({'passed':equivalent,'retained_prior_cases':2,'eviction_case':{'baseline_identity':results['baseline']['same_result_identity'],'narrow_identity':results['narrow']['same_result_identity'],'environment_equal':results['baseline']['environment']==results['narrow']['environment'],'full_flow_equal':results['baseline']['flow']==results['narrow']['flow']}}))
assert equivalent, 'Canonical bypass changed cache eviction and synthetic credential environment; close the single attempt.'
