"""One serial, uncapped, explicitly authorized experiment with retained cancellation cleanup."""
import importlib.util,json,os,signal,sys,time
from datetime import datetime,timezone
from pathlib import Path
ASSETS=Path(__file__).resolve().parent;OUT=ASSETS.parent/'v73-corrected-four-results'
spec=importlib.util.spec_from_file_location('uncapped_runner',ASSETS/'evaluate.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def preflight():
    p=r.verify();os.chdir(p['frozen_checkout']);sys.path[:0]=[str(Path.cwd()/'src'),str(Path.cwd())]
    r.approved()
    binding=json.loads((ASSETS/'launcher-binding.json').read_text())
    assert binding['proposal_sha256']==r.sha(r.PROPOSAL)
    assert binding['launcher_sha256']==r.sha(Path(__file__)) and binding['runner_sha256']==r.sha(ASSETS/'evaluate.py')
    assert binding['policy_sha256']==r.sha(ASSETS/'uncapped.py')
    assert not (ASSETS/'execution-consumed.json').exists() and not OUT.exists()
    for group in p['groups']:r.identity(group)
    return p

def main():
    if sys.argv[1:]==['check']:
        assert not r.APPROVAL.exists() and not OUT.exists()
        try:preflight()
        except FileNotFoundError as e:assert Path(e.filename)==r.APPROVAL
        else:raise AssertionError('Missing authorization accepted')
        assert not OUT.exists() and not (ASSETS/'execution-consumed.json').exists()
        print('Missing approval rejected before output/token/input; no observation.')
        return 0
    assert not sys.argv[1:]
    p=preflight()
    signal.signal(signal.SIGTERM,r.supervisor.stopped)
    signal.signal(signal.SIGINT,r.supervisor.stopped)
    for key in list(os.environ):
        if key.startswith(('OPENAI_','SENTINEL_')):os.environ.pop(key)
    os.environ['PATH']='/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin:'+os.environ.get('PATH','')
    OUT.mkdir(exist_ok=False);raw=OUT/'raw';raw.mkdir()
    started=time.monotonic()
    r.write(OUT/'launch.json',{'pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),'command':[sys.executable,'-I',str(Path(__file__))],'execution':'same-process evaluator; each input has its existing owned process group','cwd':str(Path.cwd()),'proposal_sha256':r.sha(r.PROPOSAL),'approval_sha256':r.sha(r.APPROVAL),'launcher_binding_sha256':r.sha(ASSETS/'launcher-binding.json'),'sequence_limit_seconds':None,'whole_input_limit_seconds':None,'observations_maximum':24,'paid_calls':0})
    error=None;code=0
    try:r.run(raw)
    except BaseException as e:error=f'{type(e).__name__}: {e}';code=1
    finally:
        packet=json.loads((raw/'packet.json').read_text())
        r.write(OUT/'execution.json',{'completed_at':datetime.now(timezone.utc).isoformat(),'elapsed_sequence_including_preparation_seconds':time.monotonic()-started,'returncode':code,'error':error,'proposal_sha256':r.sha(r.PROPOSAL),'approval_sha256':r.sha(r.APPROVAL),'attempts':len(packet['attempts']),'completed':sum(x['state']=='completed' for x in packet['attempts']),'budget_closed':packet['budget_closed'],'remaining':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False})
    if error:print(error,flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
