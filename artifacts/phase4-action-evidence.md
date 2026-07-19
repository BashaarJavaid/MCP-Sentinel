# Phase 4 GitHub Action evidence

Verified on 2026-07-18 (America/Los_Angeles) against the public
[`BashaarJavaid/mcp-sentinel-action-demo`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo)
repository.

## Immutable inputs

- Sentinel Action commit:
  [`a8784d6adbb577a0bc40cb2f75e110d47aa92bc5`](https://github.com/BashaarJavaid/MCP-Sentinel/commit/a8784d6adbb577a0bc40cb2f75e110d47aa92bc5)
- Demo repository commit:
  [`08507cf3665dce0385a4b830dd3173283a5dc4e1`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/commit/08507cf3665dce0385a4b830dd3173283a5dc4e1)
- Successful workflow run:
  [`29667618119`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29667618119)

## Results

- The clean job completed successfully. GitHub accepted category
  `mcp-sentinel/clean_server` with 0 results, 7 declared rules, and no processing
  error.
- The vulnerable Action step failed at `fail-on: high` as expected; the proof
  workflow asserted that failure and completed successfully. GitHub accepted
  category `mcp-sentinel/vulnerable_server` with 11 results, 11 declared rules,
  and no processing error.
- The Security tab exposes open alerts for every rule from
  [`SENT-001`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/security/code-scanning/1)
  through
  [`SENT-011`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/security/code-scanning/11),
  including all four dynamic probes.
- The vulnerable SARIF records complete live review through requested and
  returned model `gpt-5.6-sol`: 11 reviewed findings and 10,138 current tokens.
- The
  [clean SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29667618119/artifacts/8436233676)
  and
  [vulnerable SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29667618119/artifacts/8436239130)
  are retained until 2026-10-17. Both downloaded reports pass
  `python -m sentinel.report.validate_sarif` offline.

Fork behavior is covered with synthetic GitHub event tests in Phase 4. The live
fork-PR run remains the explicit Phase 5 follow-up selected during planning.
