# Replacement v7: first-frozen evaluation result

The approved additional fresh-repository evaluation **completed all six
observations**, but **fails fixed/control discrimination** at frozen scanner
**`8c62567`**. In each three-input batch, Sentinel detects the **one vulnerable
`context_import` file read**, and also emits **matching false alerts on both
negative inputs** (fixed and safe). All **three entire ordered report repeats
agree** after only the established 11 volatile exclusions. This demonstrates
first-frozen vulnerable detection on another project-unused repository, but it
is not a passing vulnerable/fixed discrimination result.

All six inputs completed within the **120-second target**. Maximum native time
was **91.706 seconds**; maximum whole-input time was
**98.448156 seconds**, below the uniform **300-second maximum**.
The single serial macOS sequence took **573.363 seconds**.
Native JSON/SARIF, source/configuration identities and process cleanup validate.
The **six-observation budget is closed**, with zero unused observations, retries,
profiles, comparators, target executions or paid calls.

The repository is **`mkreyman/mcp-memory-keeper`**: complete vulnerable
**`dd53a8f` (0.12.2)** and fixed **`84f6dfa` (0.13.0)** upstream trees, the latter
compared against its direct first parent. It was selected only after `8c62567`
freeze and is absent from all eight earlier corpus manifests and 100 unique
prior effective trees. The same implementation agent curated and assessed it;
this is one repository and one vulnerability, not independent human review,
training-data novelty or six independent discoveries. The 45 old manifest records
and two format-required mutation records were not evaluated.

The vulnerable source directly reads caller `filePath` at `src/index.ts:1724`.
The fixed source calls `resolveConfinedImportPath`, checks canonical equality or
`exportsDirReal + path.sep` containment, returns on rejection, then reads the checked
`safePath` at line 1849. The frozen sibling `exports-backup` path is rejected before
reading; the safe control lies inside `exports`. Sentinel supports the actual
fixed read but still asserts missing containment. **Fixed guard recognition fails**;
this is a matching false positive, not an unsupported-sink silence. All six reports
also retain one unnamed **unresolved MCP dispatch surface**, so complete named
metadata/dispatch coverage is not established. No runtime protection proof is claimed.

All **22 findings**, **31,802 warning/unresolved-flow occurrences** and
**six surfaces** are indexed to exact source evidence and assessed. Broader export
and Git-message candidates remain unmatched and unconfirmed; the added secret
finding is upstream test fixture data. The diagnostic assessment retains binding,
callback, class and metadata limitations without treating them as resolved or safe.
An initial inventory helper incorrectly treated a synthetic metadata diagnostic
label as a literal source token; its failure and corrected catalog binding are
preserved. No report, source, label, rubric or scanner changed, and no scan repeated.

The proposed next step is **one focused source-only correction cycle**, in
`artifacts/phase22/integration/v40-fresh-v7/recovery-proposal.json`: establish the
shared guard/root-state cause using synthetic controls, implement only a supported
fix, run required engineering checks, freeze the new source and prepare a separate
exact exposed-regression proposal. It authorizes no work until approved and requests
**zero new corpus scans, profiles, comparators, target executions or paid calls**.
The original result remains immutable; a later fix is exposed regression. Source
inspection suggests checking canonical-root propagation across startup try/catch
and termination, but no root-cause execution proof or repair has occurred.

Prior **87/87 exposed regression at `8c62567` remains passed**, with 36 whole
ordered repeats, DDG two vulnerable hits per batch, zero matching negatives and
six actual fixed/control sends carrying the narrow direct-route initial 100.64/10
qualification. Python development and both 31-input historical batches retain
actual passes. Original fresh DDG at `f85a90f` remains 10 native + five Semgrep,
two correlated native hits per batch, zero matching negatives, five ordered
repeats and Semgrep 0/2; its original fixed-coverage gap and later exposed fix
remain distinguished. Original Lighthouse misses, failed `a50e9b7` regression,
all closed experiments and the original held-out result (10 completed,
10 unsupported, five incomplete; 0/4 completed vulnerable hits out of 10 total
vulnerable inputs) remain unchanged.

Historical whole Linux timing retains `1f3f72f`: both whole 45-input batches pass
with 20 hits and zero matching alerts on 25 negatives each, and the whole 25-input
development batch is reused under the explicit amendment. Current Python and
compatible TypeScript subsets are not pooled into new whole-batch execution.
Product/tests/workflows remain identical to tested `8c62567`: local and all 12
hosted suites retain **2,283 passed / 36 skipped**, **89.91% local branch coverage**,
29 normal CI jobs and docs passed. Final status docs/package metadata are checked
separately; six zero-call production replays and runtime/image compatibility retain
source bindings. **Git campaigns stay incomplete at 312/1,040**, as requested.

The audit retains **89 original rows: 84 passed, two user-deferred, three unresolved
(R66/R88 for this failed fresh discrimination checkpoint, R84 for human acceptance)**.
All **112 added rows** remain: 106 passed, five proposed historical closure
limitations, one unresolved evaluation criterion. Passing execution/source
assessment does not turn the failed criterion into a pass. **Phase 22 remains
incomplete; technical acceptance is not requested.** The correction and any later
exact measurements need their recorded decisions. Paid benchmark and pilots stay
deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, ready-state change,
release, outreach or Phase 23 is authorized.
