# AGENTS.md

Project-specific context and instructions for **PortunusMCP Sentinel**, merged with a set of general behavioral guidelines (sections 1-4 below, adapted from [andrej-karpathy-skills/CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)) aimed at reducing common LLM coding mistakes: unstated assumptions, speculative complexity, unrelated edits, and vague success criteria.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## Project

**PortunusMCP Sentinel** — a build-time static/dynamic security scanner for MCP (Model Context Protocol) servers, mapped to the OWASP Agentic Top 10, shipped as a CLI tool and a GitHub Action that outputs SARIF.

Sentinel is one of three components of the **PortunusMCP** family:
1. **PortunusMCP Gateway** — runtime zero-trust enforcement gateway (separate repo, out of scope here).
2. **PortunusMCP Sentinel** *(this repo)* — build-time scanner.
3. **PortunusMCP Identity** — short-lived credential broker (separate repo, out of scope here).

Sentinel helps maintainers and small teams **catch MCP server security
regressions before release, with actionable source findings and reproducible
evidence for supported runtime checks**. It combines static source/manifest
analysis and adversarial probes against sandboxed targets. A completed scan is
not proof that a server is safe; OWASP mappings classify findings, not coverage
of all ten categories. Start with supported Python server maintainers and expand
according to measured detection gaps and pilot demand.

The historical build context lives in `mcp-sentinel-buildplan.md`; active contracts and status live in `ARCHITECTURE.md` and `ROADMAP.md`. Read the historical brief first for project context, then use the active documents as authority.

## Where things live

- `mcp-sentinel-buildplan.md` — historical build brief and original scope. Read this first for context; defer to Architecture and Roadmap for current contracts.
- `README.md` — public quickstart, install, supported scope, and usage examples.
- `src/sentinel/static/rules/` — one file per detection rule; each rule is independently testable and tagged with its OWASP Agentic Top 10 category (`src/sentinel/owasp_mapping.py` holds the canonical rule-id → category map).
- `src/sentinel/dynamic/` — the sandbox launcher (`sandbox.py`) and adversarial prober (`prober.py`).
- `src/sentinel/report/` — `sarif.py` (SARIF 2.1.0 writer) and `console.py` (human-readable terminal report).
- `tests/fixtures/vulnerable_server/` and `tests/fixtures/clean_server/` — the reference sample servers every rule is tested against.
- `tests/evals/` and `artifacts/` — existing review truth sets and retained
  evidence; Phase 20 adds independent vulnerable/fixed cases and held-out
  evaluation. Fixture success and code coverage are not detection accuracy.
- `action.yml` — the GitHub Action wrapper around the CLI.

Don't load the full dynamic-analysis sandbox code when working on a static rule, and vice versa — pull in only what's relevant to the current task. Both stay decoupled through the shared report/finding schema.

## Conventions

- Python with Typer for the CLI; retain the established framework.
- Every rule (static or dynamic) produces a finding using **one canonical Finding shape** (rule id, severity, OWASP category, file/location, message, remediation hint) — don't invent a bespoke shape per rule or per output format. `sarif.py` and `console.py` both consume the same Finding objects.
- Rule IDs are stable once assigned (`SENT-001`, `SENT-002`, …) — SARIF output and any historical comparisons depend on IDs not changing meaning. Add new rules with new IDs; don't renumber.
- Static analysis must never import or execute target code. Dynamic analysis
  runs targets only in Sentinel-controlled Docker sandboxes under the accepted
  isolation contract, never directly on the host or against production endpoints.
- Prefer embedding an existing engine (e.g. `semgrep`) for static pattern rules over hand-rolling a full AST walker — this is a deliberate hackathon-scope decision, not a shortcut to "fix later."
- Deterministic rules and probes must not require third-party live services.
  Keep model review separate from the explicit `--rules-only` offline tier.
  Dependency installation and explicitly selected live
  model evaluation have separate network requirements.
- SARIF output must validate against SARIF 2.1.0 schema — treat a non-validating report as a build-breaking bug, not a cosmetic issue.

## Commands

- `pip install -e ".[dev]"` — local dev install
- `uv sync --extra dev` — reproducible local dev install from `uv.lock`
- `sentinel scan <path>` — run static + dynamic checks against a local MCP server repo
- `sentinel scan <path> --rules-only` — deterministic static checks without model, cache, network, Docker, or target execution
- `sentinel scan <path> --format sarif` — emit SARIF 2.1.0
- `pytest` — run the current test suite with branch coverage
- `sentinel demo` — run the full static, GPT review, and Docker dynamic pipeline
  against the vulnerable fixture
- `python -m sentinel.schema check` — fail if generated Finding/report schemas drift
- `python -m sentinel.report.validate_sarif <file.sarif>` — validate SARIF offline

`sentinel scan --static-only` includes required GPT review and exits `0` or `1`
when complete. `--allow-degraded` explicitly permits unreviewed candidates while
keeping them visible and fail-on eligible; it does **not** disable model calls
when a key is present. Normal scans and `sentinel demo` run Phase 3 dynamic
probing and return `3` when analysis is incomplete. `--rules-only` selects completed
deterministic static analysis. Default `sentinel init` writes permissions only;
Python runtime scaffolding requires `sentinel init --dynamic`.

## Current phase

## Current fresh detection prerequisite

The user requires **detection on another previously unused repository before
Phase 22 technical acceptance**. Git runtime campaigns stay incomplete at
**312/1,040** as the retained limitation; no additional Git work is planned.
The earlier v31 acceptance packet is preserved and its readiness is superseded.

Replacement-v6 prepares **isyuricunha/mcp-ddg-research** at immutable scanner
**`f85a90f`**, frozen before new source research. Novelty checks cover seven prior
manifests and **96 unique source trees**, with no matching source files. The
upstream pair changes initial rejection of `http://100.100.200.200/` in shared
address space. Complete source archives, prerequisites, two correlated helper
renames and a fixed-tree public control are retained. Source review is by the
same implementation agent after freeze; no independent human review is claimed.

`artifacts/phase22/integration/v32-fresh-v6/evaluation-proposal.json` is
**unapproved and unexecuted**: one local macOS sequence, **10 native + 5 Semgrep
observations**, 120-second target, 300-second whole-input maximum, 90-minute
sequence cap, no retries, target execution or paid calls. The prospective native
gate requires both vulnerable hits and zero matching alerts on three negatives
in each five-input batch, plus all five ordered repeats. A later repair on this
same source cannot become an unseen-source success. Existing measurements and
all original failures remain unchanged.

The audit is **84 passed, two user-deferred and three unresolved**, plus
86 added rows: **80 passed, five proposed historical limitations awaiting
decision and one unresolved**. **Phase 22 remains incomplete**. Exact evaluation
approval, actual detection/source assessment, explicit human acceptance and
verified closeout delivery remain. Paid benchmark/pilots stay deferred;
Phase 21 remains incomplete and Phase 24/15 gates are unchanged.

## Historical v31 technical acceptance checkpoint

All current Phase 22 technical gates are ready for **explicit human acceptance**.
**Phase 22 remains incomplete** until that decision and subsequent closeout delivery.

At frozen scanner **`f85a90f`**, the approved local compatibility sequence passes
**54/54 observations**: each of SearXNG, fetch-mcp and open-webSearch completes two
whole five-input batches with two correlated vulnerable hits and zero matching
condition alerts on three negatives per batch. All **15 entire ordered repeats**
agree after only the established 11 volatile exclusions. The ten development and
14 historical TypeScript inputs each complete once with unchanged ordered findings
and named-condition outcomes: **4/4** and **6/6** vulnerable hits, respectively,
and zero matching alerts on six and eight negatives. These are partial compatibility
checks, never a pooled whole-batch execution claim.

All 54 observations meet the **120-second target**, with a longest whole input of
**114.274 seconds**, within the uniform 300-second maximum. The single serial
sequence took **2,363.732 seconds**. JSON/SARIF and owned process cleanup validate.
All **3,216 changed diagnostic occurrences** are individually source-assessed:
1,080 warnings and 2,126 unresolved flows added; five warnings and five flows removed.
Unchanged findings retain their exact source-assessed references. Diagnostic removal
does not prove runtime safety; unresolved coverage and raw unmatched scorer keys remain
visible. **One sequence and all 54 observations consumed; zero budget remains.**

The separately approved Lighthouse regression passes **10/10** at the same scanner,
workflow `75142f0`, run
[34648036083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34648036083).
Both whole batches detect two correlated vulnerable variants and preserve the narrow
IPv4 link-local qualifier on fixed/control sources; all five ordered repeats agree.
Its 10 findings, 974 warnings, 624 unresolved-flow occurrences and 20 unresolved
surfaces are source-assessed. Broader SSRF candidates remain visible.

The accepted whole **25 development + 45 historical + 45 historical** Linux gate
retains measured scanner **`1f3f72f`**. The 98-observation refresh completed all inputs:
72 within 120 seconds, 26 using extended time, maximum **176.032 seconds**.
Each whole historical batch has 20/20 vulnerable hits and zero matching alerts on
25 negatives. Whole development reuse retains ten vulnerable hits, two raw Meta
operator erratum alerts and zero matching alerts on 13 valid negatives. Source-only
AST/configuration proof establishes unchanged Python paths for 15 development and
31 historical inputs. Current TypeScript compatibility does not relabel old timing
or establish a new whole-batch Linux performance result.

Product, tests, packages and workflows still equal verified **`439c3fe`**: local
and all 12 hosted suites pass **2,242 tests / 36 skips**, local branch coverage
**89.76%**, all **29 normal jobs** and docs pass. Packaging, installed-wheel/Docker/
isolation, Ruff/format/strict mypy, lock/schema/notices/offline artifacts and six
production-request replays retain their exact source bindings. **Zero additional
paid calls.** Git runtime/image are unchanged; 13 campaigns remain incomplete at
**312/1,040** tested attempts.

The proposed acceptance explicitly retains the original fresh-source result at
`1f3f72f`: **15 completed observations, 0/2 vulnerable hits in each native batch and
comparator**. The later corrections and passes are exposed regressions, not fresh
generalization or independent human review. The original held-out result remains
ten completed, ten unsupported and five incomplete, with zero hits among four
completed vulnerable inputs out of ten vulnerable inputs total. All earlier failed
optimizations, stopped sequences and invalid v4 novelty are preserved with their
superseding evidence; no failed attempt is turned into a pass or reopened budget.

The audit contains **89 original rows: 84 passed, two user-deferred, two proposed
documented limitations and one pending human acceptance**. Its **83 added rows**
contain 78 passed and five proposed dispositions of superseded historical failures.
Those dispositions require the actual acceptance decision; no new limitation is
accepted in advance. Pilots/full paid benchmark remain deferred and nonblocking;
Phase 21 remains incomplete and Phase 24/15 gates are unchanged. No merge, ready-state,
release, outreach, participant source sharing or Phase 23 is authorized.

## Historical v30 Lighthouse regression checkpoint

The approved Lighthouse regression **passes all 10 observations** at scanner
**`f85a90f`**, workflow **`75142f0`**, run
[34648036083](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34648036083).
Both whole five-input batches detect both correlated vulnerable variants and retain
the required narrow IPv4 link-local rejection qualifier on both fixed variants and
the public control. Broader SSRF candidates remain visible. All five entire ordered
reports repeat equally after only the established 11 volatile exclusions.
Whole-input times are **11.992–14.300 seconds**, all within the 120-second target
and 300-second maximum. JSON/SARIF and owned process cleanup validate.
**Ten observations and one dispatch consumed; zero budget remains.**
All **10 findings, 974 warnings, 624 unresolved-flow occurrences and 20 unresolved
surfaces** are individually source-assessed, with zero unassessed entries.
Dispatch remains incompletely resolved; this is no runtime proof or complete coverage.

This is an **exposed regression pass**. The original independent-source evaluation
at `1f3f72f` remains 15 completed observations with **0/2 vulnerable hits per native
batch and comparator**. The stopped `6db3858` vulnerable miss and `4a2359d` fixed
qualification failure retain their closed nine- and seven-observation remainders.
No earlier failure is replaced, and no fresh generalization or independent human
review is claimed. The original held-out result remains 10 completed, 10 unsupported
and five incomplete, with zero hits among four completed vulnerable inputs out of
ten vulnerable inputs total.

Product, test, package and workflow bytes still equal verified `439c3fe`: local and
all 12 hosted suites pass **2,242 tests / 36 skips**, local branch coverage **89.76%**,
all **29 normal CI jobs** and docs pass. Packaging, installed-wheel/Docker/isolation,
Ruff/format/strict mypy, lock/schema/notices/offline artifacts and six production
request replays retain their actual source bindings. **Zero additional paid calls.**
Git runtime/image remain unchanged; 13 campaigns are incomplete, **312/1,040** tested.

The next exact proposal is **unapproved**:
`artifacts/phase22/integration/v30-compatibility-proposal/evaluation-proposal.json`.
It requests **54 serial local macOS rules-only observations** at immutable `f85a90f`:
three earlier exposed SSRF families twice each (30), followed by the 10 development
and 14 historical TypeScript inputs once (24). Bounds are 120 seconds as target,
300 seconds per whole input, 15 seconds cleanup, one 300-minute sequence, zero
retries, profiles, comparators, target executions or paid calls. Stop at the first
incomplete, late, identity/schema/cleanup, ordered-finding/condition or repeat failure;
close every unstarted observation. Every other report delta requires source assessment.
No new compatibility observation has run. Source-only AST/configuration checks bind
unchanged Python analysis for the other 15 development and 31 historical inputs.
The accepted whole 25 + 45 + 45 Linux timing/condition results retain measured scanner
`1f3f72f`; partial compatibility observations will not be called a new whole batch.

The audit contains **89 original rows: 82 passed, two user-deferred, five unresolved**,
and **81 added rows: 75 passed, six unresolved**, including closed historical failed
gates. Earlier TypeScript compatibility, the explicit disposition of fresh-result
limitations and final human technical acceptance remain open. **Phase 22 remains
incomplete.** Pilots and the full paid benchmark remain deferred; Phase 21 is
incomplete and Phase 24/15 gates are unchanged. No merge, release, outreach or Phase 23.

## Historical v29 loopback qualification checkpoint

The approved Lighthouse regression at scanner **`4a2359d`**, workflow **`b53581d`**,
run **34641101185**, detects both correlated vulnerable variants, then **fails**
the first fixed-input condition: its finding lacks the required initial link-local
rejection qualifier. All **three observations complete within 120 seconds**
(12.500–14.805 seconds whole input), with valid JSON/SARIF and verified cleanup.
**Seven unstarted observations are closed; zero budget remains.** No complete
five-input batch, control or repeat was observed. All three findings, 261 warnings,
164 unresolved-flow occurrences and six unresolved surfaces are source-assessed.

The minimal correction at **`f85a90f`** preserves the narrow IPv4 link-local fact
on a helper's IPv6 loopback equality return. It adds two shared URL-analysis lines;
broader SSRF candidates remain visible. Six synthetic checks cover loopback and
unsafe literal exceptions, compound range iteration, URL parsing and DNS branches.
All **518 affected tests pass**. Full local and all 12 hosted suites pass
**2,242 tests / 36 skips**, with **89.76%** local branch coverage and
**89.75–89.78%** hosted coverage. All **29 normal jobs** and documentation
pass at workflow **`439c3fe`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059839),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34642059977)).
Wheel/sdist source members match actual Git blobs. Ruff/format/strict mypy,
lock/schema/notices/offline artifact checks pass. Six production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and zero paid calls.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git runtime/image bindings remain unchanged; its campaigns remain incomplete.
No corpus observation has occurred at this corrected scanner.

The next exact proposal is **unapproved**:
`artifacts/phase22/integration/v29-loopback-fix/evaluation-proposal.json`,
SHA-256 `db93996f070f824b72b9bf2383e82efcde5d674c16e37d339ab7d521b7ace016`.
It retains the same five exposed sources twice: **ten native observations**, one
standard Linux job capped at **60 minutes**, 120-second target / 300-second
whole-input maximum and 15-second cleanup cap. Stop on the first execution,
condition or complete ordered-repeat failure and close the remainder. Zero retries,
profiles, comparators, target executions or paid calls. Normal CI skips this job.

The original fresh `1f3f72f` result remains 15 completed with 0/2 vulnerable hits
per native batch and comparator. The stopped `6db3858` result remains one completed
miss and nine unstarted closed. These later exposed corrections cannot establish
fresh generalization or independent human review. Earlier historical timing and
three exposed-family passes retain their actual `1f3f72f` / `2ac39aa` sources;
current-source compatibility and fresh-result disposition remain unresolved.

The **89 original rows remain 82 passed, two user-deferred and five unresolved**.
The **78 added rows are 71 passed and seven unresolved**, including five closed
historical failed gates. No stopped budget is reopened. The original held-out result
remains 10 completed, 10 unsupported and five incomplete, with zero hits among
four completed vulnerable inputs out of ten vulnerable inputs total.

**Phase 22 remains incomplete**, pending the remaining technical gates and explicit
human technical acceptance. Pilots and the full paid benchmark remain user-deferred;
Git campaigns remain incomplete (312/1,040 attempts), Phase 21 incomplete and
Phase 24/15 unchanged. Zero additional paid calls. No merge, ready-state, release,
outreach or Phase 23. The evidence labels v28/v29 do not change phase numbering.

## Historical v27 constructor-scope checkpoint

The approved exposed Lighthouse regression **fails** at scanner **`6db3858`**,
workflow **`fc3a49a`**, run **34621524649**. The first vulnerable input completes
in **9.835 seconds** whole-input time (**2.071 seconds** native) but produces zero
findings and no matching sink candidate. Its JSON/SARIF and cleanup pass.
**One observation completed; nine unstarted observations are closed; zero budget
remains.** No fixed/control or ordered-repeat result exists. All 21 warnings and
six unresolved-flow occurrences are source-assessed. No retry or paid call occurred.

The constructor-scope correction is verified at scanner **`4a2359d`**.
Constructor eligibility now excludes returns owned by nested callbacks/functions/
classes; a constructor's own returned object remains unsupported. Five synthetic
counterexamples fail at `6db3858`; all 81 class/SDK tests and 315 affected tests
pass with the correction. No current-source corpus observation has occurred.

Full local and all 12 Linux/macOS/Windows × Python 3.10–3.13 suites pass
**2,236 tests / 36 skips**. Local branch coverage is **89.76%**; hosted
coverage is **89.75–89.78%**. All **29 normal jobs** and documentation
pass at workflow **`2998b79`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34622991759),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34622991696)).
Wheel/sdist sources match actual Git blobs. Ruff/format/strict mypy, lock, schemas,
notices and offline artifacts pass. Six actual production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and **zero paid calls**.
The owned Docker demo completes 20/20 attempts with 14 findings and cleanup.
Git's unchanged runtime/image retains 13 incomplete campaigns, 312/1,040 attempts.
The earlier 2,230-test pass remains bound to `6db3858`.

The new exact **unapproved** proposal is
`artifacts/phase22/integration/v27-constructor-fix/evaluation-proposal.json`
(SHA-256 `3ee50c9d652f1cd4d897348a1b77ecf2efb60d78c2b56beb163b286623f6fd8b`): the same five exposed inputs twice, ten native observations,
one standard Linux job capped at 60 minutes, 120-second target / 300-second
whole-input maximum, 15-second cleanup cap, zero retries/profiles/comparators/
target execution/paid calls. Stop on the first execution, condition or ordered-repeat
failure and close the unstarted remainder. The optional workflow remains disabled
in normal CI. No corpus observation has occurred at `4a2359d`.

The **89-row audit remains 82 passed, two user-deferred and five unresolved**.
The 72 added rows are 66 passed and six unresolved, including four closed historical
failure rows. No failed measurement is relabeled as accepted or reopened.
The original held-out baseline remains10 completed,10 unsupported and5 incomplete,
with0 hits among4 completed vulnerable inputs out of10 vulnerable inputs total.

Both the original fresh `1f3f72f` miss (15 completed, 0/2 vulnerable hits per batch)
and this later failed exposed regression remain preserved. The existing fix-it
instruction authorizes the root-cause source correction and ordinary engineering;
the measurement approval does not reopen a stopped budget. Earlier timing and
three exposed-family gates retain `1f3f72f` / `2ac39aa`; current-source compatibility,
fresh-result disposition and final human technical acceptance remain unresolved.
**Phase 22 is incomplete.** Paid benchmark/pilots remain deferred, Git campaigns
incomplete (312/1,040), Phase 21 incomplete and Phase 24/15 unchanged. No merge,
ready-state, release, outreach or Phase 23 work. v26/v27 identify evidence only.

## Historical v25 Lighthouse correction checkpoint

The requested Lighthouse source correction is implemented at **`6db3858`**.
It follows actual module class construction and saved SDK setter forwarding,
recognizes Lighthouse URL sinks, and retains narrow initial link-local IPv4
rejection evidence. Replaced/escaped methods, wrong receivers, callback changes,
unknown array aliases and ineffective guards remain conservative. A qualified
finding still leaves other destinations, DNS, redirects and IPv6 unresolved.

The initial `b830027` candidate passed 2,229 tests locally and in all 12 suites,
but a later synthetic import-alias counterexample found another binding gap.
Canonical SDK identity invalidation corrects it at `6db3858`. That counterexample,
the original successful engineering results and both unexecuted proposals are
preserved; no corpus observation was consumed during this correction.

Verification passes **2,230 tests / 36 skips** locally and in all 12 hosted
Linux/macOS/Windows × Python 3.10–3.13 suites. Local branch coverage is **89.76%**;
hosted coverage is **89.75–89.78%**. All **29 normal CI jobs**
and documentation pass at workflow **`51fd2cb`**
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835606),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34615835565)).
Wheel/sdist sources are byte-verified. Six actual production requests regenerate
and checked-replay with unchanged fingerprints/request hashes and **zero paid
calls**. The owned Docker demo completes 20/20 attempts with 14 findings and
cleanup; the unchanged approved Git runtime retains 13 incomplete campaigns,
312/1,040 attempts. This demo is separate from corpus evaluation.

The exact **unapproved** proposal is
`artifacts/phase22/integration/v25-lighthouse-fix/evaluation-proposal-final.json`
(SHA-256 `26ac27d01740faa0ac664a13963ef7a4d91f199818bba29d9a257d98f1f4206a`). It requests the same five exposed Lighthouse inputs twice:
**ten native observations**, one standard Linux job capped at **60 minutes**,
120-second target / 300-second whole-input maximum, 15-second cleanup cap,
**zero retries, profiles, comparator runs, target execution or paid calls**.
Stop at the first execution, named-condition or ordered-repeat failure and close
all unstarted observations. All four optional corpus jobs are disabled in normal
CI. No corrected-source corpus observation has occurred.

The first fresh result stays **0/2 vulnerable hits** per native batch and in
Semgrep at frozen **`1f3f72f`**: all 15 observations completed, all five ordered
native repeats equal, zero findings, unknown tool coverage and 232 source-assessed
diagnostics. Its budget is closed. The user chose correction rather than accepting
the limitation-only proposal. Any corrected Lighthouse result is an exposed
regression, not fresh generalization or independent human review.

The **89-row audit is 82 passed, two user-deferred and five unresolved**;
66 added rows are 61 passed and five unresolved, including three closed historical
failures. Current-source compatibility of the three earlier exposed SSRF families
and whole timing/condition gates remains to be established after the TypeScript
changes. Their passes retain measured `2ac39aa` / `1f3f72f`; no pooled or new
whole-batch claim, silent waiver or reopened budget. R66/R88 and explicit final
human technical acceptance remain open. **Phase 22 is incomplete.** Paid benchmark
and pilots remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge,
release, ready-state, outreach or Phase 23 work. “v25” names evidence only.

## Historical v24 replacement-v5 result and proposed disposition

The approved replacement-v5 evaluation completed **15/15 observations** in
[run 34605934302](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34605934302),
workflow **`86cbdc9`**, immutable scanner **`1f3f72f`**. All ten native observations
and five pinned Semgrep observations completed within 120 seconds; maximum whole
input was **10.437 seconds native / 22.052 seconds comparator**. All five entire
ordered native repeats match after only the established 11 volatile exclusions.
Native JSON/SARIF, input/configuration identities and owned-child cleanup pass.
The single dispatch and all 15 observations are consumed; no remaining budget,
retry, profile, paid call or target execution.

**The fresh detection result is 0/2 vulnerable hits in each native batch and
0/2 for Semgrep.** Both tools emit zero findings on all five correlated inputs.
The two fixed variants and public control also have zero matching alerts; this
silence does not establish discrimination because vulnerable inputs are silent too.
Sentinel reports no discovered MCP surfaces, an unknown total surface count,
and 19 binding warnings on each vulnerable input versus 26 on each fixed/control.
All **232 native diagnostic occurrences** are individually source-assessed.
The upstream SDK prototype patch makes the scanner's binding resolution ambiguous;
its TypeScript request-sink list also does not include Lighthouse. Neither gate
has been bypassed or changed. Completed analysis is not proof of handler coverage,
detection accuracy, safe navigation or runtime protection.

The novel repository/source pair was curated by the implementation agent after
scanner freeze, with source exposure and correlated variants disclosed. This is
one narrow link-local-before-Chrome condition, not five independent vulnerabilities,
independent human review or unseen-source evidence. Loopback remains intentionally
allowed upstream; DNS/redirects/IPv6 and actual startup/navigation are outside labels.
First frozen misses, source archives and the disqualified replacement-v4 proposal
remain preserved. No scanner tuning, case substitution or new evaluation is authorized.

The concrete limitation proposal is
`artifacts/phase22/integration/v24-fresh-v5/limitation-proposal.json`.
Its assessment, all 15 outcome rows, diagnostic source references, audit and review
summary are in the same directory. **The limitation is proposed, not accepted.**
The original 89 rows are 84 passed, two user-deferred, two proposed documented
limitations awaiting decision (R66/R88), and one unresolved human acceptance (R84).
The 60 added rows are 56 passed, three historical unresolved checkpoints with
closed scopes, and one proposed limitation disposition. Phase 22 remains incomplete;
final technical acceptance is a separate decision after the fresh disposition.

Unchanged product/workflow bytes retain CI **34578515990** and docs **34578515965**
at **`e1ab15c`**: all 29 normal jobs and all 12 suites **2,194 passed / 36 skipped**,
89.67–89.69% hosted branch coverage, and byte-verified wheel/sdist sources. This is
compatible reuse, not a new full-suite pass at the evidence-only delivery. The
whole 25 development reuse and 45 + 45 historical gates remain passed under their
actual approval, as do the three exposed SSRF families at measured `2ac39aa`.
Original held-out misses/failures, the Meta erratum and separate Kubernetes
suspicion remain visible. Git campaigns remain incomplete (312/1,040 attempts);
six production requests retain zero-call replay bindings. Paid benchmark/pilots
remain deferred, Phase 21 incomplete, Phase 24/15 unchanged. No merge, release,
ready-state, outreach or Phase 23 work is authorized. “v24” names evidence only.

## Historical v23 source-novelty checkpoint

Replacement-v4 **fails the independent-fresh-source checkpoint before execution**.
Its vulnerable 21-file extracted tree is byte-identical to the original held-out
`auth-fetch-mcp` tree. All fixed `src/` files are also identical; only package
version/dependency metadata differs. Those earlier inputs already completed
native and Semgrep evaluation on September 9. Different Git revisions and new
helper renames do not establish fresh independent sources.

The comparison and original report hashes are retained in
`artifacts/phase22/integration/v23-freshness-assessment.json`. Earlier v4
preparation/hash checks and proposals remain preserved; they did not check
novelty against the original corpus. The prepared v4 runner was delivered for
review but remains unapproved and undispatched. No new native/comparator
observations, target execution or paid calls occurred; its proposed 15-run
budget was never authorized.

R66, R88 and R84 remain unresolved; the 89 original rows remain 84 passed and
two user-deferred. Historical whole-batch timing and all three exposed SSRF
regressions retain their passing source-bound evidence. Phase 22 remains
incomplete. The user approved source-only recovery; the exact receipt is
`artifacts/phase22/integration/v23-source-only-recovery-authorization.json`.
Replacement-v5 is prepared in `artifacts/phase22/corpus-replacement-v5/`: one
Lighthouse MCP source pair outside all prior repositories and 92 effective trees,
with no matching source-file hashes. All 12 files per revision and MIT license
are retained. The narrow condition is literal link-local rejection before Chrome
launch through `run_audit`; two reversible predicate renames and a public control
are correlated variants. Upstream intentionally permits loopback; DNS/redirects,
IPv6, successful navigation and runtime exploit proof are outside these labels.
The same agent curated after scanner `1f3f72f` froze; no independent human or
unseen-source claim. The Git command-injection research candidate was rejected
because it cannot fill the unchanged SENT-015 slot. The new exact evaluation
proposal is **unapproved and unevaluated**: 10 native plus five Semgrep observations,
one standard Linux 90-minute job, 120-second target/300-second whole-input maximum,
zero retries, target executions or paid calls. No v4 or historical budget transfers.

Current preparation CI **34578515990** and docs **34578515965** pass at
**`e1ab15c`**: all **29 normal jobs**, all **12 quality suites with
2,194 passed / 36 skipped**, and three optional measurement jobs skipped.
CI checkout is synthetic merge `c044a1a`, whose complete tree equals `e1ab15c`.
Hosted branch coverage is **89.67–89.69%**; wheel/sdist source members
are byte-verified against that Git revision. The earlier `1942760` CI
retains 28 successful jobs and one cancelled final hook job; all its
12 test suites completed, but it is **not** a whole CI pass.
The new 56-row added-scope audit retains three historical failed checkpoints
with budgets closed or never approved; its other 53 rows pass. The original 89-row audit
remains 84 passed, two user-deferred and three unresolved. Zero fresh
observations or additional paid calls. Exact source-only preparation,
novelty, approval and execution-proposal bindings are retained; evaluation
and technical acceptance remain unapproved.

Final human technical acceptance has not been requested. Paid benchmark/pilots
remain deferred, Phase 21 incomplete and Phase 24/15 unchanged.

### Historical v22 checkpoint

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

The approved full Linux sequence at scanner **`1f3f72f`**, workflow **`e7131f0`**,
run **34555414891**, **does not pass**. It consumed
**62/115 native observations**: **40** completed within
the 120-second target and **22** used extended time within the uniform
300-second native/whole-input maximum. Raw durations, cleanup, reports, condition
scores and source-assessed deltas are retained in `v21-sequence-assessment/` and
`v21-source-delta-assessment/`. The dispatch budget is closed; no retry, profile,
source tuning, target execution or paid call occurred.

Development passes **25/25**. All **37 attempted** historical inputs also complete within
300 seconds; there are **zero timeouts among 62 attempts**. The run stops on
`kubernetes-shell-vulnerable` because the old assessment expects 24 findings and
the current scanner produces 25. Source review confirms the added `kubectl_logs`
cronjob command-injection suspicion is separate from the named `kubectl_get`
condition, whose existing hit remains. Post-run source review records **19/19**
observed vulnerable condition hits and **0 matching alerts on 18 observed** negatives.
The original gate stays failed, **8 inputs** in the first historical batch remain
unstarted, and the entire 45-input repeat is skipped. All **53 unused** observations
are closed; these are not timeout failures or permission to resume.

The next exact proposal is **unapproved**:
`v21-historical-assessment-refresh-proposal.json`. It requests **98 new native
observations**, two dispatches: 8 preparatory inputs to freeze complete source-bound
assessments, then two **whole 45-input historical batches**. It explicitly asks
to reuse the already passed whole 25-input development batch at identical `1f3f72f`
bytes. The 37 + 8 preparatory reports never count as a whole 45-input execution pass. The
limits remain 300 seconds per whole input and 120 seconds as the target, with
60/245/245-minute job limits, zero retries, profiles, comparators or paid calls, and
no detector/label change. A failing or unresolved preparatory condition closes
the 90-run final budget. Strict identity and ordered-repeat checks remain in the
final pair. See the disposition for exact source evidence and timing.

This is a completion result under the approved timing policy, not a speedup.
The original Linux result at `7555a9d` remains **15/25 complete, ten Meta timeouts
at 120 seconds and both historical batches skipped**. Scanner/test/package bytes
remain `1f3f72f`. Fresh CI **34555415861** passes all **29 normal jobs**; every one
of 12 quality suites passes **2,194 tests with 36 skips**. Docs **34555415860**
passes. Prior local coverage, six zero-call production replays and Git runtime
compatibility retain their exact source bindings. Git campaigns remain incomplete;
all three exposed SSRF families retain their passing regressions at `2ac39aa`.

A later separate checkpoint is the **unapproved replacement-v4 freeze/evaluation** in
`artifacts/phase22/corpus-replacement-v4/`. Its independent auth-fetch-mcp source
pair was curated after the scanner freeze, without running a detector/comparator.
The proposal permits **10 native and 5 Semgrep observations** in one standard
Linux job, 300 seconds per whole input, 75 nominal input-minutes, a 90-minute job
limit and zero paid calls. Source exposure and correlated variants are disclosed;
there is no independent human or unseen-source review claim.

All 89 original requirements are **72 passed, 2 user-deferred,
15 unresolved**. **Phase 22 remains incomplete** pending the
remaining gates and explicit final human acceptance. The original held-out result
remains 10 completed, 10 unsupported, 5 incomplete, with 0 hits among 4 completed
vulnerable inputs out of 10 vulnerable inputs total. Paid benchmark/pilots remain
deferred; Phase 21 incomplete and Phase 24/15 unchanged. No merge/release/outreach.

### Historical v20 diagnostic and full-sequence proposal checkpoint

The approved Linux diagnostic **passes all four observations** at scanner
`1f3f72f`, workflow `71906a7`, run **34550284556**. Both named Meta inputs complete
twice, with valid native JSON/SARIF and **entire ordered reference/repeat equality**.
Whole-input times range from **137.833 to 144.225 seconds**;
**0/4** meet the 120-second target and **4/4** use the extended allowance.
All are within the approved 300-second maximum. Each owned process group is
reaped. Four observations and the single dispatch are consumed; no retries,
profiles, tuning, target execution or paid calls occurred. The raw fixed-label
Meta operator alert and approved source erratum remain unchanged.

Only the optional diagnostic workflow changed. Scanner/test/package bytes equal
`1f3f72f`; the prior local **2,194 passed / 36 skipped**, **89.68%** branch coverage
and six zero-call production replays remain valid source-bound evidence.
Fresh CI **34550284081** passes all **29 normal jobs**, with **2,194 passed /
36 skipped** in every one of 12 suites; docs **34550284214** passes. The unchanged
Git image/runtime evidence still describes 13 incomplete campaigns: 1,040 planned,
312 tested and 728 remaining; this is not complete Git coverage. All three
exposed SSRF families retain their passing source-bound
regressions at `2ac39aa`; they are not fresh generalization results. The original
held-out baseline remains 10 completed, 10 unsupported and 5 incomplete, with zero
hits among 4 completed vulnerable inputs out of 10 vulnerable inputs total.

This is a two-input diagnostic, **not a full corpus timing pass or a speedup**.
The original Linux gate at `7555a9d` remains **15/25 complete, ten Meta timeouts at 120 seconds,
both historical batches skipped**. The prospective policy remains a 120-second
target and uniform 300-second maximum. No earlier result is relabeled.

The next exact proposal is `v20-full-linux-sequence-proposal.json`, **unapproved**:
one 25-input development batch then two 45-input historical batches,
**115 native observations**, one
dispatch across three dependent standard Linux jobs with **145/245/245-minute**
limits (635 minutes total maximum), no retries/profiles/paid calls. The next job
starts only after its predecessor's completion and condition gate passes. Stop
on the first incomplete, late or mismatching result; do not pool attempts.
The existing condition requirements and ordered historical repeat gate remain.

All 89 requirements remain **70 passed, 2 user-deferred, 17 unresolved**.
**Phase 22 remains incomplete.** Full timing, fresh freeze/evaluation and final
human acceptance remain separate checkpoints. Paid benchmark/pilots remain
deferred; Phase 21 incomplete and Phase 24/15 unchanged. No merge/release/outreach.

### Historical v19 timeout policy and unapproved diagnostic checkpoint

The approved **120-second performance target / 300-second static maximum** is
implemented and verified at `1f3f72f`. The same deadline applies to every input;
fast scans return immediately. The TypeScript parser and source-flow workers use
the remaining shared budget, shorter caller deadlines are honored, and coverage/
report assembly checks expiry. No detector rules or model/dynamic budgets change.

Local full verification passes **2,194 tests / 36 skipped**, with **89.68%**
branch coverage. Fresh CI **34545976337** passes all **29 normal jobs**; each of
12 suites passes **2,194 / 36**. Docs **34545976336** and the final local docs build
pass. Six production requests regenerate/replay with **zero paid calls**; Git
runtime components/image remain compatible with the retained incomplete campaigns.
Initial failing deadline regressions, lint/type-check corrections and all earlier
failures are preserved. The scanner bytes now differ from `592a9cd` and `2ac39aa`;
prior exposed detections remain source-bound regressions with deadline-only
compatibility explained in `v19-source-verification.json`.

**No new corpus timing run has occurred.** The original Linux result remains
15/25 development complete, ten Meta timeouts at 120 seconds and both historical
batches skipped. The user approved revising the prospective hard timing criterion
to 300 seconds; completion within the original 120-second target must still be
reported separately. This is no speedup or completed timing-gate claim.

`v19-linux-timeout-diagnostic-proposal.json` is prepared and **unapproved**:
two named slow Meta inputs twice each, four native observations, 300 seconds each,
one 30-minute standard Linux job, no profiles/retries/paid calls. Stop at the first
incomplete or mismatching result. Full 25+45+45 verification, fresh evaluation and
human acceptance remain separate checkpoints. **Phase 22 remains incomplete.**
Paid benchmark/pilots remain deferred; Phase 21 incomplete and Phase 24/15 unchanged.

### Historical v18 throughput probe at `0b71a29`

The approved Stage 0 synthetic throughput probe is complete at `0b71a29`.
Run **34536965288** completed **12/12 observations** in an 88-second job;
all checksums match, all children were ready before the shared monotonic start,
and every child was reaped. No scanner or corpus input executed in the probe.

Median throughput relative to one process is **2.029× at three processes,
2.136× at four, and 2.125× at six**. Four processes add only **5.25%** over
three; six add **4.71%**. The runner reports four vCPUs, two cores and two
threads per core, with Python 3.12.14. The prospective **E3 ≥ 2.7 premise
fails**. This result does not support proceeding to the proposed partitioning
experiment; it is not proof that all scanner parallelism is ineffective.
See `v18-scaling-assessment.json` and its retained raw observations.

**One dispatch consumed; zero scanner runs, optimization attempts or paid model
calls.** Stage 1 and partitioning remain unapproved. The normal CI jobs are
structurally unchanged, but the optional workflow changed, ending workflow
equality to `592a9cd`. Fresh CI **34536886816** verifies all 29 normal jobs;
all 12 suites pass **2,183 tests / 36 skipped**. Docs **34536886750** pass.
Scanner/test/package bytes remain identical to `592a9cd`; prior local checks,
production replay and Git compatibility retain their executed sources, and the
three exposed SSRF gates retain measured `2ac39aa`. Initial probe lint issues
and an immediate post-push PR-readback assertion are preserved with corrections.

**Phase 22 remains incomplete.** The retained Linux scanner result is still
15/25 development complete, ten Meta timeouts and both historical batches
skipped. No current-source full timing pass, fresh evaluation, scope waiver or
final human acceptance is inferred. Further source-design work may investigate
reducing repeated analysis, but no safe reuse design or new experiment is
established here. Pilots/full paid benchmark remain deferred, Phase 21 incomplete,
and Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v17 diagnostic at `127763c`

The approved whole-worker sampling scope is complete at `127763c`:
**one Meta operator input**, **69.906s native / 71.578s outer**, 49 findings,
full ordered baseline equivalence after established volatile exclusions and valid
native JSON/SARIF. Four final snapshots restore timer/signal state. The sampler
changes no scanner methods and records no locals or target values.

Active workers retain 4,220 / 5,093 / 4,903 samples (SENT-012/015/016).
Shared merge inclusive shares are 24.81% / 19.18% / 22.58%; expression leaf
shares are 11.66% / 15.92% / 14.28%, mostly at function entry. Caller shares
overlap, signal delivery biases attribution, and no share is wholly removable
cost. **No safe larger optimization or native speedup is established.** See
`v17-sampling-assessment.json` and the source review in `v17-timing-disposition.json`.

The one-profile budget is closed: **zero optimization attempts, additional native
observations, comparator runs, full retries or paid calls**. No scanner/test code
changed. Existing local and 12 hosted suites retain 2,183 passed / 36 skipped,
29 normal jobs and docs, replay and Git compatibility at actual `592a9cd`.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.
The read-only cleanup check initially encountered sandbox Docker permission;
the authorized recheck passed and both records are retained.

**Phase 22 remains incomplete.** The Linux result remains 15/25 development
complete, ten Meta timeouts and both historical batches skipped. Retain the
timing gate; no scope revision, fresh evaluation or final acceptance is inferred.
Further performance experiments need a justified bounded proposal and approval;
this profile does not justify another speculative micro-optimization. Any timing
scope revision needs an explicit user decision and would still require fresh
evaluation and final human acceptance. Pilots/full paid benchmark remain deferred,
Phase 21 incomplete, and Phase 24/15 unchanged. No merge, release or next phase.

### Historical v16 diagnostic at `46b8786`

The user approved `v15-next-combine-proposal.json`; the exact receipt is
`v16-combine-authorization.json`. Its one Meta operator diagnostic completed in
**81.271s** (**82.947s** including measurement setup/finalization). The full
ordered report matches the retained native baseline after established volatile
exclusions. Native JSON/SARIF validate, all four workers have final snapshots,
and 24 synthetic comparisons preserve all Value fields, keys and cache behavior.

The prospective predicate **fails in all three active workers**. Eligible generic
combinations are frequent (83.72%, 85.54%, 84.47%), but their body CPU shares are
only **7.81% SENT-012, 5.34% SENT-015 and 6.81% SENT-016**, below the required
**10% in each worker**. Timing excludes classification counters but includes field
reductions/helpers and construction; it is instrumented attribution, not wholly
removable cost or a native gain. See `v16-combine-assessment.json`.

The stopping condition was enforced before optimization. **One profile used,
zero optimization attempts, zero native performance observations and zero exposed
regression observations.** All 12 performance and 30 conditional SSRF observations
are cancelled; no unused maximum remains open. No scanner/test code changed and
no reversion was needed. Zero paid calls.

Source/test/workflow/package inputs at diagnostic `46b8786` equal verified
`592a9cd`. The existing local and 12 hosted suites each retain 2,183 passed and
36 skipped; 29 normal jobs and docs, production replay and Git compatibility
retain their actual executed sources. No new full suite or hosted pass is claimed.
All three exposed SSRF gates remain source-compatible at measured `2ac39aa`.

The next `v16-next-worker-sampling-proposal.json` is **unapproved**: one
120-second CPU sampling profile of the same Meta operator input, at most 100Hz
per worker, zero optimizations or additional native/comparator observations and
zero paid calls. It seeks a larger whole-worker CPU concentration before another
code proposal. No further measurement, full Linux retry or fresh evaluation is
inferred. Timing/fresh evaluation/final acceptance remain unmet; Phase 22 remains
incomplete. Pilots/full paid benchmark stay deferred, Phase 21 incomplete and
Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v15 diagnostic at `77ea21f`

The user's “okay go ahead” approved the single merge diagnostic in
`v14-next-merge-diagnostic-proposal.json`; `v15-merge-authorization.json` records
that decision. The sole Meta operator profile completed in **88.533s**
(**90.084s** including measurement setup/finalization), below 120 seconds.
All four workers have final snapshots. Its full ordered report matches the
retained native baseline after only established volatile exclusions; native JSON
and SARIF validate. The revised synthetic control passes 24 state comparisons.
The initial control-coverage assertion and documentation-binding check failures
are preserved with their corrections. No scanner code changed or optimization
was attempted. The one-profile budget is closed; zero paid calls.

Shared multi-branch value processing accounts for **17.8–21.3 instrumented
CPU-seconds** per active worker. About **85% of 19.01 million key visits** reuse
existing values. Those counts do not imply that reuse consumes 85% of the time:
the block also includes nested combining, lookups, equality and instrumentation.
URL pre-processing adds 3.79 CPU-seconds. Timings overlap where explicitly marked
and include instrumentation overhead; this is not a native performance gain.
See `v15-merge-assessment.json` and `v15-combine-source-review.json`.

Code/test/workflow/package inputs at measured `77ea21f` equal verified `592a9cd`.
The existing local and 12 hosted suites each retain 2,183 passed/36 skipped,
29 normal jobs and docs passed, production replay and Git compatibility, all at
their actual executed source. No repeated full suite or new hosted pass is
claimed. All three exposed SSRF gates remain source-compatible at `2ac39aa`.

The next `v15-next-combine-proposal.json` is **unapproved**: one counter profile,
one conditional shortcut using the existing two-value combination, up to
12 native performance observations and 30 conditional exposed regressions,
120 seconds each, zero paid calls. Its diagnostic threshold must pass before
any optimization; unused maxima close on failure. No new measurement is inferred.
Full Linux timing, fresh evaluation and final human acceptance remain unmet.
Phase 22 remains incomplete; pilots/full paid benchmark stay deferred, Phase 21
incomplete and Phase 24/15 unchanged. No merge, release, outreach or next phase.

### Historical v14 verification at `592a9cd`

Phase 22 remains incomplete. The user's “go ahead” approved the exact helper-fact
proposal in `v13-next-performance-proposal.json`; the new receipt is
`v14-performance-authorization.json`. Its one counter profile completed and
observed 3,402,980 empty-fact visits among 3,422,804 binding visits (99.42%).
One ordered-pass optimization was attempted at `e57ce95` and reverted in
`a7d7de0`. Scanner bytes again equal measured `2ac39aa` and delivered `424c443`.
The new semantic regression is retained; no detector behavior change remains.

The first operator candidate took 77.556s and 195.041848 child CPU-seconds,
exceeding baseline maxima of 75.134s and 188.048785 CPU-seconds. That irrecoverably
fails the prospectively approved per-observation retention rule. Four candidate
attempts had started when the queue was stopped: three completed, and the active
Atlassian repeat ended without a completion record. It is retained as interrupted,
not completed or timed out. Two remaining performance observations were cancelled;
the 30 conditional SSRF observations were never activated. Total usage is one
completed counter profile and ten native attempts (nine complete, one interrupted).
All ten completed ordered reports, including the profile, match their baselines.
No complete candidate pair or median performance gain is claimed. The failed
lint/format checks, queue termination, partial files and all original evidence
remain preserved. See `v14-performance-disposition.json` and
`v14-queue-stop-outcome.json` under integration evidence.

All three exposed SSRF families retain their passing v13 gates at `2ac39aa`:
five inputs twice per family, two vulnerable matches and zero matching negative
alerts per batch. Current scanner/harness bytes are identical; these results keep
their original measured revision. SearXNG's broader URL candidates and unresolved
MCP dispatch remain visible. Original misses and source assessments are preserved.

Final local and all 12 hosted quality suites pass **2,183 tests, 36 skips and
no expected failures** at corrected `592a9cd`. Local branch coverage is
**89.66%**; hosted coverage is **89.65–89.68%**. All 29 normal jobs and
docs pass ([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818910),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34518818938)).
Wheel/sdist source members match actual Git blobs; all 12 wheel combinations,
Docker replay, network isolation, dependencies and hooks pass. Configured strict
mypy checks all 146 files; Ruff/format, lock, schemas, notices and offline
artifacts pass. Both approved production requests regenerate and checked-replay
without new paid calls. The approved Git runtime/image bindings match; its
13 campaigns remain incomplete (312 tested, 728 remaining).

The candidate's 1,034 affected tests and semantic before/after control passed.
Initial `12748e4` CI failed all 12 quality jobs because its source-only local mypy
check missed a required test-helper annotation. The annotation is corrected;
initial failed/cancelled CI and the superseded local suite interrupted after
365 passing tests are retained. Detector source and measurements are unchanged.
The current 89-row audit records 70 passed, two explicitly user-deferred and
17 unresolved, with current test/evidence bindings. Seven additional v14 scope
requirements are mapped separately: six passed and the performance-retention
requirement remains unresolved.

The retained full Linux gate still fails at `7555a9d`: 15/25 complete, ten Meta
timeouts and both historical batches skipped. No further optimization, profile,
native/comparator measurement, full Linux retry, runner/deadline waiver or fresh
freeze/evaluation is authorized by unused maxima. The prepared `v14-next-merge-diagnostic-proposal.json` requests only one
120-second merge diagnostic on the named Meta input, with no optimization or
additional native/comparator run; it is unapproved. A new measurement scope
requires separate approval. Timing, fresh evaluation and final human
acceptance remain unmet; final acceptance is not requested. Zero paid calls.
Pilots and the paid benchmark remain deferred; Phase 21 is incomplete and
Phase 24/15 are unchanged. No merge, release, outreach or next phase.

### Historical v13 continuation at `2ac39aa`

Phase 22 remains incomplete. At scanner `2ac39aa` (source bytes equal the
SearXNG correction `523320f`), all three exposed SSRF families pass their native
repeat gates. Each family completes five inputs twice, detects both correlated
vulnerable variants and has zero condition-matched fixed/control alerts.
SearXNG takes at most 12.821s per input, fetch-mcp 5.104s and open-webSearch
65.265s. Complete ordered repeats agree except recorded volatile fields;
JSON/SARIF and source assessments pass.

The shared correction keeps TypeScript receiver invalidation local to mutually
exclusive `if` arms, then conservatively unions possible invalidations at the
join. An HTTP-arm unknown `process` effect no longer contaminates ordinary
stdio startup. No callback or unknown function is exempted. SearXNG's fixed
sources now retain the native default-loopback qualification; their broader
URL candidates and unresolved MCP dispatch remain visible. Its 23 unmatched
scorer keys per batch (20 prior HTTP candidates and three qualified negative-source
URL candidates) are all separately source-assessed. Original frozen native and
comparator 0/2 results remain unchanged; these are exposed regressions, not fresh
generalization or runtime proof.

The separately approved immutable-Value experiment used one optimization attempt,
two counter profiles and all 12 native observations. Ordered native reports all
match, but Meta operator median wall time increased 4.58% and child CPU 1.31%.
Atlassian improved 16.70% in median wall time; Meta image improved 5.35% in wall
but only 1.64% in CPU. These mixed results fail the retention rule. The
optimization at `de2a02f` is reverted in `2ac39aa`; the test, original commit,
profiles, deadline failures and all results are retained. No full Linux retry
occurred. The retained `7555a9d` Linux result still completes 15/25, with ten Meta
timeouts and both historical batches skipped.

Final-source local and all 12 hosted quality suites pass **2,182 tests, 36 skips
and no expected failures**. Local branch coverage is **89.66%**; hosted coverage
is **89.65–89.68%**. All 29 normal jobs and docs pass at `1be0650`, whose
code/test/workflow/package inputs equal measured `2ac39aa`
([CI](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664451),
[docs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34509664440)). Actual
wheel/sdist source members match Git. Ruff/format, strict mypy, lock, schemas,
notices, offline artifacts, dependencies, wheel smoke, Docker replay, isolation
and hook checks pass. Both approved production requests regenerate and replay
without new paid calls. The exact approved Git image/runtime bindings match;
its 13 campaigns remain incomplete (312 tested, 728 remaining).
See integration `v13-searxng-assessment/packet.json`,
`v13-exposed-assessment/packet.json`, `v13-performance-disposition.json` and
`v13-performance-revert-receipt.json`. The current SearXNG receipt consumes
31 of its maximum 32 executions: one fixed trace and 30 final observations;
the optional vulnerable trace was not needed. Both approved scopes have reached
their stopping conditions. The separate `v13-next-performance-proposal.json`
is prepared but unapproved; it does not reopen either budget.

Timing, a post-stabilization fresh freeze/evaluation and final human acceptance
remain unmet/separately gated. No final acceptance is requested. There were zero
new paid calls. Pilots and the full paid benchmark remain user-deferred; Phase 21
is incomplete and Phase 24/15 gates are unchanged. No merge, release, outreach or
next phase is authorized.

Historical v12 bounded follow-up: both v10 proposals were approved with “go ahead”.
Candidate `6eb482c` adds shared factory/else discovery and narrow loopback/default
URL guard facts. One helper-context profile found no safely reusable result;
no optimization or further full timing retry occurred. Both five-input exposed
SearXNG native batches complete and detect both vulnerable variants, but both
fixed variants retain unqualified SSRF alerts; the correction gate fails.
All ten authorized SearXNG observations are consumed. Original frozen misses,
failed attempts and exposed regression evidence remain preserved. The earlier
premature guard-contract checkpoint was corrected in
`v12-scope-interpretation-correction.json`; the real next checkpoint is an
additional bounded SearXNG diagnostic/final-run budget in the unapproved
`v12-next-searxng-proposal.json`. Timing, fresh current-source evaluation and final
human acceptance remain unmet/separately gated. No paid call is authorized.
The next paragraph is the historical v10 checkpoint.

Historical v10 continuation: the user said “start with 1 and 2.” The exact approved
SearXNG at 7555a9d evaluation is complete: 5/5 inputs twice native and once Semgrep,
but both tiers miss both vulnerable variants. No source tuning occurred; preserve
all first frozen results. Its MCP tool surface is missed, and all unrelated
findings/diagnostics have source assessments. A source-informed exposure/fix
proposal is prepared but unapproved. The single approved Linux diagnostic
34446017571 completes its job but all four native and two profiled inputs time
out. CPU-bound shared traversal/merge work remains. One finite local duplicate-
merge experiment preserved reports but showed small, inconsistent gains; it was
reverted, retaining the guard regression. Scanner bytes still equal 7555a9d.
See v10 assessments/disposition under artifacts/phase22/integration. No paid call,
full benchmark retry, gate exception or final technical acceptance is inferred.

See `ROADMAP.md` for the authoritative dependency order and verification gates.
**Phases 16–20 are complete and accepted. Phase 20's independent benchmark
was accepted with its recorded detection and execution limitations. Phase 21
recruitment is deferred; Phase 22's benchmark-driven technical work is next.**
Existing phase IDs are preserved for historical releases
and evidence. Required execution order is **16 → 17 → 18 → 19 → 20 → 21 → 22 →
23 → 24 → 15**, rather than numeric order, with the user-authorized exception
below. Phases 14, 25, and 26 are deferred or conditional and never block launch.
Mark a phase complete only when its relevant gate actually passes; a roadmap
entry is not implemented behavior.

The user has deferred recruitment due to limited time and no available
maintainer participants. Continue bounded Phase 22 technical work using Phase
20's measured detection gaps, starting with path-containment detection and
independent vulnerable/fixed cases and safe controls. The subsequent approved
Phase 22 plan authorizes all ten benchmark families and all five compatibility
areas; see `docs/phase22-technical.md`. Corpus freeze, the tested Git SDK
environment and paid evaluation retain their explicit approval checkpoints.
Defer pilot-driven
compatibility prioritization until participant feedback is available. Phase 21
remains incomplete. The user subsequently removed pilots as a Phase 22 completion
prerequisite and deferred the full paid benchmark for cost; see
`artifacts/phase22/completion-scope-v1/decision.json`. Assess current technical
completion using deterministic/replay, isolated runtime and technical checks,
without claiming full reviewed accuracy or external validation. The known
replacement detection gap was returned after the completed audit; the user then
authorized bounded offline investigation and a fix. The five replacement cases
are now exposed regressions; preserve their first frozen results. See
`artifacts/phase22/corpus-replacement-v1/exposure-and-fix-authorization.json`.
Both existing exposed SSRF families pass their final native repeat gates at
`6eb482c`: 5/5 complete per run, 2/2 vulnerable matches and zero matching negative
alerts. Original misses and source assessments remain preserved. The SearXNG
source now reaches an SSRF candidate but flags both fixed variants, so its
correction gate fails. Its ten authorized observations are consumed.

The retained full Linux result at `7555a9d` completes 15/25: all ten Meta inputs
time out and both historical batches are skipped. Earlier local development
22/25 and original held-out 10 completed/10 unsupported/5 incomplete with 0/4
completed-vulnerable hits retain their measured source. No current-source full
benchmark or fresh generalization result is claimed. One newly approved
helper-context profile established no safe reuse; no optimization or full retry
was attempted.

All 29 normal jobs and docs pass at `6eb482c`; the local full suite and 12 hosted
quality suites each pass 2,169 tests with 36 skips and no expected failures. Local
branch coverage is 89.66%; hosted coverage is 89.65–89.67%.
Both approved production requests are regenerated/replayed and Git runtime
compatibility is verified without additional paid calls. Intermediate failures
remain preserved. See the 89-row v12 closeout audit and evidence index. The v10
proposals were approved; only the new v12 diagnostic/run proposal is unapproved.
Further SearXNG observations, full timing retry, fresh freeze/evaluation, paid
calls and final human acceptance retain separate checkpoints. Phase 22 remains
incomplete, with timing and fixed discrimination unmet.
Resume pilots when feasible. Phase 24 adoption and Phase 15 launch gates remain
unchanged; see `ROADMAP.md` §1 for the scope exception.

- [x] Phase 0 — repo scaffold, incomplete `sentinel scan`, valid report shells and schemas
- [x] Phase 1 — hybrid static engine, `SENT-001`–`SENT-007`, paired fixtures
- [x] Phase 2 — GPT semantic review, live captures, replay demo, and static ablation
- [x] Phase 3 — Docker sandbox and four adversarial probes
- [x] Phase 4 — GitHub Action and live SARIF upload
- [x] Phase 5 — console/report polish and judged demo
- [x] Phase 6 — package and release readiness (`portunusmcp-sentinel` distribution)
- [x] Phase 7 — trusted PyPI publishing
- [x] Phase 8 — GitHub Marketplace distribution
- [x] Phase 9 — first-run onboarding (`sentinel init`)
- [x] Phase 10 — configurable GPT review endpoint
- [x] Phase 11 — TypeScript static analysis
- [x] Phase 12 — team adoption workflows (baseline, inline suppression)
- [x] Phase 13 — public documentation and maintenance (PortunusMCP rebrand)
- [ ] Phase 14 — conditional exploit-confirmation stretch (deferred until after Phase 24; optional)
- [ ] Phase 15 — product launch (retain existing artifacts; completion depends on Phase 24)
- [x] Phase 16 — static detection correctness (helper flows and safety exemptions; local gates passed)
- [x] Phase 17 — dynamic probe correctness and evidence (valid baselines, schema violations, observed effects)
- [x] Phase 18 — explicit offline mode and first-use workflow (CLI, Action, pre-commit, onboarding)
- [x] Phase 19 — coverage reporting and actionable findings (recognized/unknown surface and useful evidence; final gate accepted)
- [x] Phase 20 — independent detection benchmark (accepted baseline; vulnerable/fixed pairs, safe controls, held-out cases)
- [ ] Phase 21 — maintainer pilot and problem validation (recruitment deferred; five external workflows and ranked blockers still required)
- [ ] Phase 22 — MCP coverage and compatibility expansion (all three exposed SSRF gates and approved historical repeats pass; new unseen-repository detection required; replacement-v6 prepared, evaluation and acceptance pending; paid benchmark/pilots deferred)
- [ ] Phase 23 — maintained feedback and regression releases (report-to-tested-release loop)
- [ ] Phase 24 — retained adoption and product decision (onboarding, 30-day retention, independent useful catches)
- [ ] Phase 25 — bounded independent AI discovery (conditional after Phase 24; advisory, source-only)
- [ ] Phase 26 — stateful multi-step security testing (conditional after Phase 24; isolated scenarios)

Phases 0–13 are complete. Their original completion statements, release links,
digests, and submission records are preserved in `docs/hackathon.md` and the
linked evidence artifacts. Phase 13's
[documentation workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/33908643137)
passed its strict build, Pages deployment, and live page/anchor smoke at the
[public site](https://bashaarjavaid.github.io/MCP-Sentinel/); its hosted
contribution and dependency-maintenance gates also passed.

The September 2026 review found that the existing implementation/test gates do
not establish real-world detection effectiveness. Preserve their completion
records while implementing the new gates; do not claim the four-case GPT
ablation or zero-finding public walkthrough proves broad accuracy or user value.

## Product-quality implementation rules

- Reproduce the review's counterexamples as durable tests before fixing them:
  same-file helper execution, validation of unrelated data, authentication
  middleware without enforcement, and hashing without trusted comparison.
  Check equivalent Python and TypeScript paths. A named check or nearby call
  alone is not evidence that the relevant input is protected.
- Dynamic probes need a legitimate baseline, valid prerequisites, and an
  observable security condition. Confirm malformed inputs violate the actual
  schema; accepting a large input alone is not exploitation. Distinguish
  unsupported, untested, and inconclusive outcomes from demonstrated defenses.
- Preserve evidence of observed effects through model review. Static suspicion,
  model corroboration, and runtime proof are distinct. A failed exploit attempt
  is not sufficient evidence to label a finding a false positive.
- Report recognized and unresolved handlers and actual tool/parameter probe
  coverage. Do not imply that `evaluated` rules covered all implementations or
  that Sentinel permission sidecars enforce runtime resource boundaries.
- Use the paired reference fixtures plus independent vulnerable/fixed cases and
  structural mutations. Freeze held-out cases before tuning. Report misses,
  false alarms, abstentions, incorrect model suppressions, and support/completion
  denominators; code coverage is a separate engineering metric.
- Benchmark the deterministic and reviewed tiers on identical inputs. Attribute
  competitor capabilities to their documentation and comparative performance
  only to reproducible measurements. Never claim unmeasured superiority.
- Existing GPT review is candidate-bound; broader independent discovery is
  scheduled only in Phase 25. Update `ARCHITECTURE.md`, canonical provenance,
  schemas, compatibility, and docs in the owning phase before implementing new
  review modes, campaign semantics, or independent finding origins. Never reuse
  an unrelated rule ID to accommodate a model discovery.
- Reuse the current pipeline, report model, issue templates, and installed
  engines. Avoid speculative plugin systems, parsers, dashboards, billing,
  automatic patches/PRs, and new languages. Phase 22 selects compatibility work
  from observed pilot blockers; Phase 24 records the commercial/product decision.
- Independent AI discovery is opt-in, advisory, bounded, and source-only.
  Stateful testing uses explicit identities, test data, security invariants, and
  isolated sequences; model-authored executable exploits are not a prerequisite.
- Keep the feedback loop reviewed and versioned: reproduction → detector change
  → regression benchmark → human review → release. AI may draft tests/rules but
  cannot automatically promote rules or change an offline scan's rule set.
- Follow `ROADMAP.md`'s live-evaluation cost policy. Routine tests and pilots use
  offline paths; new live measurements require named cases, a bounded budget,
  and a stopping condition. Label replay evidence and reuse unaffected captures.
- Pilot goals are hypotheses to validate, not results to assume. Record failed
  installs, rejected findings, and removals. Phase 24 requires three of five
  pilots meeting its onboarding/30-day retention goals and an independent useful
  catch; unmet goals remain incomplete or require an explicit scope revision.
- Prepare outreach, announcements, and case studies as reviewable drafts.
  Contacting others or publishing requires explicit user authorization; source
  sharing and maintainer attribution also require participant consent. Do not
  add automatic telemetry or treat this roadmap as outreach authorization.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

Read `mcp-sentinel-buildplan.md` first for historical context, including its
non-goals in §11. Resolve current design questions against `ARCHITECTURE.md` and
the active `ROADMAP.md` phase. The product-quality phases extend the original
hackathon scope deliberately; do not let historical stretch goals override
their order or assume a planned contract change has already shipped.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked and what the active phase calls for. Fix
  detection correctness before pulling forward independent AI discovery or
  multi-step exploit work.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested — e.g. don't build a general-purpose plugin-loading system for rules when a flat list of rule modules does the job; don't add languages beyond the supported Python and static-only TypeScript scope.
- No error handling for impossible scenarios — but do fail loudly (not silently) when a scan target is malformed or the sandbox fails to start; a scanner that silently produces an empty report on failure is worse than one that errors.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes,
simplify. Check the current roadmap's deferred/out-of-scope work and the
historical non-goals in `mcp-sentinel-buildplan.md` §11 before adding scope.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the current task or the current phase's checklist item.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add a rule for hardcoded secrets" → "Write a fixture snippet containing a hardcoded API key, assert the rule flags it as SENT-005/Critical, and write a clean-fixture snippet that the rule does NOT flag."
- "Add SARIF output" → "Run the CLI against the vulnerable fixture with `--format sarif`, and assert the output validates against the SARIF 2.1.0 schema."
- "Add the dynamic prober" → "Assert a probe sending an out-of-scope tool call against the vulnerable fixture server produces a SENT-008 finding, and that the same probe against the clean fixture produces none."

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it
detect bad stuff") require constant clarification. Keep paired vulnerable/clean
fixtures as regression controls and add the independent vulnerable/fixed cases
and held-out measurements required by the active phase. Product gates also need
actual maintainer outcomes; a passing test suite cannot substitute for them.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, phase boundaries stay respected, and clarifying questions come before implementation rather than after mistakes.
