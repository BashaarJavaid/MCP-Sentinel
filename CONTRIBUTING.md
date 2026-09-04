# Contributing to PortunusMCP Sentinel

Open an issue before proposing a new rule, behavior change, or architecture
change. Direct fixes and documentation pull requests may be opened without one.

## Local checks

```bash
uv sync --extra dev --extra docs
make check
```

`make check` is the required local gate. Run the focused test while developing,
and include its result plus any relevant hosted CI run in the pull request.
`make artifacts-check` verifies historical generated evidence separately.

## Contributor contracts

- Maintainers allocate new `SENT-xxx` IDs. Published IDs are never renamed,
  renumbered, or reused for another detection.
- Every rule emits the canonical Finding model consumed by console, JSON, and
  SARIF. Do not add rule-specific output shapes.
- Every rule change includes paired vulnerable and clean fixture expectations.
- Static analysis never imports or executes target code.
- Dynamic analysis executes local Python targets only through the existing
  Docker isolation boundary, never against a live endpoint by default.
- SARIF changes must continue to validate against the vendored 2.1.0 schema.

For a rule, prove the assigned ID, severity, OWASP mapping, evidence, and
remediation against the vulnerable fixture and prove no finding against the
clean fixture. Record accepted rules in `docs/rule-acceptance.md` and run the
relevant hosted OS/Python gates.

Add an Unreleased changelog entry for user-visible behavior or documentation
changes. Internal refactors and test-only changes do not need one.

The full process is documented in the [contribution
guide](https://bashaarjavaid.github.io/MCP-Sentinel/contributing/). This project
does not require a DCO, CLA, Code of Conduct, or CODEOWNERS approval.
