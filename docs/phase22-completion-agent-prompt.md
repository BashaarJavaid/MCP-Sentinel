# Phase 22 continuation: finish SearXNG, execution reliability, verification and human closeout

Execute this complete continuation for **PortunusMCP Sentinel** in `/private/tmp/mcp-phase22-options`. Verify current state before editing. Finish the remaining SearXNG correction and measured execution-reliability work, preserve the working fetch-mcp and open-webSearch corrections, complete final-source verification and a separately approved fresh evaluation, and continue with me through **explicit Phase 22 technical acceptance and the subsequent closeout delivery**. Do the work, not just a plan or another handoff.

Preserve existing implementation, tests, approvals, source archives, first frozen measurements, failures, source assessments and sealed evidence. Ask only for genuinely missing decisions or the explicit checkpoints below. **No additional paid model calls without my approval.** A passing engineering suite, completed scan, or vulnerable hit accompanied by the same fixed false alert does not establish the required protection.

This document was prepared on 2026-09-10. Preparing it did not execute or approve new experiments in the preceding conversation. **When I give this prompt to another agent to execute, the continuation authorization in §2 applies.** Record that new instruction separately; never rewrite historical approvals or prepared proposals to imply earlier authorization.

## 1. Authority, conventions and baseline to reverify

Read applicable `AGENTS.md` and coding skills. Apply Ponytail full: trace the actual shared flow and all affected callers, reuse existing structures, reproduce security failures in minimal durable tests before fixing them, and make the smallest correct change. No speculative frameworks, dependencies, languages, caches or abstractions. Use `rg` first for source searches; batch independent reads, keep dependent mutations sequential, and keep progress updates concise. Do not delegate to other agents unless I or applicable instructions explicitly authorize delegation.

Read `mcp-sentinel-buildplan.md` first for historical context and §11 non-goals; defer to `ARCHITECTURE.md`, `ROADMAP.md` and `docs/phase22-technical.md` for active contracts. Historical phase completion statements and older current-status paragraphs remain evidence for their named sources, not the latest state.

Read these records before implementation, using targeted extraction for large JSON packets rather than truncating their relevant contents:

- `artifacts/phase22/integration/next-agent-handoff-20260908-v2.md`, including its full technical scope and sections 9–17.
- `docs/phase22-final-agent-prompt.md` and `docs/phase22-detection-timing-closeout-agent-prompt.md`. Their old identities, budgets and unfinished-work statements are superseded by later receipts/results and this continuation; do not replay their consumed authorizations.
- Integration `requirements.md` (**all 89 rows**), `README.md`, latest `progress.md`, `v12-closeout-audit/packet.json`, and `v12-current-source-test-bindings/packet.json`.
- `docs/phase22-implementation-status.md`, `docs/phase22-ssrf-follow-up.md`, and applicable architecture/rule/compatibility docs.
- `artifacts/phase22/completion-scope-v1/decision.json` and `follow-up-proposal.json`.
- `v11-follow-up-authorization.json`, both v10 proposals it approved, `v11-performance-disposition.json`, `v12-scope-interpretation-correction.json`, and `v12-next-searxng-proposal.json`.
- `v12-native-plan.json`, `v12-exposed-assessment/packet.json`, `v12-searxng-assessment/packet.json`, and `v12-searxng-scoring-note.json`.
- Replacement-v1/v2/v3 manifests, exposure receipts, original freeze/checkpoint/authorization records, source reviews and first frozen results, following their linked provenance.
- `v12-hosted-audit/packet.json`, `v12-production-capture-revalidation/packet.json`, `v12-compatible-evidence/packet.json`, `v12-final-documentation-binding.json`, `v12-delivery-verification.json`, and current tracked draft body `v12-closeout-draft-body.md`.

Unless otherwise stated, `vN-*` paths in this prompt are relative to `artifacts/phase22/integration/`.

Verified when preparing this handoff:

| Item | Identity / state |
| --- | --- |
| Active worktree / branch | `/private/tmp/mcp-phase22-options`, `phase22/integration` |
| Local HEAD and live draft PR #37 head | `8a991500682c46c95fa3a4e4092cee1ee7f3b7d0` |
| Documentation/evidence parent | `da2927ede4db872e2104ae5348d35f395737624a` |
| Actual final tested/measured scanner | `6eb482ce4cee5c4e94bd782f47ef894af1681e65` |
| Intermediate factory/else implementation | `02e8ef72e26aef47fa33ca87d345f3ae157a6eae` |
| Previous frozen scanner | `7555a9d3b472516ea880bd0ba8fbd25e89699453` |
| Scanner source SHA-256 | `519e706e349a1a0125746c787861a497cf4f6a273dde51d81e1e9ef2945558f4` |
| Measurement harness SHA-256 | `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add` |
| Lock SHA-256 | `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b` |
| Existing draft | https://github.com/BashaarJavaid/MCP-Sentinel/pull/37 — OPEN, draft |
| Draft base / recorded PR #36 parent head | `phase22/description-poisoning`, `8b6b0ddf1d6f6cf5a8da3ab9421471865b801455` |
| Separate main worktree | `/Users/bashaarjavaid/Projects/MCP-Sentinel`, clean, `phase22/python-containment`, `4cd57593b2585b9ee05c0f175930e6a0d76d362a` |

The two latest commits change documentation/evidence only; tested code/test/workflow/package inputs equal `6eb482c`. Do not call those commits new hosted code passes. The existing draft body was bound to `v12-closeout-draft-body.md`; reverify actual remote metadata/body and ancestry before delivery.

Reverify Git status, worktrees, source/lock/harness identities, ignored evidence and active owned processes before editing. Preserve later user/agent changes. Before this prompt was created, the only untracked files were the two preceding user prompt files; this new prompt is also intentionally left untracked. Do not indiscriminately add or remove user instructions. Preserve all detached/increment worktrees, especially frozen `62987a6` and `7555a9d`; never tune inside them. No owned scanner/test/collector processes remained at the prior closeout; verify instead of assuming.

Use the existing locked environment `/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv`, putting its executables first on PATH and explicitly importing active-worktree source with `PYTHONPATH=src:.` or an exact active-root path. Verify versions: local Python 3.12.13, Semgrep 1.176.0, mcp 1.29.0, pytest 9.0.3 and pydantic 2.13.4 were recorded. Do not accidentally use the main checkout's editable package. Actual supported hosted Python versions remain governed by the workflow.

## 2. Authorization and checkpoints

Execution of this prompt authorizes completing the remaining Phase 22 work: source investigation and correction, durable regression tests, ordinary reversible implementation work, necessary offline/engineering/runtime checks, evidence and owning docs, local commits and batched delivery to existing draft PR #37. Do not request ordinary editing permission again.

### Newly authorized SearXNG pass

Execution of this prompt **approves the exact bounded next pass in `v12-next-searxng-proposal.json`**, SHA-256 `148c4b497964e24397532a1b3e4f5d89693b0234a79c99ce16e9028723a0666b`. Verify its bytes, then append a versioned receipt binding this instruction, starting source and v3 manifest before new measurements. Preserve the proposal's `prepared_not_approved` bytes as historical.

The bounds are:

- At most two instrumented native traces, one each on `searxng-default-loopback-fixed` and, only if needed, `searxng-default-loopback-vulnerable`.
- One bounded shared-root correction approach based on the actual traced cause, with a durable minimal reproduction and effective/ineffective controls.
- Ten final SearXNG native observations: all five original exposed inputs twice.
- Twenty existing-family native regressions: fetch-mcp and open-webSearch, each five inputs twice.
- Maximum **32 native or instrumented input executions**, **120 seconds per input**, nominal maximum **3,840 input-seconds**; zero paid calls, comparator runs, full benchmark retries or target execution.

Ordinary unit tests and affected engineering checks are not new-corpus evaluation. Count every native/instrumented input attempt, including failures and partial results. Do not disguise additional full-source executions as unit tests. Unused optional traces need not be consumed. Coordinate final measurements with stabilization of both detector and performance changes so avoidable edits do not invalidate the final-run budget. If further edits do invalidate it, disclose that and prepare the smallest additional budget; do not silently exceed the approved bounds.

### Performance continuation

Investigating existing source and retained profiles and preparing a concrete alternative optimization is authorized now. The v10 helper-context proposal approved by `v11-follow-up-authorization.json` already reached its explicit no-safe-work stopping condition; its unused maxima are **not an open budget**. Do not restart it or repeat the failed full Linux job on unchanged source.

Use retained evidence to prepare a new bounded performance proposal specifying the demonstrated expensive operation, safe correction strategy, exact inputs, maximum optimization attempts/profiles/native runs, deadlines, baseline comparisons, environment and stopping condition. Ask for that concrete additional measurement scope before new performance experiments. Continue independent authorized SearXNG and engineering work while the decision is pending. Once I approve it, execute without asking again for routine edits/checks inside its scope.

A further **full Linux development → historical → historical sequence** remains a separate checkpoint: prepare its exact immutable candidate and proposal after demonstrating native improvement, then request approval before dispatch. The earlier sequences and diagnostic authorization were consumed. No runner change or gate exception is implied.

### Other explicit checkpoints

- New fresh corpus freeze/evaluation: exact stabilized scanner, source-exposure disclosure, manifest/checkpoint and bounded runs approved before any new-corpus native or comparator evaluation.
- New paid calls: exact named requests, purpose, maximum cost and stopping conditions approved first. The two historical Phase 22 requests cost $0.071799 total; their approval is spent. The full 396-request paid benchmark remains user-deferred.
- A different tested Git SDK/runtime environment or paid execution resources, if actually necessary.
- Additional experiments beyond an approved budget/stopping condition; further full retries, runner changes or gate exceptions.
- Final human Phase 22 technical acceptance, only after the concrete final packet is ready and technical gates pass.

Do not resurrect the premature guard-contract checkpoint in `v11-searxng-boundary.json` / `v11-scoped-guard-proposal.json`: `v12-scope-interpretation-correction.json` explicitly corrects it. Existing source-bound URL guard evidence supports a narrow correction within the canonical model. This does not authorize unrelated new review modes or evidence origins.

Pilots and the full paid benchmark are deferred and nonblocking for Phase 22; neither counts as passed. Phase 21 remains incomplete. Phase 24 adoption/retention and Phase 15 launch gates remain unchanged. No merge, release, publication, outreach, telemetry, automatic rule promotion, Phase 23 or other next phase is authorized.

Static work must never import/execute target code, run upstream tests/builds, install target dependencies, render Helm, or follow repository escapes/symlinks. Runtime targets run only in Sentinel-controlled Docker under the accepted isolation contract, never on the host or production endpoints. Dependency-source review is read-only. Deterministic runs use the unchanged normal rules-only pipeline. `--allow-degraded` does not prevent paid calls when credentials are present; do not use it as an offline guarantee or run `make artifacts-live`.

## 3. Finish SearXNG discrimination without losing existing corrections

The remaining detection defect is specific: the full-source native scanner now detects both vulnerable variants, but **also flags both fixed variants without retaining the narrow guard qualifier**. Its MCP dispatch remains unresolved. Focused tests pass; the actual full-source cause of qualifier loss is **not established**. Do not treat suspected startup callbacks, merges, config helpers or invalidation as a proven cause.

Source and condition:

- Repository: `ihor-sokoliuk/mcp-searxng`.
- Vulnerable parent: `3010d1e80ee21baa3d33fcbe0fe2bd5006f285e2`.
- Fixed child: `48e5ecdcb4166a60b94c252dbe74b0a318110ac4`.
- Both source revisions declare 1.1.1; the fixed label is source-specific, not a generally patched package-version claim.
- Manifest: `artifacts/phase22/corpus-replacement-v3/manifest.json`, SHA-256 `275c98478617c76f92c6e0450b52c62f370a9ae22386022051b50ee792adffdd`. Verify bytes against the original checkpoint.
- Read v3 `review/condition-review.json`, retained full source archives/licenses, `checkpoint-7555a9d.json`, `authorization-7555a9d.json`, `exposure-and-fix-authorization-v1.json`, and linked original native/comparator evidence.
- Condition: caller-supplied `http://127.0.0.1/` reaches the initial outbound request through `web_url_read`, ordinary stdio startup, empty cache, no proxy and unset `MCP_HTTP_HARDEN` / `MCP_HTTP_ALLOW_PRIVATE_URLS`. The vulnerable policy returns early with hardening off; the fixed policy rejects the parsed loopback hostname under defaults.
- DNS, redirects, IPv6, HTTP authentication, response conversion and exfiltration are outside this narrow condition. The safe public-IPv4 classification control is not proof of successful downloading or broad SSRF protection.

Original frozen evaluation at `7555a9d` completed all five cases twice natively and once with pinned Semgrep; both tiers missed both correlated vulnerable variants. Preserve those 0/2 results. After exposure/fix, `v12-exposed-searxng-rules-{first,repeat}` at `6eb482c` completed 5/5 each, detected 2/2 each and produced **two condition-matched fixed false alerts per batch**. All ten earlier approved observations are consumed. Maximum wall times were 12.243s and 13.594s. All five reports retained four prior SENT-006 HTTP findings and a generic SENT-015; vulnerable sink was `src/url-reader.ts:262`, fixed/control sink `:287`. The safe control's broad URL candidate was source-assessed outside its exact public-input condition, which does not waive the fixed false alerts.

Preserve the implementation already delivered:

- `typescript_path_flow.py` tracks source-bound SDK class identities, real low-level `Server`, `McpServer.server`, actual imported `CallToolRequestSchema` registration and Semgrep optional `else` wrappers. Replaced/escaped receivers and other schemas retain correct handling.
- `typescript_registration_flow.py` includes low-level Server factory discovery.
- `TypeScriptURLFlow` in `rules/sent015.py` retains narrow `loopback-ipv4` evidence and default-only `loopback-ipv4-default` evidence when **every normal helper exit** either enforces protection of the same URL or requires a genuine positive environment option equal to `"true"`.
- Source-bound unshadowed `process` / `process.env`, replacement/escape invalidation, raw bracketed hostname versus IPv6-normalized hostname distinctions, and the minimal shared `exit_facts` hook are intentional. They do not establish unrestricted SSRF safety.
- Eighteen focused guard controls pass, including imported config/factory/redirect-layout controls and negative missing-hardening/unknown-condition/mutation/callback cases. Factory/else tests also cover replacement and escape.

Trace fact creation, propagation, merge and invalidation identities through actual production discovery → factory/low-level MCP registration → dispatch/arguments → imported URL helper → source defaults → guard → casted Undici fetch. Use only native source flow; no evaluator-injected arguments, assumed environment bindings, target execution, report rewriting, hardcoded repository/case IDs or attack-URL shortcut.

Reproduce the actual loss as a minimal durable failing test before correcting its shared root. Inspect every caller of changed shared functions and relevant SENT-012/015/016 and Python siblings. Check effective/ineffective guards, unrelated/replaced/escaped URL values, opt-in versus missing-hardening semantics, branch exits/throws/returns, alias/shadow/replacement, unknown callbacks and real SDK identity. **Do not exempt `process.on`, `once`, `cwd`, arbitrary callbacks or unknown functions as harmless without establishing the required effects.** If the supported model cannot safely represent the path within the one approved approach, retain the result and present the specific next decision.

Final correction gate: all five exposed SearXNG inputs twice, each native and end-to-end duration within 120 seconds, both vulnerable variants with source-grounded SENT-015 condition matches, **zero condition-matched fixed/control alerts**, valid native JSON/SARIF/canonical provenance, entire ordered repeat equivalence except recorded volatile fields, and source assessment of every new/changed finding or diagnostic. Narrow qualification may coexist with broader candidates; never hide real remaining uncertainty by suppressing whole findings or changing scoring labels. Explain actual recognized/unresolved coverage separately from detection.

Preserve and recheck both working exposed families on the same final source, five inputs twice each:

- **fetch-mcp:** replacement-v2, vulnerable `9fd840d575e68a37f72f07b8f4d2c77f87698c36`, fixed `e7659f8cca26ce051b65f5bc28418df155812b8e`; initial private-IPv4 request through `fetch_html`. The source fix validates the parsed hostname with actual `private-ip`, whereas the vulnerable source checks the whole URL. Preserve genuine imported schema parsing, static/private/async helpers, receiver identity and narrow guard controls.
- **open-webSearch:** replacement-v1, vulnerable `e29b2357a11d25c9288e1bb006728ddde4d4b6b1`, fixed `739aef2bf7f2c822236bcce0f404c43b57f42503`; initial IPv4-mapped IPv6 loopback request through source-established default runtime/startup/service/guard flow.

At `6eb482c`, each family completes both five-input runs, detects 2/2 vulnerable variants and has zero matching negative alerts. See `v12-exposed-fetchmcp-rules-*`, `v12-exposed-openwebsearch-rules-*` and `v12-exposed-assessment/packet.json`. Full ordered findings equal the intermediate source with assessed diagnostic deltas. Do not redo their original corrections or lose them while fixing SearXNG. Preserve original frozen misses, mutations, controls and source-specific residual uncertainty; exposed regressions do not become fresh evidence again.

## 4. Resolve execution reliability through measured, bounded work

The last full standard Linux sequence is **34435283462**, scanner `7555a9d`: **15/25 development inputs complete; all ten Meta inputs time out at 120 seconds; both 45-input historical batches are correctly skipped**. Completed results include six of ten vulnerable hits and nine of thirteen valid negatives with zero matching alerts; both raw Meta erratum negatives are incomplete. Fifteen completed ordered reports match corresponding local reports except recorded volatile fields. Local development at that scanner completes 22/25, with three Meta operator-fallback timeouts. These results are historical, not measurements of changed scanner `6eb482c`.

Read `v9-linux-assessment/packet.json`, `v9-linux-execution-delta.json`, `v9-final-corpus-assessment/packet.json`, `v10-linux-diagnostic-assessment/packet.json`, `v10-linux-review.md`, `v10-local-performance-disposition.json`, `v11-performance-disposition.json` and raw profiles. Diagnostic run **34446017571** adds four native and two profiled timeouts, not a timing pass. Worker-inclusive profiles identify heavy shared call/expression traversal, merging and Value allocation across SENT-012/015/016. Parent wait time is not total worker cost; host/OS/interpreter differences do not isolate causality.

The last approved local helper-context investigation used one counter profile on `meta-image-ssrf-vulnerable`. SENT-012/015/016 each made about 19,544 helper calls; only 108 repeated the recorded source/context/binding signature, and **every repeat changed bindings**. Mutable side-table contents are additional dependencies. No safe reusable helper result was established; no optimization or unprofiled before/after observation followed. The proposal's stopping condition was reached. See `v11-traversal-profile/`; this is not evidence that all possible optimizations are impossible.

Do not revive rejected work without new causal evidence:

- Credential-copy-skipping `3cbc3295579987d66a8b62c2c0e97adc64437555`, reverted at `62987a6`, completed only 2/6 focused native inputs despite selected test success.
- Failed AST/guard-cache attempts remain preserved with their later correction.
- Duplicate immutable merge canonicalization preserved output but yielded small/inconsistent gains around 2% and was reverted; its useful branch-guard regression remains.
- No blanket helper memoization, unsafe copy skipping, blind cache/worker increase, skipped rules/files, shorter source coverage or deadline extension.

Existing bounded caches, immutable guard snapshots and up-to-four source-flow workers must be understood before edits. Check `static/workers.py`, `path_flow.py`, `typescript_path_flow.py` and all callers. Worker eligibility includes sufficiently large inputs with at least two reported CPUs; do not assume Linux lacked workers.

Prepare the concrete new proposal required by §2 using retained source/profile evidence. After approval, run finite iterations on exact named slow Meta/historical inputs. Retain source/config/input/harness/environment identities, native and end-to-end timings, resource/load observations and worker CPU when available. Avoid overlapping owned heavy work during native measurements. Do not kill unrelated processes or delete unrelated files.

For performance-only changes, compare **entire ordered reports**, including findings and coverage/warnings, excluding only explicitly documented volatile fields. Keep both warning orders if they differ; do not silently sort away differences. Demonstrate repeatable unprofiled native improvement and variability, not just profiler percentages or one favorable run. Retain minimal guard/context/mutation regressions. Revert unsuccessful code while preserving failed measurements and useful tests. Stop at the approved limits or when evidence rules out the approach, then finish unaffected work and present the next concrete choice.

Once a corrected immutable candidate demonstrates improvement, prepare the separate standard Linux verification approval:

1. One full 25-input development batch, followed by historical first only if development passes.
2. One full 45-input historical batch, followed by historical second only if the first passes.
3. One full 45-input historical repeat.

Propose the existing bounds: maximum 115 native input runs, **120 seconds native and end to end per input**, 230 minutes nominal input budget and 240-minute job ceiling, using the established optional job/approval gate and standard runner. Bind the exact candidate, environment, manifests, harness, lock, commands and stopping conditions before requesting approval. Validate workflow/gate inputs before the single approved dispatch. Ordinary CI authorization does not authorize this optional measurement job.

Required pass: development 25/25 complete, ten vulnerable hits, only the two approved raw Meta erratum alerts and zero matching alerts on thirteen valid negatives; historical **45/45 in each whole batch**, twenty vulnerable condition hits and zero matching alerts on twenty-five negatives in each, with full repeat equivalence and adjudicated deltas. Keep the Meta erratum's raw labels/scores and adjusted interpretation separately. It does not waive timeouts. No pooled partial runs, profiled substitutes, retry-until-green, casewise waiver or unapproved runner/gate changes.

## 5. Fresh evaluation after stabilization and remaining measurements

SearXNG is exposed and cannot serve as the fresh holdout for its correction. After **all detector/performance changes stabilize**, freeze the actual scanner before curating new evaluation sources. Use the existing corpus/provenance process and next unused replacement version; preserve v1–v3 and original corpora unchanged. Do not curate or discard candidates based on testing whether the detector passes them.

Prepare an independent repository/source pair, semantics-preserving paired mutations and safe control, with narrow source-grounded conditions/prerequisites, exact revisions, archive/tree hashes, licenses, disclosure of curator/implementation-agent exposure, and a clear distinction from the exposed families. Do not claim independent human review or unseen sources when neither is true. Source review does not authorize target code execution.

Prepare a checkpoint binding actual final scanner, harness, lock, comparator engine/configuration and exact manifest, then ask for **explicit freeze/evaluation approval before any scanner or comparator run on that corpus**. Recommended bounds remain two five-input native runs at 120 seconds/input and one pinned Semgrep 1.176.0 five-input run at 300 seconds/input: 45 minutes nominal input budget, zero paid calls and no target execution. Use existing approval-enforcing `frozen(approval_path=...)`, measurement and scoring tools. Preserve the immutable scanner checkout.

After approval, execute only those runs, validate reports, compare ordered native repeats and source-assess every new unrelated finding/diagnostic. Report misses, false alarms, support/unsupported/incomplete denominators and correlated variants. Process completion is not successful protection. Do not invent a generalization threshold, conceal another fresh miss or accept a limitation for me. Explain its product implication and request a concrete disposition if necessary. If results drive another correction, first record exposure and preserve frozen measurements; a further freeze/evaluation requires its own approval. No endless holdout-replacement loop.

Complete or explicitly prove compatible reuse of the other required final-source measurement scopes: development/controls/mutations, original held-out scope separately, historical repeat pair, all three exposed SSRF families, approved fresh replacement, and affected comparator results. Detector changes do not permit relabeling earlier native outcomes as current. Reuse comparator outcomes only when identical source/input/config/engine/harness bindings support the claim. Plan any additional budgeted native executions concretely and obtain approval where §2 requires it.

Preserve the original held-out baseline: **10 completed, 10 unsupported, five incomplete; zero hits among four completed vulnerable variants out of ten vulnerable inputs total**. Original historical 70-warning unadjudicated backlog is distinct from open-webSearch's 70 source-assessed authentication warnings and assessed SSRF uncertainty. SearXNG's scorer retains 21 unmatched findings per batch—20 prior HTTP candidates and one safe broad URL candidate—with separate source assessments; unmatched scorer keys alone do not establish false positives or an unassessed backlog. Preserve `v12-searxng-scoring-note.json`. No unmeasured competitor superiority or full reviewed accuracy claims.

## 6. Revalidate every Phase 22 technical and engineering requirement

The current audit contains **89 requirements: 69 passed, two explicitly user-deferred, 18 unresolved**. The unresolved IDs are **R18–R27, R35, R63, R64, R65, R66, R84, R88, R89**. R18–R27 remain unresolved because the final whole historical pair has not passed; do not describe them as ten newly established implementation defects. R66/R88 need new fresh evidence after source exposure/change; R89 is SearXNG discrimination; R84 is final human acceptance. R77/R78 are paid-benchmark deferrals.

Read and map every row, not just these 18. Preserve IDs and prior evidence; add any necessary new requirement without renumbering. Reassess affected previously passed requirements against actual final source/test execution. Tests do not substitute for named-condition detection, timing, fresh evidence or human acceptance.

Cover all ten benchmark families and all five compatibility areas in the approved technical plan. Preserve supported Python/static TypeScript, source-established discovery/imports/workspaces/exports/configuration/boundaries, helper/class/factory/client/guard/credential semantics, Helm omissions/strict YAML, SENT-012–016 and Kubernetes SENT-002 meanings, stable rule IDs and canonical Finding/provenance. Keep native schema 1.7.0, 1.3–1.6 migrations, SARIF 2.1.0 and downstream consumers valid. No independent model discovery, new finding origins or stateful exploit expansion.

Preserve candidate-bound review, 160-line total context, omissions/redaction/cache identities, ordered runtime campaigns, attempt IDs, fair scheduling, baseline/prerequisites, observable effects, deadlines/cleanup and explicit unstarted remainder. Unsupported, unknown, incomplete and demonstrated defense remain distinct.

Revalidate the two paid Phase 22 captures against **actual production request construction**, full request hashes/fingerprints, model/settings, reviewer and packaged source/fixture bytes. Retained fingerprints:

- Static TypeScript: `b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f`.
- Runtime: `b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39`.

`v12-production-capture-revalidation/packet.json` regenerated both approved requests and accepted checked replay; four older static demo requests also replayed, six requests total. There were zero new calls. Use the actual ledger/cassettes; never change fingerprints to force reuse. If a request changes incompatibly, prepare the smallest exact paid-capture proposal and ask before calling, while finishing unaffected checks.

Verify Git runtime compatibility by exact source/dependency/image identity. Retained approved image: `sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`; environment packet SHA-256: `a3481db5cfc181de2c0c1a51beca88a332570de00443655016945060394491d7`. `v12-compatible-evidence/packet.json` binds all 13 catalog/campaign/config rows and 19 runtime components. Thirteen campaigns remain **incomplete: 1,040 planned/eligible, 312 tested, 728 remaining, exit 3 and cleanup verified**. Compatible reuse does not establish complete Git coverage or protection. Recheck affected authorized Docker scope without switching to an unapproved environment. The owned demo's 20/20 attempts and 14 findings are a separate narrower result.

Inspect real Makefile/workflows/lock/packaging for final checks. Complete Ruff/format, strict mypy, lock validation, schema drift checks, native JSON/SARIF validation, full pytest with the existing 80% branch-coverage floor, dependency audit/notices, offline generated artifacts, strict docs, wheel/sdist and installed-wheel smoke, fixtures/migrations, Docker/Action and rules-only network isolation. Run supported Linux/macOS/Windows × Python 3.10–3.13 quality/wheel matrix and required Docker/isolation/docs jobs on final code/workflow source. `make check` alone is insufficient. Broaden/repeat checks only for changed source, failures or unresolved concerns.

Preserve the delivered engineering baseline at `6eb482c`:

- Local full suite **2,169 passed, 36 skipped, no xfail**, **89.66% branch coverage**; see `v12-full-suite*` and actual JUnit/coverage files.
- Ruff/format, strict mypy across 146 files, schemas, notices, offline artifacts and strict docs pass; `v12-local-checks.json` and associated command records.
- **CI 34492040679**, **docs 34492040778**: all **29 normal jobs** and docs pass; optional benchmark correctly skipped.
- All 12 hosted quality suites: 2,169 passed / 36 skipped / no xfail, 89.65–89.67% branch coverage. Twelve wheel combinations and Docker/isolation/dependency/hook checks pass.
- **153 wheel and 166 sdist members** compared byte-for-byte against actual final Git blobs. Full logs and 225 uploaded files retained under `v12-hosted-6eb482c/`; audit in `v12-hosted-audit/packet.json`.
- Intermediate `02e8ef7` local run had four socket-permission failures and hosted CI 34485749604 had three dependency-download failures; focused local rechecks and independent final-source checks passed. Preserve actual failed runs; do not relabel them as green.
- Pinned historical reproduction jobs retain their historical scanner and do not establish final-source timing.

Local mock HTTP tests may need sandbox escalation for scanner-owned localhost sockets; owned Docker checks may also need escalation. Such checks do not authorize external model requests. Avoid credentials in commands/logs. Use exact owned labels for cleanup, then verify no owned processes/containers remain.

## 7. Evidence, draft delivery and final phase closure

Preserve numbered evidence seals **1–41** and all directly tracked post-seal records. Latest `evidence-v41.tar.gz` SHA-256 is **`ac47a7684f21db98175ddf5fe909e7a18eef1a5399b10c20431230d597032c91`**: 1,002 files, 103,057,714 raw bytes, 10,920,410 compressed bytes. Every member and all 40 earlier archive hashes were verified after writers stopped.

Follow integration README restoration instructions: restore required versions in numeric order into separate staging, validate archives/members before copying, and require an existing destination to match identical bytes or its recorded previous hash. Stop on unexpected conflicts. Never overwrite a seal. Ignored expanded evidence is not missing/disposable; the large `v12-searxng-assessment/packet.json` is retained in seal 41. Restore it if absent.

`v12-final-documentation-binding.json` supersedes only earlier audit-stage document hashes. `v12-delivery-verification.json` binds documentation delivery and tested-input equivalence. Supplemental remote-readback receipts may be ignored local post-delivery files; distinguish those from tracked/sealed evidence and reverify remote state as needed.

Temporary `/private/tmp/phase22-*.py` helpers were archived with evidence. Inspect before reuse: many hardcode source hashes, worktrees and output names. Reuse established corpus/approval/measurement/scoring tools, not an ad hoc evaluator. `/private/tmp/phase22-check.py` records commands/source/patch/log/helper state but **does not prevent overwriting labels**; always use unique labels. Keep a command wrapper's output name distinct from its produced result packet.

Retain commands/exits/logs, patches and helper sources, source/test/harness/config/input/environment hashes, native resources/timings, full reports and failed attempts, source scoring/adjudication, capture/cost provenance and hosted artifacts. Do not edit raw stored `.patch` evidence to remove unified-diff whitespace; use a scoped product/docs diff check and separately verify captured patch hashes. Check dependent shell operations actually stop on failure. No ambiguous self-referential final commit hashes.

Stop writers before appending the next unused numbered seal (**42 if nothing newer exists**), read back/hash every member, verify prior archive hashes, and update archive/restore indexes. Deliver reproducible evidence in Git/artifacts, not only temporary paths. Preserve superseded drafts and corrected interpretations.

Make reviewable commits on `phase22/integration`; verify actual draft/base/parent before batched push. Update existing draft PR #37 with a current source-bound description and read back head/base/draft/body afterward. Do not create a replacement PR unnecessarily, mark it ready, merge or release. Run required CI on final code/workflow candidate. A subsequent docs/evidence-only commit may use the explicitly permitted CI-skip convention **only after proving code/test/workflow/package inputs equal the tested candidate**; run affected docs checks and never claim a new hosted code pass for that later commit.

Prepare one final acceptance packet mapping **all 89 requirements plus any added requirements** to actual implementation, executed tests, exact evidence and honest disposition: passed, explicitly user-deferred, human-accepted documented limitation, or unresolved. Do not label a new limitation accepted before my decision. Distinguish engineering checks, named-condition detection, execution completion, fresh generalization limitations, runtime proof and external validation.

Reconcile current owning docs while preserving historical claims for their named sources: `AGENTS.md`, `ROADMAP.md`, `ARCHITECTURE.md` where affected, `docs/phase22-technical.md`, implementation status, SSRF follow-up, rules/compatibility docs, integration requirements/progress/README, corpus status and final draft body.

**Phase 22 may be marked complete only when all these conditions hold:**

1. All **three exposed SSRF families** pass their own final native repeat gates: five inputs twice per family, two correlated vulnerable condition hits per batch, zero matching fixed/control alerts, deadlines met, valid source evidence and explained report/coverage deltas.
2. One immutable final candidate passes all 25 development inputs and both entire 45-input historical batches under unchanged native/end-to-end deadlines and condition gates. No pooled observations or unapproved waiver.
3. A new post-stabilization fresh freeze is explicitly approved, its bounded native/comparator evaluation and all source assessments are complete, and actual detection outcomes/limitations are prominent. No silent acceptance of a fresh miss or invented accuracy threshold.
4. Every other authorized Phase 22 technical requirement, final quality/packaging/hosted/Docker/Action check, compatible capture/runtime proof, complete evidence and consolidated draft delivery is finished. No unresolved implementation or execution gate is disguised as an already accepted limitation.
5. I review the concrete final packet and **explicitly accept Phase 22 technical completion and its remaining documented limitations**. This continuation, a corpus/budget approval, “keep going,” or green CI is not that acceptance.

When conditions 1–4 hold, ask for final acceptance with the concrete packet, exact scanner/delivery identities, results and remaining documented limitations. **After I accept, continue in this same conversation**: record my exact decision and identities in a versioned receipt; update Phase 22 status/checklists and owning docs/audit/evidence to complete under the revised scope; validate the final documentation changes; seal new evidence where required; commit/push to the same draft and verify remote delivery. Preserve paid/pilot deferrals, incomplete Phase 21 and unchanged Phase 24/15 gates. Acceptance does not authorize merge/release/outreach or Phase 23.

If a gate fails, preserve/deliver the completed work and finish independent authorized requirements before presenting the concrete remaining choice. Do not request final acceptance with known implementation/timing gates unmet. Any proposed scope revision must show the unchanged failed gate and exact proposed change and requires my explicit decision; do not apply a waiver on my behalf. Continue with me through subsequent approvals instead of handing off again or treating compaction as a restart.

Start with a brief plan and verified baseline. Answer status questions candidly, then resume authorized work unless I cancel it. The objective is an honestly completed and accepted Phase 22, with all evidence and final documentation delivered—not merely another partial investigation or green test report.
