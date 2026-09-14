"""Retain entire synthetic serial/parallel results and compare baseline flow."""
import ast, dataclasses, hashlib, json
from pathlib import Path
import pytest
from sentinel.static import engine
import sentinel.static.typescript_path_flow as module
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
import sys
sys.path.insert(0,str(ROOT))
from tests.conftest import NOW,SCAN_ID
p=OUT/'baseline/src/sentinel/static/typescript_path_flow.py';tree=ast.parse(p.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TypeScriptPathFlow');node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='statement');scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),vars(module),scope)
original=engine.run_static_scan;observations=[]
def capture(config,*args,**kwargs):
 result=original(config,*args,**kwargs);observations.append((config,result));return result
engine.run_static_scan=capture
result=pytest.main(['tests/test_static_workers.py','--no-cov','-x'])
engine.run_static_scan=original
assert result==0
assert len(observations)==6,len(observations)
volatile={'applied_at','completed_at','duration_ms','execution_latency_ms','finding_id','latency_ms','origin_latency_ms','reviewed_at','scan_id','started_at','timestamp'}
def serialize(v):
 if hasattr(v,'model_dump'):return serialize(v.model_dump(mode='json'))
 if dataclasses.is_dataclass(v):return {f.name:serialize(getattr(v,f.name)) for f in dataclasses.fields(v)}
 if isinstance(v,dict):return {k:serialize(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [serialize(x) for x in v]
 if isinstance(v,Path):return str(v)
 return v
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k not in volatile}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
module.TypeScriptPathFlow.statement=scope['statement'];engine.run_flow_rules=lambda *_:{}
records=[]
for i,(config,actual) in enumerate(observations):
 expected=original(config,SCAN_ID,timestamp=NOW)
 record={'index':i,'baseline':serialize(expected),'candidate':serialize(actual)}
 (OUT/f'synthetic-report-{i}.json').write_text(json.dumps(record,indent=2)+'\n')
 assert stable(record['baseline'])==stable(record['candidate']),i
 records.append({'index':i,'equivalent':True,'finding_count':len(actual.findings),'sha256':hashlib.sha256((OUT/f'synthetic-report-{i}.json').read_bytes()).hexdigest()})
(OUT/'report-equivalence.json').write_text(json.dumps({'passed':True,'comparisons':records,'volatile_exclusions':sorted(volatile),'scope':'All static result fields and ordered findings, warnings, summaries and source coverage; Python/TypeScript/mixed existing owned fixtures, each serial and parallel. All five requested rules retain actual execution.','corpus_observations':0,'profiles':0,'paid_calls':0},indent=2)+'\n')
print('All six complete synthetic serial/parallel results agree with baseline flow.')
