# Consolidated Phase 22 requirement checklist

**Current scanner: `62987a6`; workflow delivery: `88a559e`. Phase 22 remains
incomplete pending execution reliability and final human technical acceptance.** The user approved both the revised Linux execution and exact
fresh-corpus checkpoint with “go ahead with these two”. Their separate decision
records preserve the exact proposal/manifest hashes and stopping conditions.

Linux development fails its gate: 17/25 inputs complete and eight time out;
maximum end-to-end time is 120.043s. Eight of ten vulnerable inputs complete and
are detected. Nine of thirteen valid negatives complete with zero matching alerts.
Both raw Meta erratum inputs are incomplete, so the raw negative denominator is
nine completed out of fifteen. Both historical batches are skipped after this failure.

The Linux run is 34421737148. No retry, pooling or deadline waiver occurred.
Earlier local historical 43/45 and development 24/25 failures remain preserved.
Seven Linux timeouts are new versus that local development run; one persists.
All 17 completed Linux reports match the prior entire ordered reports except
documented volatile fields. The next bounded Meta performance proposal is
prepared in `v8-next-performance-proposal.json` and remains unapproved.
The approved Meta erratum remains separate from raw scores and execution status.

The fresh fetch-mcp evaluation completes all five inputs twice natively and once
with Semgrep 1.176.0. Both tiers miss both correlated vulnerable variants and
have zero condition-matched alerts on the three fixed/safe inputs. Native reports
match in full except documented volatile fields; maximum wall times are 5.771s
and 5.075s (Semgrep: 16.374s). Native dispatch/schema/class flows remain unresolved.
All 50 unrelated Semgrep JQuery alerts have source-bound false-positive
assessments. No detector tuning or fresh accuracy threshold is introduced;
curation exposure remains disclosed.

The exposed open-webSearch regression remains 2/2 detections in both final runs,
with zero matching negative alerts. Its original 0/2 results are unchanged.
Original held-out evidence remains 10 completed/10 unsupported/5 incomplete,
with zero detections among four completed vulnerable variants. The original
historical 70-warning unadjudicated backlog remains distinct from source-assessed
exposed-regression warnings. Native full-report comparisons and all new finding/
coverage assessments are retained in the v8 evidence.

All 29 normal CI jobs pass at workflow delivery `88a559e`, with the optional benchmark job skipped in ordinary CI; documentation also passes. The 12 quality suites each report 2,121 passed and 36 skipped, with 89.63–89.65% branch coverage. Complete logs/artifacts and source-verified distributions are retained.

The full paid benchmark and external pilots remain explicitly user-deferred,
not passed. No additional paid model calls or target execution occurred in these
two evaluations. Compatible capture/Docker/Git evidence remains bound to the
unchanged scanner. Final human acceptance is separate; Phase 21, Phase 24 and
Phase 15 gates remain unchanged. No merge, release, outreach or next phase.

Current dispositions are in `v8-closeout-audit/packet.json`; the table below maps all 86 rows.

## Historical checkpoint summaries

Current follow-up source is `68bdf83`: supported legacy TypeScript registrations,
object methods, captured service identities and receiver binding are corrected.
The 933-test shared selection passes. All five exposed replacements complete twice
with stable findings, still missing both vulnerable conditions. A fresh five-case
proposal is prepared in `../corpus-replacement-v2/`; it requires explicit freeze
approval before evaluation. All 29 hosted jobs pass at `68bdf83`, including 12 suites with 2,057 passed / 36 skipped.
Historical batches complete 44/45, 45/45 and 41/45. All 45 inputs have two matching
completed observations under 120 seconds, but the two-complete-batch gate remains
failed. The casewise alternative and residual-SSRF disposition are proposed, not
approved, in `../completion-scope-v1/follow-up-proposal.json`. All 25 original development inputs complete with unchanged findings and the
approved Meta erratum. Original held-out results retain 10 completed, 10
unsupported and 5 incomplete inputs. The 396 paid calls and external pilots
remain user-deferred/nonblocking, without being counted as passed. No additional
paid call occurred. The previous 86-row audit at ee9721f remains historical evidence;
final technical acceptance and the residual SSRF limitation remain open.

Source at start: `68fa702`, clean `phase22/integration` worktree.
Authorization: `../authorization.json`; frozen corpus and Git environment approved.
No paid calls, merge, publication or outreach authorized. Preserve historical evidence.

A box denotes a completed, evidenced gate, not intention. Command records and raw
logs live beside this checklist. Final requirement mapping must add implementation
commits, durable tests, identities, outcomes, failures and limitations to each row.

- [x] Verify integration worktree, branch, handoff and applicable instructions.
- [ ] Shared discovery: imported handlers/schemas, aliases/re-exports, bound helpers,
  factories/methods, caller/guard/sink flows, SDK context and low-level dispatch.
- [ ] Containment: Atlassian upload/factories, Excel, mobile, filesystem and Mastra;
  traversal/absolute/prefix/symlink/unrelated/discarded/replaced-value controls.
- [ ] Workspaces: uv/npm/pnpm membership/exclusions, exports/aliases/inheritance,
  aggregate/member configuration, explicit unresolved members, consistent coverage,
  escapes/symlinks, dynamic single-package selection and Helm/strict YAML behavior.
- [ ] SENT-012 through SENT-016 and Kubernetes SENT-002: all required conditions,
  language controls, default/selection/suppression/baseline/severity/provenance,
  remediation/OWASP/limitations and rule acceptance checklists.
- [x] Original SENT-014 unrelated/replaced TypeScript guard failures reproduced
  and fixed in `37f2190`; durable tests preserved.
- [ ] Complete SENT-014 command semantics, helper mutations and final independent
  condition gates; dbt development support and local controls are implemented.
- [ ] Candidate-bound review: 160 total unique source lines, exact blocks,
  omissions/redaction/boundaries/references, compatible cache/capture identities,
  nullable reviews and runtime proof preservation, no independent discovery.
- [ ] Campaigns: ordered attempts/IDs, complete enumeration/fair rounds/priorities,
  started/time budgets including discovery, configuration precedence/Action,
  fresh baselines/attacks, invalid baseline/drift/failures/interruption/cleanup,
  explicit unsupported/inconclusive/unstarted records and exit 3 on remainder.
- [ ] Native 1.7 and all consumers: references/unique IDs/count invariants,
  structured workspace validation, honest legacy 1.3–1.6 migrations, all proof,
  console/JSON/SARIF, generated schemas and owning/public documentation.
- [ ] Final historical offline measurements: 45 inputs twice, deadline 120s,
  20 vulnerable condition hits and no fixed/control condition alerts; denominators,
  differences, unchanged 70-warning backlog and changed-finding adjudication.
- [ ] Separate frozen Phase 22 development/mutations/controls and fresh holdout;
  retain split and exposure policy; comparable pinned Semgrep measurement.
- [ ] Authorized Git mcp==1.29.0 environment: reproducible image/dependencies,
  Docker startup/discovery/campaign evidence and honest runtime exclusions.
- [ ] Full quality: Ruff/format/mypy/lock/schemas/native/SARIF/pytest>=80% branch,
  audit/notices/generated artifacts/docs/build/wheel/Docker/Action/isolation,
  fixtures and historical migrations; hosted supported OS/Python matrix.
- [ ] Exact paid approval packet after offline gates: actual model/settings,
  cases/requests/purpose/compatible reuse/replacements/token/dollar ceilings,
  identities/stopping/retry policy. Paid reviewed evaluation awaits approval.
- [ ] Reviewed comparison after approval: identical inputs, 45/45 completion,
  retention/needs_review/abstentions/suppressions/holdout/latency/tokens/cost/reuse.
- [ ] Lossless hashed acceptance evidence, reproduction, complete requirement map,
  batched status/roadmap updates and consolidated draft with delivered parent.
- [ ] Human technical acceptance (external decision; not implementation).
- [ ] Pilot-dependent acceptance (five external workflows/ranked blockers; deferred).

## Requirement-to-evidence audit (continuation; no overall acceptance claim)

The current historical gate passes at `6e6833198989e06bd8c369abab0ee1a9d3db1ef8`: 45/45 inputs complete twice, and all stable reports are also identical to dcb965f. `v2-historical-gate-6e68331/packet.json` binds the existing condition and per-instance unrelated assessments by exact report hashes. The latest completed full-suite pass remains dcb965f. The 6e68331 full suite finished with 2021 passed, two failed, 36 skipped and 89.49% branch coverage. A stale cost expectation is corrected in d7184d3 with both targeted tests passing; the unchanged TypeScript smoke capture dependency remains. The raw suite is still failed.

`v2-requirement-execution-map-6e68331/packet.json` maps all 86 rows below to
exact source/test hashes and actual JUnit executions. It preserves this owner's
historical status text and records the separate d7184d3 correction; test-file
passes do not automatically establish a requirement's condition, runtime,
reviewed, hosted or human acceptance gate. Later evidence supplements the
source-specific records below without erasing failures.
`v2-historical-gate-dcb965f/packet.json` binds 45/45 completed twice,
identical stable reports, 20/20 exposed vulnerable conditions and zero named
fixed/safe alerts. `v2-full-suite-dcb965f` passes 2007 tests with 36 Docker
skips and 89.47% branch coverage at that immutable checkout. Current-source Docker, installed-package, original corpus repeats, paid and hosted
gates remain separate. All three pinned comparator scopes are measured and their
unchanged harness/corpus bindings to 6e68331 pass. `v2-source-audit-bindings-dcb965f/packet.json` binds all three
retained compatibility/workspace/consumer audits to current source hashes and
explicit delta reviews; it is source evidence, not runtime execution.

Historical audit through `029f686`: `be6349d`/`ab0e13c` and `d5e02e9` each pass
941 affected regressions; `b3b2318` verifies crowded 160-line context selection.
The 79-test native/campaign/baseline audit supports R45–R60 without replacing their
final Docker/consumer gates. `b55a087` adds offline preparation, checked replay and
comparator treatment support for R44/R65–R68; capture uses separate Phase 22 evidence
and remains paid-approval gated. At that historical checkpoint, the d5e02e9 all-rule Meta run completed 0/5;
the later dcb965f development measurement completes all five Meta inputs. The later approved Meta erratum preserves these original labels and scores; current interpretation is recorded separately.
Commands, failures and precise limits are retained in progress and batch 18.

Scope remains the full continuation request. Each row below is required. The
current local dispositions are bound to exact command, source, test and report
hashes in `v2-local-acceptance-index-d7184d3/packet.json`; its copied earlier row
text preserves historical status. The independent local checks are finished,
except the explicitly capture-dependent full-suite/demo checks. Draft PR #37 is delivered and all hosted jobs have completed;
`v2-final-technical-disposition-1e7c16a/packet.json` binds their actual outcomes.
All 12 full quality suites fail only the missing TypeScript capture; all 12 wheel
jobs pass. The demo is separately capture-dependent. No additional platform
regression was found. Named tests do not establish
independent detection accuracy or human acceptance.
Earlier sources and archives remain authoritative for their narrower claims.
The continuation starts at `83c9985` plus tracked patch
`9f533e8eb643e68a9cc5db0217b3db20a2d120d8789987635584037387cb86d6`.

## Current 86-row closeout audit at `62987a6`

The [source-bound audit](v8-closeout-audit/packet.json) records **78 passed, 2 user-deferred and 6 unresolved** requirements. Every row retains exact source/test bindings and hashed evidence references. Unresolved rows: R20, R35, R63, R64, R65, R84. Earlier audit/checklist statements remain historical.

| ID | Required behavior / evidence | Implementation and regression owners | Evidence / outstanding gate |
| --- | --- | --- | --- |
| R01 | Correct dirty worktree and packet identities | `phase22/integration`, authorization packets | passed — Integration branch, delivered parent, preserved worktrees/history and source identities verified; no reset or cleanup. |
| R02 | Source-established constructors, fields, aliases and replacement invalidation | `discovery.py`, `path_flow.py`, `test_python_state_flow.py`, `test_ssrf.py` | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R03 | Read-only builtin dictionary inspection with shadowing controls | Shared `PathFlow.call` | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R04 | Reflection, unknown mutation, custom hooks and constructor/decorator ambiguity | Same shared flow and containment controls | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R05 | Imported handlers and schemas | `discovery.py`, TypeScript discovery, registration flow | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R06 | Aliases/re-exports, local imports and package exports | Shared module resolvers | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R07 | Statically bound helpers, factories, inherited/bound methods | Shared discovery/path/registration flow | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R08 | Cross-file caller/guard/sink evidence and binding identity | Shared Python/TypeScript flows | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R09 | Genuine SDK context vs caller/fake/rebound/local SDK | Shared discovery/context source checks | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R10 | Low-level registration and dispatch | Shared discovery/registration | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. Fresh fetch-mcp dispatch/schema/private-static-class flows remain explicitly unresolved; supported-contract tests do not imply universal dispatch coverage. |
| R11 | uv/npm/pnpm members and exclusions | `workspaces.py`, `test_workspaces.py` | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R12 | TS aliases/inherited local compiler configuration, inaccessible parents | TypeScript module resolver | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R13 | Aggregate root vs individual config, nested config disclosure | Config/traversal/workspace inventory | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R14 | Per-member counts without shared-file duplication | Static coverage and native report models | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R15 | Inaccessible/unsupported members, ambiguity/import/reflection/schema gaps | Workspace/discovery diagnostics | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R16 | Repository escapes and symlinks; dynamic single Python package | Config/traversal/workspace tests | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R17 | Helm original bytes/text secrets and explicit YAML omission | Traversal/config tests | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R18 | Historical atlassian-auth condition | SENT-016 and shared lifecycle/middleware/client flows | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R19 | Historical atlassian-ssrf condition | SENT-015, shared URL flow and enforced returned errors | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R20 | Historical atlassian-upload condition | SENT-012, service factories | unresolved — The user-approved Linux execution retained the unchanged full-batch completion/timing/condition gates. Historical pair does not pass; skipped batches and every measured outcome remain explicit, with no retry or pooling. |
| R21 | Historical excel-boundary condition | SENT-012 | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R22 | Historical filesystem-prefix condition | SENT-012, TS normalization/component/physical-parent flow | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R23 | Historical git-arguments condition | SENT-014 | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R24 | Historical git-repository condition | SENT-012 | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R25 | Historical git-staging condition | SENT-012 | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R26 | Historical kubernetes-shell condition under unchanged SENT-002 meaning | `5065f16`, `typescript_execution.py`, `test_command_execution.py` | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R27 | Historical mobile-output condition | SENT-012 | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R28 | Mastra failure-return flags and unsafe directory fallback | SENT-012, TS shared flow | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R29 | Explicit description override, exfiltration, cross-tool redirection | SENT-013, description/discovery | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R30 | Benign instructions and quoted warnings; parameter/low-level metadata | SENT-013 | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R31 | dbt selector options through nested factories/mutable argv | SENT-014 | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R32 | Git option positions, rejection, command-specific terminators, object APIs | SENT-014 Python/TS controls | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R33 | Meta image caller URL request and scheme/private/loopback checks | SENT-015 | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R34 | Fixed public authority plus caller suffix; enforced actual return value | SENT-015/shared flow | passed — Final original development results and unchanged findings verified; source-bound diagnostic changes retained. Raw Meta scores and the approved erratum remain separate. |
| R35 | Meta ContextVar/HTTP authentication/operator fallback | SENT-016/shared flow | unresolved — Linux original development fails its unchanged gate; exact incomplete/deadline/scoring outcomes remain retained. The Meta label erratum does not waive missing execution. |
| R36 | Atlassian lifespan/operator origin, real SDK request, service/client construction and enforcement | SENT-016/shared flow | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R37 | Applicable Python and TypeScript positives/negatives for every new rule | Rule-specific test files | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R38 | Rule defaults, selection, inline suppression, baseline/severity identities | Catalog/config/CLI/rule tests | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R39 | Canonical Finding, evidence/provenance/remediation/OWASP and limitations | Rules/Finding/report/docs | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R40 | Traversal/absolute/prefix/symlink and unrelated/discarded/replaced controls | Shared containment tests | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R41 | Helper execution, ineffective auth, unrelated validation, untrusted hashing | Existing correctness tests | passed — Named historical condition/source controls verified in available current-detector reports; strict whole-batch timing remains separately unresolved in R63/R64. |
| R42 | Candidate-bound 160 unique SOURCE lines across files | `llm/context.py`, review tests | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R43 | Overlap dedup/omissions, exact references, redaction LF/CRLF/CR, boundaries/symlinks | Context/reviewer tests | passed — Bounded implementation and current regression executions verified. Unsupported source forms remain explicit; test coverage is not detection accuracy. |
| R44 | Unchanged request/cache compatibility and capture reuse | Reviewer/cache/capture infrastructure | passed — Two approved requests regenerated with exact production fingerprints/hashes and replayed; original paid total $0.071799. No additional live call; full benchmark comparison is deferred separately. |
| R45 | Nullable reviews/Finding identities and all runtime proof through review | Finding/context/merge/report | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R46 | Runtime enumeration of every supported tool/path/mutation under SENT-008–011 | `dynamic/prober.py`, `test_probe_campaign.py` | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R47 | Fair rounds and rule/argument rotation; bounded GPT priorities | Same campaign tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R48 | Stable attempt ID independent of scan/time/schema identity | ProbeBinding/report tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R49 | 24 STARTED attempts / 120s; timing after image and before discovery | Campaign/config tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R50 | CLI > env > file > default positive settings; rules-only bypass; Action config | `config.py`, `cli.py`, configuration/Action tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R51 | Fresh baseline/attack; invalid baseline prevents attack | Existing sandbox/session engine | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R52 | Discovery/baseline/attack schema drift | Campaign/session tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R53 | Unsupported/inconclusive/startup/execution/interruption states; cleanup | Campaign/sandbox tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R54 | Planned/unstarted records, no fabricated empty/incomplete coverage, exit 3 | Campaign/model/orchestrator/report | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R55 | Preserve every repeated observable proof through merge/review/output | Dynamic merge/Finding/context/report | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R56 | Native 1.7 unique IDs and matching ordered binding/discovery/outcome references | Report models/validators | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R57 | Actual planned/eligible/started/tested totals and remainder/budget invariants | Report coverage/models/native validator | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R58 | Legacy 1.3/1.4/1.5/1.6 reports/baselines, honest unknown coverage | Baseline migration/report tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R59 | Workspace structured coverage validates against inventory | Report coverage and static summary | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R60 | Console/native/SARIF and every rule-keyed consumer | Runtime/report/orchestrator/scripts | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R61 | Packaged Finding/report schemas, SARIF 2.1.0 validation | Schema generator and validation tests | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R62 | Owning architecture/schema/rule/compatibility/config/onboarding/Action docs | Root and `docs/` | passed — Owning documents distinguish current code/verification, historical evidence, deferred paid/pilot scope, failed timing, pending fresh freeze and final human acceptance. Phase 22 stays incomplete. |
| R63 | Historical 45-input deterministic repeat pair, 120s deadline | Existing Phase 20 runner | unresolved — The user-approved Linux execution retained the unchanged full-batch completion/timing/condition gates. Historical pair does not pass; skipped batches and every measured outcome remain explicit, with no retry or pooling. |
| R64 | All 20 vulnerable condition hits; zero fixed/safe condition alerts | Frozen condition scorer + per-input adjudication | unresolved — The user-approved Linux execution retained the unchanged full-batch completion/timing/condition gates. Historical pair does not pass; skipped batches and every measured outcome remain explicit, with no retry or pooling. |
| R65 | All five Phase 22 development pairs, paired mutations, controls | Frozen Phase 22 runner | unresolved — Linux original development fails its unchanged gate; exact incomplete/deadline/scoring outcomes remain retained. The Meta label erratum does not waive missing execution. |
| R66 | Fresh holdout outside tuning, separate results/no invented threshold | Approved frozen Phase 22 corpus | passed — The exact62987a6 freeze was explicitly approved. All5 fresh inputs complete twice natively and once with pinned Semgrep1.176.0; both tiers miss both correlated vulnerable variants, zero named alerts on3 negatives. Native reports equal except volatile fields; unresolved dispatch/class flows and50 comparator JQuery false positives are source-assessed. Measurement requirement passes without inventing an accuracy threshold; limitations await final human acceptance. Original holdout stays separate. No tuning or paid calls. |
| R67 | All new/changed unrelated findings adjudicated; historical 70 unchanged | Evidence/adjudication ledger | passed — Fresh comparator50 false positives and every fresh native unresolved diagnostic are source-bound. Linux reports are compared in full except documented volatile fields; order-only changes retain both arrays. Any remaining substantive deltas are explicit. Original historical70-warning backlog remains unchanged. |
| R68 | Pinned comparable Semgrep rerun; Snyk/Cisco unmeasured | Existing comparator runner | passed — The exact62987a6 freeze was explicitly approved. All5 fresh inputs complete twice natively and once with pinned Semgrep1.176.0; both tiers miss both correlated vulnerable variants, zero named alerts on3 negatives. Native reports equal except volatile fields; unresolved dispatch/class flows and50 comparator JQuery false positives are source-assessed. Measurement requirement passes without inventing an accuracy threshold; limitations await final human acceptance. Original holdout stays separate. No tuning or paid calls. |
| R69 | Per-input statuses/support/completion denominators, repeated differences | Measurement/scoring infrastructure | passed — Actual per-input completion/support states, named-condition denominators and correlated variants retained. Missing reports remain missing; misses and incomplete outcomes are not relabeled. |
| R70 | Git mcp==1.29.0 image/environment identity and Docker startup/discovery/campaigns | Authorized Git packet + existing sandbox | passed — Current contract tests, hosted Docker/isolation and actual 20/20 fixture replay verified. Approved Git evidence remains 312 tested/728 remaining across 13 incomplete campaigns; no Git defense or complete coverage claim. |
| R71 | Full Ruff/format/strict mypy/lock/schema/native/SARIF/pytest >=80% branch | Makefile/workflows + locked environment | passed — Normal CI/docs checks at workflow delivery88a559e verify scanner/package inputs unchanged from tested62987a6. Complete logs and distributions retained; manual benchmark outcome is separate. Final local docs check is separately retained. |
| R72 | Audit/notices/generated artifacts offline/strict docs/build/installed wheel | Existing commands/workflows | passed — Normal CI/docs checks at workflow delivery88a559e verify scanner/package inputs unchanged from tested62987a6. Complete logs and distributions retained; manual benchmark outcome is separate. Final local docs check is separately retained. |
| R73 | Docker/Action/rules-only network isolation and supported fixtures | Existing suites/workflows | passed — Normal CI/docs checks at workflow delivery88a559e verify scanner/package inputs unchanged from tested62987a6. Complete logs and distributions retained; manual benchmark outcome is separate. Final local docs check is separately retained. |
| R74 | Hosted Linux/macOS/Windows Python 3.10–3.13 | Existing 12 quality + 12 wheel jobs, Docker/isolation jobs | passed — Normal CI/docs checks at workflow delivery88a559e verify scanner/package inputs unchanged from tested62987a6. Complete logs and distributions retained; manual benchmark outcome is separate. Final local docs check is separately retained. |
| R75 | Concrete paid packet: actual config/model, exact cases/requests/purpose/reuse/replacements | Existing request preparation/capture ledger | passed — Two approved requests regenerated with exact production fingerprints/hashes and replayed; original paid total $0.071799. No additional live call; full benchmark comparison is deferred separately. |
| R76 | Token/request/dollar ceilings, identities, retries/failure/stopping policy | Exact future approval packet | passed — Two approved requests regenerated with exact production fingerprints/hashes and replayed; original paid total $0.071799. No additional live call; full benchmark comparison is deferred separately. |
| R77 | Reviewed 45/45 completion/retention on identical inputs; abstention/needs_review/suppression accounting | Existing reviewer/measurement infrastructure | explicitly user-deferred — Full 396-request reviewed benchmark/holdout deferred for cost. No full reviewed accuracy, suppression, latency or retention result is claimed. Additional paid calls require approval. |
| R78 | Separate reviewed holdout, latency/tokens/cache reuse/cost | Existing scoring/ledger | explicitly user-deferred — Full 396-request reviewed benchmark/holdout deferred for cost. No full reviewed accuracy, suppression, latency or retention result is claimed. Additional paid calls require approval. |
| R79 | Lossless numbered evidence batch after v3; per-file hash readback/extraction | Integration archives and command wrapper | passed — Both approvals, exact workflow delivery, frozen measurement identity, raw outcomes, failures, full reports and source assessments are retained and delivered with the updated86-row audit. Earlier seals/implementation preserved. |
| R80 | Complete command/source/harness/corpus/config/environment identities; failures/limitations | Requirement map + acceptance packet | passed — Both approvals, exact workflow delivery, frozen measurement identity, raw outcomes, failures, full reports and source assessments are retained and delivered with the updated86-row audit. Earlier seals/implementation preserved. |
| R81 | Reviewable local commits on single integration branch; preserve old drafts | Git history and PRs #22–36 | passed — Both approvals, exact workflow delivery, frozen measurement identity, raw outcomes, failures, full reports and source assessments are retained and delivered with the updated86-row audit. Earlier seals/implementation preserved. |
| R82 | Inspect real ancestry/bases and deliver one consolidated final draft | Git/GitHub delivery | passed — Both approvals, exact workflow delivery, frozen measurement identity, raw outcomes, failures, full reports and source assessments are retained and delivered with the updated86-row audit. Earlier seals/implementation preserved. |
| R83 | ROADMAP/status separate delivered code, technical/paid/human/pilot gates | Roadmap/status/acceptance packet | passed — Both approvals, exact workflow delivery, frozen measurement identity, raw outcomes, failures, full reports and source assessments are retained and delivered with the updated86-row audit. Earlier seals/implementation preserved. |
| R84 | Human technical acceptance and external pilot-dependent gate | User/maintainer evidence | unresolved — Both execution/freeze approvals are received; neither grants final human technical acceptance. Phase22 remains incomplete until every technical gate is satisfied and the user accepts the concrete final packet and limitations. Pilots and paid comparison stay explicitly deferred; Phase21/24/15 remain unchanged. |
| R85 | Preserve static no-execution/no-symlinks/no-tooling; Docker-only runtime | Shared existing trust boundaries | passed — Static source-only and Docker-only target boundaries preserved. No new paid call, fresh-v2 evaluation, unapproved runner dispatch, merge, release or outreach. Exposed-v1 regression reruns use existing explicit authorization. |
| R86 | No paid calls, merge/release/outreach/source sharing without approval | Authorization record | passed — Static source-only and Docker-only target boundaries preserved. No new paid call, fresh-v2 evaluation, unapproved runner dispatch, merge, release or outreach. Exposed-v1 regression reruns use existing explicit authorization. |
