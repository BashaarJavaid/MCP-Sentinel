"""One separately approved worker-sampling input, never a regression retry."""
import importlib.util
import json
import os
import shutil
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[3]
PREVIOUS = ASSETS.parent/'v45-four-source-recovery'
OUT = ASSETS.parent/'v47-faf-sampling'
PROPOSAL = ASSETS/'diagnostic-proposal.json'
APPROVAL = ASSETS/'diagnostic-authorization.json'
spec = importlib.util.spec_from_file_location('bound_regression', PREVIOUS/'evaluate.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
sha, write = r.sha, r.write


def verify():
    plan = json.loads(PROPOSAL.read_text())
    for name, digest in plan['files_sha256'].items():
        assert sha(ROOT/name) == digest, name
    assert plan['bounds']['total_input_executions'] == 1
    assert json.loads((ASSETS/'raw/packet.json').read_text())['budget_closed']
    os.chdir(plan['frozen_checkout'])
    sys.path[:0] = [str(Path.cwd()/'src'), str(Path.cwd())]
    original, manifest, selected = r.identity('faf-read-root')
    assert original['scanner'] == plan['scanner']
    item = next(i for i in selected if i.id == plan['input']['input']['id'])
    assert item.model_dump(mode='json') == plan['input']['input']
    return plan, manifest.model_copy(update={'inputs': [item]})


def approved():
    plan, manifest = verify()
    decision = json.loads(APPROVAL.read_text())
    assert decision['approved'] is True and decision['user_decision'].strip()
    assert decision['proposal_sha256'] == sha(PROPOSAL)
    assert decision['scanner'] == plan['scanner'] and decision['bounds'] == plan['bounds']
    return plan, manifest


def child():
    from scripts import phase20_measurements as harness
    from sentinel.static import workers
    from sentinel.llm.semantic_reviewer import OpenAITransport
    plan, manifest = approved()
    token = json.loads((ASSETS/'diagnostic-consumed.json').read_text())
    assert token['proposal_sha256'] == sha(PROPOSAL) and token['output'] == str(OUT)
    async def forbidden(*_, **__):
        raise AssertionError('Live model transport forbidden')
    OpenAITransport.create = forbidden
    worker = OUT/'sampling-worker.py'
    assert sha(worker) == sha(ASSETS/'sampling-worker.py')
    original = harness.load_configuration
    def checked(*args, **kwargs):
        config = original(*args, **kwargs)
        assert config.static_only and config.scanner.scanner.rules_only
        assert r.prior.configuration(config) == plan['input']['configuration_sha256']
        return config
    # Only the existing worker entry point is wrapped; scanner methods stay intact.
    with patch.object(workers, 'WORKER', worker), patch.object(harness, 'load_configuration', checked):
        result = harness.measure(manifest, 'rules', OUT/'measurement', phase22_approval=Path.cwd()/plan['source_freeze_approval'])
    assert result['scanner'] == plan['scanner'] and result['manifest_sha256'] == plan['manifest_sha256']
    assert result['model_calls'] == 0 and not result['requests']
    assert len(result['outcomes']) == 1
    write(OUT/'child-result.json', {'outcomes': result['outcomes'], 'scanner': harness.scanner_identity(), 'paid_calls': 0})


def main():
    for key in list(os.environ):
        if key.startswith(('OPENAI_', 'SENTINEL_')):
            os.environ.pop(key)
    signal.signal(signal.SIGTERM, r.supervisor.stopped)
    if sys.argv[1:] == ['check']:
        verify()
        assert not APPROVAL.exists() and not OUT.exists() and not (ASSETS/'diagnostic-consumed.json').exists()
        try:
            approved()
        except FileNotFoundError as error:
            assert Path(error.filename) == APPROVAL
        else:
            raise AssertionError('Missing diagnostic approval accepted')
        print('Diagnostic source bindings verified; missing approval fails before output or budget mutation. Zero corpus executions.')
        return 0
    plan, _ = approved()
    if sys.argv[1:] == ['child']:
        child()
        return 0
    assert not sys.argv[1:]
    assert not OUT.exists() and not (ASSETS/'diagnostic-consumed.json').exists()
    OUT.mkdir()
    with (ASSETS/'diagnostic-consumed.json').open('x') as stream:
        json.dump({'proposal_sha256': sha(PROPOSAL), 'approval_sha256': sha(APPROVAL), 'output': str(OUT), 'attempts_consumed': 1}, stream, indent=2)
    shutil.copyfile(ASSETS/'sampling-worker.py', OUT/'sampling-worker.py')
    command = [sys.executable, '-I', str(Path(__file__).resolve()), 'child']
    write(OUT/'attempt.json', {'started_at': datetime.now(timezone.utc).isoformat(), 'command': command, 'cwd': str(Path.cwd()), 'proposal_sha256': sha(PROPOSAL), 'approval_sha256': sha(APPROVAL), 'scanner': plan['scanner'], 'total_input_executions': 1, 'paid_calls': 0})
    try:
        timing = r.supervisor.supervise(command, OUT/'observation.log', 300)
        write(OUT/'execution.json', {'timing': timing, 'darwin_group_checks': r.prior.DARWIN_GROUP_CHECKS, 'completed_at': datetime.now(timezone.utc).isoformat(), 'remaining': 0, 'budget_closed': True, 'paid_calls': 0})
        assert timing['cleanup_verified']
        assert timing['elapsed_including_cleanup_seconds'] - timing['elapsed_seconds'] <= 15
    finally:
        write(OUT/'budget-closed.json', {'remaining': 0, 'budget_closed': True, 'retries': 0, 'paid_calls': 0})
    return timing['returncode']


if __name__ == '__main__':
    raise SystemExit(main())
