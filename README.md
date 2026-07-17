# MCP Sentinel

**Shift-left security scanning for MCP (Model Context Protocol) servers.**

MCP Sentinel is a build-time static and dynamic analysis tool that catches security vulnerabilities in MCP servers *before* they reach production — prompt injection vectors, over-permissioned tool definitions, insecure auth flows, and more. It maps every finding to the OWASP Agentic Top 10 and drops straight into CI as a CLI tool or GitHub Action with SARIF output.

Sentinel is the shift-left counterpart to runtime gateways: instead of only containing threats at request time, it flags the underlying bugs at the source, on every commit and PR.

> **Implementation status:** Phase 0 is complete: packaging, strict configuration
> and Finding/report contracts, console/JSON/SARIF shells, offline schema
> validation, and CI are implemented. Detection engines intentionally remain
> incomplete until Phases 1–3. A Phase 0 scan exits `3` and cannot be mistaken
> for a clean security result.

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

## Planned product features

- 🔍 **Static analysis** of MCP server source, tool schemas, and configuration
- ⚡ **Dynamic analysis** — exercises running MCP servers with adversarial inputs
- 🧭 **OWASP Agentic Top 10 mapping** for every finding
- 🛠️ **CLI tool** for local development and ad-hoc scans
- 🤖 **GitHub Action** for automated scanning on every PR
- 📄 **SARIF output** — integrates natively with GitHub code scanning and other CI security dashboards
- 🧩 Part of the [SecureMCP suite](#related-projects) — pairs with a runtime enforcement gateway and a credential broker for full lifecycle coverage

## Phase 0 development installation

```bash
uv sync --extra dev
uv run sentinel --version
```

The pip-compatible development path is `pip install -e ".[dev]"`. The package
is not published to PyPI in Phase 0.

## Usage

### CLI

```bash
# Inspect the CLI
sentinel scan --help

# Exercise the report shell. This intentionally exits 3 until detectors exist.
sentinel scan ./path/to/mcp-server --format sarif --output results.sarif

# Run the self-contained Phase 0 scaffold demo (also exits 3 by design)
sentinel demo

# Regenerate/check native schemas and validate SARIF fully offline
python -m sentinel.schema generate
python -m sentinel.schema check
python -m sentinel.report.validate_sarif results.sarif
```

A normal scan requires `sentinel.target.yaml` because dynamic analysis is the
eventual default. `--static-only` is the sole way to omit target launch
configuration. Only local Python MCP/FastMCP repositories over stdio are
accepted.

### GitHub Action

The end-user composite Action is Phase 4 work. This repository currently has a
Python 3.10–3.12 CI workflow for the Phase 0 quality and packaging gates.

## Example output

```text
MCP Sentinel 0.1.0
Target: scaffold_target
Status: INCOMPLETE
Findings: 0

Pipeline stages:
  static: skipped — not implemented in Phase 0
  gpt_static: skipped — not implemented in Phase 0
  dynamic: skipped — not implemented in Phase 0
  gpt_dynamic: skipped — not implemented in Phase 0
  merge: skipped — not implemented in Phase 0
  reporting: succeeded
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
