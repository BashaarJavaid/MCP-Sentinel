# Phase 20 Checkpoint 1 — independent source review

Reviewer: separate agent `/root/checkpoint1_review`, 2026-09-06.
Status: **ready for the user's Checkpoint 1 review and approval**. No unresolved
source-label, mutation, provenance, or packet-binding blocker remains.
This is not user approval and does not freeze or evaluate the corpus.

Final reviewed manifest SHA-256:
`f69d043cab43e5785e7c8a9dae430bcf146c105a0d23d1d77bc4089637377682`.

This review inspected the proposed manifest, preparation code, retained upstream
advisories and fixing-commit JSON, all 17 source archives, all 20 mutation
overlays, the five safe controls, and the proposed configuration/matching rules.
It did not run Sentinel, Semgrep, target code, upstream tests, Docker, or a model
request. Python mutation files were syntax-parsed without importing them.
No scanner result informed this review.

## Review findings and corrections

The initial reviewed manifest had SHA-256
`7736ce4912e82acad26457ceed56c9d85c271c234171d6effa287aa683a223d0`.
Two approval blockers were identified and corrected before evaluation:

1. Mobile's proposed fixed condition omitted the additional `/tmp` and
   `/private/tmp` roots permitted on Darwin by `src/utils.ts:24–27`. All four
   Mobile family inputs now explicitly require Linux; the packet explains the
   platform distinction. The original upstream source is unchanged.
2. The two modified Mobile `src/server.ts` files lacked modification notices.
   Their retained Apache-2.0 `LICENSE` section 4(b) requires modified files to
   carry notices stating they were changed. Both overlays now begin with a
   prominent comment identifying the Phase 20 alias modification. Original
   archives and license notices remain intact.

A configuration wording correction was also requested and verified: the
packet now distinguishes the native dependency builder's controlled temporary
input/output mounts from user-selected host-path mounts and describes the
proposal as having no bespoke sandbox image.

## Labels and fixing revisions

For every family, the retained fixing-commit JSON's `sha` equals the manifest's
full fixed revision, and its first parent equals the vulnerable revision. The
two merge-parent selections are explicit. I compared the relevant source in
both snapshots against the advisory and fix, rather than treating advisory
titles or commit messages as sufficient proof.

| Family | Source-level basis for the vulnerable/fixed pair |
| --- | --- |
| Git staging | `git_add` changes from `repo.index.add(files)` to `repo.git.add("--", *files)`, delegating rejection of relative out-of-tree paths to Git. The `files == ["."]` branch is unchanged. |
| Git arguments | The vulnerable `git_diff` and `git_checkout` forward caller refs to Git. The fixed versions reject leading `-` and resolve the ref before invoking the CLI. |
| Git repository | Fixed `call_tool` calls `validate_repo_path` before constructing `git.Repo`; the helper resolves both paths and checks containment against the configured repository. The parent lacks this enforcement. |
| Filesystem prefix | The parent authorizes a bare string prefix. The fixed `validatePath` calls the new containment helper, which requires equality or a directory-separator boundary. Ordinary same-prefix siblings are excluded. |
| Atlassian SSRF | The parent accepts header service URLs into fetcher configuration. The original fix validates those URLs in middleware and returns an authentication error before downstream processing. Literal loopback/private IPs and blocked schemes are within the narrow label. |
| Atlassian authentication | The parent falls back to global credentials without user identity. The fixed shared fetcher resolver records HTTP context and refuses that fallback unless `ALLOW_GLOBAL_CRED_FALLBACK` is explicitly enabled. |
| Atlassian upload | The parent only makes relative upload paths absolute and checks existence. Both fixed attachment implementations use the resolved `validate_safe_path` result before opening/uploading the file. Its default boundary is CWD. |
| Excel boundary | The parent passes absolute filenames through and joins relative paths without containment. The fixed remote branch requires a relative filename, resolves it, and checks `commonpath` before returning it. Stdio remains a different condition. |
| Mobile output | On Linux, the fixed screenshot/recording paths validate extensions and reject ordinary parent paths outside CWD and `os.tmpdir()` before their sinks. The parent lacks those checks. This label does not establish general symlink/race safety. |
| Kubernetes shell | The parent builds a command string for `execSync`; the fixed `kubectl_get` passes separate arguments to `execFileSync` without a shell. Formatting changes and other tools in the same commit do not broaden this label. |

The SSRF label intentionally does not claim general SSRF resistance. The
original fix also contains DNS checks and a header-fetcher redirect hook; the
later bundled hardening retained for authentication/upload adds protections
elsewhere. The packet discloses later bypass history and excludes those broader
claims. The linked [later upstream advisory](https://github.com/sooperset/mcp-atlassian/security/advisories/GHSA-v9m3-wfh8-5646),
published July 10, 2026 and inspected during this review, identifies a redirect
bypass through a Jira request that avoided the hooked session. Authentication
and upload share a fixing commit, and the three Git
families share repository history; these are correlated observations.

## Mutations and controls

I inspected the complete diff of each of the 20 overlays against its own
snapshot. Both members of each transformation preserve the stated condition:

| Family | Verified transformation |
| --- | --- |
| Git staging | Only the internal function definition and production identifier call are renamed; the MCP tool string remains `git_add`. |
| Git arguments | A same-file identity helper wraps the diff result; argument validation and the Git invocation retain their order. |
| Git repository | `Path` becomes an import alias with all same-file identifier references updated. |
| Filesystem prefix | The internal function and every same-file call are renamed; registered tool names and checks are unchanged. |
| Atlassian SSRF | The URL utility imports `urlparse` under an alias and updates its uses, including the fixed validator. |
| Atlassian authentication | The shared resolver definition and both production callers are renamed; guards and returned fetchers are unchanged. |
| Atlassian upload | Both upload paths pass through an imported identity function before their existing checks; public parameters remain unchanged. |
| Excel boundary | Existing return expressions pass through a same-file identity helper; no check is moved or bypassed. |
| Mobile output | The default filesystem import and all its member accesses are aliased; the modification comment is non-executable. |
| Kubernetes shell | The relevant child-process import and invocation are aliased while preserving the vulnerable command string or fixed argument array. |

The five additional safe conditions are supported by the retained source:
Git status supplies no caller command-string argument; Atlassian's path helper
checks resolved containment and returns the checked path; Excel permits the
specified ordinary contained child workbook; Mobile tests the caller locale
against its actual anchored regex before locale operations; Kubernetes formats
parsed JSON through `JSON.stringify` without executing result fields. These
labels do not assert that their entire repositories or surrounding operations
are safe. Locale validity is relative to that regex, not a claim of complete
locale syntax validation.

## Integrity, split, and licenses

Independent stdlib archive inspection and SHA-256 recomputation verified all
17 archive hashes, complete regular-file inventories, 20 overlay hashes, 45
materialized tree hashes, and every evidence-file hash/range. Retained archives
contain only regular files/directories; target code was never extracted for
execution. Preparation extraction rejects traversal, links, special files,
duplicates/case collisions, file-directory collisions, and oversized input.

There are 20 original inputs, 20 mutation inputs, and five additional labels on
reused fixed trees: 45 labels, not 45 distinct source trees. Seven families are
Python and three TypeScript. All related inputs stay in their repository's
split: 27 development and 18 held out. Atlassian and Mobile are held out.
Mutation parents have the same repository, split, family, revision, and label.

The 15 non-Mobile snapshots retain revision-specific MIT licenses. Mobile's two
snapshots retain Apache-2.0 licenses. Relevant root and package LICENSE files
remain in the archives; the project license does not replace these notices.
The Mobile overlay notice correction is recorded above.

## Configuration and matching review

The Git configuration provides 12 named baseline argument mappings and a
Docker-only bootstrap that creates disposable repositories and inert control
files. It launches the original package source with an explicit repository
boundary. This makes 13 Git inputs eligible, including the Git safe control.
The other 32 inputs remain visible as unsupported runtime conditions: native
TypeScript runtime is unsupported and the remaining Python vulnerability
conditions require HTTP/SSE or remote service prerequisites. No alternate
transport is presented as equivalent evidence for those labels.

The Git executable remains an explicit prerequisite of the proposed native
image. This review does not claim it is installed or that a baseline will
succeed. A dependency/launch failure must be recorded as incomplete, and the
four native probes must not be presented as targeted advisory reproductions.
The sidecar describes permissions; it does not enforce the repository boundary.

The matching proposal appropriately requires the specific labeled condition
and input/enforcement/sink evidence. Rule IDs and file overlap alone are
insufficient. Deduplication, abstention, incorrect suppression, safe-condition
false alarms, unmatched unadjudicated findings, and zero denominators remain
explicit. Actual post-scan adjudication is still required; none was performed.

I independently recomputed the comparator preparation from the acquired
Semgrep Rules archive, without invoking Semgrep: its archive hash matches the
metadata, and all 533 selected rule identities/hashes and 511 configuration
hashes match the declared security-category Python/JavaScript/TypeScript
selection. Upstream rule bytes remain outside the repository. This verifies
preparation, not comparator behavior or performance.

## Approval boundary

Source review does not constitute user approval, corpus freeze, runtime proof,
measurement completion, paid-request approval, or Phase 20 acceptance. Public
historical examples cannot establish absence of model exposure. The final
manifest identity above binds the corrected packet and configuration.

Final independent `scripts.phase20_corpus.validate()` completed successfully for
45 inputs, 17 snapshots, and five packet artifacts. The final gzip header
normalization changes compressed identities only; the source-tree hashes and
reviewed mutation contents are preserved. I rechecked these packet bindings:

| Artifact | SHA-256 |
| --- | --- |
| `configuration/git-bootstrap.txt` | `90e23f5481a16f01e98d884942e1bffbc8720fe8d3153f3a95af000cd2d7b1ac` |
| `configuration/git.permissions.yaml` | `a7f39c71dd7bca0a413bab904d20584362b8d396a20a33540ffbeb261a05cfae` |
| `configuration/git.target.yaml` | `ecae5624f246b55f765f888bbfe101f1f6056a2c52f3914c58c71abb8e318493` |
| `artifacts/phase20/checkpoint1-packet.md` | `632f30045998a7a1b3b72c4eab761c70b48c89157e543e115165e5c95e803cae` |
| `artifacts/phase20/semgrep-preparation.json` | `795e5da795dc894838eec68c51363f3e7c91874f166eee3cd12065445c92f23f` |

Configuration paths above are relative to `tests/evals/phase20`. A later change
to the manifest or any bound artifact invalidates this final identity and
requires review of that change before approval or evaluation.
