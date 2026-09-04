# Install

## Supported hosts

PortunusMCP Sentinel runs on Python 3.10–3.13 on Linux, macOS, and Windows. The
GitHub Action runs on Ubuntu. Full dynamic scans require Docker Engine or Docker
Desktop with Buildx; Windows must use Linux containers.

Install the current package in an isolated environment:

```bash
pipx install portunusmcp-sentinel
```

The uv equivalent is:

```bash
uv tool install portunusmcp-sentinel
```

Pin `portunusmcp-sentinel==1.2.0` only for exact reproducibility. Stable `1.2.0`
artifacts still display the former runtime label until the next release.

Confirm the command is available:

```bash
sentinel --version
```

## Source checkout

```bash
git clone https://github.com/BashaarJavaid/MCP-Sentinel.git
cd MCP-Sentinel
uv sync --extra dev --extra docs
uv run sentinel --version
```

The pip-compatible development install is `pip install -e ".[dev,docs]"`.

## Supported targets

Python static analysis supports local MCP/FastMCP repositories. Dynamic analysis
supports local Python 3.10–3.12 targets and always runs them in Docker.

TypeScript support is static-only. It recognizes `.ts`, `.mts`, and `.cts`
source using official MCP SDK v1 and server v2 shapes. It does not execute Node,
package scripts, or dependency installation. JavaScript, TSX, declarations,
workspaces, imported handlers or schemas, and cross-file dataflow are outside
the supported boundary.

## First scan

```bash
cd your-mcp-server
sentinel init
# Review sentinel.permissions.yaml before granting scopes.
sentinel scan . --static-only --allow-degraded
```

`sentinel init` never imports target code. For Python it creates starter target
and permissions configuration when safely detectable. For TypeScript it creates
only `sentinel.permissions.yaml`. Existing files are preserved unless `--force`
is passed, and symlink destinations are refused.
