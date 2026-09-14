"""Prepare one unexecuted source-only literal-key serialization reuse attempt after profile assessment."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(OUT/'assessment.json')
assert a['validation_passed'] and a['source_assessment_complete_for_retained_outputs']
assert a['budget_closed'] and a['remaining']==0 and a['optimization_attempts']==0
assert not (BASE/'v69-ts-literal-key-reuse').exists()
source_files=['src/sentinel/static/path_flow.py','src/sentinel/static/typescript_discovery.py','src/sentinel/static/typescript_registration_flow.py','src/sentinel/static/model.py','src/sentinel/static/workers.py','src/sentinel/static/typescript_modules.py','src/sentinel/static/typescript_path_flow.py','src/sentinel/static/coverage.py','tests/test_static_workers.py','tests/test_typescript_discovery.py','tests/test_typescript_classes.py']
p={
 'status':'prepared_not_approved_not_started','recorded_at':datetime.now(timezone.utc).isoformat(),
 'starting_delivery':'c60b7a858497c355326044b959d9f6ad8d755a80','scanner':a['scanner'],'frozen_checkout':'/private/tmp/mcp-phase22-frozen-4145d35',
 'profile_assessment_sha256':sha(OUT/'assessment.json'),'source_assessment_sha256':sha(OUT/'source-assessment.json'),
 'target':'Reuse only the exact serialized JSON key for an immutable TypeScript literal node within its existing source program.',
 'target_files':['src/sentinel/static/typescript_discovery.py','src/sentinel/static/typescript_path_flow.py'],
 'source_files_sha256':{n:sha(ROOT/n) for n in source_files},
 'purpose':'Avoid repeating json.dumps(node["L"], sort_keys=True) on revisits to unchanged literal nodes in RegistrationFlow and other TypeScriptPathFlow consumers. Actual parent JSON-encoder leaf samples at that call site are retained below. Revisit counts, cache hits and achievable savings are unmeasured; this is not a promise of1800-second completion.',
 'proposed_change':'One source-only implementation of a bounded per-TypeScriptProgram cache for exact literal serialization strings, following the existing OrderedDict source_range identity-cache pattern. Maximum4096 entries, LRU eviction, retaining node/file objects with identity keys so synthetic object-id reuse cannot return another node result. Produce keys lazily only at the existing non-null/non-undefined literal expression branch; retain exact json.dumps input and sort_keys=True options. Recomputed evicted entries must return identical string content. New programs/workers reconstruct empty caches; no global cache or transported integer-id keys.',
 'identity_and_warning_contract':'Only a pure serialized string is reusable. Every expression still allocates its original fresh Value, updates nonnull_literals/string_literals/string_prefixes/mobilecli_paths/conditions, calls program.literal and executes subclass/RegistrationFlow bookkeeping. Preserve full Value fields, cache interning semantics, source-node aliases, all flow environments and side effects, ordered warnings, discovery bindings and reports. Do not cache a Value, function result, environment, security fact, warning, discovery result or HTTP result. Existing completed tool discovery and same-graph IPC remain unchanged.',
 'implementation_limit':'Use the existing stdlib OrderedDict pattern and one cache with4096 entries. No cache warming traversal, changed JSON options, literal/key normalization, negative/error caching, AST mutation, node/module/function pruning, function memoization, detector bypass, new dependency, worker/resource/deadline change or another optimization target. Preserve deadline checks and error behavior. If complete equivalence or avoided-serialization checks fail, preserve and close this one attempt; do not switch optimizations.',
 'bounds':{'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0},
 'verification':[
  'Preserve exact tested4145d35 source and trace all TypeScript literal-expression consumers, subclasses, generated/synthetic node lifetimes, string-key equality/identity consumers, and existing source_range cache behavior before implementation.',
  'Use existing scanner-owned synthetic ASTs to compare the complete original expression Value and entire flow state for strings/booleans/numbers and other supported literal shapes, null/undefined bypasses, same-content distinct nodes/files/programs, generated nodes, imported aliases, and all registration/security/HTTP consumers. Repeated calls must still rebuild deleted/mutated per-flow metadata exactly. No exposed-corpus fixture or timing measurement.',
  'Verify cold/warm paths and more than4096 entries through eviction against the preserved baseline. Keep complete equality and relevant Value/interning/source-node identity relations. Retain node/file references to prevent stale integer-id reuse, and verify fresh/pickle-reconstructed contexts do not share stale cache state.',
  'Synthetic invocation accounting must show fewer exact JSON serialization calls on retained repeated literal nodes while every original expression/metadata/subclass path runs. Verify zero caching of incomplete/error production, expired deadline rejection on warm cache, unsupported serialization error behavior, and unchanged input nodes. No throughput or native speedup claim.',
  'Compare complete ordered discovery results/warnings/options, all five rule outputs and full serial/parallel Python/TypeScript/mixed reports using existing tests; retain source/file aliases and all shared discovery/deadline/worker cleanup controls. This cache must not change worker IPC or bypass any rule-specific analysis.',
  'If one attempt passes full equivalence and avoided-work prerequisites, complete affected and full local/hosted engineering under the user prompt section8: strict whole-scope quality, schemas/lock/notices/advisories/offline artifacts, docs/packages/installed-wheel matrix, Docker/isolation/Action/hooks and all required CI. Regenerate/revalidate six complete production requests and approved runtime/image compatibility with live transport forbidden. Freeze the actual tested candidate and prepare separately approved affected regression. No corpus/profile/retry or paid call follows from this source-only approval.'
 ],
 'profile_metrics':a['sample_rows'],
 'uncertainty':'Only the retained sampled JSON encoder leaf work at the literal call site is measured. Its percentage is not a removable-cost estimate; cache hits/evictions/overhead and unsampled work remain unknown. Module traversal, merges, registrations, all later detectors and coverage still run. Even eliminating all of this sampled leaf cost might be insufficient for1800-second completion; no duration or savings guarantee is offered.',
 'retention':'The approved v68 sampled budget and all seven historical native regression budgets stay closed. Original four fresh failures, invalid v50 attribution/V49 preparation, both singleton failures and every earlier source-bound result remain unchanged and unaccepted where applicable. The1800-second shared policy remains retained.',
 'not_authorized':['another source-only optimization target or attempt','any corpus/profile/retry/comparator execution','new dependency/resource/parallelism/deadline policy','target tests/build/install/endpoints','paid calls','merge/ready/release/outreach/Phase 23'],
 'technical_acceptance_received':False,'phase22_complete':False
}
p['implementation_prerequisites'] = 'Prove which source and generated nodes remain immutable before caching. Preserve error behavior and reject or bypass any ineligible mutable/unsupported node according to the existing contract; no silent newly narrowed domain. Inspect all string-key identity comparisons and shared Value interning across cold/warm/evicted cache states. A source-only attempt may change only the two target source files plus required scanner-owned tests and release notes. If strict equivalence cannot hold, retain the counterexample and restore the exact baseline; any contract revision requires separate approval.'
p['prior_preparation'] = 'The v64 preliminary literal-key preparation was never delivered as the selected optimization or approved/implemented. This is a separately bound current-source proposal after the v66 accumulator revision and v68 profile. Earlier raw metrics are not reused as current evidence.'
p['retention'] += ' The v65 strict invalidation failure and explicit v66 private-domain revision remain distinct and unchanged.'
with (OUT/'optimization-proposal.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
print('Prepared one unapproved literal-key serialization reuse attempt:',sha(OUT/'optimization-proposal.json'))
