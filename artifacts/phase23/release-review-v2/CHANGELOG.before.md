# PortunusMCP Sentinel changelog

All notable changes to PortunusMCP Sentinel are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Published `SENT-xxx` rule IDs are compatibility contracts: existing IDs are
never renumbered or reused for a different detection. Changed meanings receive
new rule IDs.

## [Unreleased]

### Fixed

- Follow unique local TypeScript star exports while retaining ambiguity, rebinding,
  source-root and default-export boundaries.
- Preserve proved Node promisify wrappers around exec/execFile for static rule
  analysis, rejecting unproved factory/target identities and escaped wrappers.
- Analyze registered MCP handlers with a separate invocation stack, preserving
  genuine recursion checks, nesting limits and registration-stack restoration.
- Follow proved composed Zod field metadata through describe, extend and shape,
  preserving source descriptions, original schemas and mutation/escape boundaries.
- Recover source-established Python module-table tool dispatch, preserving
  unsupported status for ambiguous, replaced or escaped routing bindings.
- Preserve module-table dispatch through literal dictionary metadata copies,
  rejecting dynamic mappings, mutable aliases and builtin namespace changes.
- Preserve global constructor instances when following nested bound methods,
  retaining the actual receiver for filesystem guard analysis.
- Follow supported TypeScript constructor parameter properties with the bound
  argument/default value, preserving receiver replacement and escape checks.
- Preserve narrow initial URL guard evidence across trailing-slash removal and
  path suffixes only when the checked destination remains established.
- Allow deterministic static scans a 30-minute shared deadline; retain the
  two-minute target as informational and preserve incomplete results on expiry.
- Merge equal credential markers consistently regardless of cache interning, and
  bypass cache dispatch for the canonical unknown singleton without a key override.
- Recover actual startup through imported TypeScript classes, checked path-return
  facts, and source-bound Python imports. Keep reconstructed paths as qualified
  candidates instead of treating a guard on a resolved copy as full protection.
- Accept comments and trailing commas in devcontainer JSON configuration while
  retaining original source evidence and rejecting malformed content.
- Include Git in pinned Python runtime images and include the base-image digest
  in dependency cache keys so outdated runtime images are not reused.
- Recognize nullable and union field types consistently when validating GPT
  injection/oversized probe bindings and determining probe-plan eligibility.
  Preserve the original Phase 20 measurements separately from this correction.

### Added

- Source-flow rules for path containment (`SENT-012`), tool-description poisoning
  (`SENT-013`), command option injection (`SENT-014`), server-side request forgery
  (`SENT-015`), and unauthorized operator-credential fallback (`SENT-016`), with
  bounded Python/TypeScript support and explicit unresolved-source limitations.
- Add a seven-input, current-candidate offline advisory regression to routine
  PR and release CI, with reviewed complete-report references and retained
  failures, diagnostics and support evidence.
- Missed-vulnerability intake, current rule choices, optional example reuse consent,
  and maintainer guidance for source label review, weekly SDK/advisory checks,
  lifecycle timing evidence and offline regression releases.

- Native report schema 1.7.0: observed static handler inventory and actual rule
  visits, per-session runtime discovery and sent-call flags, and separate static
  and dynamic review activity. Ordered runtime attempts and workspace coverage
  preserve explicit eligibility, completion and unavailable-source information.
  Unknown historical coverage remains null.
- Default console and SARIF messages show bounded decisive evidence, remediation,
  recognition gaps, unprobed tools/fields, and explicit coverage limits.

### Changed

- Reuse the first completed TypeScript branch invalidation set under the private
  monotone-set contract, preserving independent arm analysis and conservative joins.
- Reuse completed TypeScript tool discovery across rule workers and coverage,
  preserving ordered warnings, source identities and the shared deadline.
- Reuse equal, present TypeScript branch values before preparing record fallbacks,
  retaining conservative guard and missing-state merges.
- Avoid constructing unused record fallbacks when merging TypeScript branches.
- Cancel superseded PR CI/documentation runs and build distributions alongside
  source checks while retaining the full platform matrix and release gates.
- Empty enabled review uses `not_run`; it does not imply live/replay activity.
  Baseline resolved counts are qualified as findings not observed in this scan.
- Accept native 1.3–1.7 baselines through in-memory migration, preserving matching,
  canonical findings, suppressions, model contracts, and exit-code semantics.
  Phase 19's final gate is accepted; historical captures remain unchanged.

## [1.3.0] - 2026-09-06

### Added

- Add explicit rules-only CLI/config/environment selection and Action input;
  bypass model clients, review cache, network, Docker, and target execution.
- Default `init` generates only permissions; migrate Python runtime scaffolding
  to `init --dynamic`, followed by `scan --no-rules-only`.
- Move pre-commit and first-use examples to rules-only. Preserve scan/Action
  defaults, fork credential/upload policy, findings, thresholds, and baselines.
- Keep native schema 1.5.0, with nullable finding review for rules-only results;
  export stage records in SARIF and label the selected tier in console/Action.
  Existing object review records remain readable; consumers must handle null.
- Retain baseline-v2 and historical 1.3/1.4 migration from Phase 17.


### Fixed

- Require valid runtime baselines and demonstrated tool-grant, size-limit,
  process-state, canary, or schema violations for the four dynamic probes.
- Emit native 1.5.0 per-probe outcomes in console, JSON, and SARIF; retain partial
  findings and return exit 3 for incomplete testing.
- Preserve confirmed runtime proof through GPT review, count model judgments
  separately, expose disagreements, and merge only established validation causes.
- Introduce baseline-v2 stable proof identity and migrate 1.3/1.4 reports without
  inventing proof. Preserve historical captures and provide a separately
  refreshed runtime-review bundle for current-pipeline replay. These Phase 16–18
  changes are included together in 1.3.0.

- Trace supported Python and TypeScript tool inputs through same-file named
  helpers, explicit bindings, assignments, and returns for `SENT-002`; retain
  unresolved-flow and limited-review-context warnings.
- Require validation of the consumed input, enforced authentication, and
  integrity verification of the consumed manifest bytes before granting static
  safety exemptions. Configured sanitizer trust follows its returned value.
- Preserve historical GPT evaluation inputs separately from current detector
  output, retaining existing captures and request fingerprints.

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

[Unreleased]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v1.0.0...v1.2.0
[1.0.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/BashaarJavaid/MCP-Sentinel/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v0.1.0
