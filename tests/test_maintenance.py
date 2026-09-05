"""Phase 13 public maintenance configuration checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [f"SENT-{number:03d}" for number in range(1, 12)]


def _yaml(path: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fields(form: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in form["body"] if "id" in item}


def test_issue_forms_are_bounded_and_reproducible() -> None:
    config = _yaml(".github/ISSUE_TEMPLATE/config.yml")
    assert config == {"blank_issues_enabled": False, "contact_links": []}

    false_positive = _yaml(".github/ISSUE_TEMPLATE/false-positive.yml")
    assert false_positive["title"] == "[False positive] "
    assert false_positive["labels"] == ["bug"]
    false_fields = _fields(false_positive)
    assert set(false_fields) == {
        "version",
        "rule",
        "language-framework",
        "command-configuration",
        "finding",
        "reproduction",
        "expected",
        "no-secrets",
    }
    assert false_fields["rule"]["attributes"]["options"] == RULE_IDS
    assert all(
        field.get("validations", {}).get("required") is True
        for field in false_fields.values()
        if field["type"] != "checkboxes"
    )
    assert false_fields["no-secrets"]["attributes"]["options"][0]["required"]

    proposal = _yaml(".github/ISSUE_TEMPLATE/rule-proposal.yml")
    assert proposal["title"] == "[Rule proposal] "
    assert proposal["labels"] == ["enhancement"]
    proposal_fields = _fields(proposal)
    assert set(proposal_fields) == {
        "supported-scope",
        "detection",
        "owasp",
        "impact",
        "engine",
        "vulnerable-example",
        "clean-example",
        "false-positive-risks",
        "remediation",
    }
    assert all(
        field.get("validations", {}).get("required") is True
        for field in proposal_fields.values()
    )
    assert "Maintainers assign stable rule IDs" in str(proposal["body"][-1])


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
