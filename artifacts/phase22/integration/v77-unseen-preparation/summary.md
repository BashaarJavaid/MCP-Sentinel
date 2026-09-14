# Phase 22 unseen-source evaluation proposal

**Two repositories, six source records, twelve proposed observations. No numerical approval or new scans yet. Phase 22 remains incomplete.**

The scanner is frozen at `cec0322e904bbf63c33cd95796e7289101a93e5d`. Source, harness, lock and actual isolated imports are bound before curation. Both selected complete upstream pairs are first-parent verified and absent from recorded project exposure; comparison covers 3,781 distinct prior archives with no substantive file overlap (only an empty test initializer).

| Order within each pass | Repository / actual language | Named condition | Vulnerable → fixed commits |
| --- | --- | --- | --- |
| 1–3 | awwaiid/mcp-server-taskwarrior / TypeScript | `mark_task_done.identifier` shell interpolation → shell-free argv, SENT-002 | `d502ad2` → `29850c7` |
| 4–6 | nick-holmquist/proxmox-mcp / Python | `pve_storage_upload.file_path` local open outside operator upload root → checked resolved path, SENT-012 | `3d6610b` → `39889d5` |

For each repository: vulnerable, fixed, safe; then repeat the same six in that order. Each safe record uses the complete fixed tree/configuration and a source-defined safe caller value. Repeats and related variants are correlated. Taskwarrior has a complete MIT license; Proxmox declares MIT in README/pyproject but has no standalone license/full grant text (GitHub license=null). Taskwarrior's current GitHub language metadata says JavaScript; selected source/configuration are TypeScript. Required Taskwarrior `zod` is imported but not directly declared in its package dependencies. All prerequisites and exclusions remain explicit in the source reviews; targets are never installed or executed.

Normal whole-input/static maximum **1,800 seconds**, Semgrep **10 seconds**, cleanup **15 seconds**, maximum existing **four workers**, one input at a time. The internal stop is **378 minutes**; outer process maximum **380 minutes**, plus its separate **15-second cleanup**. This comprises 363 minutes input/cleanup, 15 minutes setup/identity reserve and 2 minutes finalization. It is a worst-case cap, not an estimate. No child starts unless its full input/cleanup allowance fits. Whole-input time includes child startup/imports/materialization/analysis/reporting.

Cancellation, identity/infrastructure/execution/timeout/schema/cleanup/entire-ordered-repeat failures close unused budget. Detection misses, false alerts and unsupported negatives remain failed gates while collecting the remaining approved cases. No tuning, retry, replacement, profile, comparator, target execution, resource change or paid call. All six entire ordered reports must match on repeat after only the existing eleven volatile exclusions. Every finding, diagnostic, unresolved surface and support denominator requires source assessment. Quiet unsupported negatives fail; no positive per-sink trace is invented.

The artifact-local six-input schema reuses existing Input/Snapshot, archive/path/hash/license validators, exact frozen approval and production measure. It changes only the old corpus population/rule-ID admission for this packet; product/harness files remain unchanged. Synthetic checks caught an immediate-alarm budget-record issue in the new helper, corrected before any execution; original helpers and failures are preserved.

[Exact proposal](evaluation-proposal.json), [rubric](scoring-rubric.json), [source cases](cases.json), [selection/qualifications](selection-record.json), [435-row audit](audit.json), [prior-row preservation](prior-row-preservation.json), [staging and missing-approval checks](staging-and-boundary-verification.json), [synthetic collection checks](collection-checks.json).

V73/V75 remain separate closed approvals: 205 exposed observations, 95 entire ordered pairs and narrow current-source passes. Engineering remains actual cec0322: 2,450 tests/36 skips locally and in 12 hosted suites, 29 normal jobs/docs, 90.11% combined/85.97% branch coverage, 303 engineering inputs, 6 zero-call production requests and 19 runtime components. This proposal adds affected docs/package and helper checks, not a new hosted code pass. All 422 previous rows persist; only supplemental V76 review delivery is resolved, with its sealed previous row preserved.

All 23 historical/practical limitation proposals remain unaccepted. Ordinary FAF completion within 1,800 seconds remains unestablished; six V73 uncapped observations took 2,297.758–2,735.386 seconds. V68 stays unapproved/unimplemented. Original held-out/fresh/native/profile/equivalence failures, two Meta operator errata and unrelated candidates remain. Git 312/1,040 incomplete, 728 deferred; 396-request paid benchmark and pilots deferred; Phase 21 incomplete and Phase 24/15 unchanged. Historical paid spend remains $0.071799; zero new calls.

After exact numerical approval: execute once, assess all outcomes, handle justified follow-up under applicable approvals, deliver a new complete technical acceptance proposal, obtain explicit human technical acceptance, then deliver and verify accepted closeout. No merge, ready-state change, release, outreach or Phase 23 is authorized.
