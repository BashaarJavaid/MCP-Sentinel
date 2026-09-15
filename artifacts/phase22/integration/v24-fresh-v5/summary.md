# Phase 22 fresh evaluation and limitation review

Phase 22 remains incomplete. The approved measurement and source assessment are
complete; the measured limitation and final technical acceptance require separate
user decisions. No additional measurement budget remains.

The approved replacement-v5 evaluation completed **15/15 observations** in
[run 34605934302](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34605934302),
workflow **`86cbdc9`**, immutable scanner **`1f3f72f`**. All ten native observations
and five pinned Semgrep observations completed within 120 seconds; maximum whole
input was **10.437 seconds native / 22.052 seconds comparator**. All five entire
ordered native repeats match after only the established 11 volatile exclusions.
Native JSON/SARIF, input/configuration identities and owned-child cleanup pass.
The single dispatch and all 15 observations are consumed; no remaining budget,
retry, profile, paid call or target execution.

**The fresh detection result is 0/2 vulnerable hits in each native batch and
0/2 for Semgrep.** Both tools emit zero findings on all five correlated inputs.
The two fixed variants and public control also have zero matching alerts; this
silence does not establish discrimination because vulnerable inputs are silent too.
Sentinel reports no discovered MCP surfaces, an unknown total surface count,
and 19 binding warnings on each vulnerable input versus 26 on each fixed/control.
All **232 native diagnostic occurrences** are individually source-assessed.
The upstream SDK prototype patch makes the scanner's binding resolution ambiguous;
its TypeScript request-sink list also does not include Lighthouse. Neither gate
has been bypassed or changed. Completed analysis is not proof of handler coverage,
detection accuracy, safe navigation or runtime protection.

The novel repository/source pair was curated by the implementation agent after
scanner freeze, with source exposure and correlated variants disclosed. This is
one narrow link-local-before-Chrome condition, not five independent vulnerabilities,
independent human review or unseen-source evidence. Loopback remains intentionally
allowed upstream; DNS/redirects/IPv6 and actual startup/navigation are outside labels.
First frozen misses, source archives and the disqualified replacement-v4 proposal
remain preserved. No scanner tuning, case substitution or new evaluation is authorized.

The concrete limitation proposal is
`artifacts/phase22/integration/v24-fresh-v5/limitation-proposal.json`.
Its assessment, all 15 outcome rows, diagnostic source references, audit and review
summary are in the same directory. **The limitation is proposed, not accepted.**
The original 89 rows are 84 passed, two user-deferred, two proposed documented
limitations awaiting decision (R66/R88), and one unresolved human acceptance (R84).
The 60 added rows are 56 passed, three historical unresolved checkpoints with
closed scopes, and one proposed limitation disposition. Phase 22 remains incomplete;
final technical acceptance is a separate decision after the fresh disposition.

Unchanged product/workflow bytes retain CI **34578515990** and docs **34578515965**
at **`e1ab15c`**: all 29 normal jobs and all 12 suites **2,194 passed / 36 skipped**,
89.67–89.69% hosted branch coverage, and byte-verified wheel/sdist sources. This is
compatible reuse, not a new full-suite pass at the evidence-only delivery. The
whole 25 development reuse and 45 + 45 historical gates remain passed under their
actual approval, as do the three exposed SSRF families at measured `2ac39aa`.
Original held-out misses/failures, the Meta erratum and separate Kubernetes
suspicion remain visible. Git campaigns remain incomplete (312/1,040 attempts);
six production requests retain zero-call replay bindings. Paid benchmark/pilots
remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, release,
ready-state, outreach or Phase 23 work is authorized. “v24” names evidence only.

## All approved observations

| Input | Native first (s) | Native repeat (s) | Semgrep (s) | Vulnerable hit / negative alert |
| --- | ---: | ---: | ---: | --- |
| lighthouse-linklocal-vulnerable | 10.437 | 9.188 | 21.861 | Miss in all three batches |
| lighthouse-linklocal-vulnerable-mutation | 9.035 | 9.035 | 21.817 | Miss in all three batches |
| lighthouse-linklocal-fixed | 9.185 | 9.287 | 22.052 | No matching alert in all three batches |
| lighthouse-linklocal-fixed-mutation | 9.135 | 9.187 | 22.039 | No matching alert in all three batches |
| lighthouse-public-safe | 9.236 | 9.337 | 22.030 | No matching alert in all three batches |

These are whole-input durations, including child setup/materialization/imports,
analysis, validation and writing. Native engine durations are 2.086–2.203 seconds.
Cleanup is separately bounded and verified. The job used standard Ubuntu,
Python 3.12.14 and four reported CPUs. Ten native attempts represent five inputs
repeated, including two correlated vulnerable variants of one vulnerability.
Semgrep 1.176.0 used the approved 511 configurations / 533 security rules at
semgrep-rules `40b8c63f75dc7c22c8a77482d73bfb864b146f7e`; both TypeScript files
were among its eight scanned paths, with no errors or raw findings.
Native reports record six scanned files, eleven evaluated rules and SENT-001
skipped because permissions are absent. These counts do not establish tool coverage.

## Exact decision and evidence

- [Actual evaluation approval](../v23-fresh-v5/authorization.json), [final file binding](../v23-fresh-v5/binding.json), [single dispatch receipt](dispatch-consumed.json).
- [Frozen proposal](../../corpus-replacement-v5/evaluation-proposal.json), SHA-256 `3b3013ae4a116804421bc8c028d8a1fe800fb288ae6637ce593c3d0bd30f19f6`; [checkpoint](../../corpus-replacement-v5/checkpoint-1f3f72f.json), SHA-256 `ae4d6c817446b4cf675ec2b1f74a99323e3e21de5a2b1545f29264e4513cf60e`.
- Scanner `1f3f72f0f25c597b53c9f833e2e4bec99728d328`; source SHA-256 `7a6caaabb75c19d2dcd15325bcbb2d07fe8e59b913bce1d32f6f6aac3ee4e0f4`; harness `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add`; lock `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b`.
- Measured workflow `86cbdc96e73b08d76786933398bcb8d31c190905`; unchanged tested workflow `e1ab15c513ae736bedfb7665ac53efabff85f790`. Hosted checkout logs verify both workflow and immutable scanner. Normal CI used synthetic merge `c044a1aec17e8f3f826eb2f2c1a966a8b85c21e4`, whose entire tree equals `e1ab15c`.
- [Assessment](assessment.json), [all 232 diagnostic source assessments](warning-source-assessment.json), [raw reports/resources and full logs](hosted/packet.json), [all 89 + 60 requirement rows](audit.json), [compatible reuse](compatible-reuse.json).
- [Proposed limitation decision](limitation-proposal.json): accept the Lighthouse SDK/browser sink recognition miss as a documented Phase 22 limitation while preserving the 0/2 outcomes and unknown coverage. This authorizes no detector correction, retry, paid calls or phase closure. If accepted, prepare the separate final technical acceptance packet; if declined, prepare a bounded correction/exposure proposal before new work.

## Preserved results and failures

The 98-observation historical refresh remains 98/98 complete:72 within120 seconds,
26 extended to at most176.032seconds under the approved300-second maximum. Both
whole45historical batches retain20/20vulnerable hits and zero matching alerts on25
negatives, with entire ordered repeat equality. The explicitly reused whole25
development batch retains10vulnerable hits, exactly two raw Meta erratum alerts,
and13valid negative controls. The 1,191 preparatory diagnostic changes remain
individually assessed; the Kubernetes kubectl_logs suspicion stays distinct from
the named kubectl_get condition. Original7555a9d15/25Linux/timeouts and the later
62-attempt stale-assessment stop remain failures with closed budgets.

fetch-mcp, open-webSearch and SearXNG retain their original exposed regression
passes at2ac39aa, with deadline-only source compatibility to1f3f72f. They do not
become fresh evidence. Original held-out10complete/10unsupported/5incomplete and
0hits among4completed vulnerable variants of10total vulnerable inputs remain
unchanged. Replacement-v4 is still disqualified for prior source reuse and was
never evaluated. No prior result or failed optimization is relabeled.

The retained local suite2194/36 and89.68%coverage, six source-bound production
replays, 153wheel/166sdist member checks and all29hostednormal jobs retain their
actual sources. Thirteen Git campaigns remain incomplete:312tested,728remaining
out of1040. The separate20-attempt demo does not replace those campaigns. Prior
Phase22paid calls remain2/$0.071799; this continuation adds0. Paid396-request
benchmark and pilots remain deferred; Phase21incomplete, Phase24/15unchanged.

Seal53 preserves the first frozen observations, all source reviews, commands,
helper sources and retained failures; prior52seals are verified and unchanged.
The assessment binds its exact retained `assess-executed.py`; later lint-only
helper cleanup is disclosed in [the correction receipt](assessment-helper-correction.json).
Owning docs and post-seal delivery bindings are directly tracked. Seven user
prompt files and the separate main worktree remain unchanged. No final human
technical acceptance is requested until the fresh limitation has a disposition.
