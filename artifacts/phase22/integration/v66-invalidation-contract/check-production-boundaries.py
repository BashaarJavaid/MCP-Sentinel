"""Compare real If methods, conservative calls and partial interruption states."""
import ast,copy,dataclasses,hashlib,itertools,json,tempfile,types,time
from pathlib import Path
from unittest.mock import patch
import sentinel.static.typescript_path_flow as module
from sentinel.errors import InfrastructureError
from sentinel.static.model import TypeScriptSourceFile,RuleRunState
from sentinel.static.path_flow import Value
from sentinel.static.typescript_discovery import TypeScriptProgram,TypeScriptSymbol
from sentinel.static.typescript_execution import ShellFlow
from sentinel.static.typescript_registration_flow import RegistrationFlow,HTTPRegistrationFlow
from sentinel.static.rules.sent014 import TypeScriptOptionFlow
from sentinel.static.rules.sent015 import TypeScriptURLFlow
from sentinel.static.rules.sent016 import TypeScriptCredentialFlow
OUT=Path(__file__).resolve().parent
helper=ast.parse((OUT/'verify-production-flow.py').read_text());scope={};exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='canonical'],type_ignores=[]),'<retained canonical>','exec'),globals(),scope);canonical=scope['canonical']
tree=ast.parse((OUT/'baseline/src/sentinel/static/typescript_path_flow.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptPathFlow');node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='statement');scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<preserved baseline statement>','exec'),vars(module),scope);baseline=scope['statement'];candidate=module.TypeScriptPathFlow.statement
flows=[module.TypeScriptPathFlow,ShellFlow,RegistrationFlow,HTTPRegistrationFlow,TypeScriptOptionFlow,TypeScriptURLFlow,TypeScriptCredentialFlow]
records=[]
with tempfile.TemporaryDirectory(prefix='v66-owned-ast-') as tmp:
 path=Path(tmp)/'server.ts';source='if (unknown()) { unknown(left); } else { unknown(right); }';path.write_text(source);file=TypeScriptSourceFile(path,'server.ts',source);parsed=TypeScriptProgram((file,),deadline=time.monotonic()+30);node=parsed.trees['server.ts']['Pr'][0]
 def run(method,flow_type,exception,stop,prealias):
  program=TypeScriptProgram((file,),deadline=1e99,trees=parsed.trees)
  flow=flow_type(program,TypeScriptSymbol(file,node)) if flow_type in {RegistrationFlow,HTTPRegistrationFlow} else flow_type(program,RuleRunState())
  original={'baseline'};flow.invalidated_objects=original
  flow.objects.update({'left':{},'right':{}})
  if prealias:flow.arrays=original
  env={name:Value(key=name,sources=frozenset({'owned-synthetic'}),operator_credential=True) for name in ['left','right']};returned=[];count=0;result=None;error=None
  def tick(_):
   nonlocal count
   count+=1
   if count==stop:raise exception('owned synthetic boundary')
  with patch.object(module.TypeScriptPathFlow,'statement',method),patch.object(module,'check_deadline',tick):
   try:result=flow.statement(file,node,env,returned)
   except (RuntimeError,KeyboardInterrupt,InfrastructureError) as e:error=type(e).__name__
  return {'state':canonical((vars(flow),env,returned,result)),'error':error,'deadline_calls':count,'original_set':sorted(original),'arrays_is_original':flow.arrays is original,'invalidated_is_original':flow.invalidated_objects is original,'final_invalidations':sorted(flow.invalidated_objects)}
 for flow_type,exception,stop,prealias in itertools.product(flows,[RuntimeError,KeyboardInterrupt,InfrastructureError],[1,2,4,8,16,99],[False,True]):
  expected=run(baseline,flow_type,exception,stop,prealias);actual=run(candidate,flow_type,exception,stop,prealias)
  assert expected==actual,(flow_type.__name__,exception.__name__,stop,prealias)
  if stop==99:assert {'baseline','left','right'}<=set(actual['final_invalidations'])
  records.append({'flow':flow_type.__name__,'exception':exception.__name__,'stop':stop,'preexisting_alias':prealias,'error':actual['error'],'deadline_calls':actual['deadline_calls'],'complete_state_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True).encode()).hexdigest()})
(OUT/'production-boundaries.json').write_text(json.dumps({'passed':True,'comparisons':records,'comparison_count':len(records),'full_state_and_original_aliases_equal':True,'unknown_target_calls_still_invalidate_all_feasible_arms':True,'corpus_observations':0,'profiles':0,'paid_calls':0},indent=2)+'\n')
print(len(records),'complete real-flow boundary comparisons passed.')
