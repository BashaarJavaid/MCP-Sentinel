"""One-use launch of the separately approved sequence, with an outer deadline."""
import importlib.util
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recovery_runner', ASSETS/'evaluate.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
OUT = ASSETS.parent/'v67-invalidation-regression'
BINDING = ASSETS/'launcher-binding.json'

def preflight():
    proposal = r.verify()
    binding = json.loads(BINDING.read_text())
    assert binding['proposal_sha256'] == r.sha(r.PROPOSAL)
    assert binding['launcher_sha256'] == r.sha(Path(__file__).resolve())
    assert binding['runner_sha256'] == r.sha(ASSETS/'evaluate.py')
    os.chdir(proposal['frozen_checkout'])
    sys.path[:0] = [str(Path.cwd()/'src'), str(Path.cwd())]
    r.approved()
    approval = json.loads(r.APPROVAL.read_text())
    assert approval['launcher_binding_sha256'] == r.sha(BINDING)
    assert not (ASSETS/'execution-consumed.json').exists()
    assert not OUT.exists()
    return proposal

def main():
    if sys.argv[1:] == ['check']:
        assert not r.APPROVAL.exists() and not OUT.exists()
        try:
            preflight()
        except FileNotFoundError as error:
            assert Path(error.filename) == r.APPROVAL
        else:
            raise AssertionError('Missing approval accepted')
        assert not OUT.exists() and not (ASSETS/'execution-consumed.json').exists()
        print('Missing approval rejected before launch/output/budget mutation; zero observations.')
        return 0
    assert not sys.argv[1:]
    proposal = preflight()
    signal.signal(signal.SIGTERM, r.supervisor.stopped)
    for key in list(os.environ):
        if key.startswith(('OPENAI_', 'SENTINEL_')):
            os.environ.pop(key)
    os.environ['PATH'] = '/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin:' + os.environ.get('PATH', '')
    OUT.mkdir(exist_ok=False)
    command = [sys.executable, '-I', str(ASSETS/'evaluate.py'), 'run', str(OUT/'raw')]
    assert command == proposal['prepared_command']
    limit = proposal['bounds']['sequence_maximum_minutes'] * 60
    with (OUT/'launch.json').open('x') as stream:
        json.dump({'command': command, 'cwd': str(Path.cwd()), 'started_at': datetime.now(timezone.utc).isoformat(),
                   'proposal_sha256': r.sha(r.PROPOSAL), 'approval_sha256': r.sha(r.APPROVAL),
                   'launcher_binding_sha256': r.sha(BINDING), 'sequence_limit_seconds': limit,
                   'observations_maximum': 205, 'paid_calls': 0}, stream, indent=2)
        stream.write('\n')
    timing = r.supervisor.supervise(command, OUT/'sequence.log', limit)
    r.write(OUT/'execution.json', {'timing': timing, 'completed_at': datetime.now(timezone.utc).isoformat(),
                                 'darwin_group_checks': r.prior.DARWIN_GROUP_CHECKS,
                                 'proposal_sha256': r.sha(r.PROPOSAL), 'paid_calls': 0})
    assert timing['cleanup_verified'] and not timing['timed_out'] and not timing['remaining_group_killed']
    assert timing['elapsed_seconds'] <= limit
    return timing['returncode']

if __name__ == '__main__':
    raise SystemExit(main())
