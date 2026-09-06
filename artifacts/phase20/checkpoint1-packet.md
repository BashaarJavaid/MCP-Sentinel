# Phase 20 — Checkpoint 1 preparation packet

Prepared 2026-09-06. **Not frozen, not approved, not evaluated.**
The manifest is `tests/evals/phase20/manifest.yaml`. Its SHA-256 and the
independent review are retained separately, avoiding a circular hash.

## Corpus and provenance

Ten advisory families, seven Python and three TypeScript, from the five approved
repositories. Each family contributes original vulnerable/fixed inputs and one
paired structural mutation. Five additional safe-condition inputs make 45.
Atlassian and Mobile are held out; the other repositories are development.
No detector, prompt, probe, or scanner output was used to select labels.

Full upstream repository archives are retained without rewriting their bytes.
The manifest records the archive hash, full commit SHA, every regular file hash,
and revision-specific LICENSE/NOTICE paths. Scan roots select `src/git` and
`src/filesystem` within the MCP monorepo, and the repository root elsewhere.
Archives include upstream tests/docs/build metadata as context. Default Sentinel
file selection applies; no source file is cherry-picked to improve detection.
Mutations are separate compressed file overlays with exact hashes and parent
lineage. Original archives remain unchanged. All licenses must be read from the
selected revision; our project MIT license does not replace upstream notices.

The fixing-commit JSON contains the upstream patch and parent list. First-parent
selection for the Git staging and filesystem merge commits is explicit. The
Atlassian authentication and upload conditions share fixing commit
`b041733473f95119dd539542a43c280737a8e460`, which also changes other protections.
Neither these pairs nor the three Git families are independent repository draws.
No release-tag or missing-parent substitution is proposed.

## Proposed conditions and transformations

The manifest contains the exact conditions, prerequisites, source-file hashes,
and evidence ranges for every input. The ten transformations are:

| Family | Paired transformation |
| --- | --- |
| Git staging | Rename the internal `git_add` function and identifier references; tool name stays `git_add`. |
| Git arguments | Route the `git_diff` return value through a same-file identity helper. |
| Git repository | Alias the imported `pathlib.Path` name and its identifier references. |
| Filesystem prefix | Rename internal `validatePath` and its call sites. |
| Atlassian SSRF | Alias the imported `urllib.parse.urlparse` name in the URL utility. |
| Atlassian authentication | Rename shared `_get_fetcher` and production identifier references. |
| Atlassian upload | Route upload paths through an imported identity helper; preserve external parameter names. |
| Excel boundary | Route path return values through a same-file identity helper; keep validation ordering. |
| Mobile output | Alias the default `node:fs` import and member accesses. |
| Kubernetes shell | Alias the existing child-process import; retain the vulnerable command string or fixed argument array. |

These are proposed source-preserving transformations in the behavioral sense;
only originals preserve every primary source byte. No upstream test or target
module is executed on the host to claim semantic equivalence. Independent review
must check imports, references, public names, guards, and sinks in both members.

The five extra safe behaviors are Git status with fixed command options,
Atlassian's checked download-path containment, intentionally permitted
Excel remote-mode child workbook paths, Mobile's anchored locale validation,
and Kubernetes JSON result formatting. They reuse fixed snapshots with distinct
condition labels. **There are 45 labeled inputs, not 45 unique source trees.**
Report safe controls separately, disclose reused hashes, and do not inflate
independence or add these controls to vulnerable-condition recall.

“Fixed” is condition-specific. The original narrow Atlassian SSRF fix is retained:
literal private/loopback IP and blocked-scheme header URLs with overrides unset.
It does not establish protection against DNS rebinding, redirect/session gaps,
URL-parser disagreement, or general internal-network access. Later history is
documented in the upstream [advisory index](https://github.com/sooperset/mcp-atlassian/security/advisories)
and [redirect bypass advisory](https://github.com/sooperset/mcp-atlassian/security/advisories/GHSA-v9m3-wfh8-5646).
The bundled later hardening commit remains evidence for auth/upload only.
The Mobile label explicitly assumes Linux and includes **both** CWD and the
system temporary directory. Darwin additionally permits `/tmp` and `/private/tmp`;
no cross-platform boundary claim is made. Modified Mobile source files carry
the Apache-2.0 modification notice alongside the retained revision's license.
Excel's remote containment condition does not apply to stdio.
Atlassian's upload fix uses CWD; it does not implement tenant-specific ownership.
Authentication's `ALLOW_GLOBAL_CRED_FALLBACK` opt-in is unset in the labeled case.

## Matching and scoring proposal

A hit must describe the labeled violated boundary and ground the relevant input,
enforcement failure, and sink in the source evidence. Rule ID, line overlap, a
generic missing-validation claim, or an unrelated warning alone never qualifies.
Evidence ranges currently retain complete relevant files so reviewers can inspect
the entire flow; these are context boundaries, not automatic line-match windows.
Post-scan adjudication must record input ID, stable finding identity, condition,
decision (`match` or `unadjudicated`), source references and rationale. No labels
manufacture candidates. Every unmatched finding remains unadjudicated, including
warnings elsewhere in a vulnerable or fixed repository.

Count each condition once per treatment, deduplicating repeated warnings. Show
candidate recall, retained alerts (including `needs_review`), confirmed-only
reviewed recall, accepted abstentions, incorrect model suppressions, safe-condition
false alarms and authoritative runtime proof separately. No whole-repository
precision claim. Report total, applicable, completed, unsupported, incomplete,
inconclusive, and unadjudicated denominators, with null ratios at zero denominator.
Separate original pairs, mutations, controls, splits, language, repository and
static/runtime evidence. Shared snapshots and fixes are correlated observations.

## Exact configuration proposal

All static inputs use existing configuration loading with `environ={}`, the
production rules, and the **500 finding default**. No ambient API key, endpoint,
cache or scanner override enters offline execution. Review uses production
GPT-5.6 Sol, medium effort, serial requests, zero retries, cache disabled.
Source/configuration bytes are identical between rules and review treatments.
Review overflow, empty stages, missing captures and failures remain visible.

The Python Git inputs are eligible for the existing stdio campaign. Copy these
reviewed packet additions into each Git scan root before **both** static tiers:

| Packet source | Destination |
| --- | --- |
| `configuration/git.target.yaml` | `sentinel.target.yaml` |
| `configuration/git.permissions.yaml` | `sentinel.permissions.yaml` |
| `configuration/git-bootstrap.txt` | `.phase20/bootstrap.py` |

The bootstrap is excluded with the explicit scanner ignore `.phase20/**` in
both tiers. It runs only through DockerSandbox, initializes disposable repositories
and inert control files in container `/tmp`, then launches the untouched source
module with `--repository /tmp/phase20-repo`. The target config lists exact
baseline arguments. Dependency preparation uses the upstream `pyproject.toml`
through the existing sandbox wheelhouse builder. No install on the host, bespoke
sandbox image, external endpoint, user-selected host-path mount, credential, or
new probe is introduced. The native dependency builder retains its controlled
temporary input/output mounts and creates its usual dependency image. Native
sandbox images and their digests remain authoritative.

The Git executable is a prerequisite: the existing sandbox image may not contain
it. Record dependency/launch failure as incomplete; do not install OS packages or
substitute an engine without a new configuration decision. Record all four native
probe outcomes and coverage even when they do not exercise the advisory's input.
The sidecar grants the existing Git operations with justified broad filesystem
scope inside the disposable sandbox; it does not enforce a runtime boundary.
It neither adds a deliberately unauthorized tool nor proves the configured
repository restriction. Its source-induced findings remain unadjudicated unless
they satisfy the independently labeled condition.

Atlassian's three families and Excel's remote-boundary pair require unsupported
HTTP/SSE conditions. They remain in static and total-corpus reporting; there is
no misleading stdio substitute for their runtime labels. TypeScript has no native
runtime treatment. The Excel safe control retains remote-mode prerequisites.

## Approval boundaries and measurement limits

Checkpoint 1 requires an independent agent review and the user's explicit
approval of the manifest hash **before freeze or evaluation**. Source inspection,
integrity validation, syntax parsing, and harness tests are preparation, not
scanner measurements. Any unresolved revision/label decision stays pending.

Checkpoint 2 will name exact static requests and fingerprints, verified dated
pricing, token reservations, and a user-selected ceiling. It cannot be prepared
from scanner candidates before Checkpoint 1. Checkpoint 3 separately budgets
runtime evidence after eligible Docker measurements. Stop at the first failed or
unaffordable paid request; a further attempt requires a new decision. Unchanged
accepted captures are reused with original latency and cost distinct from replay.

Semgrep 1.176.0 uses a separately acquired pinned community-rule snapshot,
security-category Python/JavaScript/TypeScript selection before evaluation, and
an explicit local rule directory. Rule bytes are not redistributed under the
[Semgrep Rules License](https://semgrep.dev/legal/rules-license/).
The acquired revision is `40b8c63f75dc7c22c8a77482d73bfb864b146f7e` (upstream commit
date 2026-07-30). `artifacts/phase20/semgrep-preparation.json` binds **533 rules
in 511 local configurations**, selected solely by category and language before
evaluation, and gives exact IDs, hashes and command arguments. Rule files remain
outside the repository at `/tmp/phase20-community-rules`. No comparator
measurement has occurred. Reproduction downloads the pinned archive, verifies
its retained hash, and runs `python -m scripts.prepare_phase20_semgrep --archive
<archive.tar.gz> --rules-dir <new-private-directory>`; compare the regenerated
metadata byte-for-byte before any scan.

Public historical vulnerabilities cannot establish absence of model training
exposure. The small selected corpus measures these conditions, not production
accuracy. Poor results do not fail Phase 20; missing or misleading evidence does.
No detector, prompt, probe or supported scope is tuned in this phase.
Phase 20 acceptance, merge and public report deployment remain pending.
