"""Native report, schema, and console behavior tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinel import __version__
from sentinel.config import LoadedConfiguration, load_configuration
from sentinel.finding import Exploitability, Finding, FindingStatus
from sentinel.orchestrator import run_phase1_scan, run_scan
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import (
    ScanContext,
    ScanTarget,
    StageName,
    StageStatus,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
    summarize,
)
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.schema import check, generate
from sentinel.static.model import StaticScanResult
from tests.conftest import NOW, SCAN_ID
from tests.test_gpt_review import FakeTransport, _sent002_findings


def test_phase1_report_has_static_results_and_is_explicitly_incomplete(
    loaded_config: LoadedConfiguration,
) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    outcome = run_phase1_scan(loaded_config, context, completed_at=NOW)
    assert outcome.exit_code == 3
    assert outcome.report.analysis_complete is False
    assert outcome.report.execution_successful is False
    assert outcome.report.summary.total == 0
    assert set(outcome.report.summary.by_severity.values()) == {0}
    assert set(outcome.report.summary.by_status.values()) == {0}
    assert len(outcome.report.stages) == len(StageName)
    assert outcome.report.stages[0].status is StageStatus.SUCCEEDED
    assert outcome.report.stages[-1].status is StageStatus.SUCCEEDED
    assert outcome.report.static_analysis is not None
    assert len(outcome.report.static_analysis.rule_outcomes) == 7

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
    report = run_phase1_scan(loaded_config, context, completed_at=NOW).report
    console = render_console(report)
    assert "MCP Sentinel 0.1.0" in console
    assert "Target: fixture" in console
    assert "Status: INCOMPLETE" in console
    assert "Findings: 0" in console
    assert "static: succeeded" in console
    assert "reporting: succeeded" in console


def test_console_orders_by_severity_then_suppression_and_bounds_detail(
    loaded_config: LoadedConfiguration,
    sample_finding: Finding,
) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    base = run_phase1_scan(loaded_config, context, completed_at=NOW).report
    confirmed = sample_finding.model_copy(
        update={
            "title": "Confirmed high",
            "status": FindingStatus.CONFIRMED,
            "exploitability": Exploitability.CONFIRMED,
        }
    )
    suppressed = sample_finding.model_copy(
        update={
            "title": "Suppressed high",
            "status": FindingStatus.SUPPRESSED,
            "exploitability": Exploitability.CONFIRMED,
        }
    )
    lower = sample_finding.model_copy(
        update={
            "title": "Needs-review high",
            "exploitability": Exploitability.CONFIRMED,
        }
    )
    findings = (suppressed, lower, confirmed)
    report = base.model_copy(
        update={"findings": findings, "summary": summarize(findings)}
    )

    concise = render_console(report, color=True)
    assert "\x1b[" in concise
    assert concise.index("Confirmed high") < concise.index("Suppressed high")
    assert concise.index("Needs-review high") < concise.index("Suppressed high")
    assert "Description:" not in concise

    verbose = render_console(report, verbose=True)
    assert "Description: Raw tool input reaches eval." in verbose
    assert "Evidence: eval(value)" in verbose
    assert "Provenance: static:SENT-002" in verbose


def test_schema_generate_and_drift_check(tmp_path: Path) -> None:
    schema_dir = tmp_path / "schemas"
    generate(schema_dir)
    assert check(schema_dir) == []
    report_path = schema_dir / "report.schema.json"
    report_schema = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_schema["$schema"].endswith("2020-12/schema")
    assert "finding.schema.json" in report_path.read_text(encoding="utf-8")
    review_schema = json.loads(
        (schema_dir / "gpt-review.schema.json").read_text(encoding="utf-8")
    )
    assert review_schema["$id"] == "mcp_sentinel_review_v2"
    report_path.write_text("{}\n", encoding="utf-8")
    assert check(schema_dir) == ["report.schema.json"]


def test_completed_gpt_review_survives_console_json_and_sarif(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).parent / "fixtures" / "gpt_review_eval"
    configuration = load_configuration(
        root,
        environ={},
        cli_overrides={"rules": ("SENT-002",)},
        static_only=True,
    )
    configuration = configuration.model_copy(
        update={
            "scanner": configuration.scanner.model_copy(
                update={
                    "llm": configuration.scanner.llm.model_copy(
                        update={"cache_enabled": False}
                    )
                }
            )
        }
    )
    context = ScanContext(
        scan_id=SCAN_ID,
        started_at=NOW,
        target=ScanTarget(display_name="gpt_review_eval"),
    )
    finding = _sent002_findings()[0].model_copy(update={"scan_id": SCAN_ID})
    static_result = StaticScanResult(
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

    def fake_static_scan(*args: object, **kwargs: object) -> StaticScanResult:
        del args, kwargs
        return static_result

    monkeypatch.setattr("sentinel.orchestrator.run_static_scan", fake_static_scan)
    report = run_scan(
        configuration,
        context,
        completed_at=NOW,
        allow_degraded=False,
        transport=FakeTransport(),
    ).report
    assert report.analysis_complete is True
    assert report.gpt_review is not None
    assert "GPT review: LIVE" in render_console(report)
    native = json.loads(render_json(report))
    validate_report_data(native)
    assert native["findings"][0]["review"]["reasoning"].startswith("Direct")

    sarif = json.loads(render_sarif(report))
    validate_sarif_data(sarif)
    review = sarif["runs"][0]["results"][0]["properties"]["review"]
    assert review["mode"] == "live"
    assert review["suggested_severity_override"] is None
