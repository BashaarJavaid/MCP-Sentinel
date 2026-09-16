# Phase 22 continuation: fresh evaluation, explicit acceptance and final closeout

Execute this complete continuation for **PortunusMCP Sentinel** in **`/private/tmp/mcp-phase22-options`**, on `phase22/integration`. Continue with me until the remaining Phase 22 work is verified, I explicitly decide technical acceptance, and the subsequent closeout documentation and evidence are delivered to the existing draft PR. Do the authorized work, not just a plan or another handoff. Preserve all existing implementation, tests, source archives, first frozen measurements, failures, approvals, assessments and evidence.

**No additional paid calls without my explicit approval.** Writing this prompt did not approve or execute a new evaluation. Giving it to you to execute authorizes the ordinary continuation work below; the exact fresh-evaluation checkpoint and final human acceptance remain separate decisions. Do not interpret old “approved” or “go ahead” messages as a new unused measurement budget.

Prepared against the verified delivery on **2026-09-11**. The current 89-row audit is **84 passed, two explicitly user-deferred, three unresolved: R66, R88 and R84**. The remaining work is the proposed fresh evaluation and its source assessments, final requirement/evidence reconciliation, explicit human technical acceptance, and post-acceptance closeout delivery. Historical timing and all three exposed SSRF discrimination gates now pass under their actual approved scopes. Do not restart those completed workstreams merely because older prompts call them unfinished.

## 1. Working directory, authority and identities

Open this worktree, not the separate main checkout at `/Users/bashaarjavaid/Projects/MCP-Sentinel`. Read applicable `AGENTS.md` and applicable skills. Apply Ponytail full to implementation: understand the existing flow, reuse established tools, make minimal correct changes, and avoid speculative abstractions/dependencies. Do not delegate unless I or applicable instructions explicitly authorize it.

Read `mcp-sentinel-buildplan.md` first for historical context and §11 non-goals, then use `ARCHITECTURE.md`, `ROADMAP.md` and `docs/phase22-technical.md` as active authority. Preserve phase numbering and dependency order. Old status paragraphs are historical statements for their named revisions; they do not override the newest recorded approval and source-bound result.

Unless explicitly repository-relative, the `vN-*`, audit and evidence filenames below are relative to **`artifacts/phase22/integration/`**. Paths such as `corpus-replacement-v4/` are under **`artifacts/phase22/`**.

| Item | Verified starting identity |
| --- | --- |
| Active worktree / branch | `/private/tmp/mcp-phase22-options`, `phase22/integration` |
| Local HEAD and live PR #37 head | `3c29529e3f1c1f67150fd17aaf3afe57459c732e` |
| Final tested workflow / normal CI source | `61b19aeb56e087ebfeb52a7865aea50deb35e4bd` |
| Preparatory workflow source | `0d84185bfbcc8aec3e5f4cff97b35eab441c5105` |
| Actual immutable measured scanner | `1f3f72f0f25c597b53c9f833e2e4bec99728d328` |
| Scanner source SHA-256 | `7a6caaabb75c19d2dcd15325bcbb2d07fe8e59b913bce1d32f6f6aac3ee4e0f4` |
| Harness SHA-256 | `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add` |
| Lock SHA-256 | `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b` |
| Frozen scanner worktree | `/private/tmp/mcp-phase22-frozen-1f3f72f` |
| Existing PR | https://github.com/BashaarJavaid/MCP-Sentinel/pull/37 — OPEN, draft |
| PR head branch / base | `phase22/integration` / `phase22/description-poisoning` |
| Recorded PR #36 parent head | `8b6b0ddf1d6f6cf5a8da3ab9421471865b801455` |
| Separate main worktree | `/Users/bashaarjavaid/Projects/MCP-Sentinel`, `phase22/python-containment`, `4cd57593b2585b9ee05c0f175930e6a0d76d362a` |

`3c29529` is documentation/evidence delivery, not a new hosted code pass. Its code/test/workflow/package inputs equal tested `61b19ae`; product scanner bytes equal measured `1f3f72f`. The live draft body was verified against `v22-closeout-draft-body.md`. `v22-final-delivery-readback.json` and `v22-final-delivery-command.json` are supplemental ignored local receipts; reproducible source/evidence resides in the delivered Git tree and seals. Reverify actual remote state before another delivery.

Reverify Git status, worktrees, relevant source/harness/lock hashes, ignored evidence, and owned active processes before editing. Preserve newer changes rather than resetting to this snapshot. The tracked tree was clean. Before creating this prompt, six user prompt files were untracked and must remain intact:

- `docs/phase22-completion-agent-prompt.md`
- `docs/phase22-detection-timing-closeout-agent-prompt.md`
- `docs/phase22-final-agent-prompt.md`
- `docs/phase22-fable-performance-review-prompt.md`
- `docs/phase22-fable-performance-proposal.md`
- `docs/phase22-fable-performance-proposal-v2.md`

This is the seventh intentionally untracked prompt. The six preceding hashes are in `v22-final-delivery-readback.json` and `v22-refresh-authorization.json`. Do not bulk-add instructions or delete untracked/ignored files. Preserve all detached/increment worktrees, especially frozen `62987a6`, `7555a9d` and `1f3f72f`; never tune inside them.

Use the existing locked environment `/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv`, explicitly importing the intended worktree with `PYTHONPATH=src:.` or exact absolute roots. Do not accidentally evaluate its main-checkout editable package. Recorded local versions were Python 3.12.13, Semgrep 1.176.0, mcp 1.29.0, pytest 9.0.3 and pydantic 2.13.4; verify rather than assuming. Hosted versions follow the approved workflow and frozen lock.

## 2. Read the complete evidence map before acting

Read relevant contents without truncating decisive JSON fields. All 89 original requirements and all 51 additional scope rows must be accounted for; the appendix is a navigation snapshot, not a substitute for their evidence and interpretation.

Read in this order:

1. Integration `requirements.md`, `README.md`, latest `progress.md`, **`v22-closeout-audit/packet.json`**, `v22-closeout-summary.md`, `v22-source-verification.json`, `v22-final-documentation-binding.json`, `v22-delivery-verification.json` and `v22-closeout-draft-body.md`.
2. `docs/phase22-implementation-status.md`, `docs/phase22-ssrf-follow-up.md`, `docs/phase22-timeout-policy.md`, `docs/phase22-corpus-review.md`, applicable rules/compatibility/configuration docs, and `artifacts/phase22/completion-scope-v1/decision.json` plus its follow-up proposal. These establish pilot/paid deferrals and the technical acceptance scope.
3. **`v22-refresh-disposition-corrected.json`**, `v22-refresh-authorization.json`, `v21-historical-assessment-refresh-proposal.json`, `v22-assessment-freeze.json`, `v22-refresh-v1/preparatory-binding.json`, `v22-refresh-v1/final-binding.json`, `v22-refresh-v1/condition-assessment.json` and `v22-refresh-v1/runner.py`.
4. `v22-preparatory-assessment/packet.json`, `v22-historical_first-assessment/packet.json`, `v22-historical_second-assessment/packet.json`, `v22-preparatory-source-deltas/packet.json`, `v22-kubernetes-mutation-source-assessment.json`, `v22-preparatory-hosted/packet.json`, `v22-final-hosted/packet.json`, both dispatch-consumed receipts and run metadata. Follow their references to raw reports, resources, logs, source reviews and condition keys.
5. **`artifacts/phase22/corpus-replacement-v4/README.md`**, `evaluation-proposal.json`, `checkpoint-1f3f72f.json`, `manifest.json`, `configurations.json`, `review/condition-review.json`, `provenance/pair-comparison.json`, and the remaining linked provenance/licenses/source archives. Read `v21-scanner-freeze-before-curation.json` and `v21-fresh-proposal-verification.json`.
6. `v22-final-quality/packet.json`, `v22-final-quality-audit/packet.json`, corresponding preparatory quality packets, `v19-final-local-checks.json`, `v19-final-full-suite-junit.xml`, `v19-source-verification.json`, `v19-final-production-capture-revalidation/packet.json`, and `v12-compatible-evidence/packet.json`.
7. The corrections in §8; `evidence-v51.json`, integration archive restoration instructions, and directly tracked post-seal records. Restore absent expanded evidence from verified seals before concluding it is missing.
8. `docs/phase22-completion-agent-prompt.md`, its two preceding agent prompts, integration `next-agent-handoff-20260908-v2.md` (including §§9–17), and the Fable review/proposals for full historical context. Their consumed budgets, older identities and obsolete unfinished-work statements are superseded by actual later approvals/results. In particular, executing this prompt does **not** reapprove the original prompt's v12 SearXNG budget or Fable experiments.
9. Follow the audit's requirement-specific references to original held-out evidence, replacement-v1/v2/v3 freezes and exposure receipts, comparator records, regression assessments and actual source/test bindings. Preserve all first frozen results and review histories.

## 3. Authorization: act within it, preserve the checkpoints

Execution of this prompt authorizes ordinary Phase 22 continuation: read-only investigation, preparation of the exact remaining evaluation implementation and reviewable approval packet, necessary ordinary offline/engineering checks, minimal fixes within already authorized contracts, source-bound evidence reconciliation, documentation, local commits and batched delivery to **existing draft PR #37**. Do not ask again for routine editing or verification permission. Complete the concrete preparation necessary for a reviewable approval before asking for it.

The following remain explicit checkpoints:

- **Fresh replacement-v4 freeze/evaluation:** obtain approval of the exact proposal/checkpoint/scanner/manifest/exposure/bounds in §5 before any native or comparator execution on its five new sources. Preparation and source-only validation are allowed now. Record the user's actual new instruction in a versioned receipt; never modify the historical `prepared_not_approved` proposal to imply earlier approval.
- Any additional experiment, retry, profile, full benchmark sequence, runner/resource upgrade, gate exception or work beyond an approved stop/budget requires its own concrete scope decision. Failed attempts count. Unused maxima closed by a stop are not an available balance.
- Any new paid call requires exact named requests/cases, purpose, model/settings, maximum requests/tokens/dollars, reuse rationale and stopping conditions. The two prior Phase 22 production calls cost **$0.071799 total**; that approval is spent. The full **396-request paid benchmark** remains deferred.
- A different tested Git SDK/runtime environment or paid execution resources, if actually needed, requires its separate approval.
- **Final human Phase 22 technical acceptance**, after the actual final packet and technical gates are ready. A measurement approval, “continue,” green CI or this prompt is not final acceptance.

All **98 observations** in the latest approved historical assessment refresh have been consumed: eight preparatory plus two whole 45-input batches, two dispatches, zero remaining budget. No fresh observation has been approved or run. No paid call, profile, retry, comparator run or target execution occurred within that refresh. Earlier v13–v21 experiments and stopped sequences are closed historical scopes; preserve their actual dispositions.

Pilots and the full paid benchmark remain **explicitly deferred and nonblocking for Phase 22**, not passed. R84's original wording mentions pilots; apply the recorded removal of pilots as a Phase 22 prerequisite while preserving that historical wording. Phase 21 remains incomplete; Phase 24 adoption/retention and Phase 15 launch gates are unchanged. No merge, marking the draft ready, release, publication, outreach, participant source sharing, telemetry, Phase 23 or other phase is authorized.

Static analysis must never import or execute target code, run upstream tests/builds, install target dependencies, start its browser, render Helm or follow repository escapes/symlinks. Runtime targets run only in owned Sentinel-controlled Docker under the accepted isolation/environment contract. Deterministic scans use the normal rules-only pipeline with model transport forbidden and credentials absent. `--allow-degraded` does not prevent paid calls when a key exists. Do not run `make artifacts-live`.

## 4. Completed gates and limitations that must survive closeout

### Timing and historical conditions

The user approved a **120-second normal performance target and uniform 300-second deterministic static maximum**. Slow inputs continue in the same execution; there is no kill/restart at 120 seconds. Both native and whole-input time must fit the cap, with cleanup separate. This is not a cap on a complete static + model + dynamic invocation, and does not change the dynamic campaign budget. Use the exact definitions in `docs/phase22-timeout-policy.md`; do not add rounding tolerance or claim a speed improvement.

At scanner `1f3f72f`, preparatory run **34564411104** and final run **34566835295** consumed **98/98**, all complete, zero timeouts: **72 within 120 seconds, 26 using extended time**, longest whole input **176.03213226499997 seconds**. Final workflow is `61b19ae`. Both whole historical batches pass **45/45**, each **20/20 vulnerable condition hits** and **zero matching alerts on 25 negative inputs**. All 45 entire ordered reports match across repeats after excluding only the established 11 volatile fields; final reports also match their frozen assessment references.

The user's explicit scope amendment permits reuse of the already passed **whole 25-input development batch** from run **34555414891**, with identical scanner/harness/lock/configuration/input bytes: **10 vulnerable condition hits, exactly two raw Meta operator erratum alerts, zero matching alerts on 13 valid negatives**. Preserve the erratum and raw alerts; do not call all 15 nominal negatives valid or silently relabel them. The retained 37 historical reports plus eight preparations were used only to freeze source assessments, never as a pooled whole-45 execution pass.

Five preparatory report deltas contain **1,191 individually source-assessed diagnostic changes**. The Kubernetes mutation's additional `kubectl_logs` command-injection suspicion is separate from the unchanged named `kubectl_get` condition. Keep it visible without calling it runtime proof or a false positive merely because it is unmatched. All 45 labels/prerequisites/matched keys remain unchanged. Preserve source assessments and raw scorer “unadjudicated”/unmatched counts; named-condition scoring is not an assessment of every finding's real-world truth.

Preserve the original Linux **15/25** at `7555a9d`, its ten Meta timeouts at 120 seconds and skipped historical batches. Preserve the later **62-attempt** run `34555414891`: all attempted inputs completed, but the sequence stopped at a stale historical assessment identity; **53 unstarted observations were closed**. These are retained failures, not current unmet timing gates or reusable budget. The full development batch from that run is reused only under the explicit amendment above.

The Fable Stage 0 scaling probe is also closed: `v18-scaling-assessment.json`, run **34536965288**, 12 observations, four vCPUs reported as two cores with SMT. E3≈2.029, E4≈2.136, E6≈2.125; the prospective premise failed. No partitioning or proposed micro-optimization was retained through this policy change. Do not implement the old Fable proposals as unfinished accepted work.

### Exposed detections and fresh/generalization history

**fetch-mcp, open-webSearch and SearXNG** each pass their exposed five-input native repeat gate at **`2ac39aa9331818fd7e3a86c8323ee8307522c98c`**: complete twice, both correlated vulnerable conditions hit per batch, zero matching fixed/control alerts. `v13-exposed-assessment/packet.json`, `v13-searxng-assessment/packet.json`, subsequent source verifications and the audit bind compatible reuse through deadline-only scanner `1f3f72f`. Do not claim new remeasurement at that later source. Preserve original misses, false alerts, exposure authorizations, qualifier/source judgments and all first frozen results.

The original held-out result remains **10 completed, 10 unsupported, five incomplete; zero hits among four completed vulnerable variants out of ten vulnerable inputs total**. Old v1–v3 sources are exposed and cannot become the new holdout. Preserve the distinction between the original historical 70-warning unadjudicated backlog, separately source-assessed open-webSearch warnings, and SearXNG unmatched condition keys (`v12-searxng-scoring-note.json`). No competitor superiority, full reviewed accuracy, independent human validation or broad generalization claim follows from these gates.

## 5. Execute the exact fresh scope only after its approval

The complete prepared package is **`artifacts/phase22/corpus-replacement-v4/`**. Do not curate a replacement when this frozen candidate is ready. It contains 50 manifest records: **only the five new inputs run**; the 45 prior records remain unchanged.

| Binding | SHA-256 / revision |
| --- | --- |
| `evaluation-proposal.json` | `28cd716118f71c390a3aeb28c5c541981e9196e50fb909ffa26be1da8a989843` |
| `checkpoint-1f3f72f.json` | `e68cd09a5f9fa177728bfbb6e02b5f78a546350e9ed4f5ddc03df53d239e7c25` |
| `manifest.json` | `966b8b0578832916c97018316fe890a428b63533242577b8b7cc6f636b59ca7b` |
| `configurations.json` | `548efe12f406d9ec1a6cfe10243b16f51bbd88832219ece6ec1dc7867ca15355` |
| Vulnerable direct parent | `42daa70c391cde4396de877541a64a9c3f761a9d` |
| Fixed child | `177ec5f8ee9c2d5749035777e562f699971b0da9` |
| Vulnerable archive | `9c2d2b8df464c41556011f3d184aae95ad13357d7992bbbf41e869e7737cc06e` |
| Fixed archive | `4007999123174043250c21efd87561e75b983fa1d8e50a8f3151493d39adc424` |

The repository is **`ymw0407/auth-fetch-mcp`**, advisory **GHSA-pvrj-8cg3-j5f8 / CVE-2026-49857**, with full retained upstream metadata/diff and MIT license. Both exact source versions declare **3.0.1**; these are source-specific vulnerable/fixed labels, not a claim that release 3.0.1 is patched. Retain the advisory metadata/body discrepancy concerning patched 3.0.2 and older “no patch” text. Only `src/security.ts` changes between the direct pair; complete 21-file source archives include their media and licenses.

The condition is initial `auth_fetch` browser navigation to **`http://[::ffff:7f00:1]/`**, with private opt-in and hostname allowlist unset and successful browser startup as a prerequisite. Vulnerable code fails to classify the two-hex-group mapped address as IPv4 loopback; the fixed guard decodes 127.0.0.1 and rejects before `page.goto`. The safe control **`http://[::ffff:808:808]/`** maps to public 8.8.8.8. Labels cover initial classification/navigation only, not DNS, redirects, response contents, capture-button interaction or other tools. Recorded target dependencies/prerequisites include SDK 1.27.1 and Playwright 1.58.2; do not install or execute them.

The two paired mutations only rename `isPrivateV6` to `isRestrictedIPv6` reversibly. This is **one repository and one vulnerability with correlated variants**, curated by the implementation agent **after the immutable scanner freeze**. Source exposure is disclosed. It is not independent human review or an unseen-source claim, and the mapped-loopback concept overlaps the earlier open-webSearch family despite the distinct repository/browser flow. Do not convert four variants into four independent discoveries.

Exact input order:

1. `authfetch-mapped-loopback-vulnerable`
2. `authfetch-mapped-loopback-vulnerable-mutation`
3. `authfetch-mapped-loopback-fixed`
4. `authfetch-mapped-loopback-fixed-mutation`
5. `authfetch-mapped-public-safe`

Exact batch order: **`rules-first` → `rules-repeat` → `semgrep-first`**.

Proposed bounds (not yet approved): **one standard Linux dispatch; 10 native observations plus five Semgrep observations; zero profiles, retries, paid calls or target executions**. Native normal target 120 seconds; native **and whole input** maximum 300 seconds; comparator **and whole input** maximum 300 seconds. Total **75 nominal input-minutes**, **15 seconds cleanup maximum per input**, **90-minute job limit**, **88-minute internal stop**, **two minutes reserved for upload**. Do not start a child without 315 seconds remaining before the internal stop.

Environment: one standard `ubuntu-latest` job, Python 3.12, uv 0.8.22, scanner `1f3f72f`, frozen lock, no larger runner/procurement and no overlap with other owned timing work. Record actual Python patch/packages, CPU/topology/memory/load and workflow identity. Comparator: **Semgrep 1.176.0**, `semgrep/semgrep-rules` revision **`40b8c63f75dc7c22c8a77482d73bfb864b146f7e`**, archive SHA **`beb4ecfbe2ef6d14942bf58c6805456d802d9380fd894c11de8fde957ff1159c`**, **511 configurations / 533 rules**, selected before execution under the exact retained predicate. Use `artifacts/phase20/semgrep-preparation.json` and the exact command in the proposal, with metrics/version checks disabled and local prepared rules.

Before asking for approval, verify source-only materialization, hashes, immutable scanner association, prior-record equality, labels, constraints and the concrete proposed runner/workflow design. Use existing `scripts/phase22_corpus.py`, `scripts/phase20_corpus.py`, `scripts/phase20_measurements.py`, `scripts/phase20_scoring.py`, `measure()`, `frozen(approval_path=...)` and the tested process-group supervisor. Inspect existing callers; do not invent a parallel evaluator. Make only necessary workflow/runner additions in new versioned paths. Never overwrite `v22-refresh-v1/runner.py` or frozen historical artifacts. Synthetic runner checks must not sneak in new full-source observations on the five fresh inputs.

Then ask one concrete approval question binding the exact proposal/checkpoint, frozen scanner, disclosure and 15-observation budget. If the user has already approved that exact scope in the new conversation, record and use that approval without asking again. Generic authority to finish the phase is insufficient for this explicit checkpoint.

After approval:

- Append a receipt binding the actual user decision and proposal hashes. Freeze final runner/workflow bytes and source checks before the single dispatch. Preserve prepared proposal bytes. Use a separate reproducible staging checkout based on the frozen scanner; copy only approved corpus/provenance assets without changing scanner/test/harness/lock bytes.
- Verify scanner, manifest, source, configuration and comparator-rule hashes before each isolated child. Whole-input deadlines begin before `Popen` and include materialization/configuration/import/analysis/report validation/writing; never grant a new 300 seconds after setup.
- Retain commands/exits, full reports, source/resource/environment identities, CPU/wall/timing classifications, warnings/coverage/provenance, cleanup and attempted/unstarted accounting. Verify child process groups terminate and are reaped. Wait for actual tool completion before treating a dependent result as available.
- Validate native JSON and SARIF against the packaged schemas and canonical provenance. Compare **entire ordered native reports**, including findings/captures/warnings/coverage, excluding **only the existing 11 volatile fields** from the established canonicalizer. Do not widen exclusions to make a repeat pass.
- Use identical materialized input records for Semgrep. Score narrow source-grounded named conditions; rule ID or generic source overlap alone is not a condition match. Assess every new unrelated finding/diagnostic and coverage delta against actual source. Preserve uncertainty, unmatched raw counts and existing labels/prerequisites. Do not treat static evidence as runtime proof.
- Report all five input statuses in all three batches, support/completion denominators, vulnerable/fixed/control outcomes, repeat equality, comparator outcomes, durations and both timing classes. Distinguish two correlated vulnerable variants from independent vulnerabilities and process completion from successful detection.

**Exact stop rule:** one attempt per named input per batch. Any infrastructure, execution, timeout, identity, schema, cleanup or ordered-repeat failure closes unused budget. Detection misses and false alerts remain measured outcomes, do not abort remaining outcome collection, and never authorize tuning/retry/case replacement. End after 15 observations even if all succeed. No automatic technical acceptance.

Do not invent a generalization threshold. If fresh results include misses/false alerts, finish authorized outcome collection, preserve first frozen results, source-assess the limitation, explain its product implication and obtain my explicit disposition. Never silently tune, relabel, replace cases or accept the limitation for me. Any correction following these results needs a separate exposure/disposition decision and bounded regression/freeze scope as appropriate. Changes to the scanner after its pre-curation freeze invalidate the original candidate association; disclose exposure rather than calling those sources fresh for a tuned scanner. No endless holdout replacement loop.

## 6. Final verification covers every requirement, not just the fresh results

Read and update **all 89 original requirement rows and all 51 added scope rows**, preserving IDs, source-specific prior judgments and references. Add new scope rows as necessary without renumbering. Historical failed retention attempts remain historical failures with closed budgets; do not convert them to successes or treat them as automatic new work. R66/R88 need actual fresh outcomes/assessments and any explicit limitation decision; R84 requires final acceptance. R77/R78 remain user-deferred.

Account for all ten benchmark families and all five compatibility areas in the approved plan. Preserve source-established Python/static TypeScript discovery/imports/workspaces/exports/configuration/boundaries, helper/class/factory/client/guard/credential semantics, Helm original-byte omissions/strict YAML, SENT-012–016 and unchanged Kubernetes SENT-002 meaning. Rule IDs and canonical Finding/evidence/provenance/remediation/OWASP mappings must not drift. No independent discovery origin, new language or stateful exploit expansion.

Preserve candidate-bound review with **160 unique source lines total**, cross-file caller/guard/sink identities, omissions/redaction and request/cache compatibility. Keep schema **1.7.0**, legacy **1.3–1.6** migrations, SARIF **2.1.0**, all report/baseline/console/Action consumers, workspace structured coverage, and actual unknown/unsupported/incomplete states valid.

Preserve ordered runtime campaigns, stable attempt IDs, fair scheduling/rotation, baseline/prerequisites/schema checks, observable effects, actual planned/eligible/started/tested totals, unstarted remainder and exit 3 for incomplete execution. The dynamic **24 started attempts / 120 seconds** budget is separate from the new static timing maximum. Keep CLI > environment > file > default precedence, rules-only bypass, cleanup and proof preservation through model review/output.

### Existing quality evidence and when new checks are necessary

Final CI **34566768988** and docs **34566768974**, at `61b19ae`, pass **all 29 normal jobs**; two optional jobs are skipped. All **12 Linux/macOS/Windows × Python 3.10–3.13** quality suites pass **2,194 tests, 36 skips, no xfail**, hosted branch coverage **89.67–89.69%**. **153 wheel and 166 sdist members** were compared byte-for-byte to actual Git source; 225 uploaded files/full logs are retained. The local full suite at identical product bytes passed **2,194 / 36**, **89.68% branch coverage**. See quality and local packets in §2.

Inspect actual Makefile/workflows/lock/configuration. Complete affected Ruff/format, strict mypy, lock/schema/native/SARIF checks, full pytest/branch coverage (at least 80%), dependency audit/notices, offline generated artifacts, strict docs, builds/installed wheel, Docker/isolation/Action/hooks, and required hosted matrix checks for the final code/workflow candidate. Keep optional benchmark workflows gated; a push must not silently launch new corpus measurements. Reuse byte-identical verified evidence with explicit bindings where permitted; do not endlessly repeat unaffected tests. A runner/workflow change must get the required current workflow/quality validation even when product scanner bytes stay frozen.

Normal CI's pinned historical reproduction scanner is **`8824014e961722980757bb589009dc59b78d9a37`**, not `1f3f72f`. Retain its actual support/completion states; it cannot substitute for current-source historical/fresh measurements. Never imply a later docs-only commit received a new hosted code pass.

### Production review captures and Git runtime

`v19-final-production-capture-revalidation/packet.json` regenerates and replays **six actual production requests** at `1f3f72f`: two approved Phase 22 requests plus four older demo requests, **zero new calls**. Revalidate by compatible source binding or actual production request construction when affected, including full request hashes, fingerprints, model/settings, reviewer, packaged source and fixtures. Retained Phase 22 fingerprints:

- TypeScript: `b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f`.
- Runtime: `b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39`.

Never edit fingerprints/cassettes to force reuse. If a required request changes incompatibly, prepare the smallest exact paid-capture proposal before calling, and complete unaffected checks while awaiting the decision.

The approved Git runtime image is **`sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`**, environment packet SHA **`a3481db5cfc181de2c0c1a51beca88a332570de00443655016945060394491d7`**, **mcp 1.29.0**. `v12-compatible-evidence/packet.json` and v19/v22 bindings cover the actual catalog/campaign/config/runtime components. **All 13 campaigns remain incomplete: 1,040 planned/eligible, 312 tested, 728 remaining, exit 3, cleanup verified.** Compatible reuse does not establish complete Git coverage or demonstrated protection. The owned demo's **20/20 attempts and 14 findings** are a separate narrower result. Recheck affected authorized Docker scope only; no unapproved environment switch or target execution elsewhere.

Local mock HTTP checks may require permission for scanner-owned localhost sockets, and owned Docker checks may require sandbox escalation. These are not paid/model-call approvals. Keep credentials out of commands/logs; cleanup only owned labels/processes, then verify no owned work remains.

## 7. Produce a concrete acceptance packet, then obtain the decision

Before asking for final acceptance, finish all independent authorized work and deliver one reviewable final packet. Include:

- Exact measured scanner, source/harness/lock/config/input/checkpoint identities, workflow/tested/delivery revisions, all approval and budget receipts, and archive/member hashes.
- Every original and added requirement with actual source/test/evidence and disposition: passed, explicitly user-deferred, **proposed** documented limitation awaiting decision, human-accepted documented limitation with its actual receipt, or unresolved. Do not mark a new limitation accepted in advance.
- Development 25, historical whole 45 + 45, three exposed SSRF families, original held-out result, fresh five-input native pair/comparator, all source assessments and honest repeat/support/completion/detection denominators. Separate actual remeasurements from justified compatible reuse.
- Current-source quality/packaging/hosted/docs/Action/Docker results, six replay bindings, Git runtime limitations, zero additional paid calls or exact separately approved expenditure, pilot/paid deferrals and unchanged later-phase gates.
- All first frozen failures, errata and historical attempts, plus the current authoritative result. Explain the remaining practical limits without presenting fixture success or code coverage as accuracy or a completed scan as proof of safety.
- Updated owning docs and consolidated PR body so I can review the actual final state before deciding.

**Readiness conditions for requesting Phase 22 technical acceptance:**

1. All three exposed SSRF final repeat gates remain passed and source-compatible, with source-assessed findings/coverage.
2. The approved timing/condition gate remains passed: whole 25 development reused under the explicit amendment plus both whole 45 historical batches, at immutable scanner `1f3f72f`, with 120-second target / 300-second maximum reported honestly. Do not reinstate the superseded 120-second hard gate or claim it passed historically.
3. The exact fresh freeze/evaluation was approved, executed within its bounds, validated and source-assessed. Actual detection limitations are prominent, with any required explicit disposition; no hidden fresh miss, invented threshold, unsupported “freshness” claim or silent waiver.
4. Every other authorized technical/engineering/evidence/draft-delivery requirement is complete or has an actual applicable user deferral/explicit scope decision. Known implementation/execution failures are not silently reclassified as accepted limitations.

When these hold, ask me explicitly to **accept Phase 22 technical completion under the recorded revised scope and its enumerated limitations**, linking the concrete final packet and exact identities. Keep Phase 22 incomplete until I decide. Do not count this continuation, previous budget approvals or green checks as acceptance.

If a technical gate fails, preserve/deliver completed work, close its budget accurately, and finish independent authorized checks before presenting the smallest concrete next decision. A scope revision must identify the unchanged failed gate, proposed change and consequence, and requires my explicit approval. If I decline acceptance or request a correction, continue within the applicable scope and checkpoints; do not mark the phase complete.

## 8. Evidence preservation, known corrections and final delivery

Preserve **seals 1–51** and directly tracked post-seal bindings. Latest **`evidence-v51.tar.gz`** SHA-256:

`f807e90d33215b8956b11c527eab0c516e1a368326a6dbe72920549988dd58b3`

It contains **1,141 files**, **372,792,245 raw bytes**, **19,136,410 compressed bytes**; every member and all 50 prior archive hashes were verified after writers stopped. It binds source through `61b19ae`, measured scanner `1f3f72f`. The next unused seal is **52**, unless newer work exists when you resume. Never overwrite a seal.

Follow integration README's numeric restoration order into separate staging, validate archive/member hashes before copying, and require existing destinations to match identical bytes or the recorded previous hash. Stop on unexplained conflict. Ignored expanded evidence is not disposable. Owning docs and final audit/documentation/delivery bindings are directly tracked where documented; do not pretend local post-delivery readbacks were already inside the commit they describe.

Temporary `/private/tmp/phase22-*.py` helpers must not be the only reproducible source. Executed v22 helpers are retained in **`diagnostics-v51.tar.gz` inside seal 51**, and command-wrapper `*.untracked.tar.gz` captures; `v22-final-delivery-helper.py` is directly tracked. Inspect before reuse because many helpers hardcode revisions/output names. Use unique output labels: the historical command wrapper does not prevent overwrites. Keep command-wrapper paths distinct from result-packet paths, and await each dependent assessment's successful exit before aggregation.

Mandatory errata to preserve and interpret correctly:

- **`v22-refresh-disposition.json` is superseded and wrong.** A helper aggregated before the local second-batch assessment finished, although both native jobs had completed. Its 53-attempt/45-unstarted failure claim is not an actual execution/budget result. **`v22-refresh-disposition-corrected.json` is authoritative**, with `v22-aggregate-correction.json`; both originals and corrections are retained. The corrected helper requires both assessment packets when the hosted run succeeds.
- **`v22-quality-audit-label-correction.json`:** a cassette loop variable shadowed the requested stage. The preparatory audit was misnamed `v22-phase17-quality-audit/packet.json`; the final audit refused that existing destination after completing checks. Corrected read-only audits are `v22-preparatory-quality-audit/packet.json` and `v22-final-quality-audit/packet.json`. No tests/native observations were rerun; preserve the misnamed original.
- **`v22-check-failure-assessment.json`:** preserve pre-binding Ruff docstring failure/correction, source-hash helper path-prefix correction before freeze, and failed PR readback assertion after push but before dispatch. The initial returned JSON was not retained, so “stale head” is an inference, not a directly observed cause. Later exact identity was verified and the final dispatch occurred once. This assessment refines the earlier `v22-final-readback-correction.json` wording.
- Preserve **`v20-collector-metadata-correction.json`** and original stale collector metadata with the actual frozen candidate. Do not count ordinary helper corrections as new native attempts or erase their failures.
- `v22-in-progress-checkpoint.json` is a historical running-state snapshot, not current status. Its helper hashes predate some final guards.

Retain actual commands/exits/logs, helper sources and patches, input/source/test/harness/configuration/environment identities, native/comparator reports/resources, schema/repeat checks, source adjudication, budgets/cleanup/unstarted records, capture/cost provenance and full hosted artifacts. Do not edit raw stored `.patch` evidence to remove unified-diff whitespace; scope product/docs diff checks and verify evidence hashes separately. Make dependent shell operations fail safely. Avoid circular claims that a receipt contains the hash of its own final commit.

Stop writers before creating the next seal; hash/read back every member and verify old archive hashes. Update restore/index docs. Keep final evidence reproducible in Git/artifacts, not only in temporary paths. Preserve superseded drafts and source-specific historical statements.

Make reviewable commits on `phase22/integration`. Verify actual PR #37 head/base/draft and PR #36 ancestry before batched push; preserve the separate main worktree. Update the **existing draft**, then read back exact head/base/draft/body. Do not create a replacement PR unnecessarily, mark ready, merge or release. Run required CI on the final code/workflow candidate. A later docs/evidence-only commit may use the established permitted CI-skip convention only after proving code/test/workflow/package inputs equal the tested candidate; run affected docs checks and identify compatible reuse explicitly.

Reconcile current owning docs while preserving history: `AGENTS.md`, `ROADMAP.md`, `ARCHITECTURE.md` where affected, root `README.md` where affected, `docs/phase22-technical.md`, `docs/phase22-implementation-status.md`, `docs/phase22-ssrf-follow-up.md`, `docs/phase22-corpus-review.md`, `docs/phase22-timeout-policy.md`, rules/compatibility/configuration docs, integration requirements/progress/README, replacement-v4 status, final audit/summary and draft body. Rebind final document hashes after final edits; an earlier audit-stage binding does not describe later docs.

## 9. After I accept: complete the actual phase closeout

**Continue in the same conversation after my explicit acceptance. Do not end with “accepted” while leaving delivery undone.**

1. Record my exact acceptance decision in a new versioned receipt, binding the accepted packet, measured scanner, tested workflow, delivery/evidence identities, explicit limitations and retained deferrals. Do not backdate acceptance or alter the approval history.
2. Update R84 and the final audit with the actual decision. Mark R66/R88 according to measured results and the explicit disposition; do not convert an accepted documented miss into a detector hit. Preserve all 89 IDs and added historical-scope rows.
3. Mark **Phase 22 technically complete under the explicitly accepted revised scope** in owning status/checklists, roadmap, implementation/technical/corpus/integration docs and final PR description. Preserve original failed measurements, original held-out limitations, incomplete Git campaigns, deferred paid benchmark/pilots, incomplete Phase 21 and unchanged Phase 24/15 gates. Distinguish technical closure from independent validation and launch.
4. Validate the final documentation/schema/status changes as applicable, verify no unexplained code/workflow/package drift, stop owned work, seal new evidence at the next unused number where required, read back hashes and update restoration/documentation bindings.
5. Commit and push the closeout to the same draft PR #37, verify exact remote head/base/draft/body, preserve PR #36/main worktree, and retain a delivery receipt. If a push/check fails, resolve or accurately report it; acceptance alone does not prove delivery.
6. Give a concise final delivery statement linking the acceptance receipt, final audit/evidence index and PR, with exact delivered revision, measured scanner, key outcomes and remaining accepted limitations/deferrals. Explicitly distinguish Phase 22 technical completion from merge/release/launch. Stop before Phase 23 unless I separately authorize it.

The objective is met only when the required work is actually complete, I have explicitly accepted it, and the accepted closeout is delivered and verified. Preserve this objective across compaction and status questions. Start with a brief plan and verified baseline; explain any genuine approval boundary by naming the exact proposal/instruction, and continue independent authorized work while a decision is pending.

## Appendix: all 89 original requirements at this handoff

The table below is copied from `v22-closeout-audit/packet.json` as a completeness checklist. Read its full evidence, source bindings and interpretations, and the **51 additional scope rows**, before updating dispositions. “Passed” here is the recorded starting disposition, not permission to skip affected final verification. R84's pilot wording is historical; the explicit pilot deferral/removal described above controls Phase 22 acceptance.

| ID | Starting disposition | Requirement |
| --- | --- | --- |
| R01 | passed | Correct dirty worktree and packet identities |
| R02 | passed | Source-established constructors, fields, aliases and replacement invalidation |
| R03 | passed | Read-only builtin dictionary inspection with shadowing controls |
| R04 | passed | Reflection, unknown mutation, custom hooks and constructor/decorator ambiguity |
| R05 | passed | Imported handlers and schemas |
| R06 | passed | Aliases/re-exports, local imports and package exports |
| R07 | passed | Statically bound helpers, factories, inherited/bound methods |
| R08 | passed | Cross-file caller/guard/sink evidence and binding identity |
| R09 | passed | Genuine SDK context vs caller/fake/rebound/local SDK |
| R10 | passed | Low-level registration and dispatch |
| R11 | passed | uv/npm/pnpm members and exclusions |
| R12 | passed | TS aliases/inherited local compiler configuration, inaccessible parents |
| R13 | passed | Aggregate root vs individual config, nested config disclosure |
| R14 | passed | Per-member counts without shared-file duplication |
| R15 | passed | Inaccessible/unsupported members, ambiguity/import/reflection/schema gaps |
| R16 | passed | Repository escapes and symlinks; dynamic single Python package |
| R17 | passed | Helm original bytes/text secrets and explicit YAML omission |
| R18 | passed | Historical atlassian-auth condition |
| R19 | passed | Historical atlassian-ssrf condition |
| R20 | passed | Historical atlassian-upload condition |
| R21 | passed | Historical excel-boundary condition |
| R22 | passed | Historical filesystem-prefix condition |
| R23 | passed | Historical git-arguments condition |
| R24 | passed | Historical git-repository condition |
| R25 | passed | Historical git-staging condition |
| R26 | passed | Historical kubernetes-shell condition under unchanged SENT-002 meaning |
| R27 | passed | Historical mobile-output condition |
| R28 | passed | Mastra failure-return flags and unsafe directory fallback |
| R29 | passed | Explicit description override, exfiltration, cross-tool redirection |
| R30 | passed | Benign instructions and quoted warnings; parameter/low-level metadata |
| R31 | passed | dbt selector options through nested factories/mutable argv |
| R32 | passed | Git option positions, rejection, command-specific terminators, object APIs |
| R33 | passed | Meta image caller URL request and scheme/private/loopback checks |
| R34 | passed | Fixed public authority plus caller suffix; enforced actual return value |
| R35 | passed | Meta ContextVar/HTTP authentication/operator fallback |
| R36 | passed | Atlassian lifespan/operator origin, real SDK request, service/client construction and enforcement |
| R37 | passed | Applicable Python and TypeScript positives/negatives for every new rule |
| R38 | passed | Rule defaults, selection, inline suppression, baseline/severity identities |
| R39 | passed | Canonical Finding, evidence/provenance/remediation/OWASP and limitations |
| R40 | passed | Traversal/absolute/prefix/symlink and unrelated/discarded/replaced controls |
| R41 | passed | Helper execution, ineffective auth, unrelated validation, untrusted hashing |
| R42 | passed | Candidate-bound 160 unique SOURCE lines across files |
| R43 | passed | Overlap dedup/omissions, exact references, redaction LF/CRLF/CR, boundaries/symlinks |
| R44 | passed | Unchanged request/cache compatibility and capture reuse |
| R45 | passed | Nullable reviews/Finding identities and all runtime proof through review |
| R46 | passed | Runtime enumeration of every supported tool/path/mutation under SENT-008–011 |
| R47 | passed | Fair rounds and rule/argument rotation; bounded GPT priorities |
| R48 | passed | Stable attempt ID independent of scan/time/schema identity |
| R49 | passed | 24 STARTED attempts / 120s; timing after image and before discovery |
| R50 | passed | CLI > env > file > default positive settings; rules-only bypass; Action config |
| R51 | passed | Fresh baseline/attack; invalid baseline prevents attack |
| R52 | passed | Discovery/baseline/attack schema drift |
| R53 | passed | Unsupported/inconclusive/startup/execution/interruption states; cleanup |
| R54 | passed | Planned/unstarted records, no fabricated empty/incomplete coverage, exit 3 |
| R55 | passed | Preserve every repeated observable proof through merge/review/output |
| R56 | passed | Native 1.7 unique IDs and matching ordered binding/discovery/outcome references |
| R57 | passed | Actual planned/eligible/started/tested totals and remainder/budget invariants |
| R58 | passed | Legacy 1.3/1.4/1.5/1.6 reports/baselines, honest unknown coverage |
| R59 | passed | Workspace structured coverage validates against inventory |
| R60 | passed | Console/native/SARIF and every rule-keyed consumer |
| R61 | passed | Packaged Finding/report schemas, SARIF 2.1.0 validation |
| R62 | passed | Owning architecture/schema/rule/compatibility/config/onboarding/Action docs |
| R63 | passed | Historical45-input deterministic repeat pair:300-second maximum,120-second performance target |
| R64 | passed | All 20 vulnerable condition hits; zero fixed/safe condition alerts |
| R65 | passed | All five Phase 22 development pairs, paired mutations, controls |
| R66 | unresolved | Fresh holdout outside tuning, separate results/no invented threshold |
| R67 | passed | All new/changed unrelated findings adjudicated; historical 70 unchanged |
| R68 | passed | Pinned comparable Semgrep rerun; Snyk/Cisco unmeasured |
| R69 | passed | Per-input statuses/support/completion denominators, repeated differences |
| R70 | passed | Git mcp==1.29.0 image/environment identity and Docker startup/discovery/campaigns |
| R71 | passed | Full Ruff/format/strict mypy/lock/schema/native/SARIF/pytest >=80% branch |
| R72 | passed | Audit/notices/generated artifacts offline/strict docs/build/installed wheel |
| R73 | passed | Docker/Action/rules-only network isolation and supported fixtures |
| R74 | passed | Hosted Linux/macOS/Windows Python 3.10–3.13 |
| R75 | passed | Concrete paid packet: actual config/model, exact cases/requests/purpose/reuse/replacements |
| R76 | passed | Token/request/dollar ceilings, identities, retries/failure/stopping policy |
| R77 | explicitly user-deferred | Reviewed 45/45 completion/retention on identical inputs; abstention/needs_review/suppression accounting |
| R78 | explicitly user-deferred | Separate reviewed holdout, latency/tokens/cache reuse/cost |
| R79 | passed | Lossless numbered evidence batch after v3; per-file hash readback/extraction |
| R80 | passed | Complete command/source/harness/corpus/config/environment identities; failures/limitations |
| R81 | passed | Reviewable local commits on single integration branch; preserve old drafts |
| R82 | passed | Inspect real ancestry/bases and deliver one consolidated final draft |
| R83 | passed | ROADMAP/status separate delivered code, technical/paid/human/pilot gates |
| R84 | unresolved | Human technical acceptance and external pilot-dependent gate |
| R85 | passed | Preserve static no-execution/no-symlinks/no-tooling; Docker-only runtime |
| R86 | passed | No paid calls, merge/release/outreach/source sharing without approval |
| R87 | passed | Final fetch-mcp exposed correction: two complete five-input native runs, 2/2 vulnerable matches and zero matching fixed/control alerts, source-assessed deltas |
| R88 | unresolved | Next independent fresh corpus frozen after stabilization, exact approval before bounded evaluation, actual outcomes and source assessments |
| R89 | passed | Final exposed SearXNG correction: source-bound default loopback condition, two complete five-input native runs, 2/2 vulnerable matches and zero matching fixed/control alerts |
