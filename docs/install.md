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

The rules-only interface requires **1.3.0 or newer**. Upgrade an existing install
with `pipx upgrade portunusmcp-sentinel` or `uv tool upgrade portunusmcp-sentinel`.

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
sentinel scan . --rules-only
```

Optional: run `sentinel init` to generate only `sentinel.permissions.yaml` for
Python or TypeScript. No launch inference, main guard, runtime installation,
import, or execution is required. Existing files require `--force` for
replacement; symlinks are rejected and writes are atomic.

For Python Docker probing, use `sentinel init --dynamic`. It creates runtime
configuration and preserves validated existing permissions during an upgrade.
Then run `sentinel scan . --no-rules-only`. Review requires model credentials,
transmits bounded redacted source context, and incurs model costs. Docker and
target dependency installation are separate prerequisites. TypeScript rejects
`init --dynamic`.

After dependency installation, rules-only scanning needs no network. Installing
dependencies, auditing dependencies, and the Action's SARIF upload have separate
network requirements. A completed scan is not proof of security.
