"""Assess the retained candidate without reinstalling it or reopening the attempt."""
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
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path(module.__file__)) == sha(out / 'baseline-path-flow.py')

def kernel(name):
    namespace = dict(vars(module))
    tree = ast.parse((out / name).read_text())
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {'combine', '_combine'}]
    exec(compile(tree, str(out / name), 'exec'), namespace)
    return namespace

def state(value, active=()):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if id(value) in active:
        return {'cycle_type': type(value).__qualname__}
    active = (*active, id(value))
    if isinstance(value, dict):
        return {str(key): state(item, active) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [state(item, active) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((state(item, active) for item in value), key=repr)
    if isinstance(value, module.Value):
        return {name: state(getattr(value, name), active) for name in value.__dataclass_fields__}
    return {'type': type(value).__qualname__, 'fields': state(vars(value), active)}

namespaces = [kernel('baseline-path-flow.py'), kernel('candidate-path-flow.py')]
program = PythonProgram(())
rows = []
for contained in (True, False):
    first = module.Value(key='caller', sources=frozenset({'http:caller'}), contained=contained,
                         locations=frozenset({('synthetic.py', 1)}))
    second = replace(first)
    outputs = []
    for namespace in namespaces:
        combine = namespace['combine']
        namespace['_combine'].cache_clear()
        left, right = combine([first]), combine([second])
        flow = credential.CredentialFlow(program, RuleRunState(), float('inf'))
        flow.absent_markers.add('#absent:caller')
        env = {}
        branches = [{'#absent:caller': left}, {'#absent:caller': right}]
        before = state(branches)
        with patch.object(module, 'combine', combine), patch.object(credential, 'combine', combine):
            flow.merge(env, branches)
        assert state(branches) == before
        outputs.append({'environment': state(env), 'flow': state(flow), 'same_result_identity': left is right})
    rows.append({'contained': contained, 'environment_equal': outputs[0]['environment'] == outputs[1]['environment'],
                 'full_flow_equal': outputs[0]['flow'] == outputs[1]['flow'],
                 'baseline': outputs[0], 'candidate': outputs[1]})
assert rows[0]['environment_equal'] and rows[0]['full_flow_equal']
assert not rows[1]['environment_equal'] and rows[1]['full_flow_equal']
callers = []
identity_sites = []
for path in sorted(Path('src/sentinel/static').rglob('*.py')):
    source = path.read_text()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'combine', '_combine', 'id'}:
            (callers if node.func.id in {'combine', '_combine'} else identity_sites).append({'file': str(path), 'line': node.lineno, 'source_sha256': sha(path), 'expression': ast.get_source_segment(source, node)})
        elif isinstance(node, ast.Compare) and any(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops) and not any(isinstance(part, ast.Constant) and part.value in (None, True, False) for part in [node.left, *node.comparators]):
            identity_sites.append({'file': str(path), 'line': node.lineno, 'source_sha256': sha(path), 'expression': ast.get_source_segment(source, node)})
packet = {
    'assessment_passed': True, 'candidate_equivalence_passed': False,
    'baseline_sha256': sha(out/'baseline-path-flow.py'), 'candidate_sha256': sha(out/'candidate-path-flow.py'),
    'restored_source_sha256': sha(Path(module.__file__)), 'cases': rows,
    'all_static_combine_callers': callers, 'static_identity_sites': identity_sites,
    'first_check_correction': 'The initial check compared vars(flow) containing separately constructed PythonProgram, RegistrationFlow and HTTPContext objects without structural comparison; its whole-flow false flags are not semantic failures. Structural cycle-aware comparison now preserves every field and reports equal full-flow state in both cases. The contained-false environment delta remains independently verified. Initial helper and failed receipt retained unchanged.',
    'source_cause': 'path_flow._combine LRU keys use Value equality and can intern distinct equal singleton inputs. Direct return preserves their distinct identities. CredentialFlow.merge at sent016.py174 tests only is on absence/opt-in markers: equal shared uncontained Values retain fields; equal distinct uncontained Values fall through to UNKNOWN_VALUE. All other observed flow state remains equal.',
    'reachability_limit': 'This is a deliberately adversarial scanner-internal marker state, not an observed target finding change. Source guard constructors set named markers contained=True; merge can reset them to UNKNOWN_VALUE. No source path establishing a nonempty tainted contained=False marker from a real target has been demonstrated. The originally proposed complete-state identity prerequisite does not permit silently narrowing the state domain after failure.',
    'stopping_disposition': 'Single approved attempt failed the required synthetic environment equivalence gate and is closed. Candidate source and patch retained; product restored exactly to a36f696. No repair or different optimization attempted. Broader synthetic matrices and affected/full local/hosted engineering were not run because the prerequisite failed and there is no retained candidate to certify. Prior engineering remains source-bound.',
    'new_proposal': None, 'new_optimization_authorized': False,
    'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0,
    'technical_acceptance_received': False, 'phase22_complete': False,
}
with (out/'assessment.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print('Assessment verified: full-flow comparison corrected; synthetic environment difference remains. Product restored; attempt closed.')
