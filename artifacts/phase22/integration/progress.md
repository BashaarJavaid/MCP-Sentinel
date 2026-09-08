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
