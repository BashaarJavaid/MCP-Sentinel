"""Prepare a new bounded proposal only after verified engineering and scanner freeze."""
import copy
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from scripts.phase22_corpus import Manifest
from scripts.phase20_scoring import candidate_identity

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
freeze = read(OUT/'freeze.json')
quality = read(BASE/'v59-candidate-quality/packet.json')
assert quality['engineering_passed'] and quality['source'] == freeze['scanner']['revision']
assert read(BASE/'v59-full-suite.json')['exit_code'] == 0
ts = read(BASE/'v41-path-guard-recovery/evaluation-proposal.json')
py = read(BASE/'v37-ddg-trace/evaluation-proposal.json')
four = read(BASE/'v43-four-fresh-preparation/evaluation-proposal.json')
files = {}
def bind(path):
    files[str(path.relative_to(ROOT))] = sha(path)
def write(name, data):
    with (OUT/name).open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
def reference(raw, input_id, group=None):
    packet = read(raw/'packet.json')
    row, = [r for r in packet['attempts'] if r['input_id'] == input_id and r['batch'] in {'first', 'rules-first', 'compatibility'} and (group is None or r['group'] == group)]
    assert row['state'] == 'completed'
    report = raw/row['directory']/input_id/'report.json'
    config = report.with_name('configuration.json')
    return report, config

groups = {}
for case in four['repositories']:
    manifest = Manifest.model_validate_json((ROOT/case['manifest']['path']).read_text())
    group = {'manifest': case['manifest']['path'], 'manifest_sha256': case['manifest']['sha256'],
             'source_freeze_approval': 'artifacts/phase22/integration/v43-four-fresh-preparation/authorizations/'+case['id']+'.json',
             'input_ids': case['input_ids'], 'inputs': {}, 'actual_language': case['language'],
             'repository': case['repository'], 'condition_review': case['condition_review']}
    for item in manifest.inputs:
        if item.id not in case['input_ids']:
            continue
        report, config = reference(BASE/'v44-four-fresh-evaluation/raw', item.id)
        assert read(config)['language'] == case['language']
        group['inputs'][item.id] = {'input': item.model_dump(mode='json'),
            'reference_report': str(report.relative_to(ROOT)), 'configuration': str(config.relative_to(ROOT)),
            'configuration_sha256': sha(config), 'assessment': None}
    assert list(group['inputs']) == case['input_ids']
    groups[case['id']] = group
    for key in ['condition_review', 'provenance', 'configuration']:
        assert sha(ROOT/case[key]['path']) == case[key]['sha256']
        bind(ROOT/case[key]['path'])

order = [{'group': c['id'], 'batch': batch, 'input_id': name}
         for batch in ['first', 'repeat'] for c in four['repositories'] for name in c['input_ids']]
for language, old, raw in [('typescript', ts, BASE/'v42-path-guard-regression/raw'), ('python', py, BASE/'v38-guard-regression/raw')]:
    rename = {name: ('ts-' if language == 'typescript' else 'py-')+name if name in {'development', 'historical'} else name for name in old['groups']}
    for name, original in old['groups'].items():
        group = copy.deepcopy(original)
        group['actual_language'] = language
        for input_id, item in group['inputs'].items():
            report, config = reference(raw, input_id, name)
            assert read(config)['language'] == language
            assert sha(config) == item['configuration_sha256']
            item['prior_reference_report'] = item['reference_report']
            item['reference_report'] = str(report.relative_to(ROOT))
            item['configuration'] = str(config.relative_to(ROOT))
            if item['assessment'] is not None and item['assessment']['candidate_identity'] != candidate_identity(read(report)['findings']):
                item['historical_assessment'] = item['assessment']
                item['assessment'] = None
        groups[rename[name]] = group
    order.extend({**row, 'group': rename[row['group']]} for row in old['order'])
assert len(order) == 205 and sum(len(g['input_ids']) for g in groups.values()) == 110
assert sum(r['batch'] == 'repeat' for r in order) == 95
assert len({r['input_id'] for r in order}) == 110
for group in groups.values():
    assert sha(ROOT/group['manifest']) == group['manifest_sha256']
    bind(ROOT/group['manifest'])
    if group['source_freeze_approval']:
        bind(ROOT/group['source_freeze_approval'])
    for item in group['inputs'].values():
        for name in ['reference_report', 'configuration', 'prior_reference_report']:
            if name in item:
                bind(ROOT/item[name])
for name in ['v43-four-fresh-preparation/runner.py', 'v20-linux-diagnostic-v1/runner.py',
             'v43-four-fresh-preparation/scoring-rubric.json', 'v44-four-fresh-evaluation/assessment.json',
             'v44-four-fresh-evaluation/source-diagnosis.json', 'v44-four-fresh-evaluation/source-context-assessment.json',
             'v42-path-guard-regression/assessment.json', 'v42-path-guard-regression/condition-assessment.json',
             'v38-guard-regression/assessment.json', 'v37-ddg-trace/scoring-rubric.json',
             'v41-path-guard-recovery/scoring-rubric.json']:
    bind(BASE/name)

rubric = {'status': 'prospective_exposed_regression_not_approved',
    'four_original_conditions': {'path': 'artifacts/phase22/integration/v43-four-fresh-preparation/scoring-rubric.json', 'sha256': sha(BASE/'v43-four-fresh-preparation/scoring-rubric.json')},
    'requirements': 'Preserve each original condition-review, label, caller input, actual sink and source prerequisites. Each three-input four-repository batch requires one vulnerable hit and zero matching fixed/safe alerts, with source-established actual sink/guard/value support. Quiet unsupported paths fail. Do not specialize scans to illustrative caller values or use unrelated findings as named hits.',
    'qualification_review': {
        'faf-read-root': 'A supported actual read must carry the registered caller path. A fixed candidate accurately stating a component-bounded lexical restriction and only remaining physical/symlink uncertainty does not allege the scored ordinary-file sibling-root bypass. An absent candidate requires positive source/code-path support assessment; silence alone fails. Preserve unresolved loop termination and dispatch separately.',
        'no-bash-write-prefix': 'Require actual checked helper return to fs.writeFileSync. An accurate lexical-directory-boundary/physical-gap finding leaves the ordinary-file prefix condition excluded under the frozen prerequisites; a generic missing-boundary assertion remains a false alert. Preserve raw vulnerable-prefix wording and all broader filesystem candidates.',
        'lightning-discover-linklocal': 'Require actual client.get on the registered caller URL, established available HTTPX branch and terminal initial literal IPv4 link-local rejection. Existing linklocal-ipv4 or literal-ipv4 private-address qualification can support the named exclusion only when source assessment establishes the same caller route and explicit link-local rejection. The latter description is broader private-literal evidence, not DNS, redirect, rebinding or full IPv6 safety. Missing or wrong-route qualification fails.',
        'engram-export-home': 'Require actual manifest_path.write_text with the export caller input and home-relative guard. A resolved-copy finding may document the initial home guard only; it explicitly leaves reconstructed-path equivalence/containment at use unestablished. Assess the frozen stable home/cwd/environment and ordinary-file prerequisites. A generic claim of missing initial home rejection is a false alert, and an unrelated helper write cannot count as the named sink. This is narrow initial-boundary discrimination, not complete fixed-path/runtime safety.'},
    'qualification_scope': 'These prospective interpretations make the corrected report qualifiers reviewable before observations. They do not change original source labels/prerequisites, waive unsupported coverage or rewrite any first-frozen gate. Every qualifier requires actual source-bound support and remains visible in raw totals.',
    'prior_typescript': read(BASE/'v41-path-guard-recovery/scoring-rubric.json'),
    'prior_python': read(BASE/'v37-ddg-trace/scoring-rubric.json'),
    'prior_scope_interpretation': 'Nested prior rubric scope/count/stop fields describe closed historical approvals only. This proposal has205 observations,95 ordered repeats and the single collection stopping policy below. All prior named-condition and exact narrow-qualifier requirements remain.',
    'repeat': 'All95 entire ordered pairs equal after only the established11 volatile exclusions. Fifteen Python development inputs run once; they have no newly measured repeat. No sorting, diagnostic omission or broader exclusions.',
    'assessment': 'Source-assess all four-repository findings/diagnostics/surfaces and every change on earlier inputs against complete bound reports and prior assessments; unchanged items retain explicit hash-bound source judgments. Raw counts, unsupported/incomplete states, false positives, Meta operator erratum and unresolved coverage stay visible. No automatic refreshed stale assessment keys.',
    'collection_stop': 'Stop and close every unused observation on infrastructure, identity, execution, whole/native timeout, schema, process cleanup, or ordered-repeat failure. Detection/negative-support failures remain results and are assessed after collecting the other authorized inputs. No tuning, retry, profile, extra diagnostic or replacement during the sequence.',
    'technical_acceptance': False, 'paid_calls': 0, 'target_execution': False}
write('scoring-rubric.json', rubric)
for name in ['authorization.json', 'freeze.json', 'source-proof.json', 'compatibility.json',
             'prepare-regression.py', 'evaluate.py', 'scoring-rubric.json', 'runner-boundaries.json', 'timeout-confirmation.json']:
    bind(OUT/name)
proposal = {'status': 'prepared_not_approved_not_executed', 'scanner': freeze['scanner'],
    'lock_sha256': freeze['harness_and_lock_sha256']['uv.lock'], 'frozen_checkout': freeze['frozen_checkout'],
    'purpose': 'Evaluate completed results under the user-directed 1800-second shared timeout policy, including the still-unvalidated exposed four-source recovery and Python/TypeScript compatibility. Detector logic is unchanged from dc73715. Preserve every first-frozen result and earlier 300-second failure; a longer limit is not a speedup.',
    'runner': str((OUT/'evaluate.py').relative_to(ROOT)),
    'prepared_command': ['/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python', '-I', str(OUT/'evaluate.py'), 'run', str(BASE/'v60-long-timeout-regression/raw')],
    'prepared_command_cwd': freeze['frozen_checkout'],
    'launch_precondition': 'A new explicit205-observation authorization, immutable source/configuration/runner binding, one consumed launch token, no conflicting owned work, exact locked interpreter/import paths and an external6275-minute sequence supervisor. Internal stop is6274 minutes, with at most15 seconds process cleanup. No launch receipt or output directory is created by preparation.',
    'execution': 'One serial local macOS sequence in the existing locked environment; existing measure/frozen/canonicalizer/process-group supervisor, no resource upgrade or hosted evaluation dispatch.',
    'bounds': {'native_observations': 205, 'local_sequences': 1, 'hosted_dispatches': 0,
        'normal_target_seconds': 120, 'native_and_whole_input_maximum_seconds': 1800,
        'cleanup_maximum_seconds_per_input': 15, 'sequence_maximum_minutes': 6275, 'internal_stop_minutes': 6274,
        'nominal_input_minutes': 6150, 'retries': 0, 'profiles': 0, 'comparators': 0, 'paid_calls': 0,
        'target_execution': False, 'new_repositories': 0},
    'groups': groups, 'order': order, 'files_sha256': files, 'volatile_exclusions': ts['volatile_exclusions'],
    'witnesses': ts['witnesses'], 'gate': rubric['requirements']+' All prior source-labeled conditions, narrow qualifiers and support requirements must also pass; final source assessment decides the gates, never execution completion alone.',
    'stop': rubric['collection_stop'],
    'scope_justification': '24 original four-repository observations plus 94 TypeScript and 87 Python observations, 110 unique exposed records and 95 ordered pairs. The shared deadline affects both languages; earlier source recovery and credential fixes still lack current-source corpus compatibility because all four prior native sequences stopped on their first FAF input. Every old remainder is closed. No extra Python-development repeat, mutation, repository or comparator is added. Whole language subsets are never relabeled as a new whole 25/45 Linux execution.',
    'timeout_policy_revision': {'authorization_sha256':sha(OUT/'authorization.json'),'timeout_confirmation_sha256':sha(OUT/'timeout-confirmation.json'),'source_proof_sha256':sha(OUT/'source-proof.json'),'old_maximum_seconds':300,'new_maximum_seconds':1800,'target_seconds':120,'target_is_informational':True,'interpretation':'One product AST literal changes the shared deadline; detector logic, cleanup, original sources/configurations and all discrimination/support requirements remain unchanged. This prospectively revises timing acceptance and preserves every earlier failure at its actual limit. Completion within the new limit is required and does not prove safety or a speedup.','sequence_bound_basis':'205 x 30 minutes = 6150 nominal input-minutes, plus the existing 125-minute reserve = 6275 minutes (104 hours 35 minutes). This is a worst-case cap, not a runtime estimate or required wait. Each completed input returns immediately; stop/cleanup/repeat failures still close the unused budget.'},
    'original_source_bindings': {'four_fresh': '2e0efb2:24 complete,12equal pairs,all4repository gates failed', 'typescript': '2e0efb2:94complete/47equal pairs', 'python': '8c62567:87complete/36equal pairs', 'whole_linux': '1f3f72f:whole25development reuse and45+45historical; retain Meta operator erratum'},
    'ddg_language_erratum': 'The frozen DDG manifest incorrectly says TypeScript. All five actual source/configuration records are Python and remain in the Python group; do not edit the old manifest or relabel historical execution.',
    'source_freeze_receipts': 'Historical approvals bind unchanged source provenance only; all old budgets are closed. This sequence requires a new exact top-level authorization binding this proposal, scanner, rubric, order and bounds before any child can run.',
    'following_checkpoint': 'Complete source assessment and all requirement reconciliation. If actual gates pass, prepare a separate explicit human technical acceptance proposal retaining original failures and limitations; then deliver accepted closeout. Evaluation approval is not acceptance.',
    'not_authorized': ['paid calls', 'target dependencies or execution', 'new repository', 'comparator/retry/profile', 'merge/ready/release/outreach', 'Phase23'],
    'technical_acceptance_received': False, 'phase22_complete': False}
previous = read(BASE/'v57-credential-merge/evaluation-proposal.json')
for field in ['groups', 'order', 'volatile_exclusions', 'witnesses', 'gate', 'stop']:
    assert proposal[field] == previous[field], field
assert rubric == read(BASE/'v57-credential-merge/scoring-rubric.json')
write('evaluation-proposal.json', proposal)
print('Prepared205 exposed observations on110 input records and95 ordered pairs; no approval or execution.')
