# Replacement v7: memory-keeper source-only preparation

The additional fresh-repository checkpoint is **prepared, unapproved and
unevaluated**. The user's “okay proceed with this” authorizes source preparation;
the exact evaluation remains a separate decision under the original closeout
prompt. Scanner **`8c62567`** was frozen before repository selection and remains
unchanged. A separate staging checkout preserves the original frozen checkout.

The selected independent repository is **`mkreyman/mcp-memory-keeper`** (MIT).
The maintainer's [CVE-2026-54561 advisory](https://github.com/mkreyman/mcp-memory-keeper/security/advisories/GHSA-f7wf-v2vw-mpcx)
documents `context_import` reading arbitrary local files before the 0.13.0 fix.
Complete upstream trees are retained: vulnerable **`dd53a8f` (0.12.2)** and fixed
**`84f6dfa` (0.13.0)**, compared against the fix merge's direct first parent.
The repository is absent from all **eight prior corpus manifests**; neither tree
matches any of **100 unique prior effective trees**, and no source file matches
a prior corpus source file. Curation occurred after scanner freeze by the same
implementation agent. This establishes repository novelty relative to the retained
corpora, not independent human review or training-data novelty.

The named SENT-012 condition is a caller-selected import file outside the
operator-owned exports directory. The vulnerable source reads the supplied path;
the fixed source canonicalizes it and checks equality or a directory-separator
boundary before reading file bytes. A sibling `exports-backup` directory must be
rejected; a file inside `exports` is the safe control. Startup, tool profile,
operator configuration and ordinary readable-file prerequisites are frozen.
The condition excludes symlink races, later parsing/database behavior and broader
filesystem safety. Source inspection is not target execution or runtime proof.

The exact proposal is
`artifacts/phase22/integration/v39-fresh-v7/evaluation-proposal.json`:
**six native rules-only observations**, original vulnerable/fixed/safe inputs
twice, **zero comparators**, one serial local macOS sequence, **120-second target /
300-second native and whole-input maximum**, at most **15 seconds cleanup per
input** and **40 minutes overall** (38-minute internal stop). It allows **zero
retries, profiles, detector changes, target executions, target dependency installs
or paid calls**. First infrastructure, timeout, identity, schema, cleanup or ordered
repeat failure closes the unused budget. Detection misses remain recorded outcomes.

Success requires the one vulnerable condition hit and zero matching alerts on
the two negatives in each batch, three entire ordered repeats, and source
assessment of all findings, warnings, unresolved flows and coverage. Fixed-path
support and guard recognition are reported separately: silence cannot establish
that the scanner understood the fix. Any unresolved fixed-path coverage requires
an explicit disposition before final acceptance. The existing manifest contract
retains 45 earlier records and two paired variable-renaming records; **all 47 are
outside this proposed evaluation**. Six repeats do not represent six independent
repositories or vulnerabilities.

Source/configuration validation and synthetic supervisor/sequence checks pass.
An initial preflight was blocked by sandboxed read-only system topology access;
the unchanged check passed with permitted access. A preparation-only repeat
reference assignment error was corrected and both versions are preserved. No
new corpus scan, comparator observation, target execution or paid call has run.

The prior **87/87 exposed regression pass at `8c62567` remains unchanged**:
36 whole ordered repeats; DDG two vulnerable hits per batch and zero matching
negative alerts; six actual fixed/control sends support initial 100.64.0.0/10
rejection on the direct `web_fetch` route. Python development passes 15/15
(six hits, seven valid negatives, two Meta operator erratum cases each retaining
two raw matched keys). Each 31-input Python historical batch has 14 hits and
zero matching alerts on 17 negatives. 74 observations met 120 seconds; 13 used
extended time; maximum whole-input time was 157.750767 seconds. That budget is
closed. Broader URL protection, other routes, DNS, redirects and IPv6 remain
outside the narrow DDG guard qualification.

Original fresh DDG detection remains measured at `f85a90f`: 10 native and five
Semgrep observations, two correlated vulnerable hits per native batch, zero
matching negative alerts and five whole ordered repeats; Semgrep hit 0/2.
Its original fixed coverage gap is preserved; the later correction is exposed
regression. Original Lighthouse and earlier fresh misses, the failed `a50e9b7`
regression, stopped experiments and all closed budgets remain unchanged. The
original held-out baseline remains 10 completed, 10 unsupported, five incomplete,
with zero hits among four completed vulnerable inputs out of ten vulnerable inputs.

Historical whole Linux timing retains its actual `1f3f72f` source: both 45-input
batches pass with 20 vulnerable hits and zero matching alerts on 25 negatives
each, with all 45 ordered repeats; the whole 25-input development batch is reused
under the user's explicit amendment. Current Python and compatible TypeScript
subsets are not pooled into a new whole execution. Prior exposed TypeScript and
Lighthouse evidence retains its documented `f85a90f` compatibility bindings.

Product, tests and workflows equal tested `8c62567`. Local and all 12 hosted
quality suites retain **2,283 passed / 36 skipped**, **89.91% local branch
coverage**, 29 normal CI jobs and docs passed. Affected documentation and package
metadata are checked separately; no new hosted code pass is claimed. Six zero-call
production replays and Git runtime/image compatibility retain exact source evidence.
**Git coverage remains incomplete at 312/1,040 attempts**, under the user deferral.

The audit retains all **89 original rows: 84 passed, two user-deferred and three
unresolved (R66/R88 for this additional fresh checkpoint, R84 for human acceptance)**.
All **110 added scope rows** remain: 104 passed, five proposed historical closure
dispositions and the new evaluation unresolved. Historical passes stay recorded;
the new test does not erase them. The earlier v38 acceptance proposal has not been
accepted and is postponed pending this additional evaluation and source assessment.
**Phase 22 remains incomplete.** Paid benchmark and pilots remain deferred;
Phase 21 remains incomplete and Phase 24/15 gates are unchanged. No merge,
ready-state change, release, outreach or Phase 23 is authorized.
