# PortunusMCP Sentinel

## Current v38 regression pass and technical acceptance checkpoint

The separately approved **87-observation exposed regression passes** at frozen
scanner **`8c62567`**. All **87/87** inputs complete and all **36 entire ordered
repeats agree**, excluding only the established 11 volatile fields. Native JSON,
SARIF, source/configuration identities and process cleanup validate. **74**
observations finish within the **120-second target** and **13** use the approved
extended allowance. Maximum whole-input time is **157.750767 seconds**;
maximum native time is **148.514 seconds**, both within the uniform
**300-second maximum**. The single serial macOS sequence took
**3757.993 seconds**. Its **87-observation budget is closed**;
zero retries, profiles, comparators, corpus target executions or paid calls occurred.

DDG detects **both vulnerable variants in each batch**. All **six fixed/control
reports** support the actual prepared-request `client.send` and retain recognized
initial **100.64.0.0/10 rejection on the direct `web_fetch` caller route**. The
build/send calls are no longer unresolved. There are **zero matching alerts on
all three negative inputs per batch**. Broader SSRF findings remain visible;
other caller routes, later transformations, DNS, redirects, IPv6 and broader
destination protection remain unestablished. This resolves the requested actual
fixed-path coverage gate without accepting the earlier unsupported-path limitation.

Python development completes **15/15**: **six vulnerable condition hits**, **zero
matching alerts on seven valid negatives**, and the unchanged Meta operator
erratum: **two nominal fixed input cases, each with two raw matched candidate
keys**. Meta image fixed/control reports retain their narrow private-literal
qualification at all three request sinks. Each whole **31-input Python historical
batch** passes with **14 vulnerable hits and zero matching alerts on 17 negatives**.
All source labels, prerequisites and unrelated candidates remain unchanged.

Against the immediate `a50e9b7` regression, there are **15 description-only finding
changes**, individually assessed against exact retained source: six DDG direct-route
qualifications and nine Meta private-literal qualifications. No findings are added,
removed or reordered; no warnings, unresolved flows, coverage, surfaces or counters
change. Earlier source-assessed deltas against original references remain bound to
their actual reports. Raw scorer identities and unmatched broader candidates stay
visible. This is source-grounded static evidence, not runtime protection proof.

The original fresh repository **`isyuricunha/mcp-ddg-research`** remains measured
at pre-curation scanner **`f85a90f`**: **10 native + five Semgrep observations**,
two correlated vulnerable hits per native batch, zero matching negative alerts,
five whole ordered repeats, and **Semgrep 0/2**. Its original fixed-path coverage
gap remains recorded. The later `8c62567` correction is **exposed regression**;
it does not replace that first-frozen result. This is one repository and one narrow
vulnerability, curated by the implementation agent after scanner freeze, with
source exposure disclosed; no independent human review, broad accuracy or
training-data novelty is claimed.

Prior exposed TypeScript families, Lighthouse and TypeScript compatibility retain
their actual **`f85a90f` source-compatible evidence**. Historical whole Linux timing
retains **`1f3f72f`**: both whole 45-input batches pass, with the explicitly approved
reuse of the previously passed whole 25-input development batch. Current Python
and prior TypeScript subsets are **not pooled into a new whole-batch execution**.
All original misses, the failed `a50e9b7` regression, stopped experiments and closed
budgets remain preserved. No speedup or new fresh-source result is claimed.

Product, tests and workflows are unchanged from verified **`8c62567`**. Local and
all **12 hosted quality suites pass 2,283 tests / 36 skips**; local branch coverage
is **89.91%**. All **29 normal CI jobs** and docs pass at that
actual source. Package source bindings and six zero-call production replays retain
their verified source identities; final status-only documentation/package metadata
is checked separately. Existing Git runtime components/image remain compatible,
and **Git coverage stays incomplete at 312/1,040 attempts**, as the user requested.

The initial delivery preflight stopped before staging, commit or push because six
status-document hashes in the audit had not been refreshed after documentation
edits. The failed receipt and seal 65 remain preserved. Final documentation
bindings are corrected in supplemental seal 66; scanner and evaluation evidence
are unchanged.

The reconciled audit accounts for **89 original requirements: 86 passed, two
user-deferred and only R84 (human technical acceptance) unresolved**. All **108 added
scope rows** are retained: **103 passed and five historical closure dispositions
awaiting explicit acceptance**. Those five preserve the failed optimization,
stale-assessment sequence, reused-source preparation and two stopped Lighthouse
corrections; accepting their closure never converts failures into passes.

The concrete **technical acceptance proposal** is
`artifacts/phase22/integration/v38-guard-regression/acceptance-proposal-final.json`.
**Human technical acceptance has not been received; Phase 22 remains incomplete.**
Acceptance must explicitly cover the final technical scope and retained limitations,
then the authorized closeout must be delivered to existing draft PR #37. The full
paid benchmark and pilots remain user-deferred; Phase 21 remains incomplete and
Phase 24/15 gates are unchanged. No paid calls, further observations, merge,
ready-state change, release, outreach or Phase 23 is authorized by this packet.


[![PyPI](https://img.shields.io/pypi/v/portunusmcp-sentinel)](https://pypi.org/project/portunusmcp-sentinel/)
[![CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/BashaarJavaid/MCP-Sentinel/actions/workflows/ci.yml)
[![Documentation](https://github.com/BashaarJavaid/MCP-Sentinel/actions/workflows/docs.yml/badge.svg)](https://bashaarjavaid.github.io/MCP-Sentinel/)

**Build-time security scanning for MCP servers.**

PortunusMCP Sentinel scans local MCP server source before deployment. It combines
deterministic Python and TypeScript analysis, GPT-5.6 semantic review, optional
Docker-isolated runtime probes, OWASP Agentic Top 10 mappings, and validated
SARIF output for GitHub code scanning.

## Install

Sentinel supports Python 3.10–3.13 on Linux, macOS, and Windows. Install the
current package with [pipx](https://pipx.pypa.io/):

```bash
pipx install portunusmcp-sentinel
```

Or use uv:

```bash
uv tool install portunusmcp-sentinel
```

Rules-only commands below require **1.3.0 or newer**. Upgrade an existing install
with `pipx upgrade portunusmcp-sentinel` or `uv tool upgrade portunusmcp-sentinel`.

Reports expose observed handlers and recognition gaps, actual rule visits,
per-session runtime catalogs and sent attacks, and separate static/dynamic review
activity. Default findings include bounded evidence and repair guidance. Static
surface totals remain unknown; zero findings are not proof of safety. See the
[coverage and schema compatibility guide](docs/sarif.md#coverage-and-review-activity-native-160).
Phase 22 adds bounded imported handlers/schemas and containment flows;
computed registrations and unresolved source forms remain coverage gaps.
Permission sidecars express intended grants; they do not enforce runtime
boundaries. The Phase 22 integration source schedules bounded rounds across discovered
tools and supported fields (24 started attempts or 120 seconds by default).
Native 1.7.0 and campaign verification remain in progress; published releases
and historical evidence retain their recorded versions.

## Quickstart

From a local Python or TypeScript MCP server repository:

```bash
sentinel scan . --rules-only
```

Rules-only needs no model credentials, review cache, network, Docker, target
configuration, or target execution. It ignores inactive LLM settings even when
credentials and endpoint overrides are present. Installation and dependency
auditing need network access separately.

The Phase 22 integration source allows deterministic static analysis up to 300
seconds, with a 120-second performance target. Fast scans return immediately;
expiry remains an incomplete scan. Model review and dynamic budgets are separate.
See the [timing policy](docs/phase22-timeout-policy.md) for measurement limits and
the retained failures; this change is not yet a published release.

Optionally run `sentinel init` afterward to generate a deny-by-default
`sentinel.permissions.yaml`; review scopes before granting them. It never imports
or executes source and needs no main guard or launch inference. Existing files
require `--force` for replacement; symlinks are rejected.

For Python runtime scaffolding, run `sentinel init --dynamic`, then
`sentinel scan . --no-rules-only`. Adding missing runtime configuration preserves
and validates an existing permissions file. Dynamic scans require Docker,
model credentials, source-context transmission, and model cost; dependency
installation also needs network access. TypeScript does not support `--dynamic`.
If generated arguments cannot complete a legitimate tool call, add known valid
[`probe_baselines`](docs/configuration.md#dynamic-outcomes-and-valid-examples) to
`sentinel.target.yaml`; an unsuccessful baseline leaves analysis incomplete.

Exit `0` and exit `1` both mean the scan completed: `0` means no finding reached
the configured threshold, while `1` means at least one did. Exit `2` is a target
or configuration error; exit `3` means analysis was incomplete.

## Analysis tiers

| Tier | Command | Requirements | Result |
|---|---|---|---|
| Rules-only | `sentinel scan . --rules-only` | None beyond Sentinel | Deterministic findings remain `needs_review` and fail-on eligible |
| Static + GPT review | `sentinel scan . --static-only` | `OPENAI_API_KEY` | GPT reviews every selected deterministic candidate |
| Full dynamic proof | `sentinel scan .` | `OPENAI_API_KEY`, Docker, and a Python target | GPT review plus four isolated runtime probes |

`--allow-degraded` permits unavailable review; it still calls the model when a
key is available. Use `--rules-only` to disable review explicitly. Completion
describes the selected analysis tier and does not prove a server is secure.

TypeScript support is static-only and covers `.ts`, `.mts`, and `.cts` sources
using the official MCP SDK v1 and server v2 shapes. JavaScript, TSX, declaration
files and Node execution are outside the supported boundary. Declared uv, npm
and pnpm workspaces support aggregate static scans with root Sentinel settings.
Bounded local imports, package exports and TypeScript source aliases feed
containment and handler inventory. Other rules retain their documented flow
limits. Dynamic targets are individual local Python 3.10–3.12 MCP packages.

Version 1.3.0 includes Phase 16 static-correctness changes: same-file
named-helper execution flows and value-specific validation, authentication,
integrity, and configured-sanitizer checks. Unsupported flows remain unresolved;
see the [rule boundaries](docs/rules.md) and
[verification record](docs/phase16-verification.md).

Phase 17 source changes add validated dynamic baselines, explicit probe outcomes,
and proof-preserving review in native JSON 1.6.0. The current replay bundle uses
one approved runtime-review refresh and four unchanged static captures. See the
[Phase 17 verification record](docs/phase17-verification.md) for gates and acceptance status.

This integration source emits native JSON 1.7.0 with ordered runtime attempts
and workspace coverage. Final Phase 22 verification and acceptance remain open;
historical reports and release evidence retain their recorded schema versions.

## Rules

Every finding uses a stable rule ID and maps to the OWASP Agentic Top 10.

| Rule | Detection | OWASP | Impact |
|---|---|---|---|
| [SENT-001](docs/rules.md#sent-001) | Overly broad tool permission scope | ASI03:2026 | High |
| [SENT-002](docs/rules.md#sent-002) | Tool input reaches unsafe execution | ASI05:2026 | Critical |
| [SENT-003](docs/rules.md#sent-003) | Missing tool input validation | ASI02:2026 | Medium |
| [SENT-004](docs/rules.md#sent-004) | Unsanitized tool content enters a prompt | ASI01:2026 | High |
| [SENT-005](docs/rules.md#sent-005) | Hardcoded credential | ASI03:2026 | Critical |
| [SENT-006](docs/rules.md#sent-006) | Missing or ineffective route authentication | ASI03:2026 | High |
| [SENT-007](docs/rules.md#sent-007) | Unverified tool manifest | ASI04:2026 | Medium |
| [SENT-008](docs/rules.md#sent-008) | Out-of-scope tool execution | ASI02:2026 | Critical |
| [SENT-009](docs/rules.md#sent-009) | Size-limit breach or observed OOM/crash | ASI05:2026 | Medium |
| [SENT-010](docs/rules.md#sent-010) | Injection payload executed | ASI05:2026 | Critical |
| [SENT-011](docs/rules.md#sent-011) | Malformed schema input processed | ASI02:2026 | Low |
| [SENT-012](docs/rules.md#sent-012) | Path containment failure | ASI02:2026 | High |
| [SENT-013](docs/rules.md#sent-013) | Tool-description poisoning | ASI01:2026 | High |
| [SENT-014](docs/rules.md#sent-014) | Command option injection | ASI05:2026 | Critical |
| [SENT-015](docs/rules.md#sent-015) | Server-side request forgery | ASI02:2026 | High |
| [SENT-016](docs/rules.md#sent-016) | Unauthorized operator-credential fallback | ASI03:2026 | High |

Published IDs are compatibility contracts: an ID is never renumbered or reused
for a different detection. The [rule catalog](docs/rules.md) documents each
engine, boundary, false-positive risk, evidence, and remediation.

## GitHub Action

The Marketplace Action runs the full Python pipeline, validates SARIF before
upload, and preserves Sentinel's exit contract.

```yaml
name: PortunusMCP Sentinel

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  sentinel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - id: sentinel
        uses: BashaarJavaid/MCP-Sentinel@v1
        with:
          target-path: .
          fail-on: high
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

The Action exposes `sarif-path`, `findings-count`, and `highest-severity`.
Forked pull requests, where secrets are withheld, run visibly degraded analysis
and skip upload. High-assurance consumers can replace `@v1` with the immutable
commit SHA for the selected release.

## Architecture

```mermaid
flowchart LR
    A[Untrusted MCP repository] --> B[AST + Semgrep rules]
    B --> C[Canonical candidates]
    C --> D[GPT-5.6 semantic review]
    D --> E[Bounded ordered probe attempts]
    E --> F[Docker sandbox]
    F --> G[Reviewed dynamic evidence]
    D --> H[Deduplication + provenance merge]
    G --> H
    H --> I[Console]
    H --> J[JSON 1.7.0]
    H --> K[SARIF 2.1.0]
    K --> L[GitHub code scanning]
```

Static analysis never imports or executes target code. GPT receives bounded,
redacted context and can only review existing candidates or order four permanent
inert probes. Dynamic analysis mounts local Python source read-only in fresh
containers with no runtime network, resource limits, and forced cleanup. All
stages feed one canonical Finding model consumed by console, JSON, and SARIF.

PortunusMCP Sentinel is the build-time plane of the PortunusMCP family. The
[PortunusMCP Gateway](https://github.com/BashaarJavaid/PortunusMCP) provides
runtime enforcement in a separate repository, while PortunusMCP Identity is the
separate short-lived credential-broker plane. Neither is required by Sentinel.

## Configuration and adoption

Configuration precedence is CLI → `SENTINEL_*` environment → target-root
`sentinel.toml` → built-in defaults. A normal full scan also requires
`sentinel.target.yaml` and `sentinel.permissions.yaml`; `--static-only` does not
require launch configuration.

Create a baseline from a complete native JSON report, then compare later scans:

```bash
sentinel scan . --allow-degraded --format json --output sentinel-baseline.json
sentinel scan . --allow-degraded --baseline sentinel-baseline.json
```

Matched findings remain visible but do not affect `--fail-on`. Sentinel never
updates a baseline automatically.

Suppress a reviewed static source finding with a reason-bearing directive:

```python
# sentinel: ignore[SENT-005] reason=test credential is inert and rotated
api_key = "ghp_example"
```

Only static `SENT-001`–`SENT-007` and `SENT-012`–`SENT-016` findings can be suppressed. Applied
suppressions remain visible in every report; malformed, duplicate, unknown-rule,
or reasonless directives fail configuration validation.

Use Sentinel from pre-commit:

```yaml
repos:
  - repo: https://github.com/BashaarJavaid/MCP-Sentinel
    rev: v1.3.0
    hooks:
      - id: mcp-sentinel
```

See the [configuration guide](https://bashaarjavaid.github.io/MCP-Sentinel/configuration/)
for LLM endpoint trust, rule selection, baselines, suppressions, and pre-commit.

## CLI and report reference

```bash
# Full static, GPT, and Docker analysis
sentinel scan ./path/to/server

# Static analysis with required GPT review
sentinel scan ./path/to/server --static-only

# Validated SARIF
sentinel scan ./path/to/server --format sarif --output results.sarif

# Select rules and change the failure threshold
sentinel scan ./path/to/server --rules SENT-001,SENT-005 --fail-on critical

# Exercise the packaged reference pipeline
sentinel demo --replay-review --verbose
```

`--fail-on` accepts `critical`, `high`, `medium`, `low`, or `informational`.
Console output is the default; `--format json` and `--format sarif` are stable
machine-readable paths. Validate reports offline with:

```bash
python -m sentinel.schema check
python -m sentinel.report.validate_sarif results.sarif
```

The production reviewer uses GPT-5.6 Sol through the Responses API with
`store: false`, medium reasoning effort, strict Structured Outputs, bounded
context, and host-validated evidence. Sentinel's public OpenAI cost calculation
uses the rates recorded on 2026-09-04: $4/M input, $0.40/M cached input, and
$20/M output, with cache writes at 1.25× input. See the official
[GPT-5.6 Sol model and pricing page](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
and [Responses API create reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create).
Compatible endpoints retain token usage but report pricing as unavailable.

## Project resources

- [Scan a real MCP server before release](https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/)
- [Marketplace Action](https://github.com/marketplace/actions/mcp-sentinel)
- [Documentation](https://bashaarjavaid.github.io/MCP-Sentinel/)
- [Architecture contract](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [SARIF guide](https://bashaarjavaid.github.io/MCP-Sentinel/sarif/)
- [Changelog](CHANGELOG.md)
- [Security policy](SECURITY.md)
- [Project history](docs/hackathon.md)

PortunusMCP Sentinel is MIT licensed. Dependency licenses and packaged notices
are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
