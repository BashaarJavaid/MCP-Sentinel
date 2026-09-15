"""Preserve every prior requirement and add the bounded unseen continuation."""
import collections,copy,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];BASE=OUT.parent;OLD=BASE/'v76-technical-acceptance'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
old=read(OLD/'audit.json');a=copy.deepcopy(old);proposal=read(OUT/'evaluation-proposal.json')
a['historical_v76_status_fields']={k:v for k,v in old.items() if k not in ['requirements','additional_scope_requirements','current_requirement_interpretations'] and not k.startswith('historical_')}
a.update(recorded_at=datetime.now(timezone.utc).isoformat(),status='Fresh two-repository proposal prepared; exact numerical approval pending. Phase22 incomplete.',source='09fa6ce8541fde5deb1f45055ac9e6de5c8c391c',prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0)
a['new_unseen_scope']={'proposal_sha256':sha(OUT/'evaluation-proposal.json'),'prepared':True,'approved':False,'executed':False,'repository_cases':2,'distinct_input_records':6,'proposed_observations':12,'observations':0,'proposed_ordered_pairs':6,'paid_calls':0,'target_execution':False,'normal_policy_unchanged':True,'source_assessment_pending':True}
a['current_budget_interpretation']='V73 andV75 exact budgets remain closed at24+181observations and95ordered pairs. NewV77proposal12observations is unapproved; no launch token exists and zero fresh inputs have run. No previous allowance is reopened.'
receipt=read(OLD/'delivery-verification.json');assert receipt['passed'] and receipt['head']=='09fa6ce8541fde5deb1f45055ac9e6de5c8c391c'
rows=a['requirements']+a['additional_scope_requirements']
for row in rows:
 if row['id']=='V76-REVIEW-DELIVERY':
  previous=copy.deepcopy(row);row.update(disposition='passed',previous_row=previous,assessment=receipt['effective_scope_disposition']['basis']);row.setdefault('evidence',[]).append(str((OLD/'delivery-verification.json').relative_to(ROOT)))
  interpretation=a['current_requirement_interpretations'][row['id']];previous=copy.deepcopy(interpretation);interpretation.update(previous_interpretation=previous,current_disposition='passed',current_execution_interpretation='Actual supplemental V76 delivery verified09fa6ce; sealed pending row retained. Resolves only review delivery, not acceptance.')
new=[('FREEZE','Bind cec0322 and complete pre-curation exposure inventory before candidate research','passed',['scope-and-precuration-freeze.json']),('NOVELTY','Verify two distinct previously unused source families including names, forks and source fingerprints','passed',['novelty-comparison.json','selection-record.json']),('SOURCE','Freeze complete upstream pairs, licenses, source conditions, six records and actual configurations before any scan','passed',['cases.json','staging-and-boundary-verification.json']),('RUNNER','Verify normal deadlines, exact approval, cancellation, cleanup, schemas and ordered collection using synthetic controls','passed',['runner-boundaries.json','collection-checks.json','staging-and-boundary-verification.json']),('PROPOSAL','Prepare exact separately approvable twelve-observation proposal with finite outer bound and prospective stops','passed',['evaluation-proposal.json','launcher-binding.json']),('REUSE','Verify unchanged303engineering inputs,19runtime components and six production request bindings','passed',['preparation-baseline.json']),('APPROVAL','Obtain exact human approval before any new numerical launch','unresolved',['evaluation-proposal.json']),('EXECUTION','Execute only the approved first-frozen order and close its entire budget with verified cleanup','unresolved',['evaluation-proposal.json']),('ASSESSMENT','Source-assess every actual finding, diagnostic, surface, support denominator and entire ordered difference','unresolved',['scoring-rubric.json']),('REVIEW','Reconcile all requirements and deliver an updated complete technical acceptance proposal after unseen results','unresolved',['evaluation-proposal.json']),('ACCEPTANCE','Obtain separate explicit human Phase22 technical acceptance of the updated delivered packet','unresolved',['evaluation-proposal.json']),('CLOSEOUT','Record and deliver verified accepted closeout to the same OPEN DRAFT PR37','unresolved',['evaluation-proposal.json']),('DELIVERY','Complete affected docs/packages, seal and verify delivery of this exact numerical proposal to existing draft PR37','unresolved',['evaluation-proposal.json'])]
for suffix,text,status,evidence in new:
 row={'id':'V77-'+suffix,'requirement':text,'disposition':status,'assessment':('Source-only preparation and synthetic checks passed; zero corpus observations/paid calls. ' if status=='passed' else 'Pending actual required event; neither continue nor preparation implies numerical approval or technical acceptance. ')+text,'evidence':[str((OUT/p).relative_to(ROOT)) for p in evidence]}
 a['additional_scope_requirements'].append(row);a['current_requirement_interpretations'][row['id']]={'requirement':text,'current_disposition':status,'current_execution_interpretation':row['assessment'],'evidence':row['evidence']}
a['dispositions']=dict(collections.Counter(x['disposition'] for x in a['requirements']));a['additional_scope_dispositions']=dict(collections.Counter(x['disposition'] for x in a['additional_scope_requirements']))
for before,after in zip(old['requirements']+old['additional_scope_requirements'],a['requirements']+a['additional_scope_requirements']):assert before==after or after.get('previous_row')==before
assert len(a['requirements'])==89 and len(a['additional_scope_requirements'])==346
assert sum(x['disposition']=='proposed documented limitation awaiting decision' for x in a['requirements']+a['additional_scope_requirements'])==23
write(OUT/'audit.json',a)
write(OUT/'prior-row-preservation.json',{'passed':True,'prior_audit_sha256':sha(OLD/'audit.json'),'prior_rows':422,'unchanged_rows':421,'one_resolved_delivery_row_retains_previous_row':True,'new_rows':13,'total_rows':435,'proposed_limitations_unaccepted':23,'technical_acceptance_received':False})
summary='''# Phase 22 unseen-source evaluation proposal

**Two repositories, six source records, twelve proposed observations. No numerical approval or new scans yet. Phase 22 remains incomplete.**

The scanner is frozen at `cec0322e904bbf63c33cd95796e7289101a93e5d`. Source, harness, lock and actual isolated imports are bound before curation. Both selected complete upstream pairs are first-parent verified and absent from recorded project exposure; comparison covers 3,781 distinct prior archives with no substantive file overlap (only an empty test initializer).

| Order within each pass | Repository / actual language | Named condition | Vulnerable → fixed commits |
| --- | --- | --- | --- |
| 1–3 | awwaiid/mcp-server-taskwarrior / TypeScript | `mark_task_done.identifier` shell interpolation → shell-free argv, SENT-002 | `d502ad2` → `29850c7` |
| 4–6 | nick-holmquist/proxmox-mcp / Python | `pve_storage_upload.file_path` local open outside operator upload root → checked resolved path, SENT-012 | `3d6610b` → `39889d5` |

For each repository: vulnerable, fixed, safe; then repeat the same six in that order. Each safe record uses the complete fixed tree/configuration and a source-defined safe caller value. Repeats and related variants are correlated. Taskwarrior has a complete MIT license; Proxmox declares MIT in README/pyproject but has no standalone license/full grant text (GitHub license=null). Taskwarrior's current GitHub language metadata says JavaScript; selected source/configuration are TypeScript. Required Taskwarrior `zod` is imported but not directly declared in its package dependencies. All prerequisites and exclusions remain explicit in the source reviews; targets are never installed or executed.

Normal whole-input/static maximum **1,800 seconds**, Semgrep **10 seconds**, cleanup **15 seconds**, maximum existing **four workers**, one input at a time. The internal stop is **378 minutes**; outer process maximum **380 minutes**, plus its separate **15-second cleanup**. This comprises 363 minutes input/cleanup, 15 minutes setup/identity reserve and 2 minutes finalization. It is a worst-case cap, not an estimate. No child starts unless its full input/cleanup allowance fits. Whole-input time includes child startup/imports/materialization/analysis/reporting.

Cancellation, identity/infrastructure/execution/timeout/schema/cleanup/entire-ordered-repeat failures close unused budget. Detection misses, false alerts and unsupported negatives remain failed gates while collecting the remaining approved cases. No tuning, retry, replacement, profile, comparator, target execution, resource change or paid call. All six entire ordered reports must match on repeat after only the existing eleven volatile exclusions. Every finding, diagnostic, unresolved surface and support denominator requires source assessment. Quiet unsupported negatives fail; no positive per-sink trace is invented.

The artifact-local six-input schema reuses existing Input/Snapshot, archive/path/hash/license validators, exact frozen approval and production measure. It changes only the old corpus population/rule-ID admission for this packet; product/harness files remain unchanged. Synthetic checks caught an immediate-alarm budget-record issue in the new helper, corrected before any execution; original helpers and failures are preserved.

[Exact proposal](evaluation-proposal.json), [rubric](scoring-rubric.json), [source cases](cases.json), [selection/qualifications](selection-record.json), [435-row audit](audit.json), [prior-row preservation](prior-row-preservation.json), [staging and missing-approval checks](staging-and-boundary-verification.json), [synthetic collection checks](collection-checks.json).

V73/V75 remain separate closed approvals: 205 exposed observations, 95 entire ordered pairs and narrow current-source passes. Engineering remains actual cec0322: 2,450 tests/36 skips locally and in12 hosted suites,29 normal jobs/docs,90.11% combined/85.97% branch coverage,303engineering inputs,6zero-call production requests and19runtime components. This proposal adds affected docs/package and helper checks, not a new hosted code pass. All422 previous rows persist; only supplemental V76 review delivery is resolved, with its sealed previous row preserved.

All23 historical/practical limitation proposals remain unaccepted. Ordinary FAF completion within1,800seconds remains unestablished; six V73 uncapped observations took2,297.758–2,735.386seconds. V68 stays unapproved/unimplemented. Original held-out/fresh/native/profile/equivalence failures, two Meta operator errata and unrelated candidates remain. Git312/1,040incomplete/728deferred,396-request paid benchmark and pilots deferred; Phase21 incomplete and Phase24/15 unchanged. Historical paid spend remains$0.071799; zero new calls.

After exact numerical approval: execute once, assess all outcomes, handle justified follow-up under applicable approvals, deliver a new complete technical acceptance proposal, obtain explicit human technical acceptance, then deliver and verify accepted closeout. No merge, ready-state change, release, outreach or Phase23 is authorized.
'''
(OUT/'summary.md').write_text(summary)
block='''## Current v77 unseen-source preparation: exact evaluation approval pending

Two previously unused repository cases are prepared at frozen **`cec0322`**:
TypeScript Taskwarrior shell interpolation and Python Proxmox upload containment.
The exact proposal is **6 source records × 2 passes = 12 observations**, unapproved
and unexecuted, using normal **1,800-second input / 10-second Semgrep / 15-second
cleanup**, four-worker maximum, **380-minute outer limit plus 15-second cleanup**.
Source novelty, complete upstream pairs, license qualifications and synthetic
approval/stop/cleanup checks are retained in
`artifacts/phase22/integration/v77-unseen-preparation/`.

All **435 requirements (422 retained + 13 new)** remain explicit. V73/V75 retain
205 exposed observations and 95 equal entire ordered pairs; unchanged `cec0322`
engineering remains 2,450 tests / 36 skips. The 23 historical/practical limitations
remain unaccepted, including ordinary FAF completion within 1,800 seconds and
leaving V68 unopened. Git stays 312/1,040 incomplete, 728 deferred; paid benchmark
and pilots deferred, Phase 21 incomplete, Phase 24/15 unchanged. **Zero new paid calls.**

**Phase 22 remains incomplete** pending the additional unseen check, a newly
delivered complete review, explicit human technical acceptance and verified
accepted closeout. No merge, ready-state, release, outreach or Phase 23.

'''
paths=read(OLD/'documentation-binding.json')['owning_docs_sha256']
for name in paths:
 p=ROOT/name;s=p.read_text();assert '## Current v77 ' not in s
 s=s.replace('## Current v76 technical review:','## Historical v76 technical review:',1)
 first,rest=s.split('\n',1);p.write_text(first+'\n\n'+block+rest.lstrip('\n'))
write(OUT/'owning-docs.json',{'sha256':{n:sha(ROOT/n) for n in paths}})
corpus=ROOT/'artifacts/phase22/corpus-unseen-v1';(corpus/'README.md').write_text('# Two-repository unseen-source packet\n\nSix immutable vulnerable/fixed/safe records at scanner `cec0322`, proposed twice. No approval or scans yet.\n\nSee [proposal summary](../integration/v77-unseen-preparation/summary.md), [manifest](manifest.json), [checkpoint](checkpoint-cec0322.json), [novelty](novelty.json), and each repository condition review. Proxmox has declaration-only MIT evidence; Taskwarrior has a full license. No target execution or paid calls. All previous corpus files remain unchanged.\n')
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v77-unseen-preparation/'
body=f'''Phase 22 now has a prepared **two-repository unseen-source proposal** at frozen `cec0322`: TypeScript Taskwarrior shell interpolation and Python Proxmox local upload-path containment. **Six source records,12 proposed observations,6 entire ordered pairs; unapproved and unexecuted.** Source novelty, actual upstream fix pairs, licensing and source prerequisites are frozen before scanning.

[Summary]({url}summary.md) · [Exact proposal]({url}evaluation-proposal.json) · [435-row audit]({url}audit.json). Proposal SHA-256 `{sha(OUT/'evaluation-proposal.json')}`.

Order: Taskwarrior vulnerable/fixed/safe, Proxmox vulnerable/fixed/safe, then the same six repeated. Normal1,800-second input,10-second Semgrep,15-second cleanup,four-worker maximum. Outer380minutes plus15seconds cleanup; worst-case bound, not estimate. Execution/identity/schema/timeout/cleanup/repeat failures close unused scope; named misses/false alerts/unsupported negatives remain failed gates while collecting the rest. Zero retries/profiles/comparators/target execution/paid calls.

Existing exposed evidence remains205completed observations/95equal ordered pairs. Unchanged engineering:2,450tests/36skips locally and all12hosted suites,29normal jobs/docs; affected docs/packages and synthetic helper checks accompany this preparation. All422prior requirements persist, with13new continuation rows. Ordinary FAF1,800-second completion remains unestablished; V68stays unapproved/unimplemented. All23limitations remain unaccepted. Git312/1,040incomplete/728deferred; paid benchmark/pilots deferred; Phase21incomplete,Phase24/15unchanged.

**Phase22remains incomplete.** Exact evaluation approval, subsequent full source assessment, a new delivered technical acceptance packet, explicit human acceptance and verified accepted closeout are separate events. No merge, ready-state, release, outreach or Phase23.
'''
(OUT/'pr-body.md').write_text(body)
print('Preserved422rows, resolved only actualV76delivery, added13rows; updated16owning docs. No acceptance or evaluation inferred.')
