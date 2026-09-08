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
