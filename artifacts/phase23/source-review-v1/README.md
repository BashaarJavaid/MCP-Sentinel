# Phase 23 checkpoint 2: source and label review

**Prepared, not frozen or scanned.** Checkpoint 1 wording is adopted locally;
its [receipt](../intake-adoption.json) binds the exact approved patch. Phase 23
remains incomplete, with correction, technical acceptance and release still
subject to later checkpoints.

## Decision requested

Approve the seven inputs, exact bytes, minimization, identifier mutations,
proposed source labels, finding/support conditions and order in the
[manifest](../../../tests/evals/phase23/manifest.json) for freezing, or specify
changes. The manifest SHA-256 is:

`b0d7d2420d5242eedae3666dac499b2da119607af98d0f59cda28e902f9f6e0e`

This approval would freeze the proposed source contract. **It would not authorize
a scan.** The next checkpoint will present exact baseline commands, scanner and
configuration identities, ordered-report exclusions and outer time cap. The
baseline and any corrected-candidate evaluation are separate 14-observation
stages; no retries or extensions are implied.

The user's plan requires approval of **“exact source bytes, minimization,
mutations, labels, finding-match conditions, order and manifest hashes before
freezing or scanning.”** This is the reason for this checkpoint.

## Source provenance

The selected [upstream advisory](https://github.com/alfonsograziano/node-code-sandbox-mcp/security/advisories/GHSA-5w57-2ccq-8w95)
identifies versions through 1.2.0 as vulnerable and versions from 1.3.0 as patched.
The retained [advisory JSON](provenance/advisory.json) records publication at
`2025-07-08T06:35:04Z`; that is separate from Phase 23 intake and work timing.

| Source | Exact commit | Full files | Proposed bounded label |
| --- | --- | ---: | --- |
| Upstream v1.2.0 | `7fd7fb88be2cb2a03702915d05d03bdf6bc8ac80` | 86 | Vulnerable shell interpolation in `sandbox_stop` |
| Upstream v1.3.0 | `19a1ff3386c5bc00eb1f2052a4fa8f8379bb8fea` | 87 | Fixed for that shell-injection condition |

Both complete compressed snapshots remain under `tests/evals/phase23/snapshots/`.
Every file has a SHA-256 inventory entry; all 173 bytestrings also match Git blob
identities in complete, non-truncated trees. Annotated tag objects resolve to
the requested commits, and package versions agree. The comparison retains all
14 intervening commits. The stop correction began at `79d7fca`, reached the
merged fix `e461a74` through upstream PR #93, then shipped in the 1.3.0 version
commit. The version commit itself changes package metadata; it is not presented
as the whole detector-relevant source patch.

The full READMEs retain explicit MIT permission text. There is no root LICENSE
file and no invented copyright holder. Each minimized/mutated input includes
its parent revision's exact README as `UPSTREAM-README.md`; the full snapshots
also retain the separate website license. Public source availability alone is
not the reuse basis: the README permission notice is. Human source/license review
remains pending with this packet.

## Complete source path assessment

Convenience source copies under `source/` are byte-identical to the archive
members; the archives, not the convenience copies, are the full scan inputs.

1. Both [server revisions](source/vulnerable/src/server.ts) import the official
   MCP server/stdio transport, import `stopSandbox` and `argSchema as stopSchema`
   from `./tools/stop.ts` at line 15, instantiate `McpServer` at lines 38–50,
   register `sandbox_stop` with that schema and function at lines 80–85, and
   connect the transport at lines 192–196. `src/server.ts` is identical across
   the two revisions.
2. The [vulnerable handler](source/vulnerable/src/tools/stop.ts) accepts an
   unrestricted `z.string()` at line 7, destructures `container_id` at lines
   9–13, and interpolates it into `execSync` at line 22. Its preceding
   `isDockerRunning()` guard checks Docker availability, not the argument:
   [utils.ts](source/vulnerable/src/utils.ts), lines 104–112, runs the literal
   `docker info` command. Registry deletion occurs after the sink; neither that
   operation nor the catch/response formatting prevents shell interpretation.
3. The [fixed handler](source/fixed/src/tools/stop.ts) constrains the schema at
   lines 11–13, calls `sanitizeContainerId` and rejects a null result at lines
   26–31, then calls `execFileSync('docker', ['rm', '-f', validId])` at line 35.
   The [validator](source/fixed/src/utils.ts), lines 151–157, accepts only strings
   beginning with an alphanumeric and followed by alphanumerics, `_`, `.` or `-`.
   The argument remains a separate argv element and no shell option is enabled.
4. Imports, registration and sink selection are source-assessed. Target startup,
   SDK execution, Docker availability, runtime exploitability, other tool paths
   and broader sandbox safety were not executed or established. Other upstream
   tools and configuration remain in the full inputs and may yield unrelated
   findings or unresolved surfaces that must stay visible.

See the [source correction diff](upstream-stop-fix.patch). Source labels do not
establish that Sentinel currently recognizes this path or produces a finding.

## Seven correlated inputs and proposed order

Each stage proposes this order, followed by the same order once more. These are
seven correlated examples of **one advisory**, not seven independent cases.
Full, minimized, safe-control and renamed outcomes will be reported separately.

| Position | Input | Proposed label | Exact sink in `src/tools/stop.ts` |
| --- | --- | --- | --- |
| 1 | `full-vulnerable` | vulnerable | line 22 |
| 2 | `full-fixed` | fixed | line 35 |
| 3 | `minimized-vulnerable` | vulnerable | line 7 |
| 4 | `minimized-fixed` | fixed | line 14 |
| 5 | `safe-literal` | safe for the selected injection condition | line 7 |
| 6 | `renamed-vulnerable` | vulnerable | line 7 |
| 7 | `renamed-fixed` | fixed | line 14 |

### Exact minimization

The minimized pair retains separate server and imported-handler modules, the
official `McpServer`/stdio imports and tool registration, a destructured string
argument, and the actual `execSync` versus `execFileSync` distinction. The fixed
case retains both the upstream schema regex and the complete seven-line upstream
identifier validator in `src/utils.ts`, with the guard before the argv call.

It removes unrelated tools/resources/prompts, logging, UUID/package-metadata
startup, scavenging and shutdown, Docker availability checks, registry mutation,
exception handling and verbose responses. The response is a minimal typed text
object. The server metadata is a literal reproduction name/version. The new
private package manifest declares only module syntax, SDK `^1.10.2` and Zod
`^3.24.3` (the latter matches the upstream lock's 3.24.3), without install/build
scripts. No dependency was installed. The Docker-running precondition remains
part of the full-source explanation; its removal in minimized inputs means those
inputs are not runtime-equivalent copies of the complete server.

Exact code is under
[inputs](../../../tests/evals/phase23/inputs/); the
[minimized pair diff](minimized-fix.patch) shows the changed safety conditions.

### Safe control and identifier mutations

The [safe control](safe-literal.patch) changes one line in the minimized
vulnerable case: the command becomes the literal
`docker rm -f phase23-safe-container`. It retains the input/registration and
shell API, but the tool argument does not enter that command. It is safe only
for the selected input-injection condition; it is never executed here.

The [vulnerable rename](renamed-vulnerable.patch) and
[fixed rename](renamed-fixed.patch) apply the same identifier map: `server` →
`mcpServer`, `stopSandbox` → `removeSandbox`, `argSchema` → `argumentsSchema`,
`stopSchema` → `inputSchema`, `container_id` → `sandbox_ref`, `validId` →
`checkedRef`, and `sanitizeContainerId` → `validateSandboxRef` where present.
The schema field and its uses change together. Tool name, imports of external
APIs, paths, regexes, command strings and parameter flow otherwise remain intact.
Package and README bytes are unchanged from the corresponding minimized parent.

## Finding and support contract for review

Each vulnerable input needs at least one canonical **SENT-002** finding whose
file location is `src/tools/stop.ts`, whose inclusive source range covers the
declared sink line, and whose static evidence belongs to that source-bound sink.
An alert at an unrelated location or a message-only match does not satisfy it.
The manifest binds the exact sink text and file hash; there is no fuzzy
line-matching exception. Preserve additional findings and duplicates for review.

Each fixed/safe input needs zero such matching findings **and established analysis
support**: completed successful report and static stage, selected/evaluated
SENT-002, the exact tool registration and source-bound handler recognized, that
rule listed as examined, and no relevant unresolved flow, skip or warning that
prevents assessment. An unlocated warning whose relevance cannot be ruled out
leaves support unresolved. A rule visit or empty report alone is insufficient.
All other findings and diagnostics require source assessment.

Both passes must complete and entire ordered reports agree under separately
reviewed volatile exclusions. No exclusion is approved in this source packet.
Timeouts, unsupported negatives and incomplete inputs remain failed/unestablished;
there are no automatic retries. If the baseline meets the gate, retain that result
and return for a different candidate rather than inventing a detector correction.

## Verification and next step

Run `.venv/bin/python -m scripts.phase23_regression` for source-integrity checks;
it does not scan, freeze or judge reports. Focused checks and the required local
gate are bound in [verification.json](verification.json). The source helper's
current purpose is preparation; execution and report comparison will be added
against the reviewed contract in the later execution packet.

Known preparation failures remain recorded: the initial GitHub request and docs
check were blocked by sandbox access, the commit-addressed tree response failed
an identity assertion before the actual tree objects were fetched, and the old
maintenance test still expected empty contact links and 11 rules. Its updated
check uses the canonical current catalog and verifies the adopted forms. Initial
test-regex lint and focused mypy invocation errors are recorded in verification.

Zero advisory scans, profiles, comparators, target executions or paid calls.
No detector code, historical corpus validator, frozen measurement, package version,
release tag or Action alias changed. Phase 22's accepted limitations and all
excluded/deferred work remain intact.
