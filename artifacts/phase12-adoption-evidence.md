# Phase 12 team adoption evidence

Verified on 2026-09-04 (America/Los_Angeles).

## Release and distribution

- [`MCP Sentinel v1.2.0`](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.2.0)
  is a non-prerelease GitHub Release for commit
  [`cb48e5d24a785dbfafec947a3162f1e0e81ae270`](https://github.com/BashaarJavaid/MCP-Sentinel/commit/cb48e5d24a785dbfafec947a3162f1e0e81ae270).
  GitHub verified signed annotated tag `v1.2.0` (tag object
  `58bc182e95fed6f961e28e34490a94038757c440`) and signed annotated alias `v1`
  (tag object `80509d603cf053a2e4dbbd148fd3aeb84cf8f9fe`); both peel to that release
  commit.
- The signed-tag [release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33895746398)
  passed the full Linux, macOS, and Windows Python 3.10-3.13 quality and install
  matrices, the installed-wheel Docker replay, TestPyPI verification, trusted
  PyPI publication, and provenance verification. Five public-index jobs that
  began before the PyPI CDN exposed `1.2.0` passed on the workflow's failed-job
  rerun without a package or tag change.
- [PyPI](https://pypi.org/project/portunusmcp-sentinel/1.2.0/) serves wheel
  `portunusmcp_sentinel-1.2.0-py3-none-any.whl` with SHA-256
  `ec3fef5ee383f46bf9a1e38d707c3810ddeb5e7414c89d9c7835b675c78acc7a`
  and sdist `portunusmcp_sentinel-1.2.0.tar.gz` with SHA-256
  `034a4075688fcdf605369540623d5219535d9b920ba1a4fe7c8ecb828322e2ea`.
  PyPI exposes verified provenance for the
  [wheel](https://pypi.org/integrity/portunusmcp-sentinel/1.2.0/portunusmcp_sentinel-1.2.0-py3-none-any.whl/provenance)
  and [sdist](https://pypi.org/integrity/portunusmcp-sentinel/1.2.0/portunusmcp_sentinel-1.2.0.tar.gz/provenance).

## GPT checkpoint

- The two-call Python/TypeScript checkpoint used `gpt-5.6-sol`, medium effort,
  no retries, and USD 0.034249 actual spend against a USD 0.14 reservation cap.
  Both responses passed the strict schema, grounded confirmation, and four-probe
  checks. Only non-content telemetry is retained in `phase12-gpt-smoke.json`.
- The release commit's [hosted gate](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33894517253)
  passed the complete quality, distribution, public-hook, and installed-wheel
  Docker matrices without paid calls.

## External exact-tag proof

- Public proof repository commit
  [`450eb2566207e8a1da75a7ff3cf8958de0c05de5`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/commit/450eb2566207e8a1da75a7ff3cf8958de0c05de5)
  adds the Phase 12 workflow without changing the existing Phase 8 workflow.
- The preserved Phase 8 [workflow run `33894539897`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33894539897)
  remained green. Its unavoidable rerun spent USD 0.154517 on the vulnerable
  scan and USD 0 on the clean scan; this spend is recorded separately from the
  Phase 12 proof budget.
- Exact-tag [workflow run `33897900585`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33897900585)
  passed. The unchanged full scan retained five findings (one static and four
  dynamic), matched all five, reported zero new/resolved findings, and exited
  successfully. Adding one inert `ghp_...` secret retained those five matches,
  added one new `SENT-005`, and produced the expected failing Action step while
  keeping the proof job green.
- The same run installed the public pre-commit hook from `v1.2.0`: the clean
  fixture passed, the vulnerable fixture failed as expected, and the inline-
  suppressed fixture passed while displaying its reason.
- Both reports used `sentinel-baseline-v1`, native source schema `1.4.0`, and
  baseline source SHA-256
  `a63e8dce16f451ae213e95c40e3baf370b44aaee68afe3490699831efc72049c`.
  Their two full-live scans cost USD 0.073027 total. The retained
  [exact SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33897900585/artifacts/9946500888)
  has SHA-256 `2d09facac1ad5b025b6398c5cf0c82b6fe1761a352f751891c26fb42eeaac4d2`
  and expires at 2026-12-03T16:56:37Z.

## Signed alias proof

- After the exact proof passed, signed alias `v1` moved to the `v1.2.0` tag.
  Alias [workflow run `33898189505`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33898189505)
  then passed the unchanged full-live scan with five matched findings, zero new
  or resolved findings, and two accepted `gpt-5.6-sol` batches.
- The alias scan cost USD 0.035286. Combined exact-tag and alias Phase 12 proof
  spend was USD 0.108313, below the USD 0.75 cap. The retained
  [alias SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33898189505/artifacts/9946631409)
  has SHA-256 `22f5bd76ce15fde73349aca73957fe53640c73206182959cb91d9e2fbc698f78`
  and expires at 2026-12-03T17:00:02Z.
- The proof-only `OPENAI_API_KEY` repository secret was deleted after both runs,
  and its absence was verified.
