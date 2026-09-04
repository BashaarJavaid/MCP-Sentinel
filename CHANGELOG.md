# PortunusMCP Sentinel changelog

All notable changes to PortunusMCP Sentinel are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Published `SENT-xxx` rule IDs are compatibility contracts: existing IDs are
never renumbered or reused for a different detection. Changed meanings receive
new rule IDs.

## [Unreleased]

## [1.2.1] - 2026-09-04

### Changed

- Rebranded public source and documentation surfaces as PortunusMCP Sentinel
  while preserving package, CLI, rule, schema, and SARIF driver identities.
- Added contributor issue/PR paths, bounded Dependabot updates, and a strict
  MkDocs Material site deployed through GitHub Pages.

- Added a pinned real-server walkthrough, launch evidence, and private
  vulnerability-reporting guidance.

### Fixed

- Prevented cold Semgrep startup on Windows from exhausting the per-file
  timeout before static analysis begins.

## [1.2.0] - 2026-09-04

### Added

- Incremental JSON baselines with stable static/dynamic evidence matching,
  visible matched/new findings, aggregate resolved counts, and fail-threshold
  isolation.
- Auditable reason-bearing inline suppression for included Python and TypeScript
  source, including unused-directive warnings and SARIF `inSource` records.
- A public `mcp-sentinel` pre-commit hook and a baseline input for the composite
  GitHub Action.
- Static-only TypeScript analysis for official MCP SDK v1 and server v2 targets,
  retaining `SENT-001`–`SENT-007`, GPT review, and canonical reports.
- TypeScript-aware `sentinel init`, tool catalog extraction, paired fixtures,
  and installed-wheel scan gates without installing or executing Node packages.
- Configurable GPT review model, reasoning effort, and Responses-compatible
  `/v1` endpoint support through project, environment, and CLI configuration.
- Endpoint provenance in native JSON 1.4.0 and SARIF reports, with compatible
  endpoint pricing reported as unavailable.
- `sentinel init` safely inspects Python MCP repositories and atomically creates
  validated starter target and deny-by-default permissions configuration.
- First-run documentation now distinguishes rules-only degraded, static-plus-GPT,
  and full Docker analysis prerequisites.

### Changed

- The package and composite Action now share exact version `1.2.0`.
- Baseline-matched and inline-suppressed findings remain visible but are excluded
  from failure-threshold and highest-severity calculations.
- MCP-aware static rules now report the hybrid engine label shared by Python AST
  and TypeScript recognition.
- Missing `OPENAI_API_KEY` failures now explain how to enable GPT review or keep
  rules-only candidates visible with `--allow-degraded`.

### Security

- Repository-configured compatible endpoints now require explicit operator
  trust, while endpoint URLs are validated, hashed for provenance, and redacted
  from diagnostics.
- Ambient OpenAI base URLs and custom headers are rejected so repository and SDK
  configuration cannot bypass Sentinel's endpoint trust boundary.

## [1.0.0] - 2026-09-03

### Added

- GitHub Marketplace distribution through the stable `v1` Action reference.

### Changed

- The composite Action now installs the corresponding exact Sentinel release
  from public PyPI instead of building the package from its checkout.
- Exact release tags continue to publish Python distributions, while movable
  major-version Action aliases do not trigger the PyPI workflow.
- Release gates pin the newest pipx version compatible with Sentinel's tested
  packaging dependency range.

## [0.2.0] - 2026-09-03

### Added

- Python 3.13 host-runtime and CI support.
- PyPI metadata and isolated installation checks for pip, pipx, and uv.
- Attested TestPyPI-to-PyPI publishing through GitHub OIDC.

### Changed

- Renamed the distribution to `portunusmcp-sentinel` while retaining the
  `sentinel` import package and command.
- Replaced the exact MCP and OpenAI requirements with tested compatible ranges.
- Updated the exact Semgrep compatibility contract to 1.176.0 and MCP to 1.29.0.

### Security

- Removed four dependency-audit exceptions after upgrading the Semgrep-pinned
  MCP and Click versions past their recorded fixes.

## [0.1.0] - 2026-07-20

### Added

- Initial MCP Sentinel CLI with seven static rules, GPT-5.6 semantic review and
  replay, four Docker-isolated dynamic probes, console/JSON/SARIF reports, and a
  composite GitHub Action.

[Unreleased]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.0.0...v1.2.0
[1.0.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v0.1.0
