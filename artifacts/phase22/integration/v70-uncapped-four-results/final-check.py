"""Verify completed experimental evidence, preserved failures and unchanged engineering."""
import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
PREP = BASE / 'v69-uncapped-four-repository'
PREV = BASE / 'v68-invalidation-sampling'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

checks = ['v69-synthetic-equivalence', 'v69-boundaries', 'v69-preparation-corrected', 'v69-approval-boundary-corrected', 'v69-authorization', 'v70-final-validation', 'v70-final-inventory', 'v70-final-differences', 'v70-final-assessment', 'v70-compatible-reuse', 'v70-reconciliation', 'v70-review-summary', 'v70-final-docs', 'v70-final-artifacts', 'v70-final-build', 'v70-final-distributions', 'v70-owned-final']
for name in checks:
    assert read(BASE / (name + '.json'))['exit_code'] == 0, name
a = read(OUT / 'final-assessment/assessment.json')
v = read(OUT / 'final-assessment/validation.json')
p = read(PREP / 'evaluation-proposal.json')
assert a['completed'] == v['completed'] == 24 and a['entire_ordered_pairs_equal'] == 12
assert a['source_assessment_complete'] and not a['complete_report_difference_assessment_pending']
assert a['repository_gates_passed'] == 2 and a['budget_closed'] and a['remaining_observation_budget'] == 0
assert a['finding_count'] == 260 and a['diagnostic_count'] == 52492 and a['surface_count'] == 282 and a['source_context_count'] == 4963
assert a['scanner'] == p['scanner'] and a['proposal_sha256'] == sha(PREP / 'evaluation-proposal.json')
assert a['approval_sha256'] == sha(PREP / 'evaluation-authorization.json')
assert read(OUT / 'execution.json')['returncode'] == 0
for name, digest in a['evidence_sha256'].items():
    assert sha(OUT / 'final-assessment' / name) == digest, name
for name, digest in a['reused_assessments_sha256'].items():
    assert sha(ROOT / name) == digest, name
packet = read(OUT / 'raw/packet.json')
for name, digest in packet['files_sha256'].items():
    assert sha(OUT / 'raw' / name) == digest, name
for name, digest in read(BASE / 'v66-invalidation-contract/local-checks.json')['candidate_engineering_files_sha256'].items():
    assert sha(ROOT / name) == sha(Path(p['frozen_checkout']) / name) == digest, name
binding = read(PREV / 'documentation-binding.json')
for key in ['user_files_sha256', 'additional_normative_docs_sha256']:
    for name, digest in binding[key].items():
        assert sha(ROOT / name) == digest, name
for name, digest in read(PREP / 'intake.json')['protected_user_files_sha256'].items():
    assert sha(ROOT / name) == digest, name
for name, digest in read(OUT / 'owning-docs.json')['sha256'].items():
    assert sha(ROOT / name) == digest, name
prior = read(BASE / 'v45-four-source-recovery/prior-row-preservation.json')['referenced_evidence_sha256']
for name, digest in prior.items():
    assert sha(ROOT / name) == digest, name
pending = read(PREV / 'optimization-proposal.json')
assert pending['status'] == 'prepared_not_approved_not_started' and not (BASE / 'v69-ts-literal-key-reuse').exists()
assert sha(PREV / 'optimization-proposal.json') == 'fa4ffc3760d4b85b4f8236eec5c7b28d979ece894515bb1495046dd1db108cf6'
audit = read(OUT / 'audit.json')
old = read(PREV / 'audit.json')
assert audit['requirements'] == old['requirements'] and len(audit['additional_scope_requirements']) == 310
for before, after in zip(old['additional_scope_requirements'], audit['additional_scope_requirements']):
    assert before == after or after.get('previous_row') == before
assert len(audit['current_requirement_interpretations']) == 399
for identity in ['V49-DIAGNOSTIC-PREPARATION', 'V55-EQUIVALENCE', 'V56-EQUIVALENCE', 'V65-EQUIVALENCE', 'V67-REGRESSION-GATE', 'V68-OPT-DECISION', 'V70-FOUR-GATE', 'V70-PRIOR-LANGUAGES']:
    assert next(r for r in audit['additional_scope_requirements'] if r['id'] == identity)['disposition'] == 'unresolved', identity
for key in ['optimization_approved', 'optimization_synthetic_verified', 'optimization_budget_closed', 'current_optimization_approved', 'technical_acceptance_received', 'phase22_complete', 'acceptance_packet_ready']:
    assert not audit[key], key
assert audit['current_optimization_attempts'] == 0 and audit['current_timeout_policy_seconds'] == 1800
assert audit['current_source_input_accounting']['total_attempted_inputs'] == 26
assert read(OUT / 'final-distributions.json')['wheel_product_schema_fixture_members_byte_identical_to_hosted']
assert read(OUT / 'owned-final.json')['owned_processes'] == []
assert not subprocess.check_output(['git', 'diff', '4145d35', '--', 'src', 'tests', 'scripts', 'schemas', '.github', 'uv.lock', 'pyproject.toml', 'CHANGELOG.md', 'docs/architecture.md'])
assert not subprocess.check_output(['git', 'ls-files', '--deleted'])
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', '8b6b0ddf1d6f6cf5a8da3ab9421471865b801455', 'HEAD'], check=True)
main = Path('/Users/bashaarjavaid/Projects/MCP-Sentinel')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip() == '4cd57593b2585b9ee05c0f175930e6a0d76d362a'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=main)
commands = {p.stem: read(p) for prefix in ('v69-', 'v70-') for p in BASE.glob(prefix + '*.json') if 'exit_code' in read(p)}
for name, receipt in commands.items():
    assert sha(BASE / (name + '.patch')) == receipt['diff_sha256']
    assert sha(BASE / (name + '.untracked.tar.gz')) == receipt['untracked_source_sha256']
failed = {name: r['exit_code'] for name, r in commands.items() if r['exit_code'] != 0}
assert failed == {'v70-faf-first-inventory': 1}, failed
failure = {'failed_wrapper_checks': failed, 'assessment_helper_failure': 'The first FAF inventory required a literal source occurrence for a conceptual dynamic-tool-description warning. Corrected file-only precision retains the entire verified file; no line is invented. Original and corrected helpers/checks remain.', 'passed_check_corrections': ['The initial relative module binding index split a leading-dot specifier to an empty identifier and falsely matched all lines. Source review corrected it to the actual import; intermediate inventory and all helper versions remain.', 'The first21 assessment had a vacuous revision assertion. Its exact one-line correction and independent all-context/report/source binding check are retained without changing output data.', 'Initial pre-execution v69 proposal/rubric copied stale 205/95 scope fields. Both original successful structural checks and the corrected 24/12 preparation/approval-boundary checks remain; only corrected bindings were authorized and consumed.', 'A child-output mkdir collision was corrected in preparation before any input; runtime policy writes a sibling receipt.'], 'read_only_errors': 'A few guessed source/helper paths and unmatched shell globs failed during review. One partial-summary patch did not match and made no change, then the corrected patch applied. These were not input attempts, scanner failures or target executions.', 'sequence_failures': 'All 24 executions completed; Lightning qualification and FAF detection/support remain actual failed product gates. No timeout or repeat failure occurred in this uncapped sequence.', 'paid_calls': 0}
write('check-failure-assessment.json', failure)
for folder in (OUT, PREP):
    for helper in folder.glob('*.py'):
        ast.parse(helper.read_text(), filename=str(helper))
write('command-provenance.json', {'wrapper_commands': commands, 'actual_launcher': read(OUT / 'launch.json'), 'actual_execution': read(OUT / 'execution.json'), 'per_input_commands': [{'directory': r['directory'], 'command': r['command'], 'timing': r['timing']} for r in packet['attempts']], 'helper_sources_sha256': {str(p.relative_to(ROOT)): sha(p) for folder in (OUT, PREP) for p in folder.glob('*.py')}, 'failure_assessment_sha256': sha(OUT / 'check-failure-assessment.json'), 'qualification': 'Wrapper logs, commands, patches and helper archives are retained. Actual child commands/timings and per-child logs are retained by the run. The long-lived launcher stdout was returned through the tool session; no standalone complete raw console transcript is claimed. Passive progress records are process inventories, not stack profiles. Prepared but unexecuted final/check helpers are not additional observations.', 'paid_calls': 0})
write('final-checks.json', {'passed': True, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'scanner': p['scanner'], 'engineering_files_verified': 303, 'prior_evidence_files_verified': len(prior), 'requirements': 399, 'protected_user_files': 9, 'owning_docs': 16, 'main_and_parent_preserved': True, 'checks_sha256': {name: sha(BASE / (name + '.json')) for name in checks}, 'completed_observations': 24, 'entire_ordered_pairs_equal': 12, 'repository_gates_passed': 2, 'budget_closed': True, 'optimization_attempts': 0, 'paid_calls': 0, 'technical_acceptance_received': False, 'phase22_complete': False})
print('Final 399-row/source/package/uncapped-report checks pass; two repository gates and technical acceptance remain unresolved.')
