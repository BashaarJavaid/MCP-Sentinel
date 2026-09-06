# Phase 18 verification

Status: implementation and all agreed local/hosted gates passed. Final user
acceptance is pending. Phase 18 is not marked complete until that acceptance.
Prepared version: **1.3.0** (Phases 16–18). Public release availability is separate:
no merge, release tag, PyPI/Marketplace publication, or announcement is authorized.

The branch is `phase18-rules-only`; hosted gates will run through a draft PR.
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
The draft PR is [#18](https://github.com/BashaarJavaid/MCP-Sentinel/pull/18).

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
| Distribution identities | Prepared 1.3.0 wheel and sdist, unpublished | `artifacts/phase18/local-distributions.json` |

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
to the locally tested distributions (`hosted-distributions.json`). The same commit's
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

Implementation is ready for the one final user acceptance requested in the plan.
Phase 18 remains open until that acceptance is recorded. The PR remains a draft;
no merge, main push, release tag, publication, or announcement occurred.

Prepared 1.3.0 contains the unreleased Phase 16–18 changes. Default `init` users
must opt into runtime scaffolding with `init --dynamic`, then
`scan --no-rules-only`. Rules-only users can scan directly without init. Native
1.5.0 nullable review compatibility and baseline-v2 migration are described above
and in the changelog. The newly pinned Action becomes publicly usable only after
separately authorized 1.3.0 publication and release verification.
