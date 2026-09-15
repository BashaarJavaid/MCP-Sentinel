"""Render current review docs after complete assessment; never infer acceptance."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,text):
 with path.open('x') as f:f.write(text)
a=read(OUT/'audit.json');four=read(BASE/'v73-corrected-four-results/final-assessment/assessment.json');lang=read(BASE/'v75-prior-language-results/final-assessment/assessment.json')
assert a['execution_gate_passed'] and a['current_four_repository_gate_passed'] and a['current_earlier_language_compatibility_established'] and not a['technical_acceptance_received']
count=len(a['requirements'])+len(a['additional_scope_requirements']);assert count==len(a['current_requirement_interpretations'])
status=f'''## Current v76 technical review: source gates passed, human acceptance pending

At engineering-tested **`cec0322`**, the separately approved **24 four-repository
observations and 181 prior-language observations are complete**, with **all 95
entire ordered pairs equal**, verified cleanup and both budgets closed. No-bash,
Lightning, Engram and FAF pass their narrow exposed conditions; TypeScript 94
and Python 87 preserve compatibility, including caller-specific DDG CGNAT support
and two retained nominal-fixed Meta operator errata. Calculator reports add two
source-assessed findings outside the original metadata condition. Fourteen qualified
Git repository-copy findings retain physical/identity uncertainty. Raw findings,
unresolved surfaces and original fresh failures remain visible.

**Normal FAF completion within 1,800 seconds remains unestablished.** Its six
approved uncapped observations took **2,297.758–2,735.386 seconds**; the ordinary
1,800-second policy remains unchanged. The 181 language observations used normal
1,800-second input / 10-second Semgrep limits, 15-second cleanup and the existing
four-worker maximum. No speedup, isolated benchmark or broader runtime safety is
claimed. The V68 performance proposal remains unapproved and unimplemented.

Unchanged `cec0322` engineering retains **2,450 tests / 36 skips** locally and in
all 12 hosted suites, **29 normal CI jobs and docs**, combined coverage **90.11%**,
branch-only **85.97%**, six zero-call production request replays and 19 approved
runtime component bindings. This continuation adds static assessment and affected
documentation/package checks, not a new hosted code pass. All **{count} requirements
(89 original + {count-89} added)** retain their previous states and exact evidence.
Historical failures and practical limits are proposed for explicit acceptance.

**Phase 22 remains incomplete** until explicit human technical acceptance of the
review packet and subsequent verified accepted-closeout delivery. The packet is
`artifacts/phase22/integration/v76-technical-acceptance/`; its summary, complete audit
and acceptance proposal enumerate every proposed limitation. Git stays **312/1,040
incomplete, 728 deferred**; the 396-request paid benchmark and pilots are deferred,
Phase 21 is incomplete, and Phase 24/15 are unchanged. Historical paid spend stays
**$0.071799; zero new paid calls**. No merge, ready-state change, release, outreach
or Phase 23 is authorized.

'''
docs=read(BASE/'v72-prototype-property-correction/documentation-binding.json')['owning_docs_sha256'];assert len(docs)==16
heading='## Current v72 correctness recovery: engineering passed, regression pending'
for name in docs:
 path=ROOT/name;text=path.read_text();assert text.count(heading)==1,name
 path.write_text(text.replace(heading,status+heading.replace('Current','Historical',1),1))
put(OUT/'status.md',status)
put(OUT/'owning-docs.json',json.dumps({'sha256':{n:sha(ROOT/n) for n in docs}},indent=2)+'\n')
limits=(BASE/'v73-corrected-four-results/acceptance-limits-preparation.md').read_text()
limits=limits.replace('# Acceptance decisions to carry into the final packet','# Proposed Phase 22 technical acceptance limitations').replace('**Preparation only. No technical acceptance or limitation waiver has been received.**','**Proposed for explicit human acceptance. No technical acceptance or limitation waiver has been received.**')
limits=limits.replace('This document specifies the decisions to present after current-source compatibility and final\npacket delivery; it does not change any audit disposition or close the phase.','Current-source compatibility is now complete; this document specifies the decisions for the final\nreview packet. Proposed audit dispositions do not close the phase or retroactively pass failures.')
limits=limits.replace('the V75 result must supply current-source proof','V75 now supplies current-source proof').replace('current-source compatibility remains separately measured','V75 separately supplies current-source compatibility').replace('Compatibility is currently running, so these decisions are not yet ready.','V75 is complete: 181/181 observations, 83 entire ordered pairs; 76 vulnerable conditions detected, 103 valid negatives without matching alerts, 2 Meta operator errata retained with 2 matches each.')
limits=limits.replace('The companion `acceptance-requirement-preparation.json` binds every outstanding row by hash.','The prior preparation binds every outstanding row by hash; the complete current audit preserves all 407 previous rows and adds continuation requirements.')
limits=limits.replace('New V73/V74/V75 preparation, approval, execution, assessment, helper corrections,\nengineering reuse and delivery rows must be added to the final audit with exact evidence.','New V73/V74/V75 preparation, approval, execution, assessment, helper corrections,\nengineering reuse and delivery rows are included in the current audit with exact evidence.')
limits=limits.replace('V72-DELIVERY can be resolved from its actual supplemental', 'V72-DELIVERY is resolved from its actual supplemental').replace('sealed previous row.', 'sealed previous row.')
limits += '\nExplicit R66/R88 support-history disposition: DDG first-frozen `f85a90f` completed ten native observations/five pairs and passed its prospective fresh detection/output-discrimination rubric, while actual fixed `build_request`/`send` support remained absent. V35 at `a50e9b7` completed 87 observations/36 pairs with actual send support, but zero of six DDG negative send qualifications and the three Meta image fixed/control conditions passed qualification. Those support/qualification failures remain historical; V38 and current V75 exposed passes do not retroactively change them. The ten-observation DDG first-frozen pass is not relabeled a failed detection result.\n'
put(OUT/'acceptance-limits.md',limits)
summary=f'''# Phase 22 technical acceptance review

**Current source gates pass; explicit human technical acceptance and subsequent accepted-closeout delivery remain pending.**

Measured scanner: `cec0322e904bbf63c33cd95796e7289101a93e5d`, source SHA-256
`8c8aeb9937930315b0c2ba38685d3e5ac71275cc05946cbae3c790697bdf4099`.
Harness `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add`;
lock `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b`.
The eventual docs/evidence delivery revision is recorded separately by delivery-verification.json.

| Approved run | Actual outcome | Policy |
| --- | --- | --- |
| V73 corrected four-repository | 24/24 complete, 12/12 entire ordered pairs; all 4 narrow gates pass | Experiment-only uncapped input/sequence, Semgrep 0; cleanup 15; existing 4 workers |
| V75 prior-language compatibility | 181/181 complete, 83/83 entire ordered pairs; 94 TypeScript + 87 Python | Normal 1,800-second input, Semgrep 10, cleanup 15; existing 4 workers; 5,555-minute worst-case cap |

Both budgets are closed with zero remaining. No retries, profiles, comparator executions,
target execution, source tuning, resource changes or paid calls occurred. The numerical
approvals are distinct from technical acceptance. The 205 current observations cover 110 input records;
they are separately bound exposed schedules, not a new whole 25/45 Linux campaign or fresh-source test.

V73 source assessment covers 794 findings, 87,808 diagnostic occurrences, 282 surfaces and 6,781 contexts,
plus 48 complete ordered comparisons against original `2e0efb2` and preceding `4145d35` reports. V75 covers
{lang['finding_occurrences']:,} findings, {lang['diagnostic_occurrences']:,} diagnostic occurrences,
{lang['surface_occurrences']:,} surfaces and {lang['changed_occurrences']:,} changed occurrences across
{lang['source_contexts']:,} changed source contexts. Every changed occurrence is assessed; unchanged
source judgments are reused only after exact source/report/delta checks. All raw outputs remain.

No-bash retains lexical directory discrimination with physical containment uncertainty.
Lightning retains only the source-proved initial literal IPv4 guard through stable slash/suffix
URL derivation. Engram retains the initial resolved-home guard with reconstructed-use/physical
uncertainty. FAF follows actual registered faf_read dispatch through the constructor parameter
property to the read: vulnerable detected; fixed/control root confinement supported under the
frozen prerequisites. Its two unnamed unresolved surfaces stay unresolved. No DNS, redirect,
rebinding, complete IPv6, physical-race, independent-review or target-runtime claim follows.

FAF's six V73 inputs took 2,297.758–2,735.386 seconds (38m18s–45m35s), all exceeding the ordinary
1,800-second policy. These are uncapped shared-host observations, not isolated performance
measurements. Ordinary FAF completion remains unestablished and requires explicit practical
acceptance. The V68 literal-serialization proposal remains unopened, unimplemented and unapproved.

V75 retains 76 vulnerable detections and 103 valid negatives without matching condition alerts.
Two nominal-fixed Meta operator inputs retain their original erratum, with 2 matched keys each.
Calculator reports add command execution and file-read candidates outside the metadata condition;
they remain needs_review and do not change the original metadata labels. Fourteen Git repository-copy
candidates acknowledge initial containment while retaining original-path physical/identity uncertainty;
these remain unmatched to the frozen Git conditions and are not independently confirmed. DDG negatives retain the
exact web_fetch route-specific CGNAT qualification at client.send; broader routes and destinations
remain unestablished. Full source details are linked below.

Engineering remains the actual `cec0322` local/full/hosted result: 2,450 passed / 36 skipped locally and in
all 12 hosted suites, 29 normal jobs and docs 34846514312/34846514328, 90.11% combined / 85.97% branch coverage.
The 303 engineering input bindings, 6 actual zero-call production requests and 19 runtime components
remain compatible. No new hosted code pass is claimed. Affected final documentation, generated
artifact and README-aware package checks accompany this review.

[Complete {count}-row audit](audit.json), [explicit proposed limitations](acceptance-limits.md),
[acceptance proposal](acceptance-proposal.json), [V73 complete assessment](../v73-corrected-four-results/final-assessment/assessment.json),
[V75 complete assessment](../v75-prior-language-results/final-assessment/assessment.json),
[final checks](final-checks.json) and [command/failure provenance](command-provenance.json).
The seal and exact existing-draft readback are bound in documentation-binding.json and the
supplemental delivery-verification.json. Review the proposal only after verified delivery.

All 407 previous requirements, original held-out/fresh failures, DDG first-frozen unsupported fixed sends and V35
qualification failures, seven native timeouts, six valid
partial profiles, invalid stale-root preparation, singleton/strict-equivalence failures and six
unaccepted historical closures remain source-bound. Later passes do not retroactively erase them.
Git remains 312/1,040 incomplete with 728 deferred; the 396-request paid benchmark and pilots remain deferred
and nonblocking under the revised scope. Historical paid spend is $0.071799; zero added. Phase 21 is incomplete,
Phase 24/15 are unchanged. No merge, ready-state change, release, outreach, launch or Phase 23 is authorized.
'''
put(OUT/'summary.md',summary)
print('Rendered16owning review sections and complete source/limitation summary; acceptance remains pending.')
