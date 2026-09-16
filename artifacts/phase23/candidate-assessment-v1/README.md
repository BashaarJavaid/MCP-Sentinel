# Corrected candidate: partial recovery, overall case gate failed

The approved 14 observations completed in **151.922077 seconds**, with all seven
entire ordered report pairs equal and cleanup verified. The budget is closed.
No timeout, retry, target execution or paid call occurred. Normal limits remain.

| Input | Matching SENT-002 per pass | Selected shell support | Result |
| --- | --- | --- | --- |
| Full vulnerable | 0 | Unestablished; metadata rejected | Miss |
| Full fixed | 0 | Unestablished; metadata rejected | Unsupported negative |
| Minimized vulnerable | 1 | Source-matched flow | Detected |
| Minimized fixed | 0 | Proved execFile/argv path | Supported negative |
| Safe literal | 0 | Proved exec/literal path | Supported negative |
| Renamed vulnerable | 1 | Source-matched flow | Detected |
| Renamed fixed | 0 | Proved execFile/argv path | Supported negative |

These are correlated examples of one advisory. The full-source failure prevents
the case from passing. Source assessments here await human review; raw reports,
including `pending_source_assessment`, are unchanged.

## Why the full source still fails

Both full reports contain zero recognized surfaces. Their explicit warning at
`src/mcp-server/tools/gitInit/registration.ts:70` is **ambiguous legacy tool
metadata**. Lines 26–28 define the argument as
`GitInitInputSchema.extend({path: ...}).shape`; the imported base at
`logic.ts:17–45` uses string/boolean fields and `.describe(...)` modifiers.

The existing shared legacy-overload guard calls `_zod_object_schema` on source
text. That parser handles literal fields and object constructors, but not this
imported extended shape. The shared Zod value interpreter also lacks `.describe`,
`.extend` and `.shape` handling. The guard returns before `registered()` is called.
This is a sufficient source-visible blocker; removing it alone does not prove
that all subsequent full-source paths are supported. Existing inheritance,
receiver, callback, escape and recursion guards must remain.

The previous export-star correction does expose traversal: the new metadata
warning is reached inside the wrapper. Retained name-only warnings about
`ErrorHandler.tryCatch` do not prove the value interpreter failed at that member.
They are preserved, not treated as runtime traces. No additional detector change
was made during this run or assessment.

## Negative support despite retained diagnostics

The old per-file SENT-002 analyzer emits an unresolved imported-helper warning
at `src/server.ts:10`; it indexes helpers from the same file only. The separate
shared ShellFlow follows the included helper and is merged into the same report.
The minimized/renamed vulnerable reports now contain that exact cross-file
SDK-to-sink evidence.

For the three derived negatives, reviewed source is a direct SDK callback/helper
call with immutable Node imports and no wrapper mutation or escape. The corrected
shared interpreter proves `promisify(execFile)` with literal executable and argv,
or `promisify(exec)` with a literal command. The fixed reports also contain a
source-matched SENT-014 finding demonstrating shared argv traversal. The safe
control's unresolved quote replacement computes a value never passed to its
literal-command sink. These judgments establish only the selected shell condition;
they neither suppress warnings nor claim all rules or the repository are safe.

## All output and changes remain visible

- **18 findings:** four selected SENT-002, ten unchanged SENT-003 handoff findings,
  and four newly exposed SENT-014 option findings on fixed derived inputs.
- **4,994 warnings**, **824 unresolved-flow occurrences**, and **10 surfaces** are
  indexed with exact occurrences and source context where available.
- SENT-014 sees a tainted argv slot following `-b`. Its generic rule does not model
  this command's operand grammar. Exploitability is unestablished; these are
  potential false positives requiring human disposition, not additional verified
  vulnerabilities. Their original severity and status remain unchanged. No
  SENT-014 correction or suppression is proposed by this shell-case assessment.
- Entire ordered baseline-to-candidate diffs retain every change under the already
  approved volatile exclusions. New findings explain summary/review-count changes;
  metadata traversal explains additional full-source diagnostics. Removed baseline
  diagnostics remain in the immutable baseline assessment.

[observations.json](observations.json), [findings.json](findings.json),
[diagnostics.json](diagnostics.json), [surfaces.json](surfaces.json), and
[baseline-comparisons.json](baseline-comparisons.json) provide the complete index.
[Raw results](../corrected-candidate-v1/results.json) retain native JSON, offline
SARIF, timing and empty repeat diffs. Execution ran **2026-09-15T18:23:22.282405Z**
to **18:25:54.204482Z**; longest input **26.945470 seconds**.

## Next decision

Review the bounded metadata-support correction in
[metadata-review-v1](../metadata-review-v1/README.md). It is not implemented.
Current local engineering retains 2,697 passing outcomes across the full attempt
and four loopback reruns / 36 skips; no single uninterrupted full-suite or hosted
pass is claimed. Historical compatibility, offline CI/rejection proof, technical
acceptance and an approved verified release remain. Phase22 accepted limitations,
Proxmox/FAF optimization and pilot/benchmark deferrals, and Phase24/15 are unchanged.
