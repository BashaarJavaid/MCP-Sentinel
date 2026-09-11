# Phase 22 independent corpus freeze packet

## Current v22 checkpoint

The approved **98-observation assessment refresh passes** at
scanner **`1f3f72f`**, final workflow **`61b19ae`**, run **34566835295**.
It consumed **98/98** observations; **98** completed.
**72** completed within the 120-second target and
**26** used extended time within the 300-second maximum.
The longest whole-input execution took **176.032 seconds**.
All consumed attempts and any closed remainder are retained in `v22-refresh-disposition-corrected.json`.

Both whole historical batches pass **45/45**, each with **20/20 vulnerable
condition hits** and **zero matching alerts on 25 negatives**. All 45 entire ordered
reports match across the pair, excluding only the established volatile fields.
The previously passed whole **25-input development batch** at identical scanner
bytes is reused under the user's explicit scope amendment: 10 vulnerable hits,
exactly two raw Meta operator erratum alerts, and zero matching alerts on 13 valid
negatives. These results measure completion under the approved timing policy.

The eight preparatory observations completed, and all 45 historical assessments
were frozen before the final dispatch. The retained 37 plus new eight reports
were used only for source assessment, never presented as a whole-batch execution
pass. Five preparatory report deltas include 1,191 individually source-assessed
diagnostic changes. The additional `kubectl_logs` command-injection suspicion is
separate from the unchanged `kubectl_get` benchmark condition; it remains visible,
without claiming runtime proof. Final reports have no new canonical deltas.

The original **15/25** Linux result at `7555a9d`, its ten 120-second Meta timeouts,
and the later **62-attempt stale-assessment stop** in run 34555414891 remain
preserved failures. Neither result is relabeled or its closed budget reopened.
No detector, condition label, prerequisite, deadline or target source changed.
No paid calls, profiles, benchmark retries or target execution occurred.

Final CI **34566768988** passes all **29 normal jobs** and documentation
**34566768974** passes. All 12 quality suites pass **2,194 tests with 36 skips**.
The wheel and sdist retain byte-verified source bindings. Local coverage, six
zero-call production replays and Git runtime compatibility retain their exact
source evidence. Git's 13 campaigns remain incomplete (312/1,040 attempts);
the three exposed SSRF families retain their passing regressions at `2ac39aa`.

The next separate checkpoint is **replacement-v4 freeze/evaluation**, prepared
but **unapproved and unevaluated** in `artifacts/phase22/corpus-replacement-v4/`:
10 native and five Semgrep observations, one standard Linux job, 300 seconds per
whole input, a 90-minute job limit and zero paid calls. Its independent repository
pair was curated after the immutable scanner freeze; source exposure and
correlated variants are disclosed. No independent human or unseen-source review
is claimed.

The 89-row audit is **84 passed, two user-deferred and 3 unresolved**.
**Phase 22 remains incomplete** pending actual remaining gates and explicit final
human technical acceptance. The original held-out result remains 10 completed,
10 unsupported and five incomplete, with zero hits among four completed vulnerable
inputs out of ten vulnerable inputs total. Paid benchmark and pilots remain
deferred; Phase 21 stays incomplete, and Phase 24/15 gates are unchanged.
No merge, release, outreach or Phase 23 work is authorized.

### Historical v21 sequence and proposal checkpoint


This page preserves the original proposal. The user subsequently authorized its
corpus and tested Git environment in `artifacts/phase22/authorization.json`.
Its first measurements and source limitations remain unchanged. The three later
SSRF replacement families are now exposed regressions; all three pass their
bounded native correction gates at `2ac39aa`. A new post-stabilization fresh
freeze/evaluation remains separately gated. See the
[current implementation status](phase22-implementation-status.md).

The four approved Meta diagnostic observations at `1f3f72f` pass within the
300-second maximum with ordered report equality. These are existing development
inputs. Full 25 + 45 + 45 and a new fresh evaluation remain separately gated.

The replacement-v4 source packet is prepared after freezing `1f3f72f`, with
no detector/comparator execution. Its exact checkpoint and bounded proposal are
in `artifacts/phase22/corpus-replacement-v4/`; explicit evaluation approval remains
pending. All v1/v2/v3 original results and exposed regressions are preserved.

## Historical proposal

**Status: prepared and independently source-reviewed; user freeze approval pending.**
The packet contains **ten independent vulnerable/fixed pairs, ten safe controls,
and 20 paired structural mutation inputs: 50 static inputs across nine repositories**.
There is one development pair and one pair from a separate held-out repository
for each of `SENT-012`–`SENT-016`. Eight pairs use upstream fixes. Two poisoning
pairs use explicitly evaluator-authored benign-description overlays for the
user to approve. No detector, model, or runtime results informed selection,
labels, fixes, controls, or mutations.

The concrete manifest is `artifacts/phase22/corpus-review/manifest.json`.
Its SHA-256 is **a5ea6930e9cd5522f9420bef57875fea5d44d1d1c45fb5136a02a7c0292a9c67**. The independent reviewer prepared and
inspected all ten source-condition records under `review/`; the machine-checked
provenance inventory is `artifacts/phase22/corpus-review/inventory.json`.

## Exact selected sources

| Rule / split | Repository | Vulnerable → fixed source | Revision-specific license |
|---|---|---|---|
| SENT-012 / development | [mastra-ai/mastra](https://github.com/mastra-ai/mastra/tree/9e4abde7cef33e3f5cb1e71bee70c6556ef394cd) | `9e4abde7cef33e3f5cb1e71bee70c6556ef394cd` → `7f2b528ba82db512d68832d2f8ad6cbc8bb46cd4` | Apache-2.0 |
| SENT-012 / held_out | [ruvnet/sublinear-time-solver](https://github.com/ruvnet/sublinear-time-solver/tree/ea9a212b69e4449ec443fe088a7aec7546f70b4a) | `ea9a212b69e4449ec443fe088a7aec7546f70b4a` → `a701296e363192be863e79d788fa268095e3d229` | MIT (nested license files retained) |
| SENT-013 / development | [IntegSec/VulnerableMCP](https://github.com/IntegSec/VulnerableMCP/tree/4cfe46227ceb56e1cbaf36233f8e9ce4ac7fbca1) | `4cfe46227ceb56e1cbaf36233f8e9ce4ac7fbca1` + proposed description overlay | MIT |
| SENT-013 / held_out | [eyemnv/mcp-tool-poisoning-toolkit](https://github.com/eyemnv/mcp-tool-poisoning-toolkit/tree/c3615352e272be735dedc22c67caf290888cf0e7) | `c3615352e272be735dedc22c67caf290888cf0e7` + proposed description overlay | MIT |
| SENT-014 / development | [dbt-labs/dbt-mcp](https://github.com/dbt-labs/dbt-mcp/tree/733bf6cc4bb0df9ef3d030e6f6610b0ef442d8b8) | `733bf6cc4bb0df9ef3d030e6f6610b0ef442d8b8` → `291ddd1baedeacd86d36c5fab470b2ad2958a67d` | Apache-2.0 |
| SENT-014 / held_out | [tumf/mcp-shell-server](https://github.com/tumf/mcp-shell-server/tree/b070bc32ed7b7884c3f0f8221e6d0d28b7554d41) | `b070bc32ed7b7884c3f0f8221e6d0d28b7554d41` → `a8e71630865332250f616631d8eb0ea4c5df1916` | MIT declaration before; full LICENSE after |
| SENT-015 / development | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp/tree/95e852793b7ff8604a8132e85d5facd08c91a36e) | `95e852793b7ff8604a8132e85d5facd08c91a36e` → `7d9926336bbdac6285a988d043c4ccfe126c94c5` | BSL-1.1; Apache-2.0 change date 2029-01-01 |
| SENT-015 / held_out | [ymw0407/auth-fetch-mcp](https://github.com/ymw0407/auth-fetch-mcp/tree/98f381d1298b6b7e7ff29d7a7851f18ea5f2364c) | `98f381d1298b6b7e7ff29d7a7851f18ea5f2364c` → `d4dedaf55c1d39228dbed58807ea1f9fac1328e1` | MIT |
| SENT-016 / development | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp/tree/9cbd8aa4c5235a5ae2f01c60eaf464c0b60ccf6a) | `9cbd8aa4c5235a5ae2f01c60eaf464c0b60ccf6a` → `14d7371d4ed77b1e9bb04ff1d00e94e00eba32a7` | BSL-1.1; Apache-2.0 change date 2029-01-01 |
| SENT-016 / held_out | [Labs64/NetLicensing-MCP](https://github.com/Labs64/NetLicensing-MCP/tree/e826d695df5a08d250dc88e9d8843ff0042ce35a) | `e826d695df5a08d250dc88e9d8843ff0042ce35a` → `fbbb1d5ff88eb5400ec933a84e75601ebee48927` | Apache-2.0 |

The manifest binds all 18 source archives, complete retained file inventories,
revision-specific license paths, source-condition references, controls, overlays,
provenance, and the repository split by hash. Repository identity comes from
retained GitHub repository metadata. The validator normalizes aliases and
checks the split across the **whole** corpus, including controls and mutations.
Meta Ads appears twice, both in development; none of the five held-out
repositories appears in development. All selected repositories are outside the
five-repository Phase 20 population.

The accepted [Phase 20 measurement](phase20-completion-v2.md), original 45
inputs, historical split, labels, costs, captures, and acceptance are unchanged.
Those inputs remain exposed regression evidence. Public historical sources
cannot establish absence of prior model exposure, even when the repository is
held out from this detector-development effort.

## Decisions in this exact freeze packet

1. **Poisoning counterparts.** Approve or reject the two concrete
   evaluator-authored fixes in `review/integsec-calculator-poisoning-proposed-fix.patch`
   and `review/eyemnv-docs-poisoning-proposed-fix.patch`. Each removes only the
   attached malicious description and retains the tool's ordinary task
   description and original handler. Their upstream snapshots remain intact.
   These are proposed benchmark fixes, not upstream security releases. Attack
   comments, unrelated vulnerabilities, and detached strings remain in source;
   only the stated metadata condition is labeled fixed.
2. **Source scope.** Mastra is a complete `packages/mcp-docs-server` snapshot
   plus root license, README and package/workspace declarations. The original
   repository archive exceeds the existing 32 MiB ceiling. The solver snapshot
   retains its entire repository except the 26,923,866-byte generated
   `data/emergence/session_memory.json` dataset, which exceeds the 16 MiB member
   ceiling. Both scope decisions are explicit in four `*-projection.json`
   records with original archive hashes, selected-file hashes, and every
   omitted path/size. Relevant target source bytes were preserved. The existing
   archive ceilings were not changed. These are new-corpus scope choices,
   independent of detector results; no existing Phase 20 source was excluded.
3. **License details.** Meta Ads remains BSL 1.1 today, with its exact terms and
   2029 change date retained. It is not Apache-2.0 today. The earlier shell
   snapshot declares MIT in `pyproject.toml` and README but has no LICENSE file;
   those exact declarations are retained, together with the later upstream
   revision's full MIT text. Nested solver license/notice files are retained.
   The proposed use is a source-only, non-production benchmark; this packet
   does not authorize product publication or change upstream terms.

Invariant's unlicensed candidate was **not selected**. NYIT's direct-poisoning
example substantially reproduces Invariant text and was also excluded from the
final pair selection. Earlier investigative metadata remains in `provenance/`
for traceability but is not an input. The selected poisoning implementations
come from separate MIT-licensed repositories with different implementations
and descriptions; they are not two files or forks of one selected source.

## Source review and condition limits

Every pair has a source review in `review/<pair>.json`, cited complete source
files, prerequisites, an exact matching condition, a safe-control condition,
and mutation instructions. Findings qualify by the described boundary and
relevant evidence, not merely rule ID or overlapping lines. Unrelated warnings
remain separately adjudicated or explicitly unadjudicated.

- **Containment:** Mastra's condition is the directory-suggestion fallback after
  rejection, excluding colliding prefixes and symlinks. The solver condition
  concerns a caller-selected vector destination and its basename/directory
  restriction; operator-controlled ordinary ancestors are prerequisites.
- **Poisoning:** the attached descriptions explicitly demand secrets or
  unrelated behavior. The fixes remove the attached requests while retaining
  functional handlers. Model obedience and exploit success are not inferred.
- **Options:** dbt's selector tokens and the shell server's Git external-alias
  option are separate argument semantics. A shell-free argument list is not
  itself a defense. The Git label does not claim all execution-capable Git
  configuration keys are fixed.
- **SSRF:** labeled flows concern literal private/loopback URLs and prohibited
  schemes, including a separate literal canonicalization case. No DNS-rebinding
  coverage is claimed.
- **Credentials:** each condition concerns an HTTP request with no caller
  credential reaching an operator credential fallback. The fixed labels do not
  generalize to invalid-but-present credentials or all tenant-isolation paths.

Controls use ordinary permitted source paths/values or benign tool metadata,
with their own non-contradictory prerequisites. They reuse the paired fixed
source revision (or the same original source for an unrelated benign tool),
so they are **correlated source-conditioned controls**, not ten additional
independent repositories or whole-repository safety labels. Paired structural
mutations rename internal identifiers consistently on both vulnerable and fixed
sides. Python mutations use identifier tokens, preserving strings/comments;
TypeScript changes target bounded identifiers. No renamed identifier is an
attribute name, and affected imports/call sites are preserved. Exact effective
file and tree hashes bind the resulting variants. Mutations are not additional
independent pairs.

This packet is a **static treatment**. TypeScript runtime execution remains
unsupported. The Python source conditions require host-model behavior, HTTP
services, or command-specific environments that this packet does not supply
to the existing four runtime templates. In its inherited input format,
`runtime_applicability: unsupported` denotes that targeted runtime treatment;
startup and discovery for these new inputs remain explicitly **untested**.
It does not claim their Python stdio transports are unsupported in general.
Existing Phase 20 Git startup/discovery evidence is measured separately.

## Verification and handling

The Phase 22 validator reuses Phase 20 archive, artifact, source/evidence,
overlay and tree-hash validation without modifying the historical validator.
It checks all 50 inputs, exact population, per-rule split, global repository
aliases, licenses, source roots, and mutation lineage, and cannot mark itself
approved. The targeted regression test rejects forged approval, repository
alias leakage, escaping scan roots, and invalid mutation parents. Ruff,
formatting and strict mypy passed for the validator/test; its test passed.

Reproduce the checks without importing or running any upstream server:

```bash
python -m scripts.phase22_corpus
PYTHONPATH=. python artifacts/phase22/corpus-review/prepare_packet.py
pytest tests/test_phase22_corpus.py --no-cov -q
```

The generator regenerates exact overlays and labels from the retained source
archives and reviewed case records. Approval applies to the final manifest and
bound bytes, not to future regeneration with changed records. An explicit
user approval record is still required before freezing or evaluating held-out
inputs. The main implementation agent has not inspected held-out source or
used it for detector tuning. Keep `artifacts/phase22/corpus-review` review-only.
If source/results later inform a fix, mark the affected repository exposed and
prepare a replacement holdout before claiming fresh performance.

**No scan accuracy, paid evaluation, runtime execution, external validation,
or Phase 22 pilot acceptance is established by this packet.**

## Approved replacement freeze and Meta erratum

The original proposal and approval remain unchanged. The user separately approved
`artifacts/phase22/corpus-replacement-v1/manifest.json`, SHA-256
`159278d40a7d6fe2faa1c240a26f51009b37cdca30c862d5e9df1d66a6fed0da`,
for source-only deterministic and pinned comparator evaluation of its five
open-webSearch replacements. The other 45 records are unchanged. This is not a
fresh entire holdout; prior exposure and original measurements remain visible.
The additive authorization restricts input IDs and treatments. No target execution,
new detector tuning or paid model evaluation is approved by this freeze.

The user also approved `artifacts/phase22/meta-fixed-label-erratum-v1/packet.json`:
retain the frozen Meta condition and all original labels/results, with an erratum
for the alternate SSE-response configuration. The two affected fixed cases remain
visible as source counterexamples. The valid fixed/safe denominator is 13 with
zero condition false alarms; two erratum cases are reported separately. Original
raw scoring still shows two alerts among 15 nominal fixed/safe cases. This is not
runtime confirmation, a newly enlarged vulnerable denominator or human validation.
