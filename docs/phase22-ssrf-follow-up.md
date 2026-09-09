# Replacement SSRF follow-up

The user authorized a bounded offline investigation and fix after the completed
technical audit. The five open-webSearch replacements are exposed regression
cases from that decision forward. The original manifest, first measurements,
labels, source archives and paid ledgers remain unchanged. The separate decision
is `artifacts/phase22/corpus-replacement-v1/exposure-and-fix-authorization.json`.

## Registration correction

The shared TypeScript flow followed factory-created `registerTool` callbacks but
ignored legacy `.tool(...)` registrations. Both discovery and rule interpretation
now route the supported schema-bearing legacy forms through the existing
registration path. Captured helpers and caller arguments reach the request sink;
a helper that fetches a fixed public destination remains a negative control.
Computed names remain unresolved. The existing Zod reader distinguishes supported
schemas from annotation objects and unknown metadata; unsupported overloads are
reported as unresolved rather than interpreting their callback context as tool
arguments.

The regression reproduced eight missing legacy registrations while four
`registerTool` controls passed. The correction also covers six unsupported-layout
controls. Focused discovery, SSRF and containment checks pass 353 tests. The full
suite passes 2,042 tests with 36 skips and 89.50% branch coverage. Lint, formatting,
strict typing, schemas, notices and strict documentation checks also pass.
Final source-bound benchmark measurements are recorded separately in the
integration evidence.

## Remaining measured boundary

The initial exposed-case diagnostic still produces no SENT-015 candidate for the
named IPv4-mapped loopback condition. It reaches the MCP callbacks and reports
`runtime.services.fetchWeb.execute` as unresolved. The source registration factory
receives an injected runtime argument; the actual startup selects that dependency
through a local dynamic import, conditional initialization and optional dependency
factories. Recognizing a registration alone does not bind that service.

A complete follow-up must establish that source chain and preserve the distinction
between the vulnerable URL/IP predicate and the fixed bracket normalization,
address classification and request filtering. A helper's name is not a defense;
broadly flagging both revisions would not demonstrate the required distinction.
Any evaluator-assisted source trace is diagnostic evidence, not a native benchmark
hit or runtime confirmation. No upstream target is executed on the host.

More paid review is not a remedy for this missing candidate: the current review
stage is candidate-bound. The 396 deferred requests and external pilots remain
nonblocking under the user's revised completion scope, without being counted as
passed. Final technical acceptance and disposition of the residual limitation
remain with the user; Phase 22 is not marked complete by this correction.
