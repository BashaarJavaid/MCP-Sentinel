"""Typed internal contracts for deterministic static analysis."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from sentinel.config import LoadedConfiguration
from sentinel.finding import Finding, Impact, OwaspCategory, SourceRange
from sentinel.report.model import ReportWarning, StaticAnalysisSummary


class RuleEngine(str, Enum):
    AST = "ast"
    SEMGREP = "semgrep"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    title: str
    description: str
    impact: Impact
    remediation: str
    false_positive_risk: str
    owasp_category: OwaspCategory
    engine: RuleEngine
    help_uri: str


@dataclass(frozen=True)
class StaticMatch:
    rule_id: str
    path: str
    range: SourceRange
    snippet: str
    fingerprint: str | None = None
    match_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class ParsedPythonFile:
    path: Path
    relative_path: str
    source: str
    tree: ast.Module


@dataclass(frozen=True)
class StaticFileSet:
    python_files: tuple[ParsedPythonFile, ...]
    config_files: tuple[Path, ...]
    scanned_file_count: int
    ignored_file_count: int
    warnings: tuple[ReportWarning, ...]


@dataclass
class RuleRunState:
    matches: list[StaticMatch] = field(default_factory=list)
    exemptions: dict[str, int] = field(default_factory=dict)
    skip_reason: str | None = None

    def exempt(self, reason: str) -> None:
        self.exemptions[reason] = self.exemptions.get(reason, 0) + 1


@dataclass(frozen=True)
class StaticScanResult:
    findings: tuple[Finding, ...]
    warnings: tuple[ReportWarning, ...]
    summary: StaticAnalysisSummary


@dataclass(frozen=True)
class StaticContext:
    configuration: LoadedConfiguration
    files: StaticFileSet
