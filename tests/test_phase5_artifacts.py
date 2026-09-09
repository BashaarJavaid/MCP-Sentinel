"""Artifact consumers retain incomplete synthetic campaign measurements."""

import pytest

from scripts import generate_phase5_artifacts as artifacts
from sentinel.dynamic.prober import _Observation
from tests.test_dynamic_reporting import _result


def test_ablation_retains_unstarted_campaign_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = artifacts._cases()[0]
    tool = case["tool"]
    dynamic = _result(
        (
            _Observation(
                "SENT-010", tool, "expression", {}, {}, (), False, attack_attempted=True
            ),
            _Observation(
                "SENT-011", tool, "expression", {}, {}, (), False, status="untested"
            ),
        )
    )
    monkeypatch.setattr(artifacts, "run_dynamic_scan", lambda *args, **kwargs: dynamic)
    record = artifacts._run_dynamic_case(case)
    assert record["analysis_complete"] is False
    assert record["dynamic_analysis"] == dynamic.summary.model_dump(mode="json")
    coverage = record["dynamic_analysis"]["coverage"]["campaign"]
    assert coverage["started_attempts"] == 1
    assert coverage["remaining_eligible_attempts"] == 1
