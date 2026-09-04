"""Phase 11 TypeScript static-analysis acceptance tests."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from typer.testing import CliRunner

from sentinel.cli import app
from sentinel.config import TargetLanguage, load_configuration
from sentinel.errors import TargetError
from sentinel.finding import FileLocation
from sentinel.llm.context import build_finding_context
from sentinel.llm.tools import extract_tool_catalog
from sentinel.onboarding import initialize_repository
from sentinel.orchestrator import run_scan
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import ScanContext, ScanTarget
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
from sentinel.static.engine import run_static_scan
from sentinel.static.semgrep_adapter import SEMGREP_TIMEOUT_SECONDS

ROOT = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 9, 3, tzinfo=timezone.utc)
RUNNER = CliRunner()


@pytest.mark.parametrize(
    ("fixture", "expected"),
    (
        (
            "typescript_vulnerable_server",
            [f"SENT-{number:03d}" for number in range(1, 8)],
        ),
        ("typescript_clean_server", []),
    ),
)
def test_typescript_reference_fixtures(fixture: str, expected: list[str]) -> None:
    configuration = load_configuration(ROOT / fixture, environ={}, static_only=True)
    result = run_static_scan(configuration, uuid4(), timestamp=NOW)

    assert configuration.language is TargetLanguage.TYPESCRIPT
    assert [finding.rule_id for finding in result.findings] == expected
    assert not (configuration.scan_root / "top-level-marker").exists()
    assert not (configuration.scan_root / "lifecycle-marker").exists()


def test_typescript_normal_scan_is_rejected_before_analysis() -> None:
    with pytest.raises(TargetError, match="--static-only"):
        load_configuration(ROOT / "typescript_clean_server", environ={})

    result = RUNNER.invoke(app, ["scan", str(ROOT / "typescript_clean_server")])
    assert result.exit_code == 2
    assert "--static-only" in result.stderr


def test_typescript_canonical_console_json_and_sarif_outputs() -> None:
    configuration = load_configuration(
        ROOT / "typescript_vulnerable_server", environ={}, static_only=True
    )
    context = ScanContext(
        scan_id=uuid4(),
        started_at=NOW,
        target=ScanTarget(display_name="typescript_vulnerable_server"),
    )

    outcome = run_scan(
        configuration,
        context,
        completed_at=NOW,
        allow_degraded=True,
    )

    assert outcome.exit_code == 1
    assert "SENT-001" in render_console(outcome.report, color=False)
    validate_report_data(json.loads(render_json(outcome.report)))
    validate_sarif_data(json.loads(render_sarif(outcome.report)))


def test_typescript_live_smoke_cassette_replays() -> None:
    configuration = load_configuration(
        ROOT / "typescript_vulnerable_server",
        environ={},
        cli_overrides={"rules": ("SENT-003",)},
        static_only=True,
    )
    context = ScanContext(
        scan_id=uuid4(),
        started_at=NOW,
        target=ScanTarget(display_name="typescript-smoke"),
    )

    outcome = run_scan(
        configuration,
        context,
        completed_at=NOW,
        allow_degraded=False,
        review_mode="replay",
        cassette_root=Path(__file__).parents[1]
        / "src"
        / "sentinel"
        / "_cassettes"
        / "typescript-smoke",
    )

    assert outcome.exit_code == 0
    review = outcome.report.findings[0].review
    assert outcome.report.findings[0].status.value == "confirmed"
    assert review.evidence_refs is not None
    assert len(review.evidence_refs) == 1
    assert review.probe_plan is not None
    assert set(review.probe_plan.ordered_probe_ids) == {
        "SENT-008",
        "SENT-009",
        "SENT-010",
        "SENT-011",
    }


def test_typescript_catalog_preserves_supported_zod_shape() -> None:
    catalog = extract_tool_catalog(ROOT / "typescript_clean_server")
    tool = catalog.tools[0]

    assert tool.name == "read"
    assert tool.input_schema == {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "additionalProperties": False,
    }

    recovered = extract_tool_catalog(ROOT / "typescript_vulnerable_server").tools[0]
    assert recovered.input_schema["properties"] == {"path": {"type": "string"}}


def test_typescript_gpt_context_is_redacted_line_preserving_and_80_lines() -> None:
    configuration = load_configuration(
        ROOT / "typescript_vulnerable_server", environ={}, static_only=True
    )
    finding = run_static_scan(configuration, uuid4(), timestamp=NOW).findings[0]

    context = build_finding_context(configuration.scan_root, finding)

    assert len(context.blocks) == 1
    block = context.blocks[0]
    assert block.end_line - block.start_line + 1 <= 80
    assert "server.registerTool(" in block.text
    assert "return eval(source);" in block.text
    assert isinstance(finding.location, FileLocation)
    assert context.contains(
        finding.location.path,
        finding.location.range.start_line,
        finding.location.range.end_line,
    )


def test_package_json_is_strict_and_dev_dependency_is_ignored(tmp_path: Path) -> None:
    (tmp_path / "server.ts").write_text("export {};\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{/* jsonc */}", encoding="utf-8")
    with pytest.raises(TargetError, match="strict JSON"):
        load_configuration(tmp_path, environ={}, static_only=True)

    (tmp_path / "package.json").write_text(
        json.dumps({"devDependencies": {"@modelcontextprotocol/sdk": "^1"}}),
        encoding="utf-8",
    )
    with pytest.raises(TargetError, match="unsupported target"):
        load_configuration(tmp_path, environ={}, static_only=True)


def _typescript_target(root: Path, source: str, *, sdk: str = "sdk") -> Path:
    root.mkdir()
    (root / "package.json").write_text(
        json.dumps({"dependencies": {f"@modelcontextprotocol/{sdk}": "^1.0.0"}}),
        encoding="utf-8",
    )
    (root / "server.ts").write_text(source, encoding="utf-8")
    (root / "sentinel.permissions.yaml").write_text(
        "version: 1\ntools: {}\n", encoding="utf-8"
    )
    return root


def test_v1_legacy_and_register_tool_catalog_with_constant_schema(
    tmp_path: Path,
) -> None:
    root = _typescript_target(
        tmp_path / "target",
        """
import { McpServer as Server } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
const schema = {
  query: z.string(),
  limit: z.number().optional(),
  enabled: z.boolean().default(true),
  tags: z.array(z.string()),
};
const server = new Server({name: "v1", version: "1"});
async function handler({query}: {query: string}) { return query; }
server.tool("legacy", "Legacy search.", schema, handler);
server.registerTool(
  "modern",
  {description: "Modern search.", inputSchema: z.object(schema)},
  handler,
);
""",
    )

    catalog = extract_tool_catalog(root)

    assert [tool.name for tool in catalog.tools] == ["legacy", "modern"]
    schema = cast(dict[str, Any], catalog.tools[0].input_schema)
    properties = cast(dict[str, Any], schema["properties"])
    assert schema["required"] == ["query", "tags"]
    assert properties["limit"] == {"type": "number"}
    assert properties["enabled"] == {"type": "boolean"}
    assert properties["tags"] == {
        "type": "array",
        "items": {"type": "string"},
    }


def test_v1_rules_cover_legacy_tool_and_register_tool(tmp_path: Path) -> None:
    vulnerable = _typescript_target(
        tmp_path / "vulnerable",
        """
const server = new McpServer({name: "v1", version: "1"});
server.tool("legacy", "Evaluate input.", async (expression) => eval(expression));
""",
    )
    vulnerable_config = load_configuration(
        vulnerable,
        environ={},
        cli_overrides={"rules": ("SENT-001", "SENT-002", "SENT-003")},
        static_only=True,
    )
    assert [
        finding.rule_id
        for finding in run_static_scan(
            vulnerable_config, uuid4(), timestamp=NOW
        ).findings
    ] == ["SENT-001", "SENT-002", "SENT-003"]

    clean = _typescript_target(
        tmp_path / "clean",
        """
import { z } from "zod";
const server = new McpServer({name: "v1", version: "1"});
server.registerTool(
  "modern",
  {description: "Return input.", inputSchema: {value: z.string()}},
  async ({value}) => value,
);
""",
    )
    (clean / "sentinel.permissions.yaml").write_text(
        "version: 1\ntools:\n  modern:\n"
        "    filesystem:\n      read: {scopes: []}\n      write: {scopes: []}\n"
        "    network: {scopes: []}\n",
        encoding="utf-8",
    )
    clean_config = load_configuration(
        clean,
        environ={},
        cli_overrides={"rules": ("SENT-001", "SENT-002", "SENT-003")},
        static_only=True,
    )
    assert run_static_scan(clean_config, uuid4(), timestamp=NOW).findings == ()


def test_typescript_metadata_warnings_and_tools_manifest_recovery(
    tmp_path: Path,
) -> None:
    root = _typescript_target(
        tmp_path / "target",
        """
const server = new McpServer({name: "v2", version: "2"});
const app = express();
const dynamicName = process.env.TOOL_NAME;
const route = process.env.ROUTE;
server.registerTool(dynamicName, {description: "Dynamic."}, async () => "ok");
server.registerTool("known", {inputSchema: importedSchema}, async ({value}) => value);
app.get(route, (context) => context.text("ok"));
""",
    )

    warnings = {warning.code for warning in extract_tool_catalog(root).warnings}
    assert warnings == {
        "typescript_route_path_dynamic",
        "typescript_tool_description_unavailable",
        "typescript_tool_name_dynamic",
        "typescript_tool_schema_unsupported",
    }

    (root / "tools.yaml").write_text(
        "tools:\n"
        "  - name: known\n"
        "    description: Recovered metadata.\n"
        "    input_schema:\n"
        "      type: object\n"
        "      properties:\n"
        "        value: {type: string}\n",
        encoding="utf-8",
    )
    recovered = extract_tool_catalog(root)
    assert {warning.code for warning in recovered.warnings} == {
        "typescript_route_path_dynamic",
        "typescript_tool_name_dynamic",
    }
    known = next(tool for tool in recovered.tools if tool.name == "known")
    assert known.description == "Recovered metadata."
    assert known.input_schema["type"] == "object"


def test_typescript_ignores_unrelated_tool_and_route_apis(tmp_path: Path) -> None:
    root = _typescript_target(
        tmp_path / "target",
        """
const unrelated = {tool() {}, get() {}};
unrelated.tool("fake", async (value) => eval(value));
unrelated.get("/admin", () => "ok");
""",
    )
    configuration = load_configuration(root, environ={}, static_only=True)

    assert extract_tool_catalog(root).tools == ()
    assert run_static_scan(configuration, uuid4(), timestamp=NOW).findings == ()


def test_typescript_prompt_flow_in_inline_tool_handler(tmp_path: Path) -> None:
    root = _typescript_target(
        tmp_path / "target",
        """
const server = new McpServer({name: "v2", version: "2"});
server.registerTool("forward", {description: "Forward."}, async () => {
  const result = await client.callTool({name: "remote"});
  const text = result.text;
  return openai.responses.create({input: text});
});
""",
    )
    configuration = load_configuration(
        root,
        environ={},
        cli_overrides={"rules": ("SENT-004",)},
        static_only=True,
    )

    findings = run_static_scan(configuration, uuid4(), timestamp=NOW).findings
    assert [finding.rule_id for finding in findings] == ["SENT-004"]


def test_typescript_classification_honors_ignores_and_rejects_mixed_root(
    tmp_path: Path,
) -> None:
    ignored = tmp_path / "ignored"
    ignored.mkdir()
    (ignored / "package.json").write_text(
        json.dumps({"dependencies": {"@modelcontextprotocol/sdk": "^1"}}),
        encoding="utf-8",
    )
    (ignored / "dist").mkdir()
    (ignored / "dist" / "server.ts").write_text("export {};\n", encoding="utf-8")
    (ignored / "types.d.ts").write_text("export type X = string;\n", encoding="utf-8")
    (ignored / "view.tsx").write_text("export const X = <div />;\n", encoding="utf-8")
    with pytest.raises(TargetError, match="unsupported target"):
        load_configuration(ignored, environ={}, static_only=True)

    mixed = _typescript_target(tmp_path / "mixed", "export {};\n")
    (mixed / "pyproject.toml").write_text(
        '[project]\nname="mixed"\nversion="0"\ndependencies=["mcp>=1"]\n',
        encoding="utf-8",
    )
    with pytest.raises(TargetError, match="mixed supported"):
        load_configuration(mixed, environ={}, static_only=True)


def test_typescript_syntax_error_is_a_target_error(tmp_path: Path) -> None:
    root = _typescript_target(tmp_path / "target", "const broken: = ;\n")
    configuration = load_configuration(root, environ={}, static_only=True)
    with pytest.raises(TargetError, match="parse TypeScript"):
        run_static_scan(configuration, uuid4(), timestamp=NOW)


def test_scan_invokes_only_semgrep_and_never_package_lifecycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _typescript_target(
        tmp_path / "target",
        'const marker = "not executed";\n',
    )
    (root / "package.json").write_text(
        json.dumps(
            {
                "scripts": {"preinstall": "touch lifecycle-marker"},
                "dependencies": {"@modelcontextprotocol/sdk": "^1"},
            }
        ),
        encoding="utf-8",
    )
    original = subprocess.run
    commands: list[tuple[str, ...]] = []
    process_timeouts: list[float] = []

    def record(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(tuple(command))
        process_timeouts.append(cast(float, kwargs["timeout"]))
        return cast(subprocess.CompletedProcess[str], original(command, **kwargs))

    monkeypatch.setattr("sentinel.static.semgrep_adapter.subprocess.run", record)
    configuration = load_configuration(root, environ={}, static_only=True)
    run_static_scan(configuration, uuid4(), timestamp=NOW)

    assert commands and all(
        Path(command[0]).stem.lower() == "semgrep" for command in commands
    )
    assert all(
        command[command.index("--timeout") + 1] == str(SEMGREP_TIMEOUT_SECONDS)
        for command in commands
    )
    assert process_timeouts and all(
        timeout > SEMGREP_TIMEOUT_SECONDS for timeout in process_timeouts
    )
    assert not (root / "lifecycle-marker").exists()


def test_typescript_init_only_replaces_permissions_and_preserves_target(
    tmp_path: Path,
) -> None:
    root = _typescript_target(
        tmp_path / "target",
        """
const server = new McpServer({name: "x", version: "1"});
server.registerTool("hello", {description: "Hello."}, async () => "ok");
""",
        sdk="server",
    )
    target = root / "sentinel.target.yaml"
    target.write_text("canary: preserve\n", encoding="utf-8")

    result = initialize_repository(root, force=True)

    assert [item.name for item in result.files] == ["sentinel.permissions.yaml"]
    assert target.read_text(encoding="utf-8") == "canary: preserve\n"
    assert "hello:" in (root / "sentinel.permissions.yaml").read_text(encoding="utf-8")
