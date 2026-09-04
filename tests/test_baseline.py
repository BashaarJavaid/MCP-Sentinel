"""Incremental baseline contract and matcher tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinel.baseline import annotate_report, finding_identity, load_baseline
from sentinel.errors import UsageError
from sentinel.finding import Finding, StaticEvidence, make_dedup_key
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import (
    ScanReport,
    ScanTarget,
    StageName,
    StageRecord,
    StageStatus,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
    summarize,
)
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_sarif import validate_sarif_data
from tests.conftest import NOW, SCAN_ID


def _report(findings: tuple[Finding, ...], *, complete: bool = True) -> ScanReport:
    later = "static-only scan requested"
    stages = tuple(
        StageRecord(
            name=name,
            status=(
                StageStatus.SKIPPED
                if name in {StageName.DYNAMIC, StageName.GPT_DYNAMIC}
                else StageStatus.SUCCEEDED
            ),
            reason=later
            if name in {StageName.DYNAMIC, StageName.GPT_DYNAMIC}
            else None,
        )
        for name in StageName
    )
    return ScanReport(
        scan_id=SCAN_ID,
        sentinel_version="9.9.9",
        started_at=NOW,
        completed_at=NOW,
        target=ScanTarget(display_name="any-name"),
        analysis_complete=complete,
        execution_successful=complete,
        stages=stages,
        summary=summarize(findings),
        warnings=(),
        findings=findings,
        static_analysis=StaticAnalysisSummary(
            selected_rule_ids=("SENT-002",),
            scanned_file_count=1,
            ignored_file_count=0,
            total_matches=len(findings),
            duration_ms=1,
            rule_outcomes=(
                StaticRuleOutcome(
                    rule_id="SENT-002",
                    status=StaticRuleStatus.EVALUATED,
                    match_count=len(findings),
                    exemptions_by_reason={},
                ),
            ),
        ),
        gpt_review=None,
    )


def _write(path: Path, report: ScanReport, *, version: str = "1.4.0") -> None:
    payload = json.loads(render_json(report))
    if version == "1.3.0":
        payload["schema_version"] = version
        payload.pop("baseline")
        for finding in payload["findings"]:
            finding.pop("baseline_matched")
            finding.pop("suppression")
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.mark.parametrize("version", ("1.3.0", "1.4.0"))
def test_load_and_annotate_baseline(
    tmp_path: Path, sample_finding: Finding, version: str
) -> None:
    path = tmp_path / "baseline.json"
    _write(path, _report((sample_finding,)), version=version)
    baseline = load_baseline(path)

    assert isinstance(sample_finding.evidence, StaticEvidence)
    changed = sample_finding.model_copy(
        update={
            "dedup_key": make_dedup_key(("SENT-002", "server.py", "5:2")),
            "evidence": StaticEvidence(
                snippet="eval(other)", range=sample_finding.evidence.range
            ),
        }
    )
    current = _report((sample_finding, changed))
    annotated = annotate_report(current, baseline)

    assert [item.baseline_matched for item in annotated.findings] == [True, False]
    assert annotated.baseline is not None
    assert annotated.baseline.source_schema_version == version
    assert annotated.baseline.baseline_finding_count == 1
    assert annotated.baseline.matched_finding_count == 1
    assert annotated.baseline.new_finding_count == 1
    assert annotated.baseline.resolved_finding_count == 0
    assert finding_identity(sample_finding) != finding_identity(changed)
    assert "matched 1, new 1, resolved 0" in render_console(annotated)
    native = json.loads(render_json(annotated))
    assert native["findings"][0]["baseline_matched"] is True
    sarif = json.loads(render_sarif(annotated))
    validate_sarif_data(sarif)
    assert sarif["runs"][0]["results"][0]["baselineState"] == "unchanged"
    assert sarif["runs"][0]["results"][1]["baselineState"] == "new"
    assert (
        sarif["runs"][0]["invocations"][0]["properties"]["baseline"]
        == native["baseline"]
    )


def test_resolved_and_exact_duplicate_counts(
    tmp_path: Path, sample_finding: Finding
) -> None:
    duplicate = sample_finding.model_copy(
        update={"finding_id": sample_finding.finding_id}
    )
    path = tmp_path / "baseline.json"
    _write(path, _report((sample_finding, duplicate)))
    annotated = annotate_report(_report(()), load_baseline(path))
    assert annotated.findings == ()
    assert annotated.baseline is not None
    assert annotated.baseline.baseline_finding_count == 1
    assert annotated.baseline.resolved_finding_count == 1


def test_baseline_rejects_incomplete_and_conflicting_duplicates(
    tmp_path: Path, sample_finding: Finding
) -> None:
    incomplete = tmp_path / "incomplete.json"
    _write(incomplete, _report((), complete=False))
    with pytest.raises(UsageError, match="complete"):
        load_baseline(incomplete)

    assert isinstance(sample_finding.evidence, StaticEvidence)
    changed = sample_finding.model_copy(
        update={
            "evidence": StaticEvidence(
                snippet="eval(other)", range=sample_finding.evidence.range
            )
        }
    )
    conflict = tmp_path / "conflict.json"
    _write(conflict, _report((sample_finding, changed)))
    with pytest.raises(UsageError, match="conflicting evidence"):
        load_baseline(conflict)


def test_baseline_rejects_symlink_and_oversize(
    tmp_path: Path, sample_finding: Finding
) -> None:
    path = tmp_path / "baseline.json"
    _write(path, _report((sample_finding,)))
    link = tmp_path / "link.json"
    link.symlink_to(path)
    with pytest.raises(UsageError, match="non-symlink"):
        load_baseline(link)

    large = tmp_path / "large.json"
    large.write_bytes(b" " * (10 * 1024 * 1024 + 1))
    with pytest.raises(UsageError, match="10 MiB"):
        load_baseline(large)


def test_relative_baseline_and_incomplete_current_annotation(
    tmp_path: Path,
    sample_finding: Finding,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "baseline.json"
    _write(path, _report((sample_finding,)))
    monkeypatch.chdir(tmp_path)
    baseline = load_baseline(Path("baseline.json"))
    annotated = annotate_report(_report((sample_finding,), complete=False), baseline)
    assert annotated.analysis_complete is False
    assert annotated.findings[0].baseline_matched is True


def test_baseline_rejects_rule_and_mode_mismatch(
    tmp_path: Path, sample_finding: Finding
) -> None:
    path = tmp_path / "baseline.json"
    _write(path, _report((sample_finding,)))
    baseline = load_baseline(path)
    current = _report((sample_finding,))
    static = current.static_analysis
    assert static is not None
    other_rules = static.model_copy(
        update={
            "selected_rule_ids": ("SENT-003",),
            "rule_outcomes": (
                static.rule_outcomes[0].model_copy(update={"rule_id": "SENT-003"}),
            ),
        }
    )
    with pytest.raises(UsageError, match="selected rules"):
        annotate_report(
            current.model_copy(update={"static_analysis": other_rules}), baseline
        )

    full_stages = tuple(
        stage.model_copy(update={"status": StageStatus.SUCCEEDED, "reason": None})
        if stage.name is StageName.DYNAMIC
        else stage
        for stage in current.stages
    )
    with pytest.raises(UsageError, match="mode"):
        annotate_report(current.model_copy(update={"stages": full_stages}), baseline)
