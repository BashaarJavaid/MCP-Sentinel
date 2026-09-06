# Phase 17 verification record

## Status and approval boundaries

The user accepted Checkpoints 1–3 and authorized Checkpoint 4. Offline, Docker,
and distribution checks passed locally. The user approved the one-request
runtime-review refresh; live capture and installed-wheel replay passed. All required
local verification passed, and the user accepted the final checkpoint. Phase 17 is complete. Native schemas now emit 1.5.0;
package version and historical captures remain unchanged. The accepted contract
is in `ARCHITECTURE.md`, section 10. Earlier checkpoint records below describe
the code and evidence at those checkpoints, not the final implementation.

The user's implementation plan requires approval after each checkpoint:

1. Reproductions, safe controls, historical input preservation, and contracts.
2. Baselines, corrected probes, sandbox evidence, and independent Docker controls.
3. Reports, GPT proof preservation, precise merging, and migration.
4. Final evidence, required verification, budgeted capture refresh, and acceptance.

Paid model calls need a separate approved case list, purpose, model, exact
request/token or monetary ceiling, and stopping condition. The current budget
is zero. Committing, pushing, and publishing require separate instructions.

## Checkpoint 1: failing-before evidence

Production source revision: `f33a90e882acb08db6afe03292ab99b63cf69da0`.
Assertions live in `tests/test_dynamic_correctness.py`. Reproduce with:

```sh
.venv/bin/pytest tests/test_dynamic_correctness.py --no-cov -q --tb=short
```

Result: **15 failed, 10 passed in 0.94 seconds**. Full output is retained in
`artifacts/phase17/checkpoint1-before.txt`. All failures are behavioral
assertions, not collection or infrastructure errors. Tests deliberately remain
red until their owning implementation checkpoint; there are no skip or xfail
markers hiding these regressions.

Retained SHA-256 identities:

```text
c01d78cb58e7d8af2a522398aba0d361b0458b3f9d36452c9b815d34f64ce183  tests/test_dynamic_correctness.py
f9e5fb8a5eeeb1b67490d32075080d9b61ad0b9da77af16fefa73fc17f6dfcb4  tests/evals/phase17-prechange-inputs.json
f64aef08790e533151850608f2bbd066cfcf1d235a532180351a727080e0b27a  artifacts/phase17/checkpoint1-before.txt
```

| Counterexample | Observed current behavior |
|---|---|
| Object-typed field | The universal wrong-type object is schema-valid, and a schema-enforcing safe tool is reported vulnerable. |
| Unconstrained nested field | A purported wrong type remains valid inside an open object envelope. |
| Valid sibling argument | Generation ignores an enum/default and invalidates an unrelated required sibling. |
| Legitimate large document | Successful processing with no declared size limit is reported vulnerable. |
| Missing or failing baseline | Only the attack runs; the scanner reports a violation without establishing the legitimate workflow. |
| Timeout | Initialized `SENT-009` timeout alone becomes a violation; independent probes do continue in this case. |
| Canary inspection failure | Docker exit 125 is treated as absence instead of infrastructure failure. |
| Canary contamination | A pre-existing canary is mistaken for a new attack effect. |
| Proof before review | An observed violation starts `needs_review`. |
| Model judgment | Suppression or abstention changes the finding status; even confirmation can lower proof confidence. |
| Model absence | Degraded review returns observed proof to `needs_review`. |

Passing controls establish that existing string/integer/array wrong-type
mutations are invalid, an unsafe object handler is detected, enforced size
limits reject the large input, ignored explicit limits yield a finding, and
canary presence/absence is read correctly for successful inspection. Inert
injection produces no finding; canary creation followed by an MCP error still
produces a finding.

These are synthetic MCP sessions and mocked Docker command results. They never
import or execute target source. JSON Schema validation supplies an independent
payload-validity oracle; fake model responses pass through the real reviewer
parser. `mode="live"` in a fake-transport unit test is not a live capture.
These tests do not establish real Docker behavior or detection accuracy.

## Historical preservation

`tests/evals/phase17-prechange-inputs.json` inventories **137 unchanged tracked
files**, with SHA-256 and the pinned source revision above. It covers all
existing cassettes and artifacts, Python reference/evaluation fixtures, frozen
Phase 16 Findings, generated schemas, and capture/evaluation scripts. Original
bytes remain in Git; retrieve a file using `git show REVISION:PATH` and verify
its recorded hash. This avoids duplicating or editing old evidence.

Historical captures retain their original fingerprints, raw responses, models,
and timing. The old capture format does not retain full request bodies; this
checkpoint does not invent them. The pinned source and fixture versions remain
available for historical reconstruction, and original retained report evidence
is preserved. Historical responses cannot be reused as judgments about changed
runtime proof. Checkpoint 3 must distinguish historical replay from the current
pipeline before any affected capture refresh.

## Verification and remaining gates

Checkpoint 1 uses focused no-coverage runs to retain the failing baseline;
this is not the final 80% branch-coverage gate.

| Command/check | Result |
|---|---|
| `.venv/bin/pytest --ignore=tests/test_dynamic_correctness.py --no-cov -q` | 426 passed in 313.15 seconds. |
| `.venv/bin/ruff check .` | Passed. |
| `.venv/bin/ruff format --check .` | 85 files already formatted. |
| `.venv/bin/mypy` | Passed, 81 source files. |
| `.venv/bin/python -m sentinel.schema check` | Passed; generated schemas unchanged. |
| `.venv/bin/python -m sentinel.report.validate_sarif artifacts/example.sarif` | Passed offline. |
| `.venv/bin/mkdocs build --strict` | Passed. |
| Historical SHA-256 inventory verification | All 137 files unchanged. |
| `git diff --check` | Passed. |

At Checkpoint 1, no real Docker campaign, paid model request, distribution build,
commit, push, or publication was performed. That checkpoint's ordinary suite
included the 15 deliberate failing-before assertions without the exclusion above.
The exact original test source is retained as
`artifacts/phase17/checkpoint1-tests.py.txt`, matching the original SHA-256 above.

Checkpoint 2 adds real Docker controls for object schemas, legitimate large
documents, explicit size breaches, OOM/crashes, slow/failing baselines, missing
prerequisites, grant boundaries, contamination, and canary-then-error behavior.
`SENTINEL_RUN_DOCKER_TESTS=1` must fail when Docker is unavailable or a required
case is skipped. Cleanup is verified after success, failure, timeout,
and interruption.

## Checkpoint 2: baselines, probes, and Docker evidence

Implementation reuses the installed JSON Schema validator, MCP client, Docker
dependency images, canonical Finding evidence, and fixed four-probe campaign.
`probe_baselines` supplies complete examples without merging. Generated examples
are locally validated and bounded to depth 8, 16 array items, and 16 KiB; configured
examples share depth/byte limits. Declared installed dialects and local references
are supported; external references are rejected without retrieval. Schemas that
cannot yield a valid bounded example get an explicit unsupported outcome.

Each probe uses a successful legitimate control and a separate fresh attack
container. SENT-008 proves listed ungranted-tool processing after a granted
control; unknown-name success remains inconclusive. SENT-009 requires a measured
`maxLength`/`maxItems`/`maxProperties` breach or pre-teardown Docker OOM/crash proof.
SENT-010 checks baseline and pre-attack absence before attributing canary creation,
including creation followed by an error response. SENT-011 validates the complete
mutation, preserves valid siblings, and uses an actual type/required constraint.
An unconstrained nested field falls back to a constrained outer binding.

The prober retains bounded baseline/attack responses, schema checks, request/schema/
policy hashes, observed effects, and separate timings. It continues independent
probes after unsupported/inconclusive outcomes, retains completed proof on
infrastructure failure, and marks remaining attempts untested. Minimal orchestration
changes keep incomplete work exit-3 eligible and separate it from infrastructure
health. Detailed native 1.5.0 summaries and console/JSON/SARIF outcome rendering
remain Checkpoint 3 work; current reports expose incomplete attempts as warnings.

Reference fixtures now contain inert reader data and complete calculator/lookup
examples. The vulnerable calculator advertises the same 4096-character limit
that the safe counterpart enforces. The lookup runtime schemas explicitly declare
their required nested record ID. Only four inventoried current input files changed
(the two reference `server.py` and `sentinel.target.yaml` files); the original bytes
remain in the pinned Checkpoint 1 revision. Every historical capture/artifact and
the independent historical evaluation fixture remain unchanged.

Independent Docker controls live in `tests/fixtures/dynamic_controls/server.py`
and are only copied into read-only sandbox targets. The real gate is:

```sh
env SENTINEL_RUN_DOCKER_TESTS=1 .venv/bin/pytest tests/test_dynamic_docker.py --no-cov -q -s --tb=short
```

Selected controls fail when Docker is unavailable or a required case is skipped;
the skip-failure behavior is itself exercised through a subprocess pytest check.
Ordinary tests skip the Docker controls when this flag is absent. No model
transport is instantiated by the Docker suite.

Retained real-Docker output includes per-case observations and both complete
reference campaigns in `artifacts/phase17/checkpoint2-docker.txt`. The initial
OOM control only allocated zero-filled virtual memory and did not cause OOM;
writing each page corrected the control. Subsequent Docker evidence records
exit 17 for the deliberate crash and `OOMKilled=true`, exit 137 for OOM.
The before-teardown evidence also exposed roughly 14-second timeout sessions
caused by SDK shutdown waits; a timing assertion and explicit pre-teardown
termination address that overrun. Scanner-initiated termination is never used
as vulnerability proof.

Final Checkpoint 2 verification:

| Check | Actual result |
|---|---|
| Targeted arguments, probes, sandbox, config, orchestration, and Docker-gate checks | **139 passed, 4 deselected** in 2.06 seconds. The exclusions are the four Checkpoint 3 model tests below. |
| Explicit real Docker gate on final code | **32 passed** in 80.58 seconds; none skipped. |
| Timing reproduction before the teardown fix | **1 failed**, 31 deselected: slow baseline took 14,185 ms against a 12,500 ms assertion allowing Docker overhead. |
| Focused teardown/startup/interruption checks after the fix | **10 passed**, 22 deselected in 41.83 seconds. |
| Broader ordinary suite during implementation | **477 passed**, 32 Docker controls skipped, 4 Checkpoint 3 model tests deselected; four existing loopback tests were blocked by sandbox socket permissions. |
| Those four loopback tests outside the sandbox | **4 passed**, 19 deselected in 3.34 seconds; local fake HTTP only. Later added/final edits are covered by the final targeted run above. |
| Ruff and formatting | Passed; 90 files formatted. |
| Mypy | Passed; 85 source files. |
| Schema drift and offline SARIF validation | Passed; existing generated schemas and `artifacts/example.sarif` unchanged. |
| Strict MkDocs build | Passed. |

Retained logs are `artifacts/phase17/checkpoint2-unit.txt`,
`checkpoint2-docker.txt`, `checkpoint2-teardown-before.txt`,
`checkpoint2-teardown-after.txt`, `checkpoint2-ordinary.txt`,
`checkpoint2-loopback.txt`, and `checkpoint2-docs.txt` in that directory.
`checkpoint2-docker-before-teardown.txt` preserves the earlier full observations
that exposed the timing issue. `checkpoint2-environment.json` records host Python
3.12.13, MCP 1.29.0, JSON Schema 4.25.1, observed Docker 29.7.2, and the dependency
image used with Python 3.11 targets. No branch-coverage or distribution gate is
claimed here; those remain Checkpoint 4 work.

Deliberate limits remain: one selected tool/field per fixed probe, no path/network
grant-containment claims, conservative baseline generation that may require an
explicit example, and no general safety claim from a completed negative attempt.
The 10-second session deadline includes initialization/discovery; mandatory
Docker inspection and cleanup add small measured overhead, and SDK shutdown
does not extend target execution after the host has sampled proof. These controls
validate the probe contract; they do not establish independent detection accuracy.

Four model-judgment/degradation regression assertions intentionally remain red
for Checkpoint 3. New probe findings start confirmed/high; current GPT code can
still downgrade them. This checkpoint does not claim the full Phase 17 gate,
review-proof preservation, native report migration, new baseline matching,
built-wheel current-pipeline replay, or an approved live-review refresh.

Checkpoint 3 owns equivalent console/JSON/SARIF outcomes, incomplete-analysis
exit precedence, partial findings, GPT disagreement, precise merging, report
1.5.0 migration, and `sentinel-baseline-v2`. Timing changes must not alter replay
identity, and historical proof must not suppress newly verified violations.

Checkpoint 4 still requires the full ordinary suite and coverage gate, Ruff,
mypy, schema drift, offline SARIF validation, strict documentation and
distribution checks, explicitly selected live Docker checks, and built-wheel
current-pipeline replay. Only then prepare the smallest affected live-review
refresh for budget approval. Phase 17 cannot close until every required gate
passes and the user accepts it. Phase 18/19 interfaces, expanded campaigns, new
threat classes, and independent AI discovery remain outside this work.

## Checkpoint 3: reports, review, merging, and migration

The user accepted Checkpoint 2 by saying “proceed to Checkpoint 3.” This
checkpoint is implemented locally and awaits acceptance. Phase 17 is incomplete;
Checkpoint 4 and its separate live-review budget/acceptance gates remain pending.

Native schema 1.5.0 now exposes nullable `dynamic_analysis`, with exactly four
validated probe outcomes when analysis runs. Console and SARIF invocation
properties use the same outcomes as native JSON. Unsupported, untested, and
inconclusive attempts retain partial findings and take exit-3 precedence;
`executionSuccessful` distinguishes infrastructure failures.

New `DynamicEvidence.proof` contains typed host proof. Bounded responses/logs and
session timings remain diagnostics. Findings start confirmed/high and retain
that status through GPT suppression, abstention, unavailable review, and review
of merged static findings. GPT confidence, reasoning, and suggested suppression
remain independent judgments. Completed model judgments are counted separately
from final finding statuses, with explicit disagreement flags/counts. Merged
provenance also preserves originating reviews.

Merging requires a unique tool/location and exact parameter or literal-subscript
mapping to the accepted type/required violation. The existing SENT-003 contract
concerns declared-type validation: a size-only violation does **not** establish
the same cause merely by naming the same parameter. SENT-009 merges only if its
successful processing also proves that same type/required violation. Resource-only
failures, ambiguous mappings, and unrelated fields remain separate findings.

Baseline-v2 and model input use stable proof identity. Timings, container IDs,
incidental output/logs, and protocol timeout/disconnection details that do not
change a decisive canary/process effect are excluded. Requests, schema/policy
identity, bindings, constraints, and decisive effects remain significant.
Canonical reports keep the diagnostic evidence. Current proof baselines survive
serialization, including proof merged into static findings.

Supported 1.3/1.4 reports migrate in memory without creating proof or completed
probe outcomes. Static matching is preserved; historical observations cannot
match newly verified runtime proof, including merged proof. Historical model
counts are recovered from retained accepted batch judgments; unavailable
historical disagreement summaries are null. Original files remain untouched.

### Actual verification

| Check | Result |
|---|---|
| Targeted report/probe/review/baseline/orchestration/CLI/SARIF suite | **130 passed, 4 deselected** in 26.15 seconds; the four loopback cases ran separately. |
| Final report-specific controls, including current baseline roundtrips | **32 passed** in 1.15 seconds. |
| Original probe correctness plus report/probe contracts | **68 passed** in 1.20 seconds, including all four previously failing GPT controls. |
| Broader ordinary snapshot during implementation | **510 passed**, 32 unselected Docker skips; four loopback cases failed only because the sandbox denied socket binding. |
| Loopback transport cases with socket access | **4 passed**, 19 deselected in 3.50 seconds. No paid endpoint was used. |
| Ruff lint and format | Passed; 90 files already formatted. |
| mypy | Passed, 86 source/test/script files. |
| Generated schema drift | Passed for native 1.5.0 Finding/report schemas; GPT response schema unchanged. |
| SARIF | New report controls validate all generated SARIF against the vendored 2.1.0 schema. |
| Strict documentation build | Passed. |
| Historical compatibility | Both retained Phase 15 replay (11 findings) and walkthrough (0 findings) reports load as migrated 1.5.0 with null dynamic summaries. |

Commands and retained results:

```bash
.venv/bin/pytest tests/test_dynamic_reporting.py tests/test_dynamic_correctness.py tests/test_dynamic_prober.py tests/test_gpt_review.py tests/test_report.py tests/test_sarif.py tests/test_baseline.py tests/test_orchestrator.py tests/test_cli.py -k 'not real_transport_uses_responses_compatible_loopback_endpoint and not compatible_http_failures' --no-cov -q
.venv/bin/pytest tests/test_dynamic_reporting.py --no-cov -q
.venv/bin/pytest tests/test_gpt_review.py -k 'real_transport_uses_responses_compatible_loopback_endpoint or compatible_http_failures' --no-cov -q
.venv/bin/mypy
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/python -m sentinel.schema check
.venv/bin/mkdocs build --strict
```

Logs and hashes are under `artifacts/phase17/checkpoint3-*`. The compatibility
inspection verifies all 137 original inventory entries: only the two generated
native schemas and four reference fixture files differ. All inventoried
historical captures and artifacts retain their original bytes. Checkpoint 1/2
logs and hashes remain unchanged, including the earlier internal response-proof
shape; they are not relabeled as evidence for the new canonical schema.

### Remaining gates and limitations

The replay identity controls use explicitly synthetic model responses, with no
network calls. The historical static replay reuses frozen original candidates
and retained medium/low cassettes; it is not evidence for changed runtime proof.
The new runtime proof projection deliberately cannot reuse old dynamic captures.
Current-pipeline demo/built-wheel replay must wait for the separately approved
minimal affected capture refresh in Checkpoint 4; no old response has been
rebound to changed evidence.

No paid model call, commit, push, release, or publication occurred. Package
version remains 1.2.1. Checkpoint 4 still owns the full final ordinary/coverage,
selected Docker, distribution/built-wheel, approved live-refresh/replay, and user
acceptance gates. The earlier Checkpoint 2 Docker evidence remains historical
Checkpoint 2 evidence; this checkpoint does not claim a fresh Docker gate.

## Checkpoint 4: final gates and pending live-review approval

The user accepted Checkpoint 3 and authorized Checkpoint 4. Phase 17 remains
incomplete until the separately approved live refresh, final installed-wheel
replay, and final acceptance pass. At this pre-approval checkpoint, no paid call had run.

### Passed local gates before the paid refresh

- Full ordinary suite: **524 passed**, 32 Docker cases unselected;
  **86.10% branch-aware coverage**, exceeding the existing 80% gate.
- Explicit `SENTINEL_RUN_DOCKER_TESTS=1` suite: **32 passed**, no skipped cases,
  in 114.35 seconds. Includes independent safe/vulnerable controls, OOM/crash,
  timing, canary, grant, and cleanup/interruption cases.
- Ruff lint/format, mypy, generated schema drift, historical SARIF validation,
  retained judge-artifact check, and strict documentation build passed.
- Wheel and sdist build passed; Twine validated both. Isolated pip wheel/sdist,
  pipx, and uv installations and the existing package/resource/TypeScript smoke
  checks passed. Package version remains 1.2.1. Distribution hashes are retained
  in `checkpoint4-distribution-SHA256SUMS`.
- The installed wheel, run outside the checkout, replayed all four unchanged
  static batches and completed all four Docker probes. It correctly returned
  **exit 3** for the single missing new dynamic-review cassette, retaining 11
  findings and valid native 1.5.0 JSON/SARIF. This is deliberately retained as
  **before-refresh evidence, not a passing final replay gate**.

The ordinary snapshot predates the small capture utility/current-cassette
selection change. Focused capture/CLI tests verify those changes, including
input-drift rejection, budget validation before key access, no replacement of
prior captures, selection of the current bundle, and one synthetic response
through capture/replay. The full final suite and distribution/replay checks will
be repeated as needed after the approved capture changes packaged contents.

Logs and reports are `artifacts/phase17/checkpoint4-*`. Initial sandbox failures
to download build/install dependencies were resolved with approved network
access. Localhost tests ran with socket access. No test failure was waived.

### Concrete live request for separate approval

The exact redacted request, canonical findings, real Docker observations,
request hash/fingerprint, and hashes of the four reused captures are retained in
`artifacts/phase17/checkpoint4-review-plan.json`. Preparation uses existing static
replay plus a fresh current Docker campaign; it does not read an API key.

| Item | Prepared scope |
|---|---|
| Cases | SENT-008 listed ungranted tool processing; SENT-009 ignored 4096-character calculator limit; SENT-010 newly created scratch canary; SENT-011 locally verified wrong-type acceptance |
| Purpose | Review the new baseline/constraint/effect evidence and preserve host proof independently of GPT judgment |
| Model | `gpt-5.6-sol`, `medium` reasoning, existing public OpenAI endpoint |
| New requests | Exactly **1** batch with four findings; **0 retries** |
| Reuse | Four unchanged static-review captures, copied byte-for-byte; historical directories/manifests remain untouched |
| Token ceiling | **12,173 input tokens** (conservative UTF-8 request-byte bound), **5,120 output tokens**, including reasoning within the API output cap |
| Stored-rate reservation | **$0.163265**, conservatively reserving all input at the stored cache-write rate |
| Requested ceiling | **$0.17**, separate approval required; the token/request limits also apply |
| Stop condition | Stop after one request or immediately on budget/input drift, transport/schema/review failure. No automatic retry or replacement. |

After approval, the concrete command is:

```bash
.venv/bin/python -m scripts.capture_phase17_reviews capture --max-usd 0.17
```

The utility stages the new response, reuses the four unchanged static captures,
validates replay, and installs a separate `src/sentinel/_cassettes/phase17`
bundle. The demo selects that bundle when present. It preserves all historical
captures and never rebinds a response to changed evidence. Capture failure leaves
the checkpoint incomplete and does not authorize another paid attempt.

The proposed token/cost reservation uses the repository's stored model rates;
it is not a new pricing measurement. No release, commit, push, or publication is
authorized by this checkpoint. After the live refresh, rebuild and validate the
current wheel, pass its complete pipeline replay, retain final gate results,
and request the user's final Phase 17 acceptance.

### Approved live refresh and final replay

The user authorized the prepared one-request/$0.17 scope by replying “key is
set, continue.” The exact approved input was revalidated before key access.
One request completed successfully, with **zero retries**. Recorded cost from
returned usage and the stored rates was **$0.027272**, within the $0.17 ceiling:
2,935 input tokens, 630 output tokens (113 reasoning), and 2,932 cache-write
tokens. Returned model: `gpt-5.6-sol`. GPT confirmed all four runtime findings at
0.99 confidence; host findings remained confirmed/high independently.

The new response is in the separate `src/sentinel/_cassettes/phase17` bundle.
Its four static captures are byte-for-byte copies of the unchanged originals.
`checkpoint4-runtime-review.json` is explicitly a replay of that captured review;
`checkpoint4-live-capture.txt` records the single live operation. No additional
paid model request was made. This four-finding result is not a broader accuracy
or safety claim.

The rebuilt installed wheel ran outside the checkout and completed the full
current pipeline with **exit 0**, 11 retained/reviewed findings, and all four
probes tested with violations observed. Its current replay model usage was zero.
Native 1.5.0 and SARIF 2.1.0 reports validate. The packaged capture bytes and
both inert fixture data files were checked directly in the wheel archive.
Before-refresh exit-3 reports remain unchanged as before/after evidence.

The final wheel and sdist passed Twine and the isolated pip wheel/sdist, pipx,
and uv checks. Their new hashes are in
`checkpoint4-final-distribution-SHA256SUMS`; these are local verification
artifacts, not a release. Final reports are
`checkpoint4-final-wheel-report.json` and `checkpoint4-final-wheel-report.sarif`.

### Final gate result, accepted

- **529 ordinary tests passed**, 32 Docker cases unselected in that run;
  **86.10% branch-aware coverage**. Full final run: 634.73 seconds.
- The separately selected live-Docker gate passed **32/32** cases with no skips.
  Its probe/sandbox implementation is unchanged by the subsequent capture and
  demo-bundle changes; the installed-wheel replay also exercised fresh probes.
- Final Ruff lint/format, mypy (88 files), generated-schema drift, strict docs,
  retained artifact check, and native/SARIF validation passed.
- The installed-wheel baseline-v2 workflow passed: initial scan exit **1** with
  nine findings; unchanged scan exit **0**, all nine matched across fresh
  containers; inert-secret mutation exit **1**, with one new SENT-005 finding.
  These scans used explicit degraded mode with the API key removed.
- Final current-pipeline replay, package installation/resource checks, archive
  metadata checks, and Twine passed. The acceptance rebuild updates README and
  changelog status. Its wheel differs from the fully exercised build only in
  `METADATA` and `RECORD`; all code, schemas, fixtures, and captures are identical.
  This comparison and the acceptance distribution hashes are retained.
- Every inventoried historical capture/artifact remains byte-for-byte unchanged.
  The new bundle adds one paid runtime capture and reuses four original static
  captures. No extra paid call, commit, push, publication, or release occurred.

Remaining limitations are unchanged: four fixed attempts, conservative schema
support, explicit incomplete outcomes, exact rather than speculative merge
mapping, and no general safety/detection-accuracy claim from these fixtures or
code coverage. Package version remains 1.2.1. All required verification work is
complete; **the user accepted the final checkpoint and Phase 17 is complete**.

The local acceptance artifacts are in `/tmp/sentinel-phase17-acceptance-dist`;
`checkpoint4-acceptance-SHA256SUMS` identifies their exact bytes. No artifact was
published. `checkpoint4-final-source-SHA256SUMS` records the source and
documentation snapshot before the final acceptance status update; earlier
checkpoint hashes retain their earlier meaning.

The user's final acceptance ("yes" in response to the Phase 17 completion
question) closes Checkpoint 4. This acceptance authorizes recording completion;
committing, pushing, publishing, and starting Phase 18 remain separate actions.
