# Phase 18 verification

Status: **complete and accepted** on 2026-09-06 (UTC). Implementation and all
agreed local/hosted gates passed, followed by final user acceptance.
Version: **1.3.0** (Phases 16–18). The user separately authorized merge,
completion documentation, publication, release verification, and branch cleanup.
Publication and release verification are complete:
[PyPI 1.3.0](https://pypi.org/project/portunusmcp-sentinel/1.3.0/) and the
[GitHub release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.3.0)
are public. Implementation acceptance and public availability are both recorded.

The accepted `phase18-rules-only` branch was merged through PR #18.
No paid model calls are part of this gate. Historical evaluation captures remain
recorded replay, not new accuracy measurements.

## Required evidence

- Configuration precedence, inactive LLM validation, and explicit negative override.
- Absent/dummy credentials, reviewer/client/cache/network/Docker spies, unchanged
  existing cache, supported Python/TypeScript clean and vulnerable controls.
- Null reviews, stages, offline JSON/SARIF validation, thresholds, baseline,
  inline suppression, exit codes, default init, upgrade preservation, and rollback.
- Keyless ordinary/fork Action paths, inherited/explicit inputs, unchanged
  credential and upload policies, and actual pre-commit execution.
- `make check`, historical artifacts, distribution builds/smokes, Docker replay,
  and Linux/macOS/Windows Python 3.10–3.13 hosted gates.
- Installed-wheel scans in a Linux network namespace after dependencies install;
  namespace setup failure fails the gate. Spies and Semgrep adapter assertions
  separately establish avoidance of prohibited paths.

## Compatibility

Native schema stays 1.5.0 as agreed. Its canonical finding review field now admits
null for rules-only results; object review records remain valid. Older validators
requiring an object must update. Baseline-v2 is retained; rules-only and reviewed
static reports share static-mode compatibility. Historical evidence is preserved.

These checks establish offline completion and implementation compatibility. They
do not measure broad detection accuracy, security assurance, or maintainer value.

## Retained local results

Implementation commit: `b0d1bb3b20252dc8ef1718ccf8fa3cee599d1ccd`.
The merged PR is [#18](https://github.com/BashaarJavaid/MCP-Sentinel/pull/18).

| Gate | Observed result | Evidence |
|---|---|---|
| Final `make check` | Passed: 562 tests, 32 separately exercised Docker skips, 86.28% branch-aware coverage; lint/format/mypy/schema/audit/notices/strict docs passed | `artifacts/phase18/make-check.log` |
| Configuration regressions | 65 passed | `artifacts/phase18/config-regressions.log` |
| Real Docker regression controls | 32 passed, 110.93 seconds | `artifacts/phase18/docker-controls.log` |
| Actual pre-commit | Python/TypeScript clean 0, vulnerable 1; suppressed Python 0 | `artifacts/phase18/pre-commit-smoke.log` |
| Final wheel and sdist smoke | Passed pip wheel/sdist installs, pipx, uv, resources/identity checks, and paired rules-only scans with absent/dummy keys | `artifacts/phase18/wheel-smoke.log` |
| Installed-wheel Docker replay | Complete; four tested probes; inherited rules-only overridden; four cached records plus one replay, zero current tokens | `artifacts/phase18/installed-wheel-replay-summary.json` and `installed-wheel-replay/` |
| Historical compatibility | Artifact checker passed; all 182 retained capture/evaluation/evidence files unchanged | `artifacts/phase18/historical-artifacts.log` and `historical-byte-check.json` |
| Representative reports | All four Python/TypeScript controls produced validated JSON/SARIF; clean exit 0, vulnerable exit 1 | `artifacts/phase18/*_server.json` and `*_server.sarif` |
| Preparation distribution identities | Pre-release 1.3.0 wheel and sdist from the implementation checkpoint | `artifacts/phase18/local-distributions.json` |

The first broad local run retained 555 passing tests and one obsolete help-width
assertion failure, with 32 opt-in Docker skips and 85.00% branch-aware coverage.
That assertion was corrected. Additional configuration regressions then exposed
valid TOML/environment enum strings and non-table configuration handling; both
were corrected before the final gate. The initial log remains separately named
`make-check-initial.log`; `make-check.log` owns the final run.

The final cache-fixture follow-up creates an entry using `ReviewCache.write`
before installing failing constructor/read/write/client/network/Docker spies.
The same cases wrap actual Semgrep subprocesses and assert bundled local rule
files, `--metrics off`, `--disable-version-check`, and disabled telemetry/version
check environment settings. Any other subprocess executable fails the check.
All eight Python/TypeScript, absent/dummy-key cases passed locally
(`artifacts/phase18/offline-boundary.log`); the entry remained byte-identical.
This test-only refinement does not change the scanner or namespace harness.

## Hosted verification

The initial implementation commit's [CI run](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34010548726)
passed all 12 quality jobs, the canonical distribution build, all 12 installed-wheel
jobs, and Docker replay. Its mandatory Linux namespace gate failed before
scanning because the harness incorrectly required a one-line route file.
The failure is retained in `artifacts/phase18/isolation-initial-failure.log`.
The interface check passed, but the route-file line-count assumption did not.
The corrected harness checks actual route interfaces, accepting only loopback
and rejecting external interfaces/routes. Empty, padded, loopback-only, and
external-route cases are covered; nine maintenance/gate regressions passed
(`artifacts/phase18/isolation-gate-regressions.log`). Namespace setup remains
mandatory, with failure propagated through `pipefail`. Scanner/package code is
unchanged by harness commit `5f3d155`. The [corrected hosted run](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34012057981)
passed the mandatory namespace gate: all eight installed-wheel scans completed
with no external interfaces or routes. The exact log is retained in
`artifacts/phase18/hosted-isolation.log`. Its canonical wheel/sdist are byte-identical
to the locally tested distributions (`hosted-distributions.json`). The original implementation's
[documentation build](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34010548740)
passed. The earlier implementation CI was cancelled after the corrective commit
superseded it; it is not acceptance evidence.

The corrected [CI run](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34012057981)
passed **all 27 jobs** on `5f3d155de7fb1272796d01750bd361ff8f92fccd`: 12 quality
jobs, canonical build, 12 wheel jobs, installed-wheel Docker replay, and the
mandatory namespace gate. The same commit's
[documentation build](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34012058015)
passed. API summaries with job links are retained in `hosted-ci.json` and
`hosted-docs.json` under `artifacts/phase18/`.

The final local quality gate passed; the harness follow-up also passed lint,
format, mypy, and focused regressions. Subsequent evidence/status edits and the
cache-fixture refinement do not change scanner, schema, Action, or CI harness
code tested by that hosted run.

## Acceptance and release availability

The user accepted Phase 18 and authorized merging PR #18, recording completion
on main, publishing 1.3.0, verifying the release, and deleting the stale branch.
The final accepted commit is `8917ef0b8b8713249a51cf34ffe96abcb91ab10e`:
[all 27 CI jobs passed](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34014222493),
including the cache/adapter assertions and mandatory network isolation, and the
[documentation build passed](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34014222466).

Version 1.3.0 contains the Phase 16–18 changes. Default `init` users
must opt into runtime scaffolding with `init --dynamic`, then
`scan --no-rules-only`. Rules-only users can scan directly without init. Native
1.5.0 nullable review compatibility and baseline-v2 migration are described above
and in the changelog. The 1.3.0 Action package pin is now publicly usable.

## Public 1.3.0 release verification

Release commit: `c45e10cf878cfa0f926687f88a5679729ce9a19f`. The completion
documentation was committed and pushed to main after merging PR #18.
[All 27 main CI jobs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34015968345)
passed, and the [strict documentation build, deployment, and live smoke](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34015968295)
passed. The superseded merge-commit CI run was cancelled so these final-commit
checks could use the runners; it is not release evidence.

The [signed-tag release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34016000165)
passed **all 44 jobs**: signed tag/main validation, the full quality and installed
distribution matrices, mandatory network isolation, Docker replay, TestPyPI
publication and verification, protected PyPI promotion, public hashes and
attestations, and Linux/macOS/Windows Python 3.10–3.13 public pipx/uv installs.
No paid model calls were used.

The [exact v1.3.0 Action proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/34017882433)
and [signed v1 alias proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/34018002117)
passed with empty model credentials, explicit rules-only, complete reports,
zero findings, null review data, expected skipped stages, and validated SARIF
upload. Both signed tags resolve to the release commit. The
[Marketplace page](https://github.com/marketplace/actions/mcp-sentinel) advertises
`v1.3.0` as its latest release; its historical listed-version entry remains
`v1.0.0`. No Marketplace checkbox change was needed for the latest-release display.

The [initial external Action proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/34017705027)
failed its zero-finding assertion: the older demo control discarded the result
of Pydantic validation and then read the original input. It produced one
`SENT-003/Low` candidate. The initial local scan had the same finding; its exit 0
meant below the failure threshold, and the earlier zero-finding progress update
was incorrect. The demo now returns the validated model field. The retained
before/after local reports and successful hosted rerun record the correction;
the published scanner was unchanged. This is release-control evidence, not an
independent maintainer catch or a broad detection-accuracy measurement.

Canonical release SHA-256 identities:

```text
e5c529967c58735303b3ab5d6a836607d85f5f078949587a1335c5d6544d6cbf  portunusmcp_sentinel-1.3.0-py3-none-any.whl
859022c18bfd62f19983f98a40ad7ddb6ee14b655462f7217d6defd4acfd9523  portunusmcp_sentinel-1.3.0.tar.gz
```

These replace the preparation-build identities for public installation: release
documentation was finalized before tagging. TestPyPI, PyPI, and the attached
GitHub release assets use the same canonical files. Retained release records
are `artifacts/phase18/release-*.json`, `release-action-exact.sarif`, and
`action-control-before.json` / `action-control-after.json`.
