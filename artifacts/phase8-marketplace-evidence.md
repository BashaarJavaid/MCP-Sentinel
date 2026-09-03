# Phase 8 GitHub Marketplace evidence

Verified on 2026-09-03 (America/Los_Angeles).

## Stable release and distribution

- The public [MCP Sentinel Marketplace listing](https://github.com/marketplace/actions/mcp-sentinel)
  points to this repository and the root `action.yml`. It uses the approved
  `MCP Sentinel` name, Security primary category, Code quality secondary
  category, Bashaar Javaid author, and red shield branding.
- [`MCP Sentinel v1.0.0`](https://github.com/BashaarJavaid/MCP-Sentinel/releases/tag/v1.0.0)
  is the latest, immutable, non-prerelease GitHub Release. It contains only
  GitHub's generated source archives and links to the package provenance,
  Action proof, and usage documentation.
- Signed annotated tag `v1.0.0` (tag object
  `e3a0a4be8e48166a9088ee895ab602e41936a066`) and signed annotated alias `v1`
  (tag object `388c3f2933c44d0c68676b35519a8732ec798b21`) both peel to release commit
  [`8e8868243872ac34990dda1d4751bbee8dc322d3`](https://github.com/BashaarJavaid/MCP-Sentinel/commit/8e8868243872ac34990dda1d4751bbee8dc322d3).
  The exact release tag was not moved when the major alias was published.
- Active tag ruleset `22212930` restricts creation, update, and deletion for
  `refs/tags/v*`; only the repository administrator role has a bypass. GitHub
  immutable releases are enabled. The manual signed `v1` update procedure is
  documented in `README.md`.

## Package release

- The signed-tag [release workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33804931403)
  passed the full Linux, macOS, and Windows Python 3.10-3.13 matrix, installed
  the canonical wheel through pip, pipx, and uv, ran the installed-wheel Docker
  replay, published and verified TestPyPI, paused for production approval, and
  published the same release to [PyPI](https://pypi.org/project/portunusmcp-sentinel/1.0.0/)
  through OIDC. All 12 public-index pipx/uv install jobs and the provenance gate
  passed.
- PyPI serves wheel `portunusmcp_sentinel-1.0.0-py3-none-any.whl` with SHA-256
  `8fe8af788a1446e40b1f54509426d3641585f4d1c6b3594e78d5c36573763396` and
  sdist `portunusmcp_sentinel-1.0.0.tar.gz` with SHA-256
  `6514e508bb81e52f90617d090f4d64c07b5e5630f6c9e1f77e6150226115ad78`.
  PyPI exposes PEP 740 provenance for the
  [wheel](https://pypi.org/integrity/portunusmcp-sentinel/1.0.0/portunusmcp_sentinel-1.0.0-py3-none-any.whl/provenance)
  and [sdist](https://pypi.org/integrity/portunusmcp-sentinel/1.0.0/portunusmcp_sentinel-1.0.0.tar.gz/provenance).
- The composite Action runs Python 3.12 and installs exactly
  `portunusmcp-sentinel==1.0.0` from `https://pypi.org/simple`. Only exact-style
  `v*.*.*` tags trigger package publishing, so moving `v1` did not start a
  second release workflow.

## External Action proof

- Public proof repository commit
  [`8f4f0a6bf64b753f3e013139a8f8447fa3dc1639`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/commit/8f4f0a6bf64b753f3e013139a8f8447fa3dc1639)
  consumes `BashaarJavaid/MCP-Sentinel@v1`.
- Its first and only Phase 8 [workflow run `33808213435`](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33808213435)
  passed both jobs. The clean target completed with zero findings. The
  vulnerable Action step returned the expected finding exit, while the proof
  job verified complete analysis, Critical highest severity, Sentinel version
  `1.0.0`, and exactly one result for every rule from `SENT-001` through
  `SENT-011`.
- The vulnerable live review used five accepted `gpt-5.6-sol` batches, reviewed
  all 11 candidates with no failures or overflow, consumed 10,573 current
  tokens, and cost USD 0.145437. The clean target required no GPT call. Total
  cost remained below the approved USD 0.50 operator gate.
- The fresh proof-only `OPENAI_API_KEY` repository secret was deleted after the
  accepted run and its absence was verified.
- The [clean SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33808213435/artifacts/9913792152)
  and [vulnerable SARIF artifact](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/33808213435/artifacts/9913793308)
  are retained until 2026-12-02T21:29:23Z.
