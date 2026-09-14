"""Compare actual baseline/candidate If flow with explicit alias/shrinking controls."""
import ast, copy, dataclasses, hashlib, itertools, json
from pathlib import Path
from types import SimpleNamespace
import sentinel.static.typescript_path_flow as module
from sentinel.static.model import RuleRunState
from sentinel.static.path_flow import Value, _combine
OUT=Path(__file__).resolve().parent
BASE=OUT/'baseline/src/sentinel/static/typescript_path_flow.py'
tree=ast.parse(BASE.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptPathFlow');node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='statement');scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(BASE),'exec'),vars(module),scope)
baseline=scope['statement'];candidate=module.TypeScriptPathFlow.statement
class CountedSet(set):
    counts={}
    def copy(self):
        self.counts['copy']=self.counts.get('copy',0)+1
        return CountedSet(self)
    def update(self,*values):
        self.counts['update']=self.counts.get('update',0)+1
        return super().update(*values)
def canonical(value):
    if dataclasses.is_dataclass(value):return {f.name:canonical(getattr(value,f.name)) for f in dataclasses.fields(value)}
    if isinstance(value,dict):return {str(k):canonical(v) for k,v in sorted(value.items(),key=lambda x:str(x[0]))}
    if isinstance(value,(set,frozenset)):return sorted((canonical(v) for v in value),key=repr)
    if isinstance(value,(list,tuple)):return [canonical(v) for v in value]
    if isinstance(value,SimpleNamespace):return canonical(vars(value))
    if value is None or isinstance(value,(str,int,bool,float)):return value
    raise AssertionError(('unhandled full-state field',type(value)))
def run(method,initial,facts,termination,nested,prealias,control=None):
    class Probe(module.TypeScriptPathFlow):
        def expression(self,file,node,env):return Value(key='condition')
        def statement(self,file,node,env,returned):
            if 'probe' not in node:return method(self,file,node,env,returned)
            name=node['probe']
            self.arm_entries.append((name,sorted(self.invalidated_objects)))
            self.invalidate(Value(key=name))
            env[name]=Value(key=name,operator_credential=True)
            if control=='shrink':self.invalidated_objects.clear()
            if control=='alias':self.retained_arm_sets.append(self.invalidated_objects)
            if control=='interrupt' and name=='right':raise KeyboardInterrupt('synthetic interruption')
            if control=='error' and name=='right':raise RuntimeError('synthetic error')
            return not node['terminates']
    flow=Probe(SimpleNamespace(deadline=1e99),RuleRunState())
    flow.invalidated_objects=CountedSet(initial);before_set=flow.invalidated_objects
    if prealias:flow.arrays=before_set
    flow.arm_entries=[];flow.retained_arm_sets=[]
    flow.conditions['condition']=facts
    def arm(name,terminates):
        leaf={'probe':name,'terminates':terminates}
        return {'If':[None,{},leaf,None]} if nested else leaf
    source={'If':[None,{},arm('left',termination[0]),{'some':arm('right',termination[1])}]}
    preserved=copy.deepcopy(source);env={'kept':Value(key='kept',sources=frozenset({'synthetic'}))};returned=[]
    CountedSet.counts={};_combine.cache_clear()
    result=None;error=None
    try:result=flow.statement(None,source,env,returned)
    except (KeyboardInterrupt,RuntimeError) as e:error=type(e).__name__
    counts=dict(CountedSet.counts)
    state=canonical(vars(flow))
    aliases={'arrays_is_original':flow.arrays is before_set,'invalidated_is_original':flow.invalidated_objects is before_set,'final_is_retained_arm':[flow.invalidated_objects is s for s in flow.retained_arm_sets]}
    assert source==preserved
    return {'result':result,'error':error,'environment':canonical(env),'returned':canonical(returned),'complete_flow':state,'original_set':sorted(before_set),'aliases':aliases},counts
facts=[(None,None),(None,frozenset()),(frozenset(),None),(frozenset(),frozenset())]
ordinary=[]
for size,condition,termination,nested,prealias in itertools.product([0,1,32,4096],facts,[(False,False),(True,False),(False,True),(True,True)],[False,True],[False,True]):
    args=({f'initial-{i}' for i in range(size)},condition,termination,nested,prealias)
    expected,bc=run(baseline,*args);actual,cc=run(candidate,*args)
    assert expected==actual,('ordinary mismatch',size,condition,termination,nested,prealias)
    ordinary.append({'initial_size':size,'feasible_arms':sum(f is not None for f in condition),'terminating':termination,'nested':nested,'preexisting_alias':prealias,'baseline_operations':bc,'candidate_operations':cc})
controls=[]
for control,condition in [('alias',facts[3]),('shrink',facts[1]),('interrupt',facts[3]),('error',facts[3])]:
    args=({'baseline'},condition,(False,False),False,True,control)
    expected,bc=run(baseline,*args);actual,cc=run(candidate,*args)
    controls.append({'control':control,'equivalent':expected==actual,'baseline':expected,'candidate':actual,'baseline_operations':bc,'candidate_operations':cc,'scope':'Scanner-owned synthetic instrumented leaf. Alias capture/shrinking is adversarial and not found among current production writes; real-target reachability is not established. The approved proposal explicitly requires these controls without excluding failures.'})
assert all(r['candidate_operations'].get('copy',0)<=r['baseline_operations'].get('copy',0) for r in ordinary)
representative=next(r for r in ordinary if r['feasible_arms']==2 and not r['nested'] and not any(r['terminating']))
assert representative['baseline_operations']['copy']-representative['candidate_operations']['copy']==1
assert representative['baseline_operations']['update']-representative['candidate_operations']['update']==1
prior=json.loads((OUT.parent/'v65-if-invalidation-accumulator/equivalence.json').read_text())
authorization=json.loads((OUT/'authorization.json').read_text());assert authorization['decision']=='approved'
assert controls==prior['controls'], 'Retained counterexample or partial-state result changed'
passed=all(r['equivalent'] for r in controls if r['control'] not in {'alias','shrink'})
assert [r['control'] for r in controls if not r['equivalent']]==['alias','shrink']
packet={'passed':passed,'explicit_domain_revision_authorization_sha256':hashlib.sha256((OUT/'authorization.json').read_bytes()).hexdigest(),'original_strict_failure_retained':True,'out_of_domain_negative_controls':['alias','shrink'],'ordinary_comparisons':len(ordinary),'ordinary':ordinary,'controls':controls,'avoided_work_verified_for_ordinary_cases':True,'candidate_sha256':hashlib.sha256((OUT/'candidate-typescript-path-flow.py').read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'corpus_observations':0,'profiles':0,'paid_calls':0,'qualification':'Entire flow/environment/Value contents and named relevant set aliases compared. Instrumentation fields are included, not excluded. Only the exact two explicitly approved injected controls are outside the prospective domain; their unchanged complete deltas and original strict failure remain retained. All other comparisons must pass. No real-target reachability is inferred.'}
with (OUT/'equivalence.json').open('x') as f:json.dump(packet,f,indent=2);f.write('\n')
print(json.dumps({'passed':passed,'explicit_domain_revision_authorization_sha256':hashlib.sha256((OUT/'authorization.json').read_bytes()).hexdigest(),'original_strict_failure_retained':True,'out_of_domain_negative_controls':['alias','shrink'],'ordinary_comparisons':len(ordinary),'controls':[{k:r[k] for k in ['control','equivalent']} for r in controls],'representative_operations':representative},indent=2))
raise SystemExit(0 if passed else 1)
