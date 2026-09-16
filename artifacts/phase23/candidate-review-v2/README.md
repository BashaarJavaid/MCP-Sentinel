# Phase 23 replacement candidate and source-review checkpoint

**Recommend GHSA-3q26-f695-pp76, limited to `git_init.initialBranch` shell
injection in `cyanheads/git-mcp-server`.** Seven exact proposed inputs are ready
for source review. None has been scanned, imported, installed or executed.

The [upstream advisory](https://github.com/cyanheads/git-mcp-server/security/advisories/GHSA-3q26-f695-pp76)
identifies affected versions through 2.1.4 and a fix in 2.1.5. Our source review
selects the branch-name path in `git_init`; the advisory's other Git tools and
path arguments are outside this bounded condition.

## Decision requested

Approve this replacement case and freeze its exact seven inputs, transformations,
proposed labels, matching/support conditions and order, bound to
[manifest.json](../../../tests/evals/phase23/candidate-v2/manifest.json) SHA-256:

`8a489a5593bf9397382519beccb1e01b6e5add3a7dfd1fba9b1cf070e5011d5c`

This is the plan's source-review checkpoint. It does **not** approve a scan,
detector correction, contract expansion, merge or release. Exact execution
commands, scanner/helper identities, exclusions and outer limits will follow in
a separate packet. The existing one-use baseline authorization is spent and
cannot authorize this replacement.

## Why this candidate

The original node-code-sandbox case already passes by source assessment; its
14 observations and all qualifications remain in
[baseline-assessment-v1](../baseline-assessment-v1/README.md), with human review
still distinct from measured completion.

This candidate exercises a different source pattern: `util.promisify` wraps the
execution function. In the vulnerable source, `execAsync = promisify(exec)`
receives a shell command assembled with a caller-controlled branch name. The
upstream correction changes this to `execFileAsync = promisify(execFile)` and a
literal executable with separate arguments. Node documents the
[promise wrapper](https://nodejs.org/api/util.html#utilpromisifyoriginal) and the
[exec/execFile behavior](https://nodejs.org/api/child_process.html).

**Gap hypothesis, not a measured miss:** Sentinel's current
`typescript_execution.ShellFlow.call` recognizes direct resolved `child_process`
callables. Source inspection found no explicit `promisify` model in that shared
interpreter. The wrapper may therefore lose execution identity. Registration
wrappers, schema extension, path guards and error helpers are additional
full-source support risks. A baseline must establish actual behavior before any
correction proposal; neither a miss nor a one-function fix is promised.

The production scanner and existing Phase 23 runner remain unchanged. No new
dependency, language, rule meaning or Finding/report interface is proposed.
If recovery requires a contract expansion, that decision returns to the user.

## Immutable upstream bindings

| Source | Version/tag | Revision | Files |
| --- | --- | --- | --- |
| Vulnerable | 2.1.4 / v2.1.4 | `f30169ec3a2520990e5467c19ef42ea7d6d9270e` | 122 |
| Fixed | 2.1.5 / v2.1.5 | `0dbd6995ccdf76ab770b58013034365b2d06c4d9` | 122 |

The fixed commit's direct parent is the vulnerable revision. Both complete
archives, nontruncated Git trees, tag objects, commit metadata, package versions
and all 244 Git blob hashes were verified. The manifest retains archive and
per-file SHA-256 identities. The complete upstream patch and relevant source
copies are retained; [upstream-logic-fix.patch](upstream-logic-fix.patch) isolates
the selected helper's changes.

**Licensing:** these two revisions are Apache-2.0. Complete original LICENSE and
README bytes are retained in every derived input; modified source files carry a
modification notice and each input includes MODIFICATIONS.md. These examples are
not represented as MIT-licensed submissions. No upstream NOTICE file exists in
either verified tree. The project's existing maintenance policy permits reuse
under an applicable source license with its notices retained.

## Registration-to-sink source path

The full sources preserve the actual startup and wrappers:

1. `src/index.ts` starts the server through `initializeAndStartServer`.
2. `src/mcp-server/server.ts` constructs `McpServer`, initializes tool state
   accessors and calls `registerGitInitTool` (vulnerable line 368).
3. `tools/gitInit/registration.ts` registers literal tool `git_init` at line 74.
   Its callback receives `validatedArgs`; `logicArgs` preserves `initialBranch`
   while replacing the path with a resolved/sanitized path.
4. The registration calls `gitInitLogic(logicArgs, requestContext)`. Both
   `ErrorHandler.tryCatch` wrappers call their callback (`errorHandler.ts:382`).
5. The vulnerable helper takes `input.initialBranch || "main"`, escapes double
   quotes only, appends it inside a double-quoted shell argument and invokes
   `execAsync(command)` at `logic.ts:138`. That quote replacement does not remove
   shell command substitution from the branch name.
6. The fixed helper places the branch name in an argument array and invokes
   `execFileAsync("git", args)` at `logic.ts:141`, without a shell option.

The condition presumes an otherwise valid writable repository path and ordinary
tool invocation. Those are source-level prerequisites, not runtime claims from
this work. No Git operation, shell, SSH command or model request was executed.

## Seven proposed inputs, in exact order

All sink paths below are `src/mcp-server/tools/gitInit/logic.ts`.

| Order | Input | Proposed label | Sink line |
| --- | --- | --- | --- |
| 1 | Full upstream vulnerable | Vulnerable | 138 |
| 2 | Full upstream fixed | Fixed for selected shell condition | 141 |
| 3 | Minimized vulnerable | Vulnerable | 13 |
| 4 | Minimized fixed | Fixed for selected shell condition | 13 |
| 5 | Safe literal command | Safe for selected shell condition | 13 |
| 6 | Identifier-renamed vulnerable | Vulnerable | 13 |
| 7 | Identifier-renamed fixed | Fixed for selected shell condition | 13 |

These remain correlated examples of one advisory. Full-source and derived
results will be separate. The later proposed baseline will run this order twice;
no observation is authorized by this source packet.

### Minimization and mutations

Derived registration uses one `McpServer.tool` callback and one cross-file helper.
The helper retains the actual `promisify` imports/wrappers, branch default,
vulnerable quote replacement, command construction and fixed argv construction.
The quote-replacement statement is copied exactly from upstream.

The repository path becomes the literal `/tmp/phase23-git-init`. Unrelated tool
registrations, session/path/access checks, quiet/bare options, logging, error
wrappers and post-execution filesystem checks are removed. Input is narrowed to
`initialBranch`; the SDK/Zod dependency declarations match the vulnerable source,
but no dependencies are installed. These are source reproductions, not runtime-
equivalent upstream servers or evidence that the removed wrappers are supported.

The safe control changes only the execution argument to a literal command; its
unused branch-derived construction remains. The paired identifier mutations use
the same manifest-listed mapping on both parents: `server→mcpServer`,
`gitInitLogic→initializeRepository`, `input→requestData`,
`initialBranch→branchLabel`, `targetPath→repositoryPath`,
`command→shellCommand`, `branchNameToUse→branchName`, `args→argv`,
`execAsync→runShell`, `execFileAsync→runFile`. Imported API names, module paths,
tool name, literal commands and control-flow structure remain unchanged.
The exact six transformation patches are alongside this document.

## Finding and support conditions

Each vulnerable input requires SENT-002 at its exact manifest-bound source path;
both the canonical location and static evidence ranges must include the declared
sink line. A message-only or unrelated finding does not count. Preserve all
additional findings and duplicates for assessment.

Each fixed/safe input requires zero matching findings **and established analysis
support**: completed successful report/static stage, SENT-002 selected/evaluated,
exact tool registration and source handler recognized and examined, with no
relevant unresolved flow, skip or warning preventing the shell assessment.
Unlocated warnings remain unresolved unless their irrelevance is established.
Empty unsupported results and timeouts cannot pass. Fixed argv handling does not
claim safety against Git option injection or arbitrary repository creation.

Entire ordered reports must agree across repeats under exclusions reviewed with
the execution packet. There are no retries or automatic timeout extensions.
If this baseline also passes, retain that outcome and return for another case.

## Other candidates and exposure

| Candidate | Disposition from read-only screening |
| --- | --- |
| GHSA-p4h8-56qp-hpgv, mcp-ssh | Exact vulnerable/fixed archives inspected. Promising shell-enabled argv pattern, but full implementation is `.mjs`, excluded by current traversal. Not selected because it would introduce a language-support decision. |
| GHSA-4h5r-5jm8-jxjm, gemini-mcp-tool | Advisory and tags inspected. Windows quoting plus CLI file references would need more platform/sanitizer qualification; full source not evaluated. |
| GHSA-f5pj-2738-996m, mcp-shell | Public advisory screening only; Go implementation would broaden language scope. |
| GHSA-v6wj-c83f-v46x, profullstack/mcp-server | Public advisory screening only; JavaScript HTTP endpoints would introduce further language/surface questions. |
| GHSA-fhh6-4qxv-rpqj, 9router | Public advisory screening only; multi-request plugin state and HTTP endpoints are broader than this maintenance case. |

The selected repository appears in four historical Phase 22 excluded-repository
lists. This work makes no unseen-source or independent-validation claim. It is
not the deferred `modelcontextprotocol/servers` Git benchmark, whose budget and
measurements remain untouched. Research exposure and discarded candidates are
retained in [verification.json](verification.json).

**No replacement scan, target execution, paid call or detector change occurred.**
Phase 23 remains incomplete. All earlier results, failures and deferred work
retain their original status.
