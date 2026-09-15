# Phase 22 — TypeScript containment increment

This draft extends SENT-012 to TypeScript and adds source bindings from the
installed, pinned Semgrep parser. Full technical acceptance remains pending;
the external pilot gate remains pending independently.

## Implemented behavior

SENT-012 follows supported filesystem calls through local imports, re-exports,
aliases, helper functions and callbacks. Registration and handler locations stay
distinct. Discovery recognizes SDK registrations, bounded low-level dispatch and
Mastra tool objects. The parser reads source without running Node, package
managers or target code. It shares the existing 120-second static deadline and
introduces no dependency.

Enforced containment requires canonical paths and related component checks.
Regression controls cover traversal, absolute paths, colliding prefixes,
discarded or unrelated validation, replacement, imported Boolean guards,
destructuring, callbacks and collection/control-flow forms. Findings retain
their canonical identities, severity, suppression and baseline behavior.

Custom normalization and strong-prefix helpers are not fully resolved. Existing
fixed filesystem partners still produce containment candidates; their condition
adjudication and detector correction remain pending. The inspected Mastra
development pair is not counted as a successful pair evaluation. Workspace
package resolution, remaining compatibility forms and detector families,
cross-file review context, campaigns and schema 1.7.0 remain separate work.
Unresolved bindings and omitted review evidence are disclosed.

## Verification

Production source commit `11354639b46f1e1b889f936293fedc127733a0a1` has SHA-256
`d26b1dbbb0e2ee7e8548150e79071788e9180bd4e7c4757edee54050b48f61f6`.
The later test-only commit `e635402` preserves that production digest.

- **741 tests pass**, with 36 opt-in Docker tests skipped; branch coverage is
  **86.72%**, above the established 80% floor.
- Ruff, formatting, strict mypy, schema checks, locked dependency audit,
  notices checks and the strict documentation build pass.
- Two rules-only runs complete **45/45 exposed Phase 20 inputs** each. Stable
  findings, coverage, outcomes and warnings match across all 45 inputs. Native
  JSON and SARIF validate through the retained harness.
- No fresh holdout evaluation or model calls occurred. No reviewed-tier
  retention or overall condition-correct recall is claimed.

Summed input wall times are 807.773 and 792.542 seconds. Verification overlapped
other local checks; these are completion and repeatability measurements, not
isolated throughput comparisons. Native reports remain 1.6.0; SARIF stays 2.1.0.

The initial full suite found four offline process assertions that rejected the
new bundled parser invocation. Updated assertions permit its exact source-only
command and still check target boundaries and disabled metrics. All eight
parameterized offline cases and the final full suite pass. Earlier failures,
the initial dependency-audit network failure and the authorized passing audit
remain in the packet.

## Evidence and remaining gates

`artifacts/phase22/containment-typescript/verification.json` records source
identities, timings, checks and limitations. Sibling files retain both benchmark
runs, reports, repeat comparison, coverage, JUnit and diagnostics; the artifact
manifest binds their bytes. The retained Python PR CI record belongs to the
preceding increment, not this TypeScript implementation.

The [full technical contract](phase22-technical.md) remains the requested scope.
Paid evaluation requires its concrete request and budget packet. Merge,
publication, technical acceptance and external pilot acceptance remain pending.

## Windows source-coordinate correction

Commit `3fc7ce3827bc6d9cd1591f739edbd32480de61df` makes the installed parser
consume the exact retained UTF-8 source text. Previously, universal-newline
reading produced LF text while parser tokens retained CRLF disk byte offsets.
The parser still performs source-only analysis and validates original token
spellings against the supplied source. Temporary snapshots are removed after
parsing; the offline boundary tests verify their bytes against included source.

LF/CRLF regressions cover Unicode, imported handlers, findings, and registration
and sink locations. The Unicode fixture now uses explicit UTF-8 encoding.
Both new CRLF cases failed before the correction. The corrected full suite passes
**743 tests**, with **36 opt-in Docker skips** and **86.73% branch coverage**.
[CI run 34153866936](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34153866936)
passes all 30 applicable checks, including all four Windows quality jobs,
Linux/macOS quality, installed wheels, Docker replay and network isolation.
The Pages deployment is skipped for the draft PR.

`artifacts/phase22/typescript-correction/verification.json` binds the tested
source, commands, reproduction, local logs and hosted checks. This corrects the
Windows failure in the earlier increment; it does not close the remaining
containment, detector, campaign, report or benchmark-accuracy gates.
