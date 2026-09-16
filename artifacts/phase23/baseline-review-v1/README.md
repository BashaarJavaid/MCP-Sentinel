# Phase 23 checkpoint 3: baseline execution approval

**Prepared and unexecuted.** The user accepted the seven-input source freeze;
the [source-freeze receipt](../source-freeze.json) binds manifest SHA-256
`b0d7d2420d5242eedae3666dac499b2da119607af98d0f59cda28e902f9f6e0e`.
The original manifest and source review remain unchanged as historical proposals,
with acceptance recorded separately.

## Decision requested

Approve the exact [baseline proposal](proposal.json), including its commands,
identities, configuration, order, limits and volatile exclusions. Its SHA-256 is:

`8612c2e645e08b78a9cf6ab0cc5b4a6314c0c0702b722ffbd7f3b0dace74a83b`

This authorizes **one baseline attempt of at most 14 observations**, with no
retry, detector change, candidate evaluation, target execution, paid call or
publication. The user's plan explicitly requires review of the exact commands,
scanner/configuration identities and outer cap before execution. Source-freeze
approval did not authorize this stage.

## Exact command

Working directory: `/Users/bashaarjavaid/Projects/MCP-Sentinel`.

```bash
.venv/bin/python -m scripts.phase23_regression run \
  --proposal artifacts/phase23/baseline-review-v1/proposal.json \
  --approval artifacts/phase23/baseline-authorization.json \
  --output artifacts/phase23/baseline-v1
```

The real authorization file does not exist. The
[authorization template](authorization-template.json) has a null decision;
it is not approval. After explicit approval, record the user decision and exact
proposal hash in the real authorization file. The launcher consumes it once
through exclusive creation of a `.used.json` receipt and rejects reused outputs.
Preflight failure also closes the attempt; unused observations are not permission
to retry.

Each observation starts this production CLI in its own process group:

```text
<bound-python> -I -m sentinel scan <stable-source-path>
  --rules-only --format json --output <observation-directory>/report.json
```

All fourteen expanded commands are in `proposal.json`. Sources are materialized
and hash-checked, scanned once for JSON, and removed during cleanup. SARIF is
rendered from that same canonical report and validated offline; it does not
require a second scan. The source path for each input stays the same on both
passes, so no path-normalization exclusion is proposed.

## Scanner and configuration identities

| Component | Binding |
| --- | --- |
| Checkout | `dd9101ddfead19d65b7a84b374e4cf7e85462ff7` plus the explicitly hashed uncommitted helper/tests |
| Scanner source tree | `b1f044ed710e9997a9572ad3a28dcce01254dc0134bb638a53334541160a8f77` |
| Baseline helper | `7d3acd1369644e2dd03501a53788338133c6cadbb58366c9a056dbb4aef4a966` |
| Helper tests | `64700908c6f0c1552c18e1fff84336dde692e8be88340217c029a2a088242cda` |
| Host | macOS 15.7.3, arm64; Python 3.12.13 |
| Semgrep | 1.176.0; installed core binary hash retained in the proposal |
| Rules/report | Bundled rules and native schema 1.7.0 from the bound source; offline vendored SARIF schema |
| Resolved configuration | TypeScript, static rules-only, JSON, fail-on high, default rule selection, no extra ignores, no baseline/suppression override, max-findings configuration 500 |

The exact Python executable bytes, dependency versions, schemas, existing utility
files, `pyproject.toml` and `uv.lock` are also bound. All seven resolved
configurations were read from the frozen sources without scanning. They have the
same canonical JSON hash:
`bd398569204c4183b732b3303fc69a3cead530bd05154d84e696ef542521dd1a`.
The launcher verifies the actual configuration again before each CLI invocation.

The child environment is an explicit allowlist: bound Python bin plus system
command paths, UTF-8 locale, isolated Python startup,
an output-owned temporary directory, and disabled Semgrep metrics/version checks.
No model credentials or ambient Sentinel overrides are inherited. It uses the
existing offline rules-only contract and local bundled rules. This local baseline
does not claim a new OS network-isolation test; the later routine CI gate will
use the existing Linux network namespace after dependency installation.

## Order, bounds and stopping

Run this sequence twice, sequentially:

1. `full-vulnerable`
2. `full-fixed`
3. `minimized-vulnerable`
4. `minimized-fixed`
5. `safe-literal`
6. `renamed-vulnerable`
7. `renamed-fixed`

| Bound | Exact policy |
| --- | --- |
| Input | 1,800 seconds, including materialization, configuration, scanner completion and report validation |
| Semgrep | Existing `--timeout 10` limit; Semgrep's whole subprocess also remains within the shared input deadline. This flag is not a separate 10-second whole-process watchdog. |
| Workers | Existing maximum of four flow workers; no worker-count change |
| Cleanup | Separate 15 seconds; kill and reap the scanner-owned process group, verify its disappearance and remove the materialized source |
| Outer stage | 26,400 seconds = **440 minutes**, plus at most 15 seconds for active cleanup on expiry |

Fourteen maximum input-plus-cleanup allowances sum to 423.5 minutes; the outer
cap leaves 16.5 minutes for preflight, ledger and comparison work. **This is a
worst-case cap, not an estimate or speedup claim.**

Timeout, cancellation, invalid/incomplete native output, preflight drift or failed
cleanup closes all remaining observations. SIGINT/SIGTERM use the cleanup path;
signal delivery is deferred across child creation until its PID is owned. A
completed detection miss does not trigger a retry or stop the baseline sequence.
Both full passes are needed to assess repeats. Every failure and unstarted closed
input stays visible.

## Exact ordered-report exclusions

Only these JSON paths are excluded from the comparison:

```text
/scan_id
/started_at
/completed_at
/static_analysis/duration_ms
/findings/*/finding_id
/findings/*/scan_id
/findings/*/timestamp
/findings/*/provenance/*/timestamp
```

These remove run UUIDs and measured clocks. All findings, duplicates, source
locations/evidence, warnings, coverage, support states, summaries, stages and
future fields remain. Arrays keep their original order. Identically named keys
elsewhere are retained. Complete raw reports and ordered diffs are stored; no
fuzzy equality, sorting of findings, or additional exclusion is implied.

## Assessment and evidence

The helper retains JSON, SARIF, configuration, stdout/stderr, exact commands,
timings, exit codes, cleanup outcomes and complete ordered repeat diffs. It records
SENT-002 matches using the accepted source paths and both location/evidence ranges.
Additional findings remain in the reports. Detection and support judgments still
require source assessment; launcher success alone is not a passing case gate.

The accepted case gate requires findings on all three vulnerable inputs,
supported absence on all four negative inputs, complete equal repeats, and
assessment of unrelated findings/diagnostics. Unsupported negatives cannot pass.
If the baseline already meets that gate, retain it and request another candidate.
If it fails, present the smallest correction and affected historical regression
list for approval before implementation. A corrected-candidate packet follows
that decision; it is not authorized here.

## Verification

The adopted intake/source-preparation revision passed `make check`: **2,603 passed,
36 skipped**, plus lint/format, full typing, schema, dependency audit and strict
docs. Its exact earlier helper/test bytes are retained in the source-review
packet; this is not represented as a full-suite pass for the later runner extension.

The current runner extension passes **16 focused checks**, full configured mypy
(154 source files), Ruff and formatting. Checks include source integrity/drift,
exact match ranges, ordered content preservation, missing approval, incomplete
reports, real synthetic child timeout/cancellation cleanup, identity failure
closing all unused budget, a complete synthetic 14-observation sequence, and output
reuse rejection. These use inert data and synthetic subprocesses, not the advisory
targets. See [verification.json](verification.json) for hashes, logs and retained
development failures. No hosted CI was dispatched for this checkpoint.

**Zero advisory observations, target executions or paid calls.** Phase 23 remains
incomplete. Phase 22's accepted limitations and all excluded/deferred work remain
unchanged; no merge, release version, tag or publication is authorized.
