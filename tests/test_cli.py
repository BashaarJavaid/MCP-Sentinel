"""Public CLI and exit-code tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from click import unstyle
from typer.testing import CliRunner

from sentinel.cli import _use_color, app
from sentinel.config import LoadedConfiguration
from sentinel.errors import InfrastructureError
from sentinel.orchestrator import ScanOutcome, run_phase1_scan
from sentinel.report.model import (
    ScanContext,
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


def test_json_scan_returns_complete_exit_and_clean_stdout(target_root: Path) -> None:
    result = runner.invoke(app, ["scan", str(target_root), "--json", "--static-only"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["analysisComplete"] is True
    assert payload["findings"] == []
    assert result.stderr == ""


def test_conflicting_format_is_usage_error(target_root: Path) -> None:
    result = runner.invoke(
        app, ["scan", str(target_root), "--json", "--format", "sarif"]
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "conflicts" in result.stderr


@pytest.mark.parametrize("flag", ["--verbose", "--color", "--no-color"])
def test_machine_formats_reject_console_presentation_options(
    target_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    flag: str,
) -> None:
    def reject_scan(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("presentation validation must happen before scanning")

    monkeypatch.setattr("sentinel.cli.run_scan", reject_scan)
    result = runner.invoke(
        app,
        ["scan", str(target_root), "--json", flag, "--static-only"],
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "require console output" in result.stderr


def test_color_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert _use_color(None) is False
    assert _use_color(True) is True
    assert _use_color(False) is False


def test_output_atomically_overwrites_named_file(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "report.json"
    output.write_text("old", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--format",
            "json",
            "--output",
            str(output),
            "--static-only",
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == ""
    assert json.loads(output.read_text(encoding="utf-8"))["findings"] == []


def test_invalid_output_parent_is_usage_error(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "missing" / "report.json"
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--format",
            "json",
            "--output",
            str(output),
            "--static-only",
        ],
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "invalid output path" in result.stderr


def test_missing_target_uses_target_error_prefix(tmp_path: Path) -> None:
    result = runner.invoke(app, ["scan", str(tmp_path / "missing")])
    assert result.exit_code == 2
    assert result.stderr.startswith("target error:")


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
            "--static-only",
        ],
    )
    assert result.exit_code == 0
    invalid = runner.invoke(app, ["scan", str(target), "--rules", "SENT-999"])
    assert invalid.exit_code == 2


def test_orphan_reaper_failure_returns_infrastructure_exit(
    target_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_reaper() -> None:
        raise InfrastructureError("cannot list stale Sentinel containers")

    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", fail_reaper)

    result = runner.invoke(app, ["scan", str(target_root)])

    assert result.exit_code == 3
    assert result.stderr.startswith("infrastructure error:")
    assert "cannot list stale Sentinel containers" in result.stderr


def test_demo_validates_and_cleans_temporary_reports(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_run_scan(
        configuration: LoadedConfiguration,
        context: ScanContext,
        *,
        completed_at: datetime,
        **kwargs: object,
    ) -> ScanOutcome:
        del kwargs
        incomplete = run_phase1_scan(
            configuration,
            context,
            completed_at=completed_at,
        )
        return ScanOutcome(report=incomplete.report, exit_code=1)

    monkeypatch.setattr("sentinel.cli.run_scan", fake_run_scan)
    output_dir = tmp_path / "demo-output"
    output_dir.mkdir()
    unrelated = output_dir / "notes.txt"
    unrelated.write_text("keep", encoding="utf-8")
    result = runner.invoke(app, ["demo", "--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert "Validated JSON" in result.stdout
    assert "Validated SARIF" in result.stdout
    assert (output_dir / "report.json").is_file()
    assert (output_dir / "report.sarif").is_file()
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert "incomplete until Phase 3" not in result.stderr


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
