# Fresh SSRF replacement proposal v3

**Prepared; explicit approval is required before any Sentinel or comparator run.**
Scanner `7555a9d3b472516ea880bd0ba8fbd25e89699453` was frozen before source
curation and is preserved in a detached checkout. The implementation agent also
curated this pair; there is no independent human or unseen-source review.

The [manifest](manifest.json) has SHA-256
`275c98478617c76f92c6e0450b52c62f370a9ae22386022051b50ee792adffdd`.
The [exact checkpoint](checkpoint-7555a9d.json) has SHA-256
`13a292ff0b0daf77ec641224311ac533e4696599f484c83c4e840d67b2d98cbd`.
It binds source, harness, lock and comparator configuration. Only five SearXNG
inputs are proposed for evaluation; the other 45 records are unchanged.
Previous corpora, approvals, original misses and exposed regressions remain.

The source pair is `ihor-sokoliuk/mcp-searxng`, vulnerable parent
`3010d1e80ee21baa3d33fcbe0fe2bd5006f285e2` and fixed child
`48e5ecdcb4166a60b94c252dbe74b0a318110ac4`. Both declare version 1.1.1;
the fixed label describes the source commit, not a generally patched 1.1.1
package. The [upstream advisory](https://github.com/ihor-sokoliuk/mcp-searxng/security/advisories/GHSA-q87f-qc2r-2gw4)
identifies the disabled-by-default guard and a later patched release. Retained
release research led to this direct pair before any evaluation, avoiding
unrelated release changes. Both complete 52-file source archives include MIT
licenses, dependency locks, tests and configuration. Nothing is installed or run.

The condition is rejection of `http://127.0.0.1/` supplied to `web_url_read`
before its initial outbound request. Use ordinary stdio startup, an empty cache,
no proxy, and unset `MCP_HTTP_HARDEN`/`MCP_HTTP_ALLOW_PRIVATE_URLS`. The vulnerable
policy returns early when hardening is off; the fixed policy rejects the parsed
loopback hostname even with hardening unset. See the [source review](review/condition-review.json)
for the registration, type guard, imported request helper and Undici fetch chain.
DNS, redirects, IPv6, HTTP authentication, response conversion and exfiltration
are outside this narrow condition. The source fix includes additional protections
that this condition does not measure.

The five inputs comprise the vulnerable/fixed pair, exact reversible renames of
the local policy helper in each, and a public-IPv4 classification control using
the fixed source. The two vulnerable variants are correlated. The safe control
is not a claim of successful downloading or complete SSRF protection.

Approval would authorize **two native five-input runs at 120 seconds per input**
and **one Semgrep 1.176.0 five-input run at 300 seconds per input**, using existing
normal measurement/scoring infrastructure. Maximum nominal input budget: 45
minutes. Zero paid calls and no target execution. Stop after those runs; retain
all results, compare complete ordered reports, source-assess every unrelated
finding/diagnostic, and report actual hits, misses, false alarms and completion
and support denominators. No tuning or replacement based on results is included.
Final Phase 22 acceptance remains separate.
