# GitHub Action

The prepared Action pins `portunusmcp-sentinel==1.3.0`
package, runs Sentinel, validates SARIF, uploads eligible reports to GitHub code
scanning, and preserves exit codes. **1.3.0 publication is separately authorized
and still pending**; this new pin becomes usable only after release verification.
The existing published Action retains its previous behavior.

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

Add `rules-only: "true"` for keyless offline scanning. The optional input defaults
to empty, inheriting environment/project configuration; explicit `"true"` or
`"false"` overrides it through the CLI. Ordinary runs remain eligible for SARIF
upload. Installation and upload use the network separately from scanning.

Forked pull requests never receive model credentials and always skip upload.
With rules-only selected, summaries label intentionally skipped GPT review.
Legacy reviewed fork runs retain `--allow-degraded` fallback. Missing required
review or ordinary upload requirements still fail closed.

`BashaarJavaid/MCP-Sentinel@v1` follows the compatible v1 Action line. Consumers
that require an immutable supply-chain reference should pin the Action to the
full commit SHA of the selected release.
