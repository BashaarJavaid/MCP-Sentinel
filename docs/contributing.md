# Contributing

This page is the canonical contributor reference. Start with an issue for a new
rule, behavior change, or architecture change. Direct bug fixes and documentation
pull requests may be opened without one.

## Set up

```bash
git clone https://github.com/BashaarJavaid/MCP-Sentinel.git
cd MCP-Sentinel
uv sync --extra dev --extra docs
make check
```

`make check` runs lint, formatting, strict type checking, generated-schema
checks, the full branch-coverage suite, dependency audit, generated notices, and
the strict documentation build. `make artifacts-check` separately verifies the
checked historical artifacts.

## Contracts every change must preserve

- Published `SENT-xxx` IDs are permanent. Maintainers allocate new IDs; never
  rename, renumber, or reuse an existing ID.
- Every detector produces the canonical Finding model. Do not add a rule-local
  report shape.
- Static analysis never imports or executes target code.
- Dynamic analysis executes only local Python targets in the existing Docker
  isolation boundary; never probe a live endpoint by default.
- Console, JSON, and SARIF must remain views of the same findings, and SARIF must
  validate offline.
- Do not change the GPT prompt or replay cassettes unless the semantic contract
  itself changes and the applicable live, budget-capped acceptance gate is run.

## Rules

A rule proposal must describe the supported language/framework scope, exact
detection, OWASP category and rationale, security impact, proposed engine,
false-positive risks, remediation, and minimal vulnerable and clean examples.
Maintainers assign the next stable ID after accepting the proposal.

Implementation acceptance requires:

1. A vulnerable paired-fixture case that emits the assigned ID and severity.
2. A clean paired-fixture case that does not emit it.
3. Canonical Finding, OWASP, evidence, and remediation fields.
4. No target execution for static rules; Docker isolation for dynamic rules.
5. The focused rule test, `make check`, and relevant hosted OS/Python gates.

Record the rule decision in `docs/rule-acceptance.md`.

## Pull requests

Keep changes scoped. Include the command output or hosted run that verifies the
behavior. User-visible behavior and documentation changes need an Unreleased
changelog entry; internal refactors and test-only changes do not. Update public
documentation in the same pull request when interfaces or behavior change.

There is no DCO, CLA, Code of Conduct, or CODEOWNERS requirement.
