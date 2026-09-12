# Replacement-v5 execution preparation

The user approved source-only recovery. The [exact evaluation proposal](../../corpus-replacement-v5/evaluation-proposal.json)
is **unapproved and undispatched**. The runner requires a separate `authorization.json`
and final `binding.json`; neither exists. The prepared workflow input is
`phase22_fresh_v5`, false by default and exclusive with historical measurements.

`runner.py` reuses the existing measurement harness, corpus validator and tested
process-group supervisor. Product, tests, harness and lock stay at `1f3f72f`.
`preflight.py` verifies approval rejection, exact timing/cleanup boundaries,
ordered-report comparisons and optional-job isolation using synthetic data.
The source-only staging check passed in a separate `1f3f72f` checkout.

Source research and reproducible preparation helpers are retained in
`../v23-fresh-v4/`; their names preserve this turn's prior preparation history.
The rejected Git source candidate is retained in `../v23-rejected-git-source/`.
No target imports, builds, dependencies, browser or scans ran during curation.

The active source preparation helpers are `../v23-fresh-v4/download-lighthouse-source.py`
and `../v23-fresh-v4/curate-lighthouse.py`. `prepare-v5-source.py` records the
rejected Git research and is historical; it is not the Lighthouse preparation path.
