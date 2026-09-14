"""Prepare one unexecuted If invalidation-accumulator source-only attempt."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = read(OUT/'assessment.json')
assert a['validation_passed'] and a['source_assessment_complete_for_retained_outputs']
assert a['budget_closed'] and a['remaining'] == 0 and a['optimization_attempts'] == 0
assert not (OUT.parent/'v65-if-invalidation-accumulator').exists()
files = ['src/sentinel/static/typescript_path_flow.py','src/sentinel/static/typescript_registration_flow.py','src/sentinel/static/typescript_discovery.py','src/sentinel/static/path_flow.py','src/sentinel/static/workers.py','src/sentinel/static/rules/sent015.py','src/sentinel/static/rules/sent016.py','tests/test_static_workers.py','tests/test_typescript_discovery.py','tests/test_typescript_classes.py']
p = {
 'status':'prepared_not_approved_not_started','recorded_at':datetime.now(timezone.utc).isoformat(),
 'starting_delivery':'7d6e01a0e8c9e4e5f81a8fd195599dac6b7aa8ab','scanner':a['scanner'],'frozen_checkout':'/private/tmp/mcp-phase22-frozen-1948bf9',
 'profile_assessment_sha256':sha(OUT/'assessment.json'),'source_assessment_sha256':sha(OUT/'source-assessment.json'),
 'target':'Avoid a redundant baseline copy and first-arm union when forming an If invalidation accumulator.',
 'target_files':['src/sentinel/static/typescript_path_flow.py'],
 'source_files_sha256':{n:sha(ROOT/n) for n in files},
 'purpose':'The current If path copies its pre-arm invalidation baseline into an accumulator and then unions every feasible arm into it, even though the first arm already starts with an independent copy of that baseline. Final parent leaf samples include this accumulator copy and repeated union. Only those two redundant operations are proposed for removal; sample shares do not establish savings or completion.',
 'proposed_change':'One source-only change confined to TypeScriptPathFlow.statement If invalidation accumulation: keep the original independent pre-arm baseline and fresh copy before every feasible arm; initialize the result accumulator lazily from the first fully evaluated feasible arm set, then union subsequent evaluated arm sets into it. Include terminating and absent arms exactly as before. If no feasible arm was evaluated, preserve the original fresh baseline-copy fallback. Keep assignment/evaluation order, all guard/statement/environment/merge work and subsequent conditional facts unchanged.',
 'identity_and_warning_contract':'Preexisting invalidations must remain in the final set, and first-arm escapes must never affect the mutually exclusive arm. Trace every set writer/reset/reader and establish the required monotonicity and alias conditions; do not assume an externally observable or retained alias is safe to mutate. Preserve full environments, all Value fields and interning, every flow field and relevant alias relation, warnings, unresolved flows, registrations, guard/sink support, source-node identity, ordered reports and cleanup. No initial baseline mutation or set sharing across simultaneously evaluated arms.',
 'implementation_limit':'Only the If result accumulator may change. No changes to per-arm baseline copies, env.copy, guard/condition evaluation, If arm eligibility, Try/loop/function traversal, merge semantics or stopping rules. No new cache, Value/environment/function memoization, AST mutation/pruning, warning suppression, dependency, resource/worker-count or timeout revision. If full state/alias/monotonicity or avoided-work prerequisites fail, preserve and close this one attempt; do not switch targets or silently broaden the contract.',
 'bounds':{'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0},
 'verification':[
  'Preserve exact tested1948bf9 source and trace all invalidated_objects writes/resets/readers and all If callers/subclasses before editing. Establish why adopting a completed arm cannot mutate any observable retained alias, why preexisting invalidations cannot shrink on eligible source paths, and why the original baseline remains independent.',
  'Compare complete baseline/candidate Value, environment and entire flow state on existing scanner-owned synthetic ASTs for zero/one/two feasible arms, absent else, true/false/unknown facts, empty/nonempty and large preexisting sets, arm-specific escapes, both arm orders, terminating/throwing arms, nested If/Try/loops/functions/constructors/imported aliases, guard and instance/credential invalidation. Assert second-arm isolation and union of every evaluated arm, including terminating paths. Compare input state and relevant source/set/Value alias identities.',
  'Retain adversarial invalidation/alias controls and compare partial state after deadline/error/interruption. Do not drop baseline keys or accept narrowing merely because ordinary cases pass. Every production writer/reset must be accounted for; unsupported alias or shrinking behavior fails the prerequisite rather than being excluded.',
  'Synthetic operation accounting must show the redundant accumulator baseline copy and first-arm union are avoided in eligible cases, while every feasible arm, baseline isolation copy, environment copy, guard, merge and security-state update still executes. This is not a corpus observation, benchmark or native speedup measurement.',
  'Compare entire ordered registration bindings/warnings/options and all five rules; preserve serial/parallel Python/TypeScript/mixed reports, source-node/file aliases, shared completed discovery, deadline and worker cleanup controls. No exposed corpus is repurposed as a synthetic fixture.',
  'If the single attempt passes complete equivalence and avoided-work prerequisites, complete affected/full local and all required hosted engineering under prompt section8: strict whole-scope quality, schemas/lock/notices/advisories/offline artifacts, docs/packages/installed-wheel matrix, Docker/isolation/Action/hooks. Regenerate/revalidate all six complete production requests and approved runtime/image compatibility with live transport forbidden. Freeze the actual tested candidate, then prepare separately approved affected regression; no corpus/profile/paid call follows from this approval.'
 ],
 'profile_metrics':a['sample_rows'],
 'uncertainty':'Parent leaf counts at statement lines670/676/677/682 identify sampled accumulator-copy, per-arm-copy, env-copy and union sites. Samples do not separate first and later arm unions, count operations/cardinalities or establish removable fractions. Only the accumulator baseline copy and first-arm union are targets; all other copying/merging/traversal remains. No speedup or1800-second completion guarantee.',
 'preliminary_option':'The earlier unexecuted literal-key-cache preparation is retained in preliminary-literal-key with its initial source assessment and helper bytes. Final source review selected a smaller existing-set change. No literal-cache implementation or approval is requested, and no optimization attempt was consumed.',
 'retention':'The v64 one-profile budget and all six native regression budgets remain closed. Original fresh failures, invalid v50 attribution/V49 preparation, both singleton failures and all source-bound results remain unchanged and unaccepted where applicable. The1800-second shared policy remains.',
 'not_authorized':['another source-only optimization target or attempt','any corpus/profile/retry/comparator execution','new cache or dependency/resource/parallelism/deadline policy','target tests/build/install/endpoints','paid calls','merge/ready/release/outreach/Phase23'],
 'technical_acceptance_received':False,'phase22_complete':False
}
with (OUT/'optimization-proposal.json').open('x') as stream:
 json.dump(p,stream,indent=2);stream.write('\n')
print('Prepared one unapproved If invalidation-accumulator attempt:',sha(OUT/'optimization-proposal.json'))
