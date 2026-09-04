# SARIF

Generate a SARIF 2.1.0 report without mixing diagnostics into stdout:

```bash
sentinel scan . --format sarif --output results.sarif
```

Both completed exit codes (`0` and `1`) produce a report. Exit `1` means a
finding reached `--fail-on`; it does not mean report generation failed.

## Offline validation

Sentinel validates SARIF before writing it. Validate an existing file against
the vendored official OASIS schema with:

```bash
python -m sentinel.report.validate_sarif results.sarif
```

Success is silent with exit `0`; invalid SARIF is an infrastructure failure.

## Provenance

The SARIF driver keeps the stable `MCP Sentinel` identity used by existing code
scanning integrations and uses `PortunusMCP Sentinel build-time MCP security
scanner` as its public full name. Results retain rule ID, OWASP category,
severity, status, confidence, remediation, evidence references, static/dynamic
provenance, and GPT review mode. Host-absolute paths and endpoint URLs are not
serialized.

Inline suppressions use native SARIF `inSource` suppressions while preserving
their reason and directive location in result properties. Baseline-matched
findings remain results with `baselineMatched: true`; they are not removed.

## GitHub code scanning

The [composite Action](github-action.md) validates SARIF before upload. GitHub
creates alerts from visible results and preserves stable `SENT-xxx` rule IDs.
Fork pull requests run without repository secrets and therefore skip upload;
non-fork runs remain fail-closed if required analysis or upload fails.

`artifacts/example.sarif` is retained as historical evidence and is not
regenerated for a documentation-only change.
