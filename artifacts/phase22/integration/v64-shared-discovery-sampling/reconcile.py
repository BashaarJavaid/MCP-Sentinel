"""Retain every prior requirement and reconcile the completed diagnostic checkpoint."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[3]
OLD = BASE/'v63-shared-discovery-regression'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
a = read(OUT/'assessment.json')
old = read(OLD/'audit.json')
p = read(OUT/'optimization-proposal.json')
assert a['source_assessment_complete_for_retained_outputs'] and a['budget_closed']
assert read(BASE/'v64-compatible-reuse.json')['exit_code'] == 0
rows = copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V63-DELIVERY', 'V63-DIAGNOSTIC-DECISION'}:
        receipt = 'delivery-verification.json' if row['id'] == 'V63-DELIVERY' else 'diagnostic-authorization.json'
        row['previous_row'] = copy.deepcopy(row)
        row.update(disposition='passed', evidence=[str((OLD/receipt).relative_to(ROOT))], assessment='Actual7d6e01a draft delivery verified.' if row['id']=='V63-DELIVERY' else 'Exact user approved. decision authorizes only one parent-and-worker profile. No optimization, retry or human technical acceptance is inferred.')
new = [
 ('AUTH', 'Bind the exact single parent-and-worker profile approval and source/cleanup preflight', 'passed', ['../v63-shared-discovery-regression/diagnostic-authorization.json','../v63-shared-discovery-regression/diagnostic-preflight.json','attempt.json']),
 ('PROFILE-VALIDATION', 'Validate every retained process identity, sample/frame count, output, timing and closed one-use budget', 'passed', ['validation.json','sample-attribution.json','owned-work.json']),
 ('SOURCE-ASSESSMENT', 'Source-assess all retained frame attribution with separate parent/worker coverage and sampling limits', 'passed', ['assessment.json','source-assessment.json','frame-contexts.json','frame-source-bindings.json']),
 ('OPT-PREPARATION', 'Prepare one bounded source-only If invalidation-accumulator proposal without implementation or new measurement', 'passed', ['optimization-proposal.json','compatible-reuse.json']),
 ('OPT-DECISION', 'Obtain separate exact approval before the proposed source-only If invalidation-accumulator attempt', 'unresolved', ['optimization-proposal.json']),
 ('DELIVERY', 'Seal the assessed profile and complete audit, then verify delivery of the concrete next decision to the existing draft', 'unresolved', []),
]
for identity, requirement, disposition, evidence in new:
    rows.append({'id':'V64-'+identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/n).resolve().relative_to(ROOT)) for n in evidence], 'assessment':'The one current-source sampled attempt is closed; actual retained process coverage and partial samples are source-assessed. No report, native pass or speedup is inferred. One source-only If invalidation-accumulator proposal is unapproved and unimplemented. All historical failures and human acceptance remain unresolved where applicable.'})
assert len(old['requirements']) == 89 and len(old['additional_scope_requirements']) == 263 and len(rows) == 269
for before, after in zip(old['additional_scope_requirements'], rows):
    assert before == after or after.get('previous_row') == before
current = copy.deepcopy(old)
current['historical_v63_status_fields'] = {k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
current.update(recorded_at=datetime.now(timezone.utc).isoformat(), additional_scope_requirements=rows, additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)), prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')}, optimization_approved=False, optimization_attempts=0, optimization_synthetic_verified=False, optimization_budget_closed=False, optimization_remaining=0, current_optimization_approved=False,current_optimization_attempts=0,current_diagnostic_prepared=True,current_diagnostic_approved=True,current_diagnostic_executed=True,valid_current_source_profiles=1,diagnostic_attempts=1,diagnostic_remaining=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='One approved parent-and-worker FAF profile at1948bf9 timed out, retaining the actual partial process snapshots with verified identities. No report or native pass. One source-only If invalidation-accumulator proposal is unapproved and unimplemented.')
current['current_source_input_accounting'] = {'native_regression':{'attempts':1,'complete':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'budget_closed':True},'sampled_diagnostic':{'attempts':1,'approved':True,'complete':a['completed_inputs'],'incomplete':a['incomplete_inputs'],'remaining':0,'budget_closed':True,'retained_processes':[r['rule'] for r in a['sample_rows']]},'total_attempted_inputs':2}
current['current_budget_interpretation'] = 'The native205-observation sequence and separate one-use profile are closed. The new If invalidation-accumulator proposal authorizes no implementation until a separate decision; zero new corpus/profile/paid budget. Current_source_corpus_observations retains native-only accounting, not the total attempted inputs.'
for row in old['requirements'] + old['additional_scope_requirements']:
    entry = copy.deepcopy(old.get('current_requirement_interpretations', {}).get(row['id'], {}))
    entry.update(requirement=row['requirement'], historical_disposition=row['disposition'], current_execution_interpretation='Engineering remains verified at1948bf9. Its one native timeout/204closed remainder and one separate sampled timeout lack reports. Actual parent/worker attribution is retained per process; no native speedup, detection, negative support, ordered compatibility or accepted limitation follows. All original source-bound evidence and judgments are preserved.', current_execution_evidence={'assessment_sha256':sha(OUT/'assessment.json'),'compatibility_sha256':sha(OUT/'compatible-reuse.json')})
    current['current_requirement_interpretations'][row['id']] = entry
assert len(current['current_requirement_interpretations']) == 352
assert current['additional_scope_dispositions'] == {'passed':246,'unresolved':17,'proposed documented limitation awaiting decision':6}
current['current_evidence'] = {n:sha(OUT/n) for n in ['assessment.json','validation.json','budget-closed.json','optimization-proposal.json','compatible-reuse.json','owned-work.json']}
write('audit.json', current)
write('prior-row-preservation.json', {'prior_audit_sha256':sha(OLD/'audit.json'),'retained_prior_rows':352,'total_rows':358,'updated_rows':['V63-DELIVERY','V63-DIAGNOSTIC-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
roles = ', '.join(r['rule'] for r in a['sample_rows'])
status = f'''## Current v64 parent-and-worker profile: source-only decision pending

The approved single FAF profile at frozen **`1948bf9`** timed out after
**{a['timing']['elapsed_seconds']:.6f} seconds**, retaining **{a['samples']:,} partial samples**
from **{len(a['sample_rows'])} verified process snapshot(s): {roles}**. Cleanup passed;
no report exists and the one-use budget is closed. Parent and worker denominators
are separate. Missing worker snapshots do not prove workers never launched.
Partial shares establish no native speedup, removable-cost fraction or detection.

`v64-shared-discovery-sampling/optimization-proposal.json` prepares **one unapproved
source-only attempt** to avoid redundant If invalidation-accumulator construction.
The original baseline and every per-arm copy, guard, traversal and state update remain.
Complete branch-isolation, alias/state and report equivalence plus full engineering
are required. No implementation, corpus/profile/retry, paid call,
resource change or timeout revision is included. The 1800-second policy remains.

All **358 requirements (89 original + 269 added)** and every earlier failed gate
remain. Product retains tested `1948bf9`: **2,418 tests / 36 skips** locally and in
all 12 hosted suites, 29 normal CI jobs and docs passed. Combined coverage is
90.08%, branch-only 85.92%; six zero-call replays and approved runtime bindings
remain compatible. This continuation adds profile assessment and docs/package checks.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete;
paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15 unchanged.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

'''
heading = '## Current v63 shared-discovery regression: timed out, budget closed'
docs = list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
    path = ROOT/name
    text = path.read_text()
    assert text.count(heading) == 1, name
    path.write_text(text.replace(heading, status + heading.replace('Current','Historical',1), 1))
write('owning-docs.json', {'sha256':{n:sha(ROOT/n) for n in docs}})
(OUT/'status.md').write_text(status)
print('Preserved all352 prior rows;358 total. Reconciled16 owning docs; no technical acceptance inferred.')
