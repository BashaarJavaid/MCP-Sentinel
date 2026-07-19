# Judge demo runbook

## Prerequisites

- Python 3.10, 3.11, or 3.12
- Docker Engine on Linux, or Docker Desktop on macOS/Windows
- Docker Buildx
- `OPENAI_API_KEY` only for the live path

Install the prebuilt wheel with either `pip install mcp_sentinel-0.1.0-*.whl`
or `pipx install mcp_sentinel-0.1.0-*.whl`. Start Docker before the demo.

## Reproducible replay

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

## Live review

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

## Expected beats

1. The scanner finds all seven deterministic fixture rules without executing
   target code.
2. GPT review grounds decisions in supplied source ranges and produces only the
   four approved inert probe templates.
3. Docker executes every probe in a fresh isolated container.
4. The report contains `SENT-001` through `SENT-011`, OWASP mappings,
   remediation, provenance, and visible review mode.
5. `artifacts/phase4-action-evidence.md` links the matching public Security-tab
   proof.

## Under-three-minute narration

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

## Failure fallback and cleanup

- If live GPT access fails, switch to `--replay-review`; never relabel replay as
  live.
- If Docker is unavailable, show the already validated checked artifacts and
  public Phase 4 Action evidence, then state that analysis is incomplete.
- Run `uv run python scripts/reap_orphans.py` after an interrupted Docker demo.
- Re-running the demo atomically refreshes only its two known report files and
  preserves unrelated files in the output directory.

## Manual desktop release checks

On macOS and Windows, install the exact CI wheel with both pip and pipx, run the
replay demo under Docker Desktop, validate both reports, interrupt one run, and
confirm orphan cleanup. The GitHub Action itself remains Ubuntu-only.
