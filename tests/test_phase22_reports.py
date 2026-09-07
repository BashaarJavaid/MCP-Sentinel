"""Attempt identities and legacy coverage survive the native report migration."""

import copy

import pytest
from pydantic import ValidationError

from sentinel.baseline import _model_input, finding_identity, migrate_report_data
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
        dynamic_analysis=_result(()).summary.model_dump(mode="json"),
    )
    for outcome in payload["dynamic_analysis"]["probe_outcomes"]:
        for key in ("attempt_id", "legacy_attempt", "mutation", "eligible"):
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
        ScanReport.model_validate_json(_model_input(migrated)).findings[0]
    )
