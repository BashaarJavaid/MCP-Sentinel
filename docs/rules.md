# MCP Sentinel rule catalog

Every rule emits the canonical Finding contract and has a stable permanent ID.
Static severity begins from impact and theoretical exploitability; dynamic proof
raises exploitability to confirmed. GPT review may confirm, suppress, or abstain,
but it cannot change a rule's identity or delete its audit trail.

## SENT-001

### Overly broad tool permission scope

- Engine: MCP-aware AST analysis plus `sentinel.permissions.yaml`
- Impact: High
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: literal filesystem/network use in official SDK and FastMCP tools;
  dynamic paths are treated as broad
- False-positive risk: Medium; broad capabilities may carry an explicit
  justification
- Remediation: narrow each capability to the resources the handler needs

## SENT-002

### Unsafe execution from tool input

- Engine: pinned Semgrep rule
- Impact: Critical
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Boundary: `eval`, `exec`, unsafe deserialization, and shell-enabled subprocess
  sinks reached by tool input
- False-positive risk: Low
- Remediation: use explicit parsers and fixed command allowlists

## SENT-003

### Missing tool input validation

- Engine: MCP-aware AST analysis
- Impact: Medium
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Boundary: decorated tools and SDK dispatchers before first parameter use;
  concrete types, Pydantic, JSON Schema, and recognized explicit checks are safe
- False-positive risk: Medium for unrecognized custom validators
- Remediation: validate every declared field before handler behavior

## SENT-004

### Unsanitized tool content in prompt

- Engine: intraprocedural AST taint analysis
- Impact: High
- OWASP: `ASI01:2026 — Agent Goal Hijack`
- Boundary: tool-controlled content entering prompts or model-request fields
- False-positive risk: Medium–High; trusted sanitizers must be configured
- Remediation: sanitize tool-controlled text before prompt construction

## SENT-005

### Hardcoded secret

- Engine: Semgrep candidates plus deterministic signature, entropy, redaction,
  fingerprint, and paired allowlist checks
- Impact: Critical
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: supported Python/configuration files; evidence is redacted
- False-positive risk: Low–Medium
- Remediation: use an external secret store or runtime environment injection

## SENT-006

### Missing or ineffective route authentication

- Engine: framework-aware AST analysis
- Impact: High
- OWASP: `ASI03:2026 — Identity & Privilege Abuse`
- Boundary: route decorators, inherited middleware, authentication dependencies,
  and explicit rejection paths
- False-positive risk: Low; intentional public routes require configuration
- Remediation: verify identity and reject invalid credentials before route code

## SENT-007

### Unverified tool manifest

- Engine: AST ordering analysis plus integrity-sidecar validation
- Impact: Medium
- OWASP: `ASI04:2026 — Agentic Supply Chain Vulnerabilities`
- Boundary: JSON/YAML manifest loads with an earlier supported digest or signature
  verification
- False-positive risk: Low
- Remediation: verify a pinned digest or trusted detached signature before parsing

## SENT-008

### Out-of-scope tool execution

- Engine: Docker-isolated dynamic probe
- Impact: Critical
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Evidence: a tool omitted from the active permissions manifest returned a
  successful non-error response
- Remediation: reject calls not granted by the active capability policy

## SENT-009

### Oversized argument accepted

- Engine: Docker-isolated dynamic probe
- Impact: Medium
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: a grossly oversized schema-shaped argument was accepted, hung, or
  crashed the server; stored evidence is bounded and redacted
- Remediation: enforce byte and schema limits before invoking handlers

## SENT-010

### Injection payload executed

- Engine: Docker-isolated scratch-canary probe
- Impact: Critical
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: the inert approved payload caused the Sentinel-only scratch canary
- Remediation: treat tool arguments as inert data and remove execution sinks

## SENT-011

### Malformed schema input processed

- Engine: Docker-isolated dynamic probe
- Impact: Low
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Evidence: a missing or wrong-type required argument produced a successful
  non-error response
- Remediation: validate required fields and declared types before handler entry
