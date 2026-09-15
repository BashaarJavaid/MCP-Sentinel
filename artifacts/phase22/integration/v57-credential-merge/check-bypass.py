"""Require complete bypass equivalence against the retained correction-only reference."""
import ast
import builtins
import copy
import hashlib
import itertools
import json
from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import sentinel.static.path_flow as module
import sentinel.static.typescript_path_flow as ts
import sentinel.static.rules.sent014 as options
import sentinel.static.rules.sent015 as urls
import sentinel.static.rules.sent016 as credential
from sentinel.static.discovery import PythonProgram
from sentinel.static.model import RuleRunState
from sentinel.static.typescript_discovery import TypeScriptProgram

OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((OUT/'correction-validation.json').read_text())['passed']
assert json.loads((BASE/'v57-correction-tests.json').read_text())['exit_code']==0
assert sha(Path(credential.__file__))==sha(OUT/'correction-only-sent016.py')
namespace=dict(vars(module))
tree=ast.parse((OUT/'correction-only-path-flow.py').read_text())
tree.body=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in {'combine','_combine'}]
exec(compile(tree,str(OUT/'correction-only-path-flow.py'),'exec'),namespace)
baseline=namespace['combine'];candidate=module.combine
shared=dict(globals())
tree=ast.parse((BASE/'v55-singleton-combine/assess-failure.py').read_text())
tree.body=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='state']
exec(compile(tree,'retained_structural_state','exec'),shared)
state=shared['state']
history=dict(globals(),state=state,program=PythonProgram(()))
tree=ast.parse((BASE/'v56-canonical-unknown/check-synthetic.py').read_text())
tree.body=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='exercise']
exec(compile(tree,'retained_eviction_exercise','exec'),history)
eviction=[]
for contained in (False,True):
    left=history['exercise'](namespace,contained,True)
    right=history['exercise'](dict(vars(module),combine=candidate),contained,True)
    assert left['environment']==right['environment'] and left['flow']==right['flow']
    eviction.append({'contained':contained,'environment_equal':True,'full_flow_equal':True,'baseline_identity':left['same_result_identity'],'candidate_identity':right['same_result_identity'],'baseline_cache':left['before_merge'],'candidate_cache':right['before_merge']})

full=module.Value(sources=frozenset({'http:caller'}),key='root',resolved=True,contained=True,
                 locations=frozenset({('synthetic.py',1)}),path_object=True,repository_object=True,
                 instance=('synthetic.py','Instance'),option_safe=True,url_checks=frozenset({'host','scheme'}),
                 operator_credential=True,credential_fallback=True,credential_present=True,maybe_missing=True,
                 maybe_none=True,operator_opt_in=frozenset({'selected'}),checked_path_parent=True,collection_nonempty=True)
values=[module.UNKNOWN_VALUE,module.Value(),full]
values.extend(module.Value(**{name:getattr(full,name)}) for name in full.__dataclass_fields__)
values.extend([module.Value(key=key) for key in ['None','#missing','#ts:undefined']])
values.extend([replace(full,contained=False),replace(full,sources=frozenset()),replace(full,sources=frozenset(),contained=False)])
pyprogram=PythonProgram(());tsprogram=TypeScriptProgram((),deadline=float('inf'))

def flows(metadata):
    py=credential.CredentialFlow(pyprogram,RuleRunState(),float('inf'))
    py.absent_markers.update({'#absent:root','#credential:excluded:root'})
    py.opt_in_markers.add('#credential:opt-in:FLAG')
    flow=urls.TypeScriptURLFlow(tsprogram,RuleRunState())
    if metadata:
        py.instance_alternatives['root']=(full,replace(full,key='other'))
        py.record_keys.add('root');py.members['root']={'field':'#member:root:field'}
        py.member_defaults['#member:root:field']=full;py.path_origins['root']=frozenset({'input'})
        flow.objects.update({'root':{'field':replace(full,key='leaf-root')},'other':{'field':replace(full,key='leaf-other')}})
        flow.record_roots.update({'root':'root','other':'root'})
        flow.normalized.update({'root','other'});flow.mobilecli_paths.add('root')
        flow.path_inputs.update({'root':frozenset({'input'}),'other':frozenset({'input','extra'})})
        flow.arrays.update({'root','other'})
        flow.array_states.update({'root':((full,),),'other':((replace(full,key='other'),),)})
        flow.conditions.update({'root':(frozenset({'guard'}),frozenset()),'other':(frozenset(),frozenset({'else'}))})
        flow.boundaries['boundary']=(full,replace(full,key='other'))
        flow.url_parts['root']=('url','hostname')
    return py,flow

cases=0
for value_index,value in enumerate(values):
    for number,key,warm,metadata in itertools.product((0,1,2,3,8),('','root','override'),('cold','empty','equal'),(False,True)):
        inputs=[value if index%2==0 else replace(value) for index in range(number)]
        if number>2:inputs[-1]=module.Value(key='other')
        initial=state(inputs);results=[]
        for kernel,cache in [(baseline,namespace['_combine']),(candidate,module._combine)]:
            cache.cache_clear()
            if warm=='empty':kernel([module.Value()])
            elif warm=='equal':kernel([replace(v) for v in inputs],key)
            py,flow=flows(metadata)
            with ExitStack() as stack:
                for target in (module,ts,options,urls,credential):stack.enter_context(patch.object(target,'combine',kernel))
                result=kernel(inputs,key)
                py_instance=py.combine_instances(inputs)
                ts_value=flow.combined(inputs,key)
                branches=[{'ordinary':result,'#absent:root':result,'#credential:opt-in:FLAG':result},{'ordinary':replace(result),'#absent:root':replace(result),'#credential:opt-in:FLAG':replace(result)}]
                env={};py.merge(env,branches)
                tsenv={};flow.merge(tsenv,[{'ordinary':ts_value,'#record:root':ts_value},{'ordinary':replace(ts_value)}])
                owner=py.conditioned_credential(module.Value(key='owner',operator_credential=True),env)
                results.append(state({'result':result,'instance_result':py_instance,'typescript_result':ts_value,'python_env':env,'typescript_env':tsenv,'python_flow':py,'typescript_flow':flow,'conditioned_owner':owner}))
            assert state(inputs)==initial
        assert results[0]==results[1],(value_index,number,key,warm,metadata)
        cases+=1

dispatch=[]
for inputs,key in [([],''),([module.UNKNOWN_VALUE],''),([module.Value()],''),([module.UNKNOWN_VALUE],'root'),([module.UNKNOWN_VALUE,module.UNKNOWN_VALUE],''),([full],''),([replace(full,sources=frozenset())],''),([module.Value(key='None')],''),([module.Value(key='#missing')],''),([module.Value(key='#ts:undefined')],'')]:
    tuple_call=Mock(wraps=builtins.tuple);cache_call=Mock(wraps=module._combine)
    with patch.dict(vars(module),tuple=tuple_call,_combine=cache_call):candidate(inputs,key)
    eligible=len(inputs)==1 and inputs[0] is module.UNKNOWN_VALUE and not key
    assert tuple_call.call_count==cache_call.call_count==int(not eligible)
    dispatch.append({'inputs':state(inputs),'key':key,'eligible':eligible,'tuple_calls':tuple_call.call_count,'cache_calls':cache_call.call_count})
assert sum(row['eligible'] for row in dispatch)==1
record={'passed':True,'semantic_cases':cases,'cache_eviction_cases':eviction,'dispatch_cases':dispatch,'complete_value_environment_and_structural_flow_equal':True,'inputs_unchanged':True,'reference':'Credential-marker-corrected reference, not original a36f696 semantics. Intended correction deltas remain separately recorded.','reference_path_flow_sha256':sha(OUT/'correction-only-path-flow.py'),'reference_sent016_sha256':sha(OUT/'correction-only-sent016.py'),'candidate_path_flow_sha256':sha(Path(module.__file__)),'candidate_sent016_sha256':sha(Path(credential.__file__)),'eligible_dispatches_avoided':1,'all_other_dispatches_retained':9,'corpus_observations':0,'profiles':0,'paid_calls':0,'native_speedup_claim':False}
with (OUT/'synthetic-validation.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
print(f'Bypass passed{cases}complete-value/Python/TypeScript state comparisons and2eviction cases; dispatch eligibility exact.')
