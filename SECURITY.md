# Security policy

## Dependency audit exceptions

`pip-audit` remains a blocking CI gate. Four advisories are temporarily and
explicitly excepted because the required Semgrep `1.170.0` package hard-pins
the affected transitive versions and uv correctly rejects patched overrides:

| Dependency | Pinned by Semgrep | Advisory | Fixed version |
|---|---:|---|---:|
| Click | `<8.2.dev0` | `PYSEC-2026-2132` | `8.3.3` |
| MCP | `==1.23.3` | `CVE-2026-52870` | `1.27.2` |
| MCP | `==1.23.3` | `CVE-2026-52869` | `1.27.2` |
| MCP | `==1.23.3` | `CVE-2026-59950` | `1.28.1` |

Remove each exception as soon as a compatible Semgrep release stops pinning
the affected version. No wildcard advisory or package exception is permitted.
All other current and future advisories continue to fail CI.
