"""Retain every audit row and reconcile the actual stopped regression."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];oldpath=base/'v67-invalidation-regression'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=read(out/'assessment.json');old=read(oldpath/'audit.json')
assert a['source_assessment_complete_for_retained_outputs'] and a['budget_closed']
assert read(base/'v68-optimization-proposal.json')['exit_code']==0 and read(base/'v68-compatible-reuse.json')['exit_code']==0 and read(out/'recovery-assessment.json')['passed']
rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
 if row['id'] in {'V67-DELIVERY','V67-DIAGNOSTIC-DECISION'}:
  row['previous_row']=copy.deepcopy(row)
  name='delivery-verification.json' if row['id']=='V67-DELIVERY' else 'diagnostic-authorization.json'
  row.update(disposition='passed',evidence=[str((oldpath/name).relative_to(root))],assessment='Actual c60b7a8 draft delivery verified.' if name.startswith('delivery') else 'User approved the exact one-profile proposal. Initial read-only preflight failed before consumption; verified restoration preceded the sole actual attempt. Profile timed out and budget is closed. This is not technical acceptance.')
new=[('AUTH','Bind exact one-profile approval, original and restored preflights and sole consumed token','passed',['../v67-invalidation-regression/diagnostic-authorization.json','../v67-invalidation-regression/restored-launch-preflight.json','attempt.json']),('RECOVERY','Preserve file-disappearance failure and restore only missing verified tracked, sealed and protected-user bytes','passed',['recovery-assessment.json','../v67-invalidation-regression/worktree-restoration.json','../v67-invalidation-regression/sealed-evidence-restoration.json']),('DOCKER-CLEANUP','Carry out authorized selective unused Docker cleanup and verify protected resources and actual physical/logical accounting','passed',['recovery-assessment.json','../v67-invalidation-regression/docker-cleanup.json','../v67-invalidation-regression/base-image-cleanup.json']),('PROFILE-VALIDATION','Validate actual source identity, every retained partial sample, output, timeout and closed budget','passed',['validation.json','sample-attribution.json','owned-work.json']),('SOURCE-ASSESSMENT','Assess every retained frame and exact source context while preserving final-snapshot and attribution limits','passed',['assessment.json','source-assessment.json','frame-contexts.json']),('OPT-PREPARATION','Prepare one bounded current-source literal serialization reuse attempt without implementation or measurement','passed',['optimization-proposal.json']),('OPT-DECISION','Obtain separate exact approval before the proposed source-only optimization attempt','unresolved',['optimization-proposal.json']),('DELIVERY','Seal current profile and recovery evidence, retain every prior requirement and verify existing draft delivery','unresolved',[])]
for identity,requirement,disposition,evidence in new:
 rows.append({'id':'V68-'+identity,'requirement':requirement,'disposition':disposition,'evidence':[str((out/n).resolve().relative_to(root)) for n in evidence],'assessment':'One current-source partial parent profile:148001samples,1800.013225seconds,no report,cleanup verified,one-use budget closed. Final snapshot and timer restoration unconfirmed. Recovery and selective Docker cleanup verified. Proposed source-only literal serialization reuse remains unapproved/unimplemented. All current-source gates and separate human acceptance remain unresolved.'})
assert len(old['requirements'])==89 and len(old['additional_scope_requirements'])==294 and len(rows)==302
for before,after in zip(old['additional_scope_requirements'],rows):assert before==after or after.get('previous_row')==before
audit=copy.deepcopy(old)
audit['historical_v67_status_fields']={k:copy.deepcopy(v) for k,v in old.items() if k not in {'requirements','additional_scope_requirements'} and not k.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(r['disposition'] for r in rows)),prior_audit={'path':str((oldpath/'audit.json').relative_to(root)),'sha256':sha(oldpath/'audit.json')},current_diagnostic_prepared=True,current_diagnostic_approved=True,current_diagnostic_executed=True,valid_current_source_profiles=1,diagnostic_attempts=1,diagnostic_remaining=0,current_optimization_prepared=True,current_optimization_approved=False,current_optimization_executed=False,optimization_attempts=0,acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,status='One approved sampled FAF input at4145d35 timed out after1800.013225seconds;148001periodic parent samples,no report,cleanup verified and budget closed. A source-only literal serialization cache is prepared,unapproved and unimplemented. Current-source gates remain unresolved.')
audit['current_source_input_accounting']={'native_regression':{'attempts':1,'complete':0,'incomplete':1,'unstarted_closed':204,'remaining':0,'budget_closed':True},'sampled_diagnostic':{'attempts':1,'approved':True,'complete':0,'incomplete':1,'valid_partial_snapshots':1,'samples':148001,'remaining':0,'budget_closed':True},'total_attempted_inputs':2,'initial_read_only_failed_preflight_attempts':0}
audit['current_budget_interpretation']='Native205 sequence and one sampled diagnostic are separately closed. Source-only optimization is unapproved and includes no corpus/profile/retry/paid budget. No historical budget is reopened.'
for row in old['requirements']+old['additional_scope_requirements']:
 entry=copy.deepcopy(old.get('current_requirement_interpretations',{}).get(row['id'],{}))
 entry.update(requirement=row['requirement'],historical_disposition=row['disposition'],current_execution_interpretation='Engineering at4145d35 remains verified. Its native and sampled FAF inputs timed out without reports; no current-source detection, fixed/control support, compatibility, native speedup or accepted limitation follows. Current profile source/frame assessment and exact file recovery are complete. Every earlier source-bound result and failed gate remains.',current_execution_evidence={'assessment_sha256':sha(out/'assessment.json'),'compatibility_sha256':sha(out/'compatible-reuse.json'),'recovery_sha256':sha(out/'recovery-assessment.json')})
 audit['current_requirement_interpretations'][row['id']]=entry
assert len(audit['current_requirement_interpretations'])==383
assert audit['additional_scope_dispositions']=={'passed':277,'unresolved':19,'proposed documented limitation awaiting decision':6},audit['additional_scope_dispositions']
audit['current_evidence']={n:sha(out/n) for n in ['assessment.json','validation.json','budget-closed.json','source-assessment.json','optimization-proposal.json','compatible-reuse.json','owned-work.json','recovery-assessment.json']}
write('audit.json',audit)
write('prior-row-preservation.json',{'prior_audit_sha256':sha(oldpath/'audit.json'),'retained_prior_rows':383,'total_rows':391,'updated_rows':['V67-DELIVERY','V67-DIAGNOSTIC-DECISION'],'rows':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest() for r in old['requirements']+old['additional_scope_requirements']}})
status="""## Current v68 invalidation profile: source-only decision pending

The approved FAF profile at frozen **`4145d35`** timed out after **1800.013225
seconds**, retaining **148,001 verified parent samples** and no report. Cleanup
passed after forced termination; the periodic snapshot does not confirm final
snapshot completion or timer restoration. No worker snapshot exists; worker
launch history and costs are unestablished. The one-use budget is closed.
Registration discovery is 99.86% inclusive; literal serialization is 3.85% of
parent leaf samples. These overlapping partial shares establish no speedup,
removable fraction, detection or compatibility.

`v68-invalidation-sampling/optimization-proposal.json` prepares **one unapproved,
unimplemented source-only literal serialization reuse attempt**: a bounded
per-program cache for exact strings, with fresh Values and all analysis/state
updates retained. Full identity, cold/warm/eviction, error/deadline and ordered
report equivalence plus engineering are required. No corpus/profile/retry,
resource/deadline revision, target execution or paid call is included.

An initial read-only launch preflight failed before any input/token because files
had disappeared. Verified recovery restored 25,941 tracked files, six worktree
links, 7,667 expanded evidence files and two protected user documents without
overwriting existing bytes. The cause remains unknown. User-authorized Docker
cleanup removed five unused public base images; project images, all containers
and volumes remain. Logical image storage fell 2.89GB; delayed physical recovery
is separately recorded. The same unused profile approval then ran once.

All **391 requirements (89 original + 302 added)** remain, including seven native
timeouts, six valid partial profiles, invalid stale-root preparation, both
singleton failures, the original strict invalidation failure and six unaccepted
historical closure proposals. Product retains tested `4145d35`: **2,419 tests /
36 skips** locally and all 12 hosted suites, 29 normal CI jobs and docs passed.
Combined coverage is 90.08%, branch-only 85.92%; six zero-call production replays
and approved runtime bindings remain. This continuation adds profile/recovery
assessment and docs/package checks, not another hosted code pass.

**Phase 22 remains incomplete**, pending current-source gates, explicit human
technical acceptance and accepted closeout. Git stays 312/1,040 incomplete, with
728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete and Phase 24/15
unchanged. No merge, ready-state change, release, outreach or Phase 23 is authorized.

"""
heading='## Current v67 invalidation regression: timed out, budget closed'
docs=list(read(oldpath/'documentation-binding.json')['owning_docs_sha256'])
assert len(docs)==16
for name in docs:
 path=root/name;text=path.read_text();assert text.count(heading)==1,name
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
write('owning-docs.json',{'sha256':{n:sha(root/n) for n in docs}})
(out/'status.md').write_text(status)
print('Preserved383prior rows,391total; reconciled16owning docs. Optimization remains unapproved.')
