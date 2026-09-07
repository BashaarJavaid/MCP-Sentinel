# Phase 20 — Corrected-scanner completion measurement

**Phase 20 accepted on 2026-09-07 (UTC). All prepared static requests are captured; execution limitations remain.**

See the [acceptance record](phase20-acceptance.md). The report version bound by the original verification hash is [retained at the measured evidence commit](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/docs/phase20-completion-v2.md). Later changes here update publication status and links only.

This supplements the unchanged [original partial baseline](phase20-verification.md) and [execution-correction diagnostics](benchmark-execution-corrections.md). Measurement source is `8824014e961722980757bb589009dc59b78d9a37`, scanner SHA-256 `22bdb90c1a5dc23ddf6ec19c5b87adc98accd7abd5e5bd28cff16f9913b6d8dd`, harness SHA-256 `725c4ec8af374f7d9be08c19a171a8157630ba3f1f9e168e25c202a9a3e54db0`. New accepted review cost is $0.429571. Static reviewed completion rises from 22 to 32 inputs; condition-level detection does not improve. The original Semgrep measurement is reused unchanged with its own source/environment identity, rather than counted as another comparator run.

The full [scored JSON](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/results.json) retains every outcome, coverage field, source revision, decision, and denominator. The numeric tables below use the existing condition scorer. The explanatory prose records the corrected execution failures instead of the original baseline's JSONC and missing-Git failures.

Frozen manifest: `f69d043cab43e5785e7c8a9dae430bcf146c105a0d23d1d77bc4089637377682`.

The 45 condition-labeled inputs comprise ten original vulnerable/fixed pairs, ten paired structural mutations, and five safe controls across five repositories. Development and held-out repositories were separated before evaluation. Correlated variants are reported separately; public historical cases cannot establish absence of model exposure.

| Treatment | Completed / 45 | Incomplete | Unsupported | Inconclusive | Unmeasured | Vulnerable completed / 20 | Candidate recall on completed, adjudicated cases | Unadjudicated findings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dynamic | 0 | 13 | 32 | 0 | 0 | 0 | unmeasured | 0 |
| replay | 32 | 13 | 0 | 0 | 0 | 14 | 0.0% | 70 |
| rules | 32 | 13 | 0 | 0 | 0 | 14 | 0.0% | 70 |
| semgrep | 33 | 12 | 0 | 0 | 0 | 14 | 0.0% | 271 |

| Treatment | Vulnerable total / applicable / completed | Candidate / retained / confirmed detections on completed cases | Safe conditions with alerts / completed |
| --- | ---: | ---: | ---: |
| dynamic | 20 / 6 / 0 | 0 / 0 / 0 | 0 / 0 |
| replay | 20 / 20 / 14 | 0 / 0 / 0 | 0 / 18 |
| rules | 20 / 20 / 14 | 0 / 0 / 0 | 0 / 18 |
| semgrep | 20 / 20 / 14 | 0 / 0 / 0 | 0 / 19 |

## Observed limitations

The JSONC correction permits progress past devcontainer validation. Four Atlassian inputs reach the native 120-second static timeout; nine fail when Helm templates are parsed as YAML. All 13 remain incomplete. Git's low-level tool dispatch remains an unsupported registration in source coverage; completed rules do not imply that the vulnerable handler flow was covered. The 70 Sentinel warnings concern generic validation, credentials, or authentication and do not identify the labeled conditions.

The comparator returned 271 raw alerts. Kubernetes command-injection warnings concern other handlers, not the labeled kubectl_get flow. Filesystem audit warnings do not identify failure of the colliding directory-prefix check. These stay unadjudicated under the frozen input/enforcement-failure/sink criterion. This is not evidence that those warnings are useless or false positives. Twelve comparator runs include a rule timeout and remain incomplete. The initial certificate-setup failure is retained separately and is not an accuracy observation. Actual engine rule and file counts are in the raw evidence; the selected 533 rule identities are not a claim that every rule ran on every input.

All 13 eligible Docker inputs pass Git initialization but fail before tool discovery: the installed MCP SDK lacks `Server.list_tools`. The cached environment contains MCP 2.1.1 under the upstream open-ended dependency constraint. No legitimate baseline or attack was attempted. Across 52 planned probe outcomes, 13 are inconclusive startup failures and 39 are untested. There are no observed defenses or runtime confirmations. The runtime request packet contains zero requests, so Checkpoint 3 requires no paid capture. No dependency override or revised corpus configuration was used.

Paid attempts recorded: 39 ({'accepted': 35, 'failed': 4}). Accepted usage cost: $0.804567; cost including uncertain failed/interrupted reservations: $1.211247. Review cost is counted once per capture in the ledger, not once per replayed input. Zero-candidate stages make no model request and do not establish model accuracy.

Four earlier attempts failed validation and retain their full uncertain reservations. The separately approved corrected-scanner resumption accepted all 18 remaining requests without retries or new failures. All 35 request hashes and input memberships match the original preparation; 17 accepted captures were reused with their original provenance. The corrected packet binds the new scanner source identity, 39 cumulative attempts, and the unchanged $3.72 cumulative ceiling. That attempt limit is exhausted; it authorizes no further new attempts.

Accepted capture token usage: {'cache_write_tokens': 59875, 'cached_tokens': 1579, 'input_tokens': 61559, 'output_tokens': 25207, 'reasoning_tokens': 16348, 'total_tokens': 86766}. Original accepted live latency summed across unique requests: 380.818 seconds. Reasoning, cached and cache-write counts are subsets of the input/output totals; they must not be added again.

Accepted GPT decisions across all static candidate instances: {'confirmed': 36, 'needs_review': 6, 'suppressed': 28}. These include unrelated warnings and repeated use of shared captures. They are distinct from condition-matched abstentions and incorrect suppressions, and do not establish whole-repository correctness.

`replay` is the GPT-reviewed static treatment; `dynamic` is the normal reviewed pipeline. Original live latency is retained in native review telemetry; replay wall duration is separate. Runtime has 13 eligible Python Git inputs and 32 unsupported inputs. Eligibility does not imply successful probing.

Candidate, retained (including `needs_review`), and confirmed-only recall, false alarms on labeled safe conditions, abstentions, incorrect suppressions, coverage, and all split/language/repository/variant breakdowns are in the generated JSON. Total-corpus observed fractions include unfinished inputs in their denominator and are not completed-treatment recall. Zero denominators are null. Unmatched findings remain unadjudicated; whole-repository precision is not claimed.

## Static breakdowns

Rules and reviewed static have identical completion and condition-detection counts. Every row below applies to each tier separately; it is not a pooled sample. All condition-matched retained and confirmed counts are also zero.

| Dimension | Group | Completed / total | Vulnerable completed / total | Candidate detections |
| --- | --- | ---: | ---: | ---: |
| split | development | 27 / 27 | 12 / 12 | 0 |
| split | held_out | 5 / 18 | 2 / 8 | 0 |
| variant | mutation | 14 / 20 | 7 / 10 | 0 |
| variant | original | 14 / 20 | 7 / 10 | 0 |
| variant | safe_control | 4 / 5 | 0 / 0 | 0 |
| language | python | 18 / 31 | 8 / 14 | 0 |
| language | typescript | 14 / 14 | 6 / 6 | 0 |
| repository | Flux159/mcp-server-kubernetes | 5 / 5 | 2 / 2 | 0 |
| repository | haris-musa/excel-mcp-server | 5 / 5 | 2 / 2 | 0 |
| repository | mobile-next/mobile-mcp | 5 / 5 | 2 / 2 | 0 |
| repository | modelcontextprotocol/servers | 17 / 17 | 8 / 8 | 0 |
| repository | sooperset/mcp-atlassian | 0 / 13 | 0 / 6 | 0 |

## Timing and verification

| Measurement | Observed wall seconds |
| --- | ---: |
| rules | 732.371 |
| replay | 792.202 |
| dynamic | 63.507 |
| rules-repeat | 779.434 |
| replay-repeat | 791.813 |

Offline runs overlap; these wall durations are retained observations, not isolated throughput estimates. Original live request latency is reported above and is not replaced by replay duration. Both 45-input static repeats pass native stable-finding/coverage/outcome comparison, excluding volatile identifiers and timing. Failure reasons also match. All per-input native reports were validated against JSON 1.6.0 and SARIF 2.1.0 during measurement.

The current platform regression matrix remains required. CI checks corpus/comparator metadata from the PR, then verifies the versioned evidence against the exact measured scanner in parallel deterministic and replay jobs. Independent Docker and private community-rule measurements remain explicit. All 29 [CI jobs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34067265137) passed for the final evidence commit, along with the documentation build. PRs #20 and #21 are merged.

## Reproduction

Use a fresh checkout at the measured source revision and the locked development environment (`uv sync --frozen --extra dev`). Preserve its original `artifacts/phase20/{rules,replay,prepare-live,dynamic,runtime-replay}` directories elsewhere. Copy the versioned directories of those names, `captures`, `adjudications.json`, and `measurement-environment.json` into that checkout’s canonical `artifacts/phase20` location. Keep its unchanged corpus, freeze, comparator metadata, and original raw Semgrep evidence. This reconstructs the isolated measurement workspace without changing the original baseline in the working repository.

```sh
python -m scripts.run_phase20_benchmark validate
python -m scripts.run_phase20_benchmark rules --output /tmp/phase20-v2-rules --compare-to artifacts/phase20/rules
python -m scripts.run_phase20_benchmark replay --output /tmp/phase20-v2-replay --compare-to artifacts/phase20/replay
python -c "from scripts.phase20_corpus import CORPUS, validate; from scripts.phase20_scoring import build_results; build_results(validate(CORPUS / 'manifest.yaml'))"
```

The final command regenerates scored `artifacts/phase20/results.json` using the existing scorer; this document supplies the version-specific interpretation. `python -m scripts.run_phase20_benchmark report` in the original frozen checkout reproduces the original report. Output directories must be fresh. Replaying requires retained cassettes but no API key or network. The full native per-input JSON/SARIF reports are retained for both initial and repeated static runs.

To repeat Docker explicitly, use `python -m scripts.run_phase20_benchmark dynamic --output /tmp/phase20-v2-dynamic` after static replay; it sends no model requests. The result depends on the recorded runtime image/dependency prerequisites. No compatible SDK override has been approved. To repeat Semgrep, acquire the separately pinned community-rule snapshot and use the original report’s explicit `semgrep --rules-dir` command. Rule bytes are not redistributed. Do not make further paid calls from these reproduction commands; new static requests or runtime evidence require a new exact request packet and approval.

## Evidence

- [checkpoint2-packet.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/checkpoint2-packet.md)
- [checkpoint2-approval.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/checkpoint2-approval.json)
- [checkpoint2-outcome.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/checkpoint2-outcome.md)
- [checkpoint2-outcome.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/checkpoint2-outcome.json)
- [new-capture-condition-review.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/new-capture-condition-review.json)
- [adjudications.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/adjudications.json)
- [captures/ledger.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/captures/ledger.json)
- [checkpoint3-outcome.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/checkpoint3-outcome.json)
- [dynamic/budget-packet.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/dynamic/budget-packet.json)
- [measurement-environment.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/measurement-environment.json)
- [preparation-verification.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/preparation-verification.json)
- [rules-repeat/reproducibility.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/rules-repeat/reproducibility.json)
- [replay-repeat/reproducibility.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/f37402e48eb49a4495facabc7033e97ed66edd1b/artifacts/phase20/completion-v2/replay-repeat/reproducibility.json)

## Documented comparator capabilities


Snyk Agent Scan documents discovery of agent configurations and skills, connection
to MCP servers to retrieve declared capabilities, local checks, and transmission of
analysis data to its API. The documented MCP workflow takes client configurations
and may launch their stdio commands; this corpus instead supplies source snapshots.
Performance is **unmeasured**: no equivalent configuration/metadata corpus, isolated
vendor execution setup, or approved external-analysis treatment was prepared. [Snyk
scanning
documentation](https://github.com/snyk/agent-scan/blob/main/docs/scanning.md), [Snyk
CLI execution
contract](https://github.com/snyk/agent-scan/blob/main/docs/cli-reference.md).

Cisco MCP Scanner documents offline scanning of pre-generated MCP JSON with YARA and
optional LLM/API analyzers. It separately documents source behavioral analysis with
LLM alignment checks and cross-file dataflow, including Python and TypeScript.
Performance is **unmeasured**: the JSON input treatment differs from source
scanning, and no pinned behavioral analyzer/provider configuration or paid budget
was selected for this benchmark. This is not a claim that Cisco only scans metadata
or cannot analyze the corpus. [Cisco source analysis
documentation](https://github.com/cisco-ai-defense/mcp-scanner#behavioral-code-scanning-multi-language),
[Cisco offline JSON
documentation](https://github.com/cisco-ai-defense/mcp-scanner/blob/main/docs/static-scanning.md).

These are vendor-documented capabilities, not measured comparative results. No
performance or superiority ranking is supported.


Phase 20 measures a weak baseline honestly; it does not establish product usefulness or whole-repository safety. Phase 21 validates maintainer workflows and Phase 22 owns bounded coverage improvements using these gaps. The user accepted Phase 20 and authorized merge and documentation publication; see the acceptance record.
