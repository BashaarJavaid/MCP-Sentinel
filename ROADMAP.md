# MCP Sentinel Roadmap

## 1. Planning frame

This roadmap is ordered by dependency gates, not calendar dates. It assumes one engineer. A phase begins only after the previous phase's verification gate passes.

Phases 0–5 are the complete required hackathon deliverable. Required work is not deferred beyond submission. Phase 6 is conditional stretch work and must not destabilize Phases 0–5.

The architecture and accepted contracts are defined in `ARCHITECTURE.md`. This roadmap tracks implementation and verification; it does not redefine those decisions.

## 2. Delivery definition

The required delivery is complete only when all of the following are true:

- A local Python MCP repository can be scanned through the Typer CLI.
- The hybrid AST/Semgrep engine runs all seven static rules without executing target code.
- GPT-5.6 Sol reviews every candidate within the configured cap through the Responses API and strict Structured Outputs during a normal scan.
- GPT grounds each decision in validated evidence references and produces a constrained plan that orders and parameterizes all four approved probe templates.
- Docker runs all four stdio probes under the approved isolation limits.
- Static, dynamic, and GPT review data merge into canonical Findings.
- Console, JSON, and schema-valid SARIF reports are generated.
- Exit codes distinguish findings, input errors, and infrastructure failures.
- The composite GitHub Action uploads SARIF to a live repository's Security tab.
- Vulnerable and clean fixtures, offline GPT cassettes, Docker integration tests, and the quality gates pass.
- The live demo can show the vulnerable fixture, scan results, OWASP mappings, GPT reasoning, and GitHub SARIF integration.
- A versioned ablation demonstrates the difference between rules-only, GPT-reviewed, and dynamically confirmed results.
- Judges can install a prebuilt wheel and run a live or visibly labeled replay demo without rebuilding Sentinel.

## 3. Phase 0 — Scaffold and contracts

### Objective

Establish an executable, typed scan-to-report shell before implementing detectors.

### Work

- Create the approved `src/sentinel/`, `schemas/`, `scripts/`, `tests/`, and `demo/` structure.
- Configure packaging for Python 3.10–3.12.
- Add required runtime dependencies, including Typer, Pydantic, Semgrep, the OpenAI Python SDK, `sarif-om`, and `jsonschema`.
- Configure pytest, Ruff, `mypy --strict`, coverage, and `pip-audit`.
- Implement the thin Typer shell in `src/sentinel/cli.py`.
- Scaffold `sentinel demo` and the `make demo` wrapper without implementing later-phase detector behavior early.
- Implement configuration loading and precedence in `src/sentinel/config.py`.
- Reject unsupported frameworks, HTTP/SSE transport, invalid environment forwarding, and malformed target configuration.
- Implement the canonical Pydantic Finding model in `src/sentinel/finding.py`.
- Generate and check in `schemas/finding.schema.json`.
- Generate and check in `schemas/report.schema.json` with an offline relative reference to the Finding schema.
- Implement `python -m sentinel.schema generate|check` and package root schemas as wheel resources.
- Vendor the OASIS SARIF 2.1.0 schema at `schemas/sarif-2.1.0.schema.json`.
- Implement the minimal console, JSON, and SARIF output shell.
- Implement `src/sentinel/report/validate_sarif.py` and its module command.
- Implement `src/sentinel/orchestrator.py` as a no-op phase pipeline that preserves exit-code semantics.
- Make the Phase 0 pipeline report detector stages as skipped, reporting as successful, analysis as incomplete, and return exit code `3`.
- Add initial `sentinel.toml` and target-configuration fixtures.
- Add the MIT `LICENSE`, `artifacts/`, and `tests/evals/` paths required by the distribution and evaluation contracts.

### Verification gate

- `sentinel scan --help` succeeds on Python 3.10, 3.11, and 3.12.
- A malformed target returns `2`, while an internal test failure returns `3`.
- A no-findings scan emits console, JSON, and SARIF from the same Finding model.
- `python -m sentinel.report.validate_sarif <file.sarif>` succeeds offline.
- `python -m sentinel.schema check` proves both generated native schemas have no drift.
- Regenerating `schemas/finding.schema.json` produces no unexplained diff.
- Ruff, strict mypy, unit tests, and the initial 80% coverage gate pass.

## 4. Phase 1 — Static rule engine

### Objective

Produce deterministic, auditable candidates for the seven permanent static rule IDs.

### Work

- Implement the AST coordinator in `src/sentinel/static/engine.py`.
- Implement the pinned Semgrep subprocess adapter and startup version check.
- Add `src/sentinel/static/rules/` modules for `SENT-001` through `SENT-007`.
- Add the canonical `ASI0X:2026` mapping in `src/sentinel/owasp_mapping.py`.
- Apply the impact/exploitability severity calculation to every candidate.
- Implement `.gitignore`, default exclusion, symlink, and scan-root boundary behavior.
- Implement `--rules` comma-separated include/exclude filtering.
- Implement the `SENT-005` path-glob and SHA-256-fingerprint allowlist.
- Build vulnerable and clean Python MCP/FastMCP fixtures.
- Record an OWASP justification, false-positive risk, remediation, and fixture expectation for each rule.
- Complete the rule-review checklist for every rule.

### Verification gate

- Every static rule triggers its vulnerable fixture case.
- Every static rule passes its clean fixture and explicit false-positive controls.
- Static tests prove target modules are never imported or executed.
- Semgrep version mismatch fails explicitly instead of silently dropping checks.
- All Findings validate against `schemas/finding.schema.json`.
- Static output produces valid console, JSON, and offline-validated SARIF reports.
- The full Python CI matrix, quality gates, and 80% coverage pass.

## 5. Phase 2 — GPT semantic review

### Objective

Make GPT review a required, auditable, operationally consequential stage that reclassifies deterministic candidates, grounds its decisions, and plans constrained dynamic verification without replacing deterministic authority.

### Work

- Implement the response model in `src/sentinel/llm/schema.py`.
- Implement the GPT-5.6 Sol Responses API client in `src/sentinel/llm/semantic_reviewer.py`.
- Set `store: false`, use explicit `gpt-5.6-sol`, and record the requested model plus returned `response.model`.
- Use strict Structured Outputs generated from the Pydantic review models rather than parsing free-form JSON.
- Set reasoning effort to `medium` for the production baseline and evaluate `low` against the same truth set.
- Restrict requests to rule ID, tool schema/description, and a small flagged context window.
- Redact `SENT-005` secret matches and absolute paths before transmission.
- Batch related cache-miss candidates by tool or file while returning one review keyed by every requested `finding_id`.
- Validate batch completeness, status, numeric confidence, reasoning, evidence references, constrained probe plan, and advisory severity suggestions.
- Require grounded evidence references to point to supplied repository-relative paths and line ranges.
- Require every static probe plan to contain `SENT-008` through `SENT-011` exactly once.
- Limit probe targets and argument bindings to discovered tools, declared schema fields, inert values, and approved templates; reject executable model-authored probe code.
- Fall back to the fixed probe order without skipping checks when a probe plan is absent or invalid.
- Stamp the actual model and review time in the host process.
- Normalize numeric confidence into `high`, `medium`, or `low`.
- Update exploitability to `likely` only for a corroborated static finding.
- Persist suppressed findings and their reasoning.
- Implement 30-second timeouts, two retries with backoff, and five-call concurrency.
- Enforce the configurable 500-finding default cap without dropping overflow candidates.
- Mark overflow candidates `needs_review`, emit a visible truncation warning, and continue without treating the cap as an internal failure.
- Implement cache keys based on rule ID, snippet hash, and schema hash.
- Keep reusable prompt/rule prefixes stable and record cached/cache-write tokens before considering explicit cache breakpoints.
- Implement fail-closed behavior and the explicit `--allow-degraded` path.
- Capture real GPT-5.6 responses once and replay them as deterministic cassette fixtures.
- Implement the visibly labeled `sentinel demo --replay-review` path through the same parser, plan validator, merge, and reporting code.
- Record per-batch model, effort, mode, latency, retry, refusal/incomplete state, schema result, token usage, cache use, and status counts without logging source snippets.
- Attach the model, pricing source, and pricing-as-of date to cost estimates; report token usage alone when authoritative pricing is unavailable.
- Create `tests/evals/gpt_review_cases.yaml` with true positives, seeded false positives, ambiguous cases, and probe-prioritization cases.
- Generate `artifacts/gpt-ablation.json` from rules-only, GPT-reviewed, and GPT-plus-dynamic treatments over the same truth set.

### Verification gate

- A true-positive static fixture becomes `confirmed` with normalized confidence and review provenance.
- A seeded false-positive candidate can become `suppressed` but remains in all report formats.
- GPT cannot create a rule-less finding, change `source`, delete a candidate, or mutate severity.
- Invalid model output is rejected and follows retry/failure policy.
- Structured Outputs refusals, incomplete responses, missing/extra finding IDs, invalid evidence references, and invalid probe plans are covered explicitly.
- GPT cannot invent probe IDs, omit a mandatory probe, target an unknown tool/field, or emit executable probe code.
- Missing GPT access returns `3` by default.
- Degraded mode keeps candidates in `needs_review` and records why review did not run.
- Cap overflow keeps candidates in `needs_review`, warns visibly, and does not return `3`.
- CI runs fully offline against recorded responses.
- SARIF preserves review status, reasoning, confidence, and advisory severity data.
- Replay findings are unmistakably labeled and cannot appear as live reviews.
- The ablation includes rules-only, GPT-reviewed, and dynamically confirmed metrics for true/false positives, precision, recall where defined, structured-output validity, evidence grounding, plan validity, latency, tokens, cache behavior, and cost per successful review with auditable pricing metadata.
- The truth set demonstrates at least one corroborated true positive, one grounded visible suppression, one ambiguous `needs_review`, and one correctly prioritized probe.
- `medium` and `low` reasoning effort are compared without changing the production default unless the measured results justify it.

## 6. Phase 3 — Docker dynamic probing

### Objective

Confirm runtime behavior through four mandatory stdio probes without exposing the host or external systems.

### Work

- Implement target execution in `src/sentinel/dynamic/sandbox.py`.
- Implement dependency-only image builds and the approved cache key.
- Restrict build egress to configured package registries and pass no credentials.
- Mount target source read-only and scratch storage as tmpfs.
- Enforce no external DNS/egress, stripped environment, `no-new-privileges`, PID, CPU, memory, and timeout limits.
- Validate `env` and `env_from`, including secret-name denial and explicit `OPENAI_API_KEY` exclusion.
- Implement `scripts/reap_orphans.py` and run it before each dynamic invocation.
- Add forced cleanup for normal completion, crashes, and timeouts.
- Implement `SENT-008` through `SENT-011` in `src/sentinel/dynamic/prober.py`.
- Validate the Phase 2 grounded probe plan independently before it reaches the sandbox.
- Use Phase 2 review results only to order and bind approved inert template values; run all four probes even when the plan is invalid.
- Give each probe a fresh ephemeral container.
- Send dynamic candidates through the same GPT semantic reviewer.
- Batch related dynamic candidates by tool or file; dynamic reviews set `probe_plan` to null because execution has already occurred.
- Implement deduplication and provenance merging, including the `SENT-003`/`SENT-009`/`SENT-011` rule.
- Preserve `SENT-008` and `SENT-010` as distinct root causes.

### Verification gate

- The vulnerable fixture triggers all four intended dynamic behaviors.
- The clean fixture rejects all four probe classes safely.
- Dynamic proof assigns exploitability `confirmed` and computes severity from impact.
- Target source remains read-only and cannot access the host outside its mount.
- Runtime containers cannot resolve DNS or reach external networks.
- Secret-shaped `env_from` names and unsupported transports fail before launch.
- Docker absence, build failure, probe failure, and cleanup failure return `3`.
- `--static-only` is the only path that omits target configuration and Docker.
- A kill-mid-run integration test proves the orphan reaper removes stale containers.
- Merged findings retain complete static and dynamic provenance without duplicate report rows.
- A valid GPT plan prioritizes the intended probe and safe argument binding for its fixture case.
- Invalid, missing, or adversarial GPT plans fall back to the fixed order without reducing probe coverage.

## 7. Phase 4 — GitHub Action and SARIF integration

### Objective

Deliver the required CI workflow and prove that Sentinel findings appear in GitHub code scanning.

### Work

- Implement `action.yml` as a composite Action for `ubuntu-latest`.
- Add `target-path`, `fail-on`, `openai-api-key`, and `static-only` inputs.
- Add `sarif-path`, `findings-count`, and `highest-severity` outputs.
- Run the same default pipeline and exit-code contract used by the local CLI.
- Validate SARIF before upload.
- Upload through `github/codeql-action/upload-sarif` inside the composite Action.
- Publish review mode, requested/returned GPT model, reviewed/skipped counts, cache counts, token usage, and truncation state in the Action summary without source snippets.
- Detect forked pull requests without secrets, enable degraded review, and annotate the skipped review clearly.
- Preserve fail-closed GPT behavior for non-fork workflows.
- Add an end-to-end throwaway-repository workflow.
- Preserve one public successful workflow run and its validated SARIF artifact as judge-facing evidence.

### Verification gate

- The Action passes against the clean fixture repository.
- The Action reports and fails at the configured threshold against the vulnerable fixture.
- Forked PR behavior does not fail solely because GPT secrets are unavailable and does not imply review occurred.
- A real SARIF file uploads successfully to a live throwaway repository's Security tab.
- An invalid SARIF artifact blocks upload and returns `3`.
- Action outputs match the uploaded report.
- Action and SARIF summaries distinguish live, replay, and degraded review modes.

## 8. Phase 5 — Polish and judged demo

### Objective

Make the required implementation understandable, repeatable, and reliable under live demonstration.

### Work

- Polish console severity, OWASP, location, evidence, and remediation presentation.
- Ensure JSON and SARIF retain the complete canonical Finding audit trail.
- Add concise operational errors that distinguish target, configuration, and infrastructure failures.
- Reconcile `README.md`, `AGENTS.md`, and `mcp-sentinel-buildplan.md` with the implemented phase numbering, CLI, scope, and contracts in a separate documentation pass.
- Document local installation, Docker requirements, `OPENAI_API_KEY`, target configuration, degraded mode, and Action usage.
- Document the Responses API, `store: false`, requested/returned model IDs, reasoning effort, strict Structured Outputs, batching, telemetry, and replay disclosure.
- Add a README section showing where Codex accelerated implementation, which product/engineering decisions remained human-owned, and how GPT-5.6 changes runtime behavior.
- Record the Codex `/feedback` session ID for the thread containing most core implementation.
- Add an architecture diagram and OWASP mapping table to public-facing documentation where appropriate.
- Prepare the deliberately vulnerable demo repository.
- Finish `sentinel demo`, `sentinel demo --replay-review`, and the `make demo` convenience wrapper.
- Produce a prebuilt wheel containing the CLI, schemas, cassettes, and bundled vulnerable/clean fixtures.
- Test wheel installation through both `pip` and `pipx` without rebuilding from source.
- Generate and check the judge-facing `artifacts/example.sarif` and `artifacts/gpt-ablation.json` artifacts from real commands.
- Publish or preserve a public GitHub Action/Security-tab example that matches the checked-in SARIF artifact.
- Rehearse the full CLI and Action paths.
- Demonstrate multiple deterministic findings and at least one complete static rule → GPT corroboration → prioritized dynamic proof chain.
- Demonstrate a grounded false-positive suppression that remains visible and a replay run that is unmistakably labeled.
- Record a public YouTube demo shorter than three minutes with audio explaining the product, Codex contribution, and GPT-5.6 contribution.
- Prepare the Devpost category, text description, repository/test instructions, supported-platform statement, and code-access settings.
- Confirm the MIT `LICENSE` and all third-party dependency/license obligations are present and accurate.
- Preserve dated commits and Codex session evidence distinguishing submission-period implementation from any prior planning.
- Run the entire CI matrix, dependency audit, offline SARIF validation, and Docker cleanup suite from a clean checkout.

### Verification gate

- A new user can follow the documented quickstart without undocumented setup.
- A judge can install the prebuilt wheel and run `sentinel demo --replay-review` without an OpenAI API key or rebuilding Sentinel.
- A judge with an API key can run the same demo live through GPT-5.6 Sol and see the returned model/usage telemetry.
- The demo command trips every implemented fixture rule and probe expected by the catalog.
- Console, JSON, and SARIF counts and severities agree after deduplication.
- The Security-tab artifact is available before the live demo.
- `artifacts/gpt-ablation.json` is generated from the versioned eval truth set and proves the measured contribution of GPT review and dynamic proof.
- The README accurately distinguishes live, replay, and degraded review and contains the Codex collaboration record and `/feedback` submission instruction.
- The public video is under three minutes, includes audio, and shows a working product consistent with the repository instructions.
- The repository has a valid license and a free judge test path that remains available through the judging period.
- No demo step depends on an external endpoint or live target beyond GPT semantic review.
- All required Phase 0–5 gates pass from a clean checkout.

## 9. Phase 6 — Conditional exploit-confirmation stretch

### Entry condition

Begin only when every Phase 0–5 gate is passing and the judged demo is stable.

### Scope

- Implement `src/sentinel/llm/exploit_confirm.py` only for bundled vulnerable fixtures.
- Generate one context-specific exploit attempt for an eligible finding.
- Execute it within the existing Docker isolation boundary.
- Record evidence and set `confirmed` or `likely_false_positive` through the approved status lifecycle.
- Keep arbitrary user targets, automated patches, and automated pull requests out of this phase.

### Verification gate

- At least one bundled-fixture exploit succeeds reproducibly and records redacted evidence.
- The clean fixture remains unaffected.
- Failure cannot destabilize or alter the required Phase 0–5 demo path.
- No exploit code runs on the host or against a remote endpoint.

## 10. Unscheduled post-v1 and future work

These items are intentionally unscheduled and have no phase number.

### Approved product evolution

- Streamable HTTP support.
- Remote-repository scanning convenience.
- Running-endpoint scanning restricted to Sentinel-launched sandboxes.
- Exploit confirmation generalized beyond bundled fixtures.
- Multi-language analysis.
- Automated patch generation.
- Automated pull-request creation.

### Existing README commitments

- IDE integration for inline findings.
- An expanded dynamic fuzzing corpus for tool-chain abuse.
- Policy-as-code rule authoring.
- Baseline diffing that reports only new findings in pull requests.

### Explicitly outside the required build

- Full SecureMCP Gateway integration.
- SecureMCP Identity or SPIFFE/SPIRE credential brokering.
- Comprehensive coverage of every MCP vulnerability class.
- Publishing the CLI to PyPI.
- Publishing the Action to GitHub Marketplace.

## 11. Gate summary

| Phase | Required outcome | Blocking verification |
|---|---|---|
| 0 | Executable contracts and valid report shell | CLI, schemas, offline SARIF, quality tools pass. |
| 1 | Seven deterministic static rules | Vulnerable/clean fixture matrix and no-execution proof pass. |
| 2 | Required grounded GPT review and probe planning | Structured Outputs, evidence/plan validation, ablation, telemetry, cassettes, and failure modes pass. |
| 3 | Four isolated, GPT-prioritized dynamic probes | Docker security, plan fallback, behavior, merge, timeout, and reaper tests pass. |
| 4 | Composite Action and Security-tab integration | Live throwaway-repository upload passes. |
| 5 | Stable judged deliverable and submission package | Clean-checkout CI, prebuilt wheel, ablation artifacts, documented Codex/GPT usage, and rehearsed live/replay demos pass. |
| 6 | Fixture-only exploit confirmation | Optional and isolated from the required path. |
