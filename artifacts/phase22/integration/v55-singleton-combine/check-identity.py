"""Exercise the approved warm-cache identity prerequisite on scanner-owned state."""
import ast
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

import sentinel.static.path_flow as module
import sentinel.static.rules.sent016 as credential
from sentinel.static.discovery import PythonProgram
from sentinel.static.model import RuleRunState

out = Path(__file__).resolve().parent
namespace = dict(vars(module))
tree = ast.parse((out / 'baseline-path-flow.py').read_text())
tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {'combine', '_combine'}]
exec(compile(tree, str(out / 'baseline-path-flow.py'), 'exec'), namespace)
baseline = namespace['combine']
rows = []
for contained in (True, False):
    first = module.Value(key='caller', sources=frozenset({'http:caller'}), contained=contained,
                         locations=frozenset({('synthetic.py', 1)}))
    second = replace(first)
    assert first == second and first is not second
    outcomes = []
    for kernel, cache in ((baseline, namespace['_combine']), (module.combine, module._combine)):
        cache.cache_clear()
        left, right = kernel([first]), kernel([second])
        flow = credential.CredentialFlow(PythonProgram(()), RuleRunState(), float('inf'))
        marker = '#absent:caller'
        flow.absent_markers.add(marker)
        env = {}
        branches = [{marker: left}, {marker: right}]
        with patch.object(module, 'combine', kernel), patch.object(credential, 'combine', kernel):
            flow.merge(env, branches)
        outcomes.append((env, vars(flow), {'same_input_result_identity': left is right,
            'merged_marker': repr(env[marker]), 'cache': cache.cache_info()._asdict()}))
    rows.append({'contained': contained, 'environment_equal': outcomes[0][0] == outcomes[1][0],
                 'entire_flow_equal': outcomes[0][1] == outcomes[1][1],
                 'baseline': outcomes[0][2], 'candidate': outcomes[1][2]})
packet = {'passed': all(row['environment_equal'] and row['entire_flow_equal'] for row in rows),
          'cases': rows, 'candidate_source_sha256': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
          'baseline_source_sha256': hashlib.sha256((out / 'baseline-path-flow.py').read_bytes()).hexdigest(),
          'qualification': 'Synthetic internal credential-marker states. The contained-false marker is deliberately adversarial; reachability from a complete target program is not established by this check. No corpus or target program executed.',
          'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0}
with (out / 'identity-validation.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print(json.dumps(packet, indent=2))
assert packet['passed'], 'Approved identity-dependent full-state equivalence prerequisite failed; close the attempt.'
