"""Exercise the actual parent loop with synthetic results and no scanner children."""
import importlib.util,json,tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runner',OUT/'evaluate.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
order=[{'group':'synthetic','input_id':'fixture-'+str(n),'batch':batch} for batch in ['first','repeat'] for n in range(48)]+[{'group':'synthetic','input_id':'single-'+str(n),'batch':'development'} for n in range(15)]
proposal={'order':order,'scanner':{'synthetic':True},'bounds':{'internal_stop_minutes':3454,'native_observations':111}}
results=[]
scenarios=['complete_with_failed_conditions','child_identity_failure','timeout','schema_failure','cleanup_failure','ordered_repeat_failure','cancelled','insufficient_outer_allowance']
for scenario in scenarios:
 with tempfile.TemporaryDirectory(prefix='phase22-unseen-loop-synthetic-') as tmp:
  assets=Path(tmp);raw=assets/'raw';raw.mkdir();(assets/'proposal.json').write_text('{}');(assets/'approval.json').write_text('{}');calls=[0]
  p={**proposal,'bounds':{**proposal['bounds'],'internal_stop_minutes':1 if scenario=='insufficient_outer_allowance' else 3454}}
  def supervise(command,log,limit):
   assert limit==1800 and command[1]=='-I';calls[0]+=1
   if scenario=='cancelled' and calls[0]==2:raise SystemExit('synthetic cancellation')
   _,input_id,dest=command[-3:];dest=Path(dest);(dest/input_id).mkdir(parents=True)
   report={'static_analysis':{'duration_ms':1},'findings':[{'synthetic_false_alert':True}],'warnings':['retained'],'timestamp':str(calls[0])}
   if scenario=='ordered_repeat_failure' and calls[0]==49:report['warnings'].append('changed')
   r.write(dest/input_id/'report.json',report);r.write(dest/'condition.json',{'source_assessment_pending':True,'condition_passed':False})
   return {'returncode':1 if scenario in ['child_identity_failure','schema_failure'] and calls[0]==2 else 0,'timed_out':scenario=='timeout' and calls[0]==2,'cleanup_verified':not(scenario=='cleanup_failure' and calls[0]==2),'remaining_group_killed':False,'elapsed_seconds':.01,'elapsed_including_cleanup_seconds':.02}
  with patch.object(r,'ASSETS',assets),patch.object(r,'PROPOSAL',assets/'proposal.json'),patch.object(r,'APPROVAL',assets/'approval.json'),patch.object(r,'approved',return_value=p),patch.object(r,'identity',lambda _:None),patch.object(r.supervisor,'supervise',supervise),patch.object(r.supervisor,'selfcheck',lambda _:None),patch.object(r,'selfcheck',lambda:None),(assets/'stdout.log').open('w') as log,redirect_stdout(log):
   try:r.run(raw)
   except (AssertionError,SystemExit):assert scenario!='complete_with_failed_conditions'
   else:assert scenario=='complete_with_failed_conditions'
  packet=json.loads((raw/'packet.json').read_text());expected=111 if scenario=='complete_with_failed_conditions' else 49 if scenario=='ordered_repeat_failure' else 0 if scenario=='insufficient_outer_allowance' else 2
  assert len(packet['attempts'])==expected and len(packet['unstarted'])==111-expected
  assert packet['budget_closed'] and packet['remaining_observation_budget']==0
  assert packet['passed']==(scenario=='complete_with_failed_conditions')
  assert sum(x.get('ordered_repeat_equal',False) for x in packet['attempts'])==(48 if packet['passed'] else 0)
  results.append({'scenario':scenario,'attempted':expected,'closed_unstarted':111-expected,'passed':True})
with (OUT/'collection-checks-current.json').open('x') as f:json.dump({'passed':True,'scenarios':results,'method':'Actual parent run with synthetic supervision only; real schema/identity approval is checked separately. Condition failures continue; execution/timeout/schema/cleanup/repeat/cancellation/outer-admission failures close budget.','corpus_observations':0,'paid_calls':0,'target_execution':False},f,indent=2);f.write('\n')
print('Eight synthetic collection, stop, budget-closure and ordered-repeat scenarios pass.')
