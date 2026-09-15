"""Compare full production flow state at real statement entries in owned tests."""
import ast, copy, dataclasses, hashlib, json
from pathlib import Path
import pytest
import sentinel.static.typescript_path_flow as module
from sentinel.static.typescript_discovery import walk
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
p=OUT/'baseline/src/sentinel/static/typescript_path_flow.py'
t=ast.parse(p.read_text());c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptPathFlow');n=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='statement');scope={};exec(compile(ast.Module(body=[n],type_ignores=[]),str(p),'exec'),vars(module),scope)
baseline=scope['statement'];candidate=baseline
records=[];busy=False

def canonical(v,seen=None):
    if v is None or isinstance(v,(str,int,bool,float)):return v
    if isinstance(v,Path):return str(v)
    if seen is None:seen=set()
    if id(v) in seen:return {'cycle':type(v).__qualname__}
    seen=seen|{id(v)}
    if dataclasses.is_dataclass(v):return {f.name:canonical(getattr(v,f.name),seen) for f in dataclasses.fields(v)}
    if isinstance(v,dict):return sorted([(canonical(k,seen),canonical(x,seen)) for k,x in v.items()],key=repr)
    if isinstance(v,(set,frozenset)):return sorted((canonical(x,seen) for x in v),key=repr)
    if isinstance(v,(list,tuple)):return [canonical(x,seen) for x in v]
    if hasattr(v,'__dict__'):return {'type':type(v).__qualname__,'fields':canonical(vars(v),seen)}
    raise AssertionError(('unhandled state',type(v)))

def checked(self,file,node,env,returned):
    global busy
    if busy:return candidate(self,file,node,env,returned)
    memo={id(f):f for f in self.program.files.values()}
    memo.update((id(n),n) for tree in self.program.trees.values() for n in walk(tree))
    # Keep actual AST identity keys, but copy every mutable interpreter/program field.
    reference,reference_env,reference_returned=copy.deepcopy((self,env,returned),memo)
    before=copy.deepcopy(node);busy=True
    try:
        module.TypeScriptPathFlow.statement=baseline
        expected=baseline(reference,file,node,reference_env,reference_returned)
    finally:
        module.TypeScriptPathFlow.statement=checked
    try:
        actual=candidate(self,file,node,env,returned)
        expected_state=canonical((vars(reference),reference_env,reference_returned,expected))
        actual_state=canonical((vars(self),env,returned,actual))
        if expected_state!=actual_state:
            (OUT/'helper-control-mismatch.json').write_text(json.dumps({'class':type(self).__name__,'node':node,'baseline':expected_state,'candidate':actual_state},indent=2)+'\n')
            raise AssertionError('complete production flow changed; see helper-control-mismatch.json')
        assert node==before
        records.append({'flow':type(self).__name__,'statement':list(node),'file':file.relative_path,'baseline_keys':len(reference.invalidated_objects),'candidate_keys':len(self.invalidated_objects)})
        return actual
    finally:busy=False

module.TypeScriptPathFlow.statement=checked
result=pytest.main(['tests/test_typescript_classes.py::test_rule_delegation_does_not_repeat_callee_or_argument_effects[new Writer().write(args.value)-1-TypeScriptPathFlow]','--no-cov','-x'])
(OUT/'helper-control-result.json').write_text(json.dumps({'passed':result==1,'identical_baseline_methods':True,'classification':'Expected failing negative control: original copied callback remains bound to actual flow and creates a mismatch even when both compared statement implementations are the exact baseline.','pytest_exit':int(result),'comparison_count':len(records),'comparisons':records,'candidate_sha256':hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),'corpus_observations':0,'profiles':0,'paid_calls':0},indent=2)+'\n')
assert result==1 and (OUT/'helper-control-mismatch.json').exists()
print('Initial helper mismatch reproduced with identical baseline methods; corrected callback rebinding is required.')
