# Approved six-observation Proxmox regression

## Current v91 Proxmox regression: failed gate, disposition pending

The approved **six Proxmox observations** at engineering-tested **`5142a3f`**
completed with **all three entire ordered pairs equal**, verified cleanup and
zero remaining budget. **Both vulnerable reads were missed; all four fixed/safe
observations remain unsupported.** All six complete reports equal their failed
`884d376` references; zero findings, six metadata warnings and six unsupported
registration surfaces are fully source-assessed. Raw failures remain unchanged.

Source review identifies the conservative builtin-protection guard rejecting
`importlib.metadata` package-version imports when literal dictionary copies occur.
This is a sufficient source-visible rejection, not a runtime trace or proof that
removing it establishes downstream support. No further correction, scan, profile,
retry, comparator or paid call occurred during this continuation.

Unchanged engineering retains **2,596 tests / 36 skips** locally and in all 12
hosted suites, 29 normal jobs/docs, **90.28% combined / 86.23% branch coverage**,
six zero-call production replays and 19 runtime bindings. The 105 unaffected V87
observations retain their original source/report identities and compatibility
proof. This continuation adds assessment and affected docs/package verification,
not a new hosted code pass or speedup claim.

All **486 requirements and 30 unaccepted limitation proposals** remain. The concrete
next decision is whether to retain Proxmox as unsupported for Phase 22 or continue
focused recovery. Neither is inferred from numerical approval. Ordinary FAF
completion within 1,800 seconds remains unestablished; V68 is unapproved/unimplemented.
**Phase 22 is incomplete:** failed-gate disposition, explicit human technical
acceptance and verified accepted-closeout delivery remain. Git stays 312/1,040
incomplete, 728 deferred; paid benchmark/pilots deferred, Phase 21 incomplete,
Phase 24/15 unchanged. Historical spend **$0.071799; zero new paid calls**.
No merge, ready-state change, release, outreach or Phase 23 is authorized.

| Current Proxmox input | Pass | Whole-input seconds | Detection/support | Matching alerts |
| --- | --- | ---: | --- | ---: |
| vulnerable | first | 4.486411 | vulnerable_missed | 0 |
| fixed | first | 3.840037 | unsupported_negative | 0 |
| safe | first | 3.865582 | unsupported_negative | 0 |
| vulnerable | repeat | 4.018240 | vulnerable_missed | 0 |
| fixed | repeat | 5.093598 | unsupported_negative | 0 |
| safe | repeat | 4.067295 | unsupported_negative | 0 |

The sequence took 35.831059 seconds. All six inputs completed within the normal 1,800-second limit, 10-second Semgrep limit and separate 15-second cleanup allowance, with the existing four-worker maximum and one serial input. The 200-minute outer limit was a worst-case bound, not an estimate. There were zero retries, profiles, comparator executions, target executions or paid calls. All three entire ordered pairs matched after only the original eleven volatile exclusions. The budget is closed with zero remaining.

The sole warning per report is the unresolved dynamic description at `tools/backup.py:82`. The sole surface is unnamed unsupported `server.py:70` call-tool registration, examined only for SENT-004; it supplies no SENT-012 upload-path support. No finding or unresolved-flow occurrence exists. Full reference/source equality reuses all prior exact contexts and judgments, including unsupported denominators; absence of a matching alert does not establish fixed or safe qualification. Fixed and safe share source/configuration, and the safe caller value is an illustrative prerequisite rather than a static specialization.

Proxmox's original condition remains caller `file_path` outside stable operator `PROXMOX_MCP_UPLOAD_DIR=/srv/proxmox-upload`. The vulnerable code opens the original path at client.py:436; fixed code resolves and checks the path before opening at line464. Ordinary readable files, stable environment, no symlink replacement/race/mount change and no custom filesystem remain prerequisites. No target was imported or run; no remote exfiltration, Proxmox API/authentication/TLS or physical safety is established.

The literal mapping correction is implemented and engineering-tested. Source review now identifies the broad `importlib` root guard as another sufficient rejection: server.py imports `PackageNotFoundError` and `version` from `importlib.metadata` for package version/fallback. Removing the guard wholesale would weaken builtin/namespace mutation controls. A later focused correction must distinguish harmless metadata imports from dynamic import and namespace escape, preserve all existing adversarial controls and verify downstream behavior. This review does not claim an observed first rejection or a future successful fix.

One assessment-helper check initially used intermediate rather than final V87 field names and raised KeyError before output. The corrected helper binds `report_sha256` and `narrow_rubric_satisfied`; complete assessment passes. Original command/log/helper bytes remain. No native slot was repeated.

[Full six-report assessment](../v90-regression-results/final-assessment/assessment.json), [complete ordered differences](../v90-regression-results/complete-reference-assessment/difference-inventory.json), [source rejection](../v90-regression-results/remaining-source-boundary.json), [verified cleanup](../v90-regression-results/completion-verification.json), [complete 486-row audit](audit.json), [all 30 unaccepted limitations](unaccepted-limitations.md), [concrete disposition proposal](decision-proposal.json).

