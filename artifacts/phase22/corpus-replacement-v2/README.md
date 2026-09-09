# Fresh SSRF replacement proposal v2

**Prepared; explicit freeze approval required before evaluation.** The scanner
is frozen at `68bdf83ca35670946c850595f3a2a11eadee2a4a`. No scanner, comparator,
model, upstream test or target execution has been run on these five cases.
The implementation agent read the source after freezing the detector; this is
not an independent unseen-source review.

The [manifest](manifest.json) replaces only the five exposed open-webSearch
records with `zcaceres/fetch-mcp`; the other 45 records are unchanged. Original
corpora, exposure decisions, misses, captures and evidence remain preserved.
This proposal follows the handoff's requirement to replace cases that inform a
fix; it does not erase those results or establish a new 25-case held-out score.

The pair uses upstream commit `e7659f8cca26ce051b65f5bc28418df155812b8e`
and its direct parent `9fd840d575e68a37f72f07b8f4d2c77f87698c36`. Both still
declare package version 1.0.2. The [advisory](https://github.com/advisories/GHSA-8fxj-2g9q-8fjw)
lists no patched package version; the narrower fixed label here comes from the
[later source change](https://github.com/zcaceres/fetch-mcp/commit/e7659f8cca26ce051b65f5bc28418df155812b8e),
not an inferred package release.

The condition is rejection of `http://127.0.0.1/` supplied to `fetch_html`
before the initial outbound request. The original passes the whole URL to an
IP predicate; the fix passes its parsed hostname. The retained `private-ip`
3.0.2 source supports the loopback and public-address classifications. DNS,
redirects, IPv6, proxies and response/exfiltration behavior are outside this
condition; later upstream SSRF fixes are not treated as covered by this pair.

The five cases are the vulnerable and fixed revisions, reversible request-helper
renames of each, and a fixed public-IPv4 classification control. Complete source
archives retain all 12 regular files and their MIT licenses; there are no source
projections or installation steps. Hash, evidence-line, mutation-lineage and
repository-split validation passes for the 50-record manifest.

Approval would authorize two native offline runs and one run of the existing
pinned Semgrep comparator on these five cases only. The existing limits are
120 seconds per native input and 300 seconds per comparator input. Stop after those runs, score the exact condition, adjudicate unrelated
warnings and report misses/unsupported/incomplete outcomes. No paid calls,
target execution or subsequent detector tuning is included. See the
[exact approval packet](packet.json) and [source review](review/condition-review.json).

The retained pnpm lock predates some package-manifest dependency updates. Its
`private-ip` 3.0.2 entry and integrity match the reviewed dependency archive;
no successful installation or supported runtime environment is claimed.
