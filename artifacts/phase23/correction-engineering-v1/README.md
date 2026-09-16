# Phase 23 correction implementation — integration blocker retained

The approved export-star resolution and promisify(exec/execFile) tracking are
implemented in the existing shared TypeScript resolver/interpreter. No new
service, dependency, language, public Finding/report field or advisory scan was
added. The exact diff is [implemented.patch](implemented.patch).

## Local verification

- **288 passed / 2 deselected** in the affected focused run. The two exclusions
  are the known failing `test_promisified_registered_barrel_callback` variants;
  this is a subset pass, not a full engineering pass.
- Both synthetic full-path cases remain active failing tests. Discovery finds
  the registered tool, then the shared interpreter rejects reuse of the static
  wrapper as recursion before reaching the execution helper. See
  [callback-failure.log](callback-failure.log).
- Configured mypy: 154 source files passed. Ruff, formatting (161 files) and
  schema checks passed. No `make check` or new hosted pass is claimed: the required
  integration check already fails and needs an additional semantic decision.
- Both immutable seven-input source manifests still validate. Historical corpus
  files, raw observations and their original qualifications remain unchanged.

Initial development failures remain recorded: 16 overly broad assertions
required no warnings at all, but an ordinary unresolved `tool` binding remains.
The corrected assertions require established callable identity and absence of
flow warnings for supported wrapper cases; sink counts/ranges remain checked.
The initial lint failures were closure binding, import ordering and formatting.
No production diagnostic was removed to satisfy these assertions. The subsequent
two integration failures are real unresolved analysis support, not test typos.

## Implemented support boundaries

Local star exports resolve only unique included providers, with explicit exports
retaining precedence. Ambiguous/missing/external providers, unsupported namespace
export syntax, default forwarding and rebound source bindings remain unresolved;
cycles are bounded and only proven providers can resolve. Original source bytes
and parser node identities are retained.

Promisify recognizes resolved Node imports wrapping asynchronous exec/execFile.
A bounded source proof rejects mutation and unknown escape of the imported
factory/target; module/import aliases are followed, while local target aliases
are conservatively rejected. Promisified callable invalidation is checked at
the shared call-value boundary, including values obtained through record fields.
Existing shell/argv sinks and sibling flow classes consume that proved identity.

The synthetic full-path test uses an independent toy source layout, not a new
minimization or mutation of frozen advisory inputs. It invokes Sentinel's static
interpreter only; no TypeScript or advisory code is executed.

## Required next decision

The approved correction packet explicitly requires a new decision for additional
callback semantics. Review [callback-review-v1](../callback-review-v1/README.md):
its exact unapplied patch gives MCP handler analysis an independent recursion
stack, restores registration state in `finally`, and retains a 64-frame total
nesting limit using existing state. Genuine handler recursion must still fail.

After approval, fix the retained test, add boundary/restoration controls, run all
focused tests and `make check`, then prepare exact candidate/historical and hosted
execution packets. The prior 140-observation proposed compatibility scope and
FAF limitation remain unchanged. Technical acceptance, offline CI rejection proof
and an approved verified release remain outstanding. Zero new paid calls,
corpus observations, retries, target executions or publications.
