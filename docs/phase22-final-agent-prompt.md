# Phase 22 final continuation: SSRF correctness, timing, and completion

Execute this complete authorized continuation for PortunusMCP Sentinel. Start by verifying current state. Fix the exposed 0/2 SSRF detection gap, then improve benchmark reliability through measurement and targeted optimization, then finish all remaining Phase 22 verification and prepare final technical acceptance. Do the work, not merely a plan. Preserve all existing implementation, evidence, failures, source archives and approvals. Ask only for genuinely missing decisions or explicit approval checkpoints. No new paid model calls without my explicit approval.

## 1. Authority, conventions, and verified starting point

Read applicable AGENTS.md and coding skills. Read `mcp-sentinel-buildplan.md` first for historical context/non-goals, then use `ARCHITECTURE.md`, `ROADMAP.md`, and `docs/phase22-technical.md` for active contracts. Apply the project conventions and minimal shared-root fixes; do not create new frameworks, dependencies, languages, or speculative abstractions. Keep durable failing reproductions before security fixes, and verify relevant Python and TypeScript sibling paths.

Read these continuation records in full, resolving historical status statements against newer source-bound evidence and explicit user decisions:

- `artifacts/phase22/integration/next-agent-handoff-20260908-v2.md`: full original authorized technical scope, conventions, reproduction and final gates. Its old outstanding-work statements are historical, not instructions to redo finished work.
- `artifacts/phase22/integration/requirements.md`: all 86 requirement rows; audit every row, not just the two issues below.
- `artifacts/phase22/integration/README.md` and the latest sections of `progress.md`.
- `docs/phase22-ssrf-follow-up.md`, `docs/phase22-implementation-status.md`.
- `artifacts/phase22/completion-scope-v1/decision.json` and `follow-up-proposal.json`.
- `artifacts/phase22/corpus-replacement-v1/exposure-and-fix-authorization.json` and the replacement-v2 approval metadata. Keep fresh source out of tuning.

Verified when this prompt was prepared:

- Active worktree: `/private/tmp/mcp-phase22-options`, clean branch `phase22/integration`, HEAD `c2d15773c5ff66bc9d3b7d402f7547c5ad5e3c3b`, tracking origin.
- Current implementation commit: `68bdf83ca35670946c850595f3a2a11eadee2a4a`. `c2d1577` adds documentation/evidence with identical implementation/package inputs; it is not a new CI pass.
- Main worktree `/Users/bashaarjavaid/Projects/MCP-Sentinel` is separately clean at `4cd57593b2585b9ee05c0f175930e6a0d76d362a`, branch `phase22/python-containment`. Preserve it and all existing detached/increment worktrees. Work on the integration branch; do not reset, clean, switch or overwrite someone else's work.
- Existing consolidated DRAFT PR: https://github.com/BashaarJavaid/MCP-Sentinel/pull/37, head `phase22/integration`, base `phase22/description-poisoning` (PR #36), parent `8b6b0ddf1d6f6cf5a8da3ab9421471865b801455`. Verify actual ancestry and remote metadata before delivery.
- Locked environment has been `/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv`; verify lock/environment identities and explicitly use this worktree's imports (`PYTHONPATH=src:.` where appropriate). Do not accidentally test the main checkout's editable source or create an unrelated environment.

Use `git status`, worktree/branch/source identities, actual processes and evidence manifests before editing. Do not assume old temporary scripts or materialized sources still exist. The integration evidence is committed and pushed, not solely in temporary directories. Batches 1–32 are retained. Batch 32 SHA-256 is `de862c63dbb10c8c3d27a1ceee93538f015808c6b4ba47fbb307eb7001c9eed4`; its manifest describes 1,139 files. Verify manifests and restore missing evidence into a separate staging directory in recorded order, checking existing-file conflicts before copying anything. Never overwrite a sealed archive. Preserve all earlier archive hashes.

## 2. User decisions and hard boundaries

This continuation authorizes investigation, code fixes, offline regressions/benchmarks on already approved exposed/development inputs, necessary local quality checks, evidence/docs, reviewable commits, and batched delivery to the existing draft under the original delivery workflow.

- The 396-request paid benchmark is deferred for cost and does not block Phase 22. Do not execute it or count it as passed.
- External maintainer pilots are deferred and explicitly do not block Phase 22. Phase 21 remains incomplete; Phase 24 adoption/retention and Phase 15 launch gates are unchanged. Do not claim external validation.
- Only the earlier TypeScript smoke and Docker demo paid captures were approved and executed: two accepted requests, total $0.071799. That approval is spent, not continuing authority for further calls. Reuse compatible evidence offline. `--allow-degraded` does not prevent calls when a key exists; inspect runners and use explicit offline paths. Do not run `make artifacts-live`.
- The approved Meta label erratum remains authoritative in `meta-fixed-label-erratum-v1`. Preserve raw labels, scores and the documented narrower interpretation; do not silently relabel cases or reopen this settled decision.
- `follow-up-proposal.json` proposed accepting the residual SSRF miss and alternative per-input timing evidence. Neither exception was approved. The instruction now is to fix both problems and meet the original timing gate, not infer acceptance of either exception.
- Fresh replacement corpus freeze and final human technical acceptance remain explicit checkpoints. This prompt does not preapprove either. Prepare a concrete packet before asking; continue independent authorized work while awaiting a decision.
- No merge, release, publication, outreach or additional paid calls. No new tested Git environment adoption without its required approval. Reuse the approved Git `mcp==1.29.0` environment and exact retained image/dependency identities.
- Static analysis must never import/execute target code, run upstream tests/build scripts, render Helm, or follow repository escapes/symlinks. Dynamic targets run only in Sentinel-controlled Docker under the accepted isolation contract, never on the host or against production endpoints.
- Preserve canonical Finding/provenance, stable rule IDs, native 1.7.0 contracts and 1.3–1.6 migrations, SARIF 2.1.0, offline rules-only behavior, honest unsupported/unresolved/incomplete states, candidate-bound review and runtime proof. No independent model discovery or stateful exploit expansion.

## 3. First: fix the actual SSRF detection gap

Start here so subsequent optimization and final timing verification cover the completed detection behavior. Both vulnerable variants of the exposed open-webSearch replacement condition currently miss SENT-015. They are the original and a semantics-preserving helper rename, not two independent vulnerabilities. The two fixed variants and public-IP control have no matching SSRF alerts. All five complete twice; 70 unrelated SENT-006 authentication findings do not count as SSRF detections.

Source pair: Aas-ee/open-webSearch, vulnerable `e29b2357a11d25c9288e1bb006728ddde4d4b6b1` (2.1.6), fixed `739aef2bf7f2c822236bcce0f404c43b57f42503` (2.1.7). Verify against retained source and condition review, not this summary alone. The narrow condition is caller-supplied `http://[::ffff:127.0.0.1]/` reaching an initial outbound request through `fetchWebContent` in the default full runtime without proxy/service overrides. The vulnerable URL safety check supplies bracketed IPv6 hostname text to an IP classifier and misses the private destination; the fixed source normalizes brackets and classifies/rejects it before the request. Other fixed DNS/redirect/agent changes are retained but do not broaden the score or establish runtime exploitation.

Read retained diagnostics:

- `integration/v3-replacement-object-gap-trace.json`, `v3-replacement-gap-trace.json` (under `artifacts/phase22/`).
- `integration/v3-exposed-replacement-assessment/packet.json`, `v3-replacement-rules-final/`, `v3-replacement-rules-repeat/`.
- `corpus-replacement-v1/review/condition-review.json`, original manifest/results and source archives.
- Temporary materializations, if still valid: `/private/tmp/phase22-v3-object-gap-source` and `/private/tmp/phase22-v3-gap-source`; otherwise restore verified archives safely.

Trace the real chain end to end: startup's local dynamic import and conditional full-runtime selection → `createServer(runtime)`/`setupTools` → legacy `.tool` callback → `runtime.services.fetchWeb.execute` → `createWebFetchService(dependencies.fetchWebContent ?? fetchWebContent)` → returned service method/default fetcher → URL guard → axios request helper. Native analysis currently stops at the service binding. An evaluator-assisted trace can resolve `execute` after explicitly supplying a runtime but then stops at the optional/default `fetcher`. Assisted traces are diagnostics, never native detections.

Existing shared fixes already handle schema-bearing legacy `.tool` registrations, object-literal ordinary/async methods, per-call-context returned-function captures, and ordinary/lexical `this`. Inspect `src/sentinel/static/typescript_path_flow.py`, all affected callers and rules, and existing discovery/SSRF regressions before extending them. Do not reimplement or discard those fixes. Establish actual source bindings conservatively; do not pretend every dynamic import, dependency override, computed registration or unknown function is resolved.

Reproduce each real unresolved boundary in durable minimal tests, then fix the smallest shared root. Cover default versus injected/replaced dependencies, relevant branching/alias/capture/receiver behavior, and guards that validate unrelated values, return ignored results, or fail to reject. Preserve unknown cases explicitly. Check equivalent supported Python paths when shared behavior changes. No repository-name, case-ID or hardcoded malicious-URL special cases; recognizing a helper name is not proof of enforcement.

Success: the normal production rules-only pipeline, without evaluator-supplied runtime bindings, completes all five exposed cases twice; produces source-grounded SENT-015 findings matching both vulnerable conditions (2/2); produces zero condition-matched alerts on both fixed variants and the safe control; preserves valid locations/provenance and explains all changed unrelated findings and coverage diagnostics. Broadly flagging both revisions is failure. Retain original 0/2 results unchanged and clearly label new results exposed regression evidence, not fresh holdout accuracy.

## 4. Then: improve benchmark timing through measured work

Current implementation's historical batch completion was 44/45, 45/45, 41/45. Five attempts timed out, all Atlassian: fixed upload mutation in the first batch; fixed auth mutation, vulnerable upload mutation, fixed upload original and download-path safe control in the third. One additional native-completed auth-fixed report took 123.764 seconds end to end. All 45 inputs have at least two identical completed observations under 120 seconds across attempts, but this does NOT meet the original two-complete-batches gate.

Read `v3-historical-casewise-repeatability/{packet.json,wall-time-check.json}`, `v3-final-benchmark-assessment/packet.json`, raw attempts and earlier profiles in the evidence. Do not assume shared-host CPU pressure or low disk space caused the failures; observations have not proved causation. Do not kill unrelated processes or delete unrelated files to obtain a quiet machine.

Use the suggested sequence:

1. Establish controlled baseline measurements of the slow cases after the SSRF fix, with no overlapping agent-owned builds/tests/benchmarks. Record source/config/input/environment identities, available CPU/memory/disk, relevant resource pressure, native scan time, end-to-end wall time, and worker-inclusive CPU use where available. Separate resource wait/startup overhead from expensive traversal. If a quiet environment is unavailable, disclose that limitation rather than claiming isolation.
2. Profile the actual slow paths. Existing implementation already has bounded identity/combination/location caches and up to four source-flow workers for large multicore scans. Inspect them and their callers first. Remove the largest demonstrated repeated work using existing structures or stdlib; do not blindly increase workers/cache sizes or revive previously unsuccessful experiments. Preserve source/context identities, branch semantics, timeout checks, process cleanup, unresolved diagnostics and report ordering.
3. Demonstrate before/after behavior equivalence for performance-only changes and genuine native wall-time improvement without profiler overhead. Compare reports excluding only documented volatile fields, not findings, coverage or unresolved states. Keep all regressions and failures. Aim for useful margin under 120 seconds rather than one lucky pass; report actual variability without inventing an unapproved numerical gate.
4. On one immutable final implementation, run all 45 historical inputs twice through the native approved rules-only runner, sequentially without competing agent-owned work, at the unchanged 120-second/input deadline. Both full batches must complete; each must detect all 20 named vulnerable conditions and have zero named fixed/safe alerts. Check per-input native status AND end-to-end timings. Do not pool successes from multiple failed batches, extend deadlines, bypass production paths, skip expensive rules/source, or substitute profiled component timings for this gate.

If focused investigation cannot fix reliability, document the measured bottleneck, attempted fixes and remaining options and ask for the genuine decision. Do not silently fall back to the unapproved timing exception or endlessly retry until a favorable result appears.

## 5. Fresh corpus checkpoint and complete final measurements

The exposed open-webSearch cases informed implementation, so the original handoff requires fresh replacement holdout evidence. Five proposed cases are prepared in `artifacts/phase22/corpus-replacement-v2/`; manifest SHA-256 `a587427f0c40cbff512f00c8024e454a11255e34a13c10f9d8748bbc4aa9bae2`. The existing packet names implementation `68bdf83`, has `freeze_approved: false`, and records no scanner/comparator evaluation. Do not use these fresh cases as implementation targets or inspect their source for tuning.

After detector/performance changes stabilize, verify and version the proposal against the actual final detector, preserving the old packet. Disclose any source exposure honestly; if independence was compromised, prepare a suitable fresh proposal through the same process. Ask for explicit approval of the exact manifest, source/checkpoint and bounded offline evaluation before running it. Preparation or this continuation is not freeze approval. The prepared evaluation is two native five-input passes at 120 seconds/input and one pinned Semgrep 1.176.0 five-input pass at 300 seconds/input; zero paid calls, no target execution, stop after the bounded runs and report. Preserve runner approval/provenance enforcement. Do not label results at a new detector as measurements of the old frozen detector.

Complete the rest of the original measurement scope on final source: approved original development cases/mutations/controls, original held-out measurement separately, all historical cases above, targeted exposed SSRF regressions, and approved fresh replacements. Reuse existing runners/scorers/corpus/provenance tools, not new bespoke harnesses that bypass constraints. Report misses, false alarms, unsupported/incomplete inputs, correlated variants and exact support/completion denominators. Do not invent a holdout accuracy threshold or tune against fresh holdout results. If results inform another fix, mark exposure, version records and follow the replacement freeze process.

Baseline context to preserve: original development was 25/25 completed, 10 vulnerable detections, two raw fixed Meta alerts handled by the approved erratum and 13 valid clean controls without condition alerts. Original held-out results were 10 completed/10 unsupported/5 incomplete, with 0/4 completed vulnerable variants detected; these limitations do not disappear when the exposed SSRF pair improves. Retain them explicitly in acceptance. Classify any new regression separately from existing documented limitations.

Adjudicate every NEW/CHANGED unrelated finding and coverage delta with source-bound evidence. Preserve the original 70-warning unadjudicated historical backlog as such; it is distinct from the replacement cases' 70 source-assessed auth warnings. Keep raw versus erratum-adjusted scores separate. Retain pinned comparator measurements; reuse unchanged ones only after proving exact input/config/engine/harness compatibility, otherwise rerun applicable scopes. No unmeasured superiority claims.

## 6. Audit every other Phase 22 requirement on final source

Do not stop once the two issues pass. Use all 86 rows in `requirements.md` and original handoff sections 9–17 as the acceptance checklist, with the approved paid/pilot deferrals overriding their obsolete requirements. Retain valid existing evidence through explicit source/dependency compatibility checks; rerun affected checks rather than assuming old passes still apply or rebuilding everything unnecessarily.

Cover all ten benchmark families and five compatibility areas in the approved plan, all SENT-012–016 contracts and Kubernetes SENT-002, Python/TypeScript shared discovery, workspace membership/exports/configuration/boundaries, Helm omissions and strict YAML, candidate-bound review/context/redaction/cache identities, native schema/report/baseline consumers/migrations, and bounded ordered runtime campaigns. Preserve the 160-line review-context total and all runtime budget, baseline, observed-effect, isolation, cleanup and unstarted-remainder semantics.

Verify approved Git Docker startup/discovery/campaign evidence and current runtime fixtures/Action behavior; no direct host target execution. Reuse the tested Git environment identity from its existing approval packet. Maintain source-bound exclusions and unsupported/inconclusive results. Discovery alone is not runtime proof.

Revalidate the two approved captures against actual current production request construction, fingerprints, request hashes, reviewer behavior, fixtures and packaged bytes. The retained TS fingerprint is `b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f`; runtime fingerprint is `b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39`. Check the ledger rather than trusting this summary. If a changed request genuinely requires a new paid capture, prepare the smallest named request/budget/stopping packet and ask first. Never make a call, rewrite a cassette fingerprint to force reuse, or present replay as new live evidence.

Inspect actual Makefile, locked dependencies and workflows. Final checks include Ruff/format, strict mypy, lock validation, generated Finding/report schemas, native JSON and SARIF 2.1.0 validation, full pytest with the existing 80% branch-coverage floor, dependency audit/notices, generated artifacts in offline check mode, strict docs, wheel/sdist and installed-wheel checks, supported fixtures/migrations, Docker/Action and rules-only network isolation. `make check` alone is not the entire gate. Run the required hosted Linux/macOS/Windows and Python 3.10–3.13 quality/wheel matrix plus required Docker/isolation/docs checks on the final code candidate.

Existing baseline: all 29 hosted jobs passed at `68bdf83`, with 12 quality suites each 2,057 passed/36 skipped, 89.50–89.53% branch coverage; CI run 34380163487 and docs run 34380163510. This is historical evidence after edits, not a pass for new code. Pinned Phase 20 reproduction jobs test the historical scanner and do not replace current integration measurements. Retain complete hosted logs/artifacts and verify built distributions contain actual final source/schema/fixture/capture bytes.

## 7. Evidence, delivery, and exact Phase 22 closeout

Make reviewable local commits on the integration branch; batch remote delivery when the integrated candidate is ready. Update existing draft PR #37, preserving old draft PRs and the verified delivered parent. Do not repeatedly push each increment and trigger the full matrix. Do not suppress CI for implementation changes; documentation/evidence-only delivery may cite the tested code commit only after verifying identical relevant bytes, without claiming a new hosted pass.

Append new source-bound evidence and versioned decisions; do not rewrite historical sealed results. Preserve commands/exits/logs, raw reports, all failed/timeout attempts, code/test/source/harness/corpus/config/environment hashes, scoring/adjudication, captures/cost ledgers, timing/resource measurements and CI/package artifacts. Stop evidence writers before sealing; hash archives and read back every member. Ensure everything needed to reproduce the final result is retained in the repository/delivered artifacts, not just `/private/tmp`. Update restoration instructions and archive index without destroying previous seals.

Prepare one final acceptance packet mapping EVERY requirement to its implementation, tests, exact evidence and disposition: passed, explicitly user-deferred, accepted documented limitation, or unresolved. Reconcile stale status text in current owning docs while preserving historical records. Update `ROADMAP.md`, `docs/phase22-technical.md`, `docs/phase22-implementation-status.md`, the SSRF follow-up, integration requirements/progress/README and other affected owning/public docs consistently. Do not globally rewrite historical phase claims.

Phase 22 can be marked complete only when:

1. The exposed SSRF condition passes 2/2 with zero fixed/control condition alerts through native repeated scans.
2. Both entire final historical 45-input batches meet the unchanged deadline, completion and condition-scoring gates.
3. The explicit fresh freeze checkpoint is approved and its bounded evaluation, other required measurements and all new/changed finding assessments are complete, with limitations honestly recorded.
4. All remaining authorized technical requirements, final quality/packaging/Docker/Action/hosted checks, reproducible evidence and consolidated draft delivery are finished; no unresolved requirement is hidden in a TODO.
5. I have reviewed the concrete final packet and explicitly accepted Phase 22's technical completion and its remaining documented limitations. Present the results and decisions succinctly and ask for that acceptance only when the packet is ready. Do not infer acceptance from a previous “continue,” a green CI, this prompt or approval of the fresh corpus.

After that acceptance, record the exact decision and final identities, mark Phase 22 complete under the revised scope, and deliver the final documentation/evidence update to the same draft. Keep the deferred paid benchmark, incomplete Phase 21 and later Phase 24/15 gates visible. Completion does not authorize merging, releasing or starting another phase. If any necessary gate is still unmet, state exactly what remains and the evidence; do not claim completion.

Start with a brief plan and verified baseline, then proceed. Keep me informed of material findings and decisions; ask only where an explicit checkpoint or genuinely missing choice requires my input.
