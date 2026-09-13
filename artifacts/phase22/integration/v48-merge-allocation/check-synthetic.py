"""Compare the preserved baseline with the candidate on scanner-owned state only."""
import copy
import hashlib
import itertools
import json
import textwrap
import time
from pathlib import Path
from unittest.mock import patch

import sentinel.static.typescript_path_flow as module
from sentinel.static.model import RuleRunState
from sentinel.static.path_flow import Value
from sentinel.static.rules.sent015 import TypeScriptURLFlow
from sentinel.static.typescript_discovery import TypeScriptProgram

out = Path(__file__).resolve().parent
namespace = dict(vars(module))
exec(compile(textwrap.dedent((out/'baseline-merge.py').read_text()), str(out/'baseline-merge.py'), 'exec'), namespace)
baseline = namespace['merge']
program = TypeScriptProgram((), deadline=time.monotonic() + 60)
values = [Value(), Value(key='root'), Value(key='other'), Value(key='#ts:undefined')]
for sources in (frozenset(), frozenset({'caller'})):
    values.append(Value(key='root', sources=sources, contained=True, checked_path_parent=True, option_safe=True, url_checks=frozenset({'scheme', 'host'}), locations=frozenset({('synthetic.ts', 1)}), operator_credential=True, operator_opt_in=frozenset({'selected'}), collection_nonempty=True))

def flow(registered, metadata):
    result = TypeScriptURLFlow(program, RuleRunState())
    if registered:
        result.objects['root'] = {'field': Value(key='field', sources=frozenset({'caller'}))}
        result.objects['other'] = {'other_field': Value(key='other_field')}
    if metadata:
        result.record_roots.update({'root': 'root', 'other': 'root'})
        result.normalized.update({'root', 'other'})
        result.path_inputs.update({'root': frozenset({'input'}), 'other': frozenset({'input', 'extra'})})
        result.mobilecli_paths.add('root')
        result.arrays.update({'root', 'other'})
        result.array_states.update({'root': ((Value(key='item'),),), 'other': ((Value(key='other-item'),),)})
        result.conditions.update({'root': (frozenset({'guard'}), frozenset()), 'other': (frozenset({'guard'}), frozenset({'else'}))})
        result.boundaries['boundary'] = (Value(key='root'), Value(key='other'))
        result.url_parts['root'] = ('url', 'hostname')
    return result

cases = 0
saved = used = 0
for count, registered, metadata, name in itertools.product((0, 1, 2, 3, 8), (False, True), (False, True), ('#record:root', '#record:unknown', '#guard:allowed', 'ordinary')):
    for left, right in itertools.product(values, repeat=2):
        for missing in [None, *range(count)]:
            branches = [{name: left if i % 2 == 0 else right} if i != missing else {} for i in range(count)]
            snapshot = copy.deepcopy(branches)
            old, new = flow(registered, metadata), flow(registered, metadata)
            old_env, new_env = {'untouched': Value(key='keep')}, {'untouched': Value(key='keep')}
            with patch.dict(namespace, Value=Value):
                baseline(old, old_env, branches)
            module.TypeScriptPathFlow.merge(new, new_env, branches)
            assert old_env == new_env, (count, registered, metadata, name, left, right, missing)
            assert vars(old) == vars(new), (count, registered, metadata, name, left, right, missing)
            assert branches == snapshot
            cases += 1
# Count precisely the proposed root fallback, including missing first/middle/last.
allocations = []
for count in (1, 2, 3, 8):
    for missing in [None, *range(count)]:
        branches = [{'#record:root': Value(key='root')} if i != missing else {} for i in range(count)]
        counts = []
        for kernel in (baseline, module.TypeScriptPathFlow.merge):
            f = flow(True, False)
            with patch.object(module, 'Value', wraps=Value) as constructor, patch.dict(namespace, Value=constructor):
                kernel(f, {}, branches)
            counts.append(sum(c.args == () and c.kwargs == {'key': 'root'} for c in constructor.call_args_list))
        expected_old = int(any(branches))
        expected_new = int(any(branches) and missing is not None)
        assert counts == [expected_old, expected_new], (count, missing, counts)
        saved += counts[0] - counts[1]
        used += counts[1]
        allocations.append({'branches': count, 'missing_index': missing, 'baseline': counts[0], 'candidate': counts[1]})
assert saved > 0 and used > 0
packet = {'passed': True, 'semantic_cases': cases, 'equal_environment_and_entire_flow_state': True, 'inputs_unchanged': True, 'allocation_cases': allocations, 'unused_fallbacks_avoided': saved, 'used_fallbacks_preserved': used, 'baseline_sha256': hashlib.sha256((out/'baseline-merge.py').read_bytes()).hexdigest(), 'candidate_source_sha256': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(), 'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0, 'native_performance_claim': False}
with (out/'synthetic-validation.json').open('x') as stream:
    json.dump(packet, stream, indent=2); stream.write('\n')
print(json.dumps(packet, indent=2))
