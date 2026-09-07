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
its own line. Static rules `SENT-001`–`SENT-007` and `SENT-012`–`SENT-014` are supported. The finding stays in rule,
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
- Evidence: a successful granted-tool control followed by successful processing
  of valid arguments by a listed ungranted tool
- Remediation: reject calls not granted by the active capability policy

The permissions sidecar declares expectations; it does not enforce a runtime
boundary. This probe tests tool-name grants, not path or network containment.
An unknown-name rejection is a completed negative; success for an unknown name
is inconclusive because real tool execution is unproven.

## SENT-009 { #sent-009 }

### Size-limit violation or attributable resource failure

- Engine: Docker-isolated dynamic probe
- Impact: Medium
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: successful processing beyond an explicit `maxLength`, `maxItems`, or
  `maxProperties` limit, or Docker-observed OOM/crash after a successful baseline
- Control: legitimate large-input success produces no finding; timeout alone is
  inconclusive, and scanner shutdown/startup failure is not crash proof
- Remediation: enforce byte and schema limits before invoking handlers

## SENT-010 { #sent-010 }

### Injection payload executed

- Engine: Docker-isolated scratch-canary probe
- Impact: Critical
- OWASP: `ASI05:2026 — Unexpected Code Execution`
- Evidence: the canary was absent before/after the separate baseline and before
  the attack, then present after the attack, even if the response reports an error
- Control: pre-existing canaries are inconclusive; inspection failure fails infrastructure
- Remediation: treat tool arguments as inert data and remove execution sinks

## SENT-011 { #sent-011 }

### Malformed schema input processed

- Engine: Docker-isolated dynamic probe
- Impact: Low
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`
- Evidence: a missing or wrong-type required argument produced a successful
  non-error response
- Remediation: validate required fields and declared types before handler entry

SENT-011 preserves valid sibling arguments and verifies the complete mutation
against the actual schema before calling. Only an actually missing required
field or invalid type supports proof. Every dynamic finding carries baseline
and attack evidence; completed negative attempts do not establish general safety.

## SENT-012 { #sent-012 }

### Path containment failure

- Engine: bounded Python and TypeScript source flow using the installed parsers
- Impact: High
- OWASP: `ASI02:2026 — Tool Misuse & Exploitation`; a caller can exceed the
  filesystem or repository resource boundary of a tool
- Boundary: recognized Python tool inputs reaching supported `open`, pathlib,
  OS/shutil filesystem APIs, Git repository selection or `Repo.index.add`;
  literal component containment after canonical resolution is recognized
- TypeScript boundary: included imports/re-exports, official SDK registrations
  and statically recoverable Mastra tool objects; supported Node filesystem calls,
  helper returns, destructured parameters, callbacks and literal dispatch branches
- False-positive risk: Medium; intentionally unrestricted tools, unsupported
  validators and unresolved bindings require review
- Remediation: resolve the path and allowed root, enforce component containment
  before access, and use the validated value. String prefix checks alone allow
  sibling-prefix collisions; lexical normalization alone does not resolve symlinks

The development implementation follows included local imports, re-exports,
unambiguous aliases and explicitly bound methods. It recognizes nested literal
dispatchers, helper return values and rejecting validators. Discarded Boolean
checks, checks of unrelated values, swallowed exceptions and later replacement
do not establish protection. An optional operator root is analyzed under the
condition that it is configured; a caller-controlled root is not trusted.
`relative_to` with true or dynamic `walk_up` is not a rejecting containment
check: Python permits parent components in that mode. Checking an expanded
home-directory path does not validate the original unexpanded value. See the
[Python API contract](https://docs.python.org/3.12/library/pathlib.html#pathlib.PurePath.relative_to).

Recursive or deeper-than-64 helper/binding chains and unresolved calls are
disclosed. This is source analysis, with no race-free filesystem or runtime
symlink guarantee. `static_review_context_incomplete` discloses traced evidence
outside the current review blocks. TypeScript recognizes enforced rejection of
parent components and absolute destinations from a relative path after canonical
resolution, including Boolean aliases and imported guards. Unsupported dispatch,
computed members, schemas and calls remain explicit gaps. Technical rule acceptance,
the new independent corpus evaluation and reviewed-tier measurements remain
pending; this draft implementation does not complete Phase 22.

## SENT-013 { #sent-013 }

### Tool-description poisoning

- Engine: the existing Python AST and installed Semgrep TypeScript parser
- Impact: High; the existing theoretical-exploitability rubric initially reports
  Medium severity, with candidate-bound review kept separate
- OWASP: `ASI01:2026 — Agent Goal Hijack`; metadata attempts to replace the agent's
  instructions, disclose secrets, or redirect its use of tools
- Boundary: Python tool docstrings, declared descriptions and parameter metadata;
  TypeScript SDK/Mastra descriptions, schema descriptions and statically recovered
  low-level `tools/list` metadata, including included imports and literal concatenation
- False-positive risk: Medium; ordinary imperatives and explicit quoted security
  warnings are controls. Security tools may still need review of remaining directives
- Remediation: remove unrelated instruction overrides, secret-disclosure requests
  and tool redirection from descriptions; describe the tool's intended operation

The rule recognizes bounded explicit wording, including supported invisible
Unicode and ANSI representations. Suspicious vocabulary alone is insufficient.
Labeling an active directive “Warning” does not exempt it. Ordinary prerequisites
such as fetching a project ID from another tool are distinct from secret-directed
redirection. Dynamically generated descriptions remain unresolved and are disclosed;
this is not independent semantic discovery or a guarantee against all prompt attacks.

The rule is enabled by default and uses existing rule selection, reason-bearing
inline suppression, baseline identities and severity thresholds. Descriptions
remain untrusted source evidence, never instructions to Sentinel. Native reports
continue to use the canonical static Finding shape.

## SENT-014 { #sent-014 }

### Command option injection

- Engine: shared Python flow analysis and the installed Semgrep TypeScript parser
- Impact: Critical; theoretical exploitability initially produces High severity
- OWASP: `ASI05:2026 — Unexpected Code Execution`; an attacker-controlled argument
  can select executable command behavior even when the invocation is shell-free
- Boundary: GitPython raw command methods, supported TypeScript child-process and
  simple-git argument positions, and Python subprocess argument lists
- Controls: enforced leading-hyphen rejection of the actual value; rejection of
  every split selector token; supported Git terminators before caller arguments
- Remediation: reject option-like inputs before use, retain the checked value,
  and use command-specific safe positions or object APIs
- False-positive risk: Medium; unrestricted administrative tools, other command
  parsers and unresolved wrappers require source review

A list of arguments prevents shell interpretation but does not prevent an argument
from being parsed as an option. A terminator after caller input cannot protect it.
Git object methods such as `repo.commit(ref)` are distinguished from raw Git
command methods. The supported terminator checks are limited to Git revision/path
commands; they do not exempt arbitrary programs. Git documents path separation in
[checkout](https://git-scm.com/docs/git-checkout) and untrusted revision handling in
[rev-parse](https://git-scm.com/docs/git-rev-parse).

Python flows include local helpers, nested handlers, source-established registration
wrappers, list append/extend/insert, copying, and selector-list construction.
Unsupported indexing and dynamic binding remain conservative. The rule does not
establish that a fixed option's value is safe for every command-specific feature.

```python
# Vulnerable: caller text can become additional dbt options.
args.extend(["--select"] + node_selection.split())

# Enforced token rejection protects this selector condition.
tokens = node_selection.split()
if any(token.startswith("-") for token in tokens):
    raise ValueError("option-like selector")
args.extend(["--select"] + tokens)
```

Default enablement, explicit `--rules SENT-014`, reason-bearing inline suppression,
baseline matching and severity thresholds use the existing canonical Finding
pipeline. Independent development measurements, fresh holdout, reviewed retention
and human acceptance remain separate gates in the Phase 22 status record.
