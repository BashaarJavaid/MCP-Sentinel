import json,runpy,shutil,signal,sys,time
from pathlib import Path
root=Path('/private/tmp/mcp-phase22-options');out=root/'artifacts/phase22/integration/v46-four-source-regression/sampler-selfcheck';out.mkdir(exist_ok=False);worker=out/'worker.py';shutil.copyfile(str(root/'artifacts/phase22/integration/v46-four-source-regression/sampling-worker.py'),worker);sys.argv=['synthetic','synthetic'];n=runpy.run_path(str(worker),run_name='selfcheck')
sys.path[:0]=[str(root/'src'),str(root)]
from sentinel.static import path_flow
Value=path_flow.Value;combine=path_flow.combine;methods=(path_flow.PathFlow.merge,path_flow.PathFlow.call,path_flow._combine)
a=Value(key='a',sources=frozenset({'input'}),contained=True,url_checks=frozenset({'loopback'}));b=Value(key='b',maybe_none=True);c=Value(key='None');vectors=[[],[a],[a,a],[a,b],[a,b,a],[a,b,c]];expected=[combine(v) for v in vectors]
before=(signal.getsignal(signal.SIGPROF),signal.getitimer(signal.ITIMER_PROF));previous=n['start']();iterations=0;begin=time.process_time()
try:
 while time.process_time()-begin<0.25:
  assert [combine(v) for v in vectors]==expected;iterations+=1
finally:n['finish'](previous)
after=(signal.getsignal(signal.SIGPROF),signal.getitimer(signal.ITIMER_PROF));assert before==after;assert methods==(path_flow.PathFlow.merge,path_flow.PathFlow.call,path_flow._combine);n['snapshot'](True)
p=json.loads((out/'synthetic-cpu-samples.json').read_text());assert p['samples']>0 and sum(s['count'] for s in p['stacks'])==p['samples'];ids={f['id'] for f in p['frame_catalog']};assert all(set(s['frames'])<=ids for s in p['stacks']);assert p['events'].get('truncated_stacks',0)==0 and p['signal_and_timer_state_restored'];assert any(f['function']=='combine' or f['filename']==__file__ for f in p['frame_catalog'])
result={'synthetic_vectors':len(vectors),'iterations':iterations,'samples':p['samples'],'original_scanner_methods_identical':True,'same_value_results':True,'sample_count_and_frame_references_valid':True,'prior_signal_and_timer_restored':True,'full_source_input_executions':0,'new_paid_calls':0};(out/'packet.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
