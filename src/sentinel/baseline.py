"""Bounded baseline loading and deterministic finding matching."""

from __future__ import annotations

import hashlib
import json
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from sentinel.errors import InfrastructureError, UsageError
from sentinel.finding import DynamicEvidence, Finding, StaticEvidence
from sentinel.report.model import (
    BaselineSummary,
    ScanReport,
    StageName,
    StageStatus,
    summarize,
)
from sentinel.report.validate_json import validate_report_data

MAX_BASELINE_BYTES = 10 * 1024 * 1024
MATCHER_VERSION = "sentinel-baseline-v1"


@dataclass(frozen=True)
class LoadedBaseline:
    path: Path
    report: ScanReport
    source_schema_version: Literal["1.3.0", "1.4.0"]
    source_sha256: str
    identities: frozenset[str]


def load_baseline(path: Path) -> LoadedBaseline:
    """Load one strict native 1.3/1.4 report without mutating it."""

    candidate = path if path.is_absolute() else Path.cwd() / path
    try:
        metadata = candidate.lstat()
    except OSError as error:
        raise UsageError(f"cannot stat baseline: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise UsageError("baseline must be a regular non-symlink file")
    if metadata.st_size > MAX_BASELINE_BYTES:
        raise UsageError("baseline exceeds the 10 MiB limit")
    try:
        raw = candidate.read_bytes()
        text = raw.decode("utf-8")
        data = json.loads(text)
    except UnicodeDecodeError as error:
        raise UsageError("baseline is not valid UTF-8") from error
    except json.JSONDecodeError as error:
        raise UsageError(f"baseline is not valid JSON: {error.msg}") from error
    except OSError as error:
        raise UsageError(f"cannot read baseline: {path}") from error
    if not isinstance(data, dict):
        raise UsageError("baseline report must be a JSON object")
    raw_version = data.get("schema_version")
    if raw_version not in {"1.3.0", "1.4.0"}:
        raise UsageError("baseline schema_version must be 1.3.0 or 1.4.0")
    version: Literal["1.3.0", "1.4.0"] = raw_version
    normalized = _migrate_13(data) if version == "1.3.0" else data
    try:
        validate_report_data(normalized)
        report = ScanReport.model_validate_json(_model_input(normalized))
    except InfrastructureError as error:
        raise UsageError(f"baseline report is invalid: {error}") from error
    except ValidationError as error:
        raise UsageError(
            f"baseline report is invalid: {error.errors()[0]['msg']}"
        ) from error
    if not report.analysis_complete or not report.execution_successful:
        raise UsageError("baseline report must be complete and execution-successful")
    if report.static_analysis is None:
        raise UsageError("baseline report must contain a static analysis summary")
    identities = _identity_set(report.findings)
    return LoadedBaseline(
        path=candidate.resolve(),
        report=report,
        source_schema_version=version,
        source_sha256=hashlib.sha256(raw).hexdigest(),
        identities=identities,
    )


def annotate_report(report: ScanReport, baseline: LoadedBaseline) -> ScanReport:
    """Validate compatibility and mark every current finding."""

    _validate_compatibility(report, baseline.report)
    current = tuple((finding, finding_identity(finding)) for finding in report.findings)
    _validate_duplicate_evidence(report.findings)
    findings = tuple(
        finding.model_copy(update={"baseline_matched": identity in baseline.identities})
        for finding, identity in current
    )
    current_identities = {identity for _, identity in current}
    summary = BaselineSummary(
        source_schema_version=baseline.source_schema_version,
        source_sha256=baseline.source_sha256,
        baseline_finding_count=len(baseline.identities),
        matched_finding_count=sum(item.baseline_matched is True for item in findings),
        new_finding_count=sum(item.baseline_matched is False for item in findings),
        resolved_finding_count=len(baseline.identities - current_identities),
    )
    return report.model_copy(
        update={
            "findings": findings,
            "summary": summarize(findings),
            "baseline": summary,
        }
    )


def finding_identity(finding: Finding) -> str:
    evidence = finding.evidence
    if isinstance(evidence, StaticEvidence):
        payload: Any = [finding.dedup_key, evidence.snippet, evidence.fingerprint]
    elif isinstance(evidence, DynamicEvidence):
        payload = [
            finding.dedup_key,
            evidence.probe_id,
            evidence.request,
            evidence.response,
        ]
    else:  # pragma: no cover - discriminated contract is exhaustive
        raise TypeError("unsupported finding evidence")
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _identity_set(findings: tuple[Finding, ...]) -> frozenset[str]:
    _validate_duplicate_evidence(findings)
    return frozenset(finding_identity(finding) for finding in findings)


def _validate_duplicate_evidence(findings: tuple[Finding, ...]) -> None:
    by_dedup: dict[str, str] = {}
    for finding in findings:
        identity = finding_identity(finding)
        previous = by_dedup.setdefault(finding.dedup_key, identity)
        if previous != identity:
            raise UsageError(
                f"findings with dedup key {finding.dedup_key} have conflicting evidence"
            )


def _validate_compatibility(current: ScanReport, previous: ScanReport) -> None:
    if current.static_analysis is None:
        raise UsageError("current report has no static analysis summary")
    if previous.static_analysis is None:  # guarded during baseline loading
        raise UsageError("baseline report has no static analysis summary")
    if (
        current.static_analysis.selected_rule_ids
        != previous.static_analysis.selected_rule_ids
    ):
        raise UsageError("baseline selected rules do not match the current scan")
    if _static_only(current) != _static_only(previous):
        raise UsageError(
            "baseline static-only/full mode does not match the current scan"
        )


def _static_only(report: ScanReport) -> bool:
    dynamic = next(stage for stage in report.stages if stage.name is StageName.DYNAMIC)
    return (
        dynamic.status is StageStatus.SKIPPED
        and dynamic.reason == "static-only scan requested"
    )


def _migrate_13(data: dict[str, Any]) -> dict[str, Any]:
    migrated = dict(data)
    migrated["schema_version"] = "1.4.0"
    migrated["baseline"] = None
    findings = []
    raw_findings = migrated.get("findings")
    if not isinstance(raw_findings, list):
        return migrated
    for raw in raw_findings:
        if not isinstance(raw, dict):
            findings.append(raw)
            continue
        finding = dict(raw)
        finding["baseline_matched"] = None
        finding["suppression"] = None
        findings.append(finding)
    migrated["findings"] = findings
    return migrated


def _model_input(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload["analysis_complete"] = payload.pop("analysisComplete", None)
    payload["execution_successful"] = payload.pop("executionSuccessful", None)
    raw_findings = payload.get("findings")
    if isinstance(raw_findings, list):
        findings = []
        for raw in raw_findings:
            if isinstance(raw, dict):
                finding = dict(raw)
                finding.pop("severity", None)
                findings.append(finding)
            else:
                findings.append(raw)
        payload["findings"] = findings
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
