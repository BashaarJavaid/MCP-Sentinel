# Fresh SSRF replacement evaluation v2

**Approved and evaluated at frozen scanner `62987a6`.** The user approved
[the exact checkpoint](checkpoint-62987a6.json) with “go ahead with these two”; the
[separate authorization](authorization-62987a6.json) binds manifest
`a587427f0c40cbff512f00c8024e454a11255e34a13c10f9d8748bbc4aa9bae2`.
Original proposals and superseded checkpoints remain unchanged.

All five inputs complete in both native runs and the pinned Semgrep 1.176.0 run.
Both tools miss both correlated vulnerable variants and have zero condition-matched
alerts on the two fixed variants and public-IP control. Native reports are equal
in their entirety except documented volatile fields; maximum wall times are
5.771s and 5.075s. Semgrep's maximum is 16.374s. Its 50 unrelated JQuery alerts
match calls to the local Fetcher.html method and have source-bound false-positive
assessments. See [the complete assessment](../integration/v8-fresh-assessment/packet.json).

Native coverage retains one unresolved low-level tool handler per input and
unresolved schema/class/method flows. Zero findings therefore do not establish
protection. Curation exposure remains disclosed; this is a separately frozen
measurement, not independent human or unseen-source review. Target source was read after
the native runs only to assess results. No detector tuning, target execution or paid
model call occurred. No fresh accuracy threshold is invented. Final human Phase 22
technical acceptance remains a separate checkpoint.

## Original preparation record

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
[original approval packet](packet.json) and [source review](review/condition-review.json).

The retained pnpm lock predates some package-manifest dependency updates. Its
`private-ip` 3.0.2 entry and integrity match the reviewed dependency archive;
no successful installation or supported runtime environment is claimed.
