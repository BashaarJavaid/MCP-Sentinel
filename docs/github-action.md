# GitHub Action

The Marketplace Action installs the pinned `portunusmcp-sentinel==1.2.0`
package, runs Sentinel, validates SARIF, uploads eligible reports to GitHub code
scanning, and preserves exit codes.

## Full scan

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

`target-path` must stay within the checked-out workspace. `fail-on` defaults to
`high`. Full scans are the default; set `static-only: "true"` only when Docker
probing is not required. `baseline` accepts a repository-relative native JSON
report.

The Action outputs:

- `sarif-path`: absolute path to the validated report.
- `findings-count`: all visible results, including suppressed findings.
- `highest-severity`: highest fail-eligible severity, excluding suppressed and
  baseline-matched findings.

Forked pull requests do not receive `OPENAI_API_KEY`. Sentinel makes that state
visible, runs degraded static analysis, and skips code-scanning upload. Other
missing review or upload requirements fail closed.

`BashaarJavaid/MCP-Sentinel@v1` follows the compatible v1 Action line. Consumers
that require an immutable supply-chain reference should pin the Action to the
full commit SHA of the selected release.
