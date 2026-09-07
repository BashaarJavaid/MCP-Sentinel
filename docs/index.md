# PortunusMCP Sentinel

**Build-time security scanning for MCP servers.**

PortunusMCP Sentinel finds security problems in local MCP server repositories
before deployment. It combines deterministic Python and TypeScript checks,
GPT-5.6 semantic review, Docker-isolated runtime probes for Python targets, OWASP
Agentic Top 10 mappings, and SARIF output for GitHub code scanning.

The rules-only commands below require **1.3.0 or newer**; see
[installation and upgrades](install.md).

## Start without credentials or Docker

```bash
pipx install portunusmcp-sentinel
cd your-mcp-server
sentinel scan . --rules-only
```

`sentinel init` is optional and generates only the permissions sidecar.
Rules-only performs no model/cache/network/Docker operations or target execution.
Installation and Action upload have separate network requirements.

Exit `0` and exit `1` both mean analysis completed. Exit `1` means at least one
finding reached the configured failure threshold.

## Choose an analysis tier

| Tier | Command | Requirements |
|---|---|---|
| Rules-only | `sentinel scan . --rules-only` | Sentinel only |
| Static + GPT review | `sentinel scan . --static-only` | `OPENAI_API_KEY` |
| Full dynamic proof | `sentinel scan .` | `OPENAI_API_KEY`, Docker, Python target |

Start with [installation](install.md), then review [configuration](configuration.md)
and the [rule catalog](rules.md). For CI, use the [GitHub Action](github-action.md).

## Measured effectiveness

The [accepted independent benchmark](phase20-acceptance.md) records 45 labeled
inputs across five repositories. Both static tiers completed 32 inputs and
detected none of the 14 vulnerable inputs whose scans completed. Review captures
are complete; execution failures and unsupported runtime scope remain explicit.
This baseline guides further work and does not establish broad detection accuracy.

## PortunusMCP family

Sentinel is the build-time security plane of PortunusMCP. The
[PortunusMCP Gateway](https://github.com/BashaarJavaid/PortunusMCP) is the
separate runtime enforcement plane, and PortunusMCP Identity is the separate
short-lived credential-broker plane. Sentinel does not require either project.
