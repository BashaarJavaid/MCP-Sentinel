# AGENTS.md

Project-specific context and instructions for **PortunusMCP Sentinel**, merged with a set of general behavioral guidelines (sections 1-4 below, adapted from [andrej-karpathy-skills/CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)) aimed at reducing common LLM coding mistakes: unstated assumptions, speculative complexity, unrelated edits, and vague success criteria.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## Project

**PortunusMCP Sentinel** — a build-time static/dynamic security scanner for MCP (Model Context Protocol) servers, mapped to the OWASP Agentic Top 10, shipped as a CLI tool and a GitHub Action that outputs SARIF.

Sentinel is one of three components of the **PortunusMCP** family:
1. **PortunusMCP Gateway** — runtime zero-trust enforcement gateway (separate repo, out of scope here).
2. **PortunusMCP Sentinel** *(this repo)* — build-time scanner.
3. **PortunusMCP Identity** — short-lived credential broker (separate repo, out of scope here).

Sentinel helps maintainers and small teams **catch MCP server security
regressions before release, with actionable source findings and reproducible
evidence for supported runtime checks**. It combines static source/manifest
analysis and adversarial probes against sandboxed targets. A completed scan is
not proof that a server is safe; OWASP mappings classify findings, not coverage
of all ten categories. Start with supported Python server maintainers and expand
according to measured detection gaps and pilot demand.

The historical build context lives in `mcp-sentinel-buildplan.md`; active contracts and status live in `ARCHITECTURE.md` and `ROADMAP.md`. Read the historical brief first for project context, then use the active documents as authority.

## Where things live

- `mcp-sentinel-buildplan.md` — historical build brief and original scope. Read this first for context; defer to Architecture and Roadmap for current contracts.
- `README.md` — public quickstart, install, supported scope, and usage examples.
- `src/sentinel/static/rules/` — one file per detection rule; each rule is independently testable and tagged with its OWASP Agentic Top 10 category (`src/sentinel/owasp_mapping.py` holds the canonical rule-id → category map).
- `src/sentinel/dynamic/` — the sandbox launcher (`sandbox.py`) and adversarial prober (`prober.py`).
- `src/sentinel/report/` — `sarif.py` (SARIF 2.1.0 writer) and `console.py` (human-readable terminal report).
- `tests/fixtures/vulnerable_server/` and `tests/fixtures/clean_server/` — the reference sample servers every rule is tested against.
- `tests/evals/` and `artifacts/` — existing review truth sets and retained
  evidence; Phase 20 adds independent vulnerable/fixed cases and held-out
  evaluation. Fixture success and code coverage are not detection accuracy.
- `action.yml` — the GitHub Action wrapper around the CLI.

Don't load the full dynamic-analysis sandbox code when working on a static rule, and vice versa — pull in only what's relevant to the current task. Both stay decoupled through the shared report/finding schema.

## Conventions

- Python with Typer for the CLI; retain the established framework.
- Every rule (static or dynamic) produces a finding using **one canonical Finding shape** (rule id, severity, OWASP category, file/location, message, remediation hint) — don't invent a bespoke shape per rule or per output format. `sarif.py` and `console.py` both consume the same Finding objects.
- Rule IDs are stable once assigned (`SENT-001`, `SENT-002`, …) — SARIF output and any historical comparisons depend on IDs not changing meaning. Add new rules with new IDs; don't renumber.
- Static analysis must never import or execute target code. Dynamic analysis
  runs targets only in Sentinel-controlled Docker sandboxes under the accepted
  isolation contract, never directly on the host or against production endpoints.
- Prefer embedding an existing engine (e.g. `semgrep`) for static pattern rules over hand-rolling a full AST walker — this is a deliberate hackathon-scope decision, not a shortcut to "fix later."
- Deterministic rules and probes must not require third-party live services.
  Keep model review separate from the offline tier; Phase 18 will add an explicit
  review-disable mode. Dependency installation and explicitly selected live
  model evaluation have separate network requirements.
- SARIF output must validate against SARIF 2.1.0 schema — treat a non-validating report as a build-breaking bug, not a cosmetic issue.

## Commands

- `pip install -e ".[dev]"` — local dev install
- `uv sync --extra dev` — reproducible local dev install from `uv.lock`
- `sentinel scan <path>` — run static + dynamic checks against a local MCP server repo
- `sentinel scan <path> --format sarif` — emit SARIF 2.1.0
- `pytest` — run the current test suite with branch coverage
- `sentinel demo` — run the full static, GPT review, and Docker dynamic pipeline
  against the vulnerable fixture
- `python -m sentinel.schema check` — fail if generated Finding/report schemas drift
- `python -m sentinel.report.validate_sarif <file.sarif>` — validate SARIF offline

`sentinel scan --static-only` includes required GPT review and exits `0` or `1`
when complete. `--allow-degraded` explicitly permits unreviewed candidates while
keeping them visible and fail-on eligible; it does **not** disable model calls
when a key is present. Normal scans and `sentinel demo` run Phase 3 dynamic
probing and return `3` when analysis is incomplete. These are current commands;
do not document Phase 18's new offline interface as available before it ships.

## Current phase

See `ROADMAP.md` for the authoritative dependency order and verification gates.
**Phase 16 is complete; Phase 17 is next and has not started.**
Existing phase IDs are preserved for historical releases
and evidence. Required execution order is **16 → 17 → 18 → 19 → 20 → 21 → 22 →
23 → 24 → 15**, rather than numeric order. Phases 14, 25, and 26 are deferred or
conditional and never block launch. Update this section only when the relevant
gate actually passes; a roadmap entry is not implemented behavior.

- [x] Phase 0 — repo scaffold, incomplete `sentinel scan`, valid report shells and schemas
- [x] Phase 1 — hybrid static engine, `SENT-001`–`SENT-007`, paired fixtures
- [x] Phase 2 — GPT semantic review, live captures, replay demo, and static ablation
- [x] Phase 3 — Docker sandbox and four adversarial probes
- [x] Phase 4 — GitHub Action and live SARIF upload
- [x] Phase 5 — console/report polish and judged demo
- [x] Phase 6 — package and release readiness (`portunusmcp-sentinel` distribution)
- [x] Phase 7 — trusted PyPI publishing
- [x] Phase 8 — GitHub Marketplace distribution
- [x] Phase 9 — first-run onboarding (`sentinel init`)
- [x] Phase 10 — configurable GPT review endpoint
- [x] Phase 11 — TypeScript static analysis
- [x] Phase 12 — team adoption workflows (baseline, inline suppression)
- [x] Phase 13 — public documentation and maintenance (PortunusMCP rebrand)
- [ ] Phase 14 — conditional exploit-confirmation stretch (deferred until after Phase 24; optional)
- [ ] Phase 15 — product launch (retain existing artifacts; completion depends on Phase 24)
- [x] Phase 16 — static detection correctness (helper flows and safety exemptions; local gates passed)
- [ ] Phase 17 — dynamic probe correctness and evidence (valid baselines, schema violations, observed effects)
- [ ] Phase 18 — explicit offline mode and first-use workflow (CLI, Action, pre-commit, onboarding)
- [ ] Phase 19 — coverage reporting and actionable findings (recognized/unknown surface and useful evidence)
- [ ] Phase 20 — independent detection benchmark (vulnerable/fixed pairs, safe controls, held-out cases)
- [ ] Phase 21 — maintainer pilot and problem validation (five external workflows and ranked blockers)
- [ ] Phase 22 — MCP coverage and compatibility expansion (new threat classes, per-tool campaigns, pilot blockers)
- [ ] Phase 23 — maintained feedback and regression releases (report-to-tested-release loop)
- [ ] Phase 24 — retained adoption and product decision (onboarding, 30-day retention, independent useful catches)
- [ ] Phase 25 — bounded independent AI discovery (conditional after Phase 24; advisory, source-only)
- [ ] Phase 26 — stateful multi-step security testing (conditional after Phase 24; isolated scenarios)

Phases 0–13 are complete. Their original completion statements, release links,
digests, and submission records are preserved in `docs/hackathon.md` and the
linked evidence artifacts. Phase 13's
[documentation workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33908643137)
passed its strict build, Pages deployment, and live page/anchor smoke at the
[public site](https://bashaarjavaid.github.io/MCP-Sentinel/); its hosted
contribution and dependency-maintenance gates also passed.

The September 2026 review found that the existing implementation/test gates do
not establish real-world detection effectiveness. Preserve their completion
records while implementing the new gates; do not claim the four-case GPT
ablation or zero-finding public walkthrough proves broad accuracy or user value.

## Product-quality implementation rules

- Reproduce the review's counterexamples as durable tests before fixing them:
  same-file helper execution, validation of unrelated data, authentication
  middleware without enforcement, and hashing without trusted comparison.
  Check equivalent Python and TypeScript paths. A named check or nearby call
  alone is not evidence that the relevant input is protected.
- Dynamic probes need a legitimate baseline, valid prerequisites, and an
  observable security condition. Confirm malformed inputs violate the actual
  schema; accepting a large input alone is not exploitation. Distinguish
  unsupported, untested, and inconclusive outcomes from demonstrated defenses.
- Preserve evidence of observed effects through model review. Static suspicion,
  model corroboration, and runtime proof are distinct. A failed exploit attempt
  is not sufficient evidence to label a finding a false positive.
- Report recognized and unresolved handlers and actual tool/parameter probe
  coverage. Do not imply that `evaluated` rules covered all implementations or
  that Sentinel permission sidecars enforce runtime resource boundaries.
- Use the paired reference fixtures plus independent vulnerable/fixed cases and
  structural mutations. Freeze held-out cases before tuning. Report misses,
  false alarms, abstentions, incorrect model suppressions, and support/completion
  denominators; code coverage is a separate engineering metric.
- Benchmark the deterministic and reviewed tiers on identical inputs. Attribute
  competitor capabilities to their documentation and comparative performance
  only to reproducible measurements. Never claim unmeasured superiority.
- Existing GPT review is candidate-bound; broader independent discovery is
  scheduled only in Phase 25. Update `ARCHITECTURE.md`, canonical provenance,
  schemas, compatibility, and docs in the owning phase before implementing new
  review modes, campaign semantics, or independent finding origins. Never reuse
  an unrelated rule ID to accommodate a model discovery.
- Reuse the current pipeline, report model, issue templates, and installed
  engines. Avoid speculative plugin systems, parsers, dashboards, billing,
  automatic patches/PRs, and new languages. Phase 22 selects compatibility work
  from observed pilot blockers; Phase 24 records the commercial/product decision.
- Independent AI discovery is opt-in, advisory, bounded, and source-only.
  Stateful testing uses explicit identities, test data, security invariants, and
  isolated sequences; model-authored executable exploits are not a prerequisite.
- Keep the feedback loop reviewed and versioned: reproduction → detector change
  → regression benchmark → human review → release. AI may draft tests/rules but
  cannot automatically promote rules or change an offline scan's rule set.
- Follow `ROADMAP.md`'s live-evaluation cost policy. Routine tests and pilots use
  offline paths; new live measurements require named cases, a bounded budget,
  and a stopping condition. Label replay evidence and reuse unaffected captures.
- Pilot goals are hypotheses to validate, not results to assume. Record failed
  installs, rejected findings, and removals. Phase 24 requires three of five
  pilots meeting its onboarding/30-day retention goals and an independent useful
  catch; unmet goals remain incomplete or require an explicit scope revision.
- Prepare outreach, announcements, and case studies as reviewable drafts.
  Contacting others or publishing requires explicit user authorization; source
  sharing and maintainer attribution also require participant consent. Do not
  add automatic telemetry or treat this roadmap as outreach authorization.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

Read `mcp-sentinel-buildplan.md` first for historical context, including its
non-goals in §11. Resolve current design questions against `ARCHITECTURE.md` and
the active `ROADMAP.md` phase. The product-quality phases extend the original
hackathon scope deliberately; do not let historical stretch goals override
their order or assume a planned contract change has already shipped.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked and what the active phase calls for. Fix
  detection correctness before pulling forward independent AI discovery or
  multi-step exploit work.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested — e.g. don't build a general-purpose plugin-loading system for rules when a flat list of rule modules does the job; don't add languages beyond the supported Python and static-only TypeScript scope.
- No error handling for impossible scenarios — but do fail loudly (not silently) when a scan target is malformed or the sandbox fails to start; a scanner that silently produces an empty report on failure is worse than one that errors.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes,
simplify. Check the current roadmap's deferred/out-of-scope work and the
historical non-goals in `mcp-sentinel-buildplan.md` §11 before adding scope.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the current task or the current phase's checklist item.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add a rule for hardcoded secrets" → "Write a fixture snippet containing a hardcoded API key, assert the rule flags it as SENT-005/Critical, and write a clean-fixture snippet that the rule does NOT flag."
- "Add SARIF output" → "Run the CLI against the vulnerable fixture with `--format sarif`, and assert the output validates against the SARIF 2.1.0 schema."
- "Add the dynamic prober" → "Assert a probe sending an out-of-scope tool call against the vulnerable fixture server produces a SENT-008 finding, and that the same probe against the clean fixture produces none."

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it
detect bad stuff") require constant clarification. Keep paired vulnerable/clean
fixtures as regression controls and add the independent vulnerable/fixed cases
and held-out measurements required by the active phase. Product gates also need
actual maintainer outcomes; a passing test suite cannot substitute for them.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, phase boundaries stay respected, and clarifying questions come before implementation rather than after mistakes.
