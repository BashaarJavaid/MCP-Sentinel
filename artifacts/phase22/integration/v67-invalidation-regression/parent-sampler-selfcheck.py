"""Exercise actual diagnostic parent wrapping with synthetic work only."""
import importlib.util,json,signal,shutil,sys,time
from pathlib import Path
from unittest.mock import patch
assets=Path(__file__).resolve().parent;out=assets/'parent-sampler-selfcheck';out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('diagnostic',assets/'diagnostic.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
sampler=d.load_sampler();identity=sampler.verify_scanner()
from scripts import phase20_measurements as harness
from sentinel.static import workers,typescript_discovery,typescript_path_flow
methods=(workers.run_flow_rules,typescript_discovery.TypeScriptProgram.tools,typescript_path_flow.TypeScriptPathFlow.merge)
rows=[]
for fail in [False,True]:
 stage=out/('interrupted' if fail else 'completed');a=stage/'assets';o=stage/'output';a.mkdir(parents=True);o.mkdir()
 for destination in [a,o]:shutil.copyfile(assets/'corrected-sampling-worker.py',destination/'corrected-sampling-worker.py')
 proposal=a/'diagnostic-proposal.json';proposal.write_text('{}\n')
 (a/'diagnostic-consumed.json').write_text(json.dumps({'proposal_sha256':d.sha(proposal),'output':str(o)}))
 plan={'scanner':identity['scanner'],'manifest_sha256':'synthetic','source_freeze_approval':'synthetic-only','input':{'configuration_sha256':'unused-no-configuration-access'}}
 def measure(manifest,treatment,destination,**kwargs):
  assert manifest=='synthetic-only' and treatment=='rules' and destination==o/'measurement'
  assert workers.WORKER==o/'corrected-sampling-worker.py'
  begin=time.process_time();total=0
  while time.process_time()-begin<0.3:total+=sum(range(100))
  if fail:raise KeyboardInterrupt('synthetic interruption')
  return {'scanner':identity['scanner'],'manifest_sha256':'synthetic','model_calls':0,'requests':{},'outcomes':[{'state':'synthetic'}]}
 before=(signal.getsignal(signal.SIGPROF),signal.getitimer(signal.ITIMER_PROF));original_worker=workers.WORKER
 with patch.multiple(d,ASSETS=a,OUT=o,PROPOSAL=proposal),patch.object(d,'approved',return_value=(plan,'synthetic-only')),patch.object(harness,'measure',measure):
  try:d.child()
  except KeyboardInterrupt:assert fail
  else:assert not fail
 assert (signal.getsignal(signal.SIGPROF),signal.getitimer(signal.ITIMER_PROF))==before
 assert workers.WORKER==original_worker
 assert methods==(workers.run_flow_rules,typescript_discovery.TypeScriptProgram.tools,typescript_path_flow.TypeScriptPathFlow.merge)
 snapshot=json.loads((o/'parent-cpu-samples.json').read_text());assert snapshot['samples']>0 and snapshot['final_worker_snapshot'] and snapshot['signal_and_timer_state_restored']
 assert sum(s['count'] for s in snapshot['stacks'])==snapshot['samples']
 assert json.loads((o/'parent-worker-identity.json').read_text())['scanner']==identity['scanner']
 assert (o/'child-result.json').exists()==(not fail)
 rows.append({'interrupted':fail,'samples':snapshot['samples'],'restored':True,'source_identity':identity,'actual_parent_wrapper_exercised':True})
# Actual verify() must check the in-process source identity before input access.
stage=out/'identity-order';stage.mkdir();p=stage/'diagnostic-proposal.json';p.write_text(json.dumps({'files_sha256':{},'bounds':{'total_input_executions':1},'frozen_checkout':str(sampler.root)}));(stage/'budget-closed.json').write_text('{"budget_closed":true}')
class Invalid:
 def verify_scanner(self):raise AssertionError('synthetic stale parent identity')
with patch.multiple(d,ASSETS=stage,PROPOSAL=p),patch.object(d,'load_sampler',return_value=Invalid()),patch.object(d.r,'identity',side_effect=AssertionError('target access before identity')):
 try:d.verify()
 except AssertionError as error:assert str(error)=='synthetic stale parent identity'
 else:raise AssertionError('stale identity accepted')
result={'passed':True,'parent_wrapper_cases':rows,'stale_parent_rejected_before_target_access':True,'scanner_methods_unchanged':True,'target_execution':False,'full_source_input_executions':0,'paid_calls':0}
(out/'packet.json').write_text(json.dumps(result,indent=2)+'\n');print('Parent completion/interruption restore timers and worker entry; stale parent rejects before input access. Zero corpus executions.')
