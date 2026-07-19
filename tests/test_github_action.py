"""Composite GitHub Action adapter and metadata tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from scripts.run_github_action import (
    ActionInputs,
    ActionResult,
    SarifMetrics,
    analyze_sarif,
    emit_action_state,
    execute_action,
    render_step_summary,
    resolve_target,
    sarif_category,
)
from sentinel.config import LlmConfig
from sentinel.finding import Finding, FindingStatus, TokenUsage
from sentinel.llm.semantic_reviewer import MODEL, empty_review_outcome
from sentinel.report.model import (
    GptBatchRecord,
    ScanReport,
    ScanTarget,
    StageName,
    StageRecord,
    StageStatus,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
    summarize,
)
from sentinel.report.sarif import render_sarif
from tests.conftest import NOW, SCAN_ID


def _sarif_payload(finding: Finding | None = None) -> dict[str, object]:
    findings = (finding,) if finding is not None else ()
    selected = (finding.rule_id,) if finding is not None else ("SENT-002",)
    batch = GptBatchRecord(
        batch_id="batch-1",
        request_fingerprint="a" * 64,
        mode="live",
        requested_model=MODEL,
        returned_model=MODEL,
        reasoning_effort=LlmConfig().reasoning_effort,
        finding_count=len(findings),
        retry_count=0,
        status="accepted",
        schema_valid=True,
        current_usage=TokenUsage(
            input_tokens=100,
            output_tokens=20,
            reasoning_tokens=10,
            cached_tokens=5,
            total_tokens=130,
        ),
        origin_usage=TokenUsage(total_tokens=130),
        current_latency_ms=25,
        origin_latency_ms=25,
        confirmed_count=len(findings),
    )
    review = empty_review_outcome(LlmConfig(), mode="live").summary.model_copy(
        update={
            "candidate_count": len(findings),
            "selected_count": len(findings),
            "reviewed_count": len(findings),
            "confirmed_count": len(findings),
            "cache_misses": len(findings),
            "current_usage": batch.current_usage,
            "origin_usage": batch.origin_usage,
            "current_latency_ms": batch.current_latency_ms,
            "origin_latency_ms": batch.origin_latency_ms,
            "batches": (batch,) if findings else (),
        }
    )
    report = ScanReport(
        scan_id=SCAN_ID,
        sentinel_version="0.1.0",
        started_at=NOW,
        completed_at=NOW,
        target=ScanTarget(display_name="action-fixture"),
        analysis_complete=True,
        execution_successful=True,
        stages=tuple(
            StageRecord(name=name, status=StageStatus.SUCCEEDED) for name in StageName
        ),
        summary=summarize(findings),
        warnings=(),
        findings=findings,
        static_analysis=StaticAnalysisSummary(
            selected_rule_ids=selected,
            scanned_file_count=1,
            ignored_file_count=0,
            total_matches=len(findings),
            duration_ms=1,
            rule_outcomes=tuple(
                StaticRuleOutcome(
                    rule_id=rule_id,
                    status=StaticRuleStatus.EVALUATED,
                    match_count=len(findings),
                    exemptions_by_reason={},
                )
                for rule_id in selected
            ),
        ),
        gpt_review=review,
    )
    return cast(dict[str, Any], json.loads(render_sarif(report)))


def _environment(workspace: Path, runner_temp: Path) -> dict[str, str]:
    return {
        "GITHUB_WORKSPACE": str(workspace),
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_RUN_ID": "42",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_ACTION": "sentinel",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REPOSITORY": "BashaarJavaid/demo",
        "SENTINEL_ACTION_OPENAI_API_KEY": "secret-value",
    }


def test_analyze_sarif_counts_all_results_but_excludes_suppressed_severity(
    sample_finding: Finding,
) -> None:
    payload = _sarif_payload(sample_finding)
    metrics = analyze_sarif(payload)
    assert metrics.findings_count == 1
    assert metrics.highest_severity == "high"

    suppressed = sample_finding.model_copy(update={"status": FindingStatus.SUPPRESSED})
    suppressed_metrics = analyze_sarif(_sarif_payload(suppressed))
    assert suppressed_metrics.findings_count == 1
    assert suppressed_metrics.highest_severity == "none"


@pytest.mark.parametrize("scan_exit", [0, 1, 3])
def test_execute_action_validates_and_preserves_report_bearing_exits(
    tmp_path: Path,
    sample_finding: Finding,
    scan_exit: int,
) -> None:
    workspace = tmp_path / "workspace"
    target = workspace / "server"
    target.mkdir(parents=True)
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    environment = _environment(workspace, runner_temp)

    def fake_run(
        command: list[str], *, env: dict[str, str], check: bool
    ) -> subprocess.CompletedProcess[str]:
        assert check is False
        assert env["OPENAI_API_KEY"] == "secret-value"
        assert "--allow-degraded" not in command
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_sarif_payload(sample_finding)), encoding="utf-8")
        return subprocess.CompletedProcess(command, scan_exit)

    result = execute_action(
        ActionInputs("server", "high", "false"),
        environment,
        command_runner=fake_run,
    )
    assert result.effective_exit_code == scan_exit
    assert result.upload_ready is True
    assert result.category == "mcp-sentinel/server"
    assert result.metrics.findings_count == 1
    assert result.metrics.highest_severity == "high"


def test_fork_pull_request_withholds_secret_degrades_and_skips_upload(
    tmp_path: Path, sample_finding: Finding
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {"pull_request": {"head": {"repo": {"full_name": "contributor/demo"}}}}
        ),
        encoding="utf-8",
    )
    environment = {
        **_environment(workspace, runner_temp),
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_EVENT_PATH": str(event_path),
    }

    def fake_run(
        command: list[str], *, env: dict[str, str], check: bool
    ) -> subprocess.CompletedProcess[str]:
        assert check is False
        assert "OPENAI_API_KEY" not in env
        assert "--allow-degraded" in command
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_sarif_payload(sample_finding)), encoding="utf-8")
        return subprocess.CompletedProcess(command, 1)

    result = execute_action(
        ActionInputs(".", "high", "false"),
        environment,
        command_runner=fake_run,
    )
    assert result.fork_pull_request is True
    assert result.upload_ready is False
    assert result.effective_exit_code == 1
    assert result.category == "mcp-sentinel/root"
    assert "credentials were withheld" in render_step_summary(result)


def test_invalid_or_missing_sarif_blocks_upload(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    environment = _environment(workspace, runner_temp)

    def invalid_run(
        command: list[str], *, env: dict[str, str], check: bool
    ) -> subprocess.CompletedProcess[str]:
        del env, check
        output = Path(command[command.index("--output") + 1])
        output.write_text("{}", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    invalid = execute_action(
        ActionInputs(".", "high", "true"),
        environment,
        command_runner=invalid_run,
    )
    assert invalid.effective_exit_code == 3
    assert invalid.upload_ready is False
    assert "validation failed" in (invalid.message or "")

    missing = execute_action(
        ActionInputs(".", "high", "true"),
        environment,
        command_runner=lambda command, **kwargs: subprocess.CompletedProcess(
            command, 2
        ),
    )
    assert missing.effective_exit_code == 2
    assert missing.upload_ready is False


def test_target_must_remain_inside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace / "escape").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        resolve_target(workspace.resolve(), "escape")
    assert sarif_category(Path("services/payments")) == (
        "mcp-sentinel/services/payments"
    )


def test_outputs_and_summary_are_aggregate_only(tmp_path: Path) -> None:
    output = tmp_path / "output"
    summary = tmp_path / "summary"
    result = ActionResult(
        effective_exit_code=0,
        sarif_path=tmp_path / "report.sarif",
        category="mcp-sentinel/root",
        fork_pull_request=False,
        upload_ready=True,
        metrics=SarifMetrics(
            findings_count=2,
            highest_severity="critical",
            analysis_complete=True,
            review={
                "mode": "replay",
                "requested_model": MODEL,
                "candidate_count": 2,
                "reviewed_count": 1,
                "overflow_count": 1,
                "cache_hits": 1,
                "batches": [{"returned_model": MODEL}],
                "current_usage": {"total_tokens": 50},
            },
        ),
    )
    emit_action_state(
        result,
        {"GITHUB_OUTPUT": str(output), "GITHUB_STEP_SUMMARY": str(summary)},
    )
    output_text = output.read_text(encoding="utf-8")
    summary_text = summary.read_text(encoding="utf-8")
    assert "findings-count=2" in output_text
    assert "highest-severity=critical" in output_text
    assert "Mode | replay" in summary_text
    assert "Reviewed / skipped | 1 / 1" in summary_text
    assert "Truncated | yes (1 overflow)" in summary_text
    assert "snippet" not in summary_text


def test_action_metadata_exposes_only_approved_interface() -> None:
    root = Path(__file__).resolve().parents[1]
    metadata = yaml.safe_load((root / "action.yml").read_text(encoding="utf-8"))
    assert set(metadata["inputs"]) == {
        "target-path",
        "fail-on",
        "openai-api-key",
        "static-only",
    }
    assert metadata["inputs"]["target-path"]["default"] == "."
    assert metadata["inputs"]["fail-on"]["default"] == "high"
    assert set(metadata["outputs"]) == {
        "sarif-path",
        "findings-count",
        "highest-severity",
    }
    uses = [step.get("uses", "") for step in metadata["runs"]["steps"]]
    assert any(value.startswith("actions/setup-python@ece7cb06") for value in uses)
    assert any(
        value.startswith("github/codeql-action/upload-sarif@7188fc36") for value in uses
    )
