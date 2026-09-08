# Phase 22 implementation status

**The requested full technical plan is not complete.** This record distinguishes
verified increments from remaining implementation and acceptance work. Phase 21
recruitment remains deferred, and the external pilot gate remains unmet. The
[approved contract](phase22-technical.md) continues to govern scope.

## Active delivery workflow

The user approved one integration branch with batched PR/CI delivery on
September 7, 2026. Continue in `phase22/integration`, currently checked out at
`/private/tmp/mcp-phase22-options`. Existing draft PRs remain checkpoints;
do not maintain the old branch stack for each subsequent change.

The integration branch incorporates the unfinished SENT-014 checkpoint and the
preserved report/review draft, including delivered parents through PR #36.
The original two TypeScript argument-identity failures are fixed in `37f2190`.
Nested Python registration/mutable command flow, shared caller evidence, and
conditional-value corrections are committed through `355f0f7`. A full milestone
suite at `192296d` passed **891 tests, 36 skipped, 86.84% branch coverage**; this
is not final-candidate evidence for later source changes.

Subsequent work adds line-preserving multiline credential redaction (`da52eb3`),
SENT-015 caller URL/destination flow (`d3fcf79`), fixed JSON argument positions
(`dbb2464`) and fixed public URL prefixes (`536bb69`). The review/context/proof
suite passed 71 tests with loopback permission; the first SSRF affected suite
passed 201 tests. The dbt five-input measurement at `355f0f7` completed with two
vulnerable selector hits and zero fixed/control selector alerts. Its 13 unrelated
candidates are separately classified in `artifacts/phase22/integration/dbt-adjudication.json`.
Five codegen candidates were false positives; their correction is in `dbb2464`.
Eight other candidates remain uncertain after implementation-agent source review.
These correlated development inputs do not establish held-out accuracy.

The first Meta SSRF pair was incomplete because of multiline redaction. After
correction both scans complete: three image-request candidates in the vulnerable
snapshot and none at those sinks in the fixed snapshot. Unrelated candidates
remain separate. The subsequent ten-input development run at `536bb69` completes both five-input
families: each has two vulnerable condition hits and zero fixed/control condition
alerts. Five dbt codegen false positives are removed; the Meta reports retain 240
unrelated candidate instances needing adjudication. All historical conditions, campaigns,
the complete report migration and final hosted verification remain open. Source,
commands, failures and logs are retained in `artifacts/phase22/integration/`.

Use focused checks while coding, full checks at substantial integration
milestones, and the complete final benchmark/OS matrix before acceptance. Retain
raw evidence now and package it in batches. Existing workflow YAML is unchanged.

## Delivered draft stack

| Increment | Source / delivery | Verification and limits |
| --- | --- | --- |
| Execution and Python containment | PRs #22 and #23, unchanged | All 30 applicable checks pass on each. Preserve PR #23's narrower four vulnerable Git inputs and four fixed partners; no expanded accuracy claim. |
| TypeScript coordinate correction | `3fc7ce3`, PR #24 | 743 tests, 86.73% branch coverage; all 30 applicable checks pass, including Windows 3.10–3.13. LF/CRLF and UTF-8 regressions cover imported handlers and finding/registration locations. |
| Workspace correction and delivery | `756b57e` source, `9098975` evidence, PR #33 | 758 tests, 86.69% coverage. Two 45/45 rules-only runs have identical stable findings/coverage. All 30 applicable hosted checks pass. |
| Bounded shared containment | `cee0283` source, PR #34 | 776 tests, 86.86% coverage; 71 focused regressions. Two 45/45 runs agree and have no changed findings relative to workspace source. Constructor correction `e67365a` passes 780 full-suite tests and 75 focused tests; all 30 applicable hosted checks pass on `6ec5201`. |
| Filesystem condition follow-up | `276722a` source, successor to PR #34 | 798 tests, 86.88% coverage; 102 focused tests. Four-input subset: 2/2 vulnerable hits, 0/2 fixed condition alerts; eight unrelated candidates separately reviewed. Full Phase 22 gates remain pending. |
| Preserved report/review draft | `229d50e` checkpoint, `phase22/report-campaign` | Original 18 modified/untracked files were archived and committed before updating parents. The branch includes parent corrections but remains an unaccepted draft. |
| Description poisoning | `fe40322` source, successor to PR #35 | 823 tests, 86.74% coverage. Five approved development inputs complete: 2/2 vulnerable condition hits and 0/3 fixed/safe condition alerts. All 26 unrelated candidate instances separately reviewed. |

PRs remain drafts. No PR merge, release, site publication, outreach or paid model
calls occurred. Exact commands, exits, source and harness digests, logs and failed
runs are retained in the linked increment records:
[TypeScript](phase22-typescript-containment.md), [workspaces](phase22-workspaces.md),
and [shared containment](phase22-shared-containment.md), plus
[description poisoning](phase22-description-poisoning.md).

The integration now also includes returned-error URL validation (`86ac2dd`),
initial direct HTTP credential-fallback detection (`6d9bee9`), shared Python
member state (`e2b0346`), HTTP URL entry points (`e1b23b8`), and source-bound record
callbacks (`d259126`). Focused regression sets pass, including custom-constructor,
replaced-guard and unrelated/replaced-value controls. These changes do not yet
establish the approved Atlassian middleware/service-factory conditions, complete
TypeScript support for new rules, or final condition-level acceptance. The second full
milestone at `d259126` passed **1010 tests, 36 skipped, 87.38% branch coverage**.
An exposed Atlassian profiling run hit the unchanged 120-second static deadline.
Its repeated discovery traversals motivated `aaa759a`; 195 affected regressions
and whole-project mypy/Ruff/format checks pass after that correction. This is not
the final historical measurement or a claim that Atlassian conditions pass. The repeated
profile at `aaa759a` completes within the static deadline but has no SENT-016
condition hit. SDK HTTP caller tracking (`de1af5a`) subsequently passes 201 affected
regressions, including stdio and local SDK-impersonation controls; SENT-016 CLI
selection/suppression/baseline/severity checks also pass. These do not yet establish
Atlassian or Meta operator-fallback acceptance. The integration evidence is retained
losslessly in `artifacts/phase22/integration/evidence-v1.json`, `evidence-v2.json`
and `evidence-v3.json` and their checksummed archives.

## Requirement map

| Requested work | Current implementation / evidence | Remaining work |
| --- | --- | --- |
| Preserve unfinished work and repair the existing stack | Checkpoint `229d50e`; `artifacts/phase22/typescript-correction/verification.json`; PRs #22–#24 checks | Keep the report/review draft at the proper delivery point. |
| Strict JSON diagnostic and four loopback tests | `workspaces.py`; `corrected-pytest.log`; four focused loopback tests pass with socket permission | No parser weakening. Earlier five failures remain in `workspaces/pytest.log`. |
| Reproducible workspace repeat | `workspaces/verification.json`, `reproducibility.json`, checksummed `measurements.tar.gz` | The older 41-input repeat remains incomplete and preserved. Final integrated measurements must use the eventual complete implementation. |
| Imported handlers/schemas, aliases, re-exports and methods | `discovery.py`, `typescript_discovery.py`, `typescript_modules.py`; discovery/module regressions | Complete all required SDK forms and feed all relevant detectors through the shared support. Inventory recognition is not detector support. |
| Cross-file caller/guard/sink relationships | `path_flow.py`, `typescript_path_flow.py`, SENT-012 tests | Complete approved Atlassian service factories/uploads, filesystem collection/symlink branches, Mastra security-failure flags and fallback, and all condition-level adjudications. |
| SDK-injected context and bounded factories | PR #34 regressions cover imported Context, rebinding, simple local factory objects, inherited/replaced methods and annotation-only controls | Arbitrary factories, reflection, custom construction and dynamic instance state are not established by these tests. |
| All ten exposed benchmark families | Existing SENT-012 increments plus retained Phase 20 inputs | Condition-correct detection of all 20 vulnerable inputs and clean fixed/control behavior is not established. Remaining Git option, filesystem, Atlassian, Excel, mobile and Kubernetes conditions need implementation/adjudication. |
| SENT-013/014/015/016 and Kubernetes SENT-002 | SENT-013 delivered; SENT-014 nested command flows and SENT-015 request flows now have local controls and development measurements | Complete SENT-014/015/016 and Kubernetes, remaining detector support and final rule acceptance. SENT-013 holdout and reviewed retention remain pending. |
| uv/npm/pnpm membership, local exports, aliases and inherited compiler settings | Workspace/module tests; aggregate root and individual-package configuration checks | Complete structured member coverage, unsupported/inaccessible counts, all negative compatibility cases and detector integration. Dynamic scans still select one Python package. |
| Candidate-bound 160-line review context | Integrated draft carries merged flow locations and context blocks; multiline redaction/context/proof regressions pass | Complete deduplication, omission/redaction/boundary/reference checks, request/cache compatibility and runtime-proof preservation. Prepare replacements only for changed requests. |
| Bounded ordered campaigns | Existing runtime pipeline remains rule-keyed | Implement ordered attempts, stable IDs, round-robin fairness, 24-attempt/120-second budgets, settings precedence, fresh baseline/attack containers, schema drift, interruption/cleanup and explicit unstarted remainder. |
| Native 1.7.0 and consumers | Report/migration draft incorporated into integration; native 1.7 is not yet verified | Complete attempt/discovery/outcome references and invariants, legacy 1.3–1.6 migrations, workspace consistency, Finding/report schemas, console/JSON/SARIF and owning documentation. |
| Independent evidence and held-out evaluation | Existing corpus authorization and Git environment preserved unchanged | Finish development-condition measurements before evaluating fresh holdout source. Held-out performance has not been measured here. |
| Unrelated findings and competitor measurement | `shared-containment/finding-delta.json` compares 45 inputs; unchanged historical backlog remains unadjudicated | Adjudicate any later new/changed unrelated findings. Rerun the pinned comparable Semgrep measurements; Snyk/Cisco performance remains unmeasured. |
| Git runtime and paid reviewed comparison | Authorized `mcp==1.29.0` environment and earlier startup/discovery proof retained | Integrate campaign evidence; after offline gates pass, prepare exact paid requests/model/capture reuse/token/dollar ceilings and obtain approval. Reviewed completion/retention for all 45 inputs remains pending. |
| Final quality and technical acceptance packet | Increment-level Ruff, format, mypy, schemas, pytest, audit, notices, docs and CI evidence retained | Run all required checks and final repeated measurements on the complete integrated implementation; collect campaign/wheel/Action/isolation/OS evidence and requirement-level technical acceptance. |
| External acceptance | No external maintainer outcomes added | Five external workflows and ranked blockers remain required; technical checks cannot complete Phase 22's pilot-dependent gate. |

## Evidence handling

The workspace packet retains all four measurements, including the earlier
incomplete repeat, in a lossless archive with per-file SHA-256 hashes. Archive
contents were checked byte-for-byte after creation. Expanded reports remain
available in the working checkout; the documentation includes the extraction
command for a fresh checkout.

Local measurements overlapped test and documentation work, so their wall times
are verification latency rather than isolated throughput comparisons. No code
coverage percentage is presented as detection accuracy, and no approval packet
for paid evaluation is claimed ready while offline condition gates remain unmet.
