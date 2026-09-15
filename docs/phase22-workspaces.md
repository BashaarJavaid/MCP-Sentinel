# Phase 22 — Workspace increment

This draft follows the TypeScript containment increment (PR #24). It implements
aggregate source scans for declared uv, npm and pnpm workspaces, local package
exports, TypeScript aliases and inherited local compiler settings. Python and
TypeScript source files share the root scanner configuration. Individual package
scans use their own configuration. Dynamic scans still require selection of one
Python package.

Missing, inaccessible, excluded and symlink members remain explicit. Nested
Sentinel configuration is reported as unapplied during an aggregate scan.
Ambiguous local bindings and repository escapes remain unresolved. Source files
are not imported or executed, and symlinks are not followed. Structured workspace
coverage is part of the preserved schema 1.7.0 draft and is not delivered here;
this increment reports member source counts and warnings under native 1.6.0.

The malformed `package.json` diagnostic again states that strict JSON is required.
Parsing remains strict. The four local transport tests passed with loopback socket
permission; their earlier permission failures remain in the retained original log.

## Verification status

Production source is commit `756b57eb6b7e8942c6dea86058d3477362568cae`.
`artifacts/phase22/workspaces/` retains the commands' logs and separate measurement
identities. The original `rules/` measurement completed 45 inputs; its original
`rules-repeat/` stopped after 41 inputs and is **incomplete**. It is not accepted
as repeatability evidence. New `corrected-rules/` and `corrected-repeat/` runs use
the unchanged 120-second per-input deadline and preserve the earlier results.
Both corrected runs complete **45/45 inputs**, with identical stable findings
and coverage. The full suite passes **758 tests**, with **36 opt-in Docker skips**
and **86.69% branch coverage**. Ruff, formatting, strict mypy, native schemas,
notices, dependency auditing and strict documentation checks pass locally.
Hosted workspace checks remain pending. `verification.json` records the exact
commands, exits, source identities and prior failures.

All four raw measurement directories are preserved losslessly in
`artifacts/phase22/workspaces/measurements.tar.gz`; `measurement-files.json` binds
each uncompressed file. Restore them for inspection or repeat comparison with:

```sh
tar -xzf artifacts/phase22/workspaces/measurements.tar.gz -C artifacts/phase22/workspaces
```

These runs establish execution and repeatability only. They do not establish
condition-correct detection of all 20 exposed vulnerable inputs. The historical
unadjudicated-warning backlog remains unadjudicated. No fresh holdout source was
used for tuning, and no paid model calls were made.

## Remaining technical work at this increment

Shared discovery and containment still need the complete development-condition
adjudications, including Atlassian factories and upload flows, filesystem custom
guards and Mastra security-failure fallback flags. SENT-013 through SENT-016 and
the Kubernetes SENT-002 correction remain pending, as do candidate-bound review
completion, bounded runtime campaigns and coordinated native 1.7.0 migration.
The [approved technical contract](phase22-technical.md) remains the scope authority.
The original acceptance scope also required external pilot evidence. The user
subsequently removed pilots as a Phase 22 completion prerequisite and deferred
the full paid comparison. See the current
[implementation status](phase22-implementation-status.md); Phase 21 recruitment
and the later adoption/launch gates remain unchanged.
