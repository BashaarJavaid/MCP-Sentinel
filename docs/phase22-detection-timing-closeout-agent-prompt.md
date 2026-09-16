# Phase 22 continuation: fix fresh-case detection and execution reliability, then close out

Execute this complete authorized continuation for **PortunusMCP Sentinel**. Verify current state before editing. Investigate and fix both the fetch-mcp SSRF detection miss and native benchmark timing failures, preserve the already working open-webSearch correction, then finish all remaining Phase 22 verification, evidence, documentation and consolidated draft delivery. Continue with me through final technical acceptance and its subsequent documentation update if the gates pass. Do the work, not just a plan or another handoff.

Preserve existing implementation, tests, source archives, approvals, original measurements, failures and sealed evidence. Ask only for genuinely missing decisions or the explicit checkpoints below. **No additional paid model calls without my approval.** Do not silently narrow this task to timing or treat a completed scan with no detection as successful protection.

## 1. Authority, conventions and verified baseline

Read applicable `AGENTS.md` and coding skills; apply the active Ponytail/minimal-change conventions. Read `mcp-sentinel-buildplan.md` first for historical context and non-goals, then use `ARCHITECTURE.md`, `ROADMAP.md` and `docs/phase22-technical.md` as current authority. Follow supported Python/TypeScript boundaries, canonical report models and the existing CLI/pipeline. No new frameworks, speculative abstractions, dependencies or languages merely to avoid understanding the existing implementation. Trace every affected caller, reproduce security failures in durable minimal tests before fixing them, and check relevant sibling paths.

Read these records, resolving historical status statements against later evidence and this instruction:

- `artifacts/phase22/integration/next-agent-handoff-20260908-v2.md`, especially its complete technical scope and sections 9–17. Its old source identities and unfinished-work statements are historical, not instructions to redo finished work.
- `docs/phase22-final-agent-prompt.md`, the preceding continuation. Its open-webSearch miss was subsequently fixed; fetch-mcp and current timing results below supersede that starting state.
- `artifacts/phase22/integration/requirements.md`: all 86 rows, not just the unresolved ones.
- Integration `README.md`, latest `progress.md` entries, and `v8-closeout-audit/packet.json`.
- `docs/phase22-implementation-status.md` and `docs/phase22-ssrf-follow-up.md`.
- `artifacts/phase22/completion-scope-v1/decision.json` and `follow-up-proposal.json`.
- Replacement-v1 exposure authorization; replacement-v2 manifest, checkpoint, authorization, source review and completed v8 assessments.
- `v8-linux-execution-authorization.json`, `v8-linux-assessment/packet.json`, `v8-linux-execution-delta.json` and `v8-next-performance-proposal.json` under integration.

Verified when this prompt was prepared:

| Item | Identity / state |
| --- | --- |
| Active worktree | `/private/tmp/mcp-phase22-options`, branch `phase22/integration` |
| Delivered HEAD / draft PR #37 head | `c177e0cc0d5d2d66e0b915d31ce7533271f13eba` |
| Frozen measured scanner | `62987a6c519f04e443fe3c305644e24b8d128773` |
| Identical detector bytes | `e87b7c9012179178c16ee88072d9851c1d30adaa` |
| Tested workflow delivery | `88a559ec9b5c3799618d95df811f489a61283996` |
| Scanner source SHA-256 | `e3664615dedfabd629fbbb6998aecdd9afe393db7f35bd8506f1e0979ecf716f` |
| Measurement harness SHA-256 | `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add` |
| Lock SHA-256 | `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b` |
| Separate main worktree | `/Users/bashaarjavaid/Projects/MCP-Sentinel`, clean at `4cd57593b2585b9ee05c0f175930e6a0d76d362a`, branch `phase22/python-containment` |
| Existing draft | https://github.com/BashaarJavaid/MCP-Sentinel/pull/37 |
| Draft base / PR #36 head | `phase22/description-poisoning`, `8b6b0ddf1d6f6cf5a8da3ab9421471865b801455` |

`c177e0c` is documentation/evidence delivery, not a new hosted code pass. `88a559e` adds the approved optional workflow without changing scanner/test/package inputs. Reverify actual Git status, branches, ancestry, remote PR metadata, worktrees, ignored evidence and active processes before editing. Preserve later user/agent changes. The previous prompt is intentionally untracked; this new prompt may also be untracked. Do not indiscriminately add or delete user instructions.

Use the existing locked environment `/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv`, verifying versions and putting its executables first on PATH. Explicitly use the active worktree's imports (`PYTHONPATH=src:.` as appropriate). Local measurements used Python 3.12.13; the latest Linux job used Python 3.12.14. Semgrep is pinned to 1.176.0 and the approved Git environment uses mcp 1.29.0. Preserve all detached/increment worktrees, including `/private/tmp/mcp-phase22-frozen-62987a6`; do not implement inside that frozen checkout or accidentally import the main checkout's editable source.

## 2. What this continuation authorizes and what remains gated

When I give you this prompt to execute, it authorizes the complete investigation and correction of **both** problems, regression tests, measured performance work, bounded offline measurements on the already exposed/development corpora, necessary engineering checks, evidence/docs, local commits and batched delivery to existing draft PR #37. Do not ask again for ordinary reversible work inside that scope.

In particular:

1. **fetch-mcp exposure and fix are now authorized by this continuation.** Before tuning, append a versioned exposure-and-fix decision identifying this instruction, the exact replacement-v2 manifest/checkpoint and frozen results. Preserve the old `detector_tuning_approved: false` authorization and all first measurements unchanged. Those old values describe the earlier evaluation approval; do not edit them to pretend it authorized this later work. Classify the five fetch-mcp cases as exposed regressions for subsequent fixes.
2. This complete continuation supersedes the **unapproved, performance-only** `v8-next-performance-proposal.json` as the requested work plan. Preserve that proposal as historical. Do not stop at its one-optimization/eight-scan/two-profile limit instead of completing the broader authorized task; equally, do not use this scope as permission for endless retries.
3. The earlier Linux dispatch approval was consumed by run 34421737148. This continuation separately authorizes preparing and executing **one new final standard Linux verification sequence** on the corrected immutable candidate: one 25-input development batch, then a 45-input historical batch only if development passes, then the second 45-input batch only if the first passes. Maximum 115 native input runs, 120 seconds native and end to end per input, 230 minutes nominal input budget, 240-minute job ceiling. Reuse the existing optional CI job and gate infrastructure, version its new source/approval bindings, validate it before dispatch, and record this new authorization separately. Do not redispatch the old frozen job and present it as a new candidate measurement. No paid/larger/self-hosted runner procurement is authorized.
4. Necessary normal CI/quality/packaging/Docker replay checks and their ordinary hosted matrix are authorized. Batch delivery rather than pushing each experiment. Do not suppress CI for code or workflow changes.

The remaining explicit checkpoints are:

- A **new fresh replacement corpus freeze**: exact new manifest, stabilized scanner, source-exposure disclosure and bounded offline evaluation must be prepared and approved before evaluating that new corpus.
- Any **new paid model calls**: exact named requests, purpose, maximum cost and stopping conditions must be approved first.
- A **different tested Git SDK/runtime environment** or paid execution resources, if actually necessary.
- Any further full benchmark retry, runner change or gate exception after the newly authorized final sequence fails: finish the unaffected work and present the measured problem and concrete options first.
- **Final human Phase 22 technical acceptance**, only when its concrete final packet is ready and the technical gates below pass.

The 396-request paid benchmark and external maintainer pilots remain explicitly user-deferred and nonblocking for Phase 22; neither counts as passed. Phase 21 remains incomplete, and Phase 24 adoption/retention and Phase 15 launch gates are unchanged. The two original accepted paid requests cost $0.071799 total; that approval is spent. Reuse compatible captures offline. `--allow-degraded` does not prevent model calls when credentials are present. Do not run `make artifacts-live` or expose credentials in evidence.

The approved Meta fixed-label erratum remains authoritative. Preserve original labels, raw scores and the separate erratum-adjusted interpretation. It does not waive timeouts. Earlier residual-SSRF and pooled/casewise timing waivers were never approved; do not infer acceptance of them.

No merge, release, publication, outreach, telemetry, automatic rule promotion or next phase. Static analysis must never import/execute target code, run upstream tests/builds, install target dependencies, render Helm or follow repository escapes/symlinks. Runtime targets run only in Sentinel-controlled Docker under the accepted isolation contract. Source curation and dependency-source review are read-only; no production endpoints or host target execution. Preserve candidate-bound review, canonical Finding/provenance, stable rule IDs, native schema 1.7.0 and 1.3–1.6 migrations, SARIF 2.1.0 and explicit unknown/unsupported/incomplete states. No independent model discovery or stateful exploit expansion.

## 3. Correct the fresh-case detection failure first

**This is a product-relevant detection failure, not merely a completed benchmark with a documented footnote.** Sentinel's purpose is to catch security regressions before release. Passing engineering tests or the exposed open-webSearch pair does not demonstrate that it catches this different implementation. Timing work alone does not solve the user's concern.

The formerly fresh fetch-mcp evaluation at frozen `62987a6` is complete:

- Manifest: `artifacts/phase22/corpus-replacement-v2/manifest.json`; SHA-256 `a587427f0c40cbff512f00c8024e454a11255e34a13c10f9d8748bbc4aa9bae2`.
- Approval: `corpus-replacement-v2/authorization-62987a6.json`; checkpoint: `checkpoint-62987a6.json`.
- Native runs: integration `v8-fresh-rules-first/` and `v8-fresh-rules-repeat/`.
- Comparator: `v8-fresh-semgrep-first/`; assessment: `v8-fresh-assessment/packet.json`; deadline proof: `v8-fresh-completion.json`.
- All five inputs completed in each run. Both native runs and Semgrep missed both correlated vulnerable variants; zero condition-matched alerts on two fixed variants and one safe control.
- Native maximum wall times: 5.771s and 5.075s; Semgrep: 16.374s. Entire native reports match across repeats except documented volatile fields.
- Native findings are empty. Each report retains one unresolved low-level tool handler and unresolved schema/class/method flows. A completed scan is not completed semantic coverage or evidence of protection.
- All 50 comparator JQuery alerts are source-assessed false positives for that stated rule: they match calls to the locally imported `Fetcher.html`, not a JQuery DOM sink. Preserve raw outputs and assessments; they are not SSRF hits or evidence of comparative superiority.

Source pair: `zcaceres/fetch-mcp`, vulnerable parent `9fd840d575e68a37f72f07b8f4d2c77f87698c36`, fixed child `e7659f8cca26ce051b65f5bc28418df155812b8e`. Both declare package version 1.0.2. The fixed label is source-specific; do not call it a generally patched package release. Verify the retained advisory, source archives, reversible helper-renaming mutations and `review/condition-review.json` before changing the detector.

The precise condition is a caller-supplied `http://127.0.0.1/` passed to registered `fetch_html` in the upstream stdio server under ordinary defaults reaching the **initial outbound fetch**. The vulnerable source passes the entire URL string to `private-ip`; the source fix parses the URL and passes its hostname, rejecting private IPs before fetch. Retained private-ip 3.0.2 source supports the narrow labels. DNS/rebinding, redirects, IPv6, proxies, response parsing, remote availability and successful exfiltration are outside this condition.

Trace the production discovery and analysis chain end to end:

`Server.setRequestHandler(CallToolRequestSchema, callback)` → `request.params.arguments` → imported `RequestPayloadSchema.parse(args)` → `request.params.name === "fetch_html"` dispatch → imported `Fetcher.html(validatedArgs)` → static receiver `this._fetch` → private static helper with destructured RequestPayload → URL/IP guard → native `fetch(url, ...)`.

Observed boundaries to investigate, not assumptions about a finished fix:

- `src/index.ts:139–161`: unresolved low-level tool dispatch; schema parsing is at line 142 and the html call at line 145.
- `src/Fetcher.ts:6`: the class is reported as unsupported; it has private static helpers and static methods.
- `Fetcher.html/json/txt/markdown` calls remain unresolved. Trace import identity, static member binding, `this`, private members and the actual return-value/argument flow rather than adding name-based exemptions.
- The schema is imported from `src/types.ts`; its `.parse` method must be understood only where a genuine source-bound supported schema establishes that operation. Arbitrary methods named `parse` are not automatically validators or identity functions.

Inspect existing TypeScript discovery, registration, module and path-flow code, all callers/rules and current tests. The code already supports legacy registrations, object methods, factory captures, receiver identities, literal startup imports, optional default dependencies and literal-IP guard classification. Extend the smallest shared root and preserve those fixes. Check SDK/schema spoofing, aliases/re-exports, static versus instance receivers, shadowed/replaced methods, bound or detached calls, relevant inheritance/visibility cases, private/static helper renames, caller taint, ignored validation results and guards on unrelated/replaced values. Keep unsupported cases explicitly unresolved; do not hide them by changing coverage labels or disabling expensive analysis.

Create durable minimal failing reproductions before security fixes. Include vulnerable/fixed and effective/ineffective guard controls. Exercise relevant supported Python siblings when shared contracts change. No case-ID/repository special cases, hardcoded attack-URL rule or broad flagging of both revisions. Diagnostics with evaluator-supplied bindings are not native detections.

**Required correction gate:** on the final implementation, all five fetch-mcp inputs complete twice through the unchanged normal rules-only pipeline, under 120 seconds native and end to end per input; both vulnerable variants produce source-grounded SENT-015 condition matches; both fixed variants and the safe control have zero matching alerts. Validate canonical locations/provenance/native JSON/SARIF and assess every changed unrelated finding or coverage diagnostic. These become exposed regression results; preserve the original frozen 0/2 results unchanged.

Also preserve the existing open-webSearch gate: integration `v7-final-replacement-rules-first/` and `v7-final-replacement-rules-repeat/` previously completed 5/5 each, detected 2/2 correlated variants and had zero matching negative alerts. Its source pair is vulnerable `e29b2357a11d25c9288e1bb006728ddde4d4b6b1` versus fixed `739aef2bf7f2c822236bcce0f404c43b57f42503`; condition is the initial request for an IPv4-mapped IPv6 loopback URL through the default full runtime. Preserve its source-established startup/default-service/guard chain and original 0/2 evidence. Recheck both exposed five-input families twice on final source; neither substitutes for new fresh evidence.

## 4. Fix native execution reliability through measured work

Current failures are retained, not explained away by a presumed noisy host:

- Same-detector local historical attempt `v5-final-historical-rules-first`: 43/45 complete, all 20 vulnerable conditions detected, zero matching alerts on 23 completed negatives. Both fixed-upload variants time out; a natively completed fixed-authentication mutation takes 123.156s end to end. The required two-whole-batch gate failed.
- Final local development `v7-final-development-rules-first`: 24/25 complete. `meta-operator-fallback-fixed-mutation` times out at 120.063s. Ten vulnerable hits and 13 valid negatives retain expected results; the approved Meta erratum does not resolve the missing execution.
- Approved Linux run **34421737148**, scanner `62987a6`, four reported CPUs, Python 3.12.14: **17/25 development inputs complete, eight time out** at about 120 seconds. Both historical batches were correctly skipped. No retry was run.
- The eight Linux timeouts are all five `meta-image-ssrf-*` inputs plus `meta-operator-fallback-fixed`, `meta-operator-fallback-fixed-mutation`, and `meta-operator-fallback-safe`. Seven are new versus the local final run; one persists.
- Linux completes/detects eight of ten vulnerable inputs; nine of thirteen valid negatives complete without matching alerts. Both raw Meta erratum negatives are incomplete, leaving nine completed of fifteen raw negatives. Zero raw alerts is not a scoring improvement.
- All 17 completed Linux reports equal their prior entire ordered reports except documented volatile fields. The result establishes execution failure, not a newly observed finding/coverage change. Linux/macOS, CPU and interpreter differences do not isolate a causal variable.

Read `v8-linux-assessment/packet.json`, `v8-linux-execution-delta.json`, and retained raw artifacts under `v8-hosted-88a559e/artifacts/linux/phase22-final-historical/`. Review older full failures, source-bound report comparisons and profiles before repeating work.

Existing optimizations include bounded identity/combination/location caches, Python guard-marker name indexes reading current branch values, TypeScript reuse of unchanged branch values, and up to four source-flow workers for sufficiently large inputs. Inspect `static/workers.py`, `path_flow.py`, `typescript_path_flow.py` and their callers. The frozen worker code enables its path at at least two reported CPUs and sufficient source size; do not assume the Linux job lacked workers merely because it had fewer CPUs than the desktop.

Preserve the failed credential-copy-skipping experiment `3cbc3295579987d66a8b62c2c0e97adc64437555`: only 2/6 focused native inputs completed, despite passing selected tests. It was reverted at `62987a6`, retaining its regression tests and failures. Do not revive it or discard those tests without new evidence. Retained e87 native profiling attributes substantial worker CPU/traversal to SENT-016, SENT-015 and SENT-012; parent wait time is not total analysis cost. Use the actual profile packets and commands, not copied headline numbers, when choosing a change.

Work in finite, recorded iterations:

1. After the detection correction, select the actually slow exposed Meta and historical inputs. Record a bounded input/run/profile plan before each iteration. Reuse compatible profiles and earlier baselines where valid; avoid rerunning whole corpora during exploration.
2. Measure normal native execution without overlapping agent-owned heavy work. Retain scanner/config/input/harness/environment identities, native duration, end-to-end wall time, CPU/memory/disk/load and worker-inclusive CPU where available. Disclose shared-host limits; do not kill unrelated processes or delete unrelated files.
3. Profile actual expensive paths, distinguish traversal from startup/resource wait, and remove demonstrated repeated work with existing structures or stdlib. Preserve source/context/branch identity, mutation/guard semantics, deadlines, worker cleanup and ordered output. Do not blindly increase workers/cache limits, remove rules or exclude relevant files.
4. Keep durable guard/context regressions. For performance-only changes, compare **entire ordered native reports**, excluding only the recorded volatile run IDs/clocks. Retain both warning orders if order alone varies; do not silently sort away unexplained deltas. Demonstrate actual native improvement without profiler overhead and report variability, not just one favorable sample.
5. Revert unsuccessful optimization code while retaining evidence and useful regressions. Do not pool successes from failed batches or describe partial/component timing as the full gate.

On one immutable corrected candidate, execute the newly authorized final development → historical first → historical second sequence from §2. All 25 development inputs must complete under both deadlines; require ten vulnerable condition hits, only the two approved raw Meta erratum alerts and zero matching alerts on thirteen valid negatives. Both entire 45-input historical batches must complete under both deadlines, each with all twenty vulnerable condition hits and zero matching alerts on all twenty-five fixed/safe inputs. Verify full repeat equivalence and adjudicate new deltas. No deadline extension, scope truncation, profiled substitute, retry-until-green or pooled alternative.

If bounded investigation cannot establish improvement or that final sequence fails, retain the result, finish independent authorized work, explain the actual bottleneck and remaining choices, and ask for the genuine next decision. Do not request final acceptance or mark Phase 22 complete with this gate unmet.

## 5. New fresh corpus and complete measurements

fetch-mcp is now being used to guide a correction and cannot remain the fresh holdout for that correction. Prepare the next versioned replacement proposal through the existing corpus/provenance process. Preserve all previous manifests, source archives, approvals, curation disclosures and results.

Stabilize and freeze the detector **before** curating new evaluation sources. Select an appropriate independent repository/source pair, paired semantics-preserving mutations and a safe control with explicit narrow conditions, prerequisites, licenses, exact revisions/archive/tree hashes and source-grounded labels. Keep unchanged original corpus records unchanged. Explain what the new condition can and cannot test, its distinction from the exposed examples, and any source exposure by the curator or implementation agent. Do not claim independent human or unseen-source review that did not occur. Do not choose or discard cases based on trying the detector and seeing which ones pass.

Prepare a concrete checkpoint binding the actual final scanner, harness, lock, comparator/configuration and manifest. Request explicit freeze/evaluation approval **before any new-corpus scanner/comparator run**. Recommended bounded scope remains two native five-input runs at 120 seconds/input and one pinned Semgrep 1.176.0 five-input run at 300 seconds/input, zero paid calls and no target execution. Use the existing approval-enforcing `frozen(approval_path=...)`, measurement/scoring and comparator infrastructure. Preserve the immutable scanner checkout and exact recorded identities; do not fabricate approval or relabel old measurements as new-source results.

After approval, execute only the bounded runs and report all misses, false alarms, unsupported/incomplete inputs, correlated variants and support/completion denominators. Adjudicate every new unrelated finding and coverage diagnostic against source. **Do not describe the new fresh evaluation as successful protection merely because the process completed.** A fresh miss is a substantive limitation to explain, especially if it repeats the boundary supposedly corrected. Do not invent an overall accuracy threshold or silently accept that limitation on my behalf. If results inform another correction, mark exposure, preserve the frozen results and follow a new freeze process; do not tune secretly or keep replacing holdouts until one looks good.

Complete the other required measurements on final source: original development and its controls/mutations, original held-out scope separately, historical pair, both exposed SSRF families and the newly approved fresh replacements. Reuse unaffected measurements only with explicit input/configuration/engine/harness/source compatibility proof appropriate to the claim. Changes to the detector do not automatically permit relabeling prior native outcomes. Reuse pinned comparator results for identical unchanged inputs/config/engine/harness when verified; rerun affected scopes. No Snyk/Cisco or broader superiority claims without measurements.

Retain the original held-out baseline: ten completed, ten unsupported, five incomplete; zero hits among four completed vulnerable variants, out of ten vulnerable inputs total. These limitations do not vanish when exposed pairs improve. Preserve the original historical **70-warning unadjudicated backlog**, which is distinct from open-webSearch's **70 source-assessed authentication warnings** and its other assessed SSRF warnings. Unmatched named-condition scorer keys are not automatically either false positives or a new unassessed security backlog; retain their actual source judgments and uncertainty. Keep raw Meta scores and erratum-adjusted interpretation separate.

## 6. Complete all Phase 22 engineering and runtime requirements

Use all 86 existing rows and the original full handoff, not only the latest unresolved list. The v8 audit recorded 78 passed, two user-deferred and six unresolved (R20, R35, R63, R64, R65, R84). Its R66/R68 pass means the bounded fresh **measurement** was completed; it does not establish a fetch-mcp detection correction. Add an explicit fetch-mcp correction gate and next-fresh-corpus requirement to the new audit without renumbering or losing any existing requirement. Reassess affected previously passed rows after implementation changes.

Cover all ten benchmark families and five compatibility areas in the authorized technical plan. Preserve SENT-012–016 and Kubernetes SENT-002 contracts, Python/TypeScript discovery and shared flow, workspace membership/exports/configuration/boundaries, Helm omissions/strict YAML, source-established guards and caller taint, candidate-bound review, native schemas/consumers/migrations and ordered runtime campaigns. Preserve the 160-line total review context, omission/redaction/cache identities, runtime attempt IDs, fair scheduling, baseline prerequisites, observed effects, budget/cleanup behavior and honest unstarted remainder.

Revalidate the two approved captures against **actual current production request construction**, fingerprints, request hashes, model/settings, reviewer behavior and packaged source/fixture bytes. Retained fingerprints:

- TypeScript: `b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f`.
- Runtime: `b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39`.

Use the ledger and compatible replay, not an unapproved live call. Never edit cassette fingerprints to force reuse. If a changed request genuinely needs a new capture, prepare the smallest concrete named request/budget/stopping packet and ask first; continue unaffected checks.

Verify the approved Git runtime environment and evidence by exact source/dependency/image identity. Its retained image is `sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`; tested environment packet SHA-256 `a3481db5cfc181de2c0c1a51beca88a332570de00443655016945060394491d7`. Current compatible evidence has thirteen incomplete campaigns: 1,040 planned/eligible, 312 tested, 728 remaining, all exit 3 with cleanup verified. Do not claim completed Git coverage or defense. Reuse only after proving compatibility; rerun affected authorized Docker checks without adopting an unapproved environment. The retained current Docker replay demo completed 20/20 attempts with 14 findings and no remainder; preserve its narrower claim.

Inspect the real Makefile, lock, packaging and workflows. Required final checks include Ruff/format, strict mypy, lock validation, generated schemas, native JSON and SARIF 2.1.0 validation, the full pytest suite with the existing 80% branch-coverage floor, dependency audit/notices, generated artifacts in offline check mode, strict docs, wheel/sdist and installed-wheel smoke, supported fixtures/migrations, Docker/Action and rules-only network isolation. Run the supported Linux/macOS/Windows × Python 3.10–3.13 hosted quality/wheel matrix and required Docker/isolation/docs jobs on the final code candidate. `make check` alone is insufficient. Run relevant checks after fixes; broaden or repeat only for actual changes/failures/remaining concerns.

Current baseline, to preserve rather than misattribute after edits:

- Scanner `62987a6`: local 2,121 passed, 36 skipped, 89.64% branch coverage.
- Workflow delivery `88a559e`: normal CI **34421722233**, docs **34421722204**; all twenty-nine normal jobs and docs passed. The optional benchmark is correctly skipped in ordinary CI.
- Twelve hosted quality suites each: 2,121 passed, 36 skipped, 89.63–89.65% branch coverage.
- `v8-hosted-88a559e/packet.json` retains full logs and 287 uploaded artifact files, including the separately failed Linux benchmark. `v8-current-hosted-audit/packet.json` verifies 153 wheel and 166 sdist source/schema/fixture/capture members against Git blobs.
- Pinned historical reproduction jobs each report 32 completed/13 incomplete **on their historical scanner**. They are not current integration timing-gate passes.

## 7. Evidence, delivery, acceptance and finishing with this agent

Evidence batches **1–37** are preserved. Batch 37 is `artifacts/phase22/integration/evidence-v37.tar.gz`, SHA-256 `93f938ce36d3b32e44601f2e8b183cd0f5adbea9e39f4fa4af53311050a713b6`; its manifest records 407 files, 25,706,836 raw bytes and 4,530,755 compressed bytes. Every member and every prior numbered archive hash was verified. Follow the existing restoration instructions: restore needed versions in numeric order to separate staging, validate archives and members before copying, and require an existing destination to match identical bytes or its recorded prior hash. Stop on unexpected conflicts. Never overwrite a seal.

Expanded evidence is often ignored by Git. Do not assume it is missing or disposable. Temporary `/private/tmp/phase22-*.py` helpers may still exist and are archived under diagnostics, but many hardcode old worktrees, HEADs or output names. Inspect before reuse. Reuse existing corpus/measurement/scoring/approval tools; do not bypass provenance with an ad hoc harness. Command wrappers write their own metadata: use unique labels and never give a result packet the wrapper's output filename. Keep all failed commands, partial reports, invalid experiments and their corrected follow-ups.

Make reviewable commits on the integration branch. Verify PR #37 remains a draft with the actual base/parent before batched delivery. Preserve old drafts; no merge/release. Run required hosted checks on the integrated code/workflow candidate. A later docs/evidence-only commit may use the repository's permitted CI-skip convention only after proving relevant code/test/workflow/package inputs equal the tested commit; never claim a new hosted pass for that docs commit.

Retain commands/exits/logs, patches and relevant helper sources, code/test/source/harness/config/input/environment hashes, native timing/resource observations, all reports and failures, scoring/source adjudication, capture/cost provenance and complete hosted logs/artifacts. Verify distributions contain actual final bytes. Stop writers before appending numbered evidence batches starting at the next unused version (38 if nothing newer exists), hash and read back every member, and verify previous archive hashes. Deliver reproducible evidence in the repository/artifacts, not only temporary directories. Keep restore instructions and archive index current.

Prepare one source-bound final acceptance packet mapping every original requirement plus this continuation's fetch-mcp correction and new-fresh-evaluation gates to implementation, executed tests, exact evidence and disposition: passed, explicitly user-deferred, accepted documented limitation, or unresolved. Do not mark a new limitation human-accepted before I accept it. Distinguish engineering passes, named-condition detection, execution completion, fresh generalization limits and runtime proof. Reconcile current owning docs while preserving historical claims for their named sources: `AGENTS.md`, `ROADMAP.md`, `docs/phase22-technical.md`, implementation status, SSRF follow-up, applicable architecture/rule/compatibility docs, and integration requirements/progress/README.

**Phase 22 may be marked complete only when all of the following hold:**

1. Both exposed SSRF families—including the newly exposed fetch-mcp miss—pass their separate final native repeat gates: 5/5 complete per run, 2/2 correlated vulnerable condition hits per family, zero matching fixed/control alerts, valid source evidence and explained deltas.
2. All 25 original development inputs and both entire 45-input historical batches pass unchanged native/end-to-end deadline, completion and condition gates on one immutable corrected candidate. No pooled observations or unapproved waiver.
3. The next fresh freeze is explicitly approved and its bounded evaluation and source assessments are complete. Its actual detection results and remaining uncertainty are prominent, not concealed behind a process-completion pass. Original held-out limitations, prior misses and source exposure remain visible.
4. Every other authorized Phase 22 technical requirement, final quality/packaging/Docker/Action/hosted check, compatible capture/runtime proof, reproducible evidence and consolidated draft delivery is finished. No unresolved implementation or execution requirement is disguised as a TODO or a limitation I have already accepted.
5. I review the concrete final packet and **explicitly accept Phase 22 technical completion and the remaining documented limitations**. Ask for this acceptance only when the packet is ready. Neither this prompt, permission to continue, approval of a corpus/runner, nor green CI constitutes final acceptance.

After I accept, continue in this same conversation: record the exact user decision and final identities, mark Phase 22 complete under the revised scope, update the owning docs/audit/evidence, verify the final documentation change and deliver it to the same draft. Keep the deferred paid benchmark, incomplete Phase 21 and unchanged Phase 24/15 gates visible. Completion does not authorize merge, release, outreach or Phase 23.

If a necessary gate remains unmet, state exactly what failed, preserve and deliver the completed work, finish all independent authorized requirements, and present the concrete genuinely missing decision. If a new fresh case misses, do not claim reliable protection or infer my acceptance; explain the gap and its implication before requesting any disposition. Do not silently expand into an endless holdout-replacement loop.

Start with a brief plan and verified baseline. Keep progress updates concise and focused on material findings. Answer status/product questions candidly and continue the active task unless I cancel it. If context compacts, continue from retained state rather than restart; if I continue with you through approvals, finish the corresponding authorized work and closeout instead of unnecessarily handing it to yet another agent.
