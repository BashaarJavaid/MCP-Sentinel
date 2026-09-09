# Integration progress — not technical acceptance

The worktree was clean on `phase22/integration` at `68fa702` before changes.
The root checkout was not used for implementation. Existing draft PRs and Phase
20 evidence have not been modified, merged or published. No paid calls occurred.

## Reviewable source commits

- `37f2190`: TypeScript typed patterns bind runtime values without overwriting
  them with type-annotation names. Preserves the two original failing tests.
- `855a95d`: lexical Python helpers, nested and returned handlers, mutable Python
  argv, enforced selector rejection, list allocation/copy and branch controls.
- `dde2d49`: callback fields forwarded through source-established local registration
  wrappers and dataclasses; custom/annotation-only/partial bindings stay unresolved;
  source resolution uses the shared 120-second deadline.
- `ab4834b`: merge all shared caller locations, regenerate the stale Finding/report
  schemas and verify that cross-file review blocks are actually supplied.
- `192296d`: preserve token validation through concatenation and command prefixes,
  TypeScript member guards, CLI baseline/suppression/default/severity controls,
  and SENT-014 documentation. This is a milestone, not completion of SENT-014.

- `355f0f7`: conditional tests no longer contaminate returned argument values.
- `da52eb3`: multiline credential redaction preserves LF/CRLF/CR source lines;
  unchanged single-line redaction keeps its prior output.
- `d3fcf79`: default SENT-015 Python/TypeScript request flows and enforced
  destination checks, CLI selection/suppression/baseline/severity controls.
- `dbb2464`: a standard JSON container remains one fixed-prefix argv value;
  custom encoders and scalar/reassigned inputs stay conservative.
- `536bb69`: distinguish a fixed public URL authority from caller path suffixes.

- `86ac2dd`: URL validators returning errors/None establish protection only when
  their actual return value is enforced by the caller.
- `6d9bee9`: shared Python HTTP registration discovery and initial direct HTTP
  caller-to-operator credential fallback detection; not middleware-to-tool completion.
- `e2b0346`: Python dictionary members, aliasing, helper mutations, spread order,
  copies, updates and optional guarded values; SENT-014/015/016 consume shared state.
- `e1b23b8`: SENT-015 HTTP entries use the shared interpreter; FastAPI-injected
  dependencies are excluded from ordinary caller parameters.
- `d259126`: source-bound dataclass fields, callbacks, bound receivers and lambda
  callbacks; custom constructors and replaced guard decorators remain unresolved.

## Retained failures and measurements

`integration-suite-before.log`: 35 failed, 814 passed, 36 skipped; 83.33% branch
coverage. Schema drift accounted for most failures. Four loopback failures were
sandbox socket restrictions; context-warning expectations were replaced by
assertions on the actual supplied source. This exploratory run overlapped later
implementation; it is not a final immutable-source gate.

`report-consumers-after-schemas.log`: 81 passed, four sandbox loopback failures.
`report-consumers-loopback.log`: the same 85 tests pass with socket permission.
`options-registration-context.log`: 152 focused regressions pass.
`context-evidence-after.log`: 11 context/evidence checks pass.
`option-rule-contract.log`: 46 option tests pass, including CLI behavior.
`milestone-pytest.log` at `192296d`: 891 passed, 36 skipped, 86.84% coverage.
Milestone audit, lock, notices, generated-artifact check, strict docs and sdist/wheel
build pass. Network/sandbox failures and authorized reruns remain retained.
This is not final-candidate evidence for later implementation.

`ssrf-before.log` and `ssrf-initial.log`: rule not yet registered in configuration.
`ssrf-meta-development/`: both inputs incomplete because credential redaction
removed source newlines. Source formatting overlapped this exploratory run.
`multiline-redaction-before.log`: initial test collection failed from a missing
pytest import. `multiline-redaction-reproduced.log`: three actual redaction failures.
Two subsequent commands named nonexistent test files and performed no checks.
`multiline-redaction-review.log`: 67 passed, four sandbox socket failures;
`multiline-redaction-loopback.log`: all 71 pass with socket permission.
`ssrf-typescript-bindings.log`: corrected synthetic handler shape to the SDK's
single caller-input object; second SDK arguments are not ordinary caller fields.
It also exposed unsupported HTTP default-import and array-allowlist handling.
`ssrf-affected.log`: 201 pass. `ssrf-types-final.log`, `ssrf-lint-final.log` and
`ssrf-format-final.log` pass after retaining earlier formatting/type failures.
`meta-ssrf-development-retry/`: both scans complete, with three vulnerable image
request sink candidates and none at those sinks in the fixed partner. Source
SHA-256 matches the detector committed in `d3fcf79`; the commit was created while
the scan ran, without changing scanner source bytes.
`options-json-before.log`: two JSON-object/list false alarms reproduced.
`ssrf-prefix-before.log`: three fixed-public-prefix false alarms reproduced.
`ssrf-prefix-after.log`: 104 option/SSRF controls pass after both fixes.

The first dbt measurement has two incomplete reports from the stale Finding
schema. The following pair measurements complete but reveal condition-level
false alarms. `dbt-development-complete/` means the five selected input runs
completed; it does **not** mean the detector or technical gate passed. It contains
the original pair, paired mutations and source-conditioned safe control. Scoring
must use the named selector condition, not the presence of another warning at
the same subprocess sink. Other selector/command fields and codegen findings
require separate adjudication. The original historical 70-warning backlog remains
unadjudicated.

The retained diagnostic `dbt-fixed-flow-trace-boundary.log` shows safe selectors
being merged with unrelated unsafe arguments in a conditional expression.
`dbt-fixed-conditional-experiment.log` applies a diagnostic subclass only and
separates these flows. It is not a production measurement. The production correction is committed in `355f0f7`; 156 affected tests pass.
`dbt-development-conditional/` contains five completed runs with source SHA-256
matching the source tree archived from that commit, despite the run metadata
recording its parent before the local correction was committed.
`dbt-adjudication.json` records two vulnerable selector hits, zero fixed/control
selector alerts, five unrelated codegen false positives and eight uncertain
unrelated candidates. This is implementation-agent source review, not human acceptance.

`development-conditions.json` scores the ten completed inputs at `536bb69`:
each family has two vulnerable condition hits and zero condition alerts across
three fixed/safe inputs. Five unrelated dbt codegen false alarms are removed;
eight unrelated dbt candidates retain their source-review uncertainty. The Meta
reports contain 240 unrelated candidate instances still requiring adjudication.
The two independent development pairs, mutations and controls are correlated;
no holdout, runtime or reviewed-tier result is implied.
`ssrf-final-checks.log`: 110 option/SSRF/context tests pass at this source.

## Second integration milestone in progress

`python-state-bounded-regressions-corrected.log`: 214 pass; the preceding command
named a nonexistent containment test file and ran no tests. `http-url-injection-after.log`:
94 pass. `record-lambda-after.log`: 219 pass. Scoped mypy, Ruff and formatting pass
at the recorded sources after the retained type/style failures and corrections.
The full second-milestone suite at `d259126` passed **1010 tests, 36 skipped,
87.38% branch coverage** in 819.19 seconds. Ruff, formatting, schemas, strict
docs, generated artifacts, notices and the permitted lock check passed. The first
lock command could not access the existing uv cache; that failure remains retained.
Whole-project mypy found a missing generic argument in the new SSRF test helper;
`aaa759a` corrects it and whole-project mypy then passes. This source also removes
profiled repeated discovery; its 195 affected regressions, Ruff and formatting pass.
The initial correction had an import-indentation collection error, also retained.

A single exposed historical Atlassian-auth input was profiled with the
unchanged 120-second static deadline and was incomplete at that deadline. This is concurrent diagnostic verification,
not an isolated-throughput measurement or the final 45-input benchmark. An initial
profiler command failed to import the project harness; that failure is retained.
The profile records 28.8 seconds in repeated HTTP discovery, including 26.3 seconds
in repeated shadow-scope checks, and five tool-discovery passes totaling 15.6 seconds.
These instrumented concurrent timings motivate removing repeated traversal, not
increasing the deadline. `evidence-v2.json` indexes 237 losslessly retained files.

The repeated profile at `aaa759a` completed: 84.2 seconds in the static engine,
93.2 seconds including reporting, and 91 unrelated candidates (90 SENT-003 and
one SENT-012). There is no SENT-016 condition hit. It is a profiled single exposed
input; no isolated-throughput comparison or final corpus result is claimed.
`de1af5a` adds the genuine SDK HTTP request source to shared flow and distinguishes
it from ordinary stdio caller parameters and local SDK impersonation. The affected
set passes 201 regressions; the three new-rule CLI contracts pass, including
SENT-016 selection, default enablement, suppression, baseline and severity.
Whole-project mypy and corrected Ruff/format checks pass at the recorded source.
`evidence-v3.json` indexes 111 losslessly retained files including the completed
second milestone and repeated profile. Remaining condition-level work is unchanged.

## Outstanding work

The complete user-approved scope remains open in `requirements.md` and
`docs/phase22-implementation-status.md`. In particular, this milestone does not
complete SENT-015/016, all ten historical conditions, all five compatibility
areas, ordered runtime campaigns, the native 1.7 migration/consumers, final repeated
45-input measurements, fresh holdout, comparable Semgrep measurements, Git runtime
campaigns, reviewed evaluation or consolidated PR delivery. No paid approval
packet is ready. Human technical acceptance and five external pilot workflows
remain distinct, unmet external gates.

## Reproduction and identity

Each recorded command has a JSON record with command, cwd, environment overrides,
commit, diff hash, exit and duration, plus its raw log. Later commands also retain
the exact tracked diff in a same-name `.patch`; initial commands predate patch
capture and only retained the diff digest and raw failure output. The final source
commits above are authoritative for reconstruction. Measurement `results.json`
records additionally bind source/harness/corpus/configuration identities and report
hashes. Timings overlap verification work and are not isolated throughput results.

The frozen corpus and tested Git environment approvals remain exactly those in
`../authorization.json`. Held-out source has not been opened or used for tuning.

## Constructor, campaign and lifespan integration (batch 4)

`fec9215` preserves and finishes the four-file constructor handoff. The original
tracked patch matched SHA-256
`9f533e8eb643e68a9cc5db0217b3db20a2d120d8789987635584037387cb86d6`.
Additional regressions cover real builtin/dictionary inspections and constructor
reflection; the final constructor command passed 253 tests. This establishes
bounded source interpretation, not the independent Atlassian condition.

`3f75327` replaces runtime rule-keyed scheduling with ordered attempt bindings,
24-start/120-second campaign limits, discovery within the budget, fresh baseline
and attack sessions, unstarted remainder, and explicit failure/interruption
outcomes. Native 1.7 models/JSON validation check counts and references; merged
findings and candidate review retain repeated proofs. Configuration precedence,
rules-only bypass, repository Action settings, legacy migration, workspace
counts, and console/native/SARIF consumers have focused coverage.

Docker verification initially failed from socket restrictions, then from a stuck
Docker Desktop daemon (even a trusted `git --version` container remained Created).
The permitted run retained 28 failures and eight passes; these do not establish
working security controls. After daemon recovery, 31 checks passed and five
failed from a test-construction error already corrected while that run loaded
its source. The five corrected checks then passed (`campaign-docker-corrected`),
and both reference campaigns passed native/SARIF validation
(`campaign-docker-native`). Each log has its own source patch and command record.
These are fixture/independent-control Docker checks, not the required Git corpus
campaign measurement.

The full integration command `campaign-milestone-suite` failed: 1073 passed,
36 skipped, two orchestration test-fixture failures. The stronger report validator
rejected fabricated proof that did not match the fake outcomes. `a9c097e` corrects
those fixtures; 56 affected orchestration/report checks passed. The full run
started at `fec9215` plus tracked patch `d2df1f8c650a…` and untracked test snapshot,
then overlapped later lifespan implementation. Its final coverage report read
changed source and included the newly added, unexecuted lifespan module. The
reported 84.49% is therefore **not clean coverage evidence for a fixed revision**.
No full-suite pass is claimed for the campaign or subsequent source.

`9d396a4` connects explicit FastMCP lifespan registration and local mounts to
SDK context values through the shared interpreter. It preserves optional records,
real builtin `id` inspection and constructor field identity while rejecting
unestablished/local-shadowed registrations. 266 focused checks, lint, formatting
and corrected strict mypy passed at their recorded patches. The full authorized
exposed Atlassian source was materialized through the validated Phase 20 corpus
infrastructure; its tree is
`afd629310b07685052de0f3479be57da6e5c5fd5d1f692f1cfae90f6cf49f930`.
All 90 tool registrations resolve to the recorded `main_lifespan`. An explanatory
single-tool source trace now carries operator configuration through the actual
SDK context helper. It still produces **zero SENT-016 matches**: inherited mixin
initializers/forwarding, the credential-bearing client sink and enforcement
remain unfinished. The trace is not a condition-scored measurement.

The earlier post-constructor exposed measurement completed in 79.765 seconds of
reported scan time with 90 SENT-003 and one SENT-012 finding; zero SENT-016
condition hits. It overlaps later configuration/test edits, with static source
unchanged, and is not isolated throughput. Source, harness, corpus and report
identities remain in `atlassian-auth-constructor/results.json`.

`evidence-v4.tar.gz` preserves 437 additional files (including failures, source
patches, diagnostic sources and all command results above); each was read back
against its SHA-256. Earlier diagnostic script revisions were overwritten during
investigation before diagnostic-byte capture was added to the wrapper. Their
failure logs remain, but exact intermediate diagnostic bytes are not claimed;
final diagnostic scripts are in `diagnostics-v4.tar.gz`. Future wrapper snapshots
include their own wrapper and absolute `/private/tmp/*.py` command scripts.

The complete requirement map remains in `requirements.md`. No final 45-input
repeat pair, fresh Phase 22 holdout, competitor rerun, Git corpus campaigns, paid
request packet/evaluation, installed-wheel/Action/isolation/hosted final matrix or
consolidated draft is complete. No paid calls, pushes, PR creation, merge, release,
outreach or external acceptance occurred in this batch. Pilot recruitment remains
deferred; authorized implementation and offline verification still remain.


## Service construction and measured interpretation corrections

`c71e43e` follows bounded C3 mixin initializers, genuine Protocol bases, exact
positional/keyword forwarding (including present nullable keywords), real method
descriptors and source-established record truth. It retains conservative custom
construction/reflection controls. Its 280 focused regressions and corrected
lint/type/format commands are recorded under `source-service-*`.

The complete exposed Atlassian authentication input at that source exceeded the
unchanged 120-second static deadline (`atlassian-auth-service-measure`). Its
harness exited zero but the input is **incomplete**. Subsequent instrumented runs
`atlassian-auth-stage-profile`, `atlassian-auth-merge-stages` and
`atlassian-auth-sink-stages` also retain their incomplete status. Partial detector
matches and warnings are not scored as completed input results.

`1abade5` removes repeated allocation of immutable merge defaults and checks for
supported command sink syntax. `cc283a1` follows included imports from handlers,
registrations and their lifespan sources, including relative imports, re-exports,
cycles and ambiguous module matches. Files remain in the source index. Tool
visits remain recorded; an absent supported command form is not a claim that
unknown command APIs are safe. The first whole-source precheck could not avoid
unreachable subprocess calls in included tests; that intermediate run is retained.

`a2b88f1` follows explicit HTTP caller-to-operator selection into imported
`atlassian.Jira`/`Confluence` token and password keywords. Six missed cases were
reproduced first; enforced and unrelated guards, noncredential keywords, local
module impersonation and replaced/caller-shadowed bindings have controls. These
are direct-flow regressions. They do not establish the actual Atlassian middleware,
session-authentication or frozen fallback condition.

`ee6c9f5` corrects repeated interpretation during URL fact extraction. Facts now
use the values from the actual expression evaluation, scoped to its function and
expression. A once-only validator regression first failed; replaced values and
short-circuit-skipped validators also have controls. The same source-only,
single-tool profile changed from 83,061,516 calls / 23.302 seconds to 5,765,131
calls / 1.738 seconds. These are instrumented diagnostic timings, not independent
throughput measurements or condition scores.

The combined source through `ee6c9f5` passed 301 focused regressions (9.17 seconds),
Ruff, formatting and strict mypy (118 configured source files), recorded as
`source-evaluation-quality-final-{0,1,2,3}` with exact patches and command identities.
Earlier failed regressions, a mistaken test location attribute and lint/type/format
failures remain retained. No full suite result is attached to this later source.

Read-only GitHub inspection verified PR #36's head
`8b6b0ddf1d6f6cf5a8da3ab9421471865b801455`, branch
`phase22/description-poisoning`, as the integration branch's existing ancestor.
That is the selected consolidated draft base; the final draft has not been
created. `delivery-parent-pr36-permitted` retains the remote metadata and the
initial network-restricted failure is preserved separately. Old drafts remain.


The whole exposed input at `ee6c9f5` is still **incomplete**
(`atlassian-auth-evaluation-stages/results.json`). The instrumented run records
SENT-012 at 44.652 seconds, SENT-014 at 1.390 seconds and SENT-015 at 40.371
seconds, then reaches the unchanged 120-second deadline before SENT-016 finishes.
The harness exit zero is not a completed scan or condition hit. Source files
were held fixed during this run; documentation work overlapped it. Fresh holdout
source remains outside tuning. No new paid calls, pushes, draft creation,
merges, releases or outreach occurred.


The subsequent bounded dataclass/selector correction preserves exact fields and
shallow-copy aliases for genuine `dataclasses.replace`, keeps supported builtin
dataclass type inspection from invalidating records, and excludes impossible
branches for recoverable literal equality/membership selectors. Custom hooks and
replaced bindings remain conservative. Seven copy/type-control forms and literal
selector controls retain their initial failures. The broader regression run also
caught two predicate-key regressions and, in a later edit, two branch-evaluation
snapshot regressions; all are retained with their corrections. Final focused
verification is `dataclass-selector-branch-snapshot-corrected` (314 passed in 9.08
seconds) and `dataclass-selector-verified-{0,1,2}` (Ruff, formatting, strict mypy).

Current single-tool diagnostics expose four incidental SENT-016 client candidates
on per-user configuration paths. These are not the frozen missing-caller/global
fallback condition. The original config survives type inspection now, but some
record/keyword fields remain unresolved across optional/branch state. The four
candidates require further adjudication/correction; they must not be substituted
for independent condition scoring. There is no complete-input pass for this later
source and no final full-suite or hosted result.


Batch 5 seals 439 added/changed evidence files through `4d88844` in
`evidence-v5.tar.gz`, with per-file hashes in `evidence-v5.json`. All members were
read back and verified; batches 1–4 are unchanged. The focused source checks
above pass, and the owning documentation build passed (`service-evidence-docs`),
but all final technical and external gates remain explicitly open as mapped in
`requirements.md`. No consolidated draft has been created.

## Batch 6: fixed-source milestone and measured execution correction

`f12e891` distinguishes real dataclass classes and inherited classes during
`isinstance`, preserving conservative custom-metaclass behavior. Its focused
gate passed 316 tests. A detached verification checkout at that exact commit
then passed **1138 tests, 36 skipped, 87.94% branch coverage** in 927.50 seconds.
`service-milestone-fixed-suite` records the fixed checkout, exact imports and
empty final tracked diff. The original coverage database and JSON export are
retained as `service-milestone-f12.coverage` and `service-milestone-coverage.json`.
This is a milestone result, not a pass for subsequent source changes.

The same fixed checkout ran 18 original exposed historical vulnerable/fixed
inputs, excluding atlassian-auth (`exposed-pairs-f12`). Sixteen completed; both
atlassian-upload inputs exceeded 120 seconds. The completed Atlassian SSRF,
Excel, mobile and Kubernetes vulnerable inputs still missed their named rules.
Git/filesystem reports require condition adjudication; report completion alone
does not establish those gates. The harness returned zero while two inputs were
incomplete. This run is neither the final 45-input repeat nor fresh holdout.

`1d83b9c` adds shared TypeScript Express HTTP route discovery and direct
credential/URL flow, including imported handlers, rejected missing credentials,
nullish/OR/imperative fallback, source binding controls and stdio controls.
235 affected regressions, Ruff, formatting and strict mypy pass at the retained
source patch. Initial malformed target-fixture results are retained and are not
treated as TypeScript counterexamples. `typescript-http-f12-counterexample`
provides a valid prior-source failure. Two later imperative-branch false alarms
were reproduced and corrected through shared impossible-branch handling.
This does not complete middleware/factory or independent SENT-016 conditions.

`5065f16` feeds TypeScript shell execution through shared SDK discovery and
cross-file flow. The two failing low-level-dispatch regressions now pass;
220 existing execution/static regressions pass, followed by Ruff, formatting
and strict mypy. The last edits before committing only reflow source/test lines
and update owning documentation. The benchmark source patch is recorded in
`kubernetes-development-shared.json`; no implementation changed during that run.
All five approved historical Kubernetes inputs completed: two vulnerable
condition hits, zero condition-matched fixed/mutation/control alerts. The
scoring packet is `kubernetes-development-shared/condition-adjudication.json`.
Its first scoring attempt incorrectly expected the original function spelling
in the alias mutation and failed; the corrected scorer validates the actual
`execSync as runKubectlProcess` import and source flow. All failures are retained.
Thirty-two new unrelated execution candidates were source-reviewed: thirty
supported static candidates and two uncertain context-selection instances.
None is runtime-confirmed or independently human-accepted. Unchanged candidates
and the historical 70-warning backlog remain explicitly separate.

Batch 6 preserves 251 added/changed evidence files (94,420,419 raw bytes), with
every archived member read back against its SHA-256. Timings from concurrent
verification are not isolated throughput. Fresh Phase 22 holdout source remains
outside tuning. Final conditions, campaign/Docker verification, final repeat and
comparative measurements, review evaluation and consolidated draft delivery
remain open. No paid calls, pushes, merges, publications or outreach occurred.

## September 8 continuation: preserved registration and workbook work

The starting HEAD, five-file tracked diff, essential untracked registration module,
recovery archive, corpus and Git environment packet all match the handoff hashes.
The archive remains an unfinished recovery packet. The initial process inspection
was denied by the sandbox; the permitted read-only retry found no competing
verification process. No second agent runs in this worktree.

`continuation-registration-before` reproduces seven failures: six outer-call
registration origins and one escaped SDK instance. The shared TypeScript flow now
retains balanced source call sites, rejects unknown calls receiving SDK instances
(including record members), and reports those escapes. The cross-file regression
keeps two wrapped registrations, their schemas, locations and examined-rule
inventory distinct. Existing cast, callback replacement and constant controls are
preserved. An initial cross-file test used an invalid configuration keyword; the
corrected test and failed attempt are retained separately.

`continuation-void-guard-before` reproduces two lost successful-helper protections.
Normal return/fallthrough exits now carry their common enforced facts back to the
caller. Boolean return values alone do not establish enforcement, and conditional
calls do not export unconditional guard facts. Caught failures, early returns,
unrelated paths and replaced inputs remain alerts. The original workbook-loader
sink work is preserved with its six controls; it does not resolve the Excel
transport/configuration condition.

`continuation-registration-quality`: 325 focused tests passed in 76.07 seconds on
its exact retained patch. Later edits only changed formatting and the covariant
annotation for the common-facts input. Whole-project Ruff, formatting and strict
mypy pass in `continuation-registration-{ruff-final,format-corrected,mypy-final}`;
initial style/type failures remain. This is not a final whole-suite, independent
condition, campaign or acceptance gate. All uncompleted requirements remain open.

### Containment continuation after 96712f3

Enforced realpath/commonpath helper predicates retain actual value identity and
successful-return guard facts. Two original commonpath failures were reproduced;
317 affected regressions passed before launch-state changes. Explicit SDK launch
functions now supply their preceding global assignments to handler interpretation.
Native descriptions and flow evidence retain all observed launch transports;
module-level/dynamic/unresolved launch state also retains an unconfigured handler
analysis. Two hidden-unconfigured-launch regressions failed before correction.
Workbook save recognition requires a genuine constructor/loader receiver; direct
replacement and escape controls remain. The first save gate reproduced three
misses, then all twelve workbook load/save controls passed.

`continuation-excel-launch-measure` completed all five exposed Excel inputs at its
retained source patch. Each report has seven SENT-003 and eighteen SENT-012
candidates. Vulnerable variants cite SSE/streamable HTTP/stdio launches; fixed
variants and the safe control cite only stdio. These stdio candidates remain
visible and require source-condition adjudication; no whole-repository clean
claim is made. Later workbook-save support is not included in this earlier run.

TypeScript relative-path guards now retain a lexical-boundary fact across
normalization, successful helpers and the guarded Windows case-folding branch.
That fact narrows a residual path candidate to physical/symlink uncertainty,
without erasing it. `continuation-mobile-lexical-measure` completed five exposed
inputs: vulnerable variants retain ordinary screenshot boundary findings, while
fixed variants/control retain narrower physical-containment candidates. Existing
non-symlink-parent prerequisites matter to adjudication. Recording/device-command
coverage and final-candidate measurement are not established by that result.

A local wrapper regression found that inventory counted the shared internal SDK
registration as a third tool. The correction retains SDK source coordinates in
bindings while inventory uses the two outer registration calls. Imported and
same-file wrapper cases pass. Source-specific checks include 380 Python/engine
regressions, 256 TypeScript/shared regressions and then 448 combined regressions;
subsequent inventory corrections have their own retained tests. Style/type
failures, two nonexistent-test command mistakes, all failed regressions and
intermediate source patches remain preserved. Whole-project mypy/Ruff/format
pass in `continuation-containment-{mypy,ruff,format}`. No final full quality,
benchmark, review, campaign, hosted or delivery gate is claimed.

### Fixed-source 4dfd24c milestone and URL/launch follow-up

`continuation-4dfd24c-full-suite` ran with implementation/test bytes held fixed:
1,215 passed, 36 skipped in 963.81 seconds, with 88.27% branch coverage. The
combined database is retained as `continuation-4dfd24c.coverage`; its preservation
record binds it to the commit. Schema and third-party-notice checks also pass.
This is an integration milestone, not the final Phase 22 acceptance source.

`containment-4dfd24c/` contains ten completed exposed Excel/mobile scans, their
native reports and source-condition adjudication. Four vulnerable inputs have
condition-correct candidates; six fixed/control inputs have no matched alert.
Excel remote-mode candidates include real launch/global/path/load/save flow;
retained stdio alerts do not establish a remote-policy violation. Mobile evidence
covers screenshot output; the remaining physical-containment candidates concern
symlinks excluded by the frozen named condition. Recording output remains open.
All unrelated candidates and uncertainty are retained separately. Scans overlapped
pytest, so their durations are not isolated throughput measurements.

`meta-unrelated-adjudication-continuation.json` reviews all 240 unrelated instances
from the earlier `meta-ssrf-development-five` reports: 25 source-supported false
alarms, 205 uncertain framework/schema-enforcement cases, and ten uncertain output
resource-policy cases. This is implementation-agent source review, not independent
acceptance. The unchanged historical 70-warning backlog remains unadjudicated.

Three URL-composition regressions reproduced lost fixed-authority information and
an unsupported formatting exemption. SENT-015 now preserves bounded constant
string composition using evaluated source values, without executing target code.
Four launch replacement/deletion/escape regressions reproduced unsafe configured
state assumptions. Such launches now retain unconfigured analysis and a warning;
source-bound execution of SDK wrappers remains outside this launch index.
`continuation-url-launch-quality-corrected` passed 338 affected tests in 63.53s;
whole-project Ruff, formatting and strict mypy passed. The initial wrong test-file
selection and every failed reproduction remain in the evidence. Meta and Mastra
remeasurements are separate source-specific commands; their results are not
assumed here. All other authorized implementation/final gates remain open.

### 45ea165 development measurements and returned-status guards

The Meta URL-composition repeat completed five inputs. Exact candidate-key
comparison shows only twenty removals: four fixed Graph API authority false alarms
per input. Two vulnerable inputs retain the original image-URL condition hits;
fixed variants/control have no named-condition alert. Reports and scoring are in
`meta-url-composition-continuation/`. The original 240-instance adjudication is
preserved; its `-v2.json` revision classifies five operator-selected destination
cases as uncertain policy, since the base is unknown and private-base controls
remain intentional. Thus twenty false alarms were corrected and 220 unrelated
instances remain uncertain; independent human acceptance is not implied.

The Mastra repeat completed five inputs with ten findings each, including broad
directory findings on fixed sources. It does not pass the source-condition gate.
The returned `isSecurityViolation` field must preserve the initial rejection
branch before fallback is interpreted; prefix-collision/symlink conditions also
remain distinct from the frozen ordinary-directory prerequisite.

Shared TypeScript flow now retains common record fields across returns and carries
branch facts on their boolean status values. Replacement and unknown escape
invalidate those facts, including nested records and credential consumers. One
positive regression failed before correction; all seven status-field controls
pass. `continuation-record-status-quality` passed 284 affected tests in 89.86s;
strict mypy, Ruff and formatting pass after retained line-length failures. The
last correction only split Python test string literals. This establishes bounded
record-status flow, not the complete Mastra condition or final technical gate.

### Mastra initial rejection versus derived directory paths

The first prefix-precondition repeat still missed the real fallback: the generic
handling of `while` did not bind its local path variable. Three durable loop
variants reproduced the miss. Shared TypeScript statements now interpret zero or
one iteration, retaining returns and rejecting any protection inferred solely from
an optional iteration. Later loop-carried state remains explicitly unresolved.

The flow separately records the originating input of derived paths and an enforced
normalized string-prefix precondition. Guard facts survive relevant helper calls
and returned status fields. This does not exempt the filesystem sink or establish
containment of later parent paths, prefix siblings or symlinks. Mixed paths to a
shared sink retain the general description if any path lacks that precondition.
`continuation-fallback-loop-quality` passed 324 affected tests in 111.27 seconds;
nine targeted loop/status controls passed, including unreachable-loop and
zero-iteration cases. Whole-project strict mypy, Ruff and formatting pass. Original
prefix/loop regressions, style failures and scorer mistakes remain retained.

`mastra-fallback-loop-continuation/` contains five complete development scans,
with two vulnerable condition hits and zero fixed/control condition-matched alerts.
The readdir evidence includes the registered entry, initial path handling and
findNearestDirectory's split/join path inside its first iteration. Fixed candidates
explicitly require the originating input to pass its prefix check, excluding the
frozen initially rejected, non-shared-prefix traversal condition. Other path
candidates remain visible and unrelated-policy review remains open. The scorer's
first two attempts assumed the wrong source root and overly specific call-site
lines; the corrected scorer uses the manifest scan root and cited statements inside
the actual fallback function. Scans overlapped focused checks, so durations are
not isolated throughput. This is neither a final holdout result nor runtime proof.

### Git bounded campaigns on fixed source 80bd278

`git-campaigns-80bd278/results.json` records all 13 eligible historical Git inputs
in the approved separate SDK environment. The exact packet, input trees and
existing image ID were checked before execution. Each campaign planned 80
attempts, started/tested 24 and retained 56 unstarted attempts. Each returned
incomplete analysis (exit 3); cleanup passed. The driver reused one compatible
fixed-source campaign and ran the other twelve sequentially. Its exit zero means
the measurements finished, not that analysis completed. No model calls ran.

`git-native-80bd278/` additionally runs the staging vulnerable input through the
production orchestrator with explicit degraded review, no API key and cache
disabled. Native JSON and SARIF validate offline; console retains INCOMPLETE;
the remaining campaign work yields exit 3. This is source-specific runtime and
consumer evidence, not final integrated acceptance or proof of Git defenses.
The fixed checkout `/private/tmp/mcp-phase22-runtime-80bd278` remains preserved.

### Exact review source lines and manifest candidates

Eight failing regressions exposed non-Python manifest parsing and fabricated or
misaligned context lines. Context now parses only Python as Python, uses bounded
source windows for manifests, rejects primary ranges beyond actual source, and
keeps Unicode string separators from changing LF/CRLF/CR source coordinates.
The unchanged 160-source-line budget and runtime-proof blocks remain in place.
`continuation-review-source-bounds-after` passes 92 affected review/campaign/report
tests; focused mypy, Ruff and formatting pass after retained style failures.
Exact affected-request comparison and final capture reuse remain separate gates.

### Branch-selected operator clients and shared control metadata

Separate caller/operator client branches now retain enforced caller absence or
negative authentication conditions across helpers. Successful SDK HTTP getter
state is kept apart from the non-HTTP alternative. Environment comparison helpers
retain the actual selected setting/default and can qualify a fallback when the
declared default rejects it; the effective configuration is not assumed.
The candidate is retained, and mixed guarded/unguarded paths drop the blanket
qualification. Exception-prefix state remains a bounded-flow limitation.

An optional-return regression caught an incorrect inherited opt-in requirement:
shared helper return handling treated an internal control marker's empty key as
protection for unrelated empty-key values. The shared code now propagates these
facts only from actual arguments/members/globals. The corrected fixed-source
trace qualifies the real global branch with ALLOW_GLOBAL_CRED_FALLBACK and no
longer claims an unrelated OAuth-enable requirement. Incidental client candidates
remain distinct raw paths and require adjudication after native deduplication.

`continuation-credential-bound-values-quality` passed 492 affected tests in
328.17 seconds while an isolated profile ran concurrently. These are source-flow
regressions, not an independent-condition result. Both full auth inputs in
`auth-branch-pair-continuation/` exceeded the unchanged 120-second limit. The
harness exit zero and its empty diagnostic `inputs` print do not supersede the
two incomplete `outcomes` records. `auth-branch-stage-costs/` measured about 31s
in Semgrep, 49s in SENT-012, and 34s in SENT-015 before the deadline prevented
SENT-016 from running. `auth-containment-profile-current/` retains a bounded,
incomplete cProfile run: branch merges and repeated lexical-scope walks dominate.
All earlier marker, optional-return, style/type and nonexistent-test failures
remain preserved. This is not a technical acceptance checkpoint.

### Shared flow work and plain helper return truth

Immutable lexical walks are reused while their source AST remains alive. Branch
merges reuse unchanged values; empty URL facts no longer scan the entire state.
A reproduced URL false alarm came from treating an ordinary boolean helper as a
validation predicate: an unreachable request after `return False` appeared
reachable. Predicate identities now require actual destination facts. All 324
affected flow/discovery tests, focused mypy, Ruff and formatting pass in
`continuation-shared-flow-unchanged-*` and `continuation-shared-flow-final-format`.

`auth-component-costs-common-facts/` retains isolated component diagnostics:
SENT-015 completes in 42.47s and SENT-016 in 40.29s, with unchanged raw match and
warning counts. These overlapped tests and are not isolated throughput or full
scanner acceptance. Both inputs in `auth-common-facts-pair-continuation/` still
exceed the unchanged 120-second deadline. Earlier component profiles, incomplete
full scans and the failing plain-helper regression remain preserved. Actual auth
condition scoring, incidental path adjudication and final acceptance remain open.

### Immutable resolution, selected-file batches and presence checks

Complete Python name-resolution queries now reuse the immutable source index;
recursive calls retain their own cycle/depth budget and every lookup still checks
the deadline. A warmed-cache regression checks those boundaries. Semgrep batches
the same sorted selected files by encoded argument size (100,000 bytes on POSIX,
20,000 on Windows) instead of 200 files per process. Two before-failing tests check
complete path retention and batch boundaries. No rules or source paths are omitted.
The byte limit reserves room for fixed flags; process failures remain explicit.

`continuation-semgrep-byte-batches-after` passed 57 affected checks and
`continuation-semgrep-resolution-final-checks` passed three targeted checks.
An exploratory bounded flow-key cache did not resolve the deadline and was not
added. `auth-url-profile-resolution/` completed all 90 tool interpretations in
98.4 profiled seconds, with zero raw URL matches and 21,689 warnings. Branch merges
still account for about 26 cumulative profiled seconds. This is a component
profile, not a complete scan. Native stage measurements still time out at 120s;
Semgrep's measured 28s is total process/scan time, not startup time alone.

The auth trace also exposed a shared presence issue: rejection of an absent
configuration was not retained in later helpers. Branch-local narrowing now
preserves successful truth/None checks without executing the expression again.
Two failing refusal regressions now pass alongside ignored/unrelated controls;
329 affected tests pass in `continuation-presence-narrowing-quality`. The original
caller-tainted draft of the regression already passed and is preserved separately.
The real fixed-source trace now returns a non-None global configuration. Its
OAuth/PAT configuration merge still loses class identity and produces incidental
candidates; neither the named auth condition nor the deadline gate passes yet.

Six separate TypeScript class controls have been added for the recording path.
Three caller-to-method regressions currently fail; fixed-path/replacement/escape
controls pass. Their implementation remains open and their test file is retained
as deliberate uncommitted work, separate from this Python/Semgrep checkpoint.

### Reachable member state and evaluated assignment receivers

The real fixed auth trace passed 52,051 member bindings through 251 helper calls;
even scalar masking helpers received 185–273 members. Helpers now receive the
members reachable from actual arguments, closures and bound receivers, plus
changed global state. Reading one global loads that object's fields instead of
all global dictionaries. Unchanged global data loads when used. The same trace
now passes 6,872 member bindings, retaining all 251 calls, four raw credential
candidates and 87 warnings. This is bounded source interpretation, not auth proof.

Two additional callback tests reproduced a pre-existing global-assignment miss
on both the new source and the trusted `156ee17` PathFlow implementation. The
assignment receiver had been evaluated correctly and then discarded; binding the
write used an unknown receiver instead. The actual receiver is now retained for
the write without evaluating it again. Both global and closure callback tests pass.
`continuation-reachable-global-bound-quality` passes 331 affected tests in 55.83s;
focused type/style/format checks pass. Before the subsequent global-load and
receiver changes, the broader intermediate run passed 527 tests in 316.91s.

`auth-lazy-global-stage-costs/` still times out: Semgrep 28.27s, containment 25.96s,
URL 30.83s and credential analysis interrupted at 29.43s. Earlier partial state
reduction, failed callback tests, prior-source comparison, diagnostic import/type
failures and corrected runs are all retained. Those timings overlapped focused
checks and are not isolated throughput. The final receiver change still requires
native auth remeasurement. Technical acceptance, the fresh holdout and the
separate TypeScript class implementation remain unfinished.

### First complete native auth pair after state corrections

Internal flow values now use dataclass slots. Identical Python source-limit
warnings are constructed once per rule/file/line/reason, matching the final
warning identity; coverage no longer repeats the same limitation for every helper
encounter. This does not count or remove rule visits, paths or findings. A durable
before-failing regression retains both tool findings and one shared source reason.
`auth-warning-equivalence.json` compares the old and new warning methods on the
same fixed auth trace: 87 encounters become 55 distinct warnings, with identical
warning keys and raw matches. The affected suite passes 332 tests; type/style/
format checks pass. The slot-only and concurrently checked repeats still timed out.

`auth-quiet-pair-continuation/` then completed both original full auth inputs using
the production rules-only pipeline without concurrent agent test/profile jobs.
Vulnerable: 95 findings and 117.296s total wall time. Fixed: 94 findings, 118.387s
static duration and 122.299s total wall time including reporting. The configured
120-second static deadline is unchanged; completion is recorded by the native
pipeline. All incomplete earlier runs remain retained. This is a source-specific
pair, not the final repeated benchmark or an isolated-machine throughput claim.

Each report contains four SENT-016 client candidates. Fixed candidates still merge
incidental per-user paths with the flag-gated global path and lose that distinction.
The named auth condition has not passed adjudication. Broader callback/enum/class
support, remaining families, all final checks and draft delivery remain open.

### Auth condition and TypeScript receiver continuation

`b5a565d` skips impossible Python conditional-expression branches (two failing
controls before the fix; 336 affected passes). `5ac300e` retains enforced literal
string choices through helpers, with ignored/unrelated/replaced checks and custom
equality controls. `7734643` separates assigned key presence from uncertainty in
the value (five before-failing controls; 350 affected passes). A four-input native
run at that source completed three inputs, with the original fixed input exceeding
120 seconds. Its successful fixed mutation still mixed spurious per-user and
guarded global paths. All those results remain retained in
`auth-assigned-fields-development/`; the preceding incorrect five-input selection
failed before measurement and is retained separately.

The root cause of the remaining mixed paths was reproducible across two tools:
member defaults created while inspecting the first tool made declared dataclass
fields optional during the second lifespan analysis. `34220b7` establishes those
declared slots at construction/replacement. The regression fails only on the
second tool before the fix and passes afterward. All registered auth-tool traces
then retain `ALLOW_GLOBAL_CRED_FALLBACK`; 425 affected regressions and type/style
checks pass.

`auth-fixed342-development/` measures an immutable detached checkout at `34220b7`.
All four inputs complete through the native rules-only pipeline, with native JSON
and SARIF validation. Total wall durations are 112.408s, 120.065s, 121.641s and
117.430s; reporting follows the unchanged 120-second static deadline. The separate
condition adjudication records two vulnerable condition hits and zero
fixed-condition alerts, with all eight fixed nondefault candidates qualified and
the changed credential source context identified. There is no safe input in this
historical family. This is implementation-agent source review, not human
acceptance, runtime proof, fresh holdout or the final repeated benchmark.

The TypeScript continuation interprets included plain classes, actual instance
and static receivers, constructor fields, helper updates and branch-local member
state. Replacement, computed writes, deletion and unresolved escapes invalidate
inferred behavior. Arrow and ordinary function receivers remain distinct. A
constructor side-effect regression exposed three evaluations of one receiver;
the shared callee/argument cache now lasts only for one call and covers all four
flow rules. Reconstructing the earlier class implementation from its retained
patch reproduces six rule-delegation failures; all eight controls pass afterward.
The complete affected suite passes 366 tests. Its first run overlapped formatting;
`typescript-class-format-equivalence.json` verifies identical ASTs for all five
changed scanner files and the test, preserving both exact byte versions.

`continuation-mobile-class-selected-flow` reaches the actual
`src/mobilecli.ts` spawn with caller-derived arguments. Earlier diagnostics omitted
the selected flow argument and are retained as diagnostics, not evidence of no
class support. Ordered argv and executable/output semantics are still required
before claiming mobile recording detection. Other unmet families, final audits,
measurements, evidence packaging and consolidated draft delivery remain open.


### Ordered TypeScript arguments and mobile recording continuation

After `9f0e777`, shared array state retains aliases, helper appends, branch layouts
and independent slice copies. SENT-014 consumes evaluated values through both
Node process and simple-git calls. Before-failing controls cover missed variable
argv, computed writes through an alias, escaped arrays and short-circuit effects.
The argument-state change initially lost normalized collection facts; the retained
broad failure has 381 passes and one containment failure. Reusing the shared
combination logic fixes it; the subsequent broad run passes 399 tests.
Additional short-circuit checks reproduce three failures in rule overrides and
pass after correcting evaluation order (287 affected passes). The later focused
run passes 217 tests, with strict mypy, Ruff and formatting checks. An additional
before-failing executable-array control prevents a container containing a command
name from becoming an executable identity; its targeted rerun is retained.

SENT-012 recognizes only the source-selected mobilecli screenrecord output
contract at genuine Node child-process calls, with explicit executable
qualification and unresolved option warnings. Array limits are 32 layouts of
256 positions. Unknown/repeated options, computed mutation and escapes cannot
establish ordering. The same-path optional-guard controls reproduce the fixed
repository's conditional check followed by `output || temporaryPath`, preserving
lexical protection without inventing physical containment. The real fixed trace
now labels both screenshot and recording candidates as physical gaps, outside the
frozen non-symlink-parent condition. The actual vulnerable trace reaches recording
with and without the optional time-limit flag. These are source traces; no mobile
target/toolchain was executed. The native five-input rerun is the next check.

Commands and all failures remain expanded in the integration directory for the
next numbered evidence seal. Current source is not final technical acceptance;
other families, final audits, complete measurements and draft delivery remain open.


At committed `b51aee1`, `mobile-recording-b51-development/` completes all five
exposed Phase 20 mobile inputs under the unchanged deadline with native/SARIF
validation. The source adjudication records two vulnerable condition hits, each
with screenshot and recording paths, and zero fixed/control condition alerts.
All five reports have five findings: one new recording candidate per input and
unchanged content for every earlier candidate. The three fixed/control recording
candidates explicitly concern physical containment, outside the frozen condition.
Six physical-gap candidates and fifteen unchanged unrelated candidates remain
separate. The campaign took 245.94s overall; no target or model was executed.
Batch 11 seals 170 files with full hash readback. This completes a development
recording check, not final repeated benchmarks or Phase 22 technical acceptance.


### Shared HTTP clients and the remaining Meta boundary

After `761b9c2`, HTTP client construction/identity moves into the existing Python
flow state, shared by URL and credential rules. Per-request credentials on the
supported httpx/requests/aiohttp clients are recognized; unknown escape and method
replacement invalidate both rules' assumptions. Twelve of sixteen controls fail
before this change; all sixteen pass afterward. Receiver delegation controls then
expose repeated factory interpretation in the shared flow and rule overrides.
A cache scoped to one call preserves the actual receiver through delegation and
callee lookup. Positional request effects now occur before credential keywords;
two before-failing controls replace the credential through that argument flow.
All 390 affected tests pass, along with strict mypy, Ruff and formatting.

The first receiver test used HTTP routes for rules that do not analyze those
entries; its correction still lacked command syntax for SENT-014's intentional
precheck. Both diagnostic/test mistakes and a reserved pytest parameter-name
failure remain retained. The final fixture includes a supported inert command
syntax and verifies each receiver invocation separately. A failed source-edit
anchor left one intermediate rerun unchanged; that failure is retained too.

The Meta fallback snapshots inspected here are approved Phase 22 DEVELOPMENT,
not historical Phase 20: `continuation-meta-development-source-identity` verifies
106 vulnerable and 108 fixed projected files against the frozen manifest.
The first identity diagnostic selected zero inputs from the wrong manifest and
establishes nothing. The corrected selected-only check asserts two development
inputs; no fresh holdout source is inspected.

`continuation-meta-fallback-launches-trace` finds 41 tools, no HTTP entries and two
explicit unresolved launches. The selected tool reaches make_api_request directly;
its included meta_api_tool decorator is not yet interpreted. Consequently the
operator fallback/context and middleware enforcement are not established, and
there are zero SENT-016 matches in this diagnostic. Source-established decorator,
launch/middleware and ContextVar flow remain required. These shared client tests
do not pass that condition or replace the remaining native measurements.


### Source-defined tool decorators and captured state

The continuation after `7ab3214` records the exact registration decorator while
preserving its existing source location. Entry analysis applies the inner
source-defined decorators and invokes their returned callable; outer decorators
do not change the callable already registered. Named nested functions retain
individual closure state. Genuine default functools.wraps preserves behavior;
unresolved decoration does not establish it. Three original decorator controls
fail before the change; all nine forwarding, substitution, non-invocation,
replacement, registration-order and factory-isolation controls pass afterward.
The broad affected suite passes 399 tests with strict mypy and final Ruff/format
checks. The first implementation tried to use the historical FunctionDef location
as the decorator identity, and then needed named closure capture; both intermediate
failures and diagnostic import/line-number mistakes remain retained.

The real Meta DEVELOPMENT trace now reaches get_current_access_token and carries
operator credential provenance into get_ad_accounts and make_api_request through
the included wrapper. It still reports no HTTP handler and two unresolved
launches, so it correctly has no established HTTP caller fallback finding yet.
The actual source-selected launch, middleware association, ContextVar state and
fixed middleware rejection remain unfinished. This progress is not a condition
hit, native development measurement, reviewed evaluation or final technical gate.

### Request-local Python context variables

The continuation after `10cc14c` follows genuine ContextVar allocation identity,
declared/per-read defaults, set values and matching single-use reset tokens using
the shared flow's existing environment/merge mechanism. Helpers carry this state;
separate handler entries do not inherit a previous request. Invalid, escaped,
replaced or potentially reused operations remain unresolved. Manual context
switching and spawned tasks are not modeled. Known scalar literal truth now stops
unreachable fallback expressions without invoking custom target truth methods.

The first credential fixtures omitted a checked absent caller credential in most
cases; their failures do not establish the intended SENT-016 boundary. Corrected
fixtures exposed the literal-truth gap, and the corrected context controls pass.
The broad affected suite passes 410 tests in 60.49 seconds. Subsequent token-escape
hardening passes 130 credential/HTTP tests in 44.06 seconds, strict mypy across 142
source files, Ruff and formatting. All intermediate failures, including a mypy
local-variable name collision and formatting, are retained in
`continuation-context-variable-*`. This is bounded shared-flow support, not proof
of the Meta middleware attachment or final independent condition. Those source
relationships and the complete final gates remain open.

### Atlassian request destinations and unresolved middleware state

After `49f36ce`, shared client identity records genuine Jira/Confluence base URLs
and requests sessions. SENT-015 emits at supported REST requests and Jira myself,
not construction. Current URL values, relative/absolute path selection, guarded
destinations, known sessions and replaced/escaped implementations have durable
controls. Request argument effects precede the SDK's session/base-URL lookup.
The corrected initial tests fail four cases before implementation; 444 affected
tests pass after the first implementation. Final request-path/delegation controls
pass all 114 URL tests, with strict mypy, Ruff and formatting. The first fixture's
indentation error, intermediate style failures and all source traces are retained.

All four original historical Atlassian SSRF/upload source trees were compared
byte-for-byte with Phase 20's validated inventories. The vulnerable Jira trace
now finds requests at client.py:184 and users.py:62 with the HTTP request origin.
The fixed trace also alerts: the real destination validation is in attached ASGI
middleware, whose state is not yet connected to get_http_request. These are
diagnostics, not a native pair measurement or a passing fixed-condition gate.
The mistaken first diagnostic selected an invented prefixed tool name and failed;
the corrected trace selects the source-established get_issue handler. Historical
Phase 20 held-out inputs are already exposed; fresh Phase 22 holdout source has
not been used for this work. Middleware association/state and upload conditions
remain required work.

### Shared HTTP getter identity

After `43f5c96`, repeated genuine FastMCP get_http_request calls share request/state
identity within each tool entry. Included helpers retain state writes and their
validation facts; replacement writes lose the earlier protection, and separate
tool entries remain isolated. The first proposed regression used an unrelated
FastAPI route, which does not establish FastMCP's request context; that fixture
and its failure are retained without a support claim. The corrected FastMCP tool
regression fails before the fix. Caching the request alone was insufficient until
its state relationship became reachable by the existing helper-state traversal.
All five new controls and the 454-test affected suite pass (57.45 seconds), with
strict mypy and Ruff. The source change does not attach ASGI middleware or close
the independent Atlassian/Meta conditions. Its evidence follows sealed batch 12.

### Source-established ASGI middleware and request state

The continuation after `1352a9e` connects source-bound FastMCP HTTP application
overrides, explicit Starlette middleware sequences, included ASGI constructors
and ordered continuations to the tool's genuine HTTP request. Mounted application
ownership, SDK subclass methods, request/state aliases, known dictionary keys,
fresh empty mapping defaults and optional URL guard facts use the existing
source interpreter. Mapped IPv4 checks retain the original URL identity.
Replaced/escaped applications, unknown callbacks, unrelated applications and
reordered validation/overwrite controls remain conservative. A separate path
without an HTTP request preserves stdio sinks, including calls preceding the
getter. This does not implement dynamic provider patches or BaseHTTPMiddleware
dispatch, close the Meta condition, or execute target code.

The first broad run found an unsafe optional-member protection propagation;
its retained result is 601 passes and one failure. The shared helper now propagates
unconditional facts only from definitely present values. The corrected affected
suite passes 606 tests in 65.79 seconds; strict mypy passes 124 source/test files,
and Ruff/formatting pass. Membership, empty-default, mapped-IP, middleware-state,
callback and alias failures and all intermediate diagnostic scripts remain in
`continuation-http-*`, `continuation-mapping-*`, `continuation-optional-map-*`
and the earlier per-change logs. The first membership negative control used a
literal URL rather than caller data; the corrected control uses a second input.

The selected real fixed Atlassian `get_issue` trace now has zero SENT-015 matches;
its profile retains 264 unresolved diagnostics. This is one handler, not whole-input
completion or a native benchmark pass. Profiling exposes repeated application
metadata scans; performance work and native vulnerable/fixed measurements remain
required under the unchanged 120-second input limit. All post-batch-12 evidence
is retained locally and awaits the next numbered seal. Final evaluation, remaining
families, review compatibility, hosted gates and consolidated delivery stay open.

The corresponding vulnerable profile retains both Jira requests (client.py:184
and users.py:62), with 251 unresolved diagnostics. Both profiles exit zero;
instrumentation and overlapping verification make them diagnostic evidence,
not isolated throughput measurements.

The following metadata correction caches only immutable mount relationships and
source-established application-method eligibility. It reuses the existing launch
instance resolver and keeps fresh request execution/state for each tool. A repeated
fixed-handler profile resolves application eligibility once across two entries,
retains zero matches and 264 distinct diagnostics. All 314 lifespan/URL/credential
controls pass in 47.13 seconds; strict mypy checks 143 source/test/script files,
and Ruff/formatting pass. This removes repeated AST scans, not the input deadline.

### Nested source decorators

After `a25c864`, the upload trace identified an included error-handling decorator
on the write-access wrapper. The original shared interpreter rejected that nested
decorated callable and never reached the upload handler. A durable forwarding/
replacement pair reproduces the miss before the correction. Registered and nested
functions now share explicit decorator evaluation/application, retaining genuine
wraps metadata and unresolved unknown replacements. A source-order control also
exposed the source-name-only recursion check: two distinct closures from the same
factory were incorrectly treated as recursive. Callable allocation identity now
distinguishes them while retaining the 64-frame limit.

The corrected affected suite passes 610 tests in 70.19 seconds. The real upload
trace reaches upload_attachment and get_confluence_fetcher, but the returned
fetcher remains unresolved and there is no condition hit yet. The ongoing native
measurement uses the immutable earlier `3a2a276` checkout; it cannot verify this
later decorator correction. Raw failures, source-order controls, traces and type
annotation correction remain under `continuation-nested-decorator-*` and
`continuation-upload-nested-decorator-*`, after sealed batch 13.

### HTTP request caches and upload service identity

The next containment regression reproduces a service-return miss caused by an
unknown cached request object. SENT-012 now consumes the same source-established
HTTP middleware state as the URL/credential rules, with its separate stdio path
retained. A second regression reproduces the genuine Starlette state `setattr`
being treated as an unknown escape of the assigned fetcher. Known-field builtin
writes now use the actual shared state member, including source-resolved field
names. Middleware validation/overwrite order has both direct and setattr controls.

The selected real Confluence upload handler reaches open on the HTTP path in the
vulnerable source; the fixed source reaches the same read through validate_safe_path
with no match. A prior trace reached the sink only through stdio and is explicitly
not an HTTP condition hit. These are source traces, not native completion or
runtime exploitation. All 616 affected regressions pass in 64.10 seconds, with
strict mypy across 143 files. Style failures and their string-layout corrections
are retained after batch 13; final whole-input performance remains open.

The earlier immutable `3a2a276` native measurement is finished: **4/9 completed**.
The four historical SSRF originals/mutations finish in 88,007, 89,263, 94,345 and
96,120 ms. Both vulnerable variants retain the two initial Jira request candidates;
both fixed variants omit those candidates. A third permission-search URL candidate
remains in all four reports and requires separate source adjudication before a
fixed-condition gate can be claimed. All five historical upload inputs (including
the download safe control) exceed the unchanged 120-second timeout and produce
incomplete outcomes, not native reports. The harness exits zero after recording
these failures. Exact configurations/outcomes/reports are in
`atlassian-asgi-3a2-development/`, with driver/source identity in
`continuation-atlassian-asgi-nine-native.*`. The fixed checkout remains unchanged;
it does not measure the later decorator or cache-state corrections.

### Alternative service instances and checked URL paths

The remaining fixed permission-search candidate came from merging distinct
source-constructed service instances without their actual configuration fields,
then dropping validated authority facts when appending a literal URL path.
The shared interpreter now retains bounded same-class alternatives and live member
aliases; writes weakly update possible receivers. Required constructed fields stay
present when their receiver exists, while nullable receivers, field deletion and
unknown mutation retain caller defaults. Rejecting a disjunction of missing
parent/child values now establishes both surviving values' presence.

SENT-015 retains checks when a validated base gets a literal path delimiter;
unrestricted host suffixes, replaced prefixes and altered formatting remain
candidates. The real fixed get_user_profile trace now reaches the permission-search
request with scheme/literal-IP checks and no match. This is source-specific trace
evidence, not a new whole-input result or a DNS-rebinding claim. The earlier 3a2a276
native reports remain unchanged. The upload profile at af67e21 still reaches the
120-second deadline; it identifies repeated helper/state work for optimization.

Verification: 550 affected regressions pass in 55.45 seconds, plus 79 shared
state/execution tests in 9.50 seconds; strict mypy checks 143 files and Ruff/format
checks pass. The initial nonexistent test paths, missing literal helper, field
removal failures and type-name collisions are retained with their corrections in
continuation-service-*, continuation-checked-url-path-* and
continuation-ssrf-checked-path-source.*. Evidence after batch 13 awaits sealing;
native completion, all final measurements and remaining authorized scope stay open.

### Measured startup and helper traversal cost

The unprofiled 18e385f upload input remains incomplete at 120,110 ms. The next
shared optimization propagates helper guard facts in one environment pass
(`247f960`; 629 affected tests). Instrumented native measurement still times out:
SENT-012 takes 51.081 seconds, including 180 lifespan calls totaling 9.812 seconds.

`d4228fe` reuses bounded startup records and prepared HTTP state with separate
handler environments. Callable/workbook/argument-tuple state is excluded from
reuse, and explicit launch states bypass it. Mutation and launch controls pass;
339 URL/lifespan/credential tests and 292 shared tests pass, with the corrected
startup control separately rerun. Native instrumentation confirms one lifespan
call per rule, SENT-012 at 36.972 seconds, but the input still times out.

A single-handler line profile identifies repeated traversal of scalar leaves.
Its inclusive nested times must not be summed or treated as native throughput.
`7daa9c6` skips leaves without members, aliases, tuples, closures, receivers or
unknown member state. All 631 affected regressions pass in 64.27 seconds, with
strict mypy across 143 files and style/format checks. Native instrumentation
records SENT-012 at 32.108 seconds and SENT-015 at 40.378 seconds; SENT-016 remains
unfinished at the 120-second limit. These failures stay in the post-batch-14
command records. Native completion and the final gates remain open.

### Historical request identity and replay compatibility

The current production request builder reproduces all 35 requests in the frozen
Phase 20 completion-v2 preparation exactly. Their captures pass the actual checked
ledger/hash transport and response validator with zero model calls. The first
diagnostic looked only in the original capture directory, found 17 captures and
incorrectly marked the other 18 requests changed. The corrected diagnostic also
uses completion-v2 captures and retains both results. See
`historical-request-compatibility-v2.json` and the archived command scripts.

This verifies historical prepared requests and capture compatibility only. It
does not rebuild current detector candidates or their source blocks, establish
current reviewed retention, or identify the final replacement set. Those gates
remain open until final offline scans and exact request preparation finish.

### Semgrep subprocess working directory

The worker experiment passes 47 regressions but does not remove the upload timeout;
it is reverted. Semgrep timing isolates about 26 seconds of subprocess work versus
0.66 seconds of rule scanning on 312 selected files. The pinned 1.176.0 source
explains the cost: explicit files outside the child process's CWD each require a
core target-discovery subprocess. Project-root/novcs flags do not remove it.

Launching Semgrep with the already validated scan root as CWD reduces the isolated
measurement to 2.56 seconds. A repeated comparison preserves all 312 selected paths
and all 35 canonical rule/location/snippet/capture records. The initial comparison
also included Semgrep's CWD-dependent internal check_id prefix and failed; that
prefix is not Sentinel's canonical rule ID or Finding identity. Both comparisons
are retained. A paired absolute/relative/escaping-path regression exposes and fixes
relative result resolution against the new subprocess CWD; scope rejection stays
enforced. All 56 engine/TypeScript/workspace regressions and five adapter controls
pass. Final native input completion has not yet been measured at this correction.

### Handoff-v2 continuation: verified state and middleware/local imports

The continuation verified clean `020cde82dbe39d49f79187a3bfbac20d5f70f3e3`,
all retained worktrees, no other active writer, and the exact corpus, Git
packet and both handoff archive hashes. The installed approved Git image still
has its recorded identity (`v2-git-image-identity`, Linux arm64). No paid calls,
pushes, draft creation, publication or external contact occurred.

`v2-upload-family-020cde8` measures all five upload inputs on unchanged scanner
source: **0/5 complete**, each exceeding the unchanged 120-second deadline.
The harness exits zero after recording the failures. Its initial tracked patch
is empty; only new regression tests were edited while it ran. Brief focused
counterexample checks overlapped later inputs; the first timeout preceded those
checks. This is completion evidence, not an isolated throughput benchmark, and
does not erase the older fixed-input completion.

`f3fab7d` adds attached genuine BaseHTTPMiddleware dispatch, request/ContextVar
propagation and explicit continuation/refusal. Custom call/construction hooks,
replaced/escaped middleware and unknown forwarding cannot establish protection.
Unknown forwarding now traverses closure captures as well as receiver state.
`2b45b10` resolves included function-local imports before same-named globals.
These are shared prerequisites, **not a completed Meta condition**: actual SDK
launch/provider patches and module replacement remain unfinished.

The two original safe middleware misses, callback-escape and class-mutation
failures, the missing credential condition and local-import failures were
reproduced before correction. The combined affected suite passed **673 tests in
56.80 seconds**. Strict mypy initially caught a local variable type collision;
its correction passed mypy and 36 discovery tests. Ruff and formatting checks
passed. Scratch adapter diagnostics include retained parent-index and test-config
failures; they are not native scanner measurements.

`1840f13` reuses immutable lexical shadow lookups and one empty URL-merge default.
Profiling identified 28,571 empty allocations in URL merging for one warm upload
handler; the change reduces that component to 859 and total empty allocations
from 60,310 to 32,598. Three boundary flows on the production upload handler have
byte-identical complete matches/warnings before and after (`v2-flow-default-equivalence`,
SHA-256 `a84ad26f04feaa93a9fea16e7920307c036ca8972463722a30a452f8a06a06a4`).
501 affected tests pass, plus nine source/deadline checks and corrected strict
mypy. These focused profiles are not whole-input acceptance. The first warm
profile's unique-handler assertion failed because local imports now recover
additional explicit test registrations; the corrected diagnostic selects the
production registration without excluding source from native scans.

A new five-input native run uses the immutable detached
`/private/tmp/mcp-phase22-verify-v2-perf` at `1840f13`; its source and imports are
checked by `v2-upload-family-1840f13`. It finished with 3/5 completed inputs:
vulnerable 117544ms, vulnerable mutation 119078ms, fixed 123515ms total wall time
(static processing remained within the unchanged 120-second deadline). Fixed
mutation and download safe control timed out at 120134ms and 120183ms. Later
inputs overlapped independent verification; these are completion observations,
not isolated throughput measurements. Condition adjudication remains open. Final repeats, holdout,
adjudication, review/campaign/report audits, all final quality/hosted checks,
paid-request preparation and consolidated draft delivery remain open. The full
86-row requirement map remains authoritative; no phase gate is marked complete.


`0d3f9a3` retains source module identity, explicit callback replacements, saved
callbacks and function-local import timing. Unknown escape, reflection and
deletion do not restore the original callable. Actual Meta vulnerable/fixed
`setup_http_auth_patching` source traces establish the three assignments in auth,
api and authentication; they do not establish HTTP attachment or the named
credential condition (`v2-meta-source-module-patch`). 552 affected tests pass
(`v2-module-delete-fixed-shared`), strict mypy and Ruff pass. Retained failures
include the original 6/12 replacement misses, 4 unknown-mutation failures, the
reflection and deletion counterexamples, an initial type error and a nonexistent
test filename; corrected runs do not erase them. SDK launch/provider attachment
and the later same-name middleware implementation still need integration.

`6da955e` reuses frozen empty Value objects in the shared path/URL hot paths.
632 affected tests, mypy and Ruff pass (`v2-immutable-shared-corrected`,
`v2-immutable-types`, `v2-immutable-lint`). The actual production upload handler
retains byte-identical matches/warnings in all three flows before/after the change
(`v2-flow-immutable-equivalence`, SHA-256
`a84ad26f04feaa93a9fea16e7920307c036ca8972463722a30a452f8a06a06a4`).
Comparable warm component profiles record 29,200 versus 14,526 Value allocations
and 0.644 versus 0.627 profiled seconds; these are not isolated native throughput.
A mistaken diagnostic output directory failed safely without overwriting prior
evidence; the corrected comparison and missing-test-path attempts are retained.

`a035585` resolves unobserved module-level no-op forward declarations to the later
unconditional undecorated implementation, retaining ambiguity for eager captures.
The original two resolution failures and three safe controls precede the fix.
489 shared tests and corrected strict mypy pass. Actual Meta source resolves the
final middleware implementation at vulnerable line 281/fixed line 303 while
preserving all three token provider replacements (`v2-meta-forward-source`).
This does not yet establish SDK launch/provider/middleware attachment.

Evidence batch 15 seals completed post-v14 diagnostics through `a035585`, including
the supplied v2 handoff/supplemental snapshot and all retained new failures. The
ongoing `v2-upload-family-6da955e` run is excluded until it finishes. Its detached
verification worktree is `/private/tmp/mcp-phase22-verify-v2-immutable`; independent
focused tests overlap this run, so latency is not isolated throughput. Final
measurements, audits, paid preparation, consolidated draft and acceptance remain
open; the 86 requirements are not reduced by these intermediate commits.

### V2 source continuation through `f58d7d1` (not final acceptance)

`53c68be` preserves bounded list/tuple allocation, append and iteration through
aliases and helpers. The corrected shared run passed 637 tests, with 103 later
state controls; original failures and corrected unsupported cases remain retained.
`a2940e2` interprets genuine MCP 1.29 startup/provider relationships, attached
middleware, saved callbacks, source-selected JSON-response branches and unset
HTTP ContextVar fallback. The corrected shared run passed 794 tests. This is
bounded source interpretation, not SDK/target execution or a native condition gate.
`ca8efa1` preserves source launch alternatives and source locations through finding
merge; 309 affected tests and corrected style/types pass.

The completed `v2-upload-family-6da955e` native run reports four completed inputs:
vulnerable 96,076 ms, vulnerable mutation 110,242 ms, fixed 107,291 ms, fixed mutation
107,886 ms. The safe download control timed out at 120,184 ms. These elapsed values
overlap focused verification and are not isolated throughput. Counts are 98/98/96/96;
source-condition adjudication and final integrated repetitions remain open.

Both fixed-source Meta runs, `v2-meta-sdk-a2940e2` and `v2-meta-sdk-d2ba110`, report
**0/5 completed** at the unchanged 120-second deadline. Harness exits were zero;
per-input results explicitly remain incomplete. `d2ba110` narrows immutable source
reachability checks. `f58d7d1` caches middleware class validation using original
source functions and attached registrations, retaining deadline and newly reachable
mutation controls. The source-cache check passed 123 SDK/middleware tests; the prior
cache draft passed 364 shared tests. Sampled Meta account-handler outputs for all
three shared flows remain byte-identical, SHA-256
`4a4c578b1686f61323d616371cd768425cb0dcc061da19989fb139081509804e`.
Warm profiles and cache diagnostics are component evidence with overlapping work,
not native completion. The first cache draft did not reuse entries because its key
included generated adapters; the original-source key corrects that measured issue.

`16a0da6` follows Express factory routes through included helpers and callback
closures. Corrected vulnerable/guard/replacement controls pass, with 665 affected
tests and strict types/style. Initial diagnostics failed target validation before
reaching the detector; the corrected counterexample reproduces the actual miss on
the preserved pre-change source. Middleware chains and client configurations remain
separate unfinished TypeScript requirements.

`meta-fixed-label-review-v1/` records a source-level conflict with the frozen Meta
fixed label: the alternate SSE-response configuration selects a different patched
provider from the Streamable HTTP application actually served. A source-only
absent-header witness and installed-SDK source identities are retained. No runtime
exploit or final native acceptance is claimed. The user's choice of a versioned
erratum/configuration amendment remains pending; frozen labels, prerequisites and
gates have not been changed. Unrelated fixed candidates still require separate
adjudication. Independent technical work continues while that decision is pending.

The safe-upload rerun and selected-startup-path regression are subsequent work in
progress. The first isolated-control driver used an incorrect record field and
failed before measurement; its corrected command is separate. Full benchmarks,
fresh holdout, consumer/compatibility audits, final quality, paid preparation and
consolidated draft delivery remain unfinished. There have been no paid calls,
pushes, hosted runs, new drafts, merges or outreach.

`v2-upload-safe-6da955e-isolated-corrected` completes the remaining safe control in
99,783 ms with 96 findings. All five upload-family inputs now have completed native
reports at `6da955e`, across the four-completed original run and separate retry.
`v2-upload-6da955e-adjudication/condition-adjudication.json` uses the existing frozen
input validator and condition scorer: two vulnerable Confluence upload condition
hits, zero fixed/safe condition alerts. The mutation's imported identity helper is
source-reviewed separately; native evidence cites its call but not its body.
Two separate page-content read candidates remain policy-uncertain. Other rules and
the historical 70-warning backlog are not adjudicated by this packet. No separate
Jira detection or HTTP runtime proof is claimed. The safe retry had no other native
scan/profile, but a short regression ran during harness startup; timings are not a
general isolated-throughput guarantee. The earlier timeout and failed driver remain.

`0eb39b5` constrains plain SDK startup branches to the selected launch and excludes
unconditionally terminating prefixes. Eight source-path controls preserve caught
exceptions, conditional returns and separate HTTP/stdio launches; 702 affected tests
and strict types/style pass. A source-specific one-input Meta native run follows;
completion remains open until its per-input outcome is inspected. Future final
repeats must use the integrated candidate, not substitute these older reports.

The first Meta input at `0eb39b5` remains incomplete at 120,041 ms. The subsequent
instrumented full source scan confirms the remaining cost: SENT-012 processes 41
handlers in 40.58 s, SENT-015 processes 41 in 50.07 s, and SENT-016 reaches 19 before
the shared 120 s deadline. This diagnostic is not a completed native report. Reusing
startup analysis requires preserving independent handler and callback state; that
implementation/performance work remains open.

### V2 continuation through c6234a0: grouped startup, TS middleware and evidence

`cb9e4e3` groups SDK startup work while copying private state per handler. A
command-rule regression exposed its bypass of the existing command-sink precheck;
`f2ea709` restores that precheck. Preserve both failures and corrected checks.
At immutable `f2ea709`, the first Meta vulnerable input completed in 119,405 ms
with 49 findings. This establishes completion of one input, not condition scoring
or the five-input family gate. Its full suite passed 1,775 tests, 36 skipped,
89.11% branch coverage in 1,080.75 s (`v2-full-suite-f2ea709/coverage.sqlite` and
`v2-full-suite-f2ea709.*`). This intermediate pass does not cover later edits.

`0491f32` interprets source-established Express module/factory middleware in order,
following real `next()` calls through included helpers, literal mount prefixes and
bounded callback arrays. Independent route state prevents cross-request mutation.
Unknown prefixes/callbacks and replaced receivers do not establish protection.
Repeated callback registration has its own counterexample and fix; recursive
source helpers remain bounded, with at most 32 synchronous HTTP continuations.
The initial 24 controls had 12 failures; scope controls found unknown-prefix and
array failures. After fixes, 48 focused controls and the repeated-callback test
pass; the broader TypeScript selection passes 292 tests, 470 deselected, in
209.98 s. Strict mypy and Ruff pass after retained initial type/style failures.
The first repeated-callback test omitted its MCP dependency and failed before
analysis; the corrected counterexample and actual fix are separate retained runs.

`c6234a0` preserves the return-line source anchor for caller-derived helper values
in Python and TypeScript. Both missing-anchor counterexamples failed before the
change. All 49 context/review tests pass, including exact references and the
160-unique-source-line bound. Four loopback socket tests initially failed under
the sandbox; the authorized local-loopback rerun passed, without model calls.
Ruff and strict mypy pass. This metadata change still needs the final integrated
benchmark/request compatibility and broader source-evidence audit.

All five Meta development inputs are now being measured at immutable `c6234a0`;
no outcome is assumed before the records finish. The frozen fixed-label decision
remains pending. No held-out source has been inspected, and no paid calls, pushes,
hosted jobs, draft creation, publication or outreach occurred in this continuation.
Full authorized scope, final repeats, all unrelated-candidate adjudication,
compatibility/consumer audits, Git campaigns, paid preparation, quality and draft
delivery remain open.

The `c6234a0` Meta family run finished with **0/5 completed**: vulnerable 120057 ms,
vulnerable mutation 120046 ms, fixed 120065 ms, fixed mutation 120038 ms and safe
120038 ms. Every failure is the actual unchanged 120-second static deadline;
the harness returned zero while retaining these incomplete input states. Short
module-branch regressions overlapped this development run, so it is not an
isolated-throughput measurement. It does not supersede the one completed f2ea709
report or establish any condition gate.

`dc5c784` fixes module-level conditional Express registration, separates MCP and
HTTP interpretation of a mixed factory, and connects source-resolved route names
and imported handlers to coverage inventory. Two module-branch counterexamples
and seven mixed-factory/inventory counterexamples failed before their respective
fixes. The combined 43 controls pass, as do strict types and lint. Broader updated
inventory/consumer verification remains required.

`59e9fc5` reuses the existing immutable empty Value in credential analysis. On the
same source-only Meta helper, counted Value allocations fall from 63592 to 53993;
complete match/warning/visit state remains byte-identical with SHA-256
`c1f8504c6ef4068eebd2b6901a90b209673bf06c420def4f6128666879c0bdd7`.
These diagnostic profile timings do not establish an isolated native speedup;
new native measurements remain necessary. All default values remain immutable,
and no rule/deadline/source exclusion was introduced.

### Post-v17 verification and context/hash corrections

At immutable `59e9fc5`, the original Meta vulnerable input completes in 119908 ms
with 49 findings; native JSON/SARIF validate. Its four remaining development
inputs all time out: vulnerable mutation 120050 ms, fixed 120071 ms, fixed mutation
120043 ms and safe 120041 ms. These four ran without concurrent tests/profiles.
The harness returns zero but only 1/5 inputs completed across the two directories.
The complete family/condition and repeated final-source gates remain open.
`v2-defaults-regressions-59e9fc5` passes 513 credential, TypeScript, inventory and
context regressions in 182.58 s on that immutable checkout.

The real Meta POST candidate has 279 flow anchors. Its old context used 160 source
lines but omitted the credential-selection file. `b3b2318` distributes oversized
anchor selection across source files without increasing the total source budget;
all omitted anchors remain explicit. The new counterexample fails before the fix.
All 50 context/review tests pass, with strict types/lint. Before/after native-context
artifacts show auth.py:446 now included for the POST candidate, while the GET and
duplication context hashes remain unchanged; every context stays at 160 source
lines, and the POST still discloses 119 omitted anchors. This is request construction
only, with no model calls; compatible capture selection remains a final gate.

The bounded pure identity-hash cache prototype records 48382 hits and 2178 misses
(maximum 4096 entries), preserving complete helper analysis state SHA-256
`c1f8504c6ef4068eebd2b6901a90b209673bf06c420def4f6128666879c0bdd7`.
`6a3a4a2` applies the standard-library cache with no hash/identity algorithm change.
All 906 affected source-flow, credential, URL, command, TypeScript, inventory and
context tests pass in 158.10 s; strict mypy and lint pass. All five Meta development
inputs are being measured on immutable 6a3a4a2; no native outcome is assumed.

Read-only GitHub metadata confirms PR #36 remains an open draft at delivered
parent `phase22/description-poisoning`, head
`8b6b0ddf1d6f6cf5a8da3ab9421471865b801455`; it is an ancestor of integration.
No PR currently exists with head `phase22/integration`. Recheck at final delivery.
No push, draft creation, hosted jobs, paid calls, merge, publication or outreach
has occurred. Frozen labels and fresh holdout source remain untouched; the Meta
fixed-label decision is still pending. Authorized independent work remains open.

The immutable `6a3a4a2` Meta run completes two of five inputs: vulnerable 116315 ms
and vulnerable mutation 119602 ms, 49 findings each. Fixed, fixed mutation and safe
control time out at 120048, 120170 and 120056 ms. The 16384-entry cache experiment
is a separately captured diagnostic, not a committed scanner or acceptance result.
The fixed-source timing diagnostic retains all three rule costs and clone counts;
no rule was disabled and the deadline remains 120 seconds.

`v2-native-campaign-audit-6a3a4a2` passes 79 report, native migration, baseline,
campaign and repeated-proof tests in 9.54 s. This does not replace final Docker,
full-suite, consumer or benchmark gates. The in-progress TypeScript record change
has durable original misses, intermediate signature/type failures and a 781-pass,
four-failure broader run retained. Its returned-guard corrections subsequently
pass the affected guards; a distinct-helper-allocation counterexample is reproduced
and corrected. Final integrated source-flow verification remains pending.

`be6349d` preserves TypeScript plain-record aliases, field updates (including literal
string indexes), helper returns, branch alternatives and distinct helper allocation
sites. Fetch and source factory registration read current record fields. Unknown
mutation/prototype assignment invalidate protection. The original six client misses,
three branch misses, returned-guard regressions, allocation and bracket-access misses
and all intermediate signature/type/harness failures are retained. All 24 new client
cases pass. Combined with `ab0e13c`'s skipped discarded Python member defaults,
`v2-record-and-member-shared-corrected` passes 941 tests in 225.63 s. Strict mypy
checks 143 files and lint passes. The initial misspelled phase19 test-path command
ran no tests and remains explicitly failed.

Before/after member-default profiles preserve full RuleRunState SHA-256
`c1f8504c6ef4068eebd2b6901a90b209673bf06c420def4f6128666879c0bdd7`, reducing
value allocations from 53993 to 52129. The pure combine-cache prototype preserves
that same state, records 42795 hits/2392 misses (bounded to 4096), and reduces
allocations to 35744. Profile timings overlapped development checks and are not
isolated throughput claims. The actual cache change is under regression verification.
The larger identity-hash-cache prototype (16384) still times out on Meta fixed
at 120055 ms and was not adopted. Frozen labels/holdout source remain unchanged.

`d5e02e9` applies the bounded pure-combination cache; all 941 affected regressions
pass again (224.50 s), with types/lint. Its immutable five-input Meta run completes
0/5: fixed 120071 ms, vulnerable 120056, vulnerable mutation 120054, fixed mutation
120061 and safe 120057. The fixed input ran first; subsequent inputs overlapped
small development checks, so these are completion outcomes, not isolated throughput
comparisons. No deadline or detector was weakened. The full fixed-source SENT-016
CPU profile completed interpretation but its first driver failed report construction
on an invalid test UUID; all timing data and that failure are preserved. The corrected
uncached profile completes three SENT-016 findings and records full static-result
SHA-256 `70981a591a2c90eab76a1059d8321a39007cb89bbff3a0d6d6ef5adee70c6629`.
It is a selected-rule diagnostic, not the all-rule native condition gate. Of 107940
branch merges, 9094 have two identical states; full-state merging is a major measured
cost. No broader cache-performance or family-completion claim follows.

`50310e1` adds the two checked subprocess APIs to existing named Python helper
interpretation. Four original caller/shell misses fail before correction; literal,
rebound and no-shell controls pass. `b55a087` permits frozen Phase 22 offline request
preparation, checked replay and pinned local Semgrep comparison, retaining strict
source-only treatment/manifest checks and a separate Phase 22 capture ledger.
Tests forbid constructing a live transport. The original treatment rejection,
a missing dependency in the generated unit target, and its zero-candidate shell
miss are all retained (unit fixture output is labeled, not benchmark evidence).
All 239 execution/correctness/corpus/review checks pass in 231.55 s; mypy checks
143 files, Ruff passes and all 149 formatted files pass. `029f686` additionally
verifies current SDK factory metadata after configuration helpers (5 discovery
checks pass). No paid calls, holdout tuning, label changes, pushes or publication
occurred. The full authorized technical scope and external checkpoints remain open.


`4f2f81c` avoids recombining equivalent states. Its selected Meta SENT-016 result
matches the prior full findings, warnings, coverage and completion after the
established volatile-field normalization (SHA-256
`bfcb898ab84b44ad15c89dd26522c32c4f0a35159d88918a0f13d715d5ce8345`).
The first raw comparison failed on generated IDs/timing; original and corrected
comparison drivers are preserved. The cached all-rule fixed scan still times out
at 120073 ms; the separately uncached diagnostic timed out at 120202 ms.

`3ff455e` combines two abstract values directly. All 262144 exhaustive prior
cases plus 25000 seeded mixed-state cases match the prior implementation; all
942 affected regressions pass (242.54 s). The initial local type-variable name
collision is corrected and strict mypy/lint/format pass. The immutable 65ba622
five-input Meta run completes 0/5, at 120048/120044/120043/120051/120055 ms, with
fixed first. It overlaps a full historical diagnostic on immutable 4f2f81c, so it
is a completion result, not an isolated throughput comparison. Neither the
120-second deadline nor detector scope has changed.

The consumer audit found unsupported runtime schemas/local references could be
skipped while campaign enumeration remained complete. Five original misses are
retained. `65ba622` returns enumeration status with recovered attempts and keeps
the campaign incomplete on unsupported schemas. Seven schema controls include a
supported empty object and a supported property retained before a missing local
reference. All 158 campaign/argument/native/migration regressions pass (11.08 s).
`7371692` records actual campaign completion and full dynamic summary in newly
generated ablation cases, replacing an unconditional four-probes-executed claim.
The original absent-field regression is retained; 50 artifact/report checks pass
(4.34 s), using checked replay and a synthetic runtime result, with no live calls.
Historical generated artifacts remain unchanged.

`v2-consumer-audit-7371692/packet.json` links 18 exact source files and seven
passing check records. Native and SARIF use canonical ordered outcomes; console
lookup uses attempt IDs; legacy rule-keyed GPT priorities and four-probe migration
are distinguished from runtime scheduling. Full-source native/Docker/hosted
acceptance remains open. All 94 Action/configuration/workspace checks pass
(26.16 s), including repository campaign settings reaching orchestration.
Schema consistency, notices, offline retained-artifact validation, strict docs,
locked runtime requirement export, the dependency advisory audit (no known
vulnerabilities) and wheel/sdist build pass. Installed wheel checks are in progress;
the new module-location assertion correctly rejects a source-tree import in the
negative control. No paid calls, label changes, fresh-holdout inspection, push,
publication or outreach occurred. Evidence batch 19 is not yet sealed.


The installed distribution checks finish successfully: pip wheel, pip sdist,
pipx and uv, using temporary environments with PYTHONPATH removed and model
credentials withheld. Each installed module must resolve under its environment's
sys.prefix; the intentional source-import negative control fails that assertion.
The checks preserve packaged schemas/resources, TypeScript scans and Python/TS
rules-only scans with empty/dummy credentials. This local smoke is not a Linux
network-namespace isolation or hosted OS matrix result. The additional 104 core
containment regressions pass (1.23 s).


The full 4f2f81c historical diagnostic finishes 32/45 completed, with 13 static
timeouts: three Atlassian auth inputs, four upload inputs, all four mobile pairs,
and the Atlassian download/mobile locale controls. The run overlaps development
checks and the 65ba622 Meta batch; all raw native successes and incomplete
outcomes remain. It is not either required final repeat. The Git repository fixed
candidate exposed a separate presence-state regression: the validator returns a
contained Path, but its inherited possibly-missing flag prevents propagation.
The first trace used the monorepo root; the corrected driver verifies frozen
bytes and applies the declared scan root, reproducing the same lost guard.

`0bc77f8` clears missing/None flags after successful Path construction. Two guarded
counterexamples fail before correction; unguarded and local-pathlib controls pass.
All 110 containment/artifact tests pass (7.26 s), with strict mypy checking 144
files. The newly added artifact test's private re-export typing failure is
corrected in `a7cf338`, with both records retained. `c75e876` serializes immutable
TypeScript Value fields shallowly. Across 2000 records/9000 field values, before
and after identities match SHA-256
`858c9c281a9d1e2f41e7a808facb9de405f23edb637f3ebff5d57f31a75bd880`.
The microbenchmark's actual serialization changes from 0.7786 s to 0.3102 s;
this overlapped diagnostic does not establish native throughput. All 305 affected
regressions pass (364.87 s; 470 deselected), and lint/format/types pass. Final
native Git conditions and isolated Meta/large-family completion remain open.
All running checks above finish before evidence sealing. Fresh holdout source
and frozen labels remain untouched; no paid, publishing or outreach action occurs.


Evidence batch 19 is sealed through c75e876: 358 added/changed files, 69,092,685
raw bytes and 3,323,497 compressed bytes; archive SHA-256
`264172df072d0fa7e649b8ade8a0cdb4f57d1de75c9fb2b87cd713af34a27021`.
Every member was read back and verified. Earlier 18 batches, coverage databases,
worktrees and recovery packets remain unchanged. Subsequent isolated native and
full-source checks will be retained separately.

## Continued verification after evidence batch 19

The c75e876 Git repository measurement completes all four inputs: both vulnerable
conditions have one repository-selection candidate and both fixed conditions have
none. The same six-input batch times out on both Mobile inputs (120138/120078 ms)
and exits 1; its four successful Git results remain. An isolated Meta fixed scan,
with no concurrent test/native process, also times out at 120063 ms. These results
are in `v2-git-mobile-c75e876/` and `v2-meta-fixed-c75e876-isolated/`.

The c75e876 Mobile SENT-012 profile completes two candidates in 81.19 s, including
57.77 s in coverage inventory and 54.04 s in HTTP discovery. It reveals MCP
callbacks being interpreted during HTTP startup discovery. `3b501c9` reproduces
and fixes phantom routes from a deferred callback, retaining actual startup helper
calls. Its 23 regressions pass; the two-input native Mobile rerun still times out
(120037/120040 ms). `3e1faac` fixes the shared HTTP rule-entry path as well: HTTP
entry flows do not invoke registered MCP tools, while those tools retain separate
rule analysis. The reproduced raw-match regression and all 24 related tests pass,
with strict mypy checking 144 files. The initial wrong test-property diagnostic is
retained. The 3b501c9 native batch briefly overlaps small correction tests near its
end; it is not isolated throughput evidence.

The immutable 3e1faac full-suite milestone is running, collecting 1918 tests. The
same source's selected Mobile profile completes two findings in 30.63 s; source
location validation still takes 6.38 s. `fe6e3f2` adds bounded, per-program reuse
of validated immutable TypeScript locations, retaining node and source identities
and revalidating evicted/different objects. The original validating function remains
unchanged. All 157 parser/discovery/containment/class/module tests and 155 selected
TypeScript option/URL/credential checks pass. Strict mypy and corrected style pass;
formatting failures and two wrong test-path attempts remain. The selected profile
comparison is running; none of these overlapping diagnostics establishes native
all-rule throughput or final benchmark acceptance.

The compatibility audit reproduces unsupported exclusion globs being silently
ignored in uv, npm and pnpm. `4114f59` discloses both inclusion and exclusion glob
gaps, preserving potentially affected members and propagating incomplete expansion.
All three original failures and 36 passing workspace/module/native regression tests
are retained. Strict types/style pass. `v2-workspace-audit-4114f59/packet.json`
records the R11–R17 source audit, 14 exact files and six check records, including
previous Action/configuration checks. It distinguishes workspace membership from
aggregate shared-source traversal. This correction postdates the running full suite.

The 3e1faac Meta credential profile, overlapping the full suite, times out after
287 entry-handler interpretations. A separate behavior-preserving diagnostic now
counts unchanged immutable Value replacements on fe6e3f2. Meta's isolated all-rule
completion and the pending frozen-label decision remain open. All fresh holdout
source and frozen labels remain untouched. No paid calls, push, publication or
outreach occurred. Post-batch-19 evidence is retained separately; batch 20 is not
sealed while these checks are running.

The immutable 3e1faac milestone finishes successfully: **1882 passed, 36 skipped,
89.27% branch coverage**, 1519.11 s. Its coverage database is retained under
`v2-full-suite-3e1faac/coverage.sqlite`; subsequent workspace/cache changes have
focused checks and still require final integration verification. The expired
location-cache regression fails before `394bb8a` adds a deadline check; 19 related
parser/discovery/module tests then pass (12.91 s).

Mobile's selected-rule before/after cache comparison is exact after excluding only
finding IDs and the elapsed clock: normalized SHA-256
`6b78ad46fba8491d87b0998e2b54b30aa19b5292510fabf7339ce26070822362`.
Both raw results, profiles and comparison driver remain. The fe6e3f2 replacement
counter completes the full Meta fixed SENT-016 interpretation with three findings
in 74.42 s while overlapping tests; it changes no replacement behavior. Most
replacements change fields, so the diagnostic does not justify broadly suppressing
copies or altering flow semantics.

With all other checks finished, both Mobile originals complete native all-rule
scans at 394bb8a: vulnerable 88233 ms and fixed 90933 ms, five findings each.
Native/SARIF validation passes. `v2-mobile-locations-394bb8a/condition-adjudication.json`
verifies both vulnerable screenshot/recording hits and no fixed ordinary-parent
condition alert. Every candidate's semantics, including evidence and provenance,
match b51aee1 after excluding run identities/clocks. Fixed physical-symlink
uncertainty and the unchanged unrelated backlog remain separate. Mutations,
safe control and final 45-input repeats still need current-source measurement.

The isolated Meta concurrency feasibility diagnostic runs four existing selected
rule scans under one shared 120-second wall deadline. At 394bb8a all four finish
in **53.03 s**: SENT-012 two findings, SENT-014 zero, SENT-015 four, SENT-016 three.
Each worker performs its own parsing/inventory. This is a diagnostic, not a
production parallel implementation or complete all-rule native result. It provides
evidence for investigating bounded concurrent rule traversal while preserving
source isolation, deadline/cleanup behavior and exact serial result equivalence.

The approved Git image remains
`sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`,
linux/arm64. New 13-input campaign and native-consumer drivers are prepared for
394bb8a but have not run at this point. No paid calls, fresh-holdout tuning,
frozen-label changes, push, publication or outreach occurred.

Evidence batch 20 is sealed through 394bb8a: 226 files, 7,525,787 raw bytes,
1,090,315 compressed bytes; SHA-256
`275ceab22136b1e9e441120e0fe596ac61c2e0713fa8d84544f06c804b71dcd7`.
Every member was read back and verified; prior 19 seals and coverage remain.


## Production workers and context audit through 5f6bb9a

`2837d59` adds at most four source-flow workers for large multicore scans, using
private parsed snapshots and the original shared 120-second deadline. Parent
TypeScript parsing avoids worker subprocess descendants; workers rebuild indexes
that depend on node identity. Isolated Python cannot import the target from its
CWD/PYTHONPATH. Nine durable Python/TypeScript equivalence and process lifecycle
checks pass, including crash, timeout, invalid result, startup failure, interruption
and snapshot-write failure. Initial mypy/style/snapshot failures and corrections
remain. Corrected strict typing checks all 146 files successfully.

All five frozen Meta development inputs complete at immutable 2837d59 in
59,533 / 64,965 / 67,404 / 68,111 / 67,123 ms (vulnerable, its mutation, fixed,
its mutation, safe). This establishes native completion, not the disputed fixed
condition's acceptance. The versioned label/condition decision remains pending;
no label or prerequisite was changed and the fresh holdout remains unopened.

Mobile originals complete at the same worker source in 85,259 / 87,709 ms.
`v2-worker-native-equivalence/comparison.json` proves exact stable native findings,
evidence, completion, stages and coverage against serial 394bb8a, plus all 680/704
ordered warnings. These runs overlap brief binding checks (and the second the
start of broader regressions), so they are not isolated throughput measurements.
`9fbb8b8` extends installed/offline wheel smoke inputs above the worker threshold.
All 12 source-checkout CLI cases pass with absent/dummy model keys. Actual installed
and Linux-isolated smoke remain separate final checks.

The R09 source audit reproduced two local SDK impersonation misses, one unresolved
relative SDK import miss, eight lexical-shadowing misses and four omitted genuine
Annotated lifespan flows. `5f6bb9a` shares source-bound annotation recognition
between caller provenance and lifespan injection. Relative imports cannot establish
external SDK identity, and the existing lexical shadow index now includes classes,
functions and imports. The initial shared correction passes 918 regressions;
the final shadow correction passes 196 focused and 388 HTTP/context checks,
plus strict types/style. No target is imported or executed.

The approved Git SDK image was reverified and all 13 current 394bb8a runtime
campaigns executed. Each enumerates 80 eligible attempts and tests 24; 56 remain
untested and every scan exits 3 with clean container cleanup. In total, 312 tested
attempts show no violation and 728 remain untested; zero findings are not proof
of defense. The real orchestrator report validates as native 1.7.0 and SARIF 2.1.0,
retains the same incomplete campaign in console output and exits 3. It explicitly
uses degraded, unreviewed candidates and makes zero model calls. Historical SDK
configuration and earlier runtime measurements remain unchanged.

Evidence batch 21 retains 194 files, 29,216,392 raw bytes, 1,149,566 compressed
bytes, SHA-256 `e80849c1c12f75590c844d72d6fb0daf0fc74bb2358efa8ea0922ee8e1709136`.
Every member was read back against its hash. After sealing, the complete historical
45-input run began on the separate immutable 5f6bb9a checkout; no result is assumed.
All final repeat, held-out, quality/hosted, paid, draft and external gates remain.


## Session credentials and completed verification through fd9320b

Immutable 5f6bb9a full coverage passes: 1,910 tests, 36 skipped, 89.25% branch
coverage in 1,760.96 seconds. Its schemas, notices, artifacts, lock/export, audit,
build and installed pip/sdist/pipx/uv checks pass; strict docs pass at c589a73.
The historical first run completes 42/45 inputs. Both fixed upload inputs and
the vulnerable Mobile mutation exceed 120 seconds while other verification
was running. The harness exits 1; this is not a qualifying repeat.

All 36 Docker controls pass at 5f6bb9a in 158.99 seconds. The preceding vulnerable
reference failure remains, followed by a traced passing retry with all 20 attempts
observed. The corrected replay demo runs all 20 attempts but exits 3 because
dynamic review needs capture b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39.
No model calls occurred. The first `python -m sentinel.cli` invocation was a no-op
and is not demo evidence. Capture replacement belongs in the paid checkpoint.

cfeee22 follows session auth, headers and query defaults to actual requests,
including mapping copies, aliases, overrides, case-insensitive headers and known
Basic Auth fields. No-request, stdio, enforced guard, helper mutation, replaced
method and escaped-client controls are retained. Initial ten missing detections,
two setter-copy errors and two auth-precedence errors were reproduced before
correction. A wrong test line assertion, style/type failures and diagnostic strict
JSON validation error remain. The expanded shared suite passes 831 tests; strict
types/style and 39 final session checks pass. Four Python low-level if/match
dispatch controls verify imported caller/guard/sink behavior, not only discovery.

fd9320b additionally models aiohttp's known base-origin restriction and rejects
combined auth/Authorization requests. Two counterexamples failed before correction;
42 focused session checks, whole-project strict types and lint pass afterward.
Aiohttp was not installed in the locked scanner environment; its 3.14.3 official
source documentation was inspected at https://docs.aiohttp.org/en/stable/_modules/aiohttp/client.html.
Requests 2.34.2 and httpx 0.28.1 semantics were checked against installed source.
These are source-flow controls, not target runtime execution.

Exact preparation from retained native findings reproduces both request fingerprints
and normalized request bytes on one Python Git and one TypeScript filesystem input
at 5f6bb9a (two batches each). This permits reuse of validated findings for current
request preparation without claiming reviewed evaluation or compatible old captures
before the current candidate contexts are rebuilt.

Batch 22 retains 340 added/changed files through fd9320b: full quality
and installed distributions at 5f6bb9a, all 36 Docker controls, the incomplete
42/45 historical run, uncaptured demo dynamic review, session credential corrections
and exact Python/TypeScript retained-request equivalence. Every member was read
back against its hash. Archive size: 5,141,177 bytes; SHA-256
`6fabd73b363f7a3de18b12e05f9fc161b6530210d7608261f68ce0e51c6ba127`. Apply `evidence-v22.tar.gz` after batch 21 and verify
`evidence-v22.json`. All included checks finished before sealing. Final candidate
benchmarks and paid/hosted/external gates remain open.

## Post-batch-22 source and verification

`7071a26` fixes optional Basic Auth branches that incorrectly hid a caller's
Authorization header, including the existing Jira Forms request. The immutable
full suite passes 1,959 tests with 36 skips and 89.41% branch coverage. Its quality,
strict documentation, schema, audit, build and installed wheel/sdist/pipx/uv checks
pass. This suite predates the later exception-path correction.

`9083a89` corrects the Linux isolation harness to reject active non-loopback
interfaces and IPv4/IPv6 routes while accepting inactive kernel fallback tunnels.
The earlier denied/failed runs remain retained. All 12 source-only installed-wheel
isolation scans pass in the network-none container. `97e2cc5` adds the clean fixture's
known legitimate baselines after generated dynamic initialization in CI. The initial
installed scan correctly exited 3 for invalid calculator baseline arguments; the
corrected onboarding exits 0, and initial/unchanged/changed baseline checks exit
1/0/1 with valid native reports. Hosted matrix verification remains pending.

`v2-git-runtime-compatibility-7071a26/packet.json` verifies identical catalogs,
fallback campaigns and sandbox settings for all 13 retained Git inputs, plus
unchanged runtime/report components through 7071a26. It reuses the actual
394bb8a campaigns without relabeling their exit 3 or untested remainder. The later
734aa8c shared-flow change still requires final catalog compatibility binding.

The comparator runs retain Semgrep's actual rule timeouts despite process exit 0;
40/45 historical and 25/25 development inputs completed. Fresh holdout was not read.
`v2-pricing-configuration-audit.json` records official pricing and actual reviewer
settings only; it is not a paid approval packet and contains no new model calls.

Two original command wrappers overwrote their own structured adjudication filenames.
Those originals remain unchanged. The retained source and commands reconstruct the
historical packets under `v2-recovered-early-adjudications/`; these are old-source
adjudications, not current measurements. The eight isolated Git option-value parser
observations in `v2-git-option-value-parser/` executed only synthetic Git commands
inside the approved image; failed payload attempts are not defense proof.

Actual-source review found that prepared HTTP state erased the fixed Atlassian
operator-default qualification. The queued final benchmark sequence was stopped
before scanning an input. `734aa8c` preserves a proven getter/constant-local prefix
at exception entry and keeps differing absent-caller paths separate until credential
sinks, without combining unrelated credential-selection branches. Prefix controls
cover earlier unknown calls, later writes, catch-handler changes and nonlocal
mutation; only genuine prepared request records establish that prefix. Initial
failures, intermediate approaches, 383 affected passes, strict 146-file typing,
style/docs and final focused controls are retained. The actual source trace restores
the four service-construction qualifications; two separate Forms/users request
candidates remain to be adjudicated. This is not final condition acceptance.

Batch 23 retains 923 added/changed files through `734aa8c`, including the
immutable `7071a26` full suite (1,959 passed, 36 skipped, 89.41% branch coverage),
quality/build/audit and installed distributions, successful installed onboarding
and baseline controls, and Linux network-none isolation. The pinned comparator
completed 40/45 historical inputs and 25/25 development inputs; five historical
rule timeouts remain incomplete. All failures and stopped commands are retained.
The auth qualification regression discovered during source review is corrected
at `734aa8c`, with 383 affected passes, final prefix controls, strict typing and
restored source-specific qualifications. Final historical repeats, fresh holdout,
reviewed evaluation, hosted matrix and external acceptance remain open.

All 149,332,686 raw bytes were read back against their hashes. The archive is
5,570,931 bytes; SHA-256:
`ac3d5b820a33f616b55c9bc3f201a5202e8fee64cedcba263f372e1b9770d9a0`.
Apply `evidence-v23.tar.gz` after batch 22 and verify `evidence-v23.json`.
All included commands finished before sealing; the queued historical sequence
was terminated before it scanned an input. Earlier seals and worktrees remain.


### Prepared-client qualification correction at 8bcaded

`8bcaded` preserves the caller-absence selection and required operator setting
through helper returns, prepared configuration and stored credential fields.
It reuses shared Atlassian client/session construction without evaluating arguments
twice and follows source-defined `get` methods. Original failures remain retained.
The shared controls passed 995 tests before the final sink-only correction; the
final credential/HTTP run passed 407 tests, with strict typing, style/format and
docs passing. The full fixed-source SENT-016 diagnostic completed and all six
visible candidates now retain the `ALLOW_GLOBAL_CRED_FALLBACK` default qualifier,
including the two downstream request findings. This is source evidence, not
runtime proof or the final all-rule condition gate.

Batch 24 retains 235 completed new/changed files (23,442,399 raw bytes); archive
SHA-256 `efd494495167c814cb4af3706a6e5c30d9d06f86967b8efc7e3c8143067b3a25`.
Every member was read back and hashed. All previous seals, failures and worktrees
remain preserved. The immutable checkout is
`/private/tmp/mcp-phase22-verify-v2-prepared-clients`; its historical repeat pair
is prepared with the unchanged 120-second budget. The fresh holdout is still
unopened. Meta's fixed-condition decision, paid review, hosted verification,
human acceptance and deferred external pilot gates remain separate and open.


### Historical scoring and parent evidence through dcb965f

At immutable `8bcaded`, the first historical run completes 45/45 and source
adjudication detects all 20 vulnerable conditions. Three Excel fixed/control
parent-directory findings are conservatively scored as false alarms because
reported transport evidence did not retain the check on the requested filename.
The second run completes 43/45: the fixed Atlassian upload mutation and vulnerable
Mobile original time out at the unchanged 120-second deadline. All 43 completed
stable reports match the first run. These failures remain preserved; repeatability
and the zero-condition-false-alarm gate have not passed at that source.

`v2-historical-unrelated-ledger-8bcaded/packet.json` records all 1,484 new unrelated
instances, including explicit framework, parser and policy uncertainties. The
70 historical unrelated instances keep their original unadjudicated decisions.
The three Excel warnings stay in the condition score, not this unrelated ledger.
These are correlated warning occurrences and implementation-agent assessments,
not independent human acceptance or a measure of overall precision.

`6be3344` preserves original-path checks on visible, unresolved parent access,
including per-transport qualification that requires every observed alternative.
`dcb965f` reuses immutable TypeScript merge values and their existing metadata;
the retained Mobile profile covers byte-identical TypeScript source before this
change. Together they pass 996 shared regressions, strict 146-file typing,
lint/format and strict docs. Original counterexample and ledger-script failures
remain. Native remeasurement and final verification remain required.

Batch 25 retains 396 completed new/changed files (323,987,859 raw bytes), with
archive SHA-256 `e9df7b19f3a5e92da4f2674bea990a61dc10f42c7424d7351e9dde4dc02015b4`.
Every member was read back and hashed. Both stopped full-suite waiting queues
remain recorded; neither started a suite. The corrected immutable checkout is
`/private/tmp/mcp-phase22-verify-v2-parent-evidence`. Fresh holdout remains
unopened; Meta's fixed-condition decision, paid review, hosted verification,
human acceptance and deferred external pilot gates remain open.


### Immutable historical and full-suite gates at dcb965f

Both historical deterministic runs complete 45/45 under the unchanged 120-second
static deadline, with identical stable reports. The source-condition assessment
records 20/20 exposed vulnerable conditions and zero named fixed/safe alerts.
All 1,487 new unrelated instances have source assessments; the 70 original
unrelated instances retain their unadjudicated decisions. The three Excel parent
warnings remain visible with the established remote filename-check qualification
and separate parent-policy uncertainty. Their earlier failed score is preserved.
These are exposed, correlated cases and implementation-agent judgments, not fresh
accuracy, model retention, runtime proof or independent human acceptance.

At the same immutable source, the full suite passes 2,007 tests with 36 Docker
skips and 89.47% branch coverage in 1,213.21 seconds. The exact detached checkout,
scanner import, empty final source diff, log and coverage database are retained in
`v2-full-suite-dcb965f`. The separate actual Docker suite and installed-package
checks are queued. The three compatibility/workspace/consumer source audits are
bound to current file hashes and explicit delta reviews; all 13 approved Git
campaign/catalog configurations match retained execution evidence and the approved
linux/arm64 image identity was rechecked. Their 312 observations and 728 untested
attempts establish bounded incomplete coverage, not a defense.

The 25-input development run has started. Fresh held-out evaluation and all three
pinned comparator scopes follow sequentially; held-out source remains outside
implementation tuning. The Meta fixed-label decision, paid evaluation, hosted
matrix, consolidated draft, human acceptance and deferred external pilot gate
remain outstanding. Current results after batch 25 are expanded local evidence,
not yet covered by the next numbered seal.


### First held-out evaluation and source-coordinate correction

At immutable `dcb965f`, all 25 development inputs complete. Source assessment
finds all ten vulnerable conditions; the unchanged Meta labels yield two disputed
fixed-condition alerts, pending the explicit configuration/label decision. All
554 unmatched development warning instances have source assessments with explicit
uncertainties. No model calls or target execution were used for adjudication.

The first frozen held-out run completes 10/25 inputs, with ten unsupported and
five incomplete. None of the four completed vulnerable variants has a named
condition detection; six other vulnerable variants are unavailable, not completed
misses. The failures retain their exact reasons: unsupported dependency layout,
a supported file over 1 MiB, and strict YAML rejection of CloudFormation !Sub.
No scope limit, source, label or prerequisite was relaxed. The separate pinned
historical comparator completes 45/45 at dcb965f; its other scopes continue.

The holdout's ten unrelated SENT-003 warnings expose incorrect TypeScript source
coordinates. `v2-heldout-first-assessment-dcb965f/` retains the complete score,
unrelated assessments and an exposure record for all five auth-fetch inputs,
written before implementation changes. Subsequent auth-fetch results are exposed
regressions; a separately approved replacement corpus is required before claiming
new fresh performance for that slot. Other holdout misses/support failures are
retained evaluation results and have not been used for detector tuning.

`b163d7c` fixes the shared legacy tool-finding coordinate calculation from retained
original source; handler locations no longer start at registration metadata.
Permission findings without an operation use the registration. Sixteen failing
inline/named/Unicode/LF/CRLF controls are retained and now pass, as do lint and
whole-project typing. Broader immutable verification is queued. The three old
quality/installed/request-preparation queues were stopped before starting checks;
the active immutable comparator sequence was preserved. No paid calls, pushes,
new draft, publication, merge or outreach have occurred. Batch 25 remains the
latest seal; all later expanded evidence awaits the next verified archive.


### Coordinate verification and completed comparator scopes

`6e68331` corrects the durable direct-sink test to assert the actual original-source
slice, following production coordinate correction `b163d7c`. The shared check at
b163d7c records 300 passed and two failed. The corrected assertion passes; the
unchanged TypeScript smoke replay test remains a real failed gate because its
exact request fingerprint changed. The offline replacement request
`b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f`
reserves 95520 microUSD under the existing conservative accounting, with no model
call. It is a prepared request, not a complete paid approval packet or approval.

Pinned comparator results at dcb965f are complete as measurements: historical
45/45, development 25/25, held-out 20/25. The five Solver inputs retain parser
errors and incomplete status despite successful process exits. All three frozen
condition assessments record zero matches; 271 historical unrelated candidates
retain accepted original judgments, and 220 development plus 856 held-out warning
instances have source-condition assessments. Generic process/file audits are not
evidence of the named failed guard. No overall precision or superiority is claimed.

Batch 26 retains 1255 completed files, 391561198 raw bytes and 14263669 compressed
bytes, SHA-256 `4e4521bc7d05d4e65054b117b6faa1334c69ff7cb95096e6ee882e3742b02ce6`.
Every member was read back against its source hash. Current 6e68331 and coordinate
queue outputs are excluded until they complete; diagnostic drivers are retained.
All earlier seals, failed/stopped commands, source changes and temporary worktrees
remain preserved. No paid calls, push, new draft, merge, release or outreach yet.


### Current historical gate and replacement freeze proposal

At immutable `6e6833198989e06bd8c369abab0ee1a9d3db1ef8`, both historical runs
complete 45/45 with identical stable reports. Every stable report also equals
dcb965f, after raw-report hash and stable-hash verification. The retained
20/20 exposed vulnerable condition hits, zero named fixed/safe alerts, all
1487 unrelated assessments and the original 70 unadjudicated instances apply
through `v2-historical-gate-6e68331/packet.json`. First/second input wall totals
are 1464369/1387513 ms; maximum input wall durations are 112983/107209 ms.
No full suite, native corpus or comparator workload overlapped the pair;
lightweight documentation/source/corpus review and archival operations did.
These are local observations, not controlled throughput measurements.

Three source audits, 13 Git catalog/campaign/sandbox comparisons and the pinned
comparator/corpus bindings pass at 6e68331. Actual retained Git execution remains
incomplete, with 312 tested observations and 728 untested attempts; no defense
is inferred. The 2059-item full suite is running; current original Phase 22
repeats, delivery checks and exact native request preparation are queued.
No full-suite pass is claimed while its known smoke-capture dependency is open.

The implementation agent prepared `corpus-replacement-v1` after scanner code
froze at 6e68331, because independent-agent authorization has not arrived.
It contains complete pinned open-webSearch 2.1.6/2.1.7 archives, Apache-2.0
licenses, two reversible predicate-renaming mutations and one public IPv4
classification control. Existing 50-input corpus validation passes; 45 old
records are exactly unchanged. Advisory/source exposure is disclosed, no
detector changed, and no scanner/comparator/model/target evaluation ran.
The explicit freeze request names manifest
`159278d40a7d6fe2faa1c240a26f51009b37cdca30c862d5e9df1d66a6fed0da`.
Only the replacement five would be a new evaluation; the original holdout
results are not reset. The separate Meta decision remains pending.
The proposal is committed in `0367078`; its 28 local inspection copies are
byte-identical to their canonical archive members and inventoried for recovery.

No paid calls, push, new draft, merge, release or outreach have occurred.
Current completed post-v26 records await the next seal; active logs remain
outside all sealed archives. Strict current docs pass in
`v2-docs-current-gates-0367078`.

### Full-suite accounting and authorized continuation at d7184d3

The immutable 6e68331 full suite finished: 2021 passed, two failed, 36 skipped,
89.49% branch coverage, 1201.74 seconds. Original JUnit SHA-256 is
`341a4cf7d8ab429ee693a3356c40e6356222718ca72b76e502979ce28b8cf637`.
The raw failed result and stopped downstream queues remain unchanged.

`v2-phase12-budget-delta-6e68331/packet.json` reconstructs the exact old/new
TypeScript requests: correct source coordinates add one serialized byte, priced
at four microUSD by the existing legacy Phase 12 calculation. Its combined
Python/TypeScript reservation changes from 130736 to 130740 microUSD, within the
unchanged 140000 cap. Commit `d7184d3877c864cf1a48491864d820252a2f98b1` changes
only the stale expected test string. Both tests pass in
`v2-phase12-budget-expectation-corrected`; the tracked patch is preserved.
No scanner, request, calculation, cap or transport changed.

`v2-cost-correction-continuation-d7184d3.json` verifies the exact single test
change and scanner/scripts byte identity to 6e68331. The unchanged TypeScript
smoke replay failure still needs its already-prepared compatible capture. This
is a targeted correction following a failed full suite, not a new full-suite
pass. Native development/original held-out repeats resume at immutable 6e68331;
quality/build/install/Docker/demo checks queue behind them at immutable d7184d3.
All original queue failures and earlier checkpoints remain retained.

`v2-requirement-execution-map-6e68331/packet.json` maps all 86 obligations to
source/test hashes and actual full-suite test executions, including both raw
failures and the separate targeted correction. File-level passes are not inferred
requirement acceptance. These completed records await the next numbered seal.
No paid calls, push, new draft, merge, release or outreach have occurred.

### Completed local delivery checks and exact paid proposal

Current native repeats finish at 6e68331: development 25/25 with 574 findings,
all stable-identical to dcb965f; original held-out 10 completed, ten unsupported,
five incomplete. `v2-phase22-coordinate-regression-bindings-6e68331/packet.json`
verifies all report hashes and the only ten changed finding ranges against exact
auth-fetch source bytes. Existing condition/unrelated judgments apply, with the
Meta decision and original held-out exposure preserved.

All 18 independent checks in `v2-budget-delivery-checks-results.json` pass at
immutable d7184d3. Its remaining entry is the actual demo, exit 3 for the missing
dynamic capture. The 36 Docker tests pass in 148.37 seconds. All distribution
installers, 12 Linux network-none rules-only cases and installed onboarding plus
baseline controls pass. `v2-budget-postchecks-results.json` records five more
passes: public pre-commit, both offline smoke plans, coordinate binding and exact
benchmark capture selection. Earlier stopped queues and raw failures are intact.

The demo tests 20/20 planned/eligible attempts with no unstarted remainder;
seven static findings replay through four historical captures. Seven dynamic
findings retain host evidence and remain unreviewed. Both native JSON and SARIF
validate. No replay capture or runtime proof is fabricated.

All 95 original inputs retain their support/completion states in exact offline
request preparation: 323 distinct historical, 87 development and two original
held-out requests. Across 412 benchmark requests, 16 have compatible accepted
ledger captures and 396 are missing. Adding the TypeScript smoke and actual demo
requests yields the explicit **398-request / $66.321920** paid proposal, with 20
historical requests reused. Packet SHA-256:
`9fbe33de0f3dda4ccaa2e3a058d96d6c43d0cb7518eeb72547c1c30cf78ef3c1`.
The user approval request is pending. The executor and packet validate offline;
nine fake-transport checks verify approval/request/budget rejection paths.
All original and formatted executor versions are preserved with hash-verified
recovery; no synthetic self-test decision is user authorization.

`v2-local-acceptance-index-d7184d3/packet.json` binds all 86 local dispositions,
24 completed command records/logs and the source/corpus/report/request evidence.
This index precedes authorized draft/hosted delivery and does not claim those
steps ran. All completed records await seal 27. The separate replacement freeze,
Meta fixed-label and paid questions are pending; no new paid calls, push, draft,
merge, release or outreach have occurred yet.

Batch 27 is now sealed: 680 files, 403378236 raw bytes, 15105086 compressed bytes,
SHA-256 `83bfc17cdf1b267332f4e11685bf1467eb2ee7eeee1d6bf4320063f0c802721f`.
Every member was read back and matched; all included commands had completed.
The paid packet/request bundle and replacement proposal remain separate tracked
artifacts. All previous seals and worktrees remain. The copied paid executor's
README command validates without reading an API key. Main remains clean at
4cd5759. The consolidated draft and hosted matrix are the remaining independent
delivery work; paid, Meta, replacement and external decisions are pending.

### Delivered draft and completed hosted execution at 1e7c16a

Single consolidated DRAFT: https://github.com/BashaarJavaid/MCP-Sentinel/pull/37,
base phase22/description-poisoning (PR36), exact parent 8b6b0ddf1d6f6cf5a8da3ab9421471865b801455.
The normal push and draft creation passed; head 1e7c16a8ef92916c2f429d903b7decd7bff03c2b
and GitHub test-merge a638bff47bef4412a6f8b4ce207a20a899ab6d37 have identical trees.

CI 34348251747 completed all 29 jobs. Twelve wheel jobs pass. All twelve quality
suites finish with 2022 passed, one unchanged TypeScript capture failure, 36
skipped and 89.48-89.51% branch coverage. No additional platform failure was found.
Hosted isolation and strict documentation pass. Hosted Docker tests 20/20 attempts
and exits 3 for b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39;
its later installed steps are skipped, with local passing counterparts preserved.
Each pinned historical Phase20 reproduction retains 32 completed/13 incomplete
inputs; a successful reproduction is not a 45-input completion claim.

Hosted wheel SHA a7338898d7e24c2cf19a65aa11d9e48c01eeb8b5ba75d36cd3b5811cc24172d0
and sdist SHA 22759159598d51c66d99f3cdc9c551dea5808ecd5384e8fc8ef76fdfd291a682
match local distributions byte-for-byte. All downloaded members were read back.
Complete CI/docs log archives retain 419/12 checked members. The initial gh run
log request deferred until overall completion; the successful direct-job log
requests and the original failure remain. The final Windows suite took 2402.72
seconds and still has only the known capture failure; no job was canceled.

`v2-hosted-matrix-34348251747` and `v2-final-technical-disposition-1e7c16a` bind
all actual outcomes and 86 dispositions. Independent implementation, local gates,
draft delivery and hosted execution are finished. Paid/Meta/replacement decisions
are still pending; no new paid calls, merge, release or outreach occurred. Final
evidence-only bookkeeping uses [skip ci] without changing workflows or measured
implementation; required checks on that head may remain pending, never passed.
The measured run's failures remain explicit. Human/pilot acceptance remains unmet.

Evidence batch 28 seals 397 completed files (8,615,381 raw bytes), with every
member read back and archive SHA-256
`fdd0ce31c17f9f1a99181e8cf6edf5cb1cbf66d413c8dbc495ab795156ed4480`.
All 27 prior seals and their original failures remain preserved.
