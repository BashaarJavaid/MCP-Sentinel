"""Frozen Phase 20 measurements; paid review requires a separate budget approval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.phase20_corpus import CORPUS, ROOT, digest, validate

ARTIFACTS = ROOT / "artifacts/phase20"
REPORT = ROOT / "docs/phase20-verification.md"
BLOB = (
    "https://github.com/BashaarJavaid/MCP-Sentinel/blob/phase20-independent-benchmark"
)

COMPARATOR_CAPABILITIES = """

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
"""


def validate_comparator_metadata() -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "validate",
            "report",
            "rules",
            "replay",
            "prepare-live",
            "capture-live",
            "dynamic",
            "semgrep",
        ),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rules-dir", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--compare-to", type=Path)
    parser.add_argument("--stage", choices=("static", "runtime"), default="static")
    args = parser.parse_args()
    path = CORPUS / "manifest.yaml"
    manifest = validate(path)
    if args.command in {"rules", "replay", "prepare-live", "dynamic", "semgrep"}:
        from scripts.phase20_measurements import measure

        treatment = (
            "runtime-replay"
            if args.command == "replay" and args.stage == "runtime"
            else args.command
        )
        measurement = measure(
            manifest,
            treatment,
            args.output or ARTIFACTS / treatment,
            rules_dir=args.rules_dir,
        )
        if args.command in {"prepare-live", "dynamic"}:
            from scripts.phase20_review import prepare_packet

            prepare_packet(measurement, args.output or ARTIFACTS / args.command)
        if args.compare_to:
            from scripts.phase20_measurements import verify_repeat

            verify_repeat(args.compare_to, args.output or ARTIFACTS / treatment)
        return 0
    if args.command == "capture-live":
        from scripts.phase20_review import capture

        if args.approval is None:
            parser.error(
                "capture-live requires --approval with the separately approved budget"
            )
        return capture(args.stage, args.approval)
    validate_comparator_metadata()
    if args.command == "report":
        from scripts.phase20_scoring import build_results, render_results

        text = render_results(build_results(manifest))
        text += (
            "\n## Evidence\n\n"
            + "\n".join(
                f"- [{name}]({BLOB}/artifacts/phase20/{name})"
                for name in (
                    "freeze.json",
                    "checkpoint1-packet.md",
                    "checkpoint1-independent-review.md",
                    "checkpoint2-packet.md",
                    "checkpoint2-approval.json",
                    "checkpoint2-capture-outcome.md",
                    "checkpoint2-resume-proposal.json",
                    "checkpoint2-resume-approval.json",
                    "checkpoint2-resume-outcome.md",
                    "checkpoint2-resume-proposal-2.json",
                    "captures/ledger.json",
                    "measurement-environment.json",
                    "adjudications.json",
                    "results.json",
                    "prepare-live/budget-packet.json",
                    "dynamic/budget-packet.json",
                )
            )
            + "\n\n"
        )
        text += (
            "## Documented comparator capabilities (2026-09-06)"
            + COMPARATOR_CAPABILITIES
        )
        REPORT.write_text(text, encoding="utf-8")
    print(f"Validated 45 labeled inputs; manifest SHA-256 {digest(path.read_bytes())}")
    from scripts.phase20_measurements import frozen

    frozen()
    print("Checkpoint 1 freeze validated. This command makes no model requests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
