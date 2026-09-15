"""Attempt identities and legacy coverage survive the native report migration."""

import copy

import pytest
from pydantic import ValidationError

from sentinel.baseline import finding_identity, migrate_report_data
from sentinel.dynamic.prober import DEFAULT_ORDER, _Observation
from sentinel.report.json_report import report_model_input
from sentinel.report.model import (
    DynamicAnalysisSummary,
    DynamicProbeOutcome,
    ScanReport,
)
from sentinel.report.validate_json import validate_report_data
from tests.test_baseline import _report
from tests.test_dynamic_reporting import _proof, _result


def test_multiple_mutations_require_unique_attempt_ids() -> None:
    first = DynamicProbeOutcome(
        attempt_id="SENT-011:tool:value:wrong-type",
        probe_id="SENT-011",
        mutation="wrong_type",
        eligible=True,
        status="untested",
        verdict=None,
        tool="tool",
        field="value",
        argument_path=("value",),
        reason="budget exhausted",
    )
    second = first.model_copy(
        update={"attempt_id": "SENT-011:tool:value:omit", "mutation": "omit"}
    )
    assert (
        len(DynamicAnalysisSummary(probe_outcomes=(first, second)).probe_outcomes) == 2
    )
    with pytest.raises(ValidationError, match="unique attempt"):
        DynamicAnalysisSummary(probe_outcomes=(first, first))


@pytest.mark.parametrize("version", ["1.5.0", "1.6.0"])
def test_legacy_attempts_preserve_findings_without_invented_coverage(
    version: str,
) -> None:
    finding = _proof()
    payload = _report((finding,)).model_dump(mode="json", by_alias=True)
    payload.update(
        schema_version=version,
        analysisComplete=False,
        dynamic_analysis=_result(
            tuple(
                _Observation(rule, "legacy-tool", None, {}, {}, (), False)
                for rule in DEFAULT_ORDER
            )
        ).summary.model_dump(mode="json"),
    )
    payload["dynamic_analysis"]["coverage"]["campaign"] = None
    for outcome in payload["dynamic_analysis"]["probe_outcomes"]:
        for key in ("attempt_id", "legacy_attempt", "mutation", "eligible", "started"):
            outcome.pop(key)
    original = copy.deepcopy(payload)
    migrated = migrate_report_data(payload)
    assert payload == original
    validate_report_data(migrated)
    outcomes = migrated["dynamic_analysis"]["probe_outcomes"]
    assert len({item["attempt_id"] for item in outcomes}) == 4
    assert all(
        item["legacy_attempt"] and item["eligible"] is None and item["mutation"] is None
        for item in outcomes
    )
    coverage = migrated["dynamic_analysis"]["coverage"]
    assert coverage is None or coverage["campaign"] is None
    assert migrated["findings"] == original["findings"]
    assert finding_identity(finding) == finding_identity(
        ScanReport.model_validate_json(report_model_input(migrated)).findings[0]
    )


@pytest.mark.parametrize(
    "change",
    [
        "started_total",
        "binding_reference",
        "discovery_reference",
        "tested_without_start",
    ],
)
def test_campaign_records_enforce_references_and_execution_counts(change: str) -> None:
    from sentinel.dynamic.prober import _Observation
    from sentinel.report.coverage import DiscoverySnapshot

    report = _result(
        (_Observation("SENT-011", "tool", "value", {}, {}, (), False),)
    ).summary
    payload = report.model_dump(mode="json")
    if change == "started_total":
        payload["coverage"]["campaign"].update(
            started_attempts=0, tested_attempts=0, remaining_eligible_attempts=1
        )
    elif change == "binding_reference":
        payload["coverage"]["planned_bindings"][0]["attempt_id"] = "wrong"
    elif change == "discovery_reference":
        payload["coverage"]["discovery"] = [
            DiscoverySnapshot(
                probe_id="SENT-011",
                role="baseline",
                attempt_id="wrong",
                tools=(),
                more_pages=False,
                tool_total=0,
            ).model_dump(mode="json")
        ]
    else:
        payload["probe_outcomes"][0]["started"] = False
    with pytest.raises(ValidationError):
        DynamicAnalysisSummary.model_validate_json(__import__("json").dumps(payload))


@pytest.mark.parametrize(
    "change", ["duplicate", "unknown_included_counts", "surface_count", "file_count"]
)
def test_workspace_coverage_cannot_invent_counts(change: str) -> None:
    import json

    from sentinel.report.coverage import (
        StaticCoverage,
        WorkspaceCoverage,
        WorkspaceMemberCoverage,
    )
    from sentinel.report.model import StaticAnalysisSummary

    member = WorkspaceMemberCoverage(
        path=".",
        status="included",
        python_file_count=1,
        typescript_file_count=0,
        recognized_surface_count=0,
        unresolved_surface_count=0,
        unsupported_surface_count=0,
    )
    coverage = StaticCoverage(
        surfaces=(),
        excluded_rule_ids=(),
        file_wide_rule_ids=(),
        workspace=WorkspaceCoverage(
            declarations=("pyproject.toml",), members=(member,)
        ),
    )
    summary = StaticAnalysisSummary(
        coverage=coverage,
        selected_rule_ids=(),
        scanned_file_count=1,
        ignored_file_count=0,
        total_matches=0,
        duration_ms=0,
        rule_outcomes=(),
    )
    payload = summary.model_dump(mode="json")
    members = payload["coverage"]["workspace"]["members"]
    if change == "duplicate":
        members.append(dict(members[0]))
    elif change == "unknown_included_counts":
        members[0]["python_file_count"] = None
    elif change == "surface_count":
        members[0]["recognized_surface_count"] = 1
    else:
        members[0]["python_file_count"] = 2
    with pytest.raises(ValidationError):
        StaticAnalysisSummary.model_validate_json(json.dumps(payload))


def test_native_json_validation_checks_campaign_arithmetic() -> None:
    from sentinel.errors import InfrastructureError
    from tests.test_dynamic_reporting import _result

    dynamic = _result((_Observation("SENT-011", "tool", "value", {}, {}, (), False),))
    payload = _report(()).model_dump(mode="json", by_alias=True)
    payload["dynamic_analysis"] = dynamic.summary.model_dump(mode="json")
    payload["dynamic_analysis"]["coverage"]["campaign"]["started_attempts"] = 0
    with pytest.raises(InfrastructureError):
        validate_report_data(payload)


def test_empty_unknown_discovery_cannot_claim_completion() -> None:
    payload = _report(()).model_dump(mode="json", by_alias=True)
    payload["dynamic_analysis"] = {"coverage": None, "probe_outcomes": []}
    payload["analysisComplete"] = True
    with pytest.raises(ValidationError, match="discovery"):
        ScanReport.model_validate_json(report_model_input(payload))


@pytest.mark.parametrize("change", ["attempt", "mutation", "tool", "verdict"])
def test_runtime_proof_references_matching_observed_attempt(change: str) -> None:
    dynamic = _result((_Observation("SENT-011", "tool", "value", {}, {}, (), True),))
    payload = _report(dynamic.findings).model_dump(mode="json", by_alias=True)
    payload["dynamic_analysis"] = dynamic.summary.model_dump(mode="json")
    outcome = payload["dynamic_analysis"]["probe_outcomes"][0]
    finding = payload["findings"][0]
    evidence = [
        finding["evidence"],
        *(item["evidence"] for item in finding["provenance"]),
    ]
    if change == "verdict":
        outcome["verdict"] = "no_violation_observed"
    else:
        for item in evidence:
            if change == "tool":
                item["proof"]["tool"] = "different"
            else:
                item["attempt_id" if change == "attempt" else "mutation"] = "different"
    with pytest.raises(ValidationError):
        ScanReport.model_validate_json(report_model_input(payload))
