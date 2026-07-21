# AGENTS.md

Project-specific context and instructions for **MCP Sentinel**, merged with a set of general behavioral guidelines (sections 1-4 below, adapted from [andrej-karpathy-skills/CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)) aimed at reducing common LLM coding mistakes: unstated assumptions, speculative complexity, unrelated edits, and vague success criteria.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## Project

**MCP Sentinel** — a build-time static/dynamic security scanner for MCP (Model Context Protocol) servers, mapped to the OWASP Agentic Top 10, shipped as a CLI tool and a GitHub Action that outputs SARIF.

Sentinel is one of three components of a larger suite called **SecureMCP**:
1. **SecureMCP Gateway** — runtime zero-trust enforcement gateway (separate repo, out of scope here).
2. **MCP Sentinel** *(this repo)* — build-time scanner.
3. **SecureMCP Identity** — short-lived credential broker (separate repo, out of scope here).

Sentinel answers one question: *"Does this MCP server have exploitable vulnerabilities before I ever run it?"* It does this via static analysis (AST/pattern rules over source + manifests) and lightweight dynamic analysis (adversarial probes against a sandboxed instance of the target server), with every finding tagged to an OWASP Agentic Top 10 category.

Full build context, architecture, phased plan, and demo script live in `mcp-sentinel-buildplan.md` — read that first.

## Where things live

- `mcp-sentinel-buildplan.md` — the full brief: what Sentinel does, tech stack, repo layout, OWASP mapping table, phased build plan, demo script. Read this first.
- `README.md` — quickstart, install, usage examples (write once Phase 0 scaffolding exists).
- `src/sentinel/static/rules/` — one file per detection rule; each rule is independently testable and tagged with its OWASP Agentic Top 10 category (`src/sentinel/owasp_mapping.py` holds the canonical rule-id → category map).
- `src/sentinel/dynamic/` — the sandbox launcher (`sandbox.py`) and adversarial prober (`prober.py`).
- `src/sentinel/report/` — `sarif.py` (SARIF 2.1.0 writer) and `console.py` (human-readable terminal report).
- `tests/fixtures/vulnerable_server/` and `tests/fixtures/clean_server/` — the reference sample servers every rule is tested against.
- `action.yml` — the GitHub Action wrapper around the CLI.

Don't load the full dynamic-analysis sandbox code when working on a static rule, and vice versa — pull in only what's relevant to the current task. Both stay decoupled through the shared report/finding schema.

## Conventions

- Python, `click` or `typer` for the CLI — pick one in Phase 0 and stay consistent; don't mix.
- Every rule (static or dynamic) produces a finding using **one canonical Finding shape** (rule id, severity, OWASP category, file/location, message, remediation hint) — don't invent a bespoke shape per rule or per output format. `sarif.py` and `console.py` both consume the same Finding objects.
- Rule IDs are stable once assigned (`SENT-001`, `SENT-002`, …) — SARIF output and any historical comparisons depend on IDs not changing meaning. Add new rules with new IDs; don't renumber.
- Static analysis must never execute target code. Dynamic analysis always runs the target server in a sandbox/subprocess/container — never against a live/production endpoint by default.
- Prefer embedding an existing engine (e.g. `semgrep`) for static pattern rules over hand-rolling a full AST walker — this is a deliberate hackathon-scope decision, not a shortcut to "fix later."
- No rule should require live network access to third-party services to run — Sentinel must work fully offline against a local repo.
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
keeping them visible and fail-on eligible. Normal scans and `sentinel demo`
run Phase 3 dynamic probing and return `3` only when analysis is incomplete.

## Current phase

See `ROADMAP.md` for the authoritative phase order. Work through phases in
order: GPT semantic review follows the static engine, then dynamic probing, then
the GitHub Action. Update this section as each verification gate passes.

- [x] Phase 0 — repo scaffold, incomplete `sentinel scan`, valid report shells and schemas
- [x] Phase 1 — hybrid static engine, `SENT-001`–`SENT-007`, paired fixtures
- [x] Phase 2 — GPT semantic review, live captures, replay demo, and static ablation
- [x] Phase 3 — Docker sandbox and four adversarial probes
- [x] Phase 4 — GitHub Action and live SARIF upload
- [ ] Phase 5 — console/report polish and judged demo
- [ ] Phase 6 — fixture-scoped exploit-confirmation stretch

Phase 5 is **incomplete**. Its repository implementation and verification gates
are complete, but the following manual/external submission work remains:

- Record and publish the public YouTube demo (under three minutes, with audio).
- Complete and submit the Devpost entry.

The `v0.1.0` GitHub Release is published with the tested wheel, and `/feedback`
was submitted from the primary Codex thread recorded in `README.md`. Do not mark
Phase 5 complete or begin Phase 6 until both remaining items are finished.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

This is a hackathon-scoped build — most design questions should be resolved by checking `mcp-sentinel-buildplan.md` first (it already covers architecture, stack choices, and explicit non-goals in §10). If a design question genuinely isn't covered there, that's exactly the kind of thing to surface rather than silently decide.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked, and beyond what the current phase (see "Current phase" above) calls for. Don't pull forward Phase 3's GitHub Action work while still on Phase 1's rule engine.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested — e.g. don't build a general-purpose plugin-loading system for rules when a flat list of rule modules does the job; don't add multi-language support when the hackathon scope is Python MCP servers.
- No error handling for impossible scenarios — but do fail loudly (not silently) when a scan target is malformed or the sandbox fails to start; a scanner that silently produces an empty report on failure is worse than one that errors.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify. Explicit non-goals for this project are listed in `mcp-sentinel-buildplan.md` §10 — check there before adding scope.

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

Strong success criteria let you loop independently. Weak criteria ("make it detect bad stuff") require constant clarification. Use the paired vulnerable/clean fixture servers as the source of truth for "verify: [check]" on every rule, rather than inventing new verification criteria per task.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, phase boundaries stay respected, and clarifying questions come before implementation rather than after mistakes.
