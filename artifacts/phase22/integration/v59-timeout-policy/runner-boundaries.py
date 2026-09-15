"""Verify only prospective deadlines change; exercise existing stop and condition checks."""
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
old = out.parent / 'v57-credential-merge'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sys.path[:0] = [str(root / 'src'), str(root)]
expected = (old / 'evaluate.py').read_text()
for before, after, count in [
    ('STATIC_TIMEOUT_SECONDS == 300', 'STATIC_TIMEOUT_SECONDS == 1800', 1),
    ('["duration_ms"] <= 300000', '["duration_ms"] <= 1800000', 1),
    ('time.monotonic() + 315', 'time.monotonic() + 1815', 2),
    ('out / (label + ".log"), 300)', 'out / (label + ".log"), 1800)', 1),
    ('prior.completed(row["timing"])', 'completed(row["timing"])', 1),
]:
    assert expected.count(before) == count
    expected = expected.replace(before, after)
helper = '''def completed(timing):
    assert timing["returncode"] == 0 and not timing["timed_out"]
    assert timing["cleanup_verified"] and not timing["remaining_group_killed"]
    assert timing["elapsed_seconds"] <= 1800
    assert timing["elapsed_including_cleanup_seconds"] - timing["elapsed_seconds"] <= 15


'''
expected = expected.replace('def run(out):', helper + 'def run(out):')
assert (out / 'evaluate.py').read_text() == expected
assert (out / 'launch.py').read_text() == (old / 'launch.py').read_text().replace('v58-credential-regression', 'v60-long-timeout-regression')
spec = importlib.util.spec_from_file_location('timeout_runner', out / 'evaluate.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
r.selfcheck()
good = dict(returncode=0, timed_out=False, cleanup_verified=True,
            remaining_group_killed=False, elapsed_seconds=1800,
            elapsed_including_cleanup_seconds=1815)
for elapsed in [301, 1800]:
    r.completed({**good, 'elapsed_seconds': elapsed, 'elapsed_including_cleanup_seconds': elapsed + 15})
bad = [
    {'elapsed_seconds': 1800.0001, 'elapsed_including_cleanup_seconds': 1800.0001},
    {'returncode': 1}, {'timed_out': True}, {'cleanup_verified': False},
    {'remaining_group_killed': True}, {'elapsed_including_cleanup_seconds': 1815.0001},
]
for override in bad:
    try:
        r.completed({**good, **override})
    except AssertionError:
        pass
    else:
        raise AssertionError(override)
synthetic = out / 'supervisor-selfcheck'
synthetic.mkdir(exist_ok=False)
r.supervisor.selfcheck(synthetic)
assert not (out / 'evaluation-authorization.json').exists()
assert not (out.parent / 'v60-long-timeout-regression').exists()
packet = {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(),
          'deadline_controls': 8, 'existing_condition_controls_passed': True,
          'existing_synthetic_supervisor_controls_passed': True,
          'runner_delta': 'Only the scanner/native/whole deadline and admission reserve change from 300/315 to 1800/1815. Local completed validation preserves prior cleanup/failure checks; old historical helpers are not modified.',
          'launcher_delta': 'Only the output directory changes. Outer deadline is read from the new proposal.',
          'files_sha256': {str(p.relative_to(root)): sha(p) for p in [Path(__file__), out/'evaluate.py', out/'launch.py', old/'evaluate.py', old/'launch.py', Path(r.supervisor.__file__)]},
          'synthetic_files_sha256': {str(p.relative_to(out)): sha(p) for p in synthetic.rglob('*') if p.is_file()},
          'corpus_observations': 0, 'profiles': 0, 'paid_calls': 0, 'target_execution': False}
with (out / 'runner-boundaries.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print('Eight deadline controls and existing condition/process supervisor controls pass; zero corpus observations.')
