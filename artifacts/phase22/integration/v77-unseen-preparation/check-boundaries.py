"""Scanner-owned synthetic schema, approval, timing and process controls only."""
import ast,copy,importlib.util,json,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
r=load('unseen_runner',OUT/'evaluate.py');c=load('unseen_corpus',OUT/'corpus.py')
r.selfcheck()
good=dict(returncode=0,timed_out=False,cleanup_verified=True,remaining_group_killed=False,elapsed_seconds=1800,elapsed_including_cleanup_seconds=1815)
r.completed(good)
for change in [{'elapsed_seconds':1800.001},{'returncode':1},{'timed_out':True},{'cleanup_verified':False},{'remaining_group_killed':True},{'elapsed_including_cleanup_seconds':1815.001}]:
 try:r.completed({**good,**change})
 except AssertionError:pass
 else:raise AssertionError(change)
# Build synthetic records from scratch: no real candidate is passed to any scanner.
a={'path':'fixture.json','sha256':'0'*64};snapshots=[];inputs=[];pairs=[]
for k,(repo,lang,rule) in enumerate([('synthetic/python','python','SENT-012'),('synthetic/typescript','typescript','SENT-002')]):
 family='synthetic-'+lang
 pairs.append({'id':family,'rule_id':rule,'fix_origin':'upstream','provenance':[a],'review':'synthetic'})
 for j in [1,2]:snapshots.append({'repository':repo,'revision':str(k*2+j)*40,'url':'https://example.invalid/source','archive':a,'files':{'LICENSE':'0'*64},'licenses':['LICENSE']})
 for label in ['vulnerable','fixed','safe']:
  inputs.append({'id':family+'-'+label,'family':family,'repository':repo,'language':lang,'split':'held_out','variant':'safe_control' if label=='safe' else 'original','label':label,'snapshot':str(k*2+(1 if label=='vulnerable' else 2))*40,'scan_root':'.','condition':'synthetic','prerequisites':['synthetic'],'static_applicability':'synthetic','runtime_applicability':'unsupported','runtime_reason':'synthetic','runtime_configuration':None,'evidence':[{'path':'synthetic.py','start_line':1,'end_line':1,'sha256':'0'*64,'role':'synthetic'}],'matching':'synthetic','tree_sha256':'0'*64})
data={'version':1,'status':'proposed_pending_user_freeze','freeze_approved':False,'methodology':'synthetic','snapshots':snapshots,'pairs':pairs,'inputs':inputs,'packet':[a],'repository_aliases':{'synthetic/python':'synthetic/python','synthetic/typescript':'synthetic/typescript'}}
assert len(c.Manifest.model_validate(data).inputs)==6
bad=[]
x=copy.deepcopy(data);x['inputs'].pop();bad.append(x)
x=copy.deepcopy(data);x['inputs'][1]=x['inputs'][0];bad.append(x)
for key,value in [('snapshot','9'*40),('repository','unbound/repository'),('split','development'),('runtime_applicability','eligible'),('parent','parent'),('overlay',a),('transformation','mutation'),('scan_root','../escape')]:
 x=copy.deepcopy(data);x['inputs'][0][key]=value;bad.append(x)
x=copy.deepcopy(data);x['inputs'][2]['tree_sha256']='1'*64;bad.append(x)
x=copy.deepcopy(data);x['repository_aliases']={};bad.append(x)
x=copy.deepcopy(data);x['pairs'][0]['rule_id']='SENT-002';bad.append(x)
for x in bad:
 try:c.Manifest.model_validate(x)
 except ValueError:pass
 else:raise AssertionError('bad synthetic manifest admitted')
with tempfile.TemporaryDirectory(prefix='phase22-unseen-approval-control-') as tmp:
 approval=Path(tmp)/'missing.json'
 with patch.object(c.existing,'validate',side_effect=AssertionError('target validation reached')):
  try:c.frozen(approval_path=approval)
  except FileNotFoundError:pass
  else:raise AssertionError('missing approval admitted')
  approval.write_text(json.dumps({'corpus':{'manifest':'manifest.json','sha256':'0'*64,'freeze_approved':False}}))
  try:c.frozen(approval_path=approval)
  except ValueError:pass
  else:raise AssertionError('false approval admitted')
# Preserve full supervised cleanup controls, including stubborn/orphan child processes.
synthetic=OUT/'supervisor-selfcheck';synthetic.mkdir(exist_ok=False);r.supervisor.selfcheck(synthetic)
assert not r.APPROVAL.exists() and not (OUT/'execution-consumed.json').exists()
assert not (OUT.parent/'v78-unseen-results').exists()
for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
result={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'schema_negative_controls':len(bad),'deadline_controls':7,'approval_controls':2,'ordered_comparison_and_provisional_condition_checks':True,'supervisor_synthetic_controls':r.sha(synthetic/'selfcheck.json'),'runner_sha256':r.sha(OUT/'evaluate.py'),'launcher_sha256':r.sha(OUT/'launch.py'),'corpus_adapter_sha256':r.sha(OUT/'corpus.py'),'adapter_scope':'Artifact-local six-input population validation and SENT-002/012 pair IDs only. Existing source/path/archive/hash/license checks, approval gate and production measure behavior reused. No scanner/test/harness/lock changes.','corpus_observations':0,'paid_calls':0,'target_execution':False}
with (OUT/'runner-boundaries.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('Synthetic schema/approval/deadline/ordered-report/process-cleanup checks passed; zero corpus observations.')
