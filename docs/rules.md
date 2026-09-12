# PortunusMCP Sentinel rule catalog

## Current v40 fresh detection and failed discrimination checkpoint

The approved additional fresh-repository evaluation **completed all six
observations**, but **fails fixed/control discrimination** at frozen scanner
**`8c62567`**. In each three-input batch, Sentinel detects the **one vulnerable
`context_import` file read**, and also emits **matching false alerts on both
negative inputs** (fixed and safe). All **three entire ordered report repeats
agree** after only the established 11 volatile exclusions. This demonstrates
first-frozen vulnerable detection on another project-unused repository, but it
is not a passing vulnerable/fixed discrimination result.

All six inputs completed within the **120-second target**. Maximum native time
was **91.706 seconds**; maximum whole-input time was
**98.448156 seconds**, below the uniform **300-second maximum**.
The single serial macOS sequence took **573.363 seconds**.
Native JSON/SARIF, source/configuration identities and process cleanup validate.
The **six-observation budget is closed**, with zero unused observations, retries,
profiles, comparators, target executions or paid calls.

The repository is **`mkreyman/mcp-memory-keeper`**: complete vulnerable
**`dd53a8f` (0.12.2)** and fixed **`84f6dfa` (0.13.0)** upstream trees, the latter
compared against its direct first parent. It was selected only after `8c62567`
freeze and is absent from all eight earlier corpus manifests and 100 unique
prior effective trees. The same implementation agent curated and assessed it;
this is one repository and one vulnerability, not independent human review,
training-data novelty or six independent discoveries. The 45 old manifest records
and two format-required mutation records were not evaluated.

The vulnerable source directly reads caller `filePath` at `src/index.ts:1724`.
The fixed source calls `resolveConfinedImportPath`, checks canonical equality or
`exportsDirReal + path.sep` containment, returns on rejection, then reads the checked
`safePath` at line 1849. The frozen sibling `exports-backup` path is rejected before
reading; the safe control lies inside `exports`. Sentinel supports the actual
fixed read but still asserts missing containment. **Fixed guard recognition fails**;
this is a matching false positive, not an unsupported-sink silence. All six reports
also retain one unnamed **unresolved MCP dispatch surface**, so complete named
metadata/dispatch coverage is not established. No runtime protection proof is claimed.

All **22 findings**, **31,802 warning/unresolved-flow occurrences** and
**six surfaces** are indexed to exact source evidence and assessed. Broader export
and Git-message candidates remain unmatched and unconfirmed; the added secret
finding is upstream test fixture data. The diagnostic assessment retains binding,
callback, class and metadata limitations without treating them as resolved or safe.
An initial inventory helper incorrectly treated a synthetic metadata diagnostic
label as a literal source token; its failure and corrected catalog binding are
preserved. No report, source, label, rubric or scanner changed, and no scan repeated.

The proposed next step is **one focused source-only correction cycle**, in
`artifacts/phase22/integration/v40-fresh-v7/recovery-proposal.json`: establish the
shared guard/root-state cause using synthetic controls, implement only a supported
fix, run required engineering checks, freeze the new source and prepare a separate
exact exposed-regression proposal. It authorizes no work until approved and requests
**zero new corpus scans, profiles, comparators, target executions or paid calls**.
The original result remains immutable; a later fix is exposed regression. Source
inspection suggests checking canonical-root propagation across startup try/catch
and termination, but no root-cause execution proof or repair has occurred.

Prior **87/87 exposed regression at `8c62567` remains passed**, with 36 whole
ordered repeats, DDG two vulnerable hits per batch, zero matching negatives and
six actual fixed/control sends carrying the narrow direct-route initial 100.64/10
qualification. Python development and both 31-input historical batches retain
actual passes. Original fresh DDG at `f85a90f` remains 10 native + five Semgrep,
two correlated native hits per batch, zero matching negatives, five ordered
repeats and Semgrep 0/2; its original fixed-coverage gap and later exposed fix
remain distinguished. Original Lighthouse misses, failed `a50e9b7` regression,
all closed experiments and the original held-out result (10 completed,
10 unsupported, five incomplete; 0/4 completed vulnerable hits out of 10 total
vulnerable inputs) remain unchanged.

Historical whole Linux timing retains `1f3f72f`: both whole 45-input batches pass
with 20 hits and zero matching alerts on 25 negatives each, and the whole 25-input
development batch is reused under the explicit amendment. Current Python and
compatible TypeScript subsets are not pooled into new whole-batch execution.
Product/tests/workflows remain identical to tested `8c62567`: local and all 12
hosted suites retain **2,283 passed / 36 skipped**, **89.91% local branch coverage**,
29 normal CI jobs and docs passed. Final status docs/package metadata are checked
separately; six zero-call production replays and runtime/image compatibility retain
source bindings. **Git campaigns stay incomplete at 312/1,040**, as requested.

The audit retains **89 original rows: 84 passed, two user-deferred, three unresolved
(R66/R88 for this failed fresh discrimination checkpoint, R84 for human acceptance)**.
All **112 added rows** remain: 106 passed, five proposed historical closure
limitations, one unresolved evaluation criterion. Passing execution/source
assessment does not turn the failed criterion into a pass. **Phase 22 remains
incomplete; technical acceptance is not requested.** The correction and any later
exact measurements need their recorded decisions. Paid benchmark and pilots stay
deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, ready-state change,
release, outreach or Phase 23 is authorized.


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
its own line. Static rules `SENT-001`–`SENT-007` and `SENT-012`–`SENT-016` are supported. The finding stays in rule,
report, JSON, and SARIF counts with status `suppressed`, its reason and directive
location remain visible, and GPT review is skipped for that finding. Malformed,
duplicate, unknown-rule, or reasonless directives fail with exit `2`; valid
directives that match no finding emit `inline_suppression_unused`.

## Narrow TypeScript URL guard evidence

The TypeScript flow follows source-bound low-level `CallToolRequestSchema`
handlers through factory-created `Server` instances and `McpServer.server`
aliases, including the parser's optional else branch. Replaced or escaped
receivers lose that binding.

Module-level class construction and constructor registration also follow source
order. SDK prototype wrappers retain the original setter only when the source
forwards the actual schema, handler and SDK receiver through the saved method.
Replaced callbacks, wrong receivers and escaped methods do not establish that
registration. Unused classes do not create tool entries.

SENT-015 can qualify a broader SSRF candidate with narrow source-established
literal loopback IPv4 rejection. Local hostname prefix checks and `net.isIP`
comparisons preserve the actual URL identity. A default-only qualifier requires
every normal guard exit either to enforce that check or to require an unshadowed,
unmutated `process.env` option explicitly compared to `"true"`. Missing hardening
options, unknown conditions, URL replacement and environment mutation cannot
establish this protection. The scanner does not read the target environment or
suppress the broader candidate. DNS, redirects, IPv6 and other destinations remain
unestablished; this is source analysis, not runtime proof.

Lighthouse calls are recognized URL sinks. A literal `169.254.` hostname rejection
can qualify a candidate as excluding initial link-local IPv4 destinations, while
retaining the broader finding. Ordered prefix-table guards require a known array
and at most 32 iterations. Indexed aliases, unknown mutations, unresolved loop
control, swallowed failures and checks on another URL cannot establish this
qualification. This does not imply loopback, DNS, redirect or IPv6 protection.
An allowlist branch restricted to exact `::1` or `[::1]` hostname literals can
preserve the narrower IPv4 link-local exclusion at a helper's normal-return join.

At `2ac39aa`, the full exposed SearXNG source retains this qualifier on both
fixed variants. Receiver invalidations stay local to mutually exclusive `if`
arms and are conservatively unioned at their join; unknown effects in an HTTP
branch no longer contaminate its stdio alternative. Both five-input native
batches detect both vulnerable variants with zero matching fixed/control alerts.
Broader candidates and unresolved dispatch remain visible. The earlier `6eb482c`
fixed false alerts are preserved; neither result establishes complete redirect
coverage or runtime protection. See the current Phase 22 status and audit.


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
Python helper flow also recognizes imported `subprocess.check_call` and
`subprocess.check_output` with literal `shell=True`; fixed commands, locally
rebound callees and calls without an established shell do not match those sinks.
TypeScript shell calls also use shared SDK registration and source bindings to
follow imported helpers, low-level request dispatch and command reassignment.
These findings cite the external sink with cross-file source evidence. `exec`
and `execSync` invoke shells; `execFile`/`spawn` forms require established
`shell: true` for this added shell flow. Separate argv without a shell is not a
shell-injection finding. The existing command-option rule covers its own contract.
Recursion, ambiguous bindings and unsupported control or mutation paths can emit
`static_flow_unresolved`. Shared TypeScript flow has a 64-frame recursion bound;
the existing scan deadline also applies.
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

Included tool decorators are followed through their returned callable and captured
arguments. The exact registration position determines which wrappers affect the
registered handler. A wrapper that substitutes a fixed path or never invokes the
handler does not establish the original caller-to-sink flow. Unresolved decorators
remain an explicit limitation, including nondefault or impersonated `wraps`.

The current integration also follows explicit parameterless FastMCP launches and
their preceding module-global assignments, retaining the analyzed transports in
findings. Replaced or unresolved launch methods retain unconfigured analysis.
Source-bound openpyxl workbook loads and saves are filesystem sinks; unknown or
replaced workbook receivers do not establish that API identity.
Python parent-directory findings retain an enforced check on the original path
without claiming that its parent is contained. When launch modes differ, the
finding names the transports on which that original check was established. An
unguarded alternative in the same transport removes that qualification; the
parent-directory candidate remains visible for review.

TypeScript boolean status fields can carry enforced helper-return conditions.
Discarding the field, replacing it, or letting its record escape to an unknown
call does not establish protection. A retained candidate can distinguish an
initial normalized root-prefix check from the containment of paths derived
afterward. That initial check does not establish component, parent-fallback or
symlink safety. While loops receive zero-or-one-iteration source interpretation;
later loop-carried state is explicitly unresolved. No target loop is executed.

The TypeScript interpreter also follows the documented
[`mobilecli screenrecord --output` contract](https://github.com/mobile-next/mobilecli/blob/main/skills/mobilecli/SKILL.md)
through ordered arguments and included class helpers to genuine Node process
calls. It requires a literal `mobilecli` command or a caller-independent path in
its named npm package with the binary prefix `mobilecli-`. Findings explicitly
qualify this source-selected executable; operator overrides and a functioning
device/toolchain require separate verification. An arbitrary executable or an
unresolved or repeated option sequence does not establish this contract.
A conditional output guard is retained only for the same truthy returned value.
These are static source findings, not observed file writes or Node runtime support.

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
TypeScript Git and simple-git calls consume the evaluated ordered array, including
aliases, helper appends, conditional appends and zero-argument slice copies.
Arrays are bounded to 32 layouts of 256 positions; unknown escapes and computed
updates retain visible uncertainty and cannot establish a safe terminator.
Unsupported indexing and dynamic binding remain conservative. The rule does not
establish that a fixed option's value is safe for every command-specific feature.
The current Git terminator model covers `diff`, `show`, `log`, `checkout` and
`rev-parse`. It retains a known false alarm for `git add --`, whose separator is
defined by the [Git add reference](https://git-scm.com/docs/git-add), and conservative
candidates for date/commit filter values; these require separate source review.

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

## SENT-015 { #sent-015 }

- **Title:** Server-side request forgery
- **OWASP:** ASI02:2026 — Tool Misuse & Exploitation. A caller can use the server's
  outbound request capability to address destinations outside the intended boundary.
- **Impact:** High; theoretical likelihood produces initial Medium severity.
- **Engine:** Source-only Python and TypeScript flow through shared discovered
  handlers and bounded local helpers.
- **Remediation:** Restrict schemes to HTTP(S), require intended destinations,
  reject private/loopback addresses, and validate each requested value and redirect.
- **False-positive risk:** Medium. Intentionally unrestricted network tools and
  custom request clients/validators require source review.

Python requests/httpx functions and recognized requests/httpx/aiohttp client
instances are request sinks, as is urllib's URL opener. TypeScript supports global
fetch, recognized node-fetch/undici/axios imports, and Node HTTP(S) requests.
Python entry points include discovered MCP tools and source-established HTTP
routes; FastAPI dependency-injected parameters are not ordinary caller input.
Guard facts follow the actual URL binding; a discarded predicate, unrelated guard,
caught failure that continues to the request, or replacement input is insufficient.
Exact scheme/hostname allowlists are supported in both languages. Python also
supports enforced standard-library IP-address predicates and a statically nonempty
literal-address validation loop. The exception path for nonliteral hostname
resolution does not establish DNS safety.

TypeScript caller fields also flow through supported genuine Zod schemas and
async static class helpers. Schema parsing alone does not restrict destinations.
An enforced imported `private-ip` predicate on the same parsed URL's hostname
credits only literal IPv4 rejection. Checking the whole URL, ignoring the result,
or escaping/replacing the URL object does not establish that guard. A guarded
path can retain a residual finding for restrictions that remain unestablished;
that finding does not claim the initial private-IPv4 request is permitted.

Genuine Atlassian Jira/Confluence clients retain their current base URL at REST
`get`, `post`, `put`, `patch`, `delete`, `request` and Jira `myself()` calls.
Construction alone does not establish a request. The
[SDK REST contract](https://github.com/atlassian-api/atlassian-python-api/blob/4.0.7/atlassian/rest_client.py)
joins relative paths to that base; explicit `absolute=True` selects the supplied
path. Replaced URL values are checked at the call, while unknown sessions, escaped
clients and replaced request methods remain unresolved. Other SDK methods and
middleware-to-tool request-state relationships are not established by this support.

This rule's destination condition covers prohibited schemes and literal
private/loopback destinations. Hostname resolution, DNS rebinding, and complete
redirect-policy verification are not established by these checks. Ambiguous
bindings and unsupported wrappers remain disclosed rather than treated as proof
of protection. A finding is a static candidate, not an observed network request.

The frozen SearXNG evaluation missed both vulnerable variants at `7555a9d`.
Its MCP tool surface was not recognized, so completed scans of the optional HTTP
routes did not establish coverage of the ordinary stdio URL reader. The exposed
correction at `2ac39aa` now passes the narrow detection gate while retaining
unresolved dispatch coverage. See [the current assessment](phase22-implementation-status.md)
for the preserved first results and remaining limitations.

```python
# Caller input reaches the server's network capability.
return requests.get(url)

# An enforced exact destination boundary for the initial requested URL.
parsed = urlparse(url)
if parsed.scheme != "https" or parsed.hostname != "images.example.com":
    raise ValueError("destination not allowed")
return requests.get(url, allow_redirects=False)
```

The rule is enabled by default and uses canonical Finding evidence, explicit
`--rules SENT-015` selection, inline suppression, baseline matching and severity
thresholds. Development measurements, held-out evaluation, reviewed retention and
human acceptance remain separate Phase 22 gates.


## SENT-016 { #sent-016 }

- **Title:** Unauthorized operator-credential fallback
- **OWASP:** ASI03:2026 — Identity & Privilege Abuse. A request without caller
  credentials can inherit the server operator's authority at an outbound service.
- **Impact:** High; theoretical likelihood produces initial Medium severity.
- **Engine:** Python and TypeScript source flow from registered HTTP handlers to supported
  requests/httpx credential arguments and source-bound Jira/Confluence token or
  password constructor arguments, including caller headers obtained through
  the source-established SDK HTTP request getter.
- **Remediation:** Reject absent or invalid caller credentials before invoking the
  protected operation. Keep operator credentials separate from caller sessions.
- **False-positive risk:** An intentionally operator-authorized public service
  requires review of that authorization policy; merely omitting authentication
  does not establish permission to act with operator credentials.

The current implementation follows environment-derived operator credentials into
`auth` arguments, recognized credential fields in headers/parameters/payloads,
and the `token`/`password` keywords of imported `atlassian.Jira` and
`atlassian.Confluence` clients. Replaced imports, local impersonating modules and
caller-shadowed constructors do not establish those external sinks. Client URL
and username arguments alone are not treated as credential use. Explicit request
credentials are also recognized on source-established `httpx.Client`,
`httpx.AsyncClient`, `requests.Session` and `aiohttp.ClientSession` receivers.
URL and credential checks share that identity; method replacement and unknown
escape invalidate it. Session authentication, header and supported query defaults
flow to the actual request; constructing a session alone is not a credential sink.
Request overrides follow each supported library's authentication and mapping
precedence. Header names are case-insensitive, while query keys retain their case.
Httpx constructor/setter mappings are copied; requests member assignments retain
aliases. Known Basic Auth fields are tracked, including requests field mutation;
aiohttp default auth follows a known base origin, and conflicting auth/header
arguments are disclosed as invalid. Custom authentication hooks remain unresolved.
Receiver factories are evaluated
once per call, and positional argument effects precede credential keyword values.
It distinguishes caller-token rejection from checks of unrelated values and
values replaced after validation. Dictionary member writes, copies and helper
mutations retain the relevant credential selection. A local stdio tool's use of
its owner's credentials alone does not establish an HTTP caller boundary.

The integration also follows negative caller-authentication branches into a
separately constructed operator client, including helper calls. A successfully
acquired SDK HTTP context retains its branch state separately from the getter's
non-HTTP alternative. For a prepared HTTP request, constant local assignments
immediately after the genuine getter survive exception entry unless later writes
or nonlocal/global mutation invalidate them. Different caller-absence conditions
remain separate through a try/except's continuation when it has no `finally`.
General exception side effects remain a bounded-flow limitation.
Enforced environment comparisons can annotate a
fallback with the setting whose declared default would reject that path. The
candidate remains visible: the effective environment and intended authorization
policy still require review. Ignored checks, optional helper returns, replaced
predicates and a shared sink with an unqualified path do not establish that
qualification. Returned clients and credential fields retain the conditions under
which operator credentials were selected. An unguarded operator alternative removes
the qualification; unknown mutation cannot preserve it. This includes selecting
configuration initialized at startup; unrelated absence checks do not erase the
selected credential’s condition. Enforced literal allowlists retain possible
string choices across helpers. Known assigned fields remain present even when their values are unknown;
repeated lifespan analysis does not make declared dataclass fields optional.
The exposed Atlassian authentication pair and its helper-renaming mutations
completed at `34220b7`, with two vulnerable condition hits and no fixed-condition
alerts at the declared default. This is source adjudication, not runtime proof,
fresh holdout evidence or the final repeated benchmark.

TypeScript follows source-established Express module/factory route registrations,
including imported handlers, re-exports and ordered `use`/route middleware, into
global `fetch`, `node-fetch`, and
`undici.fetch` credential headers. It tracks `process.env` fallback selected by
`||`, `??`, or an enforced absent-token branch, and checks the actual caller
value when rejection returns or throws. Rebound application, environment and
request bindings remain unresolved. Plain request configurations retain header
updates through aliases, included helpers, named fields and literal string indexes.
Branch merges retain possible credential flow without treating an absent field
as an enforced guard. Unknown mutation and prototype replacement invalidate
protection. Python follows genuine `ContextVar` allocation,
defaults and request-local `get`/`set`/matching single-use `reset` through included
helpers, including token clearing and separate request state. These operations
follow the [Python context variable contract](https://docs.python.org/3/library/contextvars.html).
TypeScript middleware guards qualify the same caller value only when actual
`next()` forwarding reaches the callback. Unknown mount paths, error forwarding
and nested routers cannot establish protection. Literal arrays are bounded to
256 entries and synchronous continuation depth to 32; larger layouts remain
unresolved. Manual Python context switching and spawned tasks remain unsupported;
route tests do not establish SDK lifecycle conditions.

The genuine FastMCP HTTP getter retains current request state across included
helpers within a tool entry, following the
[SDK request-context contract](https://gofastmcp.com/v2/servers/context).
Separate tool entries do not inherit each other's state. This does not infer
middleware attachment from a class name or an unrelated HTTP route.

```python
token = request.headers.get("Authorization")
# Candidate: an unauthenticated caller selects the operator credential.
token = token or os.environ["OPERATOR_TOKEN"]
return requests.get("https://api.example.com/", headers={"Authorization": token})
```

The rule is enabled by default and produces canonical Finding evidence with
source locations and remediation. CLI regressions cover explicit rule selection,
inline suppression, baseline matching, and calculated severity thresholds. This integration remains incomplete for the
approved cross-middleware, service-factory and TypeScript conditions. Direct HTTP
regressions are not evidence that the historical or frozen development conditions
pass. See [Phase 22 implementation status](phase22-implementation-status.md) for
remaining measurement, reviewed-retention and acceptance gates.
