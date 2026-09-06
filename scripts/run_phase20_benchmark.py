"""Phase 20 benchmark preparation. Evaluation requires Checkpoint 1 approval."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.capture_gpt_reviews import _atomic_json
from scripts.phase20_corpus import CORPUS, ROOT, Manifest, digest, validate

ARTIFACTS = ROOT / "artifacts/phase20"
REPORT = ROOT / "docs/phase20-verification.md"
BLOB = (
    "https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark"
)


def preparation_result(manifest: Manifest, manifest_path: Path) -> dict[str, Any]:
    comparator = json.loads((ARTIFACTS / "semgrep-preparation.json").read_text())
    if (
        comparator["engine_version"] != "1.176.0"
        or comparator["redistributed_rule_bytes"]
        or comparator["rule_count"] != len(comparator["rules"])
        or comparator["configuration_count"]
        != len({r["source_path"] for r in comparator["rules"]})
        or any(
            r["category"] != "security"
            or not set(r["languages"]) & {"python", "javascript", "typescript"}
            for r in comparator["rules"]
        )
    ):
        raise ValueError("invalid retained comparator selection")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "artifact_version": 1,
        "phase_status": "checkpoint1_pending_user_approval",
        "measurement_status": "not_evaluated",
        "manifest_sha256": digest(manifest_path.read_bytes()),
        "independent_review": {
            "path": "artifacts/phase20/checkpoint1-independent-review.md",
            "sha256": digest(
                (ARTIFACTS / "checkpoint1-independent-review.md").read_bytes()
            ),
        },
        "scanner_base_revision": revision,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "sentinel": importlib.metadata.version("portunusmcp-sentinel"),
            "semgrep": importlib.metadata.version("semgrep"),
        },
        "input_count": len(manifest.inputs),
        "snapshot_count": len(manifest.snapshots),
        "unique_source_tree_count": len({i.tree_sha256 for i in manifest.inputs}),
        "splits": dict(Counter(i.split for i in manifest.inputs)),
        "variants": dict(Counter(i.variant for i in manifest.inputs)),
        "runtime_applicability": dict(
            Counter(i.runtime_applicability for i in manifest.inputs)
        ),
        "comparator": {k: v for k, v in comparator.items() if k != "rules"},
        "treatments": ["rules", "reviewed_static", "reviewed_normal", "semgrep"],
        "outcomes": [
            {
                "input_id": i.id,
                "split": i.split,
                "language": i.language,
                "repository": i.repository,
                "variant": i.variant,
                "label": i.label,
                "source_tree_sha256": i.tree_sha256,
                "runtime_applicability": i.runtime_applicability,
                "runtime_reason": i.runtime_reason,
                "treatments": {
                    name: {
                        "state": "not_evaluated",
                        "reason": "Checkpoint 1 approval required",
                        "finding_count": None,
                    }
                    for name in (
                        "rules",
                        "reviewed_static",
                        "reviewed_normal",
                        "semgrep",
                    )
                },
            }
            for i in manifest.inputs
        ],
        "metrics": None,
        "model_requests": 0,
        "live_spend_micro_usd": 0,
    }


def render_preparation(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 20 — Independent detection benchmark",
        "",
        "**Preparation only. Checkpoint 1 approval is pending; "
        "the baseline has not been measured.**",
        "",
        f"Manifest SHA-256: `{result['manifest_sha256']}`.",
        "",
        "The prepared corpus has 45 condition-labeled inputs across five repositories: "
        "20 original pair members, 20 structural mutation members, "
        "and five safe controls. It retains 17 upstream snapshots and "
        f"{result['unique_source_tree_count']} unique "
        "source trees. Safe controls reuse fixed trees; multiple labels can also share "
        "an upstream revision. These are correlated observations.",
        "",
        "Development: 27 inputs. Held out: 18 inputs. Native runtime prerequisites: "
        "13 Git inputs eligible for stdio; 32 other inputs require unsupported "
        "HTTP/SSE or TypeScript runtime. Eligibility is not successful execution.",
        "",
        "No Sentinel, GPT, Docker, or Semgrep corpus measurements have run. "
        "All treatment outcomes are `not_evaluated`; finding counts and detection "
        "metrics are null. No miss, false alarm, completion, or accuracy is inferred.",
        "",
        "## Preparation evidence",
        "",
        f"- [Checkpoint 1 packet]({BLOB}/artifacts/phase20/checkpoint1-packet.md)",
        "- [Independent review]"
        f"({BLOB}/artifacts/phase20/checkpoint1-independent-review.md)",
        f"- [Manifest]({BLOB}/tests/evals/phase20/manifest.yaml)",
        "- [All pending input outcomes]"
        f"({BLOB}/artifacts/phase20/preparation-results.json)",
        "- [Pinned Semgrep metadata]"
        f"({BLOB}/artifacts/phase20/semgrep-preparation.json)",
        "",
        "## Reproduce preparation offline",
        "",
        "Install the repository's locked development environment before disconnecting:",
        "",
        "```sh",
        "uv sync --frozen --extra dev",
        "python -m scripts.run_phase20_benchmark validate",
        "python -m scripts.run_phase20_benchmark report",
        "pytest tests/test_phase20.py --no-cov -q",
        "```",
        "",
        "`validate` checks the retained source/packet hashes, Pydantic manifest, "
        "safe archive handling, source evidence and repository split/lineage. "
        "`report` writes this preparation record and every pending outcome. "
        "Neither command executes/imports target code or performs scanner evaluation. "
        "`python -m scripts.prepare_phase20_corpus` regenerates the proposed manifest "
        "and overlays from retained originals; changes invalidate the review hash.",
        "",
        "Semgrep 1.176.0 preparation selected 533 security rules in 511 configurations "
        "from the pinned community snapshot before seeing scanner results. Rules are "
        "kept in a separate local directory and are not redistributed. Reproduction "
        "requires the pinned download and preparation command in the packet.",
        "",
        "## Remaining gated work",
        "",
        "Checkpoint 1 must approve the exact manifest and independent review before "
        "freeze or evaluation. The downstream `rules`, `replay`, `prepare-live`, "
        "`capture-live`, `dynamic`, and explicit `semgrep` measurement commands are "
        "not implemented in this preparation checkpoint. They remain required "
        "before Phase 20 can close. No placeholder measurement is substituted.",
        "",
        "Checkpoint 2 will separately approve exact static-review requests, dated "
        "pricing and a user-selected budget. Checkpoint 3 will separately approve "
        "review of new runtime evidence. Production findings, native report 1.6.0, "
        "SARIF 2.1.0, detector behavior and historical artifacts remain unchanged.",
        "",
        "Adjudication/scoring, full deterministic/replay CI, Docker "
        "evidence, paid captures and a measured baseline remain required deliverables. "
        "Public historical cases cannot establish absence of model exposure. "
        "Merge, public deployment and final phase acceptance require "
        "explicit approval.",
        "",
        "## Documented comparator capabilities (2026-09-06)",
        "",
        "Snyk Agent Scan documents discovery of agent configurations and skills, "
        "connection to MCP servers to retrieve declared capabilities, local checks, "
        "and transmission of analysis data to its API. The documented MCP workflow "
        "takes client configurations and may launch their stdio commands; this "
        "corpus instead supplies source snapshots. Performance is **unmeasured**: "
        "no equivalent configuration/metadata corpus, isolated vendor execution "
        "setup, or approved external-analysis treatment was prepared. "
        "[Snyk scanning documentation]"
        "(https://github.com/snyk/agent-scan/blob/main/docs/scanning.md), "
        "[Snyk CLI execution contract]"
        "(https://github.com/snyk/agent-scan/blob/main/docs/cli-reference.md).",
        "",
        "Cisco MCP Scanner documents offline scanning of pre-generated MCP JSON "
        "with YARA and optional LLM/API analyzers. It separately documents "
        "source behavioral analysis with LLM alignment checks and cross-file "
        "dataflow, including Python and TypeScript. Performance is **unmeasured**: "
        "the JSON input treatment differs from source scanning, and no pinned "
        "behavioral analyzer/provider configuration or paid budget was selected "
        "for this benchmark. This is not a claim that Cisco only scans metadata "
        "or cannot analyze the corpus. "
        "[Cisco source analysis documentation]"
        "(https://github.com/cisco-ai-defense/mcp-scanner"
        "#behavioral-code-scanning-multi-language), "
        "[Cisco offline JSON documentation]"
        "(https://github.com/cisco-ai-defense/mcp-scanner/blob/main/docs/static-scanning.md).",
        "",
        "These are vendor-documented capabilities, not measured comparative "
        "results. No performance or superiority ranking is supported.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "report"))
    args = parser.parse_args()
    path = CORPUS / "manifest.yaml"
    result = preparation_result(validate(path), path)
    if args.command == "report":
        _atomic_json(ARTIFACTS / "preparation-results.json", result)
        REPORT.write_text(render_preparation(result), encoding="utf-8")
    print(f"Validated 45 labeled inputs; manifest SHA-256 {result['manifest_sha256']}")
    print("Checkpoint 1 pending. No corpus evaluation or model requests performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
