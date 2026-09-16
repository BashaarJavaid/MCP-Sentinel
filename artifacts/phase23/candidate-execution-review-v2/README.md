# Corrected-candidate execution checkpoint

**Prepared, not approved or executed.** Review one attempt of **seven frozen
inputs twice = 14 observations** for GHSA-3q26-f695-pp76, bounded to
`git_init.initialBranch` shell injection. The original baseline and first corrected candidate remain failed on full sources;
passing synthetic tests does not establish this advisory's corrected gate.

## Exact approval requested

Approve [proposal.json](proposal.json), SHA-256:

`e6b22fa31f77330975a5bee3c80a9f4deca4d5f0db102564c9f26c0c6128a7d7`

This binds the current corrected source, helper, dependencies, configurations,
commands, order, report exclusions and **440-minute outer cap plus 15 seconds
cleanup**. Full local `make check` passed: **2,748 tests / 36 skips**,
all maintenance gates, 90.52% combined and 86.58% branch coverage.
The [engineering summary](../metadata-engineering-v1/summary.json) binds the actual
source and evidence. Advisory execution remains unapproved. This packet includes no
historical compatibility observations, hosted dispatch, retry or publication.
The separate Phase22/first-advisory compatibility scope remains pending; its FAF
limitation has not become a normal-deadline pass.

## Command and identity

Working directory: `/Users/bashaarjavaid/Projects/MCP-Sentinel`.

```bash
.venv/bin/python -m scripts.phase23_regression run \
  --proposal artifacts/phase23/candidate-execution-review-v2/proposal.json \
  --approval artifacts/phase23/candidate-authorization-v2.json \
  --output artifacts/phase23/corrected-candidate-v2
```

The real approval file does not exist; the template has a null decision. A user
approval would be recorded separately, then consumed once by exclusive creation
of its `.used.json` receipt. Preflight failures also close the one-use attempt.
No unstarted observation authorizes a retry.

| Identity | Binding |
| --- | --- |
| Checkout base | `dd9101ddfead19d65b7a84b374e4cf7e85462ff7` |
| Actual corrected scanner source tree | `2fa09818900817337863f90c41b71ab6d9e27458f11b8b1d80e1b882682c051d` |
| Actual helper | `e1c025fc59e080ad9addf1d3182cacbb9129cc249ad7b638e50e2ed826fbe55a` |
| Frozen seven-input manifest | `8a489a5593bf9397382519beccb1e01b6e5add3a7dfd1fba9b1cf070e5011d5c` |
| Host | Python 3.12.13 / macOS 15.7.3 arm64 |
| Semgrep | 1.176.0, installed binary hash in proposal |

The checkout includes explicitly hashed uncommitted changes; the base commit
alone does not identify the candidate. The proposal binds the actual scanner
tree, helper/tests, interpreter bytes, installed dependencies, lockfile and
vendored JSON/SARIF schemas. The approved changes are local star-export binding,
proved promisify(exec/execFile) identity, and the bounded separate MCP handler
invocation stack, plus the approved composed Zod metadata correction. It preserves
original field symbols and checks later mutations at registration completion.
New metadata proof is bounded to 256 identities and 64 dependency levels.
Public Finding/report interfaces and rule meanings are unchanged.

The same helper now accepts the `corrected-candidate` stage label; its baseline
versions are archived with their original proposals. Fourteen expanded production
CLI commands are retained in the proposal. Each materialized source is hashed,
scanned once for JSON and removed; SARIF is derived from that same report and
validated offline. Source paths are stable across repeats.

## Order and exact limits

Run **full-vulnerable, full-fixed, minimized-vulnerable, minimized-fixed,
safe-literal, renamed-vulnerable, renamed-fixed**, then repeat that order.
Complete upstream snapshots stay distinct from derived cases; these are seven
correlated examples of one advisory, retaining Apache-2.0 notices.

- Input: 1,800 seconds including source preparation, configuration, scanner and
  native report validation.
- Semgrep: existing 10-second rule limit, within the whole-input deadline.
- Workers: existing maximum four; inputs run sequentially.
- Cleanup: separate 15 seconds for the owned process group and materialized source.
- Outer stage: 26,400 seconds (440 minutes), plus active cleanup at expiry. This
  is a worst-case cap, not a runtime estimate or speedup claim.

Preflight drift, timeout, cancellation, incomplete/invalid report or failed
cleanup closes every unstarted slot. Completed misses remain failures and do not
trigger retries. Reports, stdout/stderr, configuration, timing, cleanup and all
repeat differences are preserved. Zero paid calls and advisory-target execution.

Configurations retain TypeScript rules-only analysis, all default rules, JSON,
fail-on high, max-findings configuration 500, and no baseline/suppression override.
All seven canonical configuration hashes remain
`bd398569204c4183b732b3303fc69a3cead530bd05154d84e696ef542521dd1a`.
The helper checks them before each observation. It inherits only its explicit
Python/system PATH, UTF-8 locale, output-owned TMPDIR and disabled Semgrep metrics
and version checks; no model credentials or ambient Sentinel overrides.
This uses the existing offline static contract, not a new local OS isolation
claim. Routine CI's Linux network isolation remains a later required gate.

## Ordered-report comparison and case gate

Exclude only these previously reviewed volatile paths:

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

Keep every other field and array order. All three vulnerable inputs must produce
a source-matched SENT-002 finding in both passes. All four negatives must have no
matching shell-injection finding **and established analysis support**. Merely
recognizing a handler or emitting no warning is insufficient. Complete ordered
reports must agree under the listed exclusions. Unrelated findings, all changes
from the failed baseline and support judgments require assessment and human review.

A completed sequence or exit code 0 is not technical acceptance. If this case
still fails, retain the result and review its actual cause before more changes.
The following checkpoints remain historical compatibility, hosted engineering,
offline CI regression/rejection proof, technical acceptance and an approved
verified release. Phase22 accepted closeout, Proxmox/FAF optimization deferrals,
pilots and Phase24/15 gates remain unchanged.

The previous corrected candidate completed 14 observations with seven equal pairs,
but missed both full vulnerable reads and left both full fixed paths unsupported.
The derived support judgments and four unrelated SENT-014 findings remain pending
human review. All their raw reports, limits and the closed budget are unchanged.
This proposed new stage is a separately reviewed evaluation of changed source.
