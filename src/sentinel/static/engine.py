"""Deterministic Phase 1 static-analysis engine."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from sentinel.config import LoadedConfiguration
from sentinel.errors import InfrastructureError
from sentinel.finding import (
    Confidence,
    Exploitability,
    FileLocation,
    Finding,
    FindingSource,
    FindingStatus,
    NotReviewedReview,
    ProvenanceEntry,
    StaticEvidence,
    make_dedup_key,
)
from sentinel.report.model import (
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
)
from sentinel.static.catalog import RULE_BY_ID, RULE_IDS
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    StaticScanResult,
)
from sentinel.static.rules import (
    sent001,
    sent002,
    sent003,
    sent004,
    sent005,
    sent006,
    sent007,
)
from sentinel.static.semgrep_adapter import run_semgrep
from sentinel.static.traversal import collect_static_files

STATIC_TIMEOUT_SECONDS = 120

AstDetector = Callable[[StaticContext, RuleRunState], None]
_AST_DETECTORS: dict[str, AstDetector] = {
    "SENT-001": sent001.detect,
    "SENT-003": sent003.detect,
    "SENT-004": sent004.detect,
    "SENT-006": sent006.detect,
    "SENT-007": sent007.detect,
}


def run_static_scan(
    configuration: LoadedConfiguration,
    scan_id: UUID,
    *,
    timestamp: datetime,
) -> StaticScanResult:
    """Execute every selected Phase 1 static rule without target-code execution."""

    started = time.monotonic()
    selected = select_rule_ids(configuration.scanner.scanner.rules)
    files = collect_static_files(
        configuration.scan_root,
        configuration.scanner.scanner.ignore_paths,
    )
    context = StaticContext(configuration=configuration, files=files)
    states = {rule_id: RuleRunState() for rule_id in selected}
    semgrep_matches = run_semgrep(
        files,
        selected,
        configuration.scan_root,
        deadline=started + STATIC_TIMEOUT_SECONDS,
    )

    for rule_id in selected:
        _enforce_timeout(started)
        state = states[rule_id]
        if rule_id == "SENT-002":
            sent002.run(semgrep_matches.get(rule_id, []), state)
        elif rule_id == "SENT-005":
            sent005.run(context, semgrep_matches.get(rule_id, []), state)
        else:
            _AST_DETECTORS[rule_id](context, state)

    findings: list[Finding] = []
    outcomes: list[StaticRuleOutcome] = []
    for rule_id in selected:
        state = states[rule_id]
        matches = _deduplicate(state.matches)
        if state.skip_reason is None:
            findings.extend(
                _finding_from_match(match, scan_id, timestamp) for match in matches
            )
            status = StaticRuleStatus.EVALUATED
        else:
            status = StaticRuleStatus.SKIPPED
        outcomes.append(
            StaticRuleOutcome(
                rule_id=rule_id,
                status=status,
                match_count=len(matches),
                exemptions_by_reason=dict(sorted(state.exemptions.items())),
                skip_reason=state.skip_reason,
            )
        )
    findings.sort(key=_finding_sort_key)
    duration_ms = round((time.monotonic() - started) * 1000)
    summary = StaticAnalysisSummary(
        selected_rule_ids=selected,
        scanned_file_count=files.scanned_file_count,
        ignored_file_count=files.ignored_file_count,
        total_matches=len(findings),
        duration_ms=duration_ms,
        rule_outcomes=tuple(outcomes),
    )
    return StaticScanResult(
        findings=tuple(findings),
        warnings=files.warnings,
        summary=summary,
    )


def select_rule_ids(tokens: tuple[str, ...]) -> tuple[str, ...]:
    """Resolve comma-list include/exclude semantics into canonical rule order."""

    includes = {
        token.removeprefix("+") for token in tokens if not token.startswith("-")
    }
    excludes = {token.removeprefix("-") for token in tokens if token.startswith("-")}
    selected = includes if includes else set(RULE_IDS)
    return tuple(rule_id for rule_id in RULE_IDS if rule_id in selected - excludes)


def _enforce_timeout(started: float) -> None:
    if time.monotonic() - started > STATIC_TIMEOUT_SECONDS:
        raise InfrastructureError("static analysis exceeded its 120-second timeout")


def _deduplicate(matches: list[StaticMatch]) -> tuple[StaticMatch, ...]:
    groups: dict[tuple[object, ...], StaticMatch] = {}
    for match in matches:
        key = (
            match.rule_id,
            match.path,
            match.range.start_line,
            match.range.start_column,
            match.range.end_line,
            match.range.end_column,
        )
        existing = groups.get(key)
        if existing is None:
            groups[key] = match
            continue
        groups[key] = StaticMatch(
            rule_id=match.rule_id,
            path=match.path,
            range=match.range,
            snippet=existing.snippet,
            fingerprint=existing.fingerprint or match.fingerprint,
            match_kinds=tuple(sorted(set((*existing.match_kinds, *match.match_kinds)))),
        )
    return tuple(sorted(groups.values(), key=_match_sort_key))


def _finding_from_match(
    match: StaticMatch,
    scan_id: UUID,
    timestamp: datetime,
) -> Finding:
    definition = RULE_BY_ID[match.rule_id]
    evidence = StaticEvidence(
        snippet=match.snippet,
        range=match.range,
        fingerprint=match.fingerprint,
    )
    provenance = ProvenanceEntry(
        source=FindingSource.STATIC,
        rule_id=match.rule_id,
        evidence=evidence,
        timestamp=timestamp,
    )
    return Finding(
        finding_id=uuid4(),
        dedup_key=make_dedup_key(
            (
                match.rule_id,
                match.path,
                str(match.range.start_line),
                str(match.range.start_column),
                str(match.range.end_line),
                str(match.range.end_column),
            )
        ),
        rule_id=match.rule_id,
        title=definition.title,
        description=definition.description,
        impact=definition.impact,
        exploitability=Exploitability.THEORETICAL,
        confidence=Confidence.HIGH,
        status=FindingStatus.NEEDS_REVIEW,
        owasp_category=definition.owasp_category,
        source=FindingSource.STATIC,
        location=FileLocation(path=match.path, range=match.range),
        evidence=evidence,
        remediation=definition.remediation,
        scan_id=scan_id,
        timestamp=timestamp,
        provenance=(provenance,),
        review=NotReviewedReview(),
    )


def _match_sort_key(match: StaticMatch) -> tuple[object, ...]:
    return (
        match.rule_id,
        match.path,
        match.range.start_line,
        match.range.start_column,
        match.range.end_line,
        match.range.end_column,
    )


def _finding_sort_key(finding: Finding) -> tuple[object, ...]:
    location = finding.location
    if not isinstance(location, FileLocation):
        return (finding.rule_id, location.path, 0, 0, 0, 0)
    source_range = location.range
    return (
        finding.rule_id,
        location.path,
        source_range.start_line,
        source_range.start_column,
        source_range.end_line,
        source_range.end_column,
    )
