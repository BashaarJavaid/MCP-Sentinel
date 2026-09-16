# Metadata candidate assessment — narrow judgments reviewed

The user subsequently approved these source judgments and CI references in
[review-acceptance.json](review-acceptance.json). Original assessment records retain
their pre-review status. This approval is not final technical acceptance or release approval.

The approved 14-observation stage completed in **188.804086 seconds**, with
**seven equal entire ordered pairs**, verified cleanup and zero remaining budget.
The source-assessed **selected shell gate passes: six vulnerable detections and
eight supported negatives**. This is not final technical acceptance or release approval.

| Input | Each pass | Narrow support |
| --- | --- | --- |
| Full vulnerable | SENT-002 at gitInit/logic.ts:138 | Source-matched |
| Full fixed | No matching SENT-002 | Proved execFile argv path |
| Minimized vulnerable | SENT-002 at logic.ts:13 | Source-matched |
| Minimized fixed | No matching SENT-002 | Proved execFile argv path |
| Safe literal | No matching SENT-002 | Proved literal-only exec path |
| Renamed vulnerable | SENT-002 at logic.ts:13 | Source-matched |
| Renamed fixed | No matching SENT-002 | Proved execFile argv path |

## Support and findings to review

[source-support.json](source-support.json) retains the selected source bytes,
actual emitted flow locations and per-input judgments. Full-source metadata now
recognizes the git_init handler. The fixed source passes literal `git` and separate
argv to the immutable `promisify(execFile)` sink without a shell option. Its
SENT-014 finding at that exact sink additionally witnesses shared traversal;
it does not establish an option exploit. The selected branch field survives the
callback's object spread. Unknown path sanitization, logging, filesystem access
and result rendering are retained as unresolved and credited with no protection.
Derived controls retain their per-file helper warnings; the separately proved
shared helper/sink path supports only this shell condition. No runtime success,
filesystem safety, general repository safety or independent-vulnerability count.

All **62 findings, 8,754 warnings, 3,940 unresolved-flow occurrences and 50 surfaces**
are indexed with source identities in [findings.json](findings.json),
[diagnostics.json](diagnostics.json), [surfaces.json](surfaces.json) and
[source-contexts.json](source-contexts.json). Identical repeats are indexed together.

| Finding disposition proposed | Occurrences across both passes |
| --- | ---: |
| Selected source-matched SENT-002 | 6 |
| Other full-source SENT-002 sinks; exploitability unestablished | 20 |
| SENT-014 argv/option findings; exploitability unestablished | 26 |
| Retained SENT-003 whole-object validation findings | 10 |

The other shell findings are in checkout, clean, fetch, merge, pull, push, show
and status. Their actual command construction, source allowlists and unresolved
path handling remain visible. They are outside this one advisory's reviewed
condition. The option findings include operand positions such as `-C` and `-b`
and other user arguments; the detector does not model complete Git option grammar.
Potential false positives and possible option effects remain open. Preserve raw
severity and `needs_review`; do not suppress, confirm or manufacture further fixes.
See [finding-dispositions.json](finding-dispositions.json).

## Evidence and historical preservation

[summary.json](summary.json) binds actual scanner/configuration/proposal/results
identities. UTC execution: 2026-09-15T19:22:53.361899Z through
2026-09-15T19:26:02.165985Z. Maximum input: **36.280423 seconds**; unchanged
1,800-second input, 10-second Semgrep, 15-second cleanup, four-worker maximum
and 440-minute outer cap. Zero model calls and advisory-target execution.
All JSON and offline SARIF reports validate.

[baseline-comparisons.json](baseline-comparisons.json) indexes entire ordered
changes from the first corrected candidate (the filenames retain the generic
baseline prefix). [original-baseline-comparisons.json](original-baseline-comparisons.json)
binds additional complete diffs against the original replacement baseline.
Both previous 14-observation failed stages retain their raw failures and hashes.
The source-vs-emitted-location preparation assertion is recorded separately;
it caused no scan or report change.

Local engineering remains **2,748 passed / 36 skipped**, coverage **90.52% combined /
86.58% branch**. This assessment adds source/report validation, not another local
suite or hosted pass. Historical compatibility (126 observations), durable offline
CI and deliberate regression rejection, hosted checks, technical acceptance and
approved verified publication remain. Phase22 accepted closeout and all deferrals
remain unchanged.
