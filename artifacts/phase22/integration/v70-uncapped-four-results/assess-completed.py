"""Extend exact source judgments only after all approved reports have completed."""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
DEST = OUT / 'final-assessment'
PRIOR = OUT / 'first21-assessment'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    with (DEST / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

validation = read(DEST / 'validation.json')
inventory = read(DEST / 'inventory.json')
old_inventory = read(PRIOR / 'inventory.json')
old_assessment = read(PRIOR / 'assessment-with-differences.json')
assert validation['passed'] and validation['completed'] == 24
assert validation['budget_closed'] and validation['entire_ordered_pairs_equal'] == 12
assert not old_assessment['complete_report_difference_assessment_pending']
assert inventory['contexts'] == old_inventory['contexts']
assert inventory['source_files'] == old_inventory['source_files']
assert inventory['rows'][:21] == old_inventory['rows']
assert len(inventory['rows']) == 24
source = read(PRIOR / 'source-context-assessment.json')
assert all(v['source'] == inventory['contexts'][k] for k, v in source['contexts'].items())
source['reused_from'] = {'path': str((PRIOR / 'source-context-assessment.json').relative_to(ROOT)), 'sha256': sha(PRIOR / 'source-context-assessment.json'), 'all_contexts_and_source_files_exactly_equal': True}
write('source-context-assessment.json', source)

rows = copy.deepcopy(old_assessment['rows'])
diagnostics = read(PRIOR / 'diagnostic-source-assessment.json')['rows']
surfaces = read(PRIOR / 'surface-source-assessment.json')['rows']
findings = read(PRIOR / 'finding-source-assessment.json')
first = {r['input_id']: r for r in old_inventory['rows'] if r['batch'] == 'first'}
for r, v in zip(inventory['rows'][21:], validation['observations'][21:], strict=True):
    previous = first[r['input_id']]
    assert r['case_id'] == 'faf-read-root' and r['batch'] == 'repeat'
    assert r['input_id'] == v['input_id'] and r['report_sha256'] == v['report_sha256']
    for key in ('snapshot', 'label', 'findings', 'diagnostics', 'surfaces', 'coverage'):
        assert r[key] == previous[key], (r['input_id'], key)
    assert not r['findings'] and v['ordered_repeat_equal']
    basis = next(x for x in old_assessment['rows'] if x['input_id'] == r['input_id'] and x['batch'] == 'first')
    rows.append({**copy.deepcopy(basis), **v, 'source_assessment_reused_from_report_sha256': basis['report_sha256']})
    findings['faf_zero_finding_reports'].append({'input_id': r['input_id'], 'batch': 'repeat', 'report_sha256': r['report_sha256'], 'qualification': 'Completed empty finding list, identical ordered report after only approved volatile exclusions; vulnerable miss or unsupported negative remains.'})
    for d in r['diagnostics']:
        assert d['context'] in source['contexts']
        diagnostics.append({'input_id': r['input_id'], 'batch': r['batch'], 'report_sha256': r['report_sha256'], **d, 'assessment_context': d['context'], 'disposition': 'Exact repeated unresolved operation retained with the same source judgment; no safety or suppression inferred.'})
    for s in r['surfaces']:
        basis = next(x for x in surfaces if x['input_id'] == r['input_id'] and x['batch'] == 'first' and x['index'] == s['index'])
        assert basis['surface'] == s['surface'] and basis['context'] == s['context']
        surfaces.append({**copy.deepcopy(basis), 'batch': 'repeat', 'report_sha256': r['report_sha256']})
assert len(rows) == 24 and len(diagnostics) == 52492 and len(surfaces) == 282
assert len(findings['rows']) == 260 and len(findings['faf_zero_finding_reports']) == 6
write('finding-source-assessment.json', findings)
write('diagnostic-source-assessment.json', {'rows': diagnostics, 'count': len(diagnostics), 'by_kind': dict(Counter(d['kind'] for d in diagnostics)), 'unmapped': 0, 'context_packet_sha256': sha(DEST / 'source-context-assessment.json')})
write('surface-source-assessment.json', {'rows': surfaces, 'count': len(surfaces), 'unassessed': 0, 'total_possible_surfaces': 'unknown; no percentage inferred', 'workspace': 'null in every report; no expanded workspace claim'})

def deltas(folder):
    with gzip.open(folder / 'complete-report-differences.jsonl.gz', 'rt') as f:
        return {(r['input_id'], r['batch']): r for r in map(json.loads, f)}

prior_deltas, current_deltas = deltas(PRIOR), deltas(DEST)
assert len(prior_deltas) == 21 and len(current_deltas) == 24
assert all(current_deltas[k] == v for k, v in prior_deltas.items())
delta_judgments = []
for key, delta in current_deltas.items():
    basis_key = key if key in prior_deltas else (key[0], 'first')
    assert delta['changes'] == prior_deltas[basis_key]['changes']
    delta_judgments.append({'input_id': key[0], 'batch': key[1], 'current_report_sha256': delta['current_report_sha256'], 'old_report_sha256': delta['old_report_sha256'], 'basis_input_id': basis_key[0], 'basis_batch': basis_key[1], 'entire_ordered_changes_exactly_equal': True, 'source_assessment': str((PRIOR / 'report-difference-assessment.json').relative_to(ROOT)), 'source_assessment_sha256': sha(PRIOR / 'report-difference-assessment.json')})
assert read(DEST / 'report-difference-inventory.json')['complete_ordered_reconstruction_passed']
write('report-difference-assessment.json', {'rows': delta_judgments, 'completed': 24, 'unassessed_changes': 0, 'complete_ordered_reconstruction_passed': True, 'differences_sha256': sha(DEST / 'complete-report-differences.jsonl.gz'), 'qualification': 'Every full ordered old/current delta equals its hash-bound source-assessed counterpart; only the 11 approved volatile exclusions apply. No sorting, new source novelty, current earlier-language compatibility, or accepted limitation is inferred.'})

cases = copy.deepcopy(old_assessment['cases'])
faf = next(c for c in cases if c['case_id'] == 'faf-read-root')
faf['batches']['repeat'] = copy.deepcopy(faf['batches']['first'])
faf.update(completed=6, ordered_report_pairs_equal=3, timings_seconds=[r['timing']['elapsed_seconds'] for r in rows if r['case_id'] == 'faf-read-root'], qualification='Both complete batches fail named vulnerable detection and negative-path support. Three entire ordered pairs agree; consistency does not convert failures to passes.')
assessment = {k: copy.deepcopy(v) for k, v in old_assessment.items() if k not in {'source_assessment_complete_for_completed21', 'execution_gate_passed_for_completed21', 'evidence_sha256', 'validation_sha256', 'reused_assessments_sha256'}}
assessment.update(completed=24, entire_ordered_pairs_equal=12, source_assessment_complete=True, four_repository_sequence_complete=True, FAF_repeats_pending=0, budget_closed=True, remaining_observation_budget=0, execution_gate_passed=True, cases=cases, rows=rows, diagnostic_count=52492, surface_count=282, beyond1800=sum(r['timing']['elapsed_seconds'] > 1800 for r in rows), max_whole_seconds=max(r['timing']['elapsed_seconds'] for r in rows), validation_sha256=sha(DEST / 'validation.json'), qualification='The sole approved uncapped experiment completed all 24 observations and 12 entire ordered pairs. Two narrow exposed gates pass; Lightning negative qualification and FAF detection/support fail. Uncapped completion does not satisfy the normal 1800-second policy, establish speedup, erase original fresh failures, complete earlier-language compatibility, accept limitations, or complete Phase 22.')
assessment['evidence_sha256'] = {name: sha(DEST / name) for name in ['inventory.json', 'source-context-assessment.json', 'finding-source-assessment.json', 'diagnostic-source-assessment.json', 'surface-source-assessment.json', 'report-difference-inventory.json', 'report-difference-assessment.json']}
assessment['reused_assessments_sha256'] = {str((PRIOR / name).relative_to(ROOT)): sha(PRIOR / name) for name in ['assessment-with-differences.json', 'assessment-binding-check.json', 'faf-fixed-source-assessment.json']}
write('assessment.json', assessment)
print('All 24 reports and complete differences source-assessed: 260 findings, 52492 diagnostics, 282 surfaces, 4963 contexts; two narrow passes, two failed repository gates.')
