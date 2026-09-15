"""Check uncapped waits, unchanged finite waits, restoration and cancellation without corpus input."""
import ast,hashlib,importlib.util,json,math,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
out=Path(__file__).resolve().parent;root=out.parents[3];sys.path[:0]=[str(root/'src'),str(root)]
spec=importlib.util.spec_from_file_location('runner',out/'evaluate.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
from sentinel import orchestrator
from sentinel.static import engine,semgrep_adapter
from sentinel.static.execution import check_deadline
old=(subprocess.run,subprocess.Popen.wait,engine.STATIC_TIMEOUT_SECONDS,orchestrator.STATIC_TIMEOUT_SECONDS,semgrep_adapter.SEMGREP_TIMEOUT_SECONDS)
with r.uncapped.policy():
 assert engine.STATIC_TIMEOUT_SECONDS==orchestrator.STATIC_TIMEOUT_SECONDS==math.inf and semgrep_adapter.SEMGREP_TIMEOUT_SECONDS==0
 check_deadline(math.inf);engine._enforce_timeout(math.inf)
 assert subprocess.run([sys.executable,'-I','-c','print(7)'],timeout=math.inf,capture_output=True,text=True).stdout.strip()=='7'
 p=subprocess.Popen([sys.executable,'-I','-c','pass']);assert p.wait(timeout=math.inf)==0
 try:subprocess.run([sys.executable,'-I','-c','import time; time.sleep(10)'],timeout=.02)
 except subprocess.TimeoutExpired:pass
 else:raise AssertionError('Finite subprocess timeout changed')
 try:check_deadline(0)
 except Exception:pass
 else:raise AssertionError('Finite deadline changed')
assert old==(subprocess.run,subprocess.Popen.wait,engine.STATIC_TIMEOUT_SECONDS,orchestrator.STATIC_TIMEOUT_SECONDS,semgrep_adapter.SEMGREP_TIMEOUT_SECONDS)
try:
 with r.uncapped.policy():raise RuntimeError('synthetic interruption')
except RuntimeError:pass
assert old==(subprocess.run,subprocess.Popen.wait,engine.STATIC_TIMEOUT_SECONDS,orchestrator.STATIC_TIMEOUT_SECONDS,semgrep_adapter.SEMGREP_TIMEOUT_SECONDS)
good=dict(returncode=0,timed_out=False,cleanup_verified=True,remaining_group_killed=False,elapsed_seconds=10**9,elapsed_including_cleanup_seconds=10**9+15)
r.completed(good)
for delta in [{'returncode':1},{'timed_out':True},{'cleanup_verified':False},{'remaining_group_killed':True},{'elapsed_including_cleanup_seconds':10**9+15.001}]:
 try:r.completed(good|delta)
 except AssertionError:pass
 else:raise AssertionError(delta)
r.selfcheck()
synthetic=out/'supervisor-selfcheck';synthetic.mkdir(exist_ok=False);r.supervisor.selfcheck(synthetic)
with r.uncapped.unlimited_waits():
 unlimited=r.supervisor.supervise([sys.executable,'-I','-c','import time; time.sleep(.05)'],synthetic/'uncapped.log',math.inf)
 assert unlimited['cleanup_verified'] and not unlimited['timed_out'] and unlimited['returncode']==0
 previous=signal.signal(signal.SIGALRM,r.supervisor.stopped)
 try:
  signal.setitimer(signal.ITIMER_REAL,.1)
  try:r.supervisor.supervise([sys.executable,'-I','-c','import time; time.sleep(10)'],synthetic/'manual-cancellation.log',math.inf)
  except SystemExit:pass
  else:raise AssertionError('Cancellation swallowed')
 finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
# Identity-sensitive scanner/detector/cleanup methods remain original; only deadline values/waits override.
assert not subprocess.check_output(['git','diff','cec0322e904bbf63c33cd95796e7289101a93e5d','--','src','tests','scripts','schemas','.github','uv.lock','pyproject.toml','CHANGELOG.md'])
for p in out.glob('*.py'):ast.parse(p.read_text())
record={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'infinite_run_and_worker_wait':True,'finite_timeouts_and_expired_deadline_retained':True,'normal_and_exception_policy_restoration':True,'arbitrarily_long_completed_timing_accepted':True,'execution_cleanup_and_repeat_failures_still_rejected':True,'uncapped_supervisor':unlimited,'manual_cancellation':'Synthetic SIGALRM interrupts the same uncapped supervisor; existing finally cleanup completed. Production arms no automatic alarm.','cleanup_policy':'Existing5-second grace stages retained,15-second allowance verified for completed inputs; no scan duration cap.','semgrep_timeout_reference':'https://docs.semgrep.dev/cli-reference#scan','semgrep_timeout_semantics':'--timeout 0 disables the rule/file time limit; other parser/coverage/resource rules remain unchanged.','source_bytes_unchanged':True,'corpus_observations':0,'profiles':0,'paid_calls':0}
(out/'boundary-checks.json').write_text(json.dumps(record,indent=2)+'\n');print('Uncapped waits, unchanged finite controls, cleanup/cancellation and restoration verified with zero corpus input.')
