"""Reconcile the verified joint correction without accepting any historical failure."""
import copy,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=Path.cwd();OLD=BASE/'v56-canonical-unknown'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
local=read(OUT/'local-checks.json');quality=read(BASE/'v57-candidate-quality-audit/packet.json');proposal=read(OUT/'evaluation-proposal.json');freeze=read(OUT/'freeze.json')
assert local['states']=={'passed':2399,'skipped':36}
assert len(quality['quality'])==12 and proposal['scanner']==freeze['scanner']
assert not (OUT/'evaluation-authorization.json').exists() and not (BASE/'v58-credential-regression').exists()
old=read(OLD/'audit.json');rows=copy.deepcopy(old['additional_scope_requirements'])
for row in rows:
    if row['id'] in {'V56-DELIVERY','V56-REVISION-DECISION'}:
        row['previous_row']=copy.deepcopy(row)
        evidence=OLD/'delivery-verification.json' if row['id']=='V56-DELIVERY' else OUT/'authorization.json'
        row.update(disposition='passed',evidence=[str(evidence.relative_to(ROOT))],assessment='Verified9b2585d draft delivery or subsequent continue instruction after the exact joint revision was explained. This is prospective correction approval, not acceptance of either historical singleton failure or Phase22.')
new=[
 ('V57-AUTH','Bind the explained prospective marker-join revision and joint attempt to the actual continue instruction','passed',['authorization.json']),
 ('V57-CORRECTION','Verify and retain every intentional equal-marker state delta and all downstream guard/cache effects','passed',['correction-validation.json','source-recovery-assessment.json']),
 ('V57-BYPASS','Require complete bypass equivalence against the correction-only reference including saturated cache eviction','passed',['synthetic-validation.json','correction-only-path-flow.py','correction-only-sent016.py']),
 ('V57-SYNTHETIC-REPORTS','Preserve complete ordered credential rule output on existing synthetic caller-to-operator cases','passed',['synthetic-reports.json']),
 ('V57-ENGINEERING','Complete affected/full local and all hosted engineering, package/schema/lock/docs and strict quality checks','passed',['local-checks.json','../v57-candidate-quality-audit/packet.json']),
 ('V57-CAPTURES','Verify six unchanged production request replays and approved runtime/image bindings with zero paid calls','passed',['compatibility.json','demo-validation.json','../v57-production-capture-revalidation/packet.json']),
 ('V57-FREEZE','Freeze exact verified scanner/harness/lock and validate every unchanged exposed source binding','passed',['freeze.json','frozen-source-validation.json']),
 ('V57-REGRESSION-PREPARATION','Prepare a separately approved205-observation both-language exposed regression without execution','passed',['evaluation-proposal.json','scoring-rubric.json','launcher-binding.json']),
 ('V57-REGRESSION-DECISION','Obtain exact new numerical approval before any current-source corpus observation','unresolved',['evaluation-proposal.json']),
 ('V57-FAILURE-RETENTION','Preserve both original singleton failures and all helper/check defects with correct dispositions','passed',['correction-validation.json','check-failure-assessment.json','source-recovery-assessment.json']),
 ('V57-DELIVERY','Seal final evidence, reconcile every prior requirement and verify existing draft delivery','unresolved',[]),
]
for identity,requirement,disposition,evidence in new:rows.append({'id':identity,'requirement':requirement,'disposition':disposition,'evidence':[str((OUT/name).resolve().relative_to(ROOT)) for name in evidence],'assessment':'Prospective equal-marker semantic correction verified separately from full bypass equivalence. Engineering and source-only prerequisites pass;205exposed observations remain unapproved. No historical failure, fresh-generalization claim or Phase22 technical acceptance follows.'})
audit=copy.deepcopy(old);audit['historical_v56_status_fields']={key:copy.deepcopy(value) for key,value in old.items() if key not in {'requirements','additional_scope_requirements'} and not key.startswith('historical_')}
audit.update(recorded_at=datetime.now(timezone.utc).isoformat(),source=freeze['scanner']['revision'],scanner_identity=freeze['scanner'],candidate_scanner=freeze['scanner'],hosted_quality='v57-candidate-quality-audit/packet.json',additional_scope_requirements=rows,additional_scope_dispositions=dict(Counter(row['disposition'] for row in rows)),prior_audit={'path':str((OLD/'audit.json').relative_to(ROOT)),'sha256':sha(OLD/'audit.json')},source_recovery_approved=True,engineering_passed=True,regression_prepared=True,regression_approved=False,regression_executed=False,current_regression_prepared=True,current_regression_approved=False,current_regression_executed=False,proposed_native_observations=205,current_source_corpus_observations=0,current_source_completed_observations=0,current_source_incomplete_observations=0,unstarted_closed=0,remaining=0,budget_closed=True,execution_gate_passed=None,diagnostic_prepared=False,diagnostic_approved=False,diagnostic_executed=False,diagnostic_attempts=0,diagnostic_completed_inputs=0,diagnostic_budget_closed=True,diagnostic_remaining=0,valid_current_source_profiles=0,current_diagnostic_prepared=False,current_diagnostic_approved=False,current_diagnostic_executed=False,current_optimization_prepared=True,current_optimization_approved=True,current_optimization_attempts=1,optimization_prepared=True,optimization_approved=True,optimization_attempts=1,optimization_synthetic_verified=True,optimization_budget_closed=True,optimization_remaining=0,candidate_retained_in_product=True,next_optimization_prepared=False,next_optimization_approved=False,next_optimization_attempts=0,prospective_contract_revision_prepared=True,prospective_contract_revision_approved=True,current_budget_interpretation='One authorized joint source-only attempt consumed/closed after engineering. Zero approved current-source corpus/profile budget.205observations are newly proposed, not remaining permission. All old native/profile/failure evidence retains its actual scanner under historical status fields.',acceptance_packet_ready=False,technical_acceptance_requested=False,technical_acceptance_received=False,phase22_complete=False,new_paid_calls=0,status='Approved equal-marker credential correction and canonical unknown bypass verified atdc73715:4050correction cases with552marker/552derived cache-input deltas,2430full bypass state comparisons, two evictions and seven unchanged ordered synthetic rule cases.2399tests/36skips locally and all12hosted suites;29normal jobs/docs pass.205exposed observations are unapproved/unexecuted. Both historical singleton failures and all original fresh/native/profile failures remain unchanged; Phase22 incomplete.')
audit['current_evidence']={name:sha(OUT/name) for name in ['authorization.json','source-recovery-assessment.json','correction-validation.json','synthetic-validation.json','synthetic-reports.json','local-checks.json','freeze.json','evaluation-proposal.json','launcher-binding.json','check-failure-assessment.json']}
assert len(old['requirements'])==89 and len(rows)==219
assert audit['additional_scope_dispositions']=={'passed':199,'unresolved':14,'proposed documented limitation awaiting decision':6},audit['additional_scope_dispositions']
for previous,current in zip(old['requirements']+old['additional_scope_requirements'],audit['requirements']+rows):assert previous==current or current.get('previous_row')==previous
save('audit.json',audit)
save('prior-row-preservation.json',{'retained_prior_rows':297,'total_rows':308,'prior_audit_sha256':sha(OLD/'audit.json'),'updated_rows':['V56-DELIVERY','V56-REVISION-DECISION'],'rows':{row['id']:hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest() for row in old['requirements']+old['additional_scope_requirements']}})
summary=f'''# Credential merge correction verified; exposed regression approval pending

**The approved joint source-only attempt passes engineering at `dc73715`. Equal credential markers now join consistently independently of cache interning; the canonical `UNKNOWN_VALUE` bypass is separately equivalent to a preserved correction-only reference. No current-source corpus observation has run. Phase 22 remains incomplete.**

The user's `continue` instruction followed the exact proposal and explanation of the problem. [Authorization](authorization.json) binds that instruction to prospective-contract proposal `12eea305c03328d6872587a051c090daf6f2d1bb83e1d0a622e3c3a92af92921`, delivered at `9b2585d`. This authorizes the specified correction and bypass, not historical failure acceptance, a new numerical measurement budget or Phase22 technical acceptance.

The product changes are confined to shared `path_flow.combine` and `CredentialFlow.merge`, with13additional persistent test cases and changelog documentation. The marker join accepts complete Value equality as well as object identity. Every unequal-marker, containment and HTTP-selection path remains unchanged. The bypass returns only the canonical unknown singleton with an empty requested key before tuple/cache dispatch; all other calls retain the existing4,096-entry LRU and `_combine` behavior. No new cache, dependency, rule suppression, resource change or analysis truncation is introduced.

[Source assessment](source-recovery-assessment.json) retains the deliberate semantic change. Across **4,050 structural correction cases**, **552 equal-marker records** differ from `a36f696`: formerly reset uncontained fields or stripped source-free safety metadata now retain the equal first marker. These exact changes are permitted by the prospective join contract, not silently excluded from an equivalence comparison. Another552derived credential-cache input tuples change accordingly; their guard facts and conditioned credential outputs agree. All other environment entries and pre-consumer flow fields agree. Uncontained markers do not establish absent-caller or operator-opt-in facts. Real-target reachability of the adversarial marker and broad detection impact remain unestablished.

The correction-only source was retained before adding the bypass. [Bypass validation](synthetic-validation.json) passes **2,430 complete Value/Python/TypeScript state comparisons**, including metadata, keys, guards, mixed identities, missing/null/undefined and varied arities, plus **two saturated-cache eviction cases**. No fields are excluded. One eligible dispatch control avoids tuple/cache entry; nine ineligible controls retain it. [Seven existing synthetic HTTP credential cases](synthetic-reports.json) preserve the entire ordered rule state: four detections and three negatives, with matches/captures, warnings, visits, exemptions and skip reason unchanged.

Both original singleton failures reproduce against their preserved original source. The broad bypass's direct interning change and canonical bypass's eviction change remain failed at their actual baselines. This prospective correction does not relabel those attempts as historical passes or accepted limitations. Canonical unknown frequency is unmeasured; neither observed sample shares nor synthetic avoided calls prove a speedup or300-second completion.

All **480 correction-stage tests** and **934 affected tests** passed. The full local suite and all12Linux/macOS/Windows×Python3.10–3.13 hosted suites pass **2,399 tests /36skips**. All29normal CI jobs pass in [34779741236](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34779741236); documentation passes in [34779741226](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34779741226). Local combined statement/branch coverage is **{local['coverage_totals']['percent_covered']:.2f}%**, branch-only **{local['coverage_totals']['percent_branches_covered']:.2f}%**. Hosted checkout `22ad9ab968d838677540932c83ff46b04e23e588` has the exact candidate tree. All four optional Phase22 corpus jobs are skipped. Normal CI's historical reproductions retain pinned scanner `8824014`; they are not current-source corpus measurements.

Whole-scope Ruff/format/strict mypy, lock/schema/notices/offline-artifact, dependency advisory, docs and package-member checks pass. Installed-wheel/platform/Docker/isolation evidence is retained from actual hosted artifacts. Six production requests regenerate and checked-replay with identical fingerprints/full request hashes and zero live model calls. The authorized scanner-owned Docker fixture completes20/20attempts with14findings and cleanup. All19Git runtime component hashes and its approved image remain unchanged; no Git campaign runs. Earlier file/worktree/evidence restoration and selective Docker cleanup remain retained.

The first bypass helper constructed self-referential synthetic record members and recursed in the unchanged correction-only reference for the failing case. Corrected only the fixture's leaf-member topology; the original helper/log remain. The first ordered-rule comparison helper lacked the repo import root and stopped before source analysis; its import correction and original receipt remain. Ruff/format initially rejected one90-character test line, then passed after test-only formatting. These verification defects do not hide a candidate semantic failure or introduce another optimization target. [Failure assessment](check-failure-assessment.json) retains each outcome.

The frozen scanner is `{proposal['scanner']['revision']}`, source SHA-256 `{proposal['scanner']['source_sha256']}` and harness `{proposal['scanner']['harness_sha256']}`. [The new regression proposal](evaluation-proposal.json), SHA-256 `{sha(OUT/'evaluation-proposal.json')}`, is **unapproved and unexecuted**: one serial local macOS sequence, **205 exposed native observations** across110unique input records with95complete ordered pairs. It comprises24original four-repository observations,94TypeScript and87Python compatibility observations. Fifteen Python development records run once; no new repeat, mutation, repository or comparator is added. Both languages remain affected, and no partial subset is pooled into a new whole25/45Linux result.

Bounds remain120-second target,300-second native/whole-input maximum,15-second cleanup, one1,150-minute outer/1,149-minute internal sequence, zero retry/profile/comparator/target execution/paid call. Reused evaluator and supervisor logic retain exact source/configuration/manifest/rubric binding and11volatile exclusions. Infrastructure, execution, timeout, identity/schema/cleanup or ordered-repeat failures close all unused observations. Detection/negative-support failures remain collected outcomes requiring source assessment. No launch token or output directory exists. All205are proposed, not approved remaining budget.

All three native timeouts remain separate: `17b4784` at300.002159seconds, `6e4fd67` at300.004111 and `a36f696` at300.000481; each had one incomplete and204unstarted closed. Partial profiles retain86,659/79,307/78,769samples at their actual sources. The invalid stale-root v50 attempt remains unusable and V49-DIAGNOSTIC-PREPARATION unresolved. Original four-repository fresh evaluation stays24completed/12equal pairs with all four gates failed at `2e0efb2`: FAF read unsupported, no-bash vulnerable hit plus two fixed/control false alerts per batch, Lightning actual client-get and Engram named manifest-write unresolved. Later corrections are exposed regressions, not clean unseen-source discrimination.

The [audit](audit.json) retains **all297prior requirements**, adding11for **308total:89original +219added**. Original rows remain84passed, two user-deferred, two proposed limitations and one human acceptance pending. Added rows have199passed, six historical closure proposals and14unresolved before supplemental delivery verification. Both singleton failure rows remain unresolved; the six older closure proposals are not accepted by this correction approval.

TS94 at `2e0efb2`, Python87 at `8c62567` and whole25development reuse plus45+45Linux at `1f3f72f` retain actual passes and the Meta operator erratum. Original memory-keeper false alerts, DDG's unsupported fixed send and wrong TypeScript label despite actual Python configuration, Lighthouse misses, and held-out10complete/10unsupported/five incomplete with zero hits among four completed vulnerable inputs out of ten vulnerable total remain unchanged. Same-agent curation/review is not independent human validation, training-data novelty, broad accuracy or runtime safety proof.

Git stays **312/1,040 incomplete**,728deferred; paid benchmark/pilots deferred, Phase21 incomplete and Phase24/15 unchanged. Historical two paid calls cost$0.071799; this continuation adds zero. Current-source regression results, explicit human technical acceptance and accepted closeout remain pending. No merge, ready-state change, release, outreach or Phase23 is authorized.
'''
for before,after in [('12Linux/macOS/Windows×Python3.10–3.13', '12 Linux/macOS/Windows × Python 3.10–3.13'), ('29normal', '29 normal'), ('13additional', '13 additional'), ('552derived', '552 derived'), ('14unresolved', '14 unresolved'), ('and14 unresolved', 'and 14 unresolved'), ('Python87', 'Python 87'), ('TS94', 'TS 94'), ('with13','with 13'),('existing4,096','existing 4,096'),('Another552','Another 552'),('or300','or 300'),('all12','all 12'),(' /36skips',' / 36 skips'),('All29','All 29'),('Phase22','Phase 22'),('completes20/20attempts with14findings','completes 20/20 attempts with 14 findings'),('All19Git','All 19 Git'),('one90-character','one 90-character'),('across110unique','across 110 unique'),('with95complete','with 95 complete'),('comprises24original','comprises 24 original'),(',94TypeScript',', 94 TypeScript'),('and87Python','and 87 Python'),('whole25/45Linux','whole 25/45 Linux'),('remain120-second','remain 120-second'),(',300-second',', 300-second'),(',15-second',', 15-second'),('one1,150-minute','one 1,150-minute'),('and11volatile','and 11 volatile'),('All205are','All 205 are'),('at300.','at 300.'),('seconds,',' seconds,'),('and204unstarted','and 204 unstarted'),('retain86,659/79,307/78,769samples','retain 86,659/79,307/78,769 samples'),('stays24completed/12equal','stays 24 completed / 12 equal'),('all297prior','all 297 prior'),('adding11for','adding 11 for'),('308total:89original +219added','308 total: 89 original + 219 added'),('remain84passed','remain 84 passed'),('have199passed','have 199 passed'),('and14unresolved','and 14 unresolved'),('whole25development','whole 25 development'),('plus45+45Linux','plus 45+45 Linux'),('held-out10complete/10unsupported/five','held-out 10 complete / 10 unsupported / five'),('**,728deferred','**, 728 deferred'),('Phase21','Phase 21'),('Phase24/15','Phase 24/15'),('cost$','cost $'),('Phase23','Phase 23')]:summary=summary.replace(before,after)
with (OUT/'summary.md').open('x') as stream:stream.write(summary)
url='https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase22/integration/artifacts/phase22/integration/v57-credential-merge/'
body=summary
for name in ['authorization.json','source-recovery-assessment.json','synthetic-validation.json','synthetic-reports.json','check-failure-assessment.json','evaluation-proposal.json','audit.json']:body=body.replace('('+name+')','('+url+name+')')
with (OUT/'pr-body.md').open('x') as stream:stream.write(body)
status=f'''## Current v57 joint correction: engineering passed, regression pending

The approved equal-marker credential correction and canonical unknown bypass
are verified at **`dc73715`**, source `{proposal['scanner']['source_sha256']}`.
Across4,050correction cases,552marker and552derived cache-input deltas retain
the explicitly revised join contract; guard results agree. The bypass then
passes2,430complete Python/TypeScript state comparisons and two saturated-cache
evictions against a preserved correction-only reference. Seven existing synthetic
HTTP patterns preserve entire ordered rule output: four detections, three negatives.
Both original singleton failures remain reproduced, closed and unaccepted.

Local and all12hosted suites pass **2,399 tests /36skips**; all29normal CI jobs
and docs pass in34779741236 /34779741226. Combined local coverage is
{local['coverage_totals']['percent_covered']:.2f}%, branch-only{local['coverage_totals']['percent_branches_covered']:.2f}%. Packages, strict quality checks, six identical zero-call
production requests and approved runtime bindings pass. Initial synthetic fixture,
import-root and test-format check failures retain their individual corrections.

`v57-credential-merge/evaluation-proposal.json` is **unapproved/unexecuted**:
205exposed observations on110inputs/95ordered pairs, comprising24four-source,
94TypeScript and87Python observations.120-second target,300-second whole/native
maximum,15-second cleanup,1,150-minute outer sequence; zero retries, profiles,
comparators, target execution or paid calls. No speedup or300-second completion
is established. All old timeouts, partial/invalid profiles and fresh failures
remain source-bound; no partial subsets become new whole Linux batches.

The audit retains **308requirements (89original +219added)**, including six
unaccepted historical closure proposals and both failed singleton rows.
**Phase 22 remains incomplete**, awaiting actual regression, explicit human
technical acceptance and accepted closeout. Git stays312/1,040incomplete;
paid benchmark/pilots deferred, Phase21incomplete and Phase24/15unchanged.
No merge, ready-state change, release, outreach or Phase23 is authorized.

'''
for before,after in [('Across4,050correction','Across 4,050 correction'),(',552marker and552derived',', 552 marker and 552 derived'),('passes2,430complete','passes 2,430 complete'),('all12hosted','all 12 hosted'),('/36skips','/ 36 skips'),('all29normal','all 29 normal'),('in34779741236 /34779741226','in 34779741236 / 34779741226'),('branch-only','branch-only '),('205exposed','205 exposed'),('on110inputs/95ordered','on 110 inputs / 95 ordered'),('comprising24four-source','comprising 24 four-source'),('94TypeScript and87Python observations.120-second','94 TypeScript and 87 Python observations. 120-second'),(',300-second',', 300-second'),(',15-second',', 15-second'),(',1,150-minute',', 1,150-minute'),('or300-second','or 300-second'),('308requirements (89original +219added)','308 requirements (89 original + 219 added)'),('stays312/1,040incomplete','stays 312/1,040 incomplete'),('Phase21incomplete','Phase 21 incomplete'),('Phase24/15unchanged','Phase 24/15 unchanged'),('Phase23','Phase 23')]:status=status.replace(before,after)
heading='## Current v56 canonical bypass: eviction failure retained'
docs=list(read(OLD/'documentation-binding.json')['owning_docs_sha256'])
for name in docs:
    path=ROOT/name;text=path.read_text();assert text.count(heading)==1,name
    path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
save('owning-docs.json',{'sha256':{name:sha(ROOT/name) for name in docs}})
save('optimization-budget-closed.json',{'approved_attempts':1,'consumed_attempts':1,'remaining_attempts':0,'closed':True,'scanner':proposal['scanner'],'local_and_hosted_engineering_passed':True,'new_corpus_observations':0,'profiles':0,'paid_calls':0,'qualification':'Approved joint source-only attempt complete. Separate205-observation proposal is unapproved; no older closed budget is reused and no historical failed gate is accepted.'})
print('Reconciled308requirements;199added passes, six closure proposals,14unresolved before delivery.205observations unapproved.')
