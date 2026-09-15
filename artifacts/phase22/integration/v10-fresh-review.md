# Frozen SearXNG result at scanner `7555a9d`

The approved five-input evaluation completes twice natively and once with pinned
Semgrep 1.176.0. **Both tiers miss both correlated vulnerable variants.** There
are zero condition-matched alerts on two fixed variants and one safe control.
Maximum wall times are 11.311s and 14.926s natively, and 20.219s for Semgrep.
Native JSON and SARIF validate; entire ordered native repeats match except the
recorded volatile fields. No paid call, target execution, retry or tuning occurred.

The narrow condition is default initial-request rejection of caller loopback IPv4
through registered `web_url_read`. The vulnerable source disables the URL guard
when hardening is unset; the source fix rejects loopback before the request.
The full source pair, reversible mutations, license and prerequisites are frozen
in `../corpus-replacement-v3/`; both revisions declare package 1.1.1 and the fixed
label is specific to this source revision, not a generally patched 1.1.1 release.

Native coverage inventories four optional HTTP routes but no MCP tool surface.
Source `src/index.ts:91–102` aliases `mcpServer.server` and registers the low-level
handler; `130–143` validates structural arguments and calls the URL reader.
The report records unresolved `server` binding and unsupported startup flow at 271.
The actual URL path includes source defaults, cache prerequisites, a local guard
and casted imported undici fetch. No evaluator binding or additional diagnostic
scan was supplied to create a native finding. The exposed fetch-mcp correction
has not demonstrated generalization to this complete independent implementation.

Each native input has four raw SENT-006 authentication candidates. Three concern
separately enabled HTTP MCP routes: source checks reject invalid credentials when
hardening is enabled but permit requests by default in unhardened HTTP mode.
The fourth concerns an intentionally public health response. Their applicability
and policy uncertainty are source-assessed; none is an SSRF hit or runtime proof.
All ten comparator alerts are source-assessed format-string false positives in
the upstream test runner: the format text uses names from a closed literal suite
table, with errors supplied as separate arguments. No upstream test was executed.

Every diagnostic, source location, finding and condition score is bound in
`v9-fresh-assessment/packet.json`. The scorer's unmatched-key field is named
`unadjudicated_findings`; its 20 native keys per run and 10 comparator keys all have
separate source assessments and are not a new unassessed security backlog.
Original held-out and exposed results, including all frozen misses, remain
unchanged. No fresh accuracy threshold or human acceptance is inferred. A fix
informed by these sources requires a separate exposure/fix decision preserving
this first result and appropriate subsequent freeze treatment.
