"""Canonical Finding contract tests."""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from sentinel.finding import (
    DynamicEvidence,
    Exploitability,
    FileLocation,
    Finding,
    FindingStatus,
    Impact,
    LogicalLocation,
    ReviewStatus,
    Severity,
    SourceRange,
    calculate_severity,
    make_dedup_key,
    transition_status,
)
from tests.conftest import NOW


@pytest.mark.parametrize(
    ("impact", "confirmed", "theoretical"),
    (
        (Impact.CRITICAL, Severity.CRITICAL, Severity.HIGH),
        (Impact.HIGH, Severity.HIGH, Severity.MEDIUM),
        (Impact.MEDIUM, Severity.MEDIUM, Severity.LOW),
        (Impact.LOW, Severity.LOW, Severity.INFORMATIONAL),
        (Impact.INFORMATIONAL, Severity.INFORMATIONAL, Severity.INFORMATIONAL),
    ),
)
def test_severity_rubric(
    impact: Impact, confirmed: Severity, theoretical: Severity
) -> None:
    assert calculate_severity(impact, Exploitability.CONFIRMED) is confirmed
    assert calculate_severity(impact, Exploitability.LIKELY) is confirmed
    assert calculate_severity(impact, Exploitability.THEORETICAL) is theoretical


def test_finding_serializes_computed_severity_and_utc(sample_finding: Finding) -> None:
    payload = sample_finding.model_dump(mode="json")
    assert payload["severity"] == "High"
    assert payload["timestamp"] == "2026-07-17T12:00:00.123456Z"
    assert payload["review"]["mode"] == "not_reviewed"
    assert "reason" in payload["review"] and payload["review"]["reason"] is None


def test_dedup_key_is_canonical_sha256() -> None:
    parts = ("SENT-001", "server.py", "1:1")
    expected = hashlib.sha256(
        json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    assert make_dedup_key(parts) == expected


def test_location_normalization_and_range_validation() -> None:
    source_range = SourceRange(start_line=1, start_column=1, end_line=1, end_column=2)
    assert FileLocation(path="./tools\\server.py", range=source_range).path == (
        "tools/server.py"
    )
    assert LogicalLocation(path="/tools/search/inputSchema").path.startswith("/")
    with pytest.raises(ValidationError):
        FileLocation(path="../secret", range=source_range)
    with pytest.raises(ValidationError):
        LogicalLocation(path="tools/search")
    with pytest.raises(ValidationError):
        SourceRange(start_line=1, start_column=2, end_line=1, end_column=2)


def test_dynamic_evidence_rejects_non_json_payloads() -> None:
    payload: dict[str, Any] = {
        "probe_id": "SENT-010",
        "request": {"payload": object()},
        "response": {},
    }
    with pytest.raises(ValidationError):
        DynamicEvidence.model_validate(payload)


def test_status_transitions_are_immutable_and_audited(sample_finding: Finding) -> None:
    confirmed = transition_status(
        sample_finding, FindingStatus.CONFIRMED, at=NOW + timedelta(seconds=1)
    )
    assert sample_finding.status is FindingStatus.NEEDS_REVIEW
    assert confirmed.status is FindingStatus.CONFIRMED
    assert confirmed.review.status is ReviewStatus.CONFIRMED
    assert confirmed.timestamp == NOW + timedelta(seconds=1)

    with pytest.raises(ValueError, match="requires"):
        transition_status(
            confirmed, FindingStatus.NEEDS_REVIEW, at=NOW + timedelta(seconds=2)
        )
    reopened = transition_status(
        confirmed,
        FindingStatus.NEEDS_REVIEW,
        at=NOW + timedelta(seconds=2),
        reason="New review event",
    )
    assert reopened.review.reason == "New review event"
    assert transition_status(reopened, reopened.status, at=NOW) is reopened


def test_suppression_requires_reason_and_disallowed_transition_fails(
    sample_finding: Finding,
) -> None:
    with pytest.raises(ValueError, match="requires"):
        transition_status(sample_finding, FindingStatus.SUPPRESSED, at=NOW)
    suppressed = transition_status(
        sample_finding,
        FindingStatus.SUPPRESSED,
        at=NOW + timedelta(seconds=1),
        reason="Accepted risk",
    )
    assert suppressed.review.reason == "Accepted risk"
    with pytest.raises(ValueError, match="disallowed"):
        transition_status(suppressed, FindingStatus.CONFIRMED, at=NOW)


def test_finding_rejects_non_uuid4_and_mismatched_provenance(
    sample_finding: Finding,
) -> None:
    data = sample_finding.model_dump(mode="python", exclude={"severity"})
    data["finding_id"] = UUID(int=sample_finding.finding_id.int, version=1)
    with pytest.raises(ValidationError, match="UUIDv4"):
        Finding.model_validate(data)

    data = sample_finding.model_dump(mode="python", exclude={"severity"})
    provenance = data["provenance"][0]
    provenance["rule_id"] = "SENT-001"
    with pytest.raises(ValidationError, match="origin"):
        Finding.model_validate(data)
