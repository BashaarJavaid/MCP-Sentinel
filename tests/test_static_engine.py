"""Phase 1 static-engine and reference-fixture acceptance tests."""

from __future__ import annotations

import hashlib
import json
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from sentinel.config import (
    RulesConfig,
    Sent004Config,
    Sent005AllowlistEntry,
    Sent006Config,
    load_configuration,
)
from sentinel.errors import UsageError
from sentinel.finding import FileLocation, FindingStatus, StaticEvidence
from sentinel.orchestrator import run_phase1_scan
from sentinel.report.model import ScanContext, ScanTarget, StaticRuleStatus
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.static.engine import run_static_scan, select_rule_ids
from sentinel.static.traversal import MAX_STATIC_FILE_BYTES, collect_static_files
from tests.conftest import make_target

ROOT = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 7, 17, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("vulnerable_server", [f"SENT-{number:03d}" for number in range(1, 8)]),
        ("clean_server", []),
    ],
)
def test_reference_fixture_acceptance(fixture: str, expected: list[str]) -> None:
    configuration = load_configuration(ROOT / fixture, environ={}, static_only=True)
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)

    assert [finding.rule_id for finding in result.findings] == expected
    assert result.summary.total_matches == len(expected)
    assert result.summary.selected_rule_ids == tuple(
        f"SENT-{number:03d}" for number in range(1, 8)
    )
    for finding in result.findings:
        assert finding.status is FindingStatus.NEEDS_REVIEW
        assert isinstance(finding.location, FileLocation)
        assert not Path(finding.location.path).is_absolute()


def test_secret_evidence_is_redacted_but_fingerprinted() -> None:
    configuration = load_configuration(
        ROOT / "vulnerable_server", environ={}, static_only=True
    )
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)
    finding = next(item for item in result.findings if item.rule_id == "SENT-005")

    assert isinstance(finding.evidence, StaticEvidence)
    assert "<redacted>" in finding.evidence.snippet
    assert "ghp_" not in finding.evidence.snippet
    assert finding.evidence.fingerprint is not None
    assert len(finding.evidence.fingerprint) == 64


def test_phase1_sarif_contains_findings_and_full_rule_catalog() -> None:
    configuration = load_configuration(ROOT / "vulnerable_server", environ={})
    context = ScanContext(
        scan_id=uuid4(),
        started_at=NOW,
        target=ScanTarget(display_name="vulnerable_server"),
    )
    report = run_phase1_scan(configuration, context, completed_at=NOW).report
    payload = json.loads(render_sarif(report))
    validate_sarif_data(payload)

    run = payload["runs"][0]
    assert len(run["tool"]["driver"]["rules"]) == 7
    assert len(run["results"]) == 7
    first = run["results"][0]
    assert first["ruleId"] == "SENT-001"
    artifact = first["locations"][0]["physicalLocation"]["artifactLocation"]
    assert artifact["uri"] == "server.py"
    assert artifact["uriBaseId"] == "SRCROOT"
    assert first["properties"]["owaspId"] == "ASI03:2026"


def test_rule_selection_uses_include_then_exclude_semantics() -> None:
    assert select_rule_ids(()) == tuple(f"SENT-{number:03d}" for number in range(1, 8))
    assert select_rule_ids(("SENT-003", "+SENT-005", "-SENT-003")) == ("SENT-005",)
    assert select_rule_ids(("-SENT-007",))[-1] == "SENT-006"


def test_missing_permissions_sidecar_marks_sent001_skipped(tmp_path: Path) -> None:
    root = make_target(
        tmp_path / "target",
        scanner_toml='[scanner]\nrules = ["SENT-001"]\n',
    )
    (root / "sentinel.permissions.yaml").unlink()
    configuration = load_configuration(root, environ={}, static_only=True)
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)

    outcome = result.summary.rule_outcomes[0]
    assert outcome.status is StaticRuleStatus.SKIPPED
    assert outcome.skip_reason == "sentinel.permissions.yaml is absent"


def test_secret_allowlist_requires_matching_path_and_fingerprint(
    tmp_path: Path,
) -> None:
    value = "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0"
    fingerprint = hashlib.sha256(value.encode()).hexdigest()
    scanner_toml = f'''\
[scanner]
rules = ["SENT-005"]

[rules.SENT-005]
allowlist = [
  {{path = "server.py", fingerprint = "{fingerprint}", reason = "fixture"}},
]
'''
    root = make_target(tmp_path / "target", scanner_toml=scanner_toml)
    (root / "server.py").write_text(f'api_key = "{value}"\n', encoding="utf-8")
    configuration = load_configuration(root, environ={}, static_only=True)
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)

    assert result.findings == ()
    assert result.summary.rule_outcomes[0].exemptions_by_reason == {
        "configured_path_and_fingerprint": 1
    }


def test_traversal_honors_nested_gitignore_config_and_symlinks(
    tmp_path: Path,
) -> None:
    root = tmp_path / "target"
    nested = root / "nested"
    ignored = root / "configured"
    nested.mkdir(parents=True)
    ignored.mkdir()
    (root / "keep.py").write_text("value = 1\n", encoding="utf-8")
    (nested / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
    (nested / "ignored.py").write_text("value = 2\n", encoding="utf-8")
    (nested / "keep.json").write_text("{}\n", encoding="utf-8")
    (ignored / "skip.py").write_text("value = 3\n", encoding="utf-8")
    with suppress(OSError):
        (root / "linked.py").symlink_to(root / "keep.py")

    files = collect_static_files(root, ("configured/",))
    assert [item.relative_path for item in files.python_files] == ["keep.py"]
    assert [path.name for path in files.config_files] == ["keep.json"]
    if (root / "linked.py").is_symlink():
        assert files.warnings[0].code == "static_symlinks_skipped"


@pytest.mark.parametrize(
    ("name", "content", "message"),
    [
        ("broken.py", "def nope(:\n", "cannot parse Python source"),
        ("broken.json", "{", "cannot parse configuration"),
        (".env", "NOT_AN_ASSIGNMENT", "invalid dotenv syntax"),
    ],
)
def test_traversal_rejects_malformed_supported_files(
    tmp_path: Path, name: str, content: str, message: str
) -> None:
    (tmp_path / name).write_text(content, encoding="utf-8")
    with pytest.raises(UsageError, match=message):
        collect_static_files(tmp_path, ())


def test_traversal_rejects_oversized_supported_file(tmp_path: Path) -> None:
    (tmp_path / "large.py").write_text(
        "x" * (MAX_STATIC_FILE_BYTES + 1), encoding="utf-8"
    )
    with pytest.raises(UsageError, match="1 MiB"):
        collect_static_files(tmp_path, ())


def test_rule_specific_configuration_is_strict() -> None:
    valid = RulesConfig.model_validate(
        {
            "SENT-004": {"sanitizers": ["security.clean"]},
            "SENT-005": {
                "allowlist": [
                    {
                        "path": "tests/fixtures/**",
                        "fingerprint": "0" * 64,
                        "reason": "recorded non-secret fixture",
                    }
                ]
            },
            "SENT-006": {"public_routes": ["GET /health"]},
        }
    )
    assert valid.sent005.allowlist[0].reason == "recorded non-secret fixture"
    with pytest.raises(ValidationError):
        Sent004Config(sanitizers=("not valid",))
    with pytest.raises(ValidationError):
        Sent006Config(public_routes=("/health",))
    with pytest.raises(ValidationError):
        Sent005AllowlistEntry(path="../escape", fingerprint="x", reason=" ")
