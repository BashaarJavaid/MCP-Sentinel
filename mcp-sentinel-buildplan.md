# MCP Sentinel — Full Build Brief & Hackathon Plan

> **Purpose of this document:** This is a complete handoff brief for building **MCP Sentinel** with the help of a GPT-based coding assistant ("Sol"). It contains full context on what Sentinel is, how it fits into the larger SecureMCP suite, the architecture, the build plan, and exactly how ChatGPT/Sol should be used at each phase. Paste this whole file into Sol as the first message of the build session.

> **Current authority:** Phase numbering and release gates in this brief have
> been reconciled with the implemented system. `ARCHITECTURE.md` owns accepted
> contracts and `ROADMAP.md` owns gate status if either document becomes more
> specific than this original handoff.

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

1. **CLI tool** (`sentinel scan <path>`) — runs static and dynamic checks against a local Python MCP repository and emits console, JSON, or SARIF output
2. **GitHub Action** — wraps the CLI, runs on PRs, uploads SARIF to GitHub's Security tab (Code Scanning), and can be configured to fail the build above a severity threshold
3. **Rule engine** — a set of discrete, independently testable detection rules, each mapped to an OWASP Agentic Top 10 category, versioned so new rules can be added without touching the core engine
4. **GPT-5.6 semantic review layer** — takes raw rule-engine candidates, reads the target server's actual tool schemas/descriptions/code context, and emits validated canonical findings (confirms real issues, suppresses false positives, adds context static rules can't see). This is the guaranteed-to-work spine of the GPT-5.6 integration — see §10.
5. **GPT-5.6 exploit-confirmation layer (scoped stretch goal)** — for findings against the project's own fixture `vulnerable_server`, GPT-5.6 generates a context-specific exploit, the sandbox runs it, and the finding is marked CONFIRMED (with evidence) or LIKELY FALSE POSITIVE. Auto-patch-generation and auto-opened PRs are a further stretch beyond this. See §10.
6. **Demo artifact** — a deliberately vulnerable sample MCP server repo that Sentinel scans live during the demo, producing a visible SARIF report / annotated PR with real findings, including at least one GPT-5.6-confirmed finding

---

## 4. Suggested Tech Stack

- **Language:** Python (consistent with the rest of your stack — FastAPI, LangGraph, RAG work — and Python has the best MCP SDK support today)
- **CLI framework:** Typer
- **Static analysis:** MCP-aware Python AST analysis plus pinned Semgrep rules
- **Dynamic analysis:** fresh Docker containers using MCP stdio and four fixed probes
- **SARIF output:** `sarif-om` objects plus offline SARIF 2.1.0 validation
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

### Phase 0 — Scaffold and contracts
- Establish the Typer CLI, canonical Finding/report schemas, valid empty report
  shells, vendored validators, fixtures, and packaging boundaries.

### Phase 1 — Hybrid static engine
- Implement `SENT-001` through `SENT-007` with paired vulnerable/clean fixtures,
  permanent OWASP mappings, Semgrep/AST boundaries, and offline-valid SARIF.

### Phase 2 — GPT-5.6 semantic review
- Review every deterministic candidate through strict Responses API Structured
  Outputs, grounded evidence references, safe probe planning, live checkpoints,
  checked replay cassettes, and a versioned static ablation.

### Phase 3 — Docker dynamic probing
- Run `SENT-008` through `SENT-011` in fresh isolated containers, review the
  resulting evidence, merge provenance, and prove cleanup and failure posture.

### Phase 4 — GitHub Action and SARIF integration
- Wrap the same CLI pipeline, validate before upload, preserve exit semantics,
  handle fork secrets visibly, and retain a public Security-tab proof.

### Phase 5 — Polish and judged demo
- Polish console/report presentation and errors; package fixtures, schemas, and
  cassettes; finish live/replay demo paths; generate judge artifacts; reconcile
  docs and licenses; and pass clean cross-platform distribution gates.

### Phase 6 — Conditional exploit-confirmation stretch
- Begin only after every Phase 0–5 gate is stable. Keep fixture-scoped exploit
  confirmation isolated from the required demo; auto-patching and auto-PRs remain
  out of scope unless separately approved and proven reliable.

---

## 7. How to Use ChatGPT/Sol Throughout the Build

Sol should be used as an active pair-programmer, not just a code generator. Concrete usage pattern per phase:

- **Phase 0:** Scaffold CLI, schemas, validators, fixtures, and package boundaries.
- **Phase 1:** Build and accept static rules one at a time with paired fixtures.
- **Phase 2:** Implement and evaluate the grounded GPT contract with live captures
  only at approved cost gates.
- **Phase 3:** Design fixed probe expectations before implementing Docker
  execution and cleanup.
- **Phase 4:** Verify the composite Action and real SARIF upload against GitHub.
- **Phase 5:** Draft public docs and narration only from actual final reports;
  exercise replay, wheel installation, and clean-checkout gates before live proof.
- **Throughout:** Paste actual error output back to Sol rather than paraphrasing it — exact tracebacks and exact SARIF validation errors get much better fixes than a description of the problem.

---

## 8. OWASP Agentic Top 10 Mapping Table (fill in as rules are built)

| Rule ID | Detection | OWASP Agentic Category | Severity |
|---|---|---|---|
| SENT-001 | Overly broad tool permission scope | ASI03:2026 Identity & Privilege Abuse | High |
| SENT-002 | Tool input reaches unsafe execution | ASI05:2026 Unexpected Code Execution | Critical |
| SENT-003 | Missing tool input validation | ASI02:2026 Tool Misuse & Exploitation | Medium |
| SENT-004 | Unsanitized tool content enters a prompt | ASI01:2026 Agent Goal Hijack | High |
| SENT-005 | Hardcoded credential | ASI03:2026 Identity & Privilege Abuse | Critical |
| SENT-006 | Missing or ineffective route authentication | ASI03:2026 Identity & Privilege Abuse | High |
| SENT-007 | Unverified tool manifest | ASI04:2026 Agentic Supply Chain Vulnerabilities | Medium |
| SENT-008 | Out-of-scope tool execution | ASI02:2026 Tool Misuse & Exploitation | Critical |
| SENT-009 | Oversized argument accepted | ASI05:2026 Unexpected Code Execution | Medium |
| SENT-010 | Injection payload executed | ASI05:2026 Unexpected Code Execution | Critical |
| SENT-011 | Malformed schema input processed | ASI02:2026 Tool Misuse & Exploitation | Low |

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

### 10.1 Option A — Semantic Security Reviewer (the spine)

```
Deterministic rules find candidates
        ↓
GPT-5.6 analyzes code context, finds semantic issues,
and emits validated canonical findings
```

- Candidates are reviewed in bounded GPT-5.6 batches, with text in/text out and
  no model-authored code execution.
- Risk: low — nothing can crash mid-demo; worst case is a mediocre finding explanation.
- Value: catches business-logic/context issues static rules miss, and kills false positives before they reach the report — a real, defensible improvement over "rules only."
- Fully buildable inside the hackathon window with room to spare.

### 10.2 Option B — Exploit-Confirm-Patch-PR Loop (the differentiator)

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

### 10.3 Decision — Layer, Don't Choose

Don't pick one outright — split them by risk, and build in this order:

1. **Build Option A as the guaranteed-to-work spine.** This is Phase 2; it sits
   between static rules and dynamic probing and also reviews dynamic evidence.
2. **Layer fixture-scoped exploit confirmation only as Phase 6 stretch work.**
   Required Phase 3 uses permanent inert probes, not LLM-authored exploit code.
3. **Treat auto-patch-generation + auto-opened PR as a stretch goal demoed only if it's reliably working by the day before** — not something the whole narration depends on. If it isn't solid, narrating live — "here's the confirmed exploit, and here's what the patch would need to fix" — is still a strong close without needing the PR to auto-open.

This gets the differentiated pitch without betting the whole demo on the riskiest four-hop chain in the plan.

### 10.4 Build Plan Impact

- **Phase 2 — Semantic Review:** implement `llm/semantic_reviewer.py`; feed it
  Phase 1 candidates and real tool schemas; prove confirmation, visible
  suppression, abstention, and constrained probe prioritization.
- **Phase 6 — Exploit Confirmation:** if separately entered, keep generation and
  execution fixture-scoped and unable to destabilize the Phase 0–5 pipeline.
- **Demo script (§9) addition:** narrate at least one finding that went through the full "rule flagged it → GPT-5.6 confirmed it → sandbox proved it" chain — this is the single most differentiating beat in the demo.

---

## 11. Explicit Non-Goals for the Hackathon

To keep scope bounded, the following are **out of scope** for the hackathon build and should be called out as "future work" rather than attempted:
- Full runtime Gateway integration (that's a separate repo/plane)
- SPIFFE/SPIRE-based identity brokering (Identity plane, separate)
- Comprehensive rule coverage of every possible MCP vulnerability class — the
  current 11 solid, demonstrable rules are preferable to 30 shallow ones
- Publishing the CLI to PyPI or the Action to the GitHub Marketplace (nice-to-have stretch goal only if time remains)

---

## 12. Quick Reference Summary (for Sol's context window if brevity is needed)

Sentinel is a build-time security scanner for local Python MCP servers. Its
hybrid AST and pinned-Semgrep static engine feeds bounded candidates through a
required GPT-5.6 semantic review, then fresh Docker-contained stdio probes test
the reviewed attack surface. All canonical findings map to the OWASP Agentic
Top 10 and feed the Typer CLI's console, JSON, and offline-validated SARIF 2.1.0
reports. Sentinel ships as that CLI plus a GitHub Action; the SecureMCP Gateway
and Identity planes remain separate. Build order: scaffold → static rules → GPT
semantic review → dynamic probes → GitHub Action → polish/demo → optional,
fixture-scoped exploit confirmation.
