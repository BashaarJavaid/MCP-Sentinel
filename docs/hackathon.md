# Project history

This page preserves the original submission, demonstration, release, and
assistant-collaboration record. It is historical evidence, not the current
installation or operations guide.

## Completion record

Phase 5 is **complete**. Its repository implementation and verification gates
passed, the `v0.1.0` GitHub Release was published with the tested wheel,
`/feedback` was submitted from the primary Codex thread recorded in `README.md`,
and the public YouTube demo and Devpost submission were completed.

Phase 5 is **complete**. The repository implementation and automated
verification gates passed, the `v0.1.0` GitHub Release was published with the
tested wheel, `/feedback` was submitted from the primary Codex thread recorded
in `README.md`, and the public YouTube demo and Devpost submission were
completed. Phase 6 is complete and Phase 7 is unblocked.

Phase 6 is **complete**: its implementation, local macOS gates, and expanded
Linux, macOS, and Windows CI matrices pass on Python 3.10–3.13. Phase 7 is
**complete**: the signed `v0.2.0`
[release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33795399096)
published and verified the canonical wheel and sdist on
[TestPyPI](https://test.pypi.org/project/portunusmcp-sentinel/0.2.0/) and
[PyPI](https://pypi.org/project/portunusmcp-sentinel/0.2.0/) through OIDC, and
all 12 public pipx/uv install jobs passed. Phase 8 is **complete**: the immutable
[`v1.0.0` release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.0.0)
published the [Marketplace Action](https://github.com/marketplace/actions/mcp-sentinel),
the signed `v1` alias resolves to the release commit, and the paired
[external proof](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33808213435)
passed. Phase 9 is **complete**: the
[onboarding gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33816774614)
passed the full quality and installed-wheel matrices, then generated a clean
fixture configuration with `sentinel init` and completed `sentinel scan .` in
Docker without an API key. Phase 10 is **complete**: the
[configurable-endpoint gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33835113247)
passed the full Linux, macOS, and Windows Python 3.10–3.13 quality matrix,
canonical distributions, isolated wheel installs, and installed-wheel Docker
replay without paid API calls.

Phase 11 is **complete**: its budget-capped live TypeScript GPT smoke passed, and
the [hosted gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33845514399)
passed the full Linux, macOS, and Windows Python 3.10–3.13 quality and
installed-wheel matrices, canonical distributions, and installed-wheel Docker
replay.

Phase 12 is **complete**: the signed
[`v1.2.0` release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.2.0)
passed trusted publication and provenance verification, the public pre-commit
hook passed the hosted OS/Python matrix, and the external
[exact-tag](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33897900585)
and signed [`v1` alias](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33898189505)
baseline proofs passed. Complete evidence is recorded in
[`artifacts/phase12-adoption-evidence.md`](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase12-adoption-evidence.md).

Later distribution and adoption evidence remains in:

- [`artifacts/phase4-action-evidence.md`](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase4-action-evidence.md)
- [`artifacts/phase8-marketplace-evidence.md`](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase8-marketplace-evidence.md)
- [`artifacts/phase12-adoption-evidence.md`](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase12-adoption-evidence.md)

## Human, Codex, and GPT contribution

The human owner defined product scope, architecture, trust boundaries, threat
model, phase gates, and release decisions.

### How Codex was used

Codex was the implementation partner for the entire build. The working pattern
was design-first: before any implementation, a long Codex session worked through
scope and architecture — MVP versus deferred features, how findings map to OWASP
categories, the allowed state transitions for a finding, and whether semantic
review should be optional (it should not; a flag would have made it decorative).
That session is the architectural backbone the rest of the project was built
against.

From there Codex built the static rule engine and Semgrep adapter, the Docker
sandbox and probe harness, the reporting pipeline, the SARIF validator, the
cross-platform test matrix, artifact automation, and the documentation. It also
did the debugging on the harder cross-platform problems — Semgrep output parsing
and runtime-file isolation on Windows, and the two rounds of SARIF fixes needed
before GitHub code scanning would render the reports correctly.

The repository ships an `AGENTS.md` that constrains how Codex works in this
codebase: ask rather than assume, no speculative complexity, no unrelated edits,
explicit success criteria. Design decisions stayed with the human owner; Codex
accelerated everything downstream of them.

### How GPT-5.6 was used

GPT-5.6 is inside the shipped product, not just the build. It is load-bearing at
scan time: it reads the server code, decides which static candidates are real
findings, and orders and parameterizes the four probes the sandbox runs — turn it
off and you get different results. It does not replace the deterministic
detectors or the Docker boundary.

The constraints are the design: strict Structured Outputs against a versioned
schema, `store: false`, redacted and capped context, and host-validated source
ranges, so the model cannot cite a line that does not exist, invent a finding
outside the rule set, or emit executable probe code. `artifacts/gpt-ablation.json`
preserves the measured comparison of rules-only, GPT-reviewed, and dynamically
confirmed outcomes.

### Codex session record

Primary Codex `/feedback` thread for core implementation:
`019f70e6-a5fb-7f13-8eae-bca041fc37ad`.

Supporting implementation threads:

- `019f7469-e3ed-75a0-9906-7059299b1484`
- `019f741f-cf91-7000-b12c-e9aa2a50ff03`
- `019f77a1-f2f0-7ab2-9a5d-e72fa1ebc40e`

The Phase 5 `/feedback` record was submitted from the primary thread above.

## Release evidence

### v1.2.0 release and adoption evidence

The signed [`v1.2.0` GitHub Release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.2.0)
published the exact package through the trusted
[release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33895746398).
The [MCP Sentinel Marketplace listing](https://github.com/marketplace/actions/mcp-sentinel)
is backed by the signed `v1` alias. The external
[exact-tag](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33897900585)
and [`v1` alias](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33898189505)
proofs passed baseline and pre-commit adoption workflows. Package hashes,
provenance, tag targets, retained SARIF, cost, and verification details are
recorded in
[`artifacts/phase12-adoption-evidence.md`](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/artifacts/phase12-adoption-evidence.md).

PyPI serves wheel `portunusmcp_sentinel-1.2.0-py3-none-any.whl` with SHA-256
`ec3fef5ee383f46bf9a1e38d707c3810ddeb5e7414c89d9c7835b675c78acc7a`
and sdist `portunusmcp_sentinel-1.2.0.tar.gz` with SHA-256
`034a4075688fcdf605369540623d5219535d9b920ba1a4fe7c8ecb828322e2ea`.

### Historical v1.0.0 release evidence

PyPI serves wheel `portunusmcp_sentinel-1.0.0-py3-none-any.whl` with SHA-256
`8fe8af788a1446e40b1f54509426d3641585f4d1c6b3594e78d5c36573763396` and
sdist `portunusmcp_sentinel-1.0.0.tar.gz` with SHA-256
`6514e508bb81e52f90617d090f4d64c07b5e5630f6c9e1f77e6150226115ad78`.

### Historical v0.2.0 release evidence

The signed-tag [Release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33795399096)
published the tested wheel and sdist through OIDC to
[TestPyPI](https://test.pypi.org/project/portunusmcp-sentinel/0.2.0/) and then
[PyPI](https://pypi.org/project/portunusmcp-sentinel/0.2.0/). It verified both
published hashes and attestations ([wheel](https://pypi.org/integrity/portunusmcp-sentinel/0.2.0/portunusmcp_sentinel-0.2.0-py3-none-any.whl/provenance),
[sdist](https://pypi.org/integrity/portunusmcp-sentinel/0.2.0/portunusmcp_sentinel-0.2.0.tar.gz/provenance))
and passed exact-version pipx and uv installs on Linux, macOS, and Windows with
Python 3.10–3.13.

### Historical v0.1.0 artifact

The earlier [`v0.1.0` GitHub Release](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v0.1.0)
contains `mcp_sentinel-0.1.0-py3-none-any.whl`, produced by the
[successful release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/29686427335).
Its SHA-256 digest is
`4672e63413e87bf750113c06a21133162d00f1e71ca6259a8394028c22b677aa`.

`artifacts/example.sarif` is retained as historical live schema-1.2 evidence.
`artifacts/gpt-ablation.json` compares rules-only, GPT-reviewed, and dynamically
confirmed outcomes over the versioned truth set.

## Judge demo runbook

### Prerequisites

- Python 3.10, 3.11, or 3.12 for the current public v0.1.0 wheel
- Python 3.10, 3.11, 3.12, or 3.13 for the local v1.0.0 artifact
- Python 3.10, 3.11, or 3.12 for dynamically scanned targets
- Docker Engine on Linux, or Docker Desktop on macOS/Windows
- Docker Buildx
- `OPENAI_API_KEY` only for the live path

The Phase 11 live TypeScript checkpoint is separately capped and never runs the
Node target:

```bash
python scripts/capture_gpt_reviews.py typescript-smoke --live --max-usd 0.25
```

Install the prebuilt wheel with either `pip install mcp_sentinel-0.1.0-*.whl`
or `pipx install mcp_sentinel-0.1.0-*.whl`. Start Docker before the demo.

### Reproducible replay

```bash
sentinel demo --replay-review --verbose
```

Replay uses checked GPT-5.6 responses but still executes schema validation,
probe planning, all four Docker probes, dynamic review parsing, merging, console
rendering, JSON rendering, and SARIF validation. The console must say
`RECORDED GPT REPLAY — NO LIVE MODEL CALL`.

Validated reports are written to:

- `sentinel-demo-results/report.json`
- `sentinel-demo-results/report.sarif`

### Live review

```bash
export OPENAI_API_KEY=your-key
sentinel demo --verbose
```

The live report must identify requested and returned `gpt-5.6-sol`, token use,
latency, cache state, and cost. Do not expose the API key in shell history,
recordings, target configuration, or reports.

The release-evidence path is separately budget gated:

```bash
MAX_USD=0.50 make artifacts-live
```

It reserves each request before sending and refuses to exceed the scan-wide
US$0.50 ceiling.

### Expected beats

1. The scanner finds all seven deterministic fixture rules without executing
   target code.
2. GPT review grounds decisions in supplied source ranges and produces only the
   four approved inert probe templates.
3. Docker executes every probe in a fresh isolated container.
4. The report contains `SENT-001` through `SENT-011`, OWASP mappings,
   remediation, provenance, and visible review mode.
5. `artifacts/phase4-action-evidence.md` links the matching public Security-tab
   proof.

### Under-three-minute narration

**0:00–0:20 — Frame the problem.** “MCP Sentinel catches exploitable MCP server
vulnerabilities before deployment. It combines deterministic source rules,
GPT-5.6 semantic review, and isolated runtime proof, then emits SARIF for CI.”

**0:20–0:45 — Show the fixture.** Point to the unsafe calculator and its direct
`eval` call, plus the deliberately broad or missing security configuration.

**0:45–1:20 — Run Sentinel.** Start `sentinel demo --replay-review --verbose`.
Call out the replay banner: it is recorded GPT evidence, not a live-model claim,
while Docker probing is still real.

**1:20–2:05 — Explain one chain.** Walk through `SENT-002`: Semgrep identifies
tool input reaching `eval`; GPT cites the exact range and prioritizes the
injection probe; the Docker scratch canary proves execution; the final finding
retains both static and dynamic provenance.

**2:05–2:30 — Show workflow fit.** Open `report.sarif` or the linked public
Security tab and point to stable rule IDs, OWASP categories, and remediation.

**2:30–2:50 — Clarify AI ownership.** The human owner chose scope, architecture,
security boundaries, and release decisions. Codex accelerated implementation,
testing, debugging, and docs. GPT changes scan-time review and safe probe
planning; it does not execute arbitrary generated code.

**2:50–3:00 — Close.** “Sentinel is the build-time plane of SecureMCP: find and
prove MCP vulnerabilities before runtime controls ever need to contain them.”

### Failure fallback and cleanup

- If live GPT access fails, switch to `--replay-review`; never relabel replay as
  live.
- If Docker is unavailable, show the already validated checked artifacts and
  public Phase 4 Action evidence, then state that analysis is incomplete.
- Run `uv run python scripts/reap_orphans.py` after an interrupted Docker demo.
- Re-running the demo atomically refreshes only its two known report files and
  preserves unrelated files in the output directory.

### Manual desktop release checks

On macOS and Windows, install the exact CI wheel with both pip and pipx, run the
replay demo under Docker Desktop, validate both reports, interrupt one run, and
confirm orphan cleanup. The GitHub Action itself remains Ubuntu-only.
