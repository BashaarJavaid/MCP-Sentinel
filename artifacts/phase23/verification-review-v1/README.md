# Next verification checkpoint

Approve [proposal.json](proposal.json), SHA-256:

`904d1218a214ea37aa3c9191af981620b55f38169b1158dc629152ff8f6ddecf`

## Completed

The advisory's 14-observation gate passes and its narrow source judgments and CI
references are human-reviewed. CI is implemented. Local `make check` passed
**2,765 tests / 36 skips**; a final test-only portability adjustment passed **48
focused checks**. Coverage is **90.52% combined / 86.58% branch**. Local wheel and
sdist match all 134 scanner files. Historical failures and 56 unrelated
`needs_review` findings remain visible.

## Exact authorization requested

1. Push local review commit **`f015c005ff40aa660452b730fda4c86c07ff1772`** on new branch
   `phase23/maintained-feedback-20260915` to `BashaarJavaid/MCP-Sentinel`, then open the exact prepared **draft**
   PR to main. [Contents](../delivery-review-v1/contents.json) and
   [PR body](../delivery-review-v1/pr-body.md) are complete. The push's empty
   expected lease permits branch creation only; it cannot overwrite an existing
   remote branch. Require remote main to remain `dd9101ddfead19d65b7a84b374e4cf7e85462ff7` first.
2. Run the normal hosted CI/docs gates through that PR, including all 12 platform
   suites and **seven** current-candidate advisory observations inside Linux
   network isolation. Verify the actual tested head/merge source tree.
3. If hosted gates pass, execute these separately bounded local stages in order:

| Stage | Observations | Outer cap |
| --- | ---: | --- |
| [First-advisory compatibility](../compatibility-advisory-review-v1/README.md) | 14 | 440 minutes + active cleanup |
| [Deliberate regression rejection](../regression-rejection-review-v1/README.md) | 1 | 35 minutes + 15 seconds cleanup |
| [Historical TypeScript compatibility](../compatibility-review-v1/README.md) | 112 | 3,520 minutes + 15 seconds cleanup |

That is **127 local observations**, plus the routine CI's seven. The caps are
worst-case bounds, not estimates. Every scan keeps the normal 1,800-second input,
10-second Semgrep, 15-second cleanup and four-worker maximum. Local inputs run
sequentially. FAF is last and may remain incomplete under the normal deadline;
its accepted uncapped history does not become a pass. No automatic retries,
uncapped evaluation, optimization or budget carryover.

Each local proposal binds exact commands, source/configuration/runner identities,
order, matching conditions and report exclusions. Original source labels and
historical measurements remain unchanged. All 56 historical source/configuration
bindings and synthetic approval/rejection/cleanup boundaries validate. Synthetic
checks are not the actual deliberate-regression observation.

A failed hosted gate or unexpected/incomplete local stage stops later work for
review. Source judgments, all changed findings and any failures are retained for
technical review. This approval does not grant final technical acceptance,
merge/ready-state changes, release version selection, tags/publication, paid calls,
target execution, Proxmox/FAF recovery, pilots or deferred benchmarks.
