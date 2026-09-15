# Replacement baseline: failed case gate

The approved baseline for **GHSA-3q26-f695-pp76** completed all 14 observations,
with seven equal entire ordered report pairs and verified cleanup. It **fails**
the reviewed case gate: all three vulnerable inputs were missed twice; all four
fixed/safe inputs lack established analysis support. The budget is closed.

## Results

| Input | Matching SENT-002, each pass | Analysis support | Gate |
| --- | --- | --- | --- |
| Full vulnerable | 0 | No recognized tool surface; wrapper unresolved | Miss |
| Full fixed | 0 | No recognized tool surface; wrapper unresolved | Unsupported negative |
| Minimized vulnerable | 0 | Handler recognized; execution wrapper unresolved | Miss |
| Minimized fixed | 0 | Handler recognized; execution wrapper identity unproved | Unsupported negative |
| Safe literal | 0 | Handler recognized; execution wrapper identity unproved | Unsupported negative |
| Renamed vulnerable | 0 | Handler recognized; execution wrapper unresolved | Miss |
| Renamed fixed | 0 | Handler recognized; execution wrapper identity unproved | Unsupported negative |

Execution ran from **2026-09-15T17:04:53.298550Z** to
**2026-09-15T17:07:19.336130Z**: **146.037580 seconds** total; the longest input
was **26.223858 seconds**. Normal 1,800-second input / 10-second Semgrep /
15-second cleanup, four-worker maximum and the approved 440-minute outer cap
remained unchanged. No retry, target execution or paid call occurred.

The raw runner status `completed` and exit code 0 mean the sequence completed
and repeats agreed. They do not mean the source gate passed. Raw
`pending_source_assessment` fields remain unchanged; this separate assessment
records the failed result and awaits human review.

## Source assessment

Two source-visible blockers explain why a wrapper-only patch is insufficient:

1. `TypeScriptProgram` indexes named exports but has no export-star resolution.
   Full-source `utils/index.ts` and `utils/internal/index.ts` re-export the
   `ErrorHandler` callback wrapper through stars. Reports explicitly leave that
   imported identity unresolved. The selected registration is inside
   `ErrorHandler.tryCatch`; its source body invokes its callback at line 382.
   Full reports contain no tool surfaces. This is a sufficient static blocker,
   not a runtime trace or a claim that resolving it alone proves full support.
2. Shared shell flow recognizes resolved `child_process` sinks, but neither its
   resolver nor the shared call interpreter models `util.promisify`. Both
   minimized vulnerable reports explicitly warn that `execAsync` is unresolved
   at the frozen sink on line 13; renamed reproduction agrees. The vulnerable
   quote replacement preserves command substitution in the command string.

The fixed source passes a literal executable and separate argv to
`promisify(execFile)` without enabling a shell. The safe control uses a literal
command. Those reviewed source labels remain correct; scanner support does not
follow merely from their labels or absence of a finding. The existing unknown
call warning depends on tainted argument values; a literal argument or taint
inside an array may produce no warning. This is why none of these negatives is
credited as supported. No array-transfer correction is inferred from silence.

The full report's unsupported class warning at `errorHandler.ts:52` refers to an
interface extending another interface, **not** the `ErrorHandler` class at line
164. Its public static `tryCatch` method and callback forwarding should first use
the existing class/function interpreter. No relaxation of inheritance, decorator,
member, callback, schema or receiver guards is proposed without further evidence.

## Complete retained output

- **10 findings:** one SENT-003 at the whole-input helper handoff in each derived
  input, repeated. The source provides an SDK schema with an optional string
  field; the validation rule's field proof does not establish whole-object
  validation at that handoff. These are unrelated validation findings awaiting
  human review, not evidence that the shell condition was detected. No finding
  is removed or relabeled in the raw reports.
- **4,690 warnings and 276 coverage unresolved-flow occurrences:** every occurrence
  is indexed in [diagnostics.json](diagnostics.json), with original content,
  source hashes/line context where available and its conservative assessment.
  Full sources retain all other unresolved bindings; no other tool is declared
  safe. Repeated occurrences are grouped only across the verified equal pair.
- **10 surfaces:** the five derived handlers are recognized twice. Full-source
  absence remains explicit, rather than being converted into a supported negative.

[observations.json](observations.json) retains each timing, report hash and gate;
[findings.json](findings.json) and [surfaces.json](surfaces.json) index all outputs.
The complete native JSON, offline-validated SARIF, diagnostics and empty repeat
diffs remain in [baseline-v2](../baseline-v2/results.json).

## Next checkpoint

Review the bounded correction and affected-case list in
[correction-review-v1](../correction-review-v1/README.md). No detector correction
has been implemented. Source labels, manifest, baseline reports and historical
measurements remain frozen. The first advisory's passing baseline remains intact.
Phase 23 is incomplete; engineering, candidate regression, offline CI rejection
proof, technical acceptance and an approved verified release remain.
