"""Assess final invalidation-set attribution and preserve the preliminary literal-only draft."""
import ast
import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
initial = OUT/'preliminary-literal-key'
initial.mkdir()
for name in ['assessment.json','source-assessment.json','prepare-proposal.py','reconcile.py','render-summary.py','final-check.py','seal.py','bind-delivery.py','deliver.py']:
    shutil.copyfile(OUT/name, initial/name)
a, source = read(OUT/'assessment.json'), read(OUT/'source-assessment.json')
assert a['samples'] == 148764 and a['budget_closed'] and a['remaining'] == 0
fixed = Path('/private/tmp/mcp-phase22-frozen-1948bf9')
path = fixed/'src/sentinel/static/typescript_path_flow.py'
lines = path.read_text().splitlines()
expected = {669:'initial_invalidated = self.invalidated_objects.copy()',670:'invalidated = initial_invalidated.copy()',676:'self.invalidated_objects = initial_invalidated.copy()',677:'local = env.copy()',682:'invalidated.update(self.invalidated_objects)'}
for line, statement in expected.items(): assert lines[line-1].strip() == statement
attribution = read(OUT/'sample-attribution.json')['rows']
for row in a['sample_rows']:
    counts = {str(line):sum(f['count'] for f in next(r for r in attribution if r['rule']==row['rule'])['leaf_frames'] if f['filename']==str(path) and f['function']=='statement' and f['line']==line) for line in expected}
    row['if_state_leaf_samples'] = counts
    row['if_state_leaf_percent'] = {line:count/row['samples']*100 for line,count in counts.items()}
source['sample_metrics'] = a['sample_rows']
uses = {}
for file in sorted((fixed/'src').rglob('*.py')):
    text = file.read_text()
    if 'invalidated_objects' not in text: continue
    tree = ast.parse(text)
    uses[str(file.relative_to(fixed))] = {'sha256':sha(file),'attribute_occurrences':[{'line':node.lineno,'expression':ast.get_source_segment(text,node)} for node in ast.walk(tree) if isinstance(node,ast.Attribute) and node.attr=='invalidated_objects'],'line_context':{str(i):line for i,line in enumerate(text.splitlines(),1) if 'invalidated_objects' in line}}
source['invalidation_attribute_source_uses'] = uses
source['if_state_sample_lines'] = expected
source['source_fact'] = 'Completed tool discovery runs in the parent. Its module initialization uses the full TypeScriptPathFlow. At every If, the implementation copies the pre-arm invalidation set, copies that baseline again into an accumulator, independently copies the same original baseline before each feasible arm, then unions each completed arm into the accumulator. The accumulator therefore repeats baseline work already present in the first arm set. Current source adds/updates invalidations; its If restoration/union preserves preexisting keys. Every reset/reader/write occurrence is retained in invalidation_attribute_source_uses. No per-arm cardinalities, first/second-arm sample split or actual copy/union counts were instrumented.'
source['reuse_constraints'] = 'A future separately approved source-only attempt could form the If union lazily from the first completed feasible arm, then union later completed arms; preserve the independent immutable pre-arm baseline and fresh per-arm copies. No first-arm invalidation may leak into the mutually exclusive arm. Preserve baseline facts, every feasible/absent/terminating arm, nested If/Try/loop/function behavior, exceptions/deadlines, all environment/Value/flow state, source aliases and ordered outputs. Verify no observable alias can be mutated by adopting a completed arm set. Preserve the original zero-feasible-arm fallback and never rely on an unproven shrinking/removal assumption.'
source['remaining_work'] = 'The next proposal targets only construction of the If invalidation accumulator. Per-arm invalidation copies, environment copies, guard and statement evaluation, all merges, registration discovery, security/HTTP rules and coverage remain. No new cache or interpreter memoization is proposed. Source-only proofs and synthetic avoided-work/equivalence checks are prerequisites; speedup and1800-second completion remain unknown.'
source['preliminary_option'] = {'path':'preliminary-literal-key','status':'unexecuted proposal-preparation option superseded before any proposal/approval/implementation','reason':'Final source/leaf review identifies a smaller standard-set accumulator change; literal serialization was4.204646285% of retained parent leaves and remains measured but is not the proposed target. No optimization attempt was consumed.'}
source['measured_scope'] = 'One verified parent snapshot,148764 samples, registration99.851442553% inclusive. No worker identity/snapshot or report exists. The final snapshot and restored-timer flags are true. Supervisor whole-input timeout and subsequent group kill still apply; the final snapshot does not cover all process teardown or prove why teardown exceeded the supervisor grace.'
(OUT/'source-assessment.json').write_text(json.dumps(source,indent=2)+'\n')
a['sample_rows'] = source['sample_metrics']
a['assessment_sha256']['source-assessment.json'] = sha(OUT/'source-assessment.json')
a['refinement'] = {'recorded_at':datetime.now(timezone.utc).isoformat(),'preliminary_assessment_sha256':sha(initial/'assessment.json'),'preliminary_source_assessment_sha256':sha(initial/'source-assessment.json'),'reason':'Complete final leaf/source review supports a narrower If invalidation accumulator proposal. Raw samples, attribution and all measured results remain unchanged. No implementation or extra measurement.'}
(OUT/'assessment.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps(a['sample_rows'],indent=2))
