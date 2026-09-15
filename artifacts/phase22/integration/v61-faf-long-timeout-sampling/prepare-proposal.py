"""Prepare one unexecuted source-only discovery-reuse attempt after profile assessment."""
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
assert not (BASE/'v62-shared-tool-discovery').exists()
source_files=['src/sentinel/static/typescript_discovery.py','src/sentinel/static/typescript_registration_flow.py','src/sentinel/static/model.py','src/sentinel/static/workers.py','src/sentinel/static/typescript_modules.py','src/sentinel/static/typescript_path_flow.py','src/sentinel/static/coverage.py','tests/test_static_workers.py','tests/test_typescript_discovery.py','tests/test_typescript_classes.py']
p={
 'status':'prepared_not_approved_not_started','recorded_at':datetime.now(timezone.utc).isoformat(),
 'starting_delivery':'777c7526f18733b7ca4b49e3caf690f02d25adf6','scanner':a['scanner'],
 'profile_assessment_sha256':sha(OUT/'assessment.json'),'source_assessment_sha256':sha(OUT/'source-assessment.json'),
 'target':'Reuse one completed TypeScript MCP tool-discovery result within the existing source context and across its existing rule workers.',
 'target_files':['src/sentinel/static/typescript_discovery.py','src/sentinel/static/model.py','src/sentinel/static/workers.py'],
 'source_files_sha256':{n:sha(ROOT/n) for n in source_files},
 'purpose':'Remove repeated identical registration discovery before rule-specific analysis and later parent coverage. The sampled factory traversal is expensive in all four verified workers. This is source-established duplicate work, not a measured achievable speedup or a promise of 30-minute completion.',
 'proposed_change':'One source-only reuse implementation: retain a successfully completed ordered tools() result for one immutable TypeScriptProgram, and provide it together with its discovery warning effects to the existing large-input workers through the SAME private pickle graph as the parsed trees and files. Reuse it for parent coverage. Preserve the tools() call contract and deadline check. Every rule-specific analysis, HTTP discovery and coverage interpretation still executes; no node, module, function, candidate or diagnostic is skipped.',
 'identity_and_warning_contract':'Serialized tool symbols must reference the same reloaded nodes and files as the worker trees; reconstruct identity-keyed program indexes from those reloaded objects. Do not copy old integer id() keys. Bind reuse only to the current immutable source/configuration context, with no process-global or cross-scan cache. Reproduce ordered discovery warnings at their original consumption point, including module-option-cache effects, pre-existing warnings and repeated-call deduplication. Empty completed results are reusable; incomplete/failed/interrupted results never are.',
 'implementation_limit':'Use existing cached-property/private-IPC patterns. Only the TypeScript discovery result and its required warning/state effects are reused. No additional HTTP-result cache, general interpreter memoization, new dependency, pruning, worker-count change, new resources or timeout revision. If full ordered equivalence or source-node identity cannot be preserved within this one attempt, stop and close it; do not switch to another optimization.',
 'bounds':{'source_only_optimization_attempts':1,'corpus_observations':0,'profiles':0,'comparators':0,'retries':0,'new_repositories':0,'paid_calls':0,'target_execution':False,'runtime_campaigns':0},
 'verification':[
  'Preserve exact 7bf4c6e source before editing. Trace all tools() callers and program/Module warning and option-cache effects; preserve complete source-node aliases through a single IPC graph and rebuild identity indexes.',
  'Extend existing synthetic TypeScript discovery and worker serial/parallel equivalence checks. Compare all ordered binding fields, factory/SDK registrations, file/source ranges, node/file alias identities, complete rule state, warnings, unresolved flows, coverage/surfaces and final reports. Cover constructors and saved setters, imported aliases/workspace exports, unsupported/rebound registrations, empty discovery, repeated calls and pre-existing/module warnings. Use fresh contexts and a pickle round trip; identical-looking different source/configuration contexts must not share results.',
  'Synthetic call accounting must show one producer discovery reused by the existing four workers and coverage in the eligible path, while rule-specific detectors still run fully. Preserve small-input, selected-rule, Python-only and mixed-language behavior. No timing or source-corpus observation is part of this check.',
  'Check deadline expiration before reuse and during production, failed/incomplete producer behavior, existing scanner-owned IPC validation, target-import prohibition and all owned-process cleanup paths. Never cache a partial result as completed.',
  'If the one attempt passes complete equivalence and avoided-work checks, complete affected/full local and hosted engineering under section 7: strict types/lint/format, schemas/lock/notices/advisories/offline artifacts, docs/packages/installed wheels, Docker/isolation/Action/hooks and production/runtime compatibility with zero paid calls. Freeze the actual tested source and prepare a separately approved current-source regression. No corpus/profile execution follows from this source-only approval.'
 ],
 'profile_metrics':a['sample_rows'],
 'uncertainty':'Sampling does not establish total invocation counts, the single-producer completion time, or the later rule-specific/HTTP/coverage costs. Concurrent worker CPU shares overlap and include sampling effects. Removing repeated discovery may expose another bottleneck or still fail at 1800 seconds. No savings percentage or completion guarantee is claimed.',
 'retention':'The approved v61 profile budget and every earlier native/profile/optimization budget remain closed. Original fresh four gates, singleton failures, invalid v50 profile and all prior source-bound results remain unchanged. The 1800-second product policy remains retained.',
 'not_authorized':['another source-only optimization target or attempt','any corpus/profile/retry/comparator execution','new dependency/resource/parallelism/deadline policy','target tests/build/install/endpoints','paid calls','merge/ready/release/outreach/Phase 23'],
 'technical_acceptance_received':False,'phase22_complete':False
}
with (OUT/'optimization-proposal.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
print('Prepared one unapproved discovery-reuse attempt:',sha(OUT/'optimization-proposal.json'))
