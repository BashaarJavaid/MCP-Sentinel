"""One-use launch after exact approval, with an outer sequence deadline."""
import importlib.util
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('four_runner', ASSETS/'runner.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
signal.signal(signal.SIGTERM, r.supervisor.stopped)
proposal = r.verify_packet()
os.chdir(proposal['frozen_checkout'])
sys.path[:0] = [str(Path.cwd()/'src'), str(Path.cwd())]
r.approved()
assert not (ASSETS/'execution-consumed.json').exists()
for key in list(os.environ):
    if key.startswith(('OPENAI_', 'SENTINEL_')):
        os.environ.pop(key)
os.environ['PATH'] = '/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin:' + os.environ.get('PATH','')
out = ASSETS.parent/'v44-four-fresh-evaluation'
out.mkdir(exist_ok=False)
command = [sys.executable, '-I', str(ASSETS/'runner.py'), 'run', str(out/'raw')]
with (out/'launch.json').open('x') as f:
    json.dump({'command':command, 'cwd':str(Path.cwd()), 'started_at':datetime.now(timezone.utc).isoformat(), 'proposal_sha256':r.sha(r.PROPOSAL), 'approval_sha256':r.sha(r.APPROVAL), 'sequence_limit_seconds':9000, 'observations_maximum':24, 'paid_calls':0},f,indent=2);f.write('\n')
timing = r.supervisor.supervise(command, out/'sequence.log', 9000)
r.write(out/'execution.json', {'timing':timing, 'completed_at':datetime.now(timezone.utc).isoformat(), 'darwin_group_checks':r.DARWIN_GROUP_CHECKS, 'proposal_sha256':r.sha(r.PROPOSAL), 'paid_calls':0})
assert timing['cleanup_verified'] and not timing['timed_out'] and not timing['remaining_group_killed']
assert timing['elapsed_seconds'] <= 9000
raise SystemExit(timing['returncode'])
