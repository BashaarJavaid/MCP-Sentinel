# Review: bounded composed Zod metadata support

**Proposed, not implemented.** Approve one source correction and its synthetic
checks/local engineering to address the failed full-source registration gate.
This is an additional private analysis-support boundary beyond the earlier
export-star/promisify/callback approvals, so the Phase23 plan requires review.

## Evidence and smallest correction

The [candidate assessment](../candidate-assessment-v1/README.md) retains the failed
full pair, successful derived shell conditions and every changed output. The exact
source chain is `GitInitInputSchema` (imported `z.object` with `.describe` fields)
→ `.extend({path: ...})` → `.shape` → legacy `server.tool` metadata at line 70.
The source-visible rejection is in `TypeScriptPathFlow.call` before registration.

Reuse the existing `zod_schemas`, object fields, source symbols, mutation/escape
tracking, deadlines and registration interpreter. Add only:

1. `.describe(<literal string>)` on a proved Zod schema, preserving its existing
   type, fields and default. Description text grants no validation or sanitization.
2. `.extend(<proved literal field map>)` on a proved Zod object. Require known
   string field names and proved schema values; copy the original fields and apply
   replacement fields with right-hand precedence. Preserve the original object.
3. `.shape` on that proved object, retaining exact field identities in an ordinary
   tracked record. Reject stale, escaped, rebound or mutated schema/field aliases,
   unknown/spread/computed fields, prototype changes and unproved library identity.
4. Let the existing three/four-argument legacy-overload guard accept that proved
   field map. Keep the existing text-recognized layouts and every ambiguous
   overload rejection. Preserve actual schema source identity in discovery and
   canonical catalog output; do not invent a schema or mark validation complete.

The intended production boundary is the existing shared TypeScript interpreter,
plus its discovery metadata consumer only if needed to retain exact source
symbols. No new schema parser, service, dependency or general framework. Do not
change the shared Python interpreter or `typescript.py` text-parser contract.
If a public Finding/report/schema interface change becomes necessary, return for
a new decision. No arbitrary Zod transform/refinement/merge support is included.

## Compatibility and checks

[proposed-tests.json](proposed-tests.json) binds the concrete synthetic sources,
controls and required assertions. Use existing pytest helpers. First retain the
current failure of the composed-schema integration; then verify the correction
for vulnerable shell, fixed argv and literal controls, including all five shared
flow rules and registration/catalog discovery. Verify defaults, field replacement,
original-schema immutability, cross-file imports and source locations. Mutation,
escape, counterfeit Zod, unknown fields and overload ambiguity must remain rejected.

The existing 64-frame bound and deadline/cancellation behavior remain. Run focused
checks, then all local `make check` components with loopback permission when needed;
retain any failed attempt. The approved PyPI audit payload may be reused only while
the exact dependency export remains unchanged. No dependency upgrade is included.
Hosted engineering is still required later; this packet does not authorize dispatch.

The exact affected historical list remains
[affected-regressions.json](../correction-review-v1/affected-regressions.json),
SHA-256 `6c763cca61ea30f7d95cc6cc2c780564f2ca7459b167070b231b4b6cfa778248`:
56 TypeScript inputs / 112 historical observations, plus the first Phase23
advisory's 14 compatibility observations. All discovery consumers and SENT-002,
012, 013, 014, 015 and 016 may change output through additional recognized tools.
The existing caller inventory is retained and supplemented in [source-evidence.json](source-evidence.json).
Python-only results remain outside this TypeScript boundary. FAF's normal-deadline
completion remains unestablished, with no optimization or uncapped retry.

No current input/source/label/match-condition change, corpus scan, profile,
negative-control observation, retry, paid call, target execution or publication
is authorized by this implementation proposal. After engineering, prepare a new
exact candidate execution packet; the completed 14-observation budget is spent.
The source-visible metadata blocker does not prove that this correction alone
will establish full-source support. Any later blocker must retain its evidence.

## Human review still pending

The six derived negative observations are source-assessed as supported only for
shell injection. Their per-file helper warnings remain and are covered by the
separate shared path. Four newly exposed SENT-014 findings retain unestablished
exploitability and require disposition before technical acceptance. This proposal
does not approve those labels, suppress those findings or accept Phase23.
