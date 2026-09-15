# Phase 23 correction review — bounded TypeScript recovery

**Decision requested:** approve implementation and engineering verification of
these two bounded analysis changes, preserving the frozen inputs and existing
rule/report contracts. The failed baseline is retained in
[baseline-assessment-v2](../baseline-assessment-v2/README.md).

This is the correction checkpoint required by the user's Phase 23 plan. The
machine-readable [proposal.json](proposal.json) binds this wording, source
identities, caller inventory, tests and exact affected regression list. It does
not authorize candidate/historical scans, retries, hosted dispatch, merge or
publication. Exact execution identities, commands and outer limits follow after
engineering. No full-source success is promised before those checks.

## Smallest proposed correction

1. **Resolve bounded local `export *` chains in `TypeScriptProgram`.** Reuse its
   module mapping, source inventory and recursion/deadline guards. Resolve only
   a uniquely exported binding from included source files; preserve explicit
   export precedence and reject ambiguous providers, cycles without a proven
   binding, default-through-star, unresolved/external star providers, escaping
   roots and rebound bindings. Named exports keep their existing semantics.
   Preserve the existing private discovery/worker graph and source identities.
   Do not parse source with a second parser or execute module initialization.
2. **Preserve proved Node `promisify` execution identity in the shared TypeScript
   call interpreter.** Recognize only resolved `util.promisify` / `node:util`
   imports wrapping the existing asynchronous `child_process.exec` or `execFile`
   identities. Named aliases and supported namespace/default imports must use
   the same proof, including the Node `util` default-module identity. Reuse
   `ShellFlow` and sibling rules' existing sink handling at the invocation;
   promise wrapping does not make a command string safe. Plain `execFile` argv
   without a shell remains a negative for the selected shell condition.

Both changes belong in the shared resolver/interpreter, with only necessary
sink integration. Do not add per-advisory spelling rules or special handling for
`ErrorHandler`, `gitInitLogic`, `initialBranch`, or the upstream repository.
Existing source-defined static methods, closures, callback parameters and try/catch
must carry the registration to its helper. If that requires another semantic
change, stop and present the actual failing control and additional scope.

**Identity guards are required.** A function passed to `promisify` can expose a
custom wrapper, and property writes or escapes can invalidate its identity.
Reject shadowed/rebound factories or targets, custom-symbol changes, computed or
reflective mutation, ambiguous branch aliases and unknown escapes. Aliases must
not retain a proof invalidated through another alias. Recognized Node built-in
wrappers are the bounded base case; do not infer arbitrary custom wrapper bodies.
Node documents the [custom-wrapper override](https://nodejs.org/api/util.html#custom-promisified-functions).

This adds supported source patterns within the existing TypeScript static
analysis contract. It does not change SENT-002's meaning, add a language or
execute targets. Keep the canonical Finding and report interfaces unchanged.
Any required public or private contract expansion beyond this described binding
support returns for a decision before implementation.

## Tests required before candidate execution

Use existing pytest modules and fixtures; no dependency or new framework:

- Export-star chains reaching a registered callback through a source-defined
  static helper; named export precedence and renamed imports; ambiguous exports,
  unresolved provider, cyclic graph, default exclusion, rebinding and root escape.
- Promisified `exec` with tainted command, safe literal, `execFile` argv, and the
  existing direct-call controls. Exercise named/namespace/default imports and
  aliases; preserve source-matched sink ranges and flow locations.
- Shadowed factory/target, custom promisify symbol (including `Symbol.for`),
  alias mutation, computed/reflection writes, unknown escape, uncertain branches
  and wrapper reassignment must not establish supported negatives. Preserve
  existing shell-option behavior; no broader argv-option correction is included.
- Synthetic registration → source wrapper → helper → sink, including try/catch,
  then malformed/unsupported registration controls. A fixture warning-free
  negative is insufficient unless callable identity and the relevant path are
  proved. Full advisory files are not extra unit-test scan inputs.
- Shared caller checks for SENT-012/014/015/016 and discovery; existing canonical
  JSON/SARIF and serial/worker parity checks must retain the private graph's
  identities and deterministic ordering.

Run focused development tests, then the existing `make check`. Prepare the full
hosted platform, packaging, replay, isolation, docs and dependency gates using
existing workflows; their exact revision/dispatch follows the delivery checkpoint.
Keep every failure and actual correction. No approval of technical success is
inferred from approval to implement.

## Exact affected historical regression list

[affected-regressions.json](affected-regressions.json) binds all **56 TypeScript
input records / 112 proposed observations** from the accepted Phase 22 regression
inventory, their original input/configuration bindings and **112 actual historical
report hashes**. This conservative list covers all shared TypeScript callers;
absence of an `export *` or `promisify` spelling is not used as immunity proof.

| Group | Inputs | Proposed observations |
| --- | ---: | ---: |
| Memory keeper | 3 | 6 |
| SearXNG | 5 | 10 |
| Fetch MCP | 5 | 10 |
| Open Web Search | 5 | 10 |
| Lighthouse | 5 | 10 |
| TypeScript development | 10 | 20 |
| TypeScript historical | 14 | 28 |
| Taskwarrior | 3 | 6 |
| No-bash | 3 | 6 |
| FAF | 3 | 6 |

Also retain the first Phase 23 advisory's **7 inputs / 14 observations** as
compatibility controls. Together with the replacement candidate's 14 observations,
this is a **proposed later scope of 140 observations**, not an execution approval.
All ordered reports, unrelated findings, warnings, surfaces and support judgments
must be compared and assessed. Python-only cases do not enter these TypeScript
components; changing common-language behavior would require a revised scope.

**FAF remains a known execution limitation.** Its accepted historical reports used
an explicitly uncapped experiment and exceeded 1,800 seconds. They remain such.
The later proposal must retain normal 1,800/10/15-second limits and place FAF last;
a timeout remains incomplete and triggers review. No automatic uncapped run,
optimization, historical pass conversion or compatibility exemption is approved
here. If needed, the execution checkpoint must resolve that limitation explicitly.

## Subsequent work

After engineering, review exact candidate and affected-case execution packets.
After successful reviewed results, install the seven-input current-candidate
regression once in existing offline Linux CI and demonstrate rejection by one
approved fix reversal in a disposable checkout. Release contents/version,
signed tag, TestPyPI/PyPI, GitHub assets and Action pins each follow the agreed
release approval. Phase 22 accepted closeout, Proxmox recovery deferral, pilots,
deferred benchmarks and Phase 24/15 gates remain unchanged.
