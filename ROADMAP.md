# MCP Sentinel Roadmap

## 1. Planning frame

This roadmap is ordered by dependency gates, not calendar dates. It assumes one
engineer. Unless explicitly marked optional, a phase begins only after the
previous required phase's verification gate passes.

Phases 0–5 are the complete required hackathon deliverable. Phases 6–13 turn
that deliverable into an installable, adoptable product. Phase 14 is optional
stretch work and does not block the final launch phase. Phase 15 completes the
product launch.

The architecture and accepted contracts are defined in `ARCHITECTURE.md`. This roadmap tracks implementation and verification; it does not redefine those decisions.

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

This schedule is a spending discipline, not permission to claim GPT behavior
from mocks or replay. The applicable live checkpoint must pass before its
dependent phase is complete.

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

**Status: implementation gates and the live GPT checkpoint complete; hosted
release and external Action proof pending.** Native JSON 1.4.0, baseline
matching, Python/TypeScript inline suppression, Action input/metrics, the public
pre-commit hook, local and hosted schema/SARIF validation, strict typing, and
the branch-covered test suite pass. The two-call GPT-5.6 checkpoint passed with
zero retries and USD 0.034249 actual spend.
Do not mark this phase complete until the signed `v1.2.0` release, PyPI proof,
exact/alias Action proofs, and evidence links are recorded.

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

### Entry condition

Begin only when every Phase 6–13 gate is passing. This optional phase may be
skipped and never blocks Phase 15.

### Scope

- Implement `src/sentinel/llm/exploit_confirm.py` only for bundled vulnerable fixtures.
- Generate one context-specific exploit attempt for an eligible finding.
- Execute it within the existing Docker isolation boundary.
- Record evidence and set `confirmed` or `likely_false_positive` through the approved status lifecycle.
- Keep arbitrary user targets, automated patches, and automated pull requests out of this phase.

### Verification gate

- At least one bundled-fixture exploit succeeds reproducibly and records redacted evidence.
- The clean fixture remains unaffected.
- Failure cannot destabilize or alter the required Phase 0–13 product path.
- No exploit code runs on the host or against a remote endpoint.

## 18. Phase 15 — Product launch

### Objective

Make the released product discoverable with claims backed by public evidence.

### Work

- Lead launch material with isolated dynamic proof, OWASP Agentic Top 10
  mapping, SARIF/code-scanning integration, and offline replay.
- Reuse the existing sub-three-minute YouTube demo instead of rerecording it
  unless the released product behavior has materially changed.
- Publish a short technical walkthrough that scans a real public MCP repository
  locally and discloses the target version, configuration, and reproducible
  findings without probing a live endpoint.
- Submit Sentinel to the relevant `awesome-mcp-servers` and MCP security lists.
- Publish concise announcements to Show HN, `r/mcp`, and the MCP Discord.
- Link the PyPI project, Marketplace listing, documentation site, source,
  changelog, demo, and security policy from the launch material.

### Verification gate

- The PyPI project and Marketplace listing are public and installable.
- The README begins with the working one-command install and links to the public
  documentation and Action.
- The list submissions are merged and the announcement posts are publicly
  accessible.
- The walkthrough is reproducible from a named public target revision and makes
  no claim unsupported by the generated report.
- Launch links resolve, and the reused demo is clearly labeled if its displayed
  version predates the product release.

## 19. Unscheduled post-launch and future work

These items are intentionally unscheduled and have no phase number.

### Approved product evolution

- Streamable HTTP support.
- Remote-repository scanning convenience.
- Running-endpoint scanning restricted to Sentinel-launched sandboxes.
- Exploit confirmation generalized beyond bundled fixtures.
- Static analysis for languages beyond Python and TypeScript.
- A Node dynamic sandbox with npm registry egress rules and an isolated stdio
  harness.
- Automated patch generation.
- Automated pull-request creation.

### Compatibility investigations

- Python 3.14 support when all required runtime dependencies permit it.

### Existing README commitments

- IDE integration for inline findings.
- An expanded dynamic fuzzing corpus for tool-chain abuse.
- Policy-as-code rule authoring.

### Explicitly outside the product roadmap

- Full PortunusMCP Gateway integration.
- PortunusMCP Identity or SPIFFE/SPIRE credential brokering.
- Comprehensive coverage of every MCP vulnerability class.

## 20. Gate summary

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
| 14 | Fixture-only exploit confirmation | Optional and isolated from the required product path. |
| 15 | Discoverable product launch | Public distribution, merged list submissions, reproducible walkthrough, and announcements pass. |
