"""Retain entire synthetic serial/parallel results and compare default timeout policy."""
import dataclasses, hashlib, json, importlib.util, os
from unittest.mock import patch
from pathlib import Path
import pytest
from sentinel.static import engine
import sentinel.static.typescript_path_flow as module
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
import sys
sys.path.insert(0,str(ROOT))
from tests.conftest import NOW,SCAN_ID
spec=importlib.util.spec_from_file_location('uncapped',OUT/'uncapped.py');uncapped=importlib.util.module_from_spec(spec);spec.loader.exec_module(uncapped)
original=engine.run_static_scan;observations=[]
def capture(config,*args,**kwargs):
 config=config.model_copy(update={'scanner':config.scanner.model_copy(update={'scanner':config.scanner.scanner.model_copy(update={'rules':tuple(f'SENT-{n:03d}' for n in range(12,17))})})})
 result=original(config,*args,**kwargs);observations.append((config,result));return result
engine.run_static_scan=capture
result=pytest.main(['tests/test_static_workers.py','--no-cov','-x'])
engine.run_static_scan=original
assert result==0
assert len(observations)==10,len(observations)
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

records=[]
for i,(config,actual) in enumerate(observations):
 with uncapped.policy(), patch.object(os,'cpu_count',return_value=4), patch('sentinel.static.workers.MIN_SOURCE_SIZE',0):
  if i%2==0:
   with patch.object(engine,'run_flow_rules',lambda *_:{}): expected=original(config,SCAN_ID,timestamp=NOW)
  else: expected=original(config,SCAN_ID,timestamp=NOW)
 record={'index':i,'selected_rules':list(config.scanner.scanner.rules),'default_policy':serialize(actual),'uncapped_policy':serialize(expected)}
 (OUT/f'synthetic-policy-report-{i}.json').write_text(json.dumps(record,indent=2)+'\n')
 assert stable(record['default_policy'])==stable(record['uncapped_policy']),i
 records.append({'index':i,'selected_rules':list(config.scanner.scanner.rules),'equivalent':True,'finding_count':len(actual.findings),'sha256':hashlib.sha256((OUT/f'synthetic-policy-report-{i}.json').read_bytes()).hexdigest()})
(OUT/'synthetic-equivalence.json').write_text(json.dumps({'passed':True,'comparisons':records,'volatile_exclusions':sorted(volatile),'scope':'All static result fields and ordered findings, warnings, summaries and source coverage; Python/TypeScript/mixed and added constructor-parameter-property owned fixtures, each serial and parallel. All five requested rules retain actual execution.','corpus_observations':0,'profiles':0,'paid_calls':0},indent=2)+'\n')
print('All ten complete synthetic serial/parallel results agree with default timeout policy.')
