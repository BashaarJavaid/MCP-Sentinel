# Replacement-v6: DDG shared-space URL condition

## Current v36 source-only investigation and diagnostic checkpoint

The approved **v36 source-only recovery investigation has reached its explicit
conditional diagnostic checkpoint**. Scanner **`a50e9b7` remains unchanged**.
Scanner-owned synthetic DDG cases preserve the guard through async callbacks,
request models/cache handling, redirects, multiple entries, separate modules,
the full rule set and isolated workers. They **do not reproduce the actual DDG
guard loss**. A separate synthetic Meta control reproduces its missing narrow
private-literal qualification. No guessed detector correction is retained.

All prototype sources, successive results and failures are preserved. An initial
full-rule test assertion incorrectly included other rules' unresolved-send
warnings; the corrected SENT-015 assertion passes in worker execution. The
prototype test edits were restored to the exact delivered source. The workspace's
missing Git link and 1,028 tracked files were restored from commit `328f7af`,
without overwriting existing files; 1,814 missing evidence members were restored
from verified seals. Existing user files and source freezes remain intact.

The exact **unapproved** fallback is
`artifacts/phase22/integration/v36-guard-recovery/diagnostic-proposal.json`:
**one instrumented `ddg-cgnat-fixed` observation** at immutable `a50e9b7`,
120-second target, **300-second native/whole-input maximum**, 15-second cleanup
maximum and **ten-minute sequence maximum**. It traces guard/predicate/request
facts and report deduplication using bounded observational wrappers. Entire
ordered output must match the retained fixed report after the established
11 volatile exclusions; JSON/SARIF, source/configuration, trace completeness and
hook/process cleanup must pass. Synthetic inline/worker report equality and
one-use/failure accounting checks pass. The initial mocked output-directory
failure and correction are retained. **No new corpus observation, comparator,
CPU profile, target execution or paid call occurred.** Any diagnostic failure
consumes its single observation; no retry or additional measurement is implied.

The actual **v35 regression still fails DDG guard coverage and Meta compatibility**:
87/87 completed at `a50e9b7`, 79 within 120 seconds, eight extended, longest
241.846285 seconds, and 36 entire ordered repeats. DDG detects both vulnerable
variants per batch; all six fixed/control sends lack the required CGNAT qualifier.
The two fixed DDG variants each have one matching generic alert. Each of two
fixed Meta image variants gains three matching alerts; their public controls
retain broader unmatched candidates. Both 31-input Python historical batches
retain 14 vulnerable hits and zero matching alerts on 17 negatives. All changed
findings and diagnostics remain source-assessed; the 87-observation budget is closed.

Engineering retains actual `8a3db58`: 2,280 passed / 36 skipped locally and in
12 hosted suites, 89.87% local branch coverage, 29 normal CI jobs, docs, verified
package sources and six zero-call production replays. Product/test/workflow bytes
are identical; no new full-suite or hosted pass is claimed for this investigation.
Original first-frozen DDG detection at `f85a90f`, its fixed-path limitation, all
original misses and every failed/closed scope remain unchanged. Prior TypeScript
compatibility and whole Linux timing retain their actual source bindings; no
partial observations are pooled into a new whole-batch pass.

The audit retains **89 original rows: 84 passed, two user-deferred, three
unresolved (R33, R65, R84)**, and **102 added rows: 94 passed, five historical
proposed limitations and three unresolved**. The added DDG correction/recovery
gates remain pending. Git campaigns stay **312/1,040 incomplete**, as requested.
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.
**Phase 22 remains incomplete; technical acceptance is not requested.** The
approved recovery proposal requires separate diagnostic approval when synthetic
controls cannot establish the actual loss. After an established correction,
ordinary engineering, a new exact regression decision and final human acceptance
remain. No merge, ready-state, release, outreach or Phase 23 is authorized.


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
