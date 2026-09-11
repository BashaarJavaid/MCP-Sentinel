# PortunusMCP Sentinel Roadmap

## 1. Planning frame

This roadmap is ordered by dependency gates, not calendar dates. It assumes one
engineer. Phase IDs are retained for existing release and evidence references;
the execution order below takes precedence over numeric order.

Phases 0–13 are complete. They established the scanner, distribution, and team
workflows. The September 2026 product review identified detection-quality and
adoption gaps that those original gates did not measure. Phases 16–26 address
that review; none is implemented merely by being scheduled here.

Phases 16–20 are complete and accepted, including the independent benchmark
with its recorded detection and execution limitations. **Next work: Phase 22's
benchmark-driven technical improvements; Phase 21 recruitment is deferred.**
Required execution order:
**16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24 → 15**. Each required phase begins
after its predecessor's verification gate passes, except for the explicitly
authorized Phase 22 scope and sequencing exception below. Phase 15 retains existing
publication artifacts but cannot close on distribution evidence alone. Phase
14 remains deferred and optional. Phases 25 and 26 are separate conditional
extensions after Phase 24; neither blocks launch, and deterministic sequence
testing in Phase 26 does not require AI discovery in Phase 25.

**User-authorized sequencing exception:** recruitment is deferred because the
author currently lacks time and available maintainer participants. Phase 22 may
begin bounded technical work selected from Phase 20's measured detection gaps,
starting with path-containment detection and independent vulnerable/fixed cases.
The user subsequently authorized all ten Phase 20 vulnerability families and
all five compatibility areas: imported handlers/schemas; local imports,
aliases/re-exports and bound helpers/methods; cross-file flows; low-level SDK
registration/dispatch; and declared Python/TypeScript workspaces. The approved
technical contract and implementation status are in
[`docs/phase22-technical.md`](docs/phase22-technical.md). Corpus freeze, the exact
tested Git SDK environment, and paid requests require separate concrete packets
and user approval. Pilot-driven prioritization waits for participant feedback.
The user subsequently removed external maintainer pilots as a Phase 22 completion
prerequisite and deferred the full paid benchmark for cost. Current Phase 22
completion uses deterministic, recorded-review, isolated runtime and technical
verification evidence; the unperformed full reviewed comparison is deferred, not
passed. See `artifacts/phase22/completion-scope-v1/decision.json`. Phase 21 remains
incomplete. Author-run evidence does not establish external validation. Resume
pilots when feasible; Phase 24 adoption and Phase 15 launch gates remain unchanged.
After the completed audit, the user authorized bounded offline investigation and
a fix for the replacement detection gap. The five replacement cases are now
exposed regressions; their original frozen measurements remain unchanged. See
`artifacts/phase22/corpus-replacement-v1/exposure-and-fix-authorization.json`.
The SSRF correction and final timing verification are recorded in
`docs/phase22-ssrf-follow-up.md`. The earlier residual-SSRF and casewise timing
waivers were never approved; the current continuation requires the original
complete-batch gate. The exact fresh replacement freeze and bounded Linux execution were subsequently
approved and executed; their failed timing and fresh detection results are retained
separately. The next authorized continuation corrects fetch-mcp and native timing,
with one separately authorized final Linux sequence. Its new fresh freeze and
final human technical acceptance remain explicit checkpoints. Final technical
acceptance remains an explicit checkpoint, never inferred from engineering checks
or permission to continue work.

Historical submission and release records are consolidated in
`docs/hackathon.md`; this file remains the authoritative phase and gate map.

The architecture and implemented contracts are defined in `ARCHITECTURE.md`.
Future phases explicitly schedule changes to those contracts; they do not
silently change current behavior. Update the architecture, schemas, compatibility
policy, and user documentation as part of the phase that implements a contract
change, before claiming the new capability is supported.

### Product direction and review evidence

The initial audience is maintainers and small teams shipping supported MCP
servers, beginning with Python. The product promise is: **catch MCP server
security regressions before release, with actionable source findings and
reproducible evidence for supported runtime checks.** Consumer inventory,
runtime enforcement, and comprehensive agent security remain different scopes.

The review ran 229 passing tests with 83.32% branch-aware coverage and passing
schema checks. Source-only counterexamples nevertheless showed a same-file
helper hiding an execution sink, ineffective validation/authentication/integrity
checks receiving safety exemptions, and missing path-containment and tool-
description poisoning coverage. Local probe checks also showed that the
wrong-type payload can be schema-valid. These are bounded reproductions, not
ecosystem precision/recall measurements or fresh live-model/Docker evidence.
Recreate them as durable tests in the owning phases; do not depend on temporary
review files.

The four-case semantic truth set and zero-finding public walkthrough establish
integration and execution evidence, not general detection effectiveness. Keep
their historical results, but qualify claims using the independent benchmark
and pilot gates below. OWASP mappings classify findings; they do not establish
coverage of all ten categories. GPT currently reviews existing candidates and
cannot recover issues missed by both the static rules and fixed probes.

Primary references for benchmark selection and positioning:

- [Official Git-server path traversal advisory](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-vjqx-cfc4-9h6v)
- [Official Git-server argument injection advisory](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-9xwc-hfwc-8w59)
- [MCP security guidance](https://modelcontextprotocol.io/docs/draft/tutorials/security/security_best_practices)
- [Starlette authentication and permission enforcement](https://starlette.dev/authentication/)
- [Snyk Agent Scan](https://github.com/snyk/agent-scan) and [Cisco MCP Scanner](https://github.com/cisco-ai-defense/mcp-scanner)

Competitor documentation establishes available alternatives, not comparative
accuracy. Need for MCP security does not by itself prove demand for Sentinel or
willingness to pay; Phases 21 and 24 test those assumptions.

### GPT-5.6 API cost-control policy

The production path remains GPT-5.6 Sol through the Responses API. Development
minimizes paid calls without substituting a different model or weakening any
GPT-specific release gate:

- Use hand-built response objects for unit tests of parsing, validation,
  retries, refusals, incomplete responses, merge behavior, and reporting.
- Use checked-in GPT-5.6 cassettes for routine integration tests, local
  development, CI, and the offline judge demo. Replay must exercise the same
  parser, validators, merge logic, and reports as live mode.
- Keep `OPENAI_API_KEY` out of routine test and CI environments. Supplying it
  never implicitly turns an offline test into a paid live test; live checkpoints
  must be selected explicitly.
- Minimize each live request using the already-approved context windows,
  redaction, batching, stable prompt prefixes, cache reuse, and fixture-scoped
  candidate caps. Do not lower the production 500-finding default to disguise
  cost or skip required candidates.
- Record tokens, cache use, requested and returned models, and the dated pricing
  source for every live checkpoint. Stop after the required evidence or cassette
  has been captured; do not repeatedly call the API while debugging host-side
  code that can be tested offline.
- Repeat an accepted live checkpoint only when its production prompt, schema,
  model, request construction, or affected semantic behavior changes, or when
  the checkpoint itself fails. A host-only reporting or sandbox change does not
  invalidate unrelated GPT cassettes.

Paid live calls are limited to these dependency gates:

1. **Phase 2 contract smoke:** after the request and response schema are stable,
   send the smallest representative batch that proves authentication,
   `store: false`, strict Structured Outputs, reasoning effort, returned model,
   usage telemetry, and one grounded valid review.
2. **Phase 2 evaluation and cassette capture:** after all host-side tests pass,
   run the versioned static truth set once at `medium` and once at `low`, capture
   accepted GPT-5.6 responses, and use those responses for subsequent offline
   development and CI.
3. **Phase 3 integrated chain:** after Docker and probe tests pass offline, run
   the smallest live fixture scan that proves static candidate → GPT review →
   prioritized probes → dynamic candidate → GPT review, then capture the new
   dynamic-review responses.
4. **Phase 5 release evidence:** after the clean-checkout and replay gates pass,
   perform one final live end-to-end demo run. Reuse that successful run for the
   ablation, checked-in artifacts, and recorded submission evidence wherever
   their inputs are identical.
5. **Product-quality evaluation (Phases 20, 22, 25, and 26):** before any new
   live evaluation, record the named cases, purpose, model, request/token or
   monetary ceiling, and stopping condition. Run host-side checks first, reuse
   unaffected accepted cassettes, and capture the smallest new evaluation that
   answers the phase's quality question. Optional discovery or model-assisted
   sequences receive separate caps and do not trigger paid calls during normal
   tests or keyless pilots. No automatic paid competitor scans or broad
   repository sweeps are part of these gates.

This schedule is a spending discipline, not permission to claim GPT behavior
from mocks or replay. The applicable live checkpoint must pass before its
dependent phase is complete.

## 2. Delivery definition

The original Phases 0–5 delivery required all of the following. These remain
historical acceptance criteria, not evidence that the new product gates pass:

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

The next product delivery additionally requires corrected safety exemptions and
probe evidence, an explicit offline tier, visible coverage boundaries, an
independent benchmark, maintained regression feedback, and retained pilot use
(Phases 16–24). Existing installations and reports must retain documented
compatibility or receive a tested migration. Launch and optional AI expansion
cannot substitute for these outcomes.

## 3. Phase 0 — Scaffold and contracts

**Status: complete.**

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

**Status: complete.** The seven-rule vulnerable/clean fixture gate, native JSON
schema validation, offline SARIF validation, and local quality gates pass.

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

**Status: complete.** Prompt v3 passes the live contract smoke, medium truth-set
expected-status, grounding, and probe-priority gates. The low-effort comparison
justifies retaining medium as the production default. All accepted captures
replay through the production parser and host validators; the replay demo reviews
all seven static findings, and the generated static ablation records the result.

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
- At the Phase 2 live checkpoints, capture accepted real GPT-5.6 responses and
  replay them as deterministic cassette fixtures; recapture only under the
  cost-control policy above.
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
- The Phase 2 contract smoke proves the real Responses API accepts the strict
  schema and returns the required model, status, and usage fields before Phase 3
  begins.
- The versioned static truth set has one accepted live `medium` run and one
  accepted live `low` run; routine reruns use their checked-in cassettes.
- The ablation includes rules-only, GPT-reviewed, and dynamically confirmed metrics for true/false positives, precision, recall where defined, structured-output validity, evidence grounding, plan validity, latency, tokens, cache behavior, and cost per successful review with auditable pricing metadata.
- The truth set demonstrates at least one corroborated true positive, one grounded visible suppression, one ambiguous `needs_review`, and one correctly prioritized probe.
- `medium` and `low` reasoning effort are compared without changing the production default unless the measured results justify it.

## 6. Phase 3 — Docker dynamic probing

**Status: complete.** The vulnerable fixture produces exactly `SENT-008`
through `SENT-011` under the GPT-prioritized plan, while the clean fixture
produces no dynamic findings. Sandbox isolation, orphan reaping,
infrastructure-failure handling, merge behavior, schema-valid reports, and the
full quality gate pass. The live `phase3-integrated` checkpoint captures and
replays the complete static candidate → GPT review → prioritized Docker probes
→ dynamic candidates → GPT review chain with the required model and telemetry.

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

**Status: complete.** The SHA-pinned composite Action preserves the CLI exit
contract, validates SARIF before upload, publishes aggregate GPT telemetry, and
handles fork events without exposing secrets. A public paired-fixture workflow
proves the clean pass, vulnerable threshold failure, retained artifacts, and 11
visible Security-tab alerts from `SENT-001` through `SENT-011`.

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

### Current status

Phase 5 is **complete**. The repository implementation and automated
verification gates passed, the `v0.1.0` GitHub Release was published with the
tested wheel, `/feedback` was submitted from the primary Codex thread recorded
in `README.md`, and the public YouTube demo and Devpost submission were
completed. Phase 6 is complete and Phase 7 is unblocked.

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
- The README accurately distinguishes live, replay, and degraded review and contains the Codex collaboration and `/feedback` submission record.
- The public video is under three minutes, includes audio, and shows a working product consistent with the repository instructions.
- The repository has a valid license and a free judge test path that remains available through the judging period.
- No demo step depends on an external endpoint or live target beyond GPT semantic review.
- All required Phase 0–5 gates pass from a clean checkout.

## 9. Phase 6 — Package and release readiness

### Objective

Prepare a conflict-free, installable distribution without changing the existing
`sentinel` import package or CLI command.

### Current status

Phase 6 is **complete**. Local macOS verification passed on Python 3.12 and
3.13, and the [cross-platform CI gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33777731624)
passed on Linux, macOS, and Windows with Python 3.10–3.13. The gate included
the zero-exception dependency audit, canonical wheel/sdist build, isolated
pip/pipx/uv installs, package metadata and contents checks, and installed-wheel
Docker replay. Phase 7 is complete.

### Work

- Change the PyPI distribution name to `portunusmcp-sentinel` while retaining
  the `sentinel` import package and the single `sentinel` console command.
- Do not register an `mcp-sentinel` console alias because that name belongs to
  an unrelated PyPI project.
- Add package keywords, classifiers, supported Python versions, and
  Documentation, Changelog, and Issues project URLs.
- Replace exact runtime dependency pins with tested compatible ranges where the
  existing adapters permit them; retain a strict pin only when a verified
  compatibility contract requires it.
- Make Python 3.13 a supported and CI-tested version after identifying and
  resolving its actual dependency blockers.
- Document `pipx install portunusmcp-sentinel` and
  `uv tool install portunusmcp-sentinel` as the primary isolated installs.
- Bump the package to `0.2.0` for the first PyPI release.
- Add `CHANGELOG.md` using Keep a Changelog conventions and document stable rule
  IDs as a compatibility contract.

### Verification gate

- Built wheel and sdist metadata identify the distribution as
  `portunusmcp-sentinel`, while `import sentinel` and the `sentinel` command work.
- No `mcp-sentinel` executable is installed.
- Dependency resolution and wheel smoke tests pass through `pip`, `pipx`, and
  `uv tool install` in clean environments.
- The full quality gate passes on Python 3.10–3.13 across the supported CI
  operating systems.
- The built artifacts report version `0.2.0`, include the schemas and replay
  assets, and match the changelog entry.

## 10. Phase 7 — Trusted PyPI publishing

### Objective

Publish reproducible, attested releases without long-lived PyPI credentials.

### Current status

Phase 7 is **complete**. The signed `v0.2.0` tag's
[Release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33795399096)
passed the complete Phase 6 matrix, published and verified the same wheel and
sdist on [TestPyPI](https://test.pypi.org/project/portunusmcp-sentinel/0.2.0/),
paused for production approval, then published them to
[PyPI](https://pypi.org/project/portunusmcp-sentinel/0.2.0/) with verified PEP
740 attestations. Exact-version pipx and uv installs passed on Linux, macOS,
and Windows with Python 3.10–3.13. No API token or release-please automation was
added. Phase 8 is complete.

### Work

- Configure separate Trusted Publisher records and protected GitHub
  environments for TestPyPI and PyPI.
- Add a tag-triggered release workflow that reuses the existing quality gates.
- Keep build and publish in separate jobs; grant `id-token: write` only to the
  publish job.
- Transfer the exact tested wheel and sdist between jobs as workflow artifacts.
- Pin third-party Actions by immutable commit SHA.
- Publish to TestPyPI first, install the resulting artifacts in clean
  environments, and promote the same release process to PyPI only after that
  gate passes.
- Require manual approval on the production `pypi` environment.
- Preserve PEP 740 attestations generated by Trusted Publishing as release
  provenance.
- Optionally add release-please-style version/changelog automation after the
  required tag-driven path works; this convenience does not gate the phase.

### Verification gate

- A release candidate installs from TestPyPI and passes CLI, schema, SARIF, and
  paired-fixture smoke tests.
- A protected version tag publishes `portunusmcp-sentinel==0.2.0` to PyPI with
  no API token stored in GitHub.
- PyPI displays the expected metadata, project links, wheel, sdist, and digital
  attestations.
- `pipx install portunusmcp-sentinel` and
  `uv tool install portunusmcp-sentinel` produce a working `sentinel` command
  from the public index.

## 11. Phase 8 — GitHub Marketplace distribution

**Status: complete.** The immutable `v1.0.0` release publishes the root Action
under Security and Code quality, the signed `v1` alias resolves to the exact
release commit, and the paired public proof passed with Sentinel `1.0.0`, zero
clean findings, and exactly `SENT-001` through `SENT-011` for the vulnerable
target. See `artifacts/phase8-marketplace-evidence.md`. Phase 9 is unblocked.

### Objective

Make the existing composite Action discoverable and consumable through a stable
major-version reference.

### Work

- Verify that the Action display name is globally unique before drafting the
  Marketplace release; stop for an explicit naming decision if it is not.
- Publish the root `action.yml` through a GitHub Release and accept the
  Marketplace Developer Agreement with account 2FA enabled.
- List the Action under Security and Code quality.
- Maintain a floating `v1` tag for the latest compatible `v1.x.y` Action release.
- Update the Action to install its explicitly pinned, corresponding
  `portunusmcp-sentinel` PyPI release instead of building from its checkout.
- Keep repository-owned workflows and third-party Action dependencies pinned to
  immutable SHAs even though consumer documentation uses the conventional `v1`
  reference.

### Verification gate

- The Marketplace listing is public and links to the correct repository,
  release, branding, and usage documentation.
- A clean external workflow succeeds with
  `uses: BashaarJavaid/MCP-Sentinel@v1`.
- The paired clean/vulnerable Action checks preserve exit codes, validate SARIF,
  upload code-scanning results, and install the documented PyPI version.
- Moving `v1` to a compatible patch or minor release is documented and tested
  without changing an existing release tag.

## 12. Phase 9 — First-run onboarding

**Status: complete.** The
[onboarding gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33816774614)
passed the full quality and installed-wheel matrices, then generated a clean
fixture configuration with `sentinel init` and completed `sentinel scan .` in
Docker without an API key.

### Objective

Turn first use into a two-command setup and make each analysis tier explicit.

### Work

- Replace the missing-key infrastructure message with concise guidance to set
  `OPENAI_API_KEY` or run `--allow-degraded` for visible rules-only candidates.
- Add `sentinel init` using the existing configuration models and framework
  detection to inspect a local Python target and generate commented starter
  `sentinel.target.yaml` and `sentinel.permissions.yaml` files.
- Detect the entry point, supported MCP framework, and dependency manifest
  without importing or executing target code.
- Refuse to overwrite existing configuration files unless the user explicitly
  requests it.
- Document the supported tiers: deterministic rules in degraded mode,
  static-plus-GPT review where API access exists, and dynamic proof where Docker
  exists.

### Verification gate

- `sentinel init` generates valid starter configuration for both supported
  Python fixtures without executing either target.
- Existing configuration is preserved by default.
- `sentinel init && sentinel scan .` reaches analysis on a representative new
  target without undocumented configuration steps.
- A missing API key explains both available next actions, and degraded findings
  remain visible and fail-on eligible.
- Documentation clearly states when Docker and paid GPT access are required.

## 13. Phase 10 — Configurable GPT review endpoint

**Status: complete.** The
[configurable-endpoint CI gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33835113247)
passed the full Linux, macOS, and Windows Python 3.10–3.13 quality matrix,
canonical distribution and isolated wheel checks, and installed-wheel Docker
replay. Compatible `/v1` routing, endpoint trust, provenance, failure handling,
and public-default compatibility are covered without paid API calls.

### Objective

Support approved OpenAI models and OpenAI-compatible organizational endpoints
without weakening review validation or auditability.

### Work

- Move the requested review model and reasoning effort from constants into the
  existing configuration precedence chain while retaining the current defaults.
- Add an explicit base-URL override for OpenAI-compatible endpoints, including
  organizational proxies and compatible Azure OpenAI deployments.
- Document supported authentication and endpoint constraints rather than
  claiming compatibility that has not been tested.
- Continue recording requested and returned models, effort, endpoint mode,
  usage, and review provenance.
- Preserve strict Structured Outputs, redaction, timeouts, retries, caps,
  grounding validation, constrained probe plans, and fail-closed behavior.

### Verification gate

- CLI, environment, project, and default precedence tests cover model, effort,
  and base-URL configuration.
- The default configuration reproduces the accepted GPT-5.6 Sol `medium` path.
- A local compatible test endpoint proves that the override is honored without
  sending fixture code to the public API.
- Unsupported authentication or response behavior fails explicitly and cannot
  be reported as a completed review.
- Report formats preserve the actual returned model and review mode.

## 14. Phase 11 — TypeScript static analysis

**Status: complete.** Local paired-fixture, no-execution, canonical JSON/SARIF,
Python regression, and distribution checks pass. The budget-capped live
TypeScript smoke passed on 2026-09-03 with `gpt-5.6-sol`: `confirmed`, one
grounded evidence reference, and the valid four-probe plan. It used 1,325 input,
542 output, and 289 reasoning tokens (1,867 total) at a recorded cost of
`$0.017462`; the
[accepted replay cassette](src/sentinel/_cassettes/typescript-smoke/manifest.json)
passes production replay. The
[hosted gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33845514399)
passed all 12 quality jobs and all 12 installed-wheel jobs across Linux, macOS,
Windows, and Python 3.10–3.13, plus the canonical distribution build and
installed-wheel Docker replay.

### Objective

Scan TypeScript MCP servers statically without waiting for a Node dynamic
sandbox.

### Work

- Extend target-language and manifest detection to TypeScript MCP repositories.
- Port `SENT-001` through `SENT-007` to TypeScript without changing their stable
  meanings, OWASP mappings, or canonical Finding shape.
- Reuse the existing Semgrep adapter and add only the language-specific parsing
  needed outside Semgrep.
- Add paired vulnerable and clean TypeScript MCP fixtures for every static rule.
- Keep static analysis non-executing and report Node dynamic probing as
  unsupported rather than launching a target outside the approved sandbox.
- Document TypeScript support as static-only.

### Verification gate

- Every static rule triggers its vulnerable TypeScript fixture case and passes
  its clean and false-positive controls.
- Tests prove TypeScript modules, package scripts, and dependencies are never
  executed or installed during static analysis.
- `sentinel scan <typescript-target> --static-only` emits valid console, JSON,
  and SARIF from the canonical Finding model.
- Python fixture behavior and rule IDs remain unchanged.
- A normal TypeScript scan fails clearly before dynamic execution and directs
  the user to the supported static-only path.

## 15. Phase 12 — Team adoption workflows

**Status: complete.** Native JSON 1.4.0, baseline matching,
Python/TypeScript inline suppression, Action input/metrics, and the public
pre-commit hook passed local and hosted gates. The signed
[`v1.2.0` release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.2.0)
was published through the trusted
[release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33895746398),
and the external [exact-tag proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33897900585)
and signed [`v1` alias proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33898189505)
passed. Full hashes, SARIF links, costs, and tag evidence are recorded in
[`artifacts/phase12-adoption-evidence.md`](artifacts/phase12-adoption-evidence.md).

### Objective

Let existing repositories adopt Sentinel incrementally without hiding accepted
risk.

### Work

- Add `--baseline <report.json>` so existing findings remain visible while only
  findings absent from the baseline affect the fail threshold.
- Define stable finding matching from existing canonical fields without changing
  rule IDs and bump the additive native report schema to 1.4.0.
- Add reason-bearing inline suppressions using
  `# sentinel: ignore[SENT-005] reason=...` alongside the existing `SENT-005`
  allowlist.
- Preserve inline-suppressed findings and their justification in reports instead
  of silently deleting them.
- Add `.pre-commit-hooks.yaml` for the static-only scan path.

### Verification gate

- Baseline tests prove unchanged findings do not newly fail a pull request, new
  findings do, and resolved findings disappear from the current report.
- Malformed, unknown-rule, or reasonless inline suppressions fail validation or
  remain ineffective with a clear diagnostic.
- Inline suppression cannot suppress a different rule or file and remains
  auditable in console, JSON, and SARIF.
- The pre-commit hook installs from the public package and runs the supported
  static-only path against the paired fixtures.
- Existing allowlists, fail thresholds, and paired fixtures remain compatible.

## 16. Phase 13 — Public documentation and maintenance

**Status: complete.** The
[documentation workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33908643137)
passed its strict build, Pages deployment, and live page/anchor smoke at the
[public site](https://bashaarjavaid.github.io/MCP-Sentinel/). The hosted
contribution templates, bounded Dependabot updates, vulnerability alerts, and
automated security updates are enabled and verified.

### Objective

Make the public repository useful to adopters and safe for outside contributors
to change.

### Work

- Reposition `README.md` around the one-command install, a 30-second scan,
  supported analysis tiers, rule table, and Marketplace Action example.
- Move judge-specific evidence, wheel digests, demo instructions, and Codex
  submission records to `docs/hackathon.md` without losing them.
- Reconcile `README.md`, `AGENTS.md`, the build plan, architecture docs, and the
  remaining documentation from SecureMCP branding to the established
  PortunusMCP product family.
- Add `CONTRIBUTING.md` covering stable rule IDs, the canonical Finding shape,
  paired fixtures, static no-execution guarantees, dynamic isolation, and the
  required quality gates.
- Add issue templates for false positives and new rule proposals plus a pull
  request template that checks the same contributor contracts.
- Enable Dependabot for GitHub Actions and Python dependencies with reviewable,
  bounded update pull requests.
- Publish a MkDocs Material site through GitHub Pages with installation,
  configuration, rule-catalog, SARIF, Action, and contribution references.

### Verification gate

- A first-time user can reach a successful scan from the README without using
  hackathon-only instructions.
- All public docs consistently identify Sentinel as part of PortunusMCP and use
  the `portunusmcp-sentinel` distribution name with the `sentinel` command.
- Contributor templates capture the information required to reproduce a false
  positive or review a new stable rule.
- Dependabot opens valid, bounded update pull requests for both configured
  ecosystems.
- The public docs site builds without warnings, deploys through pinned Actions,
  and exposes a linkable page for every rule ID.

## 17. Phase 14 — Conditional exploit-confirmation stretch

**Status: deferred, optional.** Retained under its original ID for historical
references; this fixture demonstration is not the next product milestone.

### Entry condition

Reconsider only after Phase 24, when a concrete validation need justifies a
fixture-only generated exploit. This phase never blocks Phase 15 or Phases
16–26. General sequence testing belongs to Phase 26.

### Scope

- Implement `src/sentinel/llm/exploit_confirm.py` only for bundled vulnerable fixtures.
- Generate one context-specific exploit attempt for an eligible finding.
- Execute it within the existing Docker isolation boundary.
- Record observed effects through the canonical evidence/status contract. A
  failed exploit attempt is inconclusive, not proof of a false positive; revise
  the historical stretch contract before implementation if necessary.
- Keep arbitrary user targets, automated patches, and automated pull requests out of this phase.

### Verification gate

- At least one bundled-fixture exploit succeeds reproducibly and records redacted evidence.
- The clean fixture remains unaffected.
- Failure cannot destabilize or alter the required Phase 0–13 product path.
- No exploit code runs on the host or against a remote endpoint.

## 18. Phase 15 — Product launch

**Status: pending; completion depends on Phase 24.** Retain the public package,
Action, walkthrough, and `artifacts/phase15/` evidence already produced. Do not
renumber or recreate historical releases to satisfy the revised launch gate.

### Objective

Make the released product discoverable with claims backed by public evidence.

### Work

- Lead launch material with independently reproduced findings, concrete repairs,
  supported coverage, and maintainer outcomes from Phases 20–24. Present dynamic
  proof only where observed effects justify it; explain SARIF integration and
  OWASP classification without promising comprehensive security.
- Reuse the existing sub-three-minute YouTube demo instead of rerecording it
  unless the released product behavior has materially changed.
- Publish a short technical walkthrough that scans a real public MCP repository
  locally and discloses the target version, configuration, and reproducible
  findings without probing a live endpoint. Preserve the existing zero-finding
  walkthrough as installation evidence and add a vulnerable/fixed example that
  demonstrates actionable value, respecting disclosure and maintainer consent.
- Submit Sentinel to the relevant `awesome-mcp-servers` and MCP security lists.
- Publish concise announcements to Show HN, `r/mcp`, and the MCP Discord.
- Prepare concrete list submissions and announcements for review. Public posts,
  submissions, and messages require the user's explicit authorization; planning
  this phase is not authorization to contact others.
- Link the PyPI project, Marketplace listing, documentation site, source,
  changelog, demo, and security policy from the launch material.

### Verification gate

- The PyPI project and Marketplace listing are public and installable.
- Phase 24's retained-use gate passes, and every detection or accuracy claim
  links to applicable benchmark or maintainer evidence.
- The README begins with the working one-command install and links to the public
  documentation and Action.
- The list submissions are merged and the announcement posts are publicly
  accessible.
- The walkthrough is reproducible from a named public target revision and makes
  no claim unsupported by the generated report.
- Launch links resolve, and the reused demo is clearly labeled if its displayed
  version predates the product release.

## 19. Phase 16 — Static detection correctness

**Status: complete.** Local verification passed and the user authorized committing
and pushing the completed implementation to `main`.
Depends on completed Phase 13. Phase 17 is also complete.

### Objective

Correct false safety exemptions and preserve detection through ordinary source
refactoring before adding broader threat classes.

### Work

- Reproduce the direct-tool `eval` positive control and the same-file helper
  miss. Trace supported tool inputs through local helpers using existing engine
  capabilities or bounded analysis; document unresolved flows explicitly.
- Make `SENT-003` validation exemptions refer to the actual consumed inputs and
  a check that executes before use. An unrelated `.validate()` call is not
  sufficient evidence; inspect equivalent TypeScript behavior.
- Make `SENT-006` distinguish middleware installation from enforced identity
  checks and rejection. An authentication class name, unrelated application, or
  bypassed branch cannot exempt an unprotected route.
- Make `SENT-007` require verification against a trusted value and enforcement
  of its result. Computing a digest or calling an unrelated verifier does not
  establish manifest integrity.
- Audit equivalent safety exemptions in both languages, including configured
  prompt sanitizers; never claim text sanitization guarantees injection safety.
- Preserve rule meanings and IDs. Keep uncertain candidates reviewable instead
  of declaring them safe, and retain valid framework/custom-validator controls.

### Verification gate

- Each reproduced unsafe exemption has a failing-before/passing-after check and
  a corresponding safe control. Direct and local-helper execution flows are
  detected without executing target code.
- Negative controls cover unrelated checks, ignored verification results, and
  non-enforcing branches; legitimate validation and authentication stay exempt.
- Python/TypeScript paired fixtures, existing review replay, canonical schemas,
  and SARIF validation pass, or affected contracts/cassettes are explicitly
  updated with justified compatibility changes.

Local verification on macOS/Python 3.12 passed **426 tests** with **85.83%**
branch-aware coverage, lint, formatting, type checks, canonical schemas, retained
SARIF artifacts, strict documentation build, and built-wheel fixture/SARIF
checks. The historical four-candidate review inputs are frozen separately from
the corrected detector's three current candidates; existing captures and
request fingerprints are preserved. See the
[Phase 16 verification record](docs/phase16-verification.md) for failing-before
evidence, supported boundaries, compatibility details, and the final review.
No release, hosted CI run, or new live model evaluation is claimed.

## 20. Phase 17 — Dynamic probe correctness and evidence

**Status: complete.** Depends on completed Phase 16.

The user accepted Checkpoints 1–3 and authorized Checkpoint 4. Baselines,
probe conditions, sandbox evidence, native 1.5.0 outcomes, proof-preserving review,
precise merging, and baseline-v2 migration are implemented locally. The ordinary/coverage, Docker, and distribution gates passed locally. The final
current-pipeline replay and the approved single runtime-review refresh passed.
All required local verification passed, and the user accepted the final checkpoint.
Phase 17 is complete. See
[`docs/phase17-verification.md`](docs/phase17-verification.md) for failing-before
evidence, safe controls, historical input preservation, and the four approval
checkpoints. The implementation contract is in `ARCHITECTURE.md`, section 10.

### Objective

Ensure a probe demonstrates the condition it reports and distinguish observed
vulnerability evidence from accepted input or an inconclusive attempt.

### Work

- Establish a valid baseline request for the selected tool before interpreting
  an adversarial request; report missing prerequisites as inconclusive.
- Validate malformed probe arguments against the runtime schema locally. Select
  a genuinely invalid type or omit a required field; support object schemas
  without treating a valid object as a wrong-type payload.
- Require an explicit size-policy breach or measured resource failure for
  oversized-input findings. Successful large-input processing alone is not
  confirmed exploitation; separate baseline slowness from probe-induced failure.
- Keep canary side effects distinct from protocol success. Review may interpret
  evidence but must not silently negate a host-observed security violation.
- Document that `SENT-008` tests tool-name grants, not per-tool path/network
  containment. A permissions sidecar declares expectations, not enforcement.
- Introduce explicit tested, unsupported, untested, and inconclusive outcomes
  through the canonical report contract. Revise misleading proof/severity
  semantics without repurposing stable IDs, and version migrations as needed.
- Preserve network isolation, resource limits, credential boundaries, fresh
  probe sessions, cleanup, and visible infrastructure failures.

### Verification gate

- An object-typed safe tool does not generate a malformed-input finding for a
  schema-valid object; the unsafe counterpart processes a verified invalid input.
- A legitimate large-document tool is not labeled exploited merely for accepting
  the payload. A controlled resource-policy violation records measurable proof.
- Live Docker checks on local vulnerable/safe fixtures verify baselines, canary
  behavior, inconclusive prerequisites, failure reporting, and cleanup.
- Console, JSON, SARIF, review replay, and exit policy consistently distinguish
  observed proof from review judgment and incomplete testing.

## 21. Phase 18 — Explicit offline mode and first-use workflow

**Status: complete.** Implementation, local/hosted verification, and final user
acceptance passed. Accepted on 2026-09-06 (UTC), following completed Phase 17.

The agreed interface is `--rules-only/--no-rules-only`, `[scanner].rules_only`,
and `SENTINEL_RULES_ONLY` (default false). All 27 final-commit CI jobs and the
documentation build passed. Release 1.3.0 is published and verified on PyPI and
GitHub, with both Action tags verified; see
[Phase 18 verification](docs/phase18-verification.md) for retained release evidence.

### Objective

Provide a predictable first scan with no model calls, Docker, or source upload,
and make deeper analysis a deliberate choice.

### Work

- Add an explicit rules-only mode using the existing pipeline. Choose and
  document its CLI/configuration interface in this phase; `--allow-degraded`
  remains a fallback policy and must not masquerade as a review-disable switch.
- Guarantee that the offline mode does not construct a model client, use a
  review cache as if review ran, or invoke Docker, even when API credentials or
  endpoint overrides exist in the environment. Keep findings fail-on eligible.
- Expose the same deliberate mode in the Action for ordinary and fork PRs and
  in pre-commit. Preserve fork secret restrictions and explicit upload behavior.
- Align `init`, README, CLI help, and missing-prerequisite guidance with the
  simplest successful scan. Static use must not require launch configuration.
- Explain source transmission, model requirements, costs, and runtime execution
  for optional tiers; preserve the existing configurable endpoint support.

### Verification gate

- Tests with absent and dummy-present credentials prove zero model/network and
  Docker calls in offline mode; review-enabled modes retain their contracts.
- Fresh supported Python and TypeScript targets reach a completed first scan
  from documented instructions without undocumented setup or target execution.
- Keyless ordinary-PR and fork-PR Action tests preserve findings and exit codes;
  existing reviewed workflows remain compatible or receive migration guidance.

## 22. Phase 19 — Coverage reporting and actionable findings

**Status: complete; final gate accepted on 2026-09-06.** Depends on Phase 18.
[PR #19](https://github.com/BashaarJavaid/MCP-Sentinel/pull/19) merged as
`ac3e36af4cf082e8c064acf996c46702f714b431`. The
[verification record](docs/phase19-verification.md) retains the exact tested
commits, passing local and hosted gates, and coverage limitations.

### Objective

Let maintainers understand what was examined, what remains unknown, and what
change a finding calls for.

### Work

- Report recognized tools/handlers, unsupported registrations and imported
  implementations, unresolved flows, skipped rules, and attempted tool/field
  probes. Mark unknown discovery totals honestly rather than inventing coverage.
- Distinguish successful scan execution from security assurance. Zero candidates
  means no static model review occurred; show that clearly in all output modes.
- Display decisive bounded evidence and a concrete repair direction by default;
  keep extended provenance and model reasoning in verbose/machine output.
- Distinguish static suspicion, model corroboration, dynamic observation, and
  confirmed security effects without hiding abstentions or suppressed evidence.
- Document the limits of TypeScript recognition, sidecar permissions, and the
  current four-attempt campaign. Keep baselines/suppressions auditable and
  provide explicit schema compatibility for added coverage fields.

### Verification gate

- A partially recognized server reports detected and unresolved handlers; a
  zero-finding scan cannot imply that unrecognized handlers were inspected.
- Multi-tool fixtures disclose exactly which tools/fields were probed and which
  were not; unknown counts remain unknown.
- Representative findings include location, decisive evidence, and an actionable
  remediation in default console output; equivalent JSON/SARIF fields validate.
- Empty review, explicit offline, degraded, cached, and live review states remain
  distinguishable. Baseline and suppression regression checks pass.

## 23. Phase 20 — Independent detection benchmark

**Status: complete and accepted on 2026-09-07 (UTC).** Depends on Phase 19.
Checkpoint 1 was approved on 2026-09-06. The frozen corpus, independent review,
deterministic/comparator measurements and runtime prerequisite failures are
retained in [Phase 20 verification](docs/phase20-verification.md). The separately
versioned [completion measurement](docs/phase20-completion-v2.md) retains all 35
accepted static captures after the approved validator correction and resumption;
the four earlier failed attempts remain in its cumulative accounting. Execution
limitations remain measured outcomes. The user authorized acceptance, merge,
documentation publication, and removal of the merged task branches. PRs #20
and #21 are merged into `main`; the [acceptance record](docs/phase20-acceptance.md)
binds the evidence and passing checks. No detection-accuracy threshold was added.

### Objective

Measure real detection effectiveness separately from implementation coverage,
fixture demonstrations, and successful installation.

### Work

- Build a versioned corpus with at least ten independently sourced
  vulnerable/fixed pairs across at least five repositories, plus safe controls
  and structural mutations (helpers, aliases, imports, renamed functions).
- Pin revisions, provenance, licenses, expected security conditions, language,
  prerequisites, and applicable analysis tiers. Include known path/argument
  injection cases and record unsupported cases instead of discarding them.
- Separate development and held-out cases before tuning rules or prompts;
  historical public examples alone cannot establish absence of model exposure.
- Compare deterministic Sentinel and GPT-reviewed Sentinel on identical inputs.
  Compare relevant Semgrep configurations and Snyk/Cisco capabilities only where
  their inputs and scope are comparable, recording versions/configuration.
- Publish per-case misses, false alarms, abstentions, incorrect GPT suppressions,
  dynamic confirmations, completion rate, latency, and review cost. Separate
  candidate recall from reviewed recall and report denominators/support coverage.
- Preserve the existing four-case ablation and zero-finding walkthrough with
  their limited interpretation. Do not extrapolate their perfect small-sample
  metrics to production or claim unrun competitor superiority.

### Verification gate

- A documented command reproduces deterministic results offline from retained
  inputs; model replay is labeled and traceable to budgeted live captures.
- An independently checked label manifest and held-out split accompany the
  report; every case has an outcome, including unsupported/inconclusive cases.
- Both Sentinel tiers have measured results. Competitor comparisons are either
  reproducible on applicable cases or explicitly marked unmeasured with reasons.
- Publish the initial baseline even if detection is poor. Passing this phase
  means the measurement is trustworthy, not that an accuracy target was met;
  Phase 22 owns improvements and Phase 24 owns adoption validation.

## 24. Phase 21 — Maintainer pilot and problem validation

**Status: deferred; verification gate unmet.** Depends on Phase 20. Recruitment
will resume when the author has time and access to participants; the sequencing
exception in §1 permits Phase 22's benchmark-driven technical work meanwhile.

### Objective

Test whether supported-server maintainers have a recurring problem Sentinel
helps solve and identify the obstacles to voluntary CI adoption.

### Work

- Prepare a pilot for five external maintainers/teams with source ownership,
  starting with supported Python servers. Prepare invitations for user review;
  contact participants only with explicit authorization.
- Ask about their last security issue, existing checks, findings worth fixing,
  and reasons they would remove a scanner from CI. Record competing workflows.
- Observe install-to-first-result time, need for assistance, scan completion,
  alert comprehension, accepted/rejected findings, and desired integrations.
- Use explicit offline scans by default. Source sharing, paid review, and public
  attribution require deliberate participant choices; no automatic telemetry.
- Rank compatibility and coverage blockers by observed impact. Separate pilot
  enrollment and learning here from the 30-day retention gate in Phase 24.

### Verification gate

- Five external pilot participants have attempted their own repository workflow;
  retain consented, redacted observations, including unsuccessful attempts.
- Publish an internal decision record identifying recurring needs, useful
  findings, and the highest-impact blocker, or evidence that the current audience
  does not need the product. Do not substitute stars/downloads for this evidence.
- Select a bounded Phase 22 scope and define its expected adoption improvement
  before implementing it. A lack of demand triggers a positioning revision,
  not automatic feature expansion or a fabricated success gate.

## 25. Phase 22 — MCP coverage and compatibility expansion

### Current v19 timeout policy

The user approved a uniform **120-second performance target / 300-second static
maximum** with “okay go ahead with this.” The implementation changes the shared
static deadline and the TypeScript parser's remaining-budget handling, preserves
shorter caller deadlines, and checks final coverage/report assembly. It makes no
speedup claim and changes no detector rules, model budget or dynamic budget.

The original 15/25 Linux result, ten Meta timeouts and skipped historical pair
remain preserved. The 120-second hard completion requirement is prospectively
revised; future assessments must separate completion within 120 seconds from
completion using extended time up to 300 seconds. Phase 22 remains incomplete.
Engineering verification is pending on this candidate; no new corpus run, full
Linux retry, fresh evaluation or paid call is authorized. A four-observation
Linux diagnostic proposal will bind the frozen candidate before approval.

[Static timing policy](docs/phase22-timeout-policy.md)

### Historical v18 throughput probe at `0b71a29`

The approved Stage 0 synthetic throughput probe is complete at `0b71a29`.
Run **34536965288** completed **12/12 observations** in an 88-second job;
all checksums match, all children were ready before the shared monotonic start,
and every child was reaped. No scanner or corpus input executed in the probe.

Median throughput relative to one process is **2.029× at three processes,
2.136× at four, and 2.125× at six**. Four processes add only **5.25%** over
three; six add **4.71%**. The runner reports four vCPUs, two cores and two
threads per core, with Python 3.12.14. The prospective **E3 ≥ 2.7 premise
fails**. This result does not support proceeding to the proposed partitioning
experiment; it is not proof that all scanner parallelism is ineffective.
See `v18-scaling-assessment.json` and its retained raw observations.

**One dispatch consumed; zero scanner runs, optimization attempts or paid model
calls.** Stage 1 and partitioning remain unapproved. The normal CI jobs are
structurally unchanged, but the optional workflow changed, ending workflow
equality to `592a9cd`. Fresh CI **34536886816** verifies all 29 normal jobs;
all 12 suites pass **2,183 tests / 36 skipped**. Docs **34536886750** pass.
Scanner/test/package bytes remain identical to `592a9cd`; prior local checks,
production replay and Git compatibility retain their executed sources, and the
three exposed SSRF gates retain measured `2ac39aa`. Initial probe lint issues
and an immediate post-push PR-readback assertion are preserved with corrections.

**Phase 22 remains incomplete.** The retained Linux scanner result is still
15/25 development complete, ten Meta timeouts and both historical batches
skipped. No current-source full timing pass, fresh evaluation, scope waiver or
final human acceptance is inferred. Further source-design work may investigate
reducing repeated analysis, but no safe reuse design or new experiment is
established here. Pilots/full paid benchmark remain deferred, Phase 21 incomplete,
and Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v17 diagnostic at `127763c`

The approved whole-worker sampling scope is complete at `127763c`:
**one Meta operator input**, **69.906s native / 71.578s outer**, 49 findings,
full ordered baseline equivalence after established volatile exclusions and valid
native JSON/SARIF. Four final snapshots restore timer/signal state. The sampler
changes no scanner methods and records no locals or target values.

Active workers retain 4,220 / 5,093 / 4,903 samples (SENT-012/015/016).
Shared merge inclusive shares are 24.81% / 19.18% / 22.58%; expression leaf
shares are 11.66% / 15.92% / 14.28%, mostly at function entry. Caller shares
overlap, signal delivery biases attribution, and no share is wholly removable
cost. **No safe larger optimization or native speedup is established.** See
`v17-sampling-assessment.json` and the source review in `v17-timing-disposition.json`.

The one-profile budget is closed: **zero optimization attempts, additional native
observations, comparator runs, full retries or paid calls**. No scanner/test code
changed. Existing local and 12 hosted suites retain 2,183 passed / 36 skipped,
29 normal jobs and docs, replay and Git compatibility at actual `592a9cd`.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.
The read-only cleanup check initially encountered sandbox Docker permission;
the authorized recheck passed and both records are retained.

**Phase 22 remains incomplete.** The Linux result remains 15/25 development
complete, ten Meta timeouts and both historical batches skipped. Retain the
timing gate; no scope revision, fresh evaluation or final acceptance is inferred.
Further performance experiments need a justified bounded proposal and approval;
this profile does not justify another speculative micro-optimization. Any timing
scope revision needs an explicit user decision and would still require fresh
evaluation and final human acceptance. Pilots/full paid benchmark remain deferred,
Phase 21 incomplete, and Phase 24/15 unchanged. No merge, release or next phase.

### Historical v16 diagnostic at `46b8786`

The user approved `v15-next-combine-proposal.json`; the exact receipt is
`v16-combine-authorization.json`. Its one Meta operator diagnostic completed in
**81.271s** (**82.947s** including measurement setup/finalization). The full
ordered report matches the retained native baseline after established volatile
exclusions. Native JSON/SARIF validate, all four workers have final snapshots,
and 24 synthetic comparisons preserve all Value fields, keys and cache behavior.

The prospective predicate **fails in all three active workers**. Eligible generic
combinations are frequent (83.72%, 85.54%, 84.47%), but their body CPU shares are
only **7.81% SENT-012, 5.34% SENT-015 and 6.81% SENT-016**, below the required
**10% in each worker**. Timing excludes classification counters but includes field
reductions/helpers and construction; it is instrumented attribution, not wholly
removable cost or a native gain. See `v16-combine-assessment.json`.

The stopping condition was enforced before optimization. **One profile used,
zero optimization attempts, zero native performance observations and zero exposed
regression observations.** All 12 performance and 30 conditional SSRF observations
are cancelled; no unused maximum remains open. No scanner/test code changed and
no reversion was needed. Zero paid calls.

Source/test/workflow/package inputs at diagnostic `46b8786` equal verified
`592a9cd`. The existing local and 12 hosted suites each retain 2,183 passed and
36 skipped; 29 normal jobs and docs, production replay and Git compatibility
retain their actual executed sources. No new full suite or hosted pass is claimed.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.

The next `v16-next-worker-sampling-proposal.json` is **unapproved**: one
120-second CPU sampling profile of the same Meta operator input, at most 100Hz
per worker, zero optimizations or additional native/comparator observations and
zero paid calls. It seeks a larger whole-worker CPU concentration before another
code proposal. No further measurement, full Linux retry or fresh evaluation is
inferred. Timing/fresh evaluation/final acceptance remain unmet; Phase 22 remains
incomplete. Pilots/full paid benchmark stay deferred, Phase 21 incomplete and
Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v15 diagnostic at `77ea21f`

The user's “okay go ahead” approved the single merge diagnostic in
`v14-next-merge-diagnostic-proposal.json`; `v15-merge-authorization.json` records
that decision. The sole Meta operator profile completed in **88.533s**
(**90.084s** including measurement setup/finalization), below 120 seconds.
All four workers have final snapshots. Its full ordered report matches the
retained native baseline after only established volatile exclusions; native JSON
and SARIF validate. The revised synthetic control passes 24 state comparisons.
The initial control-coverage assertion and documentation-binding check failures
are preserved with their corrections. No scanner code changed or optimization
was attempted. The one-profile budget is closed; zero paid calls.

Shared multi-branch value processing accounts for **17.8–21.3 instrumented
CPU-seconds** per active worker. About **85% of 19.01 million key visits** reuse
existing values. Those counts do not imply that reuse consumes 85% of the time:
the block also includes nested combining, lookups, equality and instrumentation.
URL pre-processing adds 3.79 CPU-seconds. Timings overlap where explicitly marked
and include instrumentation overhead; this is not a native performance gain.
See `v15-merge-assessment.json` and `v15-combine-source-review.json`.

Code/test/workflow/package inputs at measured `77ea21f` equal verified `592a9cd`.
The existing local and 12 hosted suites each retain 2,183 passed/36 skipped,
29 normal jobs and docs passed, production replay and Git compatibility, all at
their actual executed source. No repeated full suite or new hosted pass is
claimed. All three exposed SSRF gates remain source-compatible at `2ac39aa`.

The next `v15-next-combine-proposal.json` is **unapproved**: one counter profile,
one conditional shortcut using the existing two-value combination, up to
12 native performance observations and 30 conditional exposed regressions,
120 seconds each, zero paid calls. Its diagnostic threshold must pass before
any optimization; unused maxima close on failure. No new measurement is inferred.
Full Linux timing, fresh evaluation and final human acceptance remain unmet.
Phase 22 remains incomplete; pilots/full paid benchmark stay deferred, Phase 21
incomplete and Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v14 verification at `592a9cd`

Phase 22 remains incomplete. The user's “go ahead” approved the exact helper-fact
proposal in `v13-next-performance-proposal.json`; the new receipt is
`v14-performance-authorization.json`. Its one counter profile completed and
observed 3,402,980 empty-fact visits among 3,422,804 binding visits (99.42%).
One ordered-pass optimization was attempted at `e57ce95` and reverted in
`a7d7de0`. Scanner bytes again equal measured `2ac39aa` and delivered `424c443`.
The new semantic regression is retained; no detector behavior change remains.

The first operator candidate took 77.556s and 195.041848 child CPU-seconds,
exceeding baseline maxima of 75.134s and 188.048785 CPU-seconds. That irrecoverably
fails the prospectively approved per-observation retention rule. Four candidate
attempts had started when the queue was stopped: three completed, and the active
Atlassian repeat ended without a completion record. It is retained as interrupted,
not completed or timed out. Two remaining performance observations were cancelled;
the 30 conditional SSRF observations were never activated. Total usage is one
completed counter profile and ten native attempts (nine complete, one interrupted).
All ten completed ordered reports, including the profile, match their baselines.
No complete candidate pair or median performance gain is claimed. The failed
lint/format checks, queue termination, partial files and all original evidence
remain preserved. See `v14-performance-disposition.json` and
`v14-queue-stop-outcome.json` under integration evidence.

All three exposed SSRF families retain their passing v13 gates at `2ac39aa`:
five inputs twice per family, two vulnerable matches and zero matching negative
alerts per batch. Current scanner/harness bytes are identical; these results keep
their original measured revision. SearXNG's broader URL candidates and unresolved
MCP dispatch remain visible. Original misses and source assessments are preserved.

Final local and all 12 hosted quality suites pass **2,183 tests, 36 skips and
no expected failures** at corrected `592a9cd`. Local branch coverage is
**89.66%**; hosted coverage is **89.65–89.68%**. All 29 normal jobs and
docs pass ([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818910),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818938)).
Wheel/sdist source members match actual Git blobs; all 12 wheel combinations,
Docker replay, network isolation, dependencies and hooks pass. Configured strict
mypy checks all 146 files; Ruff/format, lock, schemas, notices and offline
artifacts pass. Both approved production requests regenerate and checked-replay
without new paid calls. The approved Git runtime/image bindings match; its
13 campaigns remain incomplete (312 tested, 728 remaining).

The candidate's 1,034 affected tests and semantic before/after control passed.
Initial `12748e4` CI failed all 12 quality jobs because its source-only local mypy
check missed a required test-helper annotation. The annotation is corrected;
initial failed/cancelled CI and the superseded local suite interrupted after
365 passing tests are retained. Detector source and measurements are unchanged.
The current 89-row audit records 70 passed, two explicitly user-deferred and
17 unresolved, with current test/evidence bindings. Seven additional v14 scope
requirements are mapped separately: six passed and the performance-retention
requirement remains unresolved.

The retained full Linux gate still fails at `7555a9d`: 15/25 complete, ten Meta
timeouts and both historical batches skipped. No further optimization, profile,
native/comparator measurement, full Linux retry, runner/deadline waiver or fresh
freeze/evaluation is authorized by unused maxima. The prepared `v14-next-merge-diagnostic-proposal.json` requests only one
120-second merge diagnostic on the named Meta input, with no optimization or
additional native/comparator run; it is unapproved. A new measurement scope
requires separate approval. Timing, fresh evaluation and final human
acceptance remain unmet; final acceptance is not requested. Zero paid calls.
Pilots and the paid benchmark remain deferred; Phase 21 is incomplete and
Phase 24/15 are unchanged. No merge, release, outreach or next phase.

### Historical v13 continuation at `2ac39aa`

Phase 22 remains incomplete. At scanner `2ac39aa` (source bytes equal the
SearXNG correction `523320f`), all three exposed SSRF families pass their native
repeat gates. Each family completes five inputs twice, detects both correlated
vulnerable variants and has zero condition-matched fixed/control alerts.
SearXNG takes at most 12.821s per input, fetch-mcp 5.104s and open-webSearch
65.265s. Complete ordered repeats agree except recorded volatile fields;
JSON/SARIF and source assessments pass.

The shared correction keeps TypeScript receiver invalidation local to mutually
exclusive `if` arms, then conservatively unions possible invalidations at the
join. An HTTP-arm unknown `process` effect no longer contaminates ordinary
stdio startup. No callback or unknown function is exempted. SearXNG's fixed
sources now retain the native default-loopback qualification; their broader
URL candidates and unresolved MCP dispatch remain visible. Its 23 unmatched
scorer keys per batch (20 prior HTTP candidates and three qualified negative-source
URL candidates) are all separately source-assessed. Original frozen native and
comparator 0/2 results remain unchanged; these are exposed regressions, not fresh
generalization or runtime proof.

The separately approved immutable-Value experiment used one optimization attempt,
two counter profiles and all 12 native observations. Ordered native reports all
match, but Meta operator median wall time increased 4.58% and child CPU 1.31%.
Atlassian improved 16.70% in median wall time; Meta image improved 5.35% in wall
but only 1.64% in CPU. These mixed results fail the retention rule. The
optimization at `de2a02f` is reverted in `2ac39aa`; the test, original commit,
profiles, deadline failures and all results are retained. No full Linux retry
occurred. The retained `7555a9d` Linux result still completes 15/25, with ten Meta
timeouts and both historical batches skipped.

Final-source local and all 12 hosted quality suites pass **2,182 tests, 36 skips
and no expected failures**. Local branch coverage is **89.66%**; hosted coverage
is **89.65–89.68%**. All 29 normal jobs and docs pass at `1be0650`, whose
code/test/workflow/package inputs equal measured `2ac39aa`
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664451),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664440)). Actual
wheel/sdist source members match Git. Ruff/format, strict mypy, lock, schemas,
notices, offline artifacts, dependencies, wheel smoke, Docker replay, isolation
and hook checks pass. Both approved production requests regenerate and replay
without new paid calls. The exact approved Git image/runtime bindings match;
its 13 campaigns remain incomplete (312 tested, 728 remaining).
See integration `v13-searxng-assessment/packet.json`,
`v13-exposed-assessment/packet.json`, `v13-performance-disposition.json` and
`v13-performance-revert-receipt.json`. The current SearXNG receipt consumes
31 of its maximum 32 executions: one fixed trace and 30 final observations;
the optional vulnerable trace was not needed. Both approved scopes have reached
their stopping conditions. The separate `v13-next-performance-proposal.json`
is prepared but unapproved; it does not reopen either budget.

Timing, a post-stabilization fresh freeze/evaluation and final human acceptance
remain unmet/separately gated. No final acceptance is requested. There were zero
new paid calls. Pilots and the full paid benchmark remain user-deferred; Phase 21
is incomplete and Phase 24/15 gates are unchanged. No merge, release, outreach or
next phase is authorized.

### Historical v12 follow-up at `6eb482c`

Phase 22 remains incomplete. The user's “go ahead” approved both v10 proposals;
`v11-follow-up-authorization.json` preserves their exact hashes and bounds.
One helper-context counter profile found no safely reusable result. No
optimization, native timing comparison or further full Linux retry occurred;
the retained timing failure remains authoritative.

Shared TypeScript factory/else discovery and narrow loopback/default guard
facts are implemented. The canonical finding/review contract is unchanged.
All 18 focused guard controls pass, but the full SearXNG correction gate fails:
both native batches complete 5/5 and detect 2/2 vulnerable variants, while both
fixed variants retain an unqualified SSRF alert. The public-IPv4 control also
retains a broad candidate, separately assessed outside its exact public-input
condition. That distinction does not waive the two fixed false alerts. The
new MCP dispatch surface remains unresolved. All ten authorized SearXNG runs
are consumed; original frozen native/comparator 0/2 results are preserved.

The earlier draft guard-contract stop was premature: existing URL evidence can
represent these narrow facts within the approved correction. Its correction is
recorded in `v12-scope-interpretation-correction.json`. The actual remaining
boundary is loss of that qualification in the complete source flow, not a
request for another ordinary editing approval. The exact cause is not established
by the native report; no callback or unknown effect is assumed harmless.

See `v12-searxng-assessment/packet.json` and the prepared, unapproved
`v12-next-searxng-proposal.json`. Any additional SearXNG observations, full timing
retry, new fresh freeze/evaluation or paid calls require their separate approval.
Final human acceptance is not requested. Phase 21 remains incomplete; pilots and
the full paid benchmark are user-deferred, and Phase 24/15 gates are unchanged.

Final-source verification at `6eb482c`: the local full suite and all 12 hosted
quality suites each pass **2,169 tests with 36 skips and no expected failures**.
Local branch coverage is 89.66%; hosted coverage is 89.65–89.67%.
All 29 normal hosted jobs and docs pass ([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34492040679),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34492040778)).
Wheel/sdist source members match Git; ordinary Docker replay, network isolation,
dependency checks, Ruff/format/strict mypy, schemas, notices and offline generated
artifacts pass. Both approved production review requests were regenerated and
replayed without paid calls. The approved Git environment and 13 incomplete
campaigns retain exact compatibility; no complete Git coverage is claimed.
Intermediate local socket failures and hosted dependency-download failures remain
preserved with their actual source; they are not relabeled as successful runs.

Fetch-mcp and open-webSearch each pass both five-input native regression batches:
2/2 vulnerable matches and zero matching fixed/control alerts per batch. Entire
ordered repeats match except recorded volatile fields; retained findings and
all changed diagnostics are source-assessed. SearXNG's two fixed false alerts
remain a separate failed correction gate. There is no final whole-corpus timing
pass, new fresh-source evaluation or final human acceptance.

The **89-row** current audit records **69 passed,
2 user-deferred and
18 unresolved** requirements. See
`v12-closeout-audit/packet.json`, `v12-current-source-test-bindings/packet.json`,
`v12-exposed-assessment/packet.json` and `v12-hosted-audit/packet.json`.


### Historical v10 checkpoint

**Current scanner: `7555a9d`; tested regression delivery: `bbb5fbc`. Phase 22 remains
incomplete.** Both exposed SSRF families complete five inputs twice, detect both
correlated vulnerable variants and have zero matching fixed/control alerts.
Their original frozen misses and source-assessed residual uncertainty remain.
The final Linux sequence failed: **15/25 completed, ten Meta timeouts**, with
both historical batches correctly skipped. No retry or timing waiver occurred.
Final human technical acceptance is unavailable while this gate is unmet.

Linux run [34435283462](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34435283462)
detects six of ten vulnerable inputs; nine of thirteen valid negatives complete
with zero matching alerts. Both raw Meta erratum negatives are incomplete,
leaving nine of fifteen raw negatives completed. The two vulnerable operator
variants newly time out compared with the prior Linux run. All 15 completed
reports equal current local entire ordered reports except recorded volatile
fields. See `v9-linux-assessment/packet.json` and `v9-linux-execution-delta.json`.

The user approved the exact frozen SearXNG evaluation with “start with 1 and 2.”
All five inputs complete twice natively and once with pinned Semgrep: **both tiers
miss both correlated vulnerable variants**, with zero matching fixed/control
alerts. Maximum wall times are 11.311s/14.926s native and 20.219s comparator.
Entire ordered native reports match except recorded volatile fields; JSON/SARIF
validate. The implementation agent's source exposure after freeze is disclosed.
No new paid call, target execution, retry, source tuning or replacement occurred.

Native coverage recognizes four optional HTTP routes but misses the MCP tool
surface and its ordinary stdio factory/dispatch path. The complete URL flow also
includes structural argument validation, source defaults and casted undici fetch.
Every unrelated finding and diagnostic has a source assessment. This is a
substantive fresh detection limitation, not protection or human acceptance.
See `v9-fresh-assessment/packet.json` and `v10-fresh-review.md`; the separate
`v10-searxng-exposure-fix-proposal.json` is prepared but unapproved. Original
frozen results and manifest `275c98478617c76f92c6e0450b52c62f370a9ae22386022051b50ee792adffdd`
remain unchanged.

The current source SHA-256 is
`b7b7d4d4d5b6c0382769471249c7ea6bcc18465ac2b6d0bfcb3107b6047a089c`.
All 29 normal CI jobs and documentation pass at `bbb5fbc`. Scanner and package
bytes equal `7555a9d`; the sole test change adds a branch-guard invariant. Each of
12 hosted quality suites reports 2,141 passed and 36 skipped, with 89.63–89.66%
branch coverage. All 153 wheel and 166 sdist source/schema/fixture/capture members
match Git blobs. Full logs and 225 uploaded files are retained in
`v10-hosted-bbb5fbc/packet.json`; verification is in
`v10-final-hosted-audit/packet.json`. The local suite passes 2,141 tests with
36 skips and 89.64% branch coverage. The preceding `05309f9` hosted run also
passes and is retained separately. Pinned historical reproductions retain their
original scanner and do not replace the current timing gate. Exact unchanged
source/harness/input/capture compatibility is in `v10-source-compatibility.json`.
No additional paid call occurred. Pilots and the full paid benchmark remain
user-deferred; Phase 21 is incomplete and Phase 24/15 gates are unchanged.

The separately approved Linux diagnostic ran once as
[34446017571](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34446017571):
all four native observations and both profiles time out at 120 seconds. The job's
successful diagnostic completion is not a native timing pass. Worker profiles
show CPU-bound call/expression traversal, merging and Value allocation across
SENT-012/015/016. Missing reports remain missing; see
`v10-linux-diagnostic-assessment/packet.json` and `v10-linux-review.md`.

One bounded local experiment used eight native observations and one count profile
on the two exposed Meta inputs. Removing duplicate immutable merge inputs
preserved all ordered reports, but median wall gains of 2.29%/1.84% and CPU gains
of 2.43%/1.40% were small relative to variability, with a first operator regression.
The optimization was reverted; the useful branch-guard invariant test remains.
Scanner bytes still equal `7555a9d`. See `v10-local-performance-disposition.json`.
No full benchmark retry, deadline waiver or runner change occurred. Further
execution decisions and final human acceptance remain separate; Phase 22 stays
incomplete while the timing gate is unmet.

## Historical v8 checkpoint at scanner `62987a6`

**Current scanner: `62987a6`; workflow delivery: `88a559e`. Phase 22 remains
incomplete pending execution reliability and final human technical acceptance.** The user approved both the revised Linux execution and exact
fresh-corpus checkpoint with “go ahead with these two”. Their separate decision
records preserve the exact proposal/manifest hashes and stopping conditions.

Linux development fails its gate: 17/25 inputs complete and eight time out;
maximum end-to-end time is 120.043s. Eight of ten vulnerable inputs complete and
are detected. Nine of thirteen valid negatives complete with zero matching alerts.
Both raw Meta erratum inputs are incomplete, so the raw negative denominator is
nine completed out of fifteen. Both historical batches are skipped after this failure.

The Linux run is 34421737148. No retry, pooling or deadline waiver occurred.
Earlier local historical 43/45 and development 24/25 failures remain preserved.
Seven Linux timeouts are new versus that local development run; one persists.
All 17 completed Linux reports match the prior entire ordered reports except
documented volatile fields. The next bounded Meta performance proposal is
prepared in `v8-next-performance-proposal.json` and remains unapproved.
The approved Meta erratum remains separate from raw scores and execution status.

The fresh fetch-mcp evaluation completes all five inputs twice natively and once
with Semgrep 1.176.0. Both tiers miss both correlated vulnerable variants and
have zero condition-matched alerts on the three fixed/safe inputs. Native reports
match in full except documented volatile fields; maximum wall times are 5.771s
and 5.075s (Semgrep: 16.374s). Native dispatch/schema/class flows remain unresolved.
All 50 unrelated Semgrep JQuery alerts have source-bound false-positive
assessments. No detector tuning or fresh accuracy threshold is introduced;
curation exposure remains disclosed.

The exposed open-webSearch regression remains 2/2 detections in both final runs,
with zero matching negative alerts. Its original 0/2 results are unchanged.
Original held-out evidence remains 10 completed/10 unsupported/5 incomplete,
with zero detections among four completed vulnerable variants. The original
historical 70-warning unadjudicated backlog remains distinct from source-assessed
exposed-regression warnings. Native full-report comparisons and all new finding/
coverage assessments are retained in the v8 evidence.

All 29 normal CI jobs pass at workflow delivery `88a559e`, with the optional benchmark job skipped in ordinary CI; documentation also passes. The 12 quality suites each report 2,121 passed and 36 skipped, with 89.63–89.65% branch coverage. Complete logs/artifacts and source-verified distributions are retained.

The full paid benchmark and external pilots remain explicitly user-deferred,
not passed. No additional paid model calls or target execution occurred in these
two evaluations. Compatible capture/Docker/Git evidence remains bound to the
unchanged scanner. Final human acceptance is separate; Phase 21, Phase 24 and
Phase 15 gates remain unchanged. No merge, release, outreach or next phase.

See [the implementation status](docs/phase22-implementation-status.md) and the
current `artifacts/phase22/integration/v8-closeout-audit/packet.json`.

### Retained implementation checkpoints

The following records describe their named historical sources. Later approvals
and final-source verification supersede their old pending-work statements.

The [execution correction increment](docs/phase22-execution.md) restores 45/45
rules-only completion and records a 13/13 Git startup/discovery environment.
The user subsequently authorized its adoption and the new corpus freeze;
`artifacts/phase22/authorization.json` binds both exact packets. New detectors
and the remaining technical expansion are not complete. The consolidated integration
branch now includes the original TypeScript argument-identity correction, nested
Python command/registration flows, shared review evidence and SENT-015 request
analysis. A milestone suite passed 891 tests; later changes have focused checks.
These are intermediate implementation records, not the final repeated benchmark,
campaign, reviewed-evaluation or hosted acceptance gates. See the
[implementation status](docs/phase22-implementation-status.md). The
[workspace increment](docs/phase22-workspaces.md) records the corrected
TypeScript parent, aggregate workspace source scanning and separately retained
verification. Local integration commits now implement ordered bounded attempts,
linked native 1.7 reporting and repeated runtime proof (`3f75327`), with
orchestration-fixture corrections (`a9c097e`), registered lifespan flow
(`9d396a4`), bounded service construction (`c71e43e`), direct credential-bearing
client sinks (`a2b88f1`) and actual-evaluation URL facts (`ee6c9f5`). These changes remain
undelivered and have no final technical acceptance. After the retained failed
milestone, the fixed `f12e891` checkout passed 1138 tests, 36 skipped and 87.94%
branch coverage. Later TypeScript HTTP and shared shell-dispatch commits have
focused checks; the five-input Kubernetes development measurement now completes
with two vulnerable condition hits and zero fixed/mutation/control condition
alerts. Batch 6 preserves these source-specific results and failures. They do not
replace final-candidate checks. At `c71e43e`, the exposed Atlassian-auth input
again exceeded the unchanged 120-second static deadline. The later `ee6c9f5`
measurement remains incomplete despite measured interpretation corrections. Completing that input,
its missing credential-fallback detection, the remaining detector conditions,
final migration/campaign verification, paid evaluation and consolidated draft
delivery remain authorized technical work. Human acceptance and the deferred
external pilot gate remain separately unmet.

The later `dcb965f` integration supersedes those incomplete technical measurements:
all 45 historical inputs complete twice under the unchanged 120-second deadline,
with identical stable reports, all 20 exposed vulnerable conditions detected and
zero named fixed/safe alerts. The full suite at that source passes 2,007 tests,
36 skipped, with 89.47% branch coverage. All 25 frozen development inputs complete;
two Meta fixed-condition labels remain disputed and require an explicit decision.
The first frozen held-out evaluation completes only 10/25 inputs and detects none
of four completed vulnerable variants; six vulnerable variants are unavailable.
These limits remain recorded, without a new accuracy threshold or scope relaxation.

That evaluation exposed incorrect legacy TypeScript finding coordinates. The five
auth-fetch cases were marked exposed before correction `b163d7c`; `6e68331` also
corrects a test that expected the old end column. Its two historical runs complete
45/45 with stable reports identical to dcb965f. Its full suite records 2021 passed,
two failed, 36 skipped and 89.49% branch coverage. Commit d7184d3 corrects only a
stale dry-run cost expectation, with both targeted tests passing. The raw suite
remains failed. The unchanged TypeScript smoke replay test needs a compatible capture;
its exact request is prepared offline, and paid authorization remains required.
Pinned Semgrep completes 45/45 historical, 25/25 development and 20/25 held-out
inputs; the five Solver inputs retain parser errors. All three named-condition
assessments report zero matches; unrelated warnings and uncertainty remain visible.
Evidence batch 26 preserves the earlier completed measurements, source assessments
and failures. Current independent local quality, distribution/install, 36 real
Docker, installed onboarding/baseline, pre-commit and 12 Linux network-isolation
checks pass at d7184d3. All 25 current development reports are stable-identical;
the held-out repeat retains its limits and only ten corrected coordinates.
The actual demo completes 20/20 runtime attempts but exits 3 for missing dynamic
review. The exact paid packet proposes 398 new requests, at most $66.321920,
with 20 historical requests reused; explicit approval is pending. It excludes
the separately proposed replacement corpus, whose freeze also remains pending.
The 86-requirement local acceptance index retains these distinctions. Evidence
batch 27 preserves the completed local work with verified readback. Consolidated
draft PR #37 is delivered against PR #36, and hosted execution is complete at
1e7c16a. All 12 wheel jobs, hosted isolation and docs pass. All 12 full quality
suites record 2022 passed, one unchanged capture failure and 36 skipped; the
Docker demo fails only its missing dynamic review. No additional platform
regression was found. These failed gates remain approval-dependent, alongside
reviewed evaluation, the replacement freeze, Meta decision, human acceptance
and the deferred pilot-dependent gate. Evidence-only bookkeeping preserves the
measured source and avoids duplicate CI; it does not establish merge readiness.

The subsequently approved two-request smoke/demo capture subset succeeded for
$0.071799 against its $0.400100 cap. The unchanged TypeScript replay and actual
Docker demo now pass locally; all 20 attempts and 14 reviews complete. Updated
hosted verification remains pending. Benchmark paid review, replacement freeze,
Meta amendment, human acceptance and pilot gates are unchanged and incomplete.

The replacement freeze and Meta erratum are now approved. Both offline treatments
complete all five replacements but detect neither vulnerable variant; native
repeat is stable. Unresolved registrations and all unrelated warnings remain
visible. The Meta erratum separates two affected fixed cases from 13 valid clean
controls without rewriting the original labels, conditions or raw results. No
new paid evaluation or detector tuning occurred. Full reviewed benchmarking,
human acceptance and external pilot requirements remain incomplete.

### Objective

Address measured missed vulnerabilities and real repository incompatibilities
while keeping the supported boundary explicit.

### Work

- Add bounded path-containment detection, including traversal, absolute paths,
  unsafe prefix checks, and symlink cases where evidence permits. Add dedicated
  tool-description poisoning detection rather than relying on prompt sinks.
- Evaluate command argument injection beyond `shell=True`; use the independent
  corpus to select supported sinks and safe controls. Assign new stable rule IDs
  for new meanings rather than stretching existing execution/permission rules.
- Implement the five authorized compatibility areas in §1, including imported
  handlers/schemas, aliases and statically bound helpers/methods, cross-file
  flows, low-level registration/dispatch and declared uv/npm/pnpm workspaces.
  Pilot-driven prioritization remains deferred; it is no longer a Phase 22
  completion prerequisite under the user-approved scope revision.
- Add the approved SENT-012–SENT-016 catalog and correct SENT-002 Kubernetes
  execution detection. Correct Helm parsing, measured static repeated work and
  Git startup under the separately approved environment. Follow the detailed
  [technical contract](docs/phase22-technical.md) and decision checkpoints.
- Expand fixed dynamic campaigns across eligible tools and relevant parameters
  with explicit budgets, deterministic scheduling, and per-attempt evidence.
  Reconcile the old four-attempt/probe-plan contract before implementing this.
- Reuse installed engines and shared discovery structures before adding parsers
  or dependencies. Avoid a speculative plugin framework or new language targets.
- Track ownership/authorization gaps as future discovery/sequence cases; simple
  type validation is not proof of business-policy enforcement.

### Verification gate

- New threat classes have independent vulnerable/fixed examples, safe controls,
  documented limits, and stable canonical findings with justified OWASP mapping.
- A multi-tool fixture with a safe alphabetically first tool and a vulnerable
  later tool is tested correctly; budget exhaustion discloses untested surface.
- Publish before/after independent benchmark and completion results, retaining
  misses, false alarms, unsupported inputs and known coverage limits. The former
  blocked-pilot before/after requirement is deferred from Phase 22 by the user;
  external validation must not be inferred from these benchmark results.
- Existing supported fixtures and migrated reports remain valid. Unimplemented
  compatibility requests stay documented rather than silently counted as covered.

## 26. Phase 23 — Maintained feedback and regression releases

**Status: planned.** Depends on Phase 22.

### Objective

Keep detection current through reproducible reports and reviewed releases,
without making offline scans depend on automatically changing rules.

### Work

- Extend existing issue/contribution workflows for missed vulnerabilities and
  false alarms, with private reporting for sensitive cases and opt-in sharing.
- Establish the loop: advisory/report → minimized reproduction → detector change
  → benchmark regression evaluation → human review → versioned release.
- Track time to triage, reproduce, fix, and release. Record rule/corpus versions
  and meaningful coverage changes in release notes; preserve rollback and pins.
- Allow AI-assisted test/rule drafts, but never automatically promote generated
  rules, trust arbitrary feedback labels, or upload private repositories.
- Include SDK/security-advisory review in the maintenance cadence and retain
  affected real-world cases in the corpus after fixes ship.

### Verification gate

- At least one consented pilot report or public advisory completes the entire
  reproduction-to-reviewed-release loop with retained evidence and timings.
- Offline CI exercises the updated corpus and rejects a deliberately regressed
  detector. Released rules remain reproducible by version without live feeds.
- Contribution guidance explains false-negative reporting, label review,
  disclosure, and how feedback becomes a tested release.

## 27. Phase 24 — Retained adoption and product decision

**Status: planned.** Depends on Phase 23. Required before closing Phase 15.

### Objective

Demonstrate that maintainers voluntarily keep using Sentinel, and base further
investment and launch claims on observed value.

### Work

- Revisit the five pilot workflows after the fixes. Target at least three of
  five maintainers installing without author intervention, reaching a useful
  first result within five minutes, and retaining the CI check for 30 days.
- Treat these as proposed pilot goals, not industry benchmarks. Define timing
  and a useful result in advance; disclose installation/network prerequisites,
  assistance, removals, and inconclusive observations.
- Retain maintainer-confirmed findings or prevented regressions and resulting
  repair evidence. Distinguish useful coverage reports from demonstrated catches.
- Prepare consented case studies and a vulnerable/fixed walkthrough for Phase
  15. Position against actual alternatives using measured incremental value.
- Record a continue, narrow, or pivot decision. Investigate willingness to pay
  for recurring team policy, private execution, or maintenance needs only if
  participants report them; do not build billing or a dashboard speculatively.

### Verification gate

- At least three of the five pilots meet the documented onboarding and 30-day
  retention targets, with participant-confirmed evidence rather than inferred
  usage. At least one independent finding/fix or prevented regression is verified.
- If targets fail, retain this phase as incomplete, identify the cause, and
  iterate on the responsible phase or explicitly revise product scope and goals.
  Do not replace evidence with more announcements or fixture demonstrations.
- Phase 15 materials make only supported claims and include limitations,
  benchmark provenance, and consented maintainer outcomes.

## 28. Phase 25 — Bounded independent AI discovery

**Status: conditional, planned.** Eligible after Phase 24 when measured missed
semantic issues justify an experiment. Does not block Phase 15.

### Objective

Evaluate whether source-only model discovery finds useful issues that never
become deterministic candidates, at an acceptable cost and false-alarm rate.

### Work

- Add a separate opt-in advisory discovery path over recognized tools and their
  bounded reachable implementation, including tools with zero static candidates.
- Examine path/resource ownership, privilege boundaries, description/behavior
  mismatches, and suspicious tool-to-tool data flows using explicit context.
- Define the architecture change allowing independent findings before coding:
  canonical provenance/source, stable new rule meanings, evidence references,
  uncertainty, deduplication, baselines, suppression, and report versioning.
- Reuse strict response validation, redaction, endpoint trust, budgets, and
  telemetry. Validate that cited evidence supports the claim; a valid line range
  alone does not establish semantic correctness. Treat target text as untrusted.
- Keep discovery advisory and source-only: no model-authored code execution,
  automatic patches, or default CI blocking. Do not weaken the deterministic tier.

### Verification gate

- Held-out cases include independent valid discoveries on zero-candidate targets,
  safe controls, misleading repository instructions, and insufficient-context
  abstentions. Human review checks evidence and false alarms.
- Publish incremental validated findings over Phase 22, maintainer acceptance,
  false positives, repeatability, latency, and cost against a predeclared budget
  and acceptance threshold. Ship only if the measured benefit passes that gate.
- Explicit offline mode makes zero discovery calls; existing report consumers
  receive tested compatibility/migration behavior. Otherwise retain the feature
  as an unshipped experiment with its measured outcome.

## 29. Phase 26 — Stateful multi-step security testing

**Status: conditional, planned.** Eligible after Phase 24 when a concrete pilot
or benchmark scenario needs sequence testing. Phase 25 is required only if its
model-discovery output is used; fixed sequences can be implemented independently.

### Objective

Test explicit cross-tool and ownership/authorization invariants through bounded
sequences in Sentinel-controlled sandboxes.

### Work

- Define each scenario's legitimate baseline, identities, allowed resources,
  state setup, tool sequence, security invariant, and observable violation.
  Include cross-user resource access and one cross-tool escalation scenario.
- Preserve state within a scenario and reset it between scenarios. Use synthetic
  credentials, test-owned data, controlled services, resource limits, and cleanup;
  no production endpoints or host-side execution of target/generated code.
- Begin with deterministic parameterized sequences. Model assistance, if
  justified, proposes schema-validated tool calls under explicit step/time/cost
  budgets, not arbitrary executable exploit programs.
- Separate unsupported transport or unavailable prerequisites from a blocked
  attack. Streamable HTTP/Node infrastructure must pass its own documented
  isolation and compatibility gates before a scenario can depend on it.
- Record the complete redacted sequence and before/after effects in canonical
  evidence; unsuccessful attempts remain inconclusive unless a specific defense
  is actually demonstrated. Keep automatic patches/PRs out of scope.

### Verification gate

- Reproducible vulnerable/fixed pairs demonstrate the ownership and cross-tool
  invariants; valid authorized workflows still succeed on fixed targets.
- Repeat runs establish state isolation, identity separation, step limits,
  teardown, and truthful unsupported/inconclusive results.
- An independent applicable benchmark or pilot case demonstrates added coverage
  over single-call probes, with false alarms and runtime overhead reported.
- Any model-assisted path has separate budgeted live/replay evidence and remains
  opt-in. Schema-valid reports preserve the complete causal evidence chain.

## 30. Unscheduled post-launch and future work

These items remain demand-gated and have no dedicated phase number. Phases
16–26 own the specific review recommendations above; this list is not an
instruction to build all adjacent capabilities.

### Deferred product options

- Streamable HTTP support.
- Remote-repository scanning convenience.
- Running-endpoint scanning restricted to Sentinel-launched sandboxes.
- Arbitrary-target generated exploit confirmation beyond the bounded scenarios
  of Phase 26.
- Static analysis for languages beyond Python and TypeScript.
- A Node dynamic sandbox with npm registry egress rules and an isolated stdio
  harness.
- Automated patch generation.
- Automated pull-request creation.
- Dashboards and billing, only after recurring demand and willingness to pay
  are established in Phase 24.

### Compatibility investigations

- Python 3.14 support when all required runtime dependencies permit it.

### Existing README commitments

- IDE integration for inline findings.
- Broader fuzzing beyond the measured per-tool campaigns and bounded tool-chain
  scenarios in Phases 22 and 26.
- Policy-as-code rule authoring.

### Explicitly outside the product roadmap

- Full PortunusMCP Gateway integration.
- PortunusMCP Identity or SPIFFE/SPIRE credential brokering.
- Comprehensive coverage of every MCP vulnerability class.
- Unsupervised promotion of automatically evolved rules or a claim of universal
  zero-day detection.

## 31. Gate summary

Phase IDs below preserve history. Execute **16–24, then 15**; 14, 25, and 26
are conditional/optional and do not block the required product path.

| Phase | Required outcome | Blocking verification |
|---|---|---|
| 0 | Executable contracts and valid report shell | CLI, schemas, offline SARIF, quality tools pass. |
| 1 | Seven deterministic static rules | Vulnerable/clean fixture matrix and no-execution proof pass. |
| 2 | Required grounded GPT review and probe planning | Structured Outputs, evidence/plan validation, ablation, telemetry, cassettes, and failure modes pass. |
| 3 | Four isolated, GPT-prioritized dynamic probes | Docker security, plan fallback, behavior, merge, timeout, and reaper tests pass. |
| 4 | Composite Action and Security-tab integration | Live throwaway-repository upload passes. |
| 5 | Stable judged deliverable and submission package | Clean-checkout CI, prebuilt wheel, ablation artifacts, documented Codex/GPT usage, and rehearsed live/replay demos pass. |
| 6 | Release-ready `portunusmcp-sentinel` package | Metadata, dependency, Python 3.13, artifact, and isolated-install gates pass. |
| 7 | Trusted PyPI release | TestPyPI promotion, protected OIDC publishing, attestations, and public installs pass. |
| 8 | Marketplace Action | Public listing, stable `v1`, pinned package install, and external workflow pass. |
| 9 | Two-command onboarding | Safe config generation, actionable no-key UX, and tier documentation pass. |
| 10 | Configurable GPT endpoint | Precedence, compatible endpoint, validation, and provenance gates pass. |
| 11 | TypeScript static support | Paired seven-rule fixtures, no-execution proof, and valid reports pass. |
| 12 | Incremental team adoption | Baseline, inline suppression, auditability, and pre-commit gates pass. |
| 13 | Public docs and maintenance | Repositioned docs, PortunusMCP branding, contributor paths, Dependabot, and docs site pass. |
| 14 | Fixture-only exploit confirmation | Deferred until after Phase 24; optional and isolated from product gates. |
| 15 | Evidence-backed product launch | Phase 24 passes; public distribution, submissions, actionable walkthrough, and authorized announcements support measured claims. |
| 16 | Correct static safety decisions | Unsafe exemptions and local-helper misses have durable regressions and safe controls. |
| 17 | Sound dynamic evidence | Valid baselines, genuinely invalid payloads, measured effects, and Docker isolation checks pass. |
| 18 | Predictable offline onboarding | Zero model/Docker calls with credentials present; keyless CLI, Action, and pre-commit work. |
| 19 | Visible coverage and actionable findings | Recognized/unknown surface, per-attempt coverage, evidence, and review states are accurate in all formats. |
| 20 | Independent benchmark | Pinned vulnerable/fixed corpus, held-out cases, honest denominators, and reproducible tier comparisons. |
| 21 | Maintainer problem validation | Five external pilots attempt their workflows and establish a bounded improvement priority. |
| 22 | Broader useful MCP coverage | New threat controls, per-tool campaigns, and a pilot compatibility fix improve measured results. |
| 23 | Maintained detection feedback | A report/advisory reaches a tested, reviewed, reproducible release with recorded timings. |
| 24 | Retained adoption | Three of five pilots meet onboarding/30-day retention goals and an independent useful catch is verified. |
| 25 | Independent AI discovery | Conditional; held-out incremental findings justify noise/cost, with advisory provenance and no execution. |
| 26 | Stateful security testing | Conditional; isolated identity/tool sequences prove violations on vulnerable cases and defenses on fixed cases. |
