# MCP Sentinel — Full Build Brief & Hackathon Plan

> **Purpose of this document:** This is a complete handoff brief for building **MCP Sentinel** with the help of a GPT-based coding assistant ("Sol"). It contains full context on what Sentinel is, how it fits into the larger SecureMCP suite, the architecture, the build plan, and exactly how ChatGPT/Sol should be used at each phase. Paste this whole file into Sol as the first message of the build session.

---

## 1. Project Identity

**Name:** MCP Sentinel (aliases used in prior planning: SecureMCP Sentinel, securmcp-sentinel)

**One-line description:** A build-time static/dynamic security scanner for MCP (Model Context Protocol) servers, mapped to the OWASP Agentic Top 10, shipped as a CLI tool and a GitHub Action that outputs SARIF.

**Context:** Sentinel is one of three components of a larger suite called **SecureMCP**, a zero-trust agentic AI security architecture. The suite is deliberately split into three independent repos/planes, mirroring how tools like SPIRE and Vault separate concerns:

1. **SecureMCP Gateway** — runtime zero-trust gateway (RBAC/ABAC policy enforcement, live risk scoring, ECDSA-signed audit logging). Operates *while* an agent runs.
2. **MCP Sentinel** *(this project)* — build-time scanner. Operates *before* anything is deployed.
3. **SecureMCP Identity** — short-lived credential broker (OAuth 2.1, Dynamic Client Registration, SPIFFE/SPIRE-style workload identity).

**Why Sentinel was chosen for the hackathon (not Gateway or Identity):**
- Self-contained — no live infrastructure, databases, or long-running services required
- Demos cleanly as a CLI run or a GitHub Action output in a PR — judges can *see* the artifact (a SARIF report / annotated PR) immediately
- Clear, bounded scope achievable in a hackathon timeframe
- Directly reusable as a portfolio piece independent of the rest of the suite

**Suite-level docs that exist and should inform Sentinel's design** (reference these conceptually even if rebuilding fresh for the hackathon):
- `THREAT_MODEL.md` — shared threat model across all three planes
- `SUITE_ARCHITECTURE.md` — documents the three-plane zero-trust design

---

## 2. What Sentinel Actually Does

Sentinel answers one question: **"Does this MCP server have exploitable vulnerabilities before I ever run it?"**

It does this through two complementary passes:

### 2.1 Static Analysis
- Parses an MCP server's source code, tool/resource manifest definitions, and declared permissions/scopes
- Flags dangerous patterns without executing anything:
  - Overly broad tool permission scopes (e.g., a tool declaring filesystem-wide or network-wide access when it only needs read access to one directory)
  - Unsafe deserialization or eval-like patterns in tool handlers
  - Missing input validation/schema enforcement on tool parameters
  - Prompt-injection-susceptible patterns (e.g., tool descriptions or outputs that get blindly re-injected into the model context without sanitization)
  - Hardcoded secrets/credentials in server code or config
  - Missing or overly permissive CORS / auth middleware on server endpoints
  - Unsigned or unverified tool manifests

### 2.2 Dynamic Analysis (lightweight, hackathon-scoped)
- Spins up the target MCP server in a sandboxed/ephemeral mode
- Sends a battery of adversarial probe requests (malformed inputs, oversized payloads, injection payloads in tool arguments, attempts to call tools outside declared scope)
- Observes actual behavior vs. declared behavior — does the server actually enforce what its manifest claims?

### 2.3 OWASP Agentic Top 10 Mapping
Every finding Sentinel produces is tagged against a category in the OWASP Agentic Top 10 (e.g., "Excessive Agency," "Tool Misuse," "Insecure Output Handling," "Prompt Injection via Tool Response," etc.). This mapping is what gives the tool credibility and makes findings legible to security teams who already think in OWASP terms.

---

## 3. Deliverables

1. **CLI tool** (`sentinel scan <path-or-url>`) — runs static + dynamic checks against a local MCP server repo or a running MCP endpoint, prints a human-readable report to stdout, and can emit SARIF (`--format sarif`)
2. **GitHub Action** — wraps the CLI, runs on PRs, uploads SARIF to GitHub's Security tab (Code Scanning), and can be configured to fail the build above a severity threshold
3. **Rule engine** — a set of discrete, independently testable detection rules, each mapped to an OWASP Agentic Top 10 category, versioned so new rules can be added without touching the core engine
4. **GPT-5.6 semantic review layer** — takes raw rule-engine candidates, reads the target server's actual tool schemas/descriptions/code context, and emits validated canonical findings (confirms real issues, suppresses false positives, adds context static rules can't see). This is the guaranteed-to-work spine of the GPT-5.6 integration — see §12.
5. **GPT-5.6 exploit-confirmation layer (scoped stretch goal)** — for findings against the project's own fixture `vulnerable_server`, GPT-5.6 generates a context-specific exploit, the sandbox runs it, and the finding is marked CONFIRMED (with evidence) or LIKELY FALSE POSITIVE. Auto-patch-generation and auto-opened PRs are a further stretch beyond this. See §12.
6. **Demo artifact** — a deliberately vulnerable sample MCP server repo that Sentinel scans live during the demo, producing a visible SARIF report / annotated PR with real findings, including at least one GPT-5.6-confirmed finding

---

## 4. Suggested Tech Stack

- **Language:** Python (consistent with the rest of your stack — FastAPI, LangGraph, RAG work — and Python has the best MCP SDK support today)
- **CLI framework:** `click` or `typer` for ergonomic command structure
- **Static analysis:** AST-based parsing (`ast` module) for Python MCP servers; regex/pattern rules as a fallback for quick wins; consider `semgrep` as an embedded engine for custom rule definitions rather than writing an AST walker from scratch — this saves significant hackathon time
- **Dynamic analysis:** spin up target server in a subprocess or Docker container, use `httpx`/`requests` to send probe payloads against its MCP endpoint
- **SARIF output:** use the `sarif-om` Python package (or hand-roll a minimal SARIF 2.1.0 JSON writer — the schema is well documented and a minimal valid output is not large)
- **Packaging:** `pyproject.toml` + `pip install -e .` for local dev; publish-ready structure even if you don't actually publish to PyPI during the hackathon
- **GitHub Action:** a `action.yml` wrapping a Docker container or composite run steps that install and invoke the CLI
- **Testing:** `pytest` for rule engine unit tests against fixture "vulnerable" and "clean" MCP server snippets

---

## 5. Repo Structure (proposed)

```
mcp-sentinel/
├── action.yml                     # GitHub Action definition
├── pyproject.toml
├── README.md
├── THREAT_MODEL.md                 # carried over / adapted from suite-level doc
├── src/
│   └── sentinel/
│       ├── cli.py                  # entrypoint: sentinel scan ...
│       ├── static/
│       │   ├── rules/              # one file per rule, each tagged w/ OWASP category
│       │   └── engine.py           # loads rules, runs against parsed source
│       ├── dynamic/
│       │   ├── prober.py           # adversarial request generator
│       │   └── sandbox.py          # spins up target server safely
│       ├── report/
│       │   ├── sarif.py            # SARIF 2.1.0 writer
│       │   └── console.py          # human-readable terminal report
│       ├── llm/
│       │   ├── semantic_reviewer.py  # GPT-5.6: candidate -> validated canonical finding
│       │   └── exploit_confirm.py    # GPT-5.6: finding -> context-specific exploit (scoped stretch goal)
│       └── owasp_mapping.py        # canonical rule-id -> OWASP Agentic Top 10 category map
├── tests/
│   ├── fixtures/
│   │   ├── vulnerable_server/      # deliberately broken sample MCP server
│   │   └── clean_server/           # a hardened reference server
│   └── test_rules/
└── demo/
    └── vulnerable_server/          # same or similar to fixtures, used live in demo
```

---

## 6. Phased Build Plan

### Phase 0 — Setup (Day 1, first hour)
- Scaffold repo structure above
- Get `sentinel scan --help` running end-to-end with a no-op scan
- Write the minimal valid SARIF output shell so the pipeline (scan → report) exists before rules do

### Phase 1 — Static Rule Engine (Day 1)
- Implement the AST/pattern-based rule engine
- Write 5–8 concrete rules covering the categories in §2.1
- Build the deliberately vulnerable fixture server that trips every rule
- Get `sentinel scan ./fixtures/vulnerable_server --format sarif` producing a correct, validating SARIF file

### Phase 2 — Dynamic Probing (Day 1–2)
- Implement the sandbox launcher (subprocess or Docker)
- Implement 3–5 adversarial probes (oversized payload, injection in args, out-of-scope tool call, malformed schema)
- Merge dynamic findings into the same report/SARIF pipeline as static findings

### Phase 2.5 — GPT-5.6 Semantic Review (Day 1–2, the guaranteed-to-work spine — see §10)
- Implement `llm/semantic_reviewer.py`: takes raw rule-engine candidates + the target server's actual tool schemas/descriptions, emits validated canonical findings
- Confirm it correctly validates true positives and suppresses at least one seeded false positive in the fixture set
- Merge its output into the same Finding shape/report pipeline as static and dynamic findings

### Phase 3 — GitHub Action Wrapper (Day 2)
- Write `action.yml`
- Test on a real PR against the fixture repo (or a throwaway repo) to confirm SARIF uploads to the Security tab correctly
- Add pass/fail threshold logic (e.g., fail on any "high" severity finding)

### Phase 4 — Polish & Demo Prep (Day 2, final hours)
- Human-readable console report formatting (color-coded severity, OWASP category labels, remediation hints per finding)
- README with quickstart, architecture diagram, and OWASP mapping table
- Rehearse the live demo: run `sentinel scan` against the vulnerable fixture, show the SARIF/PR annotation, narrate 2–3 findings and why they matter — including at least one finding that went through the full "rule flagged it → GPT-5.6 confirmed it" chain

### Phase 4 (stretch) — GPT-5.6 Exploit Confirmation (only if time remains — see §10.3)
- Implement `llm/exploit_confirm.py`, scoped only to `tests/fixtures/vulnerable_server`
- For each confirmed finding, generate one context-specific exploit, run it in the Phase 2 sandbox, mark CONFIRMED (with evidence) or LIKELY FALSE POSITIVE
- Auto-patch generation and auto-opened PR stay out of scope unless this is solid with time to spare

---

## 7. How to Use ChatGPT/Sol Throughout the Build

Sol should be used as an active pair-programmer, not just a code generator. Concrete usage pattern per phase:

- **Phase 0:** Ask Sol to scaffold the full repo structure and boilerplate CLI in one shot from this brief — this is the highest-leverage single prompt, since it removes all the setup friction.
- **Phase 1:** For each rule, give Sol the specific vulnerable pattern description from §2.1 and ask for (a) the detection logic, (b) a fixture snippet that triggers it, and (c) a fixture snippet that doesn't. Do this rule-by-rule rather than asking for all rules at once — smaller, verifiable units are easier to debug under time pressure.
- **Phase 2:** Ask Sol to generate the adversarial probe payloads as a structured list (payload, expected-safe-behavior, expected-vulnerable-behavior) before writing the prober code — this front-loads the security thinking and makes the resulting code easier to review quickly.
- **Phase 3:** GitHub Actions YAML has a lot of small syntactic gotchas (inputs/outputs wiring, permissions blocks for the Security tab upload) — this is a good place to let Sol write the full file and then verify against GitHub's own Action + SARIF upload docs rather than hand-writing it.
- **Phase 4:** Use Sol to draft the README and the demo narration script — feed it the actual findings your scanner produces on the fixture server so the narration is accurate rather than generic.
- **Throughout:** Paste actual error output back to Sol rather than paraphrasing it — exact tracebacks and exact SARIF validation errors get much better fixes than a description of the problem.

---

## 8. OWASP Agentic Top 10 Mapping Table (fill in as rules are built)

| Rule ID | Detection | OWASP Agentic Category | Severity |
|---|---|---|---|
| SENT-001 | Overly broad tool permission scope | Excessive Agency | High |
| SENT-002 | Unsafe eval/deserialization in tool handler | Tool Misuse | Critical |
| SENT-003 | Missing input schema validation | Insecure Output/Input Handling | Medium |
| SENT-004 | Prompt-injection-susceptible tool output re-injection | Prompt Injection via Tool Response | High |
| SENT-005 | Hardcoded secrets in server code/config | Insecure Credential Handling | Critical |
| SENT-006 | Missing/overly permissive auth middleware | Excessive Agency | High |
| SENT-007 | Unsigned/unverified tool manifest | Supply Chain / Manifest Integrity | Medium |
| SENT-008 (dynamic) | Server executes out-of-scope tool call | Excessive Agency | Critical |
| SENT-009 (dynamic) | Server accepts malformed/oversized payload without rejection | Insecure Input Handling | Medium |

*(Expand this table as real rules get implemented — keep rule IDs stable once assigned so SARIF output stays consistent across runs.)*

---

## 9. Demo Script (for judges)

1. One-sentence framing: "Sentinel catches MCP server vulnerabilities before they ever run — think Semgrep or Snyk, but purpose-built for the agentic threat model."
2. Show the vulnerable fixture server's code for ~10 seconds — point out one clearly bad pattern (e.g., a hardcoded secret or an overly broad tool scope).
3. Run `sentinel scan` live.
4. Show the console report — walk through 2–3 findings, naming the OWASP category each maps to.
5. Show the SARIF output rendered in GitHub's Security tab (or a PR annotation) — this is the "this fits into a real workflow" moment.
6. Close with where Sentinel sits in the bigger SecureMCP picture (Gateway + Identity) to show the scope of the broader vision without overclaiming what's built.

---

## 10. GPT-5.6 Integration — Making It Core, Not Decorative

The question that drove this design: *what should GPT-5.6 do inside Sentinel so its use is genuinely core to the product*, not a bolted-on chatbot feature. Two options were weighed.

### 12.1 Option A — Semantic Security Reviewer (the spine)

```
Deterministic rules find candidates
        ↓
GPT-5.6 analyzes code context, finds semantic issues,
and emits validated canonical findings
```

- One GPT-5.6 call per candidate finding, text in/text out. No code execution.
- Risk: low — nothing can crash mid-demo; worst case is a mediocre finding explanation.
- Value: catches business-logic/context issues static rules miss, and kills false positives before they reach the report — a real, defensible improvement over "rules only."
- Fully buildable inside the hackathon window with room to spare.

### 12.2 Option B — Exploit-Confirm-Patch-PR Loop (the differentiator)

```
Sentinel static/dynamic scan
        ↓
Raw findings (SARIF + OWASP Agentic Top 10 tags)
        ↓
GPT-5.6 reads the target MCP server's actual tool schemas/descriptions
and generates a CONTEXT-SPECIFIC exploit attempt (not a generic payload)
        ↓
Sandbox executes the exploit against the target MCP server
        ↓
Exploit succeeds → finding CONFIRMED as real (with evidence/logs)
Exploit fails → finding marked LIKELY FALSE POSITIVE
        ↓
For confirmed findings: GPT-5.6 generates a patch
        ↓
Sandbox re-validates:
  - re-run the SAME exploit against patched code → must now be BLOCKED
  - re-run existing test suite → must show NO REGRESSION
        ↓
Auto-opens a GitHub PR containing:
  - the exploit proof (before)
  - the patch diff
  - the blocked-exploit proof (after)
  - test suite pass confirmation
```

- Scope: 4 chained GPT-5.6 calls + 2 rounds of live code execution + git automation. Every link can fail independently.
- Risk: high, for real reasons, not just "more code to write":
  - Generating a working exploit against arbitrary MCP server code is not a solved problem — it's the hardest, least controllable part of the whole pipeline.
  - Safely sandboxing LLM-authored exploit code, twice (attack, then re-run against the patch), is a genuine security-engineering problem in its own right.
  - Auto-applying an LLM-written patch and opening a PR on "tests still pass" is a claim judges will poke at — one bad patch that happens to pass a thin fixture test suite undercuts the whole pitch.
  - This is the most likely part of the whole project to break live, and the hardest to debug at 2am the night before.
- Ceiling: much higher — this isn't "a scanner," it's an autonomous vulnerability-to-fix agent. It's the pitch that actually differentiates the project as founding-engineer-caliber agentic AI work, not just tooling.

### 12.3 Decision — Layer, Don't Choose

Don't pick one outright — split them by risk, and build in this order:

1. **Build Option A as the guaranteed-to-work spine.** This alone is legitimate and demoable no matter what else lands. This is Phase 2.5 in the build plan (§6) — it sits between static rules and dynamic probing, consuming candidates from either.
2. **Layer in the *first half* of Option B — exploit generation + sandbox execution + confirm/reject — as the differentiator, scoped tightly to the project's own fixture `vulnerable_server`**, where the exact exploit surface is controlled and known ahead of time. This is the empirically-validated, "not just an LLM's opinion" finding-confirmation story, and it's the most defensible part of Option B. This is a scoped Phase 4 stretch item, not a Phase 0–3 dependency.
3. **Treat auto-patch-generation + auto-opened PR as a stretch goal demoed only if it's reliably working by the day before** — not something the whole narration depends on. If it isn't solid, narrating live — "here's the confirmed exploit, and here's what the patch would need to fix" — is still a strong close without needing the PR to auto-open.

This gets the differentiated pitch without betting the whole demo on the riskiest four-hop chain in the plan.

### 12.4 Build Plan Impact

- **New Phase 2.5 — Semantic Review (Day 1–2, after static rules, before/alongside dynamic probing):** implement `llm/semantic_reviewer.py`; feed it real candidate findings from Phase 1's rule engine plus the target server's tool schemas/descriptions; validate that it correctly confirms true positives and suppresses at least one seeded false positive in the fixture set.
- **Phase 4 stretch addition — Exploit Confirmation:** implement `llm/exploit_confirm.py` scoped only to `tests/fixtures/vulnerable_server`; wire it to generate one context-specific exploit per confirmed finding, run it in the existing sandbox (§2.2/`dynamic/sandbox.py`), and mark the finding CONFIRMED or LIKELY FALSE POSITIVE with evidence attached to the report. Auto-patch + auto-PR stays explicitly out of scope unless this is solid with time to spare.
- **Demo script (§9) addition:** narrate at least one finding that went through the full "rule flagged it → GPT-5.6 confirmed it → sandbox proved it" chain — this is the single most differentiating beat in the demo.

---

## 11. Explicit Non-Goals for the Hackathon

To keep scope bounded, the following are **out of scope** for the hackathon build and should be called out as "future work" rather than attempted:
- Full runtime Gateway integration (that's a separate repo/plane)
- SPIFFE/SPIRE-based identity brokering (Identity plane, separate)
- Comprehensive rule coverage of every possible MCP vulnerability class — 8–10 solid, demonstrable rules beat 30 shallow ones
- Publishing the CLI to PyPI or the Action to the GitHub Marketplace (nice-to-have stretch goal only if time remains)

---

## 12. Quick Reference Summary (for Sol's context window if brevity is needed)

Sentinel = build-time MCP server security scanner. Static (AST/pattern rules) + light dynamic (adversarial probes) analysis, plus a GPT-5.6 semantic review layer that validates rule-engine candidates into confirmed findings (the guaranteed spine), with a scoped GPT-5.6 exploit-generation + sandbox-confirmation layer against the project's own fixture server as the stretch-goal differentiator (auto-patch/auto-PR out of scope unless time allows). Findings mapped to OWASP Agentic Top 10. Ships as CLI + GitHub Action producing SARIF. Part of a larger SecureMCP suite (Gateway = runtime enforcement, Identity = credential brokering) but those are out of scope here. Python stack, `click`/`typer` CLI, optional `semgrep` embedding for static rules, `sarif-om` or hand-rolled SARIF writer, `pytest` fixtures of vulnerable/clean sample servers. Build order: scaffold → static rules → GPT-5.6 semantic review → dynamic probes → GitHub Action → polish/demo → (stretch) exploit confirmation.
