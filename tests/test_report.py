"""Native report, schema, and console behavior tests."""

from __future__ import annotations

import json
from pathlib import Path

from sentinel import __version__
from sentinel.config import LoadedConfiguration
from sentinel.orchestrator import run_phase0_scan
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import ScanContext, ScanTarget, StageName, StageStatus
from sentinel.report.validate_json import validate_report_data
from sentinel.schema import check, generate
from tests.conftest import NOW, SCAN_ID


def test_phase0_report_is_explicitly_incomplete(
    loaded_config: LoadedConfiguration,
) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    outcome = run_phase0_scan(loaded_config, context, completed_at=NOW)
    assert outcome.exit_code == 3
    assert outcome.report.analysis_complete is False
    assert outcome.report.execution_successful is False
    assert outcome.report.summary.total == 0
    assert set(outcome.report.summary.by_severity.values()) == {0}
    assert set(outcome.report.summary.by_status.values()) == {0}
    assert len(outcome.report.stages) == len(StageName)
    assert outcome.report.stages[-1].status is StageStatus.SUCCEEDED

    json_text = render_json(outcome.report)
    assert json_text.endswith("\n")
    payload = json.loads(json_text)
    assert payload["analysisComplete"] is False
    assert payload["executionSuccessful"] is False
    assert payload["sentinel_version"] == __version__
    validate_report_data(payload)


def test_console_reports_semantic_state(loaded_config: LoadedConfiguration) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    report = run_phase0_scan(loaded_config, context, completed_at=NOW).report
    console = render_console(report)
    assert "MCP Sentinel 0.1.0" in console
    assert "Target: fixture" in console
    assert "Status: INCOMPLETE" in console
    assert "Findings: 0" in console
    assert "static: skipped" in console
    assert "reporting: succeeded" in console


def test_schema_generate_and_drift_check(tmp_path: Path) -> None:
    schema_dir = tmp_path / "schemas"
    generate(schema_dir)
    assert check(schema_dir) == []
    report_path = schema_dir / "report.schema.json"
    report_schema = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_schema["$schema"].endswith("2020-12/schema")
    assert "finding.schema.json" in report_path.read_text(encoding="utf-8")
    report_path.write_text("{}\n", encoding="utf-8")
    assert check(schema_dir) == ["report.schema.json"]
