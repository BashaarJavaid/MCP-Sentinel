# Changelog

All notable changes to MCP Sentinel are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Published `SENT-xxx` rule IDs are compatibility contracts: existing IDs are
never renumbered or reused for a different detection. Changed meanings receive
new rule IDs.

## [Unreleased]

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

[Unreleased]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v0.1.0
