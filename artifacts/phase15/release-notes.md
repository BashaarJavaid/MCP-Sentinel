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

Verified release commit: `9fae385c684781f12702f50cbae60a6cfc48c867`.

- [Release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33932405826): all 43 jobs passed, including TestPyPI verification, protected PyPI promotion, provenance, and Linux/macOS/Windows Python 3.10–3.13 installs. Four initial public installs encountered stale PyPI index responses and passed on a failed-job-only retry; no artifacts were republished.
- Public artifact provenance: [wheel](https://pypi.org/integrity/portunusmcp-sentinel/1.2.1/portunusmcp_sentinel-1.2.1-py3-none-any.whl/provenance) and [source archive](https://pypi.org/integrity/portunusmcp-sentinel/1.2.1/portunusmcp_sentinel-1.2.1.tar.gz/provenance).
- [Exact v1.2.1 clean Action proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33933771928) and [signed v1 clean proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33933933476) passed with complete, validated, uploaded SARIF and zero findings. Both signed refs resolve to the release commit.
- The published-package walkthrough reproduced zero findings across five files; SENT-001 was skipped for absent permissions. This is not a claim that the target is vulnerability-free.
- Current positive evidence comes from installed-wheel Docker replay, with recorded GPT responses and fresh probes. Historical positive code-scanning upload proof remains [v0.1.0, verified 2026-07-21](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase4-action-evidence.md). The new clean Action runs are integration proof, not fresh positive-alert proof.

SHA-256:

```text
143230824f214ac8d374d3c9850d2de8e4f568a069bc227f326722376140be94  portunusmcp_sentinel-1.2.1-py3-none-any.whl
753ea10b8256e0d91a9902d0473b817a73e740c5daca992360f6bb0a4fd5a38a  portunusmcp_sentinel-1.2.1.tar.gz
```
