"""SARIF object construction and offline validation tests."""

from __future__ import annotations

import json

import pytest

from sentinel.config import LoadedConfiguration
from sentinel.errors import InfrastructureError
from sentinel.finding import Finding, FindingStatus
from sentinel.orchestrator import run_phase1_scan
from sentinel.report.model import ScanContext, ScanTarget
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_sarif import validate_sarif_data
from tests.conftest import NOW, SCAN_ID


def test_sarif_shell_validates_and_preserves_failure_state(
    loaded_config: LoadedConfiguration,
) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    report = run_phase1_scan(loaded_config, context, completed_at=NOW).report
    text = render_sarif(report)
    payload = json.loads(text)
    validate_sarif_data(payload)

    assert payload["version"] == "2.1.0"
    run = payload["runs"][0]
    assert run["tool"]["driver"]["name"] == "MCP Sentinel"
    assert [item["id"] for item in run["tool"]["driver"]["rules"]] == [
        f"SENT-{number:03d}" for number in range(1, 8)
    ]
    assert run["results"] == []
    assert run["originalUriBaseIds"]["SRCROOT"]["uri"] == "./"
    invocation = run["invocations"][0]
    assert invocation["executionSuccessful"] is False
    assert invocation["exitCode"] == 3
    assert "arguments" not in invocation and "commandLine" not in invocation
    assert invocation["toolExecutionNotifications"][0]["level"] == "error"
    assert "/Users/" not in text


def test_invalid_sarif_is_an_infrastructure_failure() -> None:
    with pytest.raises(InfrastructureError, match="SARIF schema"):
        validate_sarif_data({"version": "2.1.0", "runs": "not-an-array"})


def test_suppressed_result_uses_schema_valid_native_suppression(
    loaded_config: LoadedConfiguration,
    sample_finding: Finding,
) -> None:
    context = ScanContext(
        scan_id=SCAN_ID, started_at=NOW, target=ScanTarget(display_name="fixture")
    )
    report = run_phase1_scan(loaded_config, context, completed_at=NOW).report
    finding = sample_finding.model_copy(update={"status": FindingStatus.SUPPRESSED})
    report = report.model_copy(
        update={
            "findings": (finding,),
            "summary": report.summary.model_copy(
                update={
                    "total": 1,
                    "by_severity": {
                        **report.summary.by_severity,
                        finding.severity: 1,
                    },
                    "by_status": {
                        **report.summary.by_status,
                        FindingStatus.SUPPRESSED: 1,
                    },
                }
            ),
        }
    )
    payload = json.loads(render_sarif(report))
    validate_sarif_data(payload)
    suppression = payload["runs"][0]["results"][0]["suppressions"][0]
    assert suppression["status"] == "accepted"
    assert "state" not in suppression
