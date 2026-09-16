# Additional checkpoint: MCP callback invocation boundary

**Approve one additional bounded semantic correction:** analyze a registered MCP
handler with its own recursion stack, while preserving the registration stack and
the existing total nesting limit. The exact proposed change is
[proposed-callback-boundary.patch](proposed-callback-boundary.patch), against the
current implemented candidate. It is **not applied**.

## Why this checkpoint is required

The approved [correction packet](../correction-review-v1/README.md) states:

> If that requires another semantic change, stop and present the actual failing
> control and additional scope.

The two approved fixes are implemented. Export-star controls and the direct
promisify controls work, but the required synthetic full-path test fails for both
vulnerable and fixed variants. The failures remain in
[callback-failure.log](../correction-engineering-v1/callback-failure.log); the
failing test remains active in `tests/test_command_execution.py`.

## Confirmed source path and failure

The synthetic test constructs the following source path without running it:

1. A factory constructs an MCP server and calls a registration helper.
2. That helper calls an imported static callback wrapper through two export-star
   barrels. The wrapper invokes its callback inside try/catch.
3. The callback registers a tool. Its tool handler invokes the same static wrapper
   again, then calls the promisified execution helper.
4. Discovery now recognizes the tool. During rule analysis,
   `TypeScriptPathFlow.registered` immediately analyzes its handler while the
   registration wrapper remains in `self.active`.
5. `function` rejects the handler's wrapper as active recursion, reporting
   `SENT-002 at boundary.ts:2: recursive or unsupported handler`. The execution
   helper is never reached and no promisified binding is established.

This is a synthetic, measured failure plus source-level explanation. It is not a
new advisory observation, a runtime trace, or a claim that fixing it proves all
full-advisory support. No target, corpus, comparator or paid call ran.

## Proposed behavior and boundaries

At the single MCP handler-entry boundary in `registered`, save the active
registration stack, start an empty handler invocation stack, analyze using the
existing callback/argument/closure handling, and restore the original stack in
`finally`. The existing HTTP callback implementation already separates its
invocation stack this way. Do not reset recursion tracking inside ordinary source
function calls. Genuine handler recursion must still warn and stop.

Because nested SDK registration can create another synthetic handler entry,
check the existing `normal_exits` nesting depth against 64 before resetting the
active stack. This retains a finite total bound, including nested callbacks.
No new state field, dependency, public interface, report field, language, generic
callback framework, callback scheduling queue or runtime execution is proposed.
Existing state updates and closure transfer remain as implemented; changed
findings/support judgments require later review.

## Required checks after approval

- Both retained end-to-end synthetic cases must reach the execution helper;
  vulnerable shell detection and supported fixed argv discrimination must pass.
- Exercise all five shared rule flows in that test, then genuine direct/mutual
  recursion within a handler, nested SDK registration at the 64-frame boundary,
  and exception/deadline restoration of the original active stack.
- Preserve unresolved/mutated SDK receiver rejection and the existing private
  invalidation contract; keep canonical JSON/SARIF and serial/worker checks.
- Run all focused checks without exclusions, then `make check`. Preserve every
  failure and correction. Full engineering is currently **not passed**.

The exact previously reviewed affected list stays
[56 Phase22 TypeScript inputs plus the first Phase23 case](../correction-review-v1/affected-regressions.json).
The later proposed scope remains 140 candidate/compatibility observations. No
Python/common-language code or new advisory input is added. FAF's accepted
uncapped-only result and ordinary deadline limitation remain unchanged.

Approval here covers this patch, necessary tests and local engineering, followed
by preparation of exact evaluation and hosted-gate packets. It does **not** approve
new corpus scans, hosted dispatch, retries, uncapped FAF execution, optimization,
Proxmox recovery, technical acceptance, merge or release. Any further required
semantic expansion returns for another concrete decision.
