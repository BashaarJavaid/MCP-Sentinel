"""Bind the finite unchanged-timeout sequence; source-only approval cannot launch it."""
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = json.loads((out/'evaluation-proposal.json').read_text())
assert json.loads((out/'runner-boundaries.json').read_text())['passed']
assert not (out/'evaluation-authorization.json').exists()
assert not (out.parent/'v67-invalidation-regression').exists()
binding = {'status': 'prepared_not_approved_not_executed',
    'proposal_sha256': sha(out/'evaluation-proposal.json'),
    'launcher_sha256': sha(out/'launch.py'), 'runner_sha256': sha(out/'evaluate.py'),
    'command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', '-I', str(out/'launch.py')],
    'initial_cwd': str(out.parents[3]), 'child_cwd': p['frozen_checkout'],
    'sequence_maximum_seconds': p['bounds']['sequence_maximum_minutes'] * 60,
    'internal_stop_seconds': p['bounds']['internal_stop_minutes'] * 60,
    'native_observations_maximum': 205, 'scope_change': True,
    'approval_requirement': 'New numerical evaluation authorization must bind this launcher and exact proposal. The approved source-only invalidation change alone does not launch or reopen a budget.',
    'logic_reuse': {'runner_byte_identical': True, 'runner_boundaries_sha256': sha(out/'runner-boundaries.json'),
        'change': 'Byte-identical v59 evaluator, unchanged outer supervisor logic and one new output directory.'},
    'qualification': 'Thirty-minute native/whole input maximum; 6275-minute outer cap is a worst-case limit, not a duration estimate. Original sources, labels, order, 11 volatile exclusions and condition/coverage/cleanup/repeat requirements are unchanged. Earlier failures remain source-bound.',
    'paid_calls': 0, 'target_execution': False}
assert binding['sequence_maximum_seconds'] == 376500
assert binding['internal_stop_seconds'] == 376440
with (out/'launcher-binding.json').open('x') as stream:
    json.dump(binding, stream, indent=2)
    stream.write('\n')
print('Bound 30-minute input / 6275-minute sequence proposal; unapproved and unexecuted.')
