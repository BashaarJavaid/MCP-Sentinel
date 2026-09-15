# Phase 23: completed advisory baseline

**The unchanged detector meets the selected shell-injection case gate by source
assessment. Human review is pending.** All 14 approved observations completed;
all seven entire ordered report pairs agree under the approved exclusions.
The one-use budget is closed, cleanup is verified and no retry occurred.

The plan says to retain an already-passing baseline and return for another
candidate. No detector correction is warranted by this case. Phase 23 remains
incomplete: this baseline is not a correction, regression-rejection proof,
release or final technical acceptance.

## Exact result

| Input | Pass 1 / pass 2 seconds | Matching SENT-002 findings per pass | Bound condition |
| --- | --- | --- | --- |
| Full vulnerable | 12.193 / 9.975 | 1 / 1 | Detected at stop.ts:22 |
| Full fixed | 10.989 / 10.685 | 0 / 0 | Supported absence at stop.ts:35 |
| Minimized vulnerable | 4.479 / 4.659 | 1 / 1 | Detected at stop.ts:7 |
| Minimized fixed | 4.368 / 4.515 | 0 / 0 | Supported absence at stop.ts:14 |
| Safe literal | 4.462 / 4.172 | 0 / 0 | Supported absence at stop.ts:7 |
| Renamed vulnerable | 4.235 / 4.499 | 1 / 1 | Detected at stop.ts:7 |
| Renamed fixed | 4.386 / 4.444 | 0 / 0 | Supported absence at stop.ts:14 |

These are seven correlated inputs from **one advisory**, not seven independent
vulnerabilities. Full-source results remain distinct from the derived examples.
All listed sink paths are `src/tools/stop.ts`.

Actual execution: **2026-09-15 15:52:01.481044–15:53:29.948347 UTC**, or
**88.467303 seconds** including preflight and comparison. Each input stayed within
1,800 seconds and cleanup within 15 seconds. Semgrep's existing 10-second limit
and maximum four flow workers were unchanged. The approved 440-minute cap was a
worst-case bound, not an estimate. These observations establish no general speedup.

Approval binds proposal SHA-256
`8612c2e645e08b78a9cf6ab0cc5b4a6314c0c0702b722ffbd7f3b0dace74a83b`;
the frozen manifest remains
`b0d7d2420d5242eedae3666dac499b2da119607af98d0f59cda28e902f9f6e0e`.
Scanner tree remains
`b1f044ed710e9997a9572ad3a28dcce01254dc0134bb638a53334541160a8f77`.

## Why the negatives have narrow analysis support

Every report completed successfully, with a successful static stage, SENT-002
selected and evaluated, and the exact `sandbox_stop` registration and handler
recognized with SENT-002 examined. Support also needs source assessment; these
metadata checks alone would be insufficient.

**SUPPORT-ARGV:** Each fixed handler imports `execFileSync` directly from
`node:child_process`, then calls it with literal executable `docker`, an argument
array and no shell option. The existing
[ShellFlow.call](../../../src/sentinel/static/typescript_execution.py:237)
explicitly handles that API. Its shell decision is independent of the identifier
value and of whether the validator establishes protection. The three fixed
reports therefore support absence of the selected shell injection even though
they do not establish all validator behavior, Docker argument safety or runtime
container safety.

**SUPPORT-LITERAL:** The safe handler imports `execSync` and supplies a single
literal command. Its registered argument is unused. The same existing rule
handles this shell API and requires input-derived command content before emitting
a finding. The literal control has no unresolved flow diagnostics.

**Schema warnings remain warnings.** The metadata catalog reports an unsupported
schema even on the vulnerable and literal controls. The
[catalog warning](../../../src/sentinel/static/typescript.py:111) concerns schema
representation. The independent shared flow analysis
[visits the handler and seeds the first parameter](../../../src/sentinel/static/typescript_path_flow.py:2577)
without relying on that catalog schema as sanitization. Actual coverage recognizes
the exact registration and handler in every report. This is not an unsupported
negative being credited solely because it has no findings.

**Validator warnings remain unresolved.** Fixed inputs report an unresolved
RegExp.test call in `sanitizeContainerId`/`validateSandboxRef`. We do not credit
the regex as a proved sanitizer. The argv decision above does not require it.
Full-source registry deletion and logging warnings occur after the selected sink
or on its exception path; they do not alter the earlier command API or arguments.
Warnings from other rules do not establish protection for those rules.

## Complete findings and diagnostic assessment

Retained totals across both passes: **22 findings, 1,908 top-level warnings,
748 coverage unresolved-flow occurrences and 42 surfaces**. The warning and
coverage counts overlap; they are not independent defects.

- Six findings match the selected advisory: three vulnerable inputs on both passes.
- Twelve other SENT-002 occurrences are retained on the full vulnerable source:
  shell commands in `dockerUtils.ts:59`, `tools/exec.ts:27`,
  `tools/initialize.ts:60` and `tools/runJs.ts:74,85,111`. Their source and reported
  flow contexts are preserved. They are outside `sandbox_stop`; this case does
  not establish their exploitability or independently verify their corrections.
- Four SENT-015 occurrences remain on full vulnerable/fixed sources at
  `utils.ts:90`: HTTP polling of an interpolated localhost port. This is outside
  the selected shell condition. No false-positive disposition, runtime
  exploitability or broad fixed-version safety is claimed.
- Each full report retains four unresolved tool schemas and one unsupported
  `run-node-js-script` registration. These other surfaces receive no support
  credit. Selected `sandbox_stop` remains recognized.

[findings.json](findings.json), [diagnostics.json](diagnostics.json) and
[surfaces.json](surfaces.json) preserve each ordered index, source identity and
assessment. Equal-repeat entries reference both observations explicitly; raw
reports retain every duplicate. Diagnostic classes distinguish catalog metadata,
unresolved bindings, unknown validators, post-sink effects and other rule/tool
flows. None is deleted from reports or counted as globally resolved.

## Retained verification

- [observations.json](observations.json) binds all native JSON/SARIF reports,
  stdout/stderr, resolved configuration and outcome files by SHA-256.
- [Raw results](../baseline-v1/results.json) retain commands, timings, cleanup,
  report hashes and all seven ordered diff hashes. The raw machine gate remains
  `pending_source_assessment`; this separate assessment does not rewrite it.
- Native schema and offline SARIF validation passed for each completed
  observation. SARIF was rendered from the same report, without another scan.
- [verification.json](verification.json) binds this assessment and its checks.
  No scanner code changed; no new full-suite or hosted-code pass is claimed.
- Zero paid calls, advisory-target executions, retries or detector changes.
  Source snapshots, original review packets, Phase 22 evidence and limitations
  remain unchanged. Phase 21/24/15 and all deferred work remain unchanged.

## User checkpoint

Review the negative-support reasoning, retained unrelated findings and warnings,
and the completed repeated results. Accepting this baseline does not complete
Phase 23. The next unresolved decision is the replacement advisory candidate
needed to exercise a real detector correction; no replacement source freeze,
scan, detector edit, version, merge, tag or publication is authorized here.
