# PortunusMCP Sentinel rule catalog

Every rule emits the canonical Finding contract and has a stable permanent ID.
Static severity begins from impact and theoretical exploitability; dynamic proof
raises exploitability to confirmed. GPT review may confirm, suppress, or abstain,
but it cannot change a rule's identity or delete its audit trail.

Static findings may be suppressed in included Python or TypeScript source with
an exact reason-bearing directive:

```text
# sentinel: ignore[SENT-005] reason=reviewed fixture credential
// sentinel: ignore[SENT-005] reason=reviewed fixture credential
```

A standalone directive binds the next physical line; a trailing directive binds
its own line. Only `SENT-001`–`SENT-007` are supported. The finding stays in rule,
report, JSON, and SARIF counts with status `suppressed`, its reason and directive
location remain visible, and GPT review is skipped for that finding. Malformed,
duplicate, unknown-rule, or reasonless directives fail with exit `2`; valid
directives that match no finding emit `inline_suppression_unused`.

## SENT-001 { #sent-001 }

### Overly broad tool permission scope

- Engine: MCP-aware Python AST/TypeScript analysis plus `sentinel.permissions.yaml`
- Impact: High
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: literal filesystem/network use in official SDK and FastMCP tools;
  dynamic paths are treated as broad
- False-positive risk: Medium; broad capabilities may carry an explicit
  justification
- Remediation: narrow each capability to the resources the handler needs

## SENT-002 { #sent-002 }

### Unsafe execution from tool input

- Engine: pinned Semgrep plus bounded Python AST/TypeScript helper-flow analysis
- Impact: Critical
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Boundary: `eval`, `exec`, unsafe deserialization, and shell-enabled subprocess
  sinks reached by tool input, including top-level same-file named helpers,
  explicit argument bindings, assignments, and helper returns
- False-positive risk: Low
- Remediation: use explicit parsers and fixed command allowlists

Helper findings point to the tool's call site and identify the known sink.
Imported helpers, recursion, ambiguous bindings, and unsupported control or
mutation paths remain unresolved and can emit `static_flow_unresolved`.
There is no fixed helper-depth cap; the existing scan deadline still applies.
`static_review_context_incomplete` means a traced flow exceeds the unchanged
GPT context window. An unresolved flow is not evidence of safety.

## SENT-003 { #sent-003 }

### Missing tool input validation

- Engine: MCP-aware Python AST/TypeScript analysis
- Impact: Medium
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Boundary: consumed input in decorated tools and SDK dispatchers; primitive
  framework schemas, Pydantic/Zod parsed results, enforced JSON Schema/Ajv checks,
  and recognized custom type/allowlist guards before use
- False-positive risk: Medium for unrecognized custom validators
- Remediation: validate every declared field before handler behavior

The relevant field must be protected on each continuing path. Unrelated
validation, discarded parsed outputs, late checks, and replacement after
validation do not exempt the consumed value. Ordinary branches and rejecting
exits are recognized; arbitrary custom validation remains outside this boundary.

## SENT-004 { #sent-004 }

### Unsanitized tool content in prompt

- Engine: intraprocedural Python AST/TypeScript taint analysis
- Impact: High
- OWASP: `ASI01:2026 — Agent Goal Hijack`
- Boundary: tool-controlled content entering prompts or model-request fields
- False-positive risk: Medium–High; trusted sanitizers must be configured
- Remediation: sanitize tool-controlled text before prompt construction

Configured sanitizers are an explicit trust decision. Only their returned value
loses taint; discarded output and reintroduced raw content remain candidates.
Recognition does not prove that text sanitization prevents prompt injection.

## SENT-005 { #sent-005 }

### Hardcoded secret

- Engine: Semgrep candidates plus deterministic signature, entropy, redaction,
  fingerprint, and paired allowlist checks
- Impact: Critical
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: supported Python/TypeScript/configuration files; evidence is redacted
- False-positive risk: Low–Medium
- Remediation: use an external secret store or runtime environment injection

## SENT-006 { #sent-006 }

### Missing or ineffective route authentication

- Engine: framework-aware Python AST/TypeScript analysis
- Impact: High
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: recognized FastAPI dependencies, Starlette authentication plus
  authenticated permissions, Express middleware, and Hono bearer authentication;
  application/path scope, trusted credential anchors, and rejecting failure paths
- False-positive risk: Low; intentional public routes require configuration
- Remediation: verify identity and reject invalid credentials before route code

Middleware installation or an authentication-related name is insufficient.
Wrong applications/paths, bypassed checks, ignored results, and request-derived
trust anchors cannot establish a protected route. Unrecognized authentication
implementations can retain a finding for review.

## SENT-007 { #sent-007 }

### Unverified tool manifest

- Engine: Python AST/TypeScript ordering plus integrity-sidecar validation
- Impact: Medium
- OWASP: `ASI04:2026 — Agentic Supply Chain Vulnerabilities`
- Boundary: JSON/YAML manifest loads with enforced SHA-256 comparison or native
  Ed25519, RSA-PSS-SHA256, or ECDSA-SHA256 verification over the consumed bytes;
  literal anchors or validated integrity-sidecar references
- False-positive risk: Low
- Remediation: verify a pinned digest or trusted detached signature before parsing

Computing a hash is insufficient. The check must reject a mismatch before
consumption; verifying different bytes, ignoring Node's boolean verification
result, or overwriting verified bytes does not establish integrity. Python's
native signature verifier rejects by raising. Recognition is bounded to the
supported source forms and does not execute the target.

## SENT-008 { #sent-008 }

### Out-of-scope tool execution

- Engine: Docker-isolated dynamic probe
- Impact: Critical
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Evidence: a tool omitted from the active permissions manifest returned a
  successful non-error response
- Remediation: reject calls not granted by the active capability policy

## SENT-009 { #sent-009 }

### Oversized argument accepted

- Engine: Docker-isolated dynamic probe
- Impact: Medium
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: a grossly oversized schema-shaped argument was accepted, hung, or
  crashed the server; stored evidence is bounded and redacted
- Remediation: enforce byte and schema limits before invoking handlers

## SENT-010 { #sent-010 }

### Injection payload executed

- Engine: Docker-isolated scratch-canary probe
- Impact: Critical
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: the inert approved payload caused the Sentinel-only scratch canary
- Remediation: treat tool arguments as inert data and remove execution sinks

## SENT-011 { #sent-011 }

### Malformed schema input processed

- Engine: Docker-isolated dynamic probe
- Impact: Low
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Evidence: a missing or wrong-type required argument produced a successful
  non-error response
- Remediation: validate required fields and declared types before handler entry
