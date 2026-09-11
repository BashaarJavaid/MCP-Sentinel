# Proposed replacement-v4 evaluation

Status: **prepared, not approved or run**. Scanner `1f3f72f` was frozen before
source research. The same implementation agent curated the cases; this is not
independent human review or a claim that the implementation agent never saw them.

The exact checkpoint is [checkpoint-1f3f72f.json](checkpoint-1f3f72f.json);
[evaluation-proposal.json](evaluation-proposal.json) contains the execution bounds.
Only the five new inputs in [manifest.json](manifest.json) would run: the
`authfetch-mapped-loopback` vulnerable/fixed pair, two reversible local helper
renames and `authfetch-mapped-public-safe`. The other 45 manifest records stay
unchanged. Previous corpora and exposed SearXNG results remain preserved.

The source pair is `ymw0407/auth-fetch-mcp`, parent
`42daa70c391cde4396de877541a64a9c3f761a9d` and fix
`177ec5f8ee9c2d5749035777e562f699971b0da9`. Both exact revisions still declare
3.0.1; this is a source-specific fix label, not a patched-version claim. Only
`src/security.ts` changes. Both complete archives, licenses and every file hash
are retained in `sources/` and the manifest; the full diff and upstream metadata
are in `provenance/`. The input-to-guard-to-browser flow, prerequisites, narrow
labels and mutation checks are in [review/condition-review.json](review/condition-review.json)
and [provenance/pair-comparison.json](provenance/pair-comparison.json).

The condition is initial browser navigation to the mapped-loopback literal
`http://[::ffff:7f00:1]/` through `auth_fetch`, with private opt-in and hostname
allowlist unset. The safe control uses the public mapped address
`http://[::ffff:808:808]/`. DNS, redirects, response contents, capture-button
interaction and other tools are outside these labels. The pair and its renames
represent one vulnerability, not four independent discoveries.

Approval would permit one standard Linux dispatch: two five-input native batches
and one five-input Semgrep batch. Each whole input has a 300-second ceiling;
120 seconds remains the native performance target. The maximum is 15 observations,
75 nominal input-minutes in one 90-minute job, with no retries, profiles, paid
calls, target execution or detector tuning. Execution/identity/cleanup/repeat
failures stop the sequence. Detection misses and false alerts remain visible
outcomes. Final human Phase22 acceptance remains separate.
