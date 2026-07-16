# MCP Sentinel

**Shift-left security scanning for MCP (Model Context Protocol) servers.**

MCP Sentinel is a build-time static and dynamic analysis tool that catches security vulnerabilities in MCP servers *before* they reach production — prompt injection vectors, over-permissioned tool definitions, insecure auth flows, and more. It maps every finding to the OWASP Agentic Top 10 and drops straight into CI as a CLI tool or GitHub Action with SARIF output.

Sentinel is the shift-left counterpart to runtime gateways: instead of only containing threats at request time, it flags the underlying bugs at the source, on every commit and PR.

---

## Why Sentinel

MCP servers expose tools, resources, and prompts to AI agents — often with far more trust and reach than a typical API endpoint. A single overly-permissive tool schema or unsanitized prompt template can let an agent be manipulated into leaking data, escalating privileges, or taking unintended actions. Most of these issues are visible in the code and config *before* deployment — if something is actually looking for them.

Sentinel looks for them.

## What it checks

- **Prompt injection surfaces** — unsanitized user/tool input flowing into prompt templates
- **Over-permissioned tool definitions** — tools requesting broader scopes/capabilities than their function needs
- **Insecure auth flows** — weak or missing credential handling, hardcoded secrets, unsafe token storage
- **Unsafe tool composition** — tool chains that could be combined to bypass intended guardrails
- **Schema and input validation gaps** — missing or overly permissive JSON schema constraints on tool inputs

Every finding is mapped to the relevant category in the **OWASP Agentic Top 10**, with a severity rating and a suggested remediation.

## Features

- 🔍 **Static analysis** of MCP server source, tool schemas, and configuration
- ⚡ **Dynamic analysis** — exercises running MCP servers with adversarial inputs
- 🧭 **OWASP Agentic Top 10 mapping** for every finding
- 🛠️ **CLI tool** for local development and ad-hoc scans
- 🤖 **GitHub Action** for automated scanning on every PR
- 📄 **SARIF output** — integrates natively with GitHub code scanning and other CI security dashboards
- 🧩 Part of the [SecureMCP suite](#related-projects) — pairs with a runtime enforcement gateway and a credential broker for full lifecycle coverage

## Installation

```bash
pip install mcp-sentinel
```

Or use it directly in CI via the GitHub Action (see below).

## Usage

### CLI

```bash
# Scan a local MCP server project
sentinel scan ./path/to/mcp-server

# Output as SARIF for CI ingestion
sentinel scan ./path/to/mcp-server --format sarif --output results.sarif

# Run dynamic checks against a live server
sentinel scan --dynamic --endpoint http://localhost:8000
```

### GitHub Action

```yaml
- name: Run MCP Sentinel
  uses: <org>/mcp-sentinel-action@v1
  with:
    path: ./mcp-server
    format: sarif
    output: results.sarif

- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

## Example output

```
$ sentinel scan ./mcp-server

MCP Sentinel — 3 findings

[HIGH]   Over-permissioned tool schema
         tools/delete_record.py:12
         OWASP Agentic Top 10 — A03: Excessive Agency
         Tool grants unscoped filesystem write access; scope to specific paths.

[MEDIUM] Unsanitized prompt template input
         prompts/summarize.py:44
         OWASP Agentic Top 10 — A01: Prompt Injection
         User-supplied field interpolated directly into system prompt.

[LOW]    Missing input schema constraints
         tools/search.py:8
         OWASP Agentic Top 10 — A07: Insecure Output Handling
         `query` parameter accepts unbounded string; add maxLength.
```

## Related projects

Sentinel is one piece of the **SecureMCP** suite, a set of independent, zero-trust-aligned tools for securing agentic AI systems end-to-end:

| Project | Role |
|---|---|
| **SecureMCP Gateway** | Runtime zero-trust gateway — RBAC/ABAC policy enforcement, risk scoring, signed audit logs |
| **MCP Sentinel** *(this repo)* | Build-time static/dynamic scanner, OWASP Agentic Top 10 mapped |
| **SecureMCP Identity** | Short-lived credential broker — OAuth 2.1, Dynamic Client Registration, SPIFFE/SPIRE-style workload identity |

Each project runs independently, mirroring how tools like SPIRE and Vault operate as separate trust planes rather than a single monolith.

## Roadmap

- [ ] IDE plugin (VS Code) for inline findings
- [ ] Expanded dynamic fuzzing corpus for tool-chain abuse cases
- [ ] Policy-as-code rule authoring for custom checks
- [ ] Baseline diffing to flag only new findings in PRs

## Contributing

Issues and PRs welcome. Please open an issue describing the vulnerability class or false positive/negative before submitting a fix, so it can be traced back to an OWASP Agentic Top 10 category.

## License

MIT
