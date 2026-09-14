"""Compare complete discovery against preserved code on scanner-owned tests."""
import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest

from sentinel.static.typescript_discovery import TypeScriptProgram

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
source = ROOT / 'src/sentinel/static/typescript_discovery.py'
baseline = OUT / 'baseline/src/sentinel/static/typescript_discovery.py'


def method(path, name):
    tree = ast.parse(path.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'TypeScriptProgram')
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    node.name = 'tools'
    return ast.dump(node, include_attributes=False)


assert method(source, '_discover_tools') == method(baseline, '_discover_tools')
import sentinel.static.typescript_path_flow as flow_module
flow_path=OUT/'baseline/src/sentinel/static/typescript_path_flow.py'
t=ast.parse(flow_path.read_text());c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptPathFlow');n=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='statement');scope={};exec(compile(ast.Module(body=[n],type_ignores=[]),str(flow_path),'exec'),vars(flow_module),scope)
candidate_statement=flow_module.TypeScriptPathFlow.statement
original = TypeScriptProgram.tools
records = []


def checked(program):
    modules = copy.deepcopy(program.modules)
    reference = TypeScriptProgram(tuple(program.files.values()), deadline=program.deadline,
                                  modules=modules, trees=program.trees)
    reference.warnings[:] = program.warnings
    flow_module.TypeScriptPathFlow.statement=scope['statement']
    try: expected = reference._discover_tools()
    finally: flow_module.TypeScriptPathFlow.statement=candidate_statement
    actual = original(program)
    assert actual == expected, 'complete ordered discovery fields changed'
    assert program.warnings == reference.warnings, 'ordered discovery warnings changed'
    if modules is not None:
        assert program.modules.option_cache == modules.option_cache, 'module option effects changed'
    records.append({'files': list(program.files), 'bindings': len(actual), 'warnings': len(program.warnings)})
    return actual


TypeScriptProgram.tools = checked
result = pytest.main([
    'tests/test_typescript_classes.py', 'tests/test_typescript_modules.py',
    'tests/test_typescript_sdk_wrappers.py', 'tests/test_flow_recovery.py',
    '--no-cov', '-x',
])
with (OUT / 'discovery-equivalence.json').open('x') as handle:
    json.dump({'passed': result == 0, 'pytest_exit': int(result),
               'producer_ast_identical_to_baseline': True,
               'comparisons': records, 'comparison_count': len(records),
               'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'source_corpus_observations': 0, 'paid_calls': 0}, handle, indent=2)
    handle.write('\n')
raise SystemExit(result)
