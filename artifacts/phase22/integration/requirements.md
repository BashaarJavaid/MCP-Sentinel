# Consolidated Phase 22 requirement checklist

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

## Requirement-to-evidence audit (continuation; no final gate claims)

Additional audit through `029f686`: `be6349d`/`ab0e13c` and `d5e02e9` each pass
941 affected regressions; `b3b2318` verifies crowded 160-line context selection.
The 79-test native/campaign/baseline audit supports R45–R60 without replacing their
final Docker/consumer gates. `b55a087` adds offline preparation, checked replay and
comparator treatment support for R44/R65–R68; capture uses separate Phase 22 evidence
and remains paid-approval gated. R35 remains open: the latest d5e02e9 all-rule Meta
run completes 0/5, while the selected-rule fixed-source profile completes three
candidates and is not a family gate. The frozen fixed-label decision remains pending.
Commands, failures and precise limits are retained in progress and batch 18.

Scope remains the full continuation request. Each row below is required; `open`
means implementation, condition measurement, or final-source evidence remains.
Named tests are regression locations, not proof of independent condition gates.
Earlier sources and archives remain authoritative for their narrower claims.
The continuation starts at `83c9985` plus tracked patch
`9f533e8eb643e68a9cc5db0217b3db20a2d120d8789987635584037387cb86d6`.

| ID | Required behavior / evidence | Implementation and regression owners | Evidence / outstanding gate |
| --- | --- | --- | --- |
| R01 | Correct dirty worktree and packet identities | `phase22/integration`, authorization packets | Verified exact handoff diff and both SHA-256 values; no reset or source loss |
| R02 | Source-established constructors, fields, aliases and replacement invalidation | `discovery.py`, `path_flow.py`, `test_python_state_flow.py`, `test_ssrf.py` | `fec9215`; `constructor-final-focused` 253 passed; types/lint/format retained |
| R03 | Read-only builtin dictionary inspection with shadowing controls | Shared `PathFlow.call` | Five false alarms reproduced; corrected with real dictionary/builtin binding checks in `fec9215` |
| R04 | Reflection, unknown mutation, custom hooks and constructor/decorator ambiguity | Same shared flow and containment controls | Computed `getattr` and `vars` assignment targets reproduced and fixed; broader unsupported flows remain explicit |
| R05 | Imported handlers and schemas | `discovery.py`, TypeScript discovery, registration flow | `2b45b10` fixes local import precedence; `0d3f9a3` tracks source module replacement; `a035585` resolves unobserved forward declarations. Focused/shared checks pass; final detector and inventory support gate open |
| R06 | Aliases/re-exports, local imports and package exports | Shared module resolvers | Existing delivered controls; final integrated coverage open |
| R07 | Statically bound helpers, factories, inherited/bound methods | Shared discovery/path/registration flow | Python C3/lifespan controls retained; `2066ca7` adds plain TypeScript class receivers/fields and once-only calls. Auth condition passes at `34220b7`; other service/lifecycle conditions and final verification remain open |
| R08 | Cross-file caller/guard/sink evidence and binding identity | Shared Python/TypeScript flows | `c6234a0` fixes missing Python/TypeScript returned-helper source anchors; both counterexamples reproduced and 49 context/review tests pass. Native condition evidence and full caller/guard/sink audit remain open |
| R09 | Genuine SDK context vs caller/fake/rebound/local SDK | Shared discovery/context source checks | Bounded SDK launch/provider/middleware state is implemented through a2940e2/0eb39b5/f2ea709. `0491f32` adds source-established Express middleware/next ordering with 292 affected passes. Final actual-source condition and low-level attachment audit remain open |
| R10 | Low-level registration and dispatch | Shared discovery/registration | Final required source forms open |
| R11 | uv/npm/pnpm members and exclusions | `workspaces.py`, `test_workspaces.py` | `4114f59` discloses unsupported exclusion globs across uv/npm/pnpm. Three original failures and 36 passing regressions retained; `v2-workspace-audit-4114f59/packet.json` binds the source audit. Final integrated/hosted acceptance remains separate |
| R12 | TS aliases/inherited local compiler configuration, inaccessible parents | TypeScript module resolver | Local origins, private/ambiguous/escaping exports and unavailable inherited settings audited in `v2-workspace-audit-4114f59/packet.json`; module regressions pass in its 36-test check. Final hosted acceptance remains open |
| R13 | Aggregate root vs individual config, nested config disclosure | Config/traversal/workspace inventory | Root/member precedence and nested-configuration disclosure audited in `v2-workspace-audit-4114f59/packet.json`; current focused regressions pass. Final integrated/hosted acceptance remains open |
| R14 | Per-member counts without shared-file duplication | Static coverage and native report models | Longest member-path ownership and exact native surface/file-count invariants audited in `v2-workspace-audit-4114f59/packet.json`; 36 workspace/module/native regressions pass. Final integrated acceptance remains open |
| R15 | Inaccessible/unsupported members, ambiguity/import/reflection/schema gaps | Workspace/discovery diagnostics | Workspace issue propagation, unsupported globs and unavailable members audited in `v2-workspace-audit-4114f59/packet.json`. Broader source-binding/reflection/schema audit and final integration remain open |
| R16 | Repository escapes and symlinks; dynamic single Python package | Config/traversal/workspace tests | Boundary and single-package contracts audited in `v2-workspace-audit-4114f59/packet.json`; symlink/escape/dynamic selection controls pass. Final runtime/hosted acceptance remains separate |
| R17 | Helm original bytes/text secrets and explicit YAML omission | Traversal/config tests | Original-text retention, secret locations and strict ordinary/sidecar YAML audited in `v2-workspace-audit-4114f59/packet.json`. Owning full-suite milestone is running on 3e1faac |
| R18 | Historical atlassian-auth condition | SENT-016 and shared lifecycle/middleware/client flows | Fixed `34220b7`: 4/4 exposed inputs completed, 2 vulnerable condition hits, 0 fixed-condition alerts; 8 fixed nondefault candidates qualified. `auth-fixed342-development/condition-adjudication.json`; final repeat/holdout/review and human acceptance open |
| R19 | Historical atlassian-ssrf condition | SENT-015, shared URL flow and enforced returned errors | `3a2a276`: 4/4 native inputs complete; initial requests distinguish vulnerable/fixed but permission-search candidate remains. `18e385f` corrects its service-field/URL-path trace, with 629 affected passes; native remeasurement/final gate open |
| R20 | Historical atlassian-upload condition | SENT-012, service factories | At `6da955e`, all 5 complete across original run plus separate safe retry; 2 vulnerable Confluence condition hits and 0 fixed/safe alerts. `v2-upload-6da955e-adjudication/` retains condition scoring, source hashes, failures and separate policy-uncertain content reads. Final integrated repeats and independent acceptance remain open |
| R21 | Historical excel-boundary condition | SENT-012 | `4dfd24c`: five exposed inputs completed; two vulnerable condition hits, zero fixed/control matched alerts; stdio policy mismatch separate; final repeat open |
| R22 | Historical filesystem-prefix condition | SENT-012, TS normalization/component/physical-parent flow | Earlier four-input gate retained; integrated remeasurement open |
| R23 | Historical git-arguments condition | SENT-014 | Final independent measurement open |
| R24 | Historical git-repository condition | SENT-012 | At c75e876 all four native inputs complete: one repository-selection condition hit per vulnerable input, zero on both fixed inputs. `v2-git-mobile-c75e876/` retains these successes and the two separate Mobile timeouts. Final 45-input repeats remain open |
| R25 | Historical git-staging condition | SENT-012 | PR #23 narrow result retained; integrated remeasurement open |
| R26 | Historical kubernetes-shell condition under unchanged SENT-002 meaning | `5065f16`, `typescript_execution.py`, `test_command_execution.py` | Five development inputs complete, two vulnerable hits, zero fixed/mutation/control condition alerts; `kubernetes-development-shared/condition-adjudication.json`; final repeat open |
| R27 | Historical mobile-output condition | SENT-012 | `b51aee1`: five exposed inputs complete; two vulnerable inputs have both screenshot and recording condition hits; zero fixed/control matched alerts, residual physical uncertainty separate; final repeat open |
| R28 | Mastra failure-return flags and unsafe directory fallback | SENT-012, TS shared flow | Five development inputs completed with two vulnerable condition hits and zero fixed/control matched alerts; `mastra-fallback-loop-continuation/condition-adjudication.json`; later loop-carried state, unrelated review and final repeat remain open |
| R29 | Explicit description override, exfiltration, cross-tool redirection | SENT-013, description/discovery | Earlier independent development result retained; final discovery/holdout/retention open |
| R30 | Benign instructions and quoted warnings; parameter/low-level metadata | SENT-013 | Existing regressions; final-source acceptance open |
| R31 | dbt selector options through nested factories/mutable argv | SENT-014 | Earlier 5/5 development result retained; final remeasurement open |
| R32 | Git option positions, rejection, command-specific terminators, object APIs | SENT-014 Python/TS controls | Full acceptance open; preserve unrelated/replaced TS fix `37f2190` |
| R33 | Meta image caller URL request and scheme/private/loopback checks | SENT-015 | Earlier 5/5 result retained; final remeasurement/adjudication open |
| R34 | Fixed public authority plus caller suffix; enforced actual return value | SENT-015/shared flow | `ee6c9f5` derives facts from actual evaluation (once-only, replacement and short-circuit controls); redirects/DNS rebinding outside claim |
| R35 | Meta ContextVar/HTTP authentication/operator fallback | SENT-016/shared flow | Prior source-specific completions and all failures retained. At 65ba622, all five native inputs time out (120048/120044/120043/120051/120055 ms) while a historical diagnostic also runs. Binary combinations match 287144 differential cases and 942 regressions pass; isolated completion and condition gates remain open. Frozen fixed-label configuration conflict still awaits a versioned user decision |
| R36 | Atlassian lifespan/operator origin, real SDK request, service/client construction and enforcement | SENT-016/shared flow | `34220b7` records the actual HTTP/lifespan/client condition on all four exposed inputs; 425 affected regressions. Session-based client auth and remaining authorization/compatibility gates remain open |
| R37 | Applicable Python and TypeScript positives/negatives for every new rule | Rule-specific test files | `16a0da6` adds Express factory callbacks through source helpers; 665 affected tests pass. TypeScript middleware/client and final real-flow gates remain open |
| R38 | Rule defaults, selection, inline suppression, baseline/severity identities | Catalog/config/CLI/rule tests | Earlier per-rule checks retained; final integrated acceptance open |
| R39 | Canonical Finding, evidence/provenance/remediation/OWASP and limitations | Rules/Finding/report/docs | Final acceptance checklist open |
| R40 | Traversal/absolute/prefix/symlink and unrelated/discarded/replaced controls | Shared containment tests | Existing controls retained; all required independent families open |
| R41 | Helper execution, ineffective auth, unrelated validation, untrusted hashing | Existing correctness tests | Preserve; final-source full suite open |
| R42 | Candidate-bound 160 unique SOURCE lines across files | `llm/context.py`, review tests | `v2-helper-return-evidence-fixed-loopback`: 49 context/review tests pass at c6234a0, including 160 unique source lines, omitted anchors and exact helper references; final current-request audit remains open |
| R43 | Overlap dedup/omissions, exact references, redaction LF/CRLF/CR, boundaries/symlinks | Context/reviewer tests | ecdf579 source-coordinate/boundary fixes retained. At c6234a0, 49 context/review tests pass; initial four denied loopback binds and permitted rerun retained. Exact request compatibility/final regression gate open |
| R44 | Unchanged request/cache compatibility and capture reuse | Reviewer/cache/capture infrastructure | All 35 historical prepared requests reproduce exactly and their captures pass checked replay; initial missing-directory diagnostic retained/corrected. Current candidate/context rebuilding and final replacement selection remain open |
| R45 | Nullable reviews/Finding identities and all runtime proof through review | Finding/context/merge/report | Repeated standalone proofs now covered by `test_probe_campaign.py`; final gate open |
| R46 | Runtime enumeration of every supported tool/path/mutation under SENT-008–011 | `dynamic/prober.py`, `test_probe_campaign.py` | Integration implementation under verification; no final Docker gate yet |
| R47 | Fair rounds and rule/argument rotation; bounded GPT priorities | Same campaign tests | Focused controls pass; final gate open |
| R48 | Stable attempt ID independent of scan/time/schema identity | ProbeBinding/report tests | Focused controls pass; final gate open |
| R49 | 24 STARTED attempts / 120s; timing after image and before discovery | Campaign/config tests | Focused budget/discovery/startup tests pass; final gate open |
| R50 | CLI > env > file > default positive settings; rules-only bypass; Action config | `config.py`, `cli.py`, configuration/Action tests | The existing Action-to-CLI test verifies repository settings of 7 attempts/31 seconds at orchestration. `v2-workspace-action-configuration`: all 94 Action/configuration/workspace checks pass. Final hosted/installed Action gate remains open |
| R51 | Fresh baseline/attack; invalid baseline prevents attack | Existing sandbox/session engine | Existing and focused controls; integrated Docker gate running/pending |
| R52 | Discovery/baseline/attack schema drift | Campaign/session tests | Focused discovery drift test passes; final Docker/consumer gate open |
| R53 | Unsupported/inconclusive/startup/execution/interruption states; cleanup | Campaign/sandbox tests | 65ba622 fixes unsupported schemas and missing local references incorrectly establishing complete enumeration. Five original failures retained; seven schema controls preserve supported partial attempts and native incomplete status. 158 affected checks pass; final actual Docker gate remains open |
| R54 | Planned/unstarted records, no fabricated empty/incomplete coverage, exit 3 | Campaign/model/orchestrator/report | Integration migration under verification |
| R55 | Preserve every repeated observable proof through merge/review/output | Dynamic merge/Finding/context/report | Repeated-proof tests pass; full gate open |
| R56 | Native 1.7 unique IDs and matching ordered binding/discovery/outcome references | Report models/validators | Focused invalid-reference tests pass; final gate open |
| R57 | Actual planned/eligible/started/tested totals and remainder/budget invariants | Report coverage/models/native validator | Focused model/native arithmetic tests pass; final gate open |
| R58 | Legacy 1.3/1.4/1.5/1.6 reports/baselines, honest unknown coverage | Baseline migration/report tests | Existing + new tests; final whole-suite gate open |
| R59 | Workspace structured coverage validates against inventory | Report coverage and static summary | New inconsistent-count cases reproduced; 32 affected checks pass |
| R60 | Console/native/SARIF and every rule-keyed consumer | Runtime/report/orchestrator/scripts | `v2-consumer-audit-7371692/packet.json` retains source hashes and the consumer audit. 7371692 adds actual completion/outcomes to generated ablation cases; original missing-field failure retained, 50 related tests pass. Rule-keyed GPT priority validation is distinct from ordered runtime attempts. Final Docker/full-suite/hosted gates remain open |
| R61 | Packaged Finding/report schemas, SARIF 2.1.0 validation | Schema generator and validation tests | Generated draft; final source consistency gate open |
| R62 | Owning architecture/schema/rule/compatibility/config/onboarding/Action docs | Root and `docs/` | Batched updates in progress; strict docs gate open |
| R63 | Historical 45-input deterministic repeat pair, 120s deadline | Existing Phase 20 runner | Final candidate not ready; both runs open |
| R64 | All 20 vulnerable condition hits; zero fixed/safe condition alerts | Frozen condition scorer + per-input adjudication | Final gate open; source-specific R18 auth condition passes, while R19 remeasurement, R20 completion and integrated all-family repeats remain open |
| R65 | All five Phase 22 development pairs, paired mutations, controls | Frozen Phase 22 runner | Prior partial measurements retained; full final run open |
| R66 | Fresh holdout outside tuning, separate results/no invented threshold | Approved frozen Phase 22 corpus | Source not opened for tuning; final evaluation open |
| R67 | All new/changed unrelated findings adjudicated; historical 70 unchanged | Evidence/adjudication ledger | Meta v2 source review: 20 corrected fixed-authority false alarms; 220 uncertain framework/resource/operator-policy cases; five-input repeat passes named condition, final remeasurement/other changed findings open; historical 70 explicitly unadjudicated |
| R68 | Pinned comparable Semgrep rerun; Snyk/Cisco unmeasured | Existing comparator runner | Open |
| R69 | Per-input statuses/support/completion denominators, repeated differences | Measurement/scoring infrastructure | Final results open; harness exit alone never qualifies |
| R70 | Git mcp==1.29.0 image/environment identity and Docker startup/discovery/campaigns | Authorized Git packet + existing sandbox | Fixed `80bd278`: all 13 eligible inputs measured, 24/80 attempts each, 56 untested each, exit 3 and clean cleanup; native/SARIF/console orchestrator check passes. Final-source compatibility/reverification open; Phase 20 preserved |
| R71 | Full Ruff/format/strict mypy/lock/schema/native/SARIF/pytest >=80% branch | Makefile/workflows + locked environment | Immutable 3e1faac full milestone: 1882 passed, 36 skipped, 89.27% branch coverage; database/logs retained. Later workspace/location/deadline changes have focused checks (36 workspace, 312 TypeScript and 19 deadline/parser/module passes). Final candidate complete quality gate open |
| R72 | Audit/notices/generated artifacts offline/strict docs/build/installed wheel | Existing commands/workflows | At 65ba622/7371692, schema/notices/offline retained-artifact checks, strict docs, locked requirement export, advisory audit and wheel/sdist build pass. Audit reports no known vulnerabilities. Local pip wheel/sdist, pipx and uv checks pass with installed-module identity enforced and model credentials withheld. Linux network isolation, hosted OS matrix and final-candidate repetition remain open |
| R73 | Docker/Action/rules-only network isolation and supported fixtures | Existing suites/workflows | Integrated gate open; permitted Docker run evidence retained |
| R74 | Hosted Linux/macOS/Windows Python 3.10–3.13 | Existing 12 quality + 12 wheel jobs, Docker/isolation jobs | No final hosted run yet; historical scanner job cannot replace integrated measurement |
| R75 | Concrete paid packet: actual config/model, exact cases/requests/purpose/reuse/replacements | Existing request preparation/capture ledger | Not ready until offline gates pass; no new paid calls |
| R76 | Token/request/dollar ceilings, identities, retries/failure/stopping policy | Exact future approval packet | Explicit paid authorization still required |
| R77 | Reviewed 45/45 completion/retention on identical inputs; abstention/needs_review/suppression accounting | Existing reviewer/measurement infrastructure | Approval-dependent; prepare after offline gates |
| R78 | Separate reviewed holdout, latency/tokens/cache reuse/cost | Existing scoring/ledger | Approval-dependent; not replaced by replay or synthetic checks |
| R79 | Lossless numbered evidence batch after v3; per-file hash readback/extraction | Integration archives and command wrapper | Verified batch 20 retains 226 completed added/changed files through 394bb8a, including the 3e1faac full-suite database, HTTP/MCP and workspace corrections, cached-source equivalence/deadline checks, successful Mobile originals and isolated Meta concurrency feasibility. All member hashes read back; earlier 19 seals and coverage preserved |
| R80 | Complete command/source/harness/corpus/config/environment identities; failures/limitations | Requirement map + acceptance packet | Final packet open; exploratory source overlap must stay disclosed |
| R81 | Reviewable local commits on single integration branch; preserve old drafts | Git history and PRs #22–36 | Local implementation commits through 394bb8a; all original and subsequent failures preserved with numbered evidence seals. No repeated parent updates or pushes |
| R82 | Inspect real ancestry/bases and deliver one consolidated final draft | Git/GitHub delivery | PR #36 head `phase22/description-poisoning` at `8b6b0dd` verified as ancestor; selected base, final draft open |
| R83 | ROADMAP/status separate delivered code, technical/paid/human/pilot gates | Roadmap/status/acceptance packet | Final reconciliation open; no Phase 22 completion claim |
| R84 | Human technical acceptance and external pilot-dependent gate | User/maintainer evidence | Unmet external decisions; Phase 21 deferred, five workflows/ranked blockers still required |
| R85 | Preserve static no-execution/no-symlinks/no-tooling; Docker-only runtime | Shared existing trust boundaries | Required across every implementation/check; no target executed on host |
| R86 | No paid calls, merge/release/outreach/source sharing without approval | Authorization record | No new paid calls/merge/release/outreach in this continuation |
