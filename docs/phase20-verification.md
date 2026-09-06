# Phase 20 — Independent detection benchmark

**Partial baseline retained; final Phase 20 acceptance is pending.**

Frozen manifest: `f69d043cab43e5785e7c8a9dae430bcf146c105a0d23d1d77bc4089637377682`.

The 45 condition-labeled inputs comprise ten original vulnerable/fixed pairs, ten paired structural mutations, and five safe controls across five repositories. Development and held-out repositories were separated before evaluation. Correlated variants are reported separately; public historical cases cannot establish absence of model exposure.

| Treatment | Completed / 45 | Incomplete | Unsupported | Inconclusive | Unmeasured | Vulnerable completed / 20 | Candidate recall on completed, adjudicated cases | Unadjudicated findings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rules | 32 | 13 | 0 | 0 | 0 | 14 | 0.0% | 70 |
| replay | 22 | 23 | 0 | 0 | 0 | 10 | 0.0% | 70 |
| dynamic | 0 | 13 | 32 | 0 | 0 | 0 | unmeasured | 0 |
| semgrep | 33 | 12 | 0 | 0 | 0 | 14 | 0.0% | 271 |

| Treatment | Vulnerable total / applicable / completed | Candidate / retained / confirmed detections on completed cases | Safe conditions with alerts / completed |
| --- | ---: | ---: | ---: |
| rules | 20 / 20 / 14 | 0 / 0 / 0 | 0 / 18 |
| replay | 20 / 20 / 10 | 0 / 0 / 0 | 0 / 12 |
| dynamic | 20 / 6 / 0 | 0 / 0 / 0 | 0 / 0 |
| semgrep | 20 / 20 / 14 | 0 / 0 / 0 | 0 / 19 |

## Observed limitations

Sentinel cannot parse Atlassian's JSON-with-comments devcontainer configuration under the frozen input configuration: all 13 inputs remain incomplete. Git's low-level tool dispatch is reported as an unsupported registration by source coverage; completed rules do not imply the vulnerable handler flow was covered. The 70 Sentinel warnings concern generic validation, credentials or authentication and do not identify the labeled conditions.

The comparator returned 271 raw alerts. Kubernetes command-injection warnings concern other handlers, not the labeled kubectl_get flow. Filesystem audit warnings do not identify failure of the colliding directory-prefix check. These stay unadjudicated under the frozen input/enforcement-failure/sink criterion. This is not evidence that those warnings are useless or false positives. Twelve comparator runs include a rule timeout and remain incomplete. The initial certificate-setup failure is retained separately and is not an accuracy observation. Actual engine rule and file counts are in the raw evidence; the selected 533 rule identities are not a claim that every rule ran on every input.

All 13 eligible Docker runs failed because the native image lacks the Git executable. No legitimate baseline or attack completed. The remaining probes are untested; no defense or exploit confirmation is inferred. The retained runtime review packet has zero requests.

Paid attempts recorded: 20 ({'accepted': 17, 'failed': 3}). Accepted usage cost: $0.374996; cost including uncertain failed/interrupted reservations: $0.679951. Review cost is counted once per capture in the ledger, not once per replayed input. Zero-candidate stages make no model request and do not establish model accuracy.

Failed attempts: attempt 6: injection probe requires a string field; attempt 19: injection probe requires a string field; attempt 20: injection probe requires a string field. Each failure stops capture until a new user decision. Rejected responses have no accepted usage telemetry; their full reservations remain charged conservatively. Missing captures leave reviewed inputs incomplete. The original request packet is unchanged; the ledger binds each approved cumulative request/cost ceiling and the retained capture history records each separately authorized resumption.

Accepted capture token usage: {'input_tokens': 30406, 'cached_tokens': 1579, 'cache_write_tokens': 28776, 'output_tokens': 11514, 'reasoning_tokens': 7149, 'total_tokens': 41920}. Original accepted live latency summed across unique requests: 191.290 seconds. Reasoning, cached and cache-write counts are subsets of the input/output totals; they must not be added again.

Accepted GPT decisions across all static candidate instances: {'suppressed': 16, 'needs_review': 2, 'confirmed': 21}. These include unrelated warnings and repeated use of shared captures. They are distinct from condition-matched abstentions and incorrect suppressions, and do not establish whole-repository correctness.

`replay` is the GPT-reviewed static treatment; `dynamic` is the normal reviewed pipeline. Original live latency is retained in native review telemetry; replay wall duration is separate. Runtime has 13 eligible Python Git inputs and 32 unsupported inputs. Eligibility does not imply successful probing.

Candidate, retained (including `needs_review`), and confirmed-only recall, false alarms on labeled safe conditions, abstentions, incorrect suppressions, coverage, and all split/language/repository/variant breakdowns are in the generated JSON. Total-corpus observed fractions include unfinished inputs in their denominator and are not completed-treatment recall. Zero denominators are null. Unmatched findings remain unadjudicated; whole-repository precision is not claimed.

## Reproduction

```sh
python -m scripts.run_phase20_benchmark validate
python -m scripts.run_phase20_benchmark rules --output /tmp/phase20-rules-repeat
python -m scripts.run_phase20_benchmark prepare-live --output /tmp/phase20-requests-repeat
python -m scripts.run_phase20_benchmark replay --output /tmp/phase20-replay-repeat
python -m scripts.run_phase20_benchmark semgrep --rules-dir /tmp/phase20-community-rules --output /tmp/phase20-comparator-repeat
python -m scripts.run_phase20_benchmark report
```

Install the locked development environment first (`uv sync --frozen --extra dev`). Obtain the exact private community-rule snapshot using the Checkpoint 1 packet; do not commit rule bytes. Measurement commands refuse to overwrite evidence. Repeated static execution is reproducibility verification, not an additional accuracy observation. Full native JSON 1.6.0 and SARIF 2.1.0 reports are retained per input; failures without native reports remain in `results.json`.

`prepare-live` runs the production request builder offline, serially, with GPT-5.6 Sol medium, retries disabled, cache disabled, and the 500-finding default. It never reads an API key. `capture-live --stage static --approval <file>` requires a separately approved packet hash and cumulative request/dollar ceilings. Runtime capture uses `--stage runtime` and a separate Checkpoint 3 decision. `dynamic` requires completed eligible static replay and uses native Docker isolation. It preserves runtime proof and prepares new runtime review requests offline.

Phase 20 remains open until all evidence gates pass. Detectors, prompts and probes have not been tuned. Historical ablation/walkthrough artifacts and native scanner contracts are unchanged. Draft PR merge, public deployment and final acceptance still require explicit approval.

## Evidence

- [freeze.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/freeze.json)
- [checkpoint1-packet.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint1-packet.md)
- [checkpoint1-independent-review.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint1-independent-review.md)
- [checkpoint2-packet.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-packet.md)
- [checkpoint2-approval.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-approval.json)
- [checkpoint2-capture-outcome.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-capture-outcome.md)
- [checkpoint2-resume-proposal.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-proposal.json)
- [checkpoint2-resume-approval.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-approval.json)
- [checkpoint2-resume-outcome.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-outcome.md)
- [checkpoint2-resume-proposal-2.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-proposal-2.json)
- [checkpoint2-resume-approval-2.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-approval-2.json)
- [checkpoint2-resume-outcome-2.md](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-outcome-2.md)
- [checkpoint2-resume-proposal-3.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/checkpoint2-resume-proposal-3.json)
- [captures/ledger.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/captures/ledger.json)
- [measurement-environment.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/measurement-environment.json)
- [adjudications.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/adjudications.json)
- [results.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/results.json)
- [prepare-live/budget-packet.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/prepare-live/budget-packet.json)
- [dynamic/budget-packet.json](https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark/artifacts/phase20/dynamic/budget-packet.json)

## Documented comparator capabilities (2026-09-06)

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
