"""Public maintenance configuration checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from sentinel.owasp_mapping import RULE_OWASP_IDS

ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = list(RULE_OWASP_IDS)


def _yaml(path: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fields(form: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in form["body"] if "id" in item}


def test_issue_forms_are_bounded_and_reproducible() -> None:
    config = _yaml(".github/ISSUE_TEMPLATE/config.yml")
    assert config["blank_issues_enabled"] is False
    assert config["contact_links"][0]["url"] == (
        "https://github.com/BashaarJavaid/MCP-Sentinel/security/advisories/new"
    )
    required_fields = {
        "false-positive": {
            "version",
            "rule",
            "language-framework",
            "command-configuration",
            "finding",
            "reproduction",
            "expected",
        },
        "missed-vulnerability": {
            "version",
            "rule",
            "language-framework",
            "command-configuration",
            "observed-report",
            "reproduction",
            "expected",
            "fixed-safe",
        },
        "rule-proposal": {
            "related-rule",
            "environment-configuration",
            "supported-scope",
            "detection",
            "owasp",
            "impact",
            "engine",
            "vulnerable-example",
            "clean-example",
            "false-positive-risks",
            "remediation",
        },
    }
    for name, required in required_fields.items():
        form = _yaml(f".github/ISSUE_TEMPLATE/{name}.yml")
        assert len(form["body"]) <= 20
        assert form["labels"] == ["enhancement" if name == "rule-proposal" else "bug"]
        fields = _fields(form)
        assert len(fields) == sum("id" in item for item in form["body"])
        assert set(fields) == required | {
            "source-rights",
            "no-secrets",
            "example-reuse",
        }
        rule_field = fields["related-rule" if name == "rule-proposal" else "rule"]
        assert [
            value
            for value in rule_field["attributes"]["options"]
            if value.startswith("SENT-")
        ] == RULE_IDS
        assert all(
            field.get("validations", {}).get("required") is True
            for field in fields.values()
            if field["type"] != "checkboxes"
        )
        assert fields["no-secrets"]["attributes"]["options"][0]["required"] is True
        consent = fields["example-reuse"]
        assert consent["attributes"]["options"][0]["required"] is False
        assert not consent.get("validations", {}).get("required", False)
        assert "MIT license" in consent["attributes"]["options"][0]["label"]
        assert "unreviewed" in str(form)
        assert "private reporting" in str(form)
        assert "upstream security policy" in str(form)


def test_dependabot_updates_are_bounded() -> None:
    config = _yaml(".github/dependabot.yml")
    assert config["version"] == 2
    updates = {item["package-ecosystem"]: item for item in config["updates"]}
    assert set(updates) == {"pip", "github-actions"}
    for ecosystem, item in updates.items():
        assert item["directory"] == "/"
        assert item["schedule"] == {
            "interval": "weekly",
            "day": "monday",
            "time": "09:00",
            "timezone": "America/Los_Angeles",
        }
        assert item["open-pull-requests-limit"] == 5
        assert "labels" not in item
        assert "assignees" not in item and "reviewers" not in item
        groups = list(item["groups"].values())
        assert groups == [{"update-types": ["minor", "patch"]}]
        assert "applies-to" not in groups[0]
        if ecosystem == "pip":
            assert item["versioning-strategy"] == "increase-if-necessary"


def test_documentation_workflow_is_pinned_and_deploy_limited() -> None:
    text = (ROOT / ".github/workflows/docs.yml").read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert workflow["on"] == {
        "pull_request": "",
        "push": {"branches": ["main"]},
        "workflow_dispatch": "",
    }
    for revision in (
        "d23441a48e516b6c34aea4fa41551a30e30af803",
        "ece7cb06caefa5fff74198d8649806c4678c61a1",
        "d0cc045d04ccac9d8b7881df0226f9e82c39688e",
        "983d7736d9b0ae728b81ab479565c72886d7745b",
        "7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
        "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
    ):
        assert revision in text
    deploy = workflow["jobs"]["deploy"]
    assert deploy["permissions"] == {"pages": "write", "id-token": "write"}
    assert deploy["environment"]["name"] == "github-pages"
    assert deploy["concurrency"]["cancel-in-progress"] == "true"
    assert "mkdocs build --strict" in text
    assert "sent-001" not in text  # anchors are checked generically, not duplicated
    assert "{001..011}" in text


def test_public_surfaces_reject_unscoped_legacy_branding() -> None:
    allowed_files = {
        Path("CHANGELOG.md"),
        Path("mcp-sentinel-buildplan.md"),
        Path("docs/hackathon.md"),
        Path("docs/sarif.md"),
    }
    allowed_roots = {"artifacts", "scripts", "src", "tests"}
    legacy = re.compile(r"(?<!Portunus)MCP Sentinel")
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if (
            not path.is_file()
            or path.suffix not in {".md", ".py", ".toml", ".yaml", ".yml"}
            or relative in allowed_files
            or relative.parts[0] in allowed_roots
            or ".git" in relative.parts
            or ".venv" in relative.parts
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if relative == Path("docs/walkthrough.md"):
            text = text.replace("older **MCP Sentinel v0.1.0** branding", "")
        if legacy.search(text):
            offenders.append(str(relative))
    assert offenders == []


@pytest.mark.parametrize(
    ("interfaces", "routes", "flags", "ipv6_routes", "accepted"),
    (
        ("lo: 0", "", "0x1", "", True),
        ("lo: 0", "Iface Destination\n\n", "0x1", "", True),
        ("lo: 0", "Iface Destination\nlo 00000000\n", "0x1", "", True),
        ("eth0: 0", "Iface Destination\n", "0x1", "", False),
        ("lo: 0", "Iface Destination\neth0 00000000\n", "0x1", "", False),
        ("lo: 0\ngre0: 0", "Iface Destination\n", "0x80", "", True),
        ("lo: 0", "Iface Destination\n", "0x1", "0000 00 lo\n", True),
        ("lo: 0", "Iface Destination\n", "0x1", "0000 00 eth0\n", False),
        ("eth0: 0", "Iface Destination\neth0 00000000\n", "0x0", "", False),
    ),
)
def test_offline_gate_checks_network_state_not_route_file_length(
    monkeypatch: pytest.MonkeyPatch,
    interfaces: str,
    routes: str,
    flags: str,
    ipv6_routes: str,
    accepted: bool,
) -> None:
    from scripts import smoke_wheel

    monkeypatch.setattr("sys.argv", ["smoke_wheel.py", "offline", "bin"])
    scans: list[Path] = []
    monkeypatch.setattr(smoke_wheel, "_check_rules_only_scans", scans.append)

    def read_text(path: Path, *args: object, **kwargs: object) -> str:
        return {
            "dev": "header\nheader\n" + interfaces,
            "route": routes,
            "ipv6_route": ipv6_routes,
            "flags": flags,
        }[path.name]

    monkeypatch.setattr(Path, "read_text", read_text)
    if accepted:
        assert smoke_wheel.main() == 0
        assert scans == [Path("bin")]
    else:
        with pytest.raises(AssertionError):
            smoke_wheel.main()
        assert scans == []
