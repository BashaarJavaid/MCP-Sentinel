"""Deterministic Phase 1 static-analysis engine."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from sentinel.config import LoadedConfiguration, TargetLanguage
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
    SourceRange,
    StaticEvidence,
    make_dedup_key,
)
from sentinel.report.model import (
    ReportWarning,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
)
from sentinel.static import typescript
from sentinel.static.catalog import RULE_BY_ID, RULE_IDS
from sentinel.static.coverage import inventory
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
    sent012,
    sent013,
    sent014,
)
from sentinel.static.semgrep_adapter import run_semgrep
from sentinel.static.suppression import apply_inline_suppressions
from sentinel.static.traversal import collect_static_files

STATIC_TIMEOUT_SECONDS = 120

AstDetector = Callable[[StaticContext, RuleRunState], None]
_AST_DETECTORS: dict[str, AstDetector] = {
    "SENT-001": sent001.detect,
    "SENT-003": sent003.detect,
    "SENT-004": sent004.detect,
    "SENT-006": sent006.detect,
    "SENT-007": sent007.detect,
    "SENT-012": sent012.detect,
    "SENT-013": sent013.detect,
    "SENT-014": sent014.detect,
}


def run_static_scan(
    configuration: LoadedConfiguration,
    scan_id: UUID,
    *,
    timestamp: datetime,
    deadline: float | None = None,
    forced_ignored_paths: frozenset[str] = frozenset(),
) -> StaticScanResult:
    """Execute every selected Phase 1 static rule without target-code execution."""

    started = time.monotonic()
    scan_deadline = deadline or started + STATIC_TIMEOUT_SECONDS
    selected = select_rule_ids(configuration.scanner.scanner.rules)
    files = collect_static_files(
        configuration.scan_root,
        configuration.scanner.scanner.ignore_paths,
        configuration.language,
        forced_ignored_paths,
    )
    context = StaticContext(
        configuration=configuration, files=files, deadline=scan_deadline
    )
    states = {rule_id: RuleRunState() for rule_id in selected}
    semgrep_matches = run_semgrep(
        files,
        selected,
        configuration.scan_root,
        deadline=scan_deadline,
    )

    for rule_id in selected:
        _enforce_timeout(scan_deadline)
        state = states[rule_id]
        if rule_id in {"SENT-012", "SENT-013", "SENT-014"}:
            _AST_DETECTORS[rule_id](context, state)
        elif configuration.language is TargetLanguage.TYPESCRIPT:
            if rule_id == "SENT-005":
                sent005.run(context, semgrep_matches.get(rule_id, []), state)
            else:
                typescript.detect(
                    rule_id,
                    context,
                    state,
                    semgrep_matches.get(rule_id),
                )
        elif rule_id == "SENT-002":
            sent002.run(context, semgrep_matches.get(rule_id, []), state)
        elif rule_id == "SENT-005":
            sent005.run(context, semgrep_matches.get(rule_id, []), state)
        else:
            _AST_DETECTORS[rule_id](context, state)
        if configuration.language is TargetLanguage.WORKSPACE and rule_id not in {
            "SENT-005",
            "SENT-012",
            "SENT-013",
            "SENT-014",
        }:
            typescript.detect(rule_id, context, state, semgrep_matches.get(rule_id))

    findings: list[Finding] = []
    outcomes: list[StaticRuleOutcome] = []
    for rule_id in selected:
        state = states[rule_id]
        matches = _deduplicate(state.matches)
        if state.skip_reason is None:
            for match in matches:
                finding = _finding_from_match(match, scan_id, timestamp)
                findings.append(finding)
                if "flow_locations" in match.captures:
                    from sentinel.llm.context import build_finding_context

                    review_context = build_finding_context(
                        configuration.scan_root, finding
                    )
                    if any(
                        not review_context.contains(path, line, line)
                        for path, line in json.loads(match.captures["flow_locations"])
                    ):
                        state.warnings.append(
                            ReportWarning(
                                code="static_review_context_incomplete",
                                message=(
                                    f"{rule_id} at {match.path}:"
                                    f"{match.range.start_line}: resolved source/guard/"
                                    "sink evidence extends beyond the supplied "
                                    "review context."
                                ),
                            )
                        )
                if "flow_lines" in match.captures:
                    from sentinel.llm.context import build_finding_context

                    review_context = build_finding_context(
                        configuration.scan_root, finding
                    )
                    if any(
                        not review_context.contains(match.path, line, line)
                        for line in json.loads(match.captures["flow_lines"])
                    ):
                        state.warnings.append(
                            ReportWarning(
                                code="static_review_context_incomplete",
                                message=(
                                    f"SENT-002 at {match.path}:"
                                    f"{match.range.start_line}: helper flow extends "
                                    "beyond the existing model-review context."
                                ),
                            )
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
    suppressed_findings, suppression_warnings = apply_inline_suppressions(
        files, tuple(findings)
    )
    duration_ms = round((time.monotonic() - started) * 1000)
    summary = StaticAnalysisSummary(
        coverage=inventory(context, states),
        selected_rule_ids=selected,
        scanned_file_count=files.scanned_file_count,
        ignored_file_count=files.ignored_file_count,
        total_matches=len(findings),
        duration_ms=duration_ms,
        rule_outcomes=tuple(outcomes),
    )
    warnings = [*files.warnings, *suppression_warnings]
    workspace = configuration.workspace
    if workspace:
        for issue in workspace.issues:
            warnings.append(
                ReportWarning(
                    code="workspace_member_incomplete",
                    message=f"{issue.path}: {issue.reason}",
                )
            )
        for path in files.config_files:
            if path.parent != configuration.scan_root and path.name.startswith(
                "sentinel."
            ):
                warnings.append(
                    ReportWarning(
                        code="workspace_nested_configuration",
                        message=(
                            f"{path.relative_to(configuration.scan_root).as_posix()}: "
                            "nested configuration is not applied; "
                            "the aggregate uses root Sentinel configuration"
                        ),
                    )
                )

    for rule_id in selected:
        warnings.extend(states[rule_id].warnings)
    keys = tuple(dict.fromkeys((warning.code, warning.message) for warning in warnings))
    return StaticScanResult(
        findings=suppressed_findings,
        warnings=tuple(
            next(
                warning
                for warning in warnings
                if (warning.code, warning.message) == key
            )
            for key in keys
        ),
        summary=summary,
        incomplete=bool(workspace and workspace.issues),
    )


def select_rule_ids(tokens: tuple[str, ...]) -> tuple[str, ...]:
    """Resolve comma-list include/exclude semantics into canonical rule order."""

    includes = {
        token.removeprefix("+") for token in tokens if not token.startswith("-")
    }
    excludes = {token.removeprefix("-") for token in tokens if token.startswith("-")}
    selected = includes if includes else set(RULE_IDS)
    return tuple(rule_id for rule_id in RULE_IDS if rule_id in selected - excludes)


def _enforce_timeout(deadline: float) -> None:
    if time.monotonic() > deadline:
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
        captures = {**match.captures, **existing.captures}
        for field in ("flow_locations", "flow_lines"):
            if field in captures:
                records = [
                    item
                    for candidate in (existing, match)
                    for item in json.loads(candidate.captures.get(field, "[]"))
                ]
                captures[field] = json.dumps(
                    sorted(
                        {
                            tuple(item) if isinstance(item, list) else item
                            for item in records
                        }
                    )
                )
        groups[key] = StaticMatch(
            rule_id=match.rule_id,
            path=match.path,
            range=match.range,
            snippet=existing.snippet,
            fingerprint=existing.fingerprint or match.fingerprint,
            match_kinds=tuple(sorted(set((*existing.match_kinds, *match.match_kinds)))),
            captures=captures,
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
        flow_locations=tuple(
            FileLocation(
                path=path,
                range=SourceRange(
                    start_line=line,
                    start_column=1,
                    end_line=line,
                    end_column=2,
                ),
            )
            for path, line in json.loads(match.captures.get("flow_locations", "[]"))
        )
        or tuple(
            FileLocation(
                path=match.path,
                range=SourceRange(
                    start_line=line,
                    start_column=1,
                    end_line=line,
                    end_column=2,
                ),
            )
            for line in json.loads(match.captures.get("flow_lines", "[]"))
        ),
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
        description=definition.description
        + (
            f" Tool input reaches {match.captures['execution_sinks']} "
            "through a same-file helper."
            if "execution_sinks" in match.captures
            else ""
        ),
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
