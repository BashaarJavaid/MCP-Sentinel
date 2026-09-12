# Replacement-v6: DDG shared-space URL condition

## Current v34 correction and regression approval checkpoint

The DDG fixed-request correction is implemented at **`a50e9b7`**. SENT-015
follows source-established HTTPX `build_request` → `send`, retaining a narrow
initial shared-space (`100.64.0.0/10`) rejection qualification on the same caller
URL. Removing/bypassing the guard or replacing/escaping the request loses that
qualification in synthetic controls. Known IP type inspection preserves valid
facts; local module/package shadows, replaced classes/imported attributes and
unknown mutation stay conservative.
The old six negative IP flags alone no longer establish CGNAT rejection. Broader
destinations, subsequent transformations, DNS, redirects and IPv6 remain unproven.

Current engineering passes at **`8a3db58`**: **2,280 tests / 36 skips** locally
and in all **12 supported hosted suites**, **89.87%** local branch coverage,
all **29 normal CI jobs** and docs. Ruff/format/strict mypy, lock/schema/notices,
offline artifacts, installed-wheel/Docker/isolation/hooks and exact package-source
checks pass. All **six production requests regenerate and replay with zero paid
calls**. The initial candidate's full-suite failure, failed/cancelled CI jobs,
additional replacement control, disk exhaustion and interrupted verification are
retained, including the local-module identity failure after the earlier full pass.
The final import-binding correction passes a new full suite and hosted matrix.

**Actual corrected DDG coverage is not yet evaluated.** The exact proposal at
`artifacts/phase22/integration/v34-import-binding/evaluation-proposal.json`
requires separate approval: **87 native observations**, one serial local macOS
sequence, **zero comparator runs, retries, profiles, paid calls or corpus target
executions**. The five unchanged DDG inputs run twice (10), 15 Python development
inputs once, and 31 Python historical inputs twice (62). The target is 120 seconds,
the uniform native/whole-input maximum 300 seconds, cleanup at most 15 seconds,
and sequence maximum 480 minutes. Execution/identity/schema/cleanup/timing/repeat
failure closes all unused observations; detector outcomes are retained for source
assessment. No old budget is reopened.

The gate requires actual fixed-source `send` coverage with initial CGNAT rejection
evidence, both vulnerable detections per DDG batch, unchanged Python named
conditions and **36 entire ordered repeats**. Source-sensitive synthetic controls
are separate engineering evidence. All changed findings and diagnostics require
source assessment. Preserve the two nominal fixed Meta operator erratum inputs,
each with its retained two matched keys, separately from the seven valid Python
development negatives. The unchanged TypeScript paths support reuse of the prior
54-observation compatibility and ten-observation Lighthouse results at `f85a90f`.
Historical whole 25 + 45 + 45 Linux timing remains measured at `1f3f72f`; these
partial checks will not be pooled into a new whole-batch result.

The original **DDG fresh detection at `f85a90f` remains immutable**: two correlated
vulnerable hits in each native batch, zero matching negative alerts and five
ordered repeats; fixed request/guard recognition was unresolved. The correction
follows source exposure and is an exposed regression, not another unseen success.
Original Lighthouse fresh misses, original held-out misses and all earlier failed
attempts remain preserved. Git campaigns stay **312/1,040 incomplete**, as requested.
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.

The current audit accounts for **89 original requirements** (69 passed, two
user-deferred, 18 pending current-source regression/acceptance) and **94 added
rows** (87 passed, five historical proposed limitations, two unresolved). The
pending original rows converge on this regression and its assessments. **Phase 22
remains incomplete** until the actual remaining gates, explicit human technical
acceptance and verified final closeout delivery. No merge, ready-state, release,
outreach or Phase 23 is authorized.


Approved first-frozen evaluation completed: 10 native + 5 Semgrep, zero paid calls or target execution. Native2/2 hits per batch and0/3matching negative alerts;5ordered repeats. Fixed HTTP send remains unresolved, so no recognized-fix claim. See `../integration/v33-fresh-v6/assessment.json` and `summary.md` for complete source assessments and the proposed limitation.

The complete upstream AGPL v3 source archives are retained verbatim with their
licenses and notices. The two mutation overlays rename one local helper and its
two calls; each changed file carries a dated modification/license notice. These
are evaluation source assets, not code incorporated into the Sentinel package.

Upstream repository: https://github.com/isyuricunha/mcp-ddg-research
Direct vulnerable parent: `97d3c6c511946be4dee99de0bfce82dbf3eb8687`.
Fixed child: `cf0a415758ce156f42db1dd48ec09663d0a21fd2`.
Both package versions say 0.5.1; labels bind exact source, not a patched release.

See `review/condition-review.json` for the complete flow, dependency prerequisites,
literal-address checks and unrelated upstream changes. See `provenance/novelty.json`
for the seven-manifest/96-tree exclusion check, `checkpoint-f85a90f.json` for the
source freeze, and `../integration/v32-fresh-v6/evaluation-proposal.json` for the
exact separately approvable scope and prospective scoring rubric.

One repository and one narrow vulnerability, with correlated variants. No target
imports, tests, builds, dependency installation, DNS or HTTP requests occurred.
Current-source first-frozen candidate detection is demonstrated for this narrow condition. Earlier misses and exposed regressions
are preserved; a fix after observing this source cannot count as fresh success.
