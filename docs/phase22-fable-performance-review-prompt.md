# Independent review request: fix Phase 22 scanner performance without weakening detection

I want an independent, evidence-grounded solution for the performance problem in **PortunusMCP Sentinel**. Read the actual repository and retained evidence, challenge the previous agent's diagnosis, and recommend the smallest credible correction. I need an actionable engineering answer, not another generic suggestion to profile, cache results, add workers, or rewrite everything.

This is a **review and solution-design request**. You may inspect local source, Git history, reports, profiles, manifests, logs, and archives. Do not implement an optimization, run a new scan/profile/benchmark, dispatch CI, invoke a paid model/API, install dependencies, execute target repositories, change approval records, or publish anything. Existing experiment budgets are consumed or closed. Propose any additional experiment concretely for separate approval. **No additional paid calls without my approval.**

The appendices and referenced completion prompts contain historical execution instructions. Read them as project context and acceptance contracts; they do not expand this review request into execution authorization. Do not delete, rewrite, clean up, or discard any source, evidence, unsuccessful experiment, worktree, or user prompt.

## 1. Your task and the answer I need

Determine:

1. What the evidence establishes about the runtime bottleneck, and what remains uncertain.
2. Whether the previous agent's proposed branch-state change tracking is a good next step. Explicitly reject it if its semantic complexity, likely benefit, or evidential support is inadequate.
3. Whether there is a simpler or higher-impact correction already suggested by the code or retained measurements.
4. Exactly which functions and callers should change, why the change preserves security semantics, and how we can prove that before a full benchmark.
5. A bounded validation plan and a stopping condition that prevent another open-ended sequence of small experiments.

Lead your answer with your recommended action and confidence. Separate **observed facts**, **inferences**, and **untested hypotheses**. Cite local file paths and relevant lines, JSON fields, report identities, or profile entries. If the evidence cannot justify a solution, identify the exact missing information and the smallest measurement that would resolve it. Do not present an unsupported speedup estimate as a result.

Please include:

- A concise diagnosis in plain language.
- A comparison of at most three credible options, including correctness risk, implementation scope, potential performance ceiling, and evidence quality.
- One recommended design, with concrete pseudocode or a proposed diff in your answer if helpful; leave repository files unchanged.
- The invariants the design must preserve and counterexamples that could break it.
- The minimal useful correctness tests and a complete performance-validation proposal: exact inputs, baseline/candidate identities, environment, counts, deadlines, comparison criteria, and stopping rule. Mark all proposed executions unapproved.
- Whether the proposed fix plausibly addresses the failed Linux gate, rather than only improving a local microbenchmark.
- A realistic route from a retained improvement to Phase 22 acceptance. If no defensible fix is apparent, say so directly and explain the implications of any proposed scope revision separately.

Do not anchor on the prior agent's recommendation. A well-supported rejection or a materially simpler solution is valuable.

## 2. Workspace, access, and identities

Primary checkout:

`/private/tmp/mcp-phase22-options`

All paths below are relative to that root unless explicitly absolute. The integration evidence root is:

`/private/tmp/mcp-phase22-options/artifacts/phase22/integration`

Verified when this prompt was prepared:

| Item | Identity |
| --- | --- |
| Branch | `phase22/integration` |
| Local HEAD / last verified delivered draft head | `c07ffeb8a621d00a0ebbe762eda9444ff1f76c40` |
| Existing PR | https://github.com/BashaarJavaid/MCP-Sentinel/pull/37 — OPEN, draft |
| PR base | `phase22/description-poisoning` |
| Recorded PR #36 parent | `8b6b0ddf1d6f6cf5a8da3ab9421471865b801455` |
| Actual latest CPU-sampled source | `127763c09ea23ca2f1c5bbc4871f364cab4a1411` |
| Actual final engineering-test source | `592a9cd016537d827589567bf9be310d4e757c75` |
| Actual final exposed SSRF measurement source | `2ac39aa9331818fd7e3a86c8323ee8307522c98c` |
| Scanner source SHA-256 | `9639435c0657e28f7c9a16ff25b05b4101910241dc35413f5c26392f9fc36647` |
| Measurement harness SHA-256 | `9bfc9229b7ec7d23580c44f2306edb9274bc1d2a3c2261d01db0445b8b480add` |
| `uv.lock` SHA-256 | `c34da413d4761ca42f243bc41a10afd8961a98daa1f3a236d37fe03720743b2b` |
| Separate main checkout | `/Users/bashaarjavaid/Projects/MCP-Sentinel` |
| Main checkout recorded clean source / branch | `4cd57593b2585b9ee05c0f175930e6a0d76d362a`, `phase22/python-containment` |

Later delivery commits changed documentation/evidence only. Current code/test/workflow/package inputs match `592a9cd`. Scanner/harness/configuration/fixture inputs match the exposed measurement at `2ac39aa`; retained test changes distinguish those revisions. Do not call a later docs commit a new tested or benchmarked scanner.

Reverify current state; another user or agent may have made changes after this prompt. Use `git status --short`, `git rev-parse HEAD`, and `git worktree list --porcelain`. Preserve all worktrees, especially frozen historical checkouts. The three prior user prompt files are intentionally untracked; this new review prompt is also initially untracked.

If you cannot access the filesystem, say so before claiming to have checked it. A pasted absolute path does not provide access. Request the checkout plus the referenced evidence archives/files, or access to this workspace. A remote Git checkout alone may lack expanded ignored evidence and untracked user prompts. Do not infer missing evidence merely from GitHub's file listing.

## 3. Project purpose, authority, and current completion state

Sentinel is a build-time security scanner for MCP servers, with a CLI, GitHub Action, native JSON and SARIF. It analyzes supported Python and static TypeScript source and has a separate Docker-isolated dynamic layer. The performance issue concerns the deterministic static source-flow engine. Static analysis must never import or execute target code.

Read these in order:

1. `mcp-sentinel-buildplan.md` — historical context and §11 non-goals.
2. `AGENTS.md`, `ARCHITECTURE.md`, `ROADMAP.md` — active project constraints and gates. Read the latest current-status sections; older sections are explicitly historical.
3. `docs/phase22-technical.md`, `docs/phase22-implementation-status.md`, `docs/phase22-ssrf-follow-up.md`, `docs/rules.md`.
4. `docs/phase22-completion-agent-prompt.md` — full continuation scope, approval boundaries, exact timing/detection/fresh-evaluation/acceptance requirements. A verbatim copy is appended below for context.
5. `docs/phase22-final-agent-prompt.md`, `docs/phase22-detection-timing-closeout-agent-prompt.md`, and `artifacts/phase22/integration/next-agent-handoff-20260908-v2.md` — earlier context, superseded where later evidence says otherwise.
6. `artifacts/phase22/completion-scope-v1/decision.json` and `follow-up-proposal.json` in that directory — explicit paid-benchmark/pilot deferrals.
7. Integration `README.md`, `progress.md`, `requirements.md` and `v17-closeout-audit/packet.json` — evidence restoration, chronological record, all 89 original requirements and 22 added execution requirements.

Phases 16–20 are accepted. Phase 21 recruitment is deferred and remains incomplete. Phase 22 is incomplete. Its current original-requirement audit is **70 passed, 2 explicitly user-deferred, 17 unresolved**; added requirements are **21 passed, 1 unresolved**. Original unresolved IDs are R18–R27, R35, R63–R66, R84 and R88. R18–R27 depend on the full historical gate; these are not ten newly discovered implementation bugs.

Pilots and the full paid benchmark are deferred, not passed. Phase 24 adoption/retention and Phase 15 launch requirements remain unchanged. No next phase, merge, release, outreach or automatic rule promotion is authorized.

### Two remaining technical concerns

**Performance/execution reliability:** The retained full standard Linux sequence at `7555a9d` (run **34435283462**) completes **15/25 development inputs**. All ten Meta inputs time out at 120 seconds; both 45-input historical batches are skipped. Later local diagnostics do not establish a current-source Linux pass. Earlier local development 22/25 and original held-out 10 complete / 10 unsupported / 5 incomplete are separate historical results.

**Fresh evaluation:** The repaired SSRF repositories have been inspected and tuned against. They are exposed regression cases, not fresh generalization evidence. Once the scanner stabilizes, a new source-grounded freeze and bounded native/comparator evaluation require explicit approval. This is an evidence gate, not proof of another known detector bug.

### Detection work that must remain correct

All three exposed SSRF families now pass their narrow final native repeat gates at `2ac39aa`: each has five inputs twice, two vulnerable condition matches per batch, and zero matching fixed/control alerts.

- SearXNG: default loopback-IPv4 rejection; prior guard-fact loss was corrected through shared TypeScript branch invalidation-state isolation. Broader candidates and unresolved MCP dispatch remain visible.
- fetch-mcp: initial private-IPv4 request through `fetch_html`, source-grounded parsed-host validation.
- open-webSearch: initial IPv4-mapped IPv6 loopback through established startup/service/guard flow.

Do not describe SearXNG's old fixed false positives as still failing; that particular correction passed. Preserve the original frozen misses, failed intermediate fixes, broader warnings, and narrow-condition limitations. These results are neither general SSRF safety nor runtime exploit proof.

## 4. What the performance evidence actually says

Evidence paths in this section are relative to `artifacts/phase22/integration/`.

### Earlier Linux and local attempts

- `v10-linux-diagnostic-assessment/packet.json`, `v10-linux-dispatch.json`, `v10-hosted-05309f9/` — the single Linux diagnostic run **34446017571**; all four native and two profiled inputs time out. Preserve partial profiles and their attribution limits.
- `v10-local-performance-assessment.json`, `v10-local-performance-disposition.json`, `v10-merge-hypothesis.json`, `v10-local-performance-profile/`, `v10-local-performance-baseline/`, `v10-local-performance-after/` — duplicate immutable-merge canonicalization preserved reports but produced small/inconsistent gains and was reverted. Its useful guard regression remains.
- `v11-performance-disposition.json`, `v11-traversal-profile/`, `v11-follow-up-authorization.json`, `v10-next-performance-proposal.json` — helper-context profiling did not prove any safely reusable full helper result. In SENT-012, 19,543 helper calls yielded 19,435 unique signatures; the 108 repeated source/context/binding signatures still had changed bindings, and side-table sizes do not establish equal contents. Read the actual counters for all rules. Blanket helper memoization is not justified by repeated source function names.
- `v14-retained-profile-review.json` — source/hash binding and selected entries from an earlier partial Linux cProfile. Full profile:
  `v10-hosted-05309f9/artifacts/linux/phase22-linux-diagnostic/profile-meta-image-ssrf-vulnerable-1-workers/SENT-015.prof`.
  SHA-256: `0fa2d507a1c078bd0fb40af29463cf19cf9a0d8bff44203143423d5bdabed2e5`.
  Related `SENT-015-counts.json` is alongside it. Inspect raw callers/callees with standard-library `pstats`; reading a retained profile is not a new scan. Source paths inside that profile point to the former Linux runner.

The earlier full Linux failure is cross-referenced by those records, the completion prompt, and historical integration audits. Locate its underlying retained manifest/logs through those references and the numbered seal indexes rather than assuming a new filesystem path. Hosted run: https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34435283462.

### v13: immutable Value reconstruction attempt — reverted

Read `v13-performance-proposal.json`, `v13-performance-authorization.json`, `v13-performance-counter-assessment.json`, `v13-performance-final-comparison.json`, `v13-performance-disposition.json`, `v13-performance-revert-receipt.json`, and raw `v13-performance/`.

One optimization at `de2a02f51295518ca34449210e5ce9a7fc3eb78d` was reverted to `2ac39aa`. Two profiles and 12 native observations consumed the budget. Full ordered native reports matched, but gains were inconsistent: Atlassian median wall improved about16.7%, image Meta about5.35%, while operator Meta worsened about4.58% in wall and1.31% in child CPU. This failed the approved retention requirement. The two profiles also have recorded deadline failures: image120.049s; operator end-to-end120.409s. Do not present either as a passing bounded observation.

### v14: one-pass helper-fact selection — reverted

Read `v13-next-performance-proposal.json`, `v14-performance-authorization.json`, `v14-counter-assessment.json`, `v14-optimization-attempt.json`, `v14-performance-disposition.json`, `v14-queue-stop-outcome.json`, `v14-performance-completed-comparison.json`, `v14-performance-revert-receipt.json`, and `v14-performance/`.

The counter found 99.42% empty-fact visits, but the one-pass candidate `e57ce9569ee793882f1c0524bad8ba0aefa17588` failed the prospective individual-observation rule: operator candidate77.556s /195.041848 child CPU seconds exceeded baseline maxima75.134s /188.048785. It was reverted in `a7d7de0d32ece24eecc654d902496ebff78ee033`.

Budget used: one profile and ten native attempts, of which nine completed and one was interrupted. Two remaining native observations and30 conditional SSRF observations were cancelled. All ten completed reports, including the profile, matched their baselines. No complete candidate pair or median improvement is claimed. Preserve the initial type/lint failures, interrupted run and corrected checks.

Retained test: `tests/test_python_state_flow.py::test_helper_guard_facts_preserve_filters_and_aliases`; final typing/test verification is at `592a9cd`.

### v15: merge counters, no optimization

Read `v14-next-merge-diagnostic-proposal.json`, `v15-merge-authorization.json`, `v15-merge-assessment.json`, `v15-combine-source-review.json`, `v15-merge-profile/`, and `v15-instrumentation-selfcheck-final/packet.json`. Earlier failed/initial self-check and review records remain alongside them.

One operator Meta profile at `77ea21fa1f8c52f1f1ab11eba4d1cc8f2c24c7ef` completed88.533s native /90.084s outer. Ordered report matched. Approximately19.01 million multi-branch key visits across three active workers, with about85% taking existing direct reuse. The multibranch processing block consumed17.8–21.3 instrumented CPU seconds per worker; it includes nested combination and instrumentation. URL preprocessing added3.79 CPU seconds. **85% of visits is not85% of CPU.**

### v16: duplicate-operand combination predicate — failed before optimization

Read `v15-next-combine-proposal.json`, `v16-combine-authorization.json`, `v16-combine-assessment.json`, `v16-combine-profile/`, and `v16-instrumentation-selfcheck/packet.json`.

One profile at `46b8786a30ec44e6176e5900512ab0eea56518ac` completed81.271s native /82.947s outer, matching the entire ordered report. A shortcut for more than two operands with exactly two distinct immutable object identities was conditional on a prospective10% eligible-body CPU share **in each active worker**, along with count/frequency/report conditions.

Eligible combinations were frequent (83.72%,85.54%,84.47%), but body CPU shares were only **7.81% SENT-012,5.34% SENT-015,6.81% SENT-016**. All three failed that CPU threshold. **Zero optimization attempts**; all12 performance and30 conditional exposed observations were cancelled. Those unused maxima are closed, not an open budget.

### v17: whole-worker CPU sampling — complete, no proven fix

Read `v16-next-worker-sampling-proposal.json`, `v17-sampling-authorization.json`, `v17-sampling-assessment.json`, `v17-timing-disposition.json`, `v17-sampler-selfcheck/packet.json`, and raw `v17-sampled-profile/`.

One `meta-operator-fallback-fixed-mutation` profile at `127763c` completed **69.906s native /71.578s outer**,49 findings, full ordered baseline match, valid native JSON/SARIF. No scanner method was replaced; a standard-library POSIX CPU timer sampled Python worker frames at a requested maximum100Hz. Four final snapshots restore signal/timer state. No locals or target values were recorded.

| Rule | Samples | Base expression leaf share | Shared merge inclusive share |
| --- | ---: | ---: | ---: |
| SENT-012 | 4,220 | 11.66% | 24.81% |
| SENT-015 | 5,093 | 15.92% | 19.18% |
| SENT-016 | 4,903 | 14.28% | 22.58% |

SENT-014 has only107 samples and1.183 sampled CPU seconds. Active workers delivered85.06–87.38 samples per sampled CPU second. Most expression leaf samples occur at the definition/entry line, limiting line-level inference. Python signal delivery, native-code/GIL delays, sampling overhead and snapshot-thread CPU can bias attribution. Inclusive caller/callee shares overlap and must not be summed. No sample share is wholly removable cost. The lower wall time of this differently instrumented observation is **not a demonstrated optimization**.

Raw files:

- `v17-sampled-profile/SENT-012-cpu-samples.json` and corresponding SENT-014/015/016 files: frame catalogs, full leaf-to-root stack IDs/counts, timing, events and final-state flags.
- `v17-sampled-profile/worker-profile.py`: actual sampler.
- `v17-sampled-profile/attempt.json`, `execution.json`: source, environment, resource/load and deadline information.
- `v17-sampled-profile/measurement/meta-operator-fallback-fixed-mutation/report.json` and `report.sarif`.
- Baseline: `v14-performance/baseline-meta-operator-fallback-fixed-mutation-1/measurement/meta-operator-fallback-fixed-mutation/report.json`.

This scope consumed one profile and permitted zero optimizations. It is closed. Current source remains unchanged. No larger safe optimization has yet been established.

## 5. The prior agent's current suggestion — challenge it

The prior agent recommended keeping the timing gate and first assessing a focused redesign of branch-state merging:

1. Track each branch's changes and deletions relative to its starting state.
2. Avoid reprocessing entries proven unaffected, while retaining required guard normalization, alias handling, defaults, missing/None semantics and conservative fallback.
3. Prove equivalence against the existing implementation on small security-relevant cases before proposing a bounded performance experiment.
4. Reject the approach if it needs pervasive mutation machinery or cannot safely cover the shared callers.

**This is only a hypothesis. No design, prototype, measured benefit, or experiment approval exists.** The19–25% inclusive merge shares include required work, so even eliminating that entire cost is an unrealistic upper bound. Evaluate whether the realistically removable part could matter for Linux timeouts, whose true completion times are censored at120 seconds. Do not infer that a20% local improvement would necessarily pass Linux.

Consider the existing shortcuts before proposing new ones: immutable `Value` objects, bounded `_combine` and `_key` caches, whole-equal-branch handling, single-branch handling, per-value identity/equality reuse, and rule-specific caches. No blanket memoization, blind worker/cache increase, skipped files/rules, reduced source coverage, weaker guards or longer deadline should be smuggled in as an equivalent optimization.

Investigate repeated work across handler/startup/helper contexts as an alternative only if full state and side effects can be accounted for. Repeated source function names do not prove equal analysis contexts. A combined-rule traversal or new environment abstraction is not automatically smaller or safer; justify its scope if recommended.

## 6. Source map and correctness risks

Start with these actual files; line numbers are hints for the current unchanged source, not immutable API contracts:

- `src/sentinel/static/path_flow.py`:
  - `Value` near25; `combine`54; `_combine`58; `_key`160.
  - `PathFlow` state near190; `entry_group`274; `entry_handler`395; `function`556; `statements`640.
  - `combine_instances`982; `assign`1166; `merge`1243; `truth_value`1302; `expression`1520; `call_receiver`1914; `call`1927.
  - Shared merge call sites include helper exits609; branches791; try/finally832/834; loops877/884/895; expressions1798. Search all callers yourself.
- `src/sentinel/static/rules/sent012.py`: analysis orchestration and path rule.
- `src/sentinel/static/rules/sent015.py`: `URLFlow`, `fixed_destination`73, rule merge149, statement/guard logic, `expression`293 / `expression_value`307 and call handling509; TypeScript URL logic also lives here.
- `src/sentinel/static/rules/sent016.py`: `CredentialFlow`, branch-local credential conditioning93, merge159, expression251 and call303; TypeScript credential logic also lives here.
- `src/sentinel/static/execution.py`: `check_deadline`29 and existing helper-summary structures for other source recognizers. Do not assume those summaries model PathFlow effects.
- `src/sentinel/static/discovery.py`: source indexes, `resolve_in`124 and its existing cache.
- `src/sentinel/static/http_context.py`, `http_discovery.py`, `registration_flow.py`, `lifespan.py`, `launches.py`: source-established startup, callbacks, HTTP state, registration and helper context.
- `src/sentinel/static/typescript_path_flow.py`, `typescript_registration_flow.py`, `typescript_discovery.py`: sibling semantics and corrected branch/factory/discovery behavior.
- `src/sentinel/static/workers.py`: normal bounded worker eligibility, isolated scanner-owned snapshots, deadline enforcement and cleanup. There are up to four workers for sufficiently large inputs; do not assume the Linux run was single-threaded or lacked worker eligibility.
- `src/sentinel/static/engine.py`, `model.py`, `coverage.py`: detector dispatch and canonical report/coverage integration.

Trace mutations before suggesting an environment shortcut. Relevant behavior includes additions/deletions, aliases and escaped/replaced objects, global/member defaults, instance alternatives, closure/callback side tables, nested branches, exceptions/finally, loops, return exits, truth facts, URL/credential qualifiers and dictionary/report ordering. Some apparently unchanged untainted values deliberately lose guard exemptions at merge. A changed-key list alone does not prove that such values may be skipped.

Tests and tools:

- `tests/test_python_state_flow.py`, `tests/test_ssrf.py`, `tests/test_credential_fallback.py` and other affected discovery/containment/HTTP/TypeScript tests found with `rg`.
- `tests/test_phase22_reports.py`, `tests/test_phase22_corpus.py`, `tests/test_phase20_measurements.py`, reference fixtures under `tests/fixtures/`, independent corpora under `tests/evals/` and `artifacts/`.
- `scripts/phase22_corpus.py`, `scripts/phase20_corpus.py`, `scripts/phase20_measurements.py`, `scripts/phase20_scoring.py`, `scripts/run_phase20_benchmark.py` — existing freeze, measure, scoring and repeat-comparison machinery. Reuse these contracts; do not design a substitute evaluator.
- `.github/workflows/ci.yml`, `Makefile`, `pyproject.toml`, `uv.lock`, `action.yml` — real verification, packaging and runner configuration.

For performance-only changes, compare the **entire ordered report**, including warnings/coverage. Do not sort away differing arrays. Only established volatile fields may be excluded; the exact list is in `v14-performance-completed-comparison.json` and `v17-sampling-assessment.json`: `applied_at`, `completed_at`, `duration_ms`, `execution_latency_ms`, `finding_id`, `latency_ms`, `origin_latency_ms`, `reviewed_at`, `scan_id`, `started_at`, `timestamp`.

Keep stable rule IDs, canonical Finding/provenance, native schema1.7.0 and migrations1.3–1.6, SARIF2.1.0, supported Python/static-TypeScript scope, deterministic offline mode, and distinct unsupported/incomplete/unknown/defense outcomes. Do not hide findings or weaken scoring to make an optimization pass.

## 7. Corpus, detection, engineering, and cost evidence map

Original corpus/source and mutation archives:

- `tests/evals/phase20/manifest.yaml`, `tests/evals/phase20/snapshots/`, `tests/evals/phase20/mutations/`, `tests/evals/phase20/configuration/`.
- `artifacts/phase22/corpus-review/manifest.json`, `source-review.json`, `inventory.json`, `review/`, `provenance/`, `snapshots/`, `mutations/`, `THIRD_PARTY_NOTICES.md`.
- `artifacts/phase22/corpus-replacement-v1/` — open-webSearch; v2 — fetch-mcp; v3 — SearXNG. Read their README, manifests, checkpoints, authorization/exposure receipts, source reviews, snapshots and mutations. Follow the exact paths stored in each manifest; do not substitute a current upstream checkout.
- `artifacts/phase22/meta-fixed-label-erratum-v1/` — raw Meta labels and the separate approved interpretation. This erratum does not waive timeouts.
- `artifacts/phase22/execution/` — earlier execution measurements, before/after Atlassian profiles and source-bound verification. These are historical, not current full Linux results.

Exposed SSRF results under integration:

- `v13-exposed-assessment/packet.json`, `v13-searxng-assessment/packet.json`.
- `v13-exposed-fetchmcp-rules-first/` and `-repeat/`.
- `v13-exposed-openwebsearch-rules-first/` and `-repeat/`.
- `v13-exposed-searxng-rules-first/` and `-repeat/`.
- `v13-searxng-fixed-trace/`, `v13-final-native-attempts/` and related continuation authorization/scoring evidence.
- Original v3 freeze/checkpoint at `7555a9d` and v12 failed fixed-discrimination results remain retained. The correction of an earlier mistaken scope boundary is in `v12-scope-interpretation-correction.json`; do not revive the superseded v11 guard-contract checkpoint.

Engineering and compatibility under integration:

- `v14-hosted-final/packet.json`, `v14-hosted-final-audit/packet.json`, and the directories they index: complete logs and225 uploaded files; CI **34518818910**, docs **34518818938**, at `592a9cd`.
- `v14-final-local-checks.json`, `v14-final-full-suite.json`, `v14-final-full-suite-coverage.json`, `v14-current-source-test-bindings/packet.json`.
- Final local and each of12 hosted suites: **2,183 passed,36 skipped,no expected failures**. Local branch coverage89.66%; hosted89.65–89.68%. All29 normal jobs plus docs pass; optional measurement job skipped. Wheel/sdist153/166 members were compared with actual Git blobs.
- `v14-final-production-capture-revalidation/packet.json`: both previously approved production requests regenerated/replayed, plus four older static demo requests; zero new paid calls.
- `v14-compatible-evidence/packet.json`: approved Git runtime source/dependency/image compatibility. Thirteen campaigns remain incomplete:1,040 planned,312 tested,728 remaining, exit3 and cleanup. Do not turn compatible reuse into complete runtime protection.
- `v17-source-verification.json`, `v17-final-documentation-binding.json`, `v17-delivery-verification.json`, `v17-final-delivery-readback.json`, `v17-closeout-draft-body.md`: source equality, latest docs and draft delivery. The final readback is an ignored local supplemental record; directly tracked/sealed records remain authoritative for their named identities.

Paid/runtime scope:

- `artifacts/phase22/paid-evaluation-v2/`, `artifacts/phase22/git-environment-v1/`, `artifacts/phase22/git-environment-v1-tested/`.
- Two historical paid requests cost **$0.071799 total**; that approval is spent. Full396-request paid benchmark is user-deferred. Never use `--allow-degraded` as an offline guarantee; it can call the model when credentials exist. Do not run `make artifacts-live`.
- Approved Git runtime image: `sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`. Do not change the tested runtime environment or execute production targets.

## 8. How to find and read all retained evidence

**Do not rely only on `rg --files` defaults:** expanded evidence is often Git-ignored. Use explicit known paths, `Path.iterdir()` / `Path.rglob()`, or `rg --files --hidden --no-ignore` scoped to the evidence directories. Avoid dumping the entire corpus into your context; inspect relevant JSON sections fully and follow their referenced raw files.

Integration evidence is preserved in **46 immutable numbered seals**:

`artifacts/phase22/integration/evidence-v1.json` through `evidence-v46.json`, with matching `evidence-v1.tar.gz` through `evidence-v46.tar.gz`.

Latest seal46: **64 files**,11,318,576 raw bytes,410,595 compressed bytes; SHA-256:

`9ea5341776dddd494c9d9c160e9b587bc385a930b385b3268a00dfa30a43e0a5`.

Every seal46 member and all45 earlier archive hashes were verified. Seal46 contains the v17 raw diagnostic and closed commands, source review/verification, the initial sandbox Docker-inspection failure and successful authorized recheck, and diagnostic helper sources. Latest owning docs and post-seal audit/delivery bindings are tracked directly. Earlier raw failures are retained in their original seals; do not rewrite them as successes.

Read integration `README.md` for the full restoration/conflict protocol. If expanded evidence is missing, find its member in the manifests and inspect it directly from the archive or restore into a separate empty staging directory. Verify archive hashes and each member's hash/size; reject traversal paths/symlinks and unexpected conflicts. Apply batches in numeric order if reconstructing cumulative state. Never extract blindly over the active checkout or overwrite a numbered seal. Existing destinations must match identical bytes or their recorded prior hashes.

Each `evidence-vN.json` contains an archive name/hash and `files` rows with member path/hash/size. This is the exhaustive retained-file index; the lists above are starting points, not permission to discard omitted evidence.

Diagnostic helper copies also exist at `/private/tmp/phase22-*.py`. The v17 helpers include `phase22-v17-sampling-worker.py`, `phase22-v17-run.py`, `phase22-v17-selfcheck.py`, `phase22-v17-assess.py`, `phase22-v17-review.py`, `phase22-v17-verify.py`, `phase22-v17-seal.py`, `phase22-v17-closeout.py` and `phase22-v17-delivery.py`. Their archived copies are in `diagnostics-v46.tar.gz` inside seal46, plus command-specific `*.untracked.tar.gz` captures. Earlier helper generations live in earlier diagnostic archives. Read them, but do not execute old scripts: many hardcode commits, output labels, approvals and mutation/delivery actions.

`/private/tmp/phase22-check.py` records command, source, patch, helper snapshot, logs and exit code. It does **not** prevent label reuse/overwriting. Any future approved execution must use new labels and preserve partial/failing records.

Existing locked interpreter: `/Users/bashaarjavaid/Projects/MCP-Sentinel/.venv/bin/python`; recorded Python3.12.13, Semgrep1.176.0, mcp1.29.0, pytest9.0.3, pydantic2.13.4 on macOS. Active source imports need the integration `src` and root, not the main checkout's editable package. These versions describe retained local measurements, not every hosted environment. Do not change/install the environment for this review.

## 9. What an eventual successful correction must demonstrate

The proposed experiment must preserve all reported security behavior and show repeatable **uninstrumented native** improvement under the unchanged120-second native/end-to-end cap. The historically named performance inputs are:

- `meta-image-ssrf-vulnerable`
- `meta-operator-fallback-fixed-mutation`
- `atlassian-upload-fixed`

Exact source archives, configurations and manifest hashes are in the existing proposals and measurement records. Bind a future proposal to those identities, the immutable candidate, harness, lock, environment, input count and stopping rule. Propose enough controlled observations to assess variability, while acknowledging cost/time limits. Do not pool partial runs or substitute profiled results for native passes.

A full Linux retry is a **separate approval after demonstrated native improvement**:

1. 25 development inputs; proceed only if that entire gate passes.
2. 45 historical inputs; proceed only if the entire first historical gate passes.
3. 45 historical inputs repeated, with full ordered equivalence and adjudicated deltas.

Maximum115 native observations,120 seconds native and end-to-end per input,230 nominal input-minutes and240-minute job ceiling, standard approved runner/workflow. Required development:25/25 complete,10 vulnerable hits, only the two approved raw Meta erratum alerts and zero matching alerts on13 valid negatives. Each historical batch:45/45 complete,20 vulnerable condition hits and zero matching alerts on25 negatives. No pooled partial batches, unapproved runner change, timeout extension or casewise waiver.

After detector/performance stabilization, a separately approved fresh freeze/evaluation is needed. Recommended existing shape: independent vulnerable/fixed source pair, paired mutations and a safe control; two five-input native runs at120s/input and one pinned Semgrep five-input run at300s/input; source-exposure disclosure, full reports and assessments. Do not curate cases by first testing whether the scanner passes them. The original held-out result remains10 complete/10 unsupported/5 incomplete, with0/4 completed-vulnerable hits; never relabel it as a current success.

All other applicable engineering/capture/runtime evidence must either be rerun when affected or proved compatible at its actual executed source. Final Phase22 acceptance requires my explicit decision after the concrete passing packet; neither this review nor an experiment approval is acceptance.

## 10. Final instruction

Please read the evidence and code yourself, then tell me what you would actually change and why. Preserve the uncertainty where the evidence is weak. I prefer an honest, narrowly justified next step over an impressive rewrite or another sequence of speculative micro-optimizations.

The current agent thinks an independent review is worthwhile, recommends preserving the timing gate, and considers branch-state change tracking only a candidate for scrutiny. You are explicitly invited to disagree. Finish with the one decision or precisely bounded additional evidence request, if any, that I need to make next.

## Appendix: original completion prompt, verbatim historical context

The following is a preserved copy of `docs/phase22-completion-agent-prompt.md`. Its starting identities and old current-status statements are superseded by the v13–v17 evidence above. Its historical execution language does not authorize new experiments or implementation during this independent review. The current review-only scope at the top controls your actions.

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
