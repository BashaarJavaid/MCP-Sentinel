# MCP Sentinel

**Shift-left security scanning for MCP (Model Context Protocol) servers.**

MCP Sentinel is a build-time static and dynamic analysis tool that catches security vulnerabilities in MCP servers *before* they reach production — prompt injection vectors, over-permissioned tool definitions, insecure auth flows, and more. It maps every finding to the OWASP Agentic Top 10 and drops straight into CI as a CLI tool or GitHub Action with SARIF output.

Sentinel is the shift-left counterpart to runtime gateways: instead of only containing threats at request time, it flags the underlying bugs at the source, on every commit and PR.

> **Implementation status:** Phases 0–2 are complete. GPT-5.6 prompt v3 passes
> the live contract smoke, medium truth-set quality gate, low-effort comparison,
> deterministic replay demo, and generated static ablation gate. Phase 3
> dynamic analysis is not implemented.

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

## Product scope

- ✅ **Static analysis** of MCP server source, tool schemas, and configuration
- 🧠 **GPT-5.6 semantic review** of every deterministic candidate, with grounded
  evidence and constrained dynamic-probe planning
- ⚡ **Dynamic analysis** — exercises running MCP servers with adversarial inputs
- 🧭 **OWASP Agentic Top 10 mapping** for every finding
- 🛠️ **CLI tool** for local development and ad-hoc scans
- 🤖 **GitHub Action** for automated scanning on every PR
- 📄 **SARIF output** — integrates natively with GitHub code scanning and other CI security dashboards
- 🧩 Part of the [SecureMCP suite](#related-projects) — pairs with a runtime enforcement gateway and a credential broker for full lifecycle coverage

## Development installation

```bash
uv sync --extra dev
uv run sentinel --version
```

The pip-compatible development path is `pip install -e ".[dev]"`. The package
is not published to PyPI yet.

## Usage

### CLI

```bash
# Inspect the CLI
sentinel scan --help

# Run static analysis, required live GPT review, then available later stages.
# Normal scans still exit 3 because Phase 3 dynamic probing is incomplete.
sentinel scan ./path/to/mcp-server --format sarif --output results.sarif

# Complete static analysis plus GPT review; exits 0 or 1 based on --fail-on.
sentinel scan ./path/to/mcp-server --static-only

# Explicitly permit a complete, prominently degraded static-only scan when GPT
# is unavailable. Findings remain needs_review and still participate in fail-on.
sentinel scan ./path/to/mcp-server --static-only --allow-degraded

# Run all seven static rules against the vulnerable reference fixture.
sentinel demo

# Regenerate/check native schemas and validate SARIF fully offline
python -m sentinel.schema generate
python -m sentinel.schema check
python -m sentinel.report.validate_sarif results.sarif
```

A normal scan requires `sentinel.target.yaml`. `--static-only` omits target
launch configuration but does not omit semantic review. Candidate-bearing live
reviews read `OPENAI_API_KEY` from the process environment; the value is never
printed, persisted, cached, or forwarded to target code. Missing access fails
closed with exit `3` unless `--allow-degraded` is explicit.

### GitHub Action

The end-user composite Action is Phase 4 work. This repository currently has a
Python 3.10–3.12 CI workflow for the Phase 0–1 quality and packaging gates.

## Example output

```text
MCP Sentinel 0.1.0
Target: vulnerable_server
Status: INCOMPLETE
Static findings: 7

Rules:
  SENT-001: evaluated, 1 match(es)
  ...
  SENT-007: evaluated, 1 match(es)

Pipeline stages:
  static: succeeded
  gpt_static: succeeded
  dynamic: skipped — not implemented until Phase 3 dynamic probing
  gpt_dynamic: skipped — not implemented until Phase 3 dynamic probing
  merge: skipped — not implemented until Phase 3 dynamic probing
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
