"""Bind existing state before any new repository research; never scan targets."""
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/private/tmp/mcp-phase22-options')
OUT = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/phase22/integration/v76-technical-acceptance'
FROZEN = Path('/private/tmp/mcp-phase22-frozen-cec0322')
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from scripts.phase20_measurements import scanner_identity
import sentinel

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd, text=True)

def save(name, data):
    with (OUT / name).open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    return {'path': (OUT / name).relative_to(ROOT).as_posix(), 'sha256': sha(OUT / name)}

identity = scanner_identity()
assert identity['revision'] == '09fa6ce8541fde5deb1f45055ac9e6de5c8c391c'
assert identity['source_sha256'] == '8c8aeb9937930315b0c2ba38685d3e5ac71275cc05946cbae3c790697bdf4099'
assert identity['harness_sha256'] == '9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add'
assert sha(ROOT / 'uv.lock') == 'c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b'
assert not command(['git', 'diff', 'cec0322', '--', 'src', 'tests', 'scripts', 'schemas', 'pyproject.toml', 'uv.lock', '.github', 'action.yml', 'Makefile'])
assert not command(['git', 'diff', '--cached'])
assert not command(['git', 'status', '--porcelain'], FROZEN)
revision = command(['git', 'rev-parse', 'HEAD'], FROZEN).strip()
assert revision == 'cec0322e904bbf63c33cd95796e7289101a93e5d'
protected = json.loads((OLD / 'documentation-binding.json').read_text())['user_files_sha256']
assert len(protected) == 10
for name, digest in protected.items():
    assert sha(ROOT / name) == digest, name
prompt = 'docs/phase22-unseen-evaluation-acceptance-closeout-agent-prompt.md'
protected[prompt] = sha(ROOT / prompt)
reuse = json.loads((ROOT / 'artifacts/phase22/integration/v72-prototype-property-correction/local-checks.json').read_text())
for name, digest in reuse['candidate_engineering_files_sha256'].items():
    assert sha(ROOT / name) == sha(FROZEN / name) == digest, name
assert len(reuse['candidate_engineering_files_sha256']) == 303
assert set(command(['git', 'ls-files', '--others', '--exclude-standard']).splitlines()) == set(protected)
binding = json.loads((OLD / 'documentation-binding.json').read_text())
for field in ['owning_docs_sha256', 'review_packet_sha256', 'additional_normative_docs_sha256']:
    for name, digest in binding[field].items():
        assert sha(ROOT / name) == digest, name
assert command(['git', 'worktree', 'list', '--porcelain']) == binding['worktrees'].replace('5263cb26297f2cb9669a6a9f41c28b5b858b02f4', identity['revision'])
assert not command(['git', 'status', '--porcelain'], Path('/Users/bashaarjavaid/Projects/MCP-Sentinel'))
command(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'])
assert not command(['git', 'ls-files', '--deleted'])
assert sys.version_info[:3] == (3, 12, 13)
assert {name: importlib.metadata.version(name) for name in ['semgrep','mcp','pytest','pydantic']} == {'semgrep':'1.176.0','mcp':'1.29.0','pytest':'9.0.3','pydantic':'2.13.4'}
compat=json.loads((ROOT/'artifacts/phase22/integration/v72-prototype-property-correction/compatibility.json').read_text())
for name,digest in compat['runtime_component_files_sha256'].items(): assert sha(ROOT/name)==digest,name
assert sha(ROOT/'artifacts/phase22/integration/v72-production-capture-revalidation/packet.json')==compat['production_replay_sha256']
for folder in ['v73-corrected-four-results','v75-prior-language-results']:
    budget=json.loads((ROOT/'artifacts/phase22/integration'/folder/'execution.json').read_text())
    assert budget['budget_closed'] and budget['remaining']==0
assert not (OUT/'evaluation-authorization.json').exists() and not (OUT/'execution-consumed.json').exists()
assert not (OUT.parent/'evidence-v100.json').exists()
inventory = save('workspace-inventory.json', {
    'tracked': command(['git', 'ls-files']).splitlines(),
    'untracked': command(['git', 'ls-files', '--others', '--exclude-standard']).splitlines(),
    'ignored': command(['git', 'ls-files', '--others', '--ignored', '--exclude-standard']).splitlines(),
    'status': command(['git', 'status', '--porcelain=v1']),
    'worktrees': command(['git', 'worktree', 'list', '--porcelain']),
    'disk_available_bytes': __import__('shutil').disk_usage(ROOT).free,
    'separate_main_status': command(['git', 'status', '--porcelain'], Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')),
})
# Inventory all prior research records, including ignored expanded evidence.
records = {}
for base in [ROOT / 'artifacts', ROOT / 'tests/evals', ROOT / 'docs']:
    for directory, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {'__pycache__', 'node_modules', '.git'} and not (Path(directory) / d).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if OUT in path.parents or path.is_symlink() or path.suffix not in {'.json', '.yaml', '.yml', '.md', '.py'}:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if re.search(r'provenance|expos|select|search|novel|candidate|curat|manifest|freeze|handoff|agent-prompt', relative, re.I):
                records[relative] = sha(path)
exposure = save('prior-exposure-inventory.json', {'files_sha256': dict(sorted(records.items())), 'qualification': 'Complete matching prior on-disk evidence and instruction inventory; candidate identity and file overlap review follows against these records and prior complete corpus trees.'})
processes = command(['ps', '-axo', 'pid=,ppid=,command='])
owned = [line for line in processes.splitlines() if re.search(r'python|semgrep|sentinel|pytest', line, re.I)]
containers = command(['docker', 'ps', '-aq', '--filter', 'label=com.securemcp.sentinel=true']).splitlines()
assert not containers
pr = json.loads(command(['gh', 'pr', 'view', '37', '--json', 'number,state,isDraft,headRefName,headRefOid,baseRefName,title,body']))
assert pr['headRefOid'] == identity['revision'] and pr['state'] == 'OPEN' and pr['isDraft']
assert pr['headRefName'] == 'phase22/integration' and pr['baseRefName'] == 'phase22/description-poisoning'
assert pr['body'] == (OLD / 'pr-body-delivery.md').read_text()
remote = command(['gh', 'api', 'repos/BashaarJavaid/MCP-Sentinel/branches/phase22/integration', '--jq', '.commit.sha']).strip()
assert remote == identity['revision']
save('preparation-baseline.json', {'recorded_at': datetime.now(timezone.utc).isoformat(), 'inventory': inventory, 'pr': pr, 'remote_head': remote, 'process_identity_candidates': owned, 'managed_containers': containers, 'versions': {name: importlib.metadata.version(name) for name in ['semgrep', 'mcp', 'pytest', 'pydantic']}, 'python': sys.version, 'sentinel_import': sentinel.__file__, 'frozen_imports': json.loads(command(['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', '-I', '-c', "import sys,json,importlib; sys.path[:0]=['/private/tmp/mcp-phase22-frozen-cec0322','/private/tmp/mcp-phase22-frozen-cec0322/src']; names=['sentinel.static.engine','sentinel.static.workers','sentinel.static.typescript_path_flow','sentinel.static.path_flow','sentinel.static.rules.sent015']; print(json.dumps({n:importlib.import_module(n).__file__ for n in names}))"])), 'engineering_files_verified': len(reuse['candidate_engineering_files_sha256']), 'initial_checks': ['Sandbox network read failed; authorized escalated PR/branch read succeeded.', 'No process-query sandbox attempt was needed.'], 'paid_calls': 0, 'observations': 0})
save('scope-and-precuration-freeze.json', {
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'user_instruction': 'Read docs/phase22-unseen-evaluation-acceptance-closeout-agent-prompt.md and execute its complete authorized scope. Continue with me through explicit Phase 22 technical acceptance and final closeout delivery. No additional paid calls without my approval.',
    'instruction': {'path': prompt, 'sha256': protected[prompt]},
    'scanner': {**identity, 'revision': revision}, 'delivery_head': identity['revision'],
    'frozen_worktree': str(FROZEN), 'lock_sha256': sha(ROOT / 'uv.lock'),
    'prior_exposure_inventory': exposure, 'protected_files_sha256': protected,
    'prior_audit': {'path': str((OLD / 'audit.json').relative_to(ROOT)), 'sha256': sha(OLD / 'audit.json')},
    'prior_acceptance_proposal': {'path': str((OLD / 'acceptance-proposal.json').relative_to(ROOT)), 'sha256': sha(OLD / 'acceptance-proposal.json'), 'disposition': 'Preserved and unaccepted; readiness superseded by the new 2–4-repository requirement.'},
    'normal_policy': {'input_seconds': 1800, 'semgrep_seconds': 10, 'cleanup_seconds': 15, 'workers_max': 4}, 'new_source_research_started': False, 'authorized_now': 'Source-only preparation of 2–4 distinct previously unused repositories covering Python and TypeScript, ordinary engineering, evidence reconciliation and draft PR delivery.',
    'selection_policy': 'No scans or detector previews. Exclude all prior corpus and source-selection/tuning/exposure families, aliases, forks and equivalent source. Freeze all selected cases before any evaluation. Preserve complete licensed source and actual supported caller/guard/sink proofs.',
    'freshness_limits': 'Project-record novelty only; same-agent post-freeze source review, no independent human review or model-training-data novelty claim.',
    'proposed_native_observations': None, 'evaluation_approved': False,
    'native_observations': 0, 'comparator_observations': 0, 'paid_calls': 0, 'target_executions': 0,
    'technical_acceptance_received': False, 'phase22_complete': False,
})
print('Frozen cec0322 before new source research; protected 11 documents; inventoried', len(records), 'prior exposure records. Zero observations or paid calls.')
