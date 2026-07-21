# Phase 4 GitHub Action evidence

Verified on 2026-07-21 (America/Los_Angeles) against the public
[`BashaarJavaid/mcp-sentinel-action-demo`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo)
repository.

## Immutable inputs

- Sentinel Action commit:
  [`ee91e07d0fa78106dbb6d85b60bd8288173abd23`](https://github.com/BashaarJavaid/MCP-Sentinel/commit/ee91e07d0fa78106dbb6d85b60bd8288173abd23),
  the commit used by the successful
  [`v0.1.0` release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/29686427335)
  and release.
- Demo repository commit:
  [`b516de0524ceaad64cedc031081dca580b8027ba`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/commit/b516de0524ceaad64cedc031081dca580b8027ba)
- Successful workflow run:
  [`29874088698`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29874088698)

## Results

- The clean job completed successfully. GitHub accepted category
  `mcp-sentinel/clean_server` with 0 results, 7 declared rules, and no processing
  error.
- The vulnerable Action step failed at `fail-on: high` as expected; the proof
  workflow observed exit code 1, asserted that failure, verified 11 findings at
  critical highest severity, and completed successfully. GitHub accepted category
  `mcp-sentinel/vulnerable_server` with 11 results, 11 declared rules, and no
  processing error.
- The Security tab exposes open alerts for every rule from
  [`SENT-001`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/security/code-scanning/1)
  through
  [`SENT-011`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/security/code-scanning/11),
  including all four dynamic probes.
- The vulnerable SARIF records complete live review through requested and
  returned model `gpt-5.6-sol`: 11 of 11 candidates reviewed, 10,155 current
  tokens, five accepted batches, no failed batches, and no overflow.
- The
  [clean SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29874088698/artifacts/8512314413)
  and
  [vulnerable SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29874088698/artifacts/8512323599)
  are retained until 2026-10-19. Both downloaded reports pass
  `python -m sentinel.report.validate_sarif` offline.

Fork behavior is covered with synthetic GitHub event tests in Phase 4. The live
fork-PR run remains the explicit Phase 5 follow-up selected during planning.
