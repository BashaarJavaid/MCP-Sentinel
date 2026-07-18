"""Public CLI and exit-code tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from click import unstyle
from typer.testing import CliRunner

from sentinel.cli import app
from sentinel.config import LoadedConfiguration
from sentinel.report.model import (
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
)
from sentinel.static.model import StaticScanResult
from tests.conftest import make_target
from tests.test_gpt_review import _sent002_findings

runner = CliRunner()


def test_version_and_help() -> None:
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert version.stdout.strip() == "0.1.0"
    help_result = runner.invoke(app, ["scan", "--help"])
    assert help_result.exit_code == 0
    assert "--static-only" in unstyle(help_result.stdout)


def test_json_scan_returns_incomplete_exit_and_clean_stdout(target_root: Path) -> None:
    result = runner.invoke(app, ["scan", str(target_root), "--json"])
    assert result.exit_code == 3
    payload = json.loads(result.stdout)
    assert payload["analysisComplete"] is False
    assert payload["findings"] == []
    assert "analysis incomplete" in result.stderr


def test_conflicting_format_is_usage_error(target_root: Path) -> None:
    result = runner.invoke(
        app, ["scan", str(target_root), "--json", "--format", "sarif"]
    )
    assert result.exit_code == 2
    assert "conflicts" in result.stderr


def test_output_atomically_overwrites_named_file(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "report.json"
    output.write_text("old", encoding="utf-8")
    result = runner.invoke(
        app,
        ["scan", str(target_root), "--format", "json", "--output", str(output)],
    )
    assert result.exit_code == 3
    assert result.stdout == ""
    assert json.loads(output.read_text(encoding="utf-8"))["findings"] == []


def test_invalid_output_parent_is_usage_error(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "missing" / "report.json"
    result = runner.invoke(
        app,
        ["scan", str(target_root), "--format", "json", "--output", str(output)],
    )
    assert result.exit_code == 2
    assert "invalid output path" in result.stderr


def test_static_only_skips_target_launch_and_completes_when_clean(
    tmp_path: Path,
) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    result = runner.invoke(app, ["scan", str(target), "--static-only"])
    assert result.exit_code == 0
    assert "Status: COMPLETE" in result.stdout


def test_static_only_gpt_failure_is_fatal_or_explicitly_degraded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fake_static_scan(
        configuration: LoadedConfiguration,
        scan_id: UUID,
        *,
        timestamp: datetime,
    ) -> StaticScanResult:
        del configuration
        finding = _sent002_findings()[0].model_copy(
            update={"scan_id": scan_id, "timestamp": timestamp}
        )
        return StaticScanResult(
            findings=(finding,),
            warnings=(),
            summary=StaticAnalysisSummary(
                selected_rule_ids=("SENT-002",),
                scanned_file_count=1,
                ignored_file_count=0,
                total_matches=1,
                duration_ms=1,
                rule_outcomes=(
                    StaticRuleOutcome(
                        rule_id="SENT-002",
                        status=StaticRuleStatus.EVALUATED,
                        match_count=1,
                        exemptions_by_reason={},
                    ),
                ),
            ),
        )

    monkeypatch.setattr("sentinel.orchestrator.run_static_scan", fake_static_scan)
    target = Path(__file__).parent / "fixtures" / "vulnerable_server"
    base = ["scan", str(target), "--static-only", "--rules", "SENT-002", "--json"]

    fatal = runner.invoke(app, base)
    assert fatal.exit_code == 3
    fatal_payload = json.loads(fatal.stdout)
    assert fatal_payload["analysisComplete"] is False
    assert fatal_payload["gpt_review"]["failure_count"] == 1
    assert fatal_payload["findings"][0]["review"]["mode"] == "not_reviewed"

    degraded = runner.invoke(app, [*base, "--allow-degraded"])
    assert degraded.exit_code == 1
    degraded_payload = json.loads(degraded.stdout)
    assert degraded_payload["analysisComplete"] is True
    assert degraded_payload["gpt_review"]["mode"] == "degraded"
    review = degraded_payload["findings"][0]["review"]
    assert review["mode"] == "degraded"
    assert review["reviewed_at"] is None
    assert review["applied_at"] is not None


def test_launch_override_and_rule_validation(tmp_path: Path) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    result = runner.invoke(
        app,
        [
            "scan",
            str(target),
            "--target-launch-cmd",
            "python server.py",
            "--rules",
            "SENT-001,-SENT-007",
        ],
    )
    assert result.exit_code == 3
    invalid = runner.invoke(app, ["scan", str(target), "--rules", "SENT-999"])
    assert invalid.exit_code == 2


def test_demo_validates_and_cleans_temporary_reports() -> None:
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 3
    assert "Validated temporary JSON" in result.stdout
    assert "Validated temporary SARIF" in result.stdout
    assert "Temporary demo reports cleaned up" in result.stdout
    assert "incomplete until Phase 3" in result.stderr


def test_debug_controls_internal_tracebacks(
    target_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_load(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError("synthetic internal failure")

    monkeypatch.setattr("sentinel.cli.load_configuration", fail_load)
    concise = runner.invoke(app, ["scan", str(target_root)])
    assert concise.exit_code == 3
    assert "internal Sentinel failure" in concise.stderr
    assert "Traceback" not in concise.stderr

    debug = runner.invoke(app, ["--debug", "scan", str(target_root)])
    assert debug.exit_code == 3
    assert "Traceback" in debug.stderr
    assert "synthetic internal failure" in debug.stderr
