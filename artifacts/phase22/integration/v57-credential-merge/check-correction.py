"""Validate the authorized equal-marker delta before adding any bypass."""
import ast
import hashlib
import itertools
import json
from dataclasses import fields, replace
from pathlib import Path
from unittest.mock import patch

import sentinel.static.path_flow as module
import sentinel.static.rules.sent016 as credential
from sentinel.static.discovery import PythonProgram
from sentinel.static.model import RuleRunState

OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
namespace=dict(vars(credential))
tree=ast.parse((OUT/'baseline-sent016.py').read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CredentialFlow']
exec(compile(tree,str(OUT/'baseline-sent016.py'),'exec'),namespace)
BaselineFlow=namespace['CredentialFlow']
shared=dict(globals())
tree=ast.parse((BASE/'v55-singleton-combine/assess-failure.py').read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='state']
exec(compile(tree,'retained_structural_state','exec'),shared)
state=shared['state']
history=dict(globals(),out=OUT,old=BASE/'v55-singleton-combine',state=state,program=PythonProgram(()))
tree=ast.parse((BASE/'v56-canonical-unknown/check-synthetic.py').read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'kernel','exercise'}]
exec(compile(tree,'retained_identity_exercise','exec'),history)
kernel,exercise=history['kernel'],history['exercise']
with patch.object(credential,'CredentialFlow',BaselineFlow):
    before=exercise(kernel(OUT/'baseline-path-flow.py'),False,False)
    broad=exercise(kernel(BASE/'v55-singleton-combine/candidate-path-flow.py'),False,False)
    evicted=exercise(kernel(OUT/'baseline-path-flow.py'),False,True)
    narrow=exercise(kernel(BASE/'v56-canonical-unknown/candidate-path-flow.py'),False,True)
assert before['environment']!=broad['environment'] and evicted['environment']!=narrow['environment']

metadata={'sources':frozenset({'http:caller'}),'key':'caller','resolved':True,'contained':True,
          'locations':frozenset({('synthetic.py',1)}),'path_object':True,'repository_object':True,
          'instance':('synthetic.py','Instance'),'option_safe':True,'url_checks':frozenset({'host','scheme'}),
          'operator_credential':True,'credential_fallback':True,'credential_present':True,
          'maybe_missing':True,'maybe_none':True,'operator_opt_in':frozenset({'configured'}),
          'checked_path_parent':True,'collection_nonempty':True}
assert set(metadata)=={f.name for f in fields(module.Value)}
values=[module.UNKNOWN_VALUE,module.Value(),module.Value(**metadata)]
values.extend(module.Value(**{name:value}) for name,value in metadata.items())
values.extend([module.Value(key=key) for key in ['None','#missing','#ts:undefined']])
values.extend([replace(values[2],contained=False),replace(values[2],sources=frozenset()),replace(values[2],sources=frozenset(),contained=False)])
program=PythonProgram(())
count=0;deltas=[];cache_deltas=[]
for value_index,value in enumerate(values):
    for number,variant,marker,http in itertools.product((0,1,2,3,8),('shared','distinct','unequal','missing-first','missing-last'),('#absent:caller','#credential:excluded:caller','#credential:opt-in:FLAG'),(False,True)):
        branches=[]
        for index in range(number):
            current=value if variant=='shared' else replace(value)
            if variant=='unequal' and index%2:current=replace(value,key='different')
            branch={marker:current,'ordinary':module.Value(key='keep')}
            if variant=='missing-first' and index==0 or variant=='missing-last' and index==number-1:branch.pop(marker)
            if http and index%2==0:branch['#credential:http']=module.Value(contained=True)
            branches.append(branch)
        selected=[b for b in branches if b.get('#credential:http',module.UNKNOWN_VALUE).contained] or branches
        inputs=state(branches);outputs=[]
        for flow_type in (BaselineFlow,credential.CredentialFlow):
            flow=flow_type(program,RuleRunState(),float('inf'))
            (flow.opt_in_markers if marker.startswith('#credential:opt-in:') else flow.absent_markers).add(marker)
            env={'untouched':module.Value(key='keep')}
            flow.merge(env,branches)
            flow_before=state(flow)
            result=flow.conditioned_credential(module.Value(key='owner',operator_credential=True),env)
            outputs.append((env,flow_before,state(flow),state(result)))
        assert state(branches)==inputs
        old,new=outputs
        assert old[1]==new[1] and old[3]==new[3],(value_index,number,variant,marker,http)
        assert {k:v for k,v in old[0].items() if k!=marker}=={k:v for k,v in new[0].items() if k!=marker}
        equal=bool(selected) and all(b.get(marker,module.UNKNOWN_VALUE)==selected[0].get(marker,module.UNKNOWN_VALUE) for b in selected)
        if equal and marker in new[0]:assert new[0][marker] is selected[0].get(marker,module.UNKNOWN_VALUE)
        if old[0]!=new[0]:
            assert equal and not all(b.get(marker,module.UNKNOWN_VALUE) is selected[0].get(marker,module.UNKNOWN_VALUE) for b in selected)
            deltas.append({'case':count,'value_index':value_index,'branches':number,'variant':variant,'marker':marker,'http_selected':http,'before':state(old[0][marker]),'after':state(new[0][marker])})
        differing={k for k in old[2]['fields'] if old[2]['fields'][k]!=new[2]['fields'][k]}
        assert differing<={'credential_guard_cache'},differing
        if differing:
            assert old[0]!=new[0]
            cache_deltas.append({'case':count,'before':old[2]['fields']['credential_guard_cache'],'after':new[2]['fields']['credential_guard_cache'],'assessment':'Only cached input marker tuple differs, derived from the authorized join delta. Guard facts and conditioned credential result agree.'})
        count+=1
assert deltas
record={'passed':True,'cases':count,'value_fields':list(metadata),'values':state(values),'intended_marker_deltas':deltas,'downstream_guard_cache_deltas':cache_deltas,'no_unrelated_environment_or_flow_delta':True,'conditioned_credential_and_guard_facts_equal':True,'inputs_unchanged':True,'retained_failures':{'broad_original_reproduced':True,'canonical_eviction_original_reproduced':True},'baseline_sent016_sha256':sha(OUT/'baseline-sent016.py'),'corrected_sent016_sha256':sha(Path(credential.__file__)),'path_flow_unchanged':sha(Path(module.__file__))==sha(OUT/'baseline-path-flow.py'),'qualification':'The proposed equal-marker join intentionally changes the retained marker fields, including source-free guard metadata when the old unequal-identity path stripped it. These are exactly equal-marker-join deltas, not unrelated changes. Uncontained markers establish no new credential guard facts; cached input tuples retain their explicit derived deltas. No real-target reachability or detection performance claim.','corpus_observations':0,'profiles':0,'paid_calls':0}
assert record['path_flow_unchanged']
with (OUT/'correction-validation.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
with (OUT/'correction-only-sent016.py').open('xb') as stream:stream.write(Path(credential.__file__).read_bytes())
with (OUT/'correction-only-path-flow.py').open('xb') as stream:stream.write(Path(module.__file__).read_bytes())
print(f'Correction passed{count}cases;{len(deltas)}explicit equal-marker deltas and{len(cache_deltas)}derived cache-input deltas; both original failures reproduced.')
