"""Typed internal contracts for deterministic static analysis."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from sentinel.config import LoadedConfiguration
from sentinel.finding import Finding, Impact, OwaspCategory, SourceRange
from sentinel.report.model import ReportWarning, StaticAnalysisSummary

if TYPE_CHECKING:
    from sentinel.static.discovery import PythonProgram
    from sentinel.static.http_discovery import HTTPBinding
    from sentinel.static.typescript_discovery import TypeScriptProgram


class RuleEngine(str, Enum):
    AST = "ast"
    SEMGREP = "semgrep"
    HYBRID = "hybrid"


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
    captures: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedPythonFile:
    path: Path
    relative_path: str
    source: str
    tree: ast.Module


@dataclass(frozen=True)
class TypeScriptSourceFile:
    path: Path
    relative_path: str
    source: str


@dataclass(frozen=True)
class StaticFileSet:
    python_files: tuple[ParsedPythonFile, ...]
    typescript_files: tuple[TypeScriptSourceFile, ...]
    config_files: tuple[Path, ...]
    scanned_file_count: int
    ignored_file_count: int
    warnings: tuple[ReportWarning, ...]


@dataclass
class RuleRunState:
    matches: list[StaticMatch] = field(default_factory=list)
    exemptions: dict[str, int] = field(default_factory=dict)
    skip_reason: str | None = None
    warnings: list[ReportWarning] = field(default_factory=list)

    visits: list[tuple[str, SourceRange]] = field(default_factory=list)

    def visit(self, path: str, location: SourceRange) -> None:
        self.visits.append((path, location))

    def exempt(self, reason: str) -> None:
        self.exemptions[reason] = self.exemptions.get(reason, 0) + 1


@dataclass(frozen=True)
class StaticScanResult:
    findings: tuple[Finding, ...]
    warnings: tuple[ReportWarning, ...]
    summary: StaticAnalysisSummary
    incomplete: bool = False


@dataclass(frozen=True)
class StaticContext:
    configuration: LoadedConfiguration
    files: StaticFileSet
    deadline: float = float("inf")

    @cached_property
    def python_program(self) -> PythonProgram:
        from sentinel.static.discovery import PythonProgram

        return PythonProgram(self.files.python_files, deadline=self.deadline)

    @cached_property
    def python_http_handlers(self) -> tuple[HTTPBinding, ...]:
        from sentinel.static.http_discovery import handlers

        return handlers(self.python_program)

    @cached_property
    def typescript_program(self) -> TypeScriptProgram:
        from sentinel.static.typescript_discovery import TypeScriptProgram
        from sentinel.static.typescript_modules import TypeScriptModules

        workspace = self.configuration.workspace
        return TypeScriptProgram(
            self.files.typescript_files,
            deadline=self.deadline,
            modules=TypeScriptModules(
                self.configuration.scan_root,
                self.files.config_files,
                workspace.members if workspace else (".",),
            ),
        )
