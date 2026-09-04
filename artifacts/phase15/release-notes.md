# PortunusMCP Sentinel 1.2.1

PortunusMCP Sentinel scans MCP server source before deployment and pairs static
candidates with GPT review, isolated Python runtime probes, and SARIF reports.

This maintenance release brings the PortunusMCP branding to installed console
output, adds the public documentation and pinned real-server walkthrough, and
fixes cold Semgrep startup exhausting the Windows scan deadline. Private
vulnerability reporting and contributor/maintenance guidance are now available.
No scanner capabilities, dependencies, stable rule IDs, or Action inputs/outputs
were added. Native JSON remains 1.4.0 and SARIF remains 2.1.0.

```sh
pipx install portunusmcp-sentinel==1.2.1
sentinel scan /path/to/server --static-only --allow-degraded
```

Rules-only Python/TypeScript scans need no key or Docker. Static GPT review needs
an operator key; full probing additionally needs Docker and a Python target.
`sentinel demo --replay-review` runs fresh isolated fixture probes with recorded
GPT responses, without new model calls.

- [Walkthrough and coverage limits](https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/)
- [Changelog](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/CHANGELOG.md)
- [PyPI](https://pypi.org/project/portunusmcp-sentinel/1.2.1/)
- [Marketplace](https://github.com/marketplace/actions/mcp-sentinel)
- [Security policy](https://github.com/BashaarJavaid/MCP-Sentinel/security/policy)
- [2:45 demo: older MCP Sentinel v0.1.0 branding and historical alerts](https://www.youtube.com/watch?v=0myxPyTDx2c&t=3s)

Release approval and publication are pending. Append verified release workflow,
TestPyPI/PyPI provenance, public installation, and clean exact-tag/alias Action
proof URLs before publishing these notes. Clean Action proof is not new positive
code-scanning alert evidence; that historical evidence remains dated separately.
