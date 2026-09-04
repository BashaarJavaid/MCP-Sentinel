# Configuration

## Precedence

Every scanner or GPT value resolves independently in this order:

1. CLI option.
2. `SENTINEL_*` environment variable.
3. Target-root `sentinel.toml`.
4. Built-in default.

Launch and installation details belong in `sentinel.target.yaml`; capability
grants belong in `sentinel.permissions.yaml`. `sentinel.toml` contains scanner,
GPT, sandbox, and `SENT-005` allowlist settings only.

```toml
[scanner]
format = "console"
fail_on = "high"
rules = []
ignore_paths = []
target_config = "sentinel.target.yaml"
max_findings_per_scan = 500

[llm]
model = "gpt-5.6-sol"
reasoning_effort = "medium"
timeout_seconds = 30
retries = 2
max_concurrency = 5
cache_enabled = true

[sandbox]
allowed_registries = ["pypi.org", "files.pythonhosted.org"]
```

Use `--rules SENT-001,SENT-005,-SENT-007` to include or exclude rules. The
default threshold is `--fail-on high`; accepted values are `critical`, `high`,
`medium`, `low`, and `informational`.

## Analysis tiers

| Tier | Command | What runs |
|---|---|---|
| Rules-only | `sentinel scan . --static-only --allow-degraded` | Static rules; candidates remain visible and fail-on eligible |
| Static + GPT review | `sentinel scan . --static-only` | Static rules and required semantic review |
| Full dynamic proof | `sentinel scan .` | Static rules, GPT review, and four Docker probes |

`--static-only` still requires GPT review unless `--allow-degraded` is explicit.
TypeScript targets support only the first two tiers.

## GPT review and endpoint trust

Public OpenAI review accepts `gpt-5.6-sol` or its `gpt-5.6` alias with `low` or
`medium` reasoning effort. Set `OPENAI_API_KEY`; Sentinel does not print,
persist, forward to the target, or ask the Responses API to store that key or
the response.

The reviewer uses the Responses API with `store: false`, strict Structured
Outputs, bounded redacted context, and independently validated evidence ranges.
Sentinel's cost calculation preserves the rates recorded on 2026-09-04:
$4/M input, $0.40/M cached input, and $20/M output, with cache writes at 1.25×
input. See the official [GPT-5.6 Sol model and pricing
page](https://developers.openai.com/api/docs/models/gpt-5.6-sol) and [Responses
API create reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create).

Responses-compatible organizational and Azure OpenAI v1 endpoints can be set
with `--llm-base-url` or `SENTINEL_LLM_BASE_URL`. URLs must end in `/v1`; HTTPS
is required except for literal loopback hosts. Only bearer authentication through
`OPENAI_API_KEY` is supported. A repository-controlled endpoint in
`sentinel.toml` additionally requires `--trust-llm-endpoint` or
`SENTINEL_TRUST_LLM_ENDPOINT=true`. Reports retain only endpoint mode and a
SHA-256 URL hash. Compatible-endpoint token counts are retained, but pricing is
reported as unavailable.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Complete; no finding reached the failure threshold |
| `1` | Complete; one or more findings reached the threshold |
| `2` | Target, usage, framework, transport, or configuration error |
| `3` | GPT, Docker, Semgrep, report-validation, or internal failure |

Treat `0` and `1` as completed scans. Treat `2` and `3` as missing analysis.

## Baselines

Create a baseline only from a complete native JSON report:

```bash
sentinel scan . --allow-degraded --format json --output sentinel-baseline.json
sentinel scan . --allow-degraded --baseline sentinel-baseline.json
```

The baseline must use the same ordered rules and static/full mode. Matched
findings remain visible but do not affect `--fail-on`; resolved findings appear
as an aggregate count. Sentinel never updates a baseline automatically. Generate
a separate candidate file, review its diff, then replace the accepted baseline.

## Inline suppressions

Python and TypeScript source may suppress one static finding with a documented
reason:

```python
# sentinel: ignore[SENT-005] reason=test credential is inert and rotated
api_key = "ghp_example"
```

```typescript
const apiKey = "ghp_example"; // sentinel: ignore[SENT-005] reason=test fixture
```

A standalone directive binds the next physical line; a trailing directive binds
its line. Only `SENT-001`–`SENT-007` are supported. Suppressed findings remain
auditable in console, JSON, and SARIF. Invalid directives fail; unused valid
directives warn.

## Pre-commit

```yaml
repos:
  - repo: https://github.com/BashaarJavaid/MCP-Sentinel
    rev: v1.2.0
    hooks:
      - id: mcp-sentinel
```

The hook runs the Rules-only tier. Add `args: [--baseline,
sentinel-baseline.json]` to use a reviewed baseline.
