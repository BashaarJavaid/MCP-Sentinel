# Phase 22 fresh detection and technical acceptance packet

The approved **replacement-v6 fresh evaluation passes its frozen output gate**
at scanner **`f85a90f`**, selected before source curation. The new repository is
**isyuricunha/mcp-ddg-research**, absent from seven prior manifests and 96 unique
source trees. Both native batches detect **2/2 correlated vulnerable variants**
and produce **zero matching alerts on three fixed/control inputs**. All **five
entire ordered repeats agree**. All **15 observations** completed: 10 native and
five pinned Semgrep; Semgrep detected **0/2** vulnerable variants. The native
maximum is **8.452 seconds**, comparator maximum **21.079 seconds**, and local
sequence **201.977 seconds**. Zero retries, target execution or paid calls; the
budget is closed. This is one repository and one narrow vulnerability, not broad
accuracy, independent human review or runtime proof.

**Fixed guard recognition is not established.** The native finding identifies the
registered `web_fetch` caller URL reaching `client.get` without sufficient destination
restriction, which includes the missing `100.64.0.0/10` rejection. Upstream also
changed fixed HTTP access to `build_request`/`send`, which Sentinel explicitly
reports as unresolved. Zero fixed alerts therefore establish the measured output
contrast, not recognition of the CGNAT fix or complete fixed-path coverage. This
limitation is prominently proposed for explicit human acceptance, never silently
accepted. All **80 findings, 3,308 warnings, 3,058 unresolved-flow occurrences and
60 recognized surface occurrences** are source-assessed. The 76 unmatched findings
include framework-validation and hashed-cache-path false positives under stated
source prerequisites; raw findings and unresolved coverage remain visible.

Current exposed Lighthouse and the three prior SSRF repeat gates remain passed.
The existing 54-observation compatibility packet and historical whole 25 + 45 + 45
Linux evidence retain their actual source bindings; no new whole-batch timing
claim is made. Product/test/package/workflow bytes equal tested **`439c3fe`**:
**2,242 tests / 36 skips**, **89.76%** local branch coverage, all **29 normal CI
jobs** and docs passed. Six production-request replays retain zero-call evidence.
Git campaigns remain **312/1,040 incomplete**, as the user instructed.

Original fresh Lighthouse misses at `1f3f72f` and original held-out failures remain
unchanged; later Lighthouse passes are exposed regressions. All earlier failed
optimizations, stale-assessment stops, invalid v4 novelty and corrective attempts
remain preserved with closed budgets. The audit contains **89 original rows:
86 passed, two user-deferred and one pending acceptance**, plus **88 added rows:
82 passed and six proposed documented limitations awaiting decision**.
**Phase 22 remains incomplete** until explicit human technical acceptance and
verified closeout delivery. Paid benchmark/pilots remain deferred; Phase 21 stays
incomplete and Phase 24/15 gates are unchanged. No merge, ready-state, release,
outreach or Phase 23 is authorized.

Review `assessment.json`, `audit.json` and `acceptance-proposal.json` in this directory. The exact prospective output criterion is retained in `../v32-fresh-v6/scoring-rubric.json`; approval is in `../v32-fresh-v6/evaluation-authorization.json`.
