"""Shared scanner fixtures."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from sentinel.config import LoadedConfiguration, load_configuration
from sentinel.finding import (
    Confidence,
    Exploitability,
    FileLocation,
    Finding,
    FindingSource,
    FindingStatus,
    Impact,
    OwaspCategory,
    ProvenanceEntry,
    SourceRange,
    StaticEvidence,
    make_dedup_key,
)

SCAN_ID = UUID("00000000-0000-4000-8000-000000000001")
FINDING_ID = UUID("00000000-0000-4000-8000-000000000002")
NOW = datetime(2026, 7, 17, 12, 0, 0, 123456, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def forbid_live_openai_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """Routine tests must remain offline even on a developer machine with a key."""

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def reject_live_client(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("offline tests cannot instantiate AsyncOpenAI")

    monkeypatch.setattr(
        "sentinel.llm.semantic_reviewer.AsyncOpenAI", reject_live_client
    )


def make_target(
    root: Path,
    *,
    scanner_toml: str | None = None,
    target_yaml: str | None = None,
    dependency: str = "mcp>=1,<2",
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(
        "\n".join(
            (
                "[project]",
                'name = "fixture-target"',
                'version = "0.0.0"',
                'requires-python = ">=3.10,<3.13"',
                f'dependencies = ["{dependency}"]',
                "",
            )
        ),
        encoding="utf-8",
    )
    (root / "server.py").write_text(
        'raise RuntimeError("target code must not execute")\n', encoding="utf-8"
    )
    if target_yaml is None:
        target_yaml = """\
language: python
launch_cmd: [python, server.py]
transport: stdio
working_dir: .
env: {LOG_LEVEL: debug}
env_from: []
"""
    if target_yaml:
        (root / "sentinel.target.yaml").write_text(target_yaml, encoding="utf-8")
    if scanner_toml is not None:
        (root / "sentinel.toml").write_text(scanner_toml, encoding="utf-8")
    return root


@pytest.fixture
def target_root(tmp_path: Path) -> Path:
    return make_target(tmp_path / "target")


@pytest.fixture
def loaded_config(target_root: Path) -> LoadedConfiguration:
    return load_configuration(target_root, environ={})


@pytest.fixture
def sample_finding() -> Finding:
    source_range = SourceRange(start_line=4, start_column=2, end_line=4, end_column=12)
    evidence = StaticEvidence(snippet="eval(value)", range=source_range)
    return Finding(
        finding_id=FINDING_ID,
        dedup_key=make_dedup_key(("SENT-002", "server.py", "4:2")),
        rule_id="SENT-002",
        title="Unsafe evaluation",
        description="Raw tool input reaches eval.",
        impact=Impact.CRITICAL,
        exploitability=Exploitability.THEORETICAL,
        confidence=Confidence.HIGH,
        status=FindingStatus.NEEDS_REVIEW,
        owasp_category=OwaspCategory(id="ASI05:2026", name="Unexpected Code Execution"),
        source=FindingSource.STATIC,
        location=FileLocation(path="server.py", range=source_range),
        evidence=evidence,
        remediation="Replace eval with an explicit parser.",
        scan_id=SCAN_ID,
        timestamp=NOW,
        provenance=(
            ProvenanceEntry(
                source=FindingSource.STATIC,
                rule_id="SENT-002",
                evidence=evidence,
                timestamp=NOW,
            ),
        ),
    )
