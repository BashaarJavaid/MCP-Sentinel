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
rules_only = false
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
| Rules-only | `sentinel scan . --rules-only` | Static rules; candidates remain visible and fail-on eligible |
| Static + GPT review | `sentinel scan . --static-only` | Static rules and required semantic review |
| Full dynamic proof | `sentinel scan .` | Static rules, GPT review, and four Docker probes |

`--rules-only/--no-rules-only`, `SENTINEL_RULES_ONLY`, and `[scanner].rules_only`
use CLI > environment > project > default precedence. The default is `false`.
Environment booleans accept `true`, `false`, `1`, and `0` (case-insensitive).
Rules-only implies static execution and bypasses model clients, cache, network,
Docker, runtime configuration, and target execution. LLM values, endpoint
settings, ambient OpenAI routing, and trust acknowledgments are inactive and
ignored. Scanner configuration, TOML/CLI syntax, supported-target validation,
and filesystem boundaries remain enforced.

`--static-only`, `--allow-degraded`, and `--target-launch-cmd` have no additional
effect with rules-only. `--no-rules-only` explicitly restores the normal selection;
`sentinel demo` always overrides inherited rules-only configuration.

`--static-only` retains GPT review. `--allow-degraded` permits unavailable review
but does not disable calls when credentials are available.
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
| `3` | Incomplete probes or GPT, Docker, Semgrep, report-validation, or internal failure |

Treat `0` and `1` as completed scans. Treat `2` and `3` as missing analysis.

## Baselines

Create a baseline only from a complete native JSON report:

```bash
sentinel scan . --rules-only --format json --output sentinel-baseline.json
sentinel scan . --rules-only --baseline sentinel-baseline.json
```

The baseline must use the same ordered rules and static/full mode. Matched
findings remain visible but do not affect `--fail-on`; resolved findings appear
as an aggregate count of findings not observed in this scan. Sentinel never updates a baseline automatically. Generate
a separate candidate file, review its diff, then replace the accepted baseline.

Native 1.7.0 reports use `sentinel-baseline-v2`. Supported 1.3/1.4/1.5/1.6 baselines
migrate in memory without changing their files or claiming completed dynamic
testing. Static matching is preserved. Historical entries cannot hide newly
verified runtime proof, including proof appended to a static finding. Timings
and incidental logs do not invalidate otherwise identical proof.

## Dynamic outcomes and valid examples

Provide complete legitimate argument objects in `sentinel.target.yaml`:

`sentinel init --dynamic` leaves these examples empty. Generated schema-valid
arguments may still be invalid for the application: a calculator can accept
strings while requiring a valid expression. Supply known valid examples when
baseline calls fail; Sentinel reports incomplete analysis rather than treating
those failed baselines as defenses.

```yaml
probe_baselines:
  reader:
    path: data/users.json
  calculator:
    expression: "1"
```

Examples replace generated arguments. Both must validate against the listed
runtime schema and succeed in a fresh baseline container. Examples share depth-8
and 16-KiB bounds; generated arrays are limited to 16 items. References resolve
locally only. Each probe has separate fresh baseline and attack sessions, with
10-second session deadlines. Campaigns default to 24 started attempts or 120
seconds including runtime discovery, whichever comes first. Startup failures
count as started; mandatory cleanup still runs after expiry.

```toml
[sandbox]
max_probe_attempts = 24
campaign_timeout_seconds = 120
```

Override with `--max-probe-attempts` / `SENTINEL_MAX_PROBE_ATTEMPTS` and
`--campaign-timeout-seconds` / `SENTINEL_CAMPAIGN_TIMEOUT_SECONDS`. Values must
be positive integers. Precedence is CLI > environment > file > default.
Rules-only ignores these runtime settings, including invalid inactive values.
The GitHub Action consumes this configuration from its selected repository.

Default console, native JSON `dynamic_analysis.probe_outcomes`, and SARIF
invocation `properties.dynamicAnalysis` show one outcome per planned attempt, including the unstarted remainder.
Attempts rotate across discovered tools and supported arguments. Multiple
attempts may share a rule; use `attempt_id` to join bindings, discovery and
outcomes. Empty or failed discovery does not invent four attempts. A `tested`
probe has verdict `violation_observed` or `no_violation_observed`. Unsupported,
untested, and inconclusive probes have null verdicts and make analysis incomplete
(exit 3), preserving any findings. Timeout alone cannot prove a violation.
Skipped analysis and unavailable historical summaries use null `dynamic_analysis`.
A completed negative attempt does not establish general safety.

Verified runtime findings remain confirmed with high confidence even if GPT
abstains, disagrees, or is unavailable. GPT judgments and reasons remain under
`review`; disagreements are visible in every output format. Model judgment
counts are separate from finding status counts. Required GPT failures still make
a normal scan incomplete unless the existing degraded-mode policy applies.

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
    rev: v1.3.0
    hooks:
      - id: mcp-sentinel
```

The hook runs the Rules-only tier. Add `args: [--baseline,
sentinel-baseline.json]` to use a reviewed baseline.

## Rules-only report compatibility

Native schema 1.7.0 retains the canonical Finding shape, with nullable finding
review for explicitly unreviewed rules-only results. Provenance reviews and the
GPT summary are null. Existing `not_reviewed`, degraded, and completed review
records remain readable. Consumers must handle null review; older validators
that required a review object need the 1.3.0 schema. Baseline-v2 and
supported historical baseline migration remain compatible. Rules-only and
reviewed static scans share static-mode baseline compatibility.

GPT-static, dynamic, and GPT-dynamic stages are skipped with
`rules-only scan requested`; static finalization and reporting succeed. SARIF
exports stages in invocation properties; older SARIF lacking stages is readable.
Completion applies to the selected tier and does not establish security assurance.
