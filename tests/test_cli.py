"""Public CLI and exit-code tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from click import unstyle
from typer.testing import CliRunner

from sentinel.cli import _use_color, app
from sentinel.config import LoadedConfiguration
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    DynamicScanResult,
    ProbeBinding,
    ProbeCampaign,
    _Observation,
)
from sentinel.dynamic.sandbox import DependencyImage, DockerSandbox
from sentinel.errors import InfrastructureError
from sentinel.finding import Finding
from sentinel.orchestrator import ScanOutcome, run_phase1_scan
from sentinel.report.model import (
    ScanContext,
    StaticAnalysisSummary,
    StaticRuleOutcome,
    StaticRuleStatus,
)
from sentinel.static.model import StaticScanResult
from tests.conftest import make_target
from tests.test_gpt_review import _sent002_findings

runner = CliRunner()


def test_version_and_help() -> None:
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert version.stdout.strip() == "1.3.0"
    help_result = runner.invoke(app, ["scan", "--help"], terminal_width=160)
    assert help_result.exit_code == 0
    assert "--static-only" in unstyle(help_result.stdout)
    assert "--llm-model" in unstyle(help_result.stdout)
    assert "--llm-reasoning-" in unstyle(help_result.stdout)
    assert "--llm-base-url" in unstyle(help_result.stdout)
    assert "--trust-llm-endp" in unstyle(help_result.stdout)
    assert "--baseline" in unstyle(help_result.stdout)


def test_json_scan_returns_complete_exit_and_clean_stdout(target_root: Path) -> None:
    result = runner.invoke(app, ["scan", str(target_root), "--json", "--static-only"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["analysisComplete"] is True
    assert payload["findings"] == []
    assert result.stderr == ""


def test_conflicting_format_is_usage_error(target_root: Path) -> None:
    result = runner.invoke(
        app, ["scan", str(target_root), "--json", "--format", "sarif"]
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "conflicts" in result.stderr


def test_scan_cli_configures_compatible_endpoint_without_printing_url(
    target_root: Path,
) -> None:
    private = "https://private.example/openai/v1"
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--json",
            "--static-only",
            "--llm-model",
            "deployment",
            "--llm-reasoning-effort",
            "low",
            "--llm-base-url",
            private,
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["gpt_review"]["requested_model"] == "deployment"
    assert payload["gpt_review"]["reasoning_effort"] == "low"
    assert payload["gpt_review"]["endpoint_mode"] == "compatible"
    assert private not in result.stdout


def test_invalid_or_untrusted_endpoint_fails_before_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    untrusted = make_target(
        tmp_path / "untrusted",
        scanner_toml='[llm]\nmodel = "deployment"\nbase_url = "https://private.example/v1"\n',
    )

    def reject_scan(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("analysis must not start")

    monkeypatch.setattr("sentinel.cli.run_scan", reject_scan)
    result = runner.invoke(app, ["scan", str(untrusted), "--static-only"])
    assert result.exit_code == 2
    assert "requires --trust-llm-endpoint" in result.stderr

    invalid = make_target(tmp_path / "invalid")
    degraded = runner.invoke(
        app,
        [
            "scan",
            str(invalid),
            "--static-only",
            "--allow-degraded",
            "--llm-base-url",
            "http://private.example/v1",
        ],
    )
    assert degraded.exit_code == 2
    assert "configuration error:" in degraded.stderr


@pytest.mark.parametrize("flag", ["--verbose", "--color", "--no-color"])
def test_machine_formats_reject_console_presentation_options(
    target_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    flag: str,
) -> None:
    def reject_scan(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("presentation validation must happen before scanning")

    monkeypatch.setattr("sentinel.cli.run_scan", reject_scan)
    result = runner.invoke(
        app,
        ["scan", str(target_root), "--json", flag, "--static-only"],
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "require console output" in result.stderr


def test_color_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert _use_color(None) is False
    assert _use_color(True) is True
    assert _use_color(False) is False


def test_output_atomically_overwrites_named_file(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "report.json"
    output.write_text("old", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--format",
            "json",
            "--output",
            str(output),
            "--static-only",
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == ""
    assert json.loads(output.read_text(encoding="utf-8"))["findings"] == []


def test_invalid_output_parent_is_usage_error(
    target_root: Path, tmp_path: Path
) -> None:
    output = tmp_path / "missing" / "report.json"
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--format",
            "json",
            "--output",
            str(output),
            "--static-only",
        ],
    )
    assert result.exit_code == 2
    assert result.stderr.startswith("configuration error:")
    assert "invalid output path" in result.stderr


def test_baseline_cannot_collide_with_output(
    target_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "baseline.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "sentinel.cli.load_baseline", lambda _: SimpleNamespace(path=path.resolve())
    )
    result = runner.invoke(
        app,
        [
            "scan",
            str(target_root),
            "--baseline",
            str(path),
            "--output",
            str(path),
        ],
    )
    assert result.exit_code == 2
    assert "baseline and output paths must differ" in result.stderr


def test_missing_target_uses_target_error_prefix(tmp_path: Path) -> None:
    result = runner.invoke(app, ["scan", str(tmp_path / "missing")])
    assert result.exit_code == 2
    assert result.stderr.startswith("target error:")


def test_static_only_skips_target_launch_and_completes_when_clean(
    tmp_path: Path,
) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    result = runner.invoke(app, ["scan", str(target), "--static-only"])
    assert result.exit_code == 0
    assert "Status: COMPLETE" in result.stdout


def test_static_only_gpt_failure_is_fatal_or_explicitly_degraded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fake_static_scan(
        configuration: LoadedConfiguration,
        scan_id: UUID,
        *,
        timestamp: datetime,
    ) -> StaticScanResult:
        del configuration
        finding = _sent002_findings()[0].model_copy(
            update={"scan_id": scan_id, "timestamp": timestamp}
        )
        return StaticScanResult(
            findings=(finding,),
            warnings=(),
            summary=StaticAnalysisSummary(
                selected_rule_ids=("SENT-002",),
                scanned_file_count=1,
                ignored_file_count=0,
                total_matches=1,
                duration_ms=1,
                rule_outcomes=(
                    StaticRuleOutcome(
                        rule_id="SENT-002",
                        status=StaticRuleStatus.EVALUATED,
                        match_count=1,
                        exemptions_by_reason={},
                    ),
                ),
            ),
        )

    monkeypatch.setattr("sentinel.orchestrator.run_static_scan", fake_static_scan)
    target = Path(__file__).parent / "fixtures" / "vulnerable_server"
    base = ["scan", str(target), "--static-only", "--rules", "SENT-002", "--json"]

    fatal = runner.invoke(app, base)
    assert fatal.exit_code == 3
    fatal_payload = json.loads(fatal.stdout)
    assert fatal_payload["analysisComplete"] is False
    assert fatal_payload["gpt_review"]["failure_count"] == 1
    assert fatal_payload["findings"][0]["review"]["mode"] == "not_reviewed"
    fatal_guidance = (
        "OPENAI_API_KEY is not set; set it for GPT review or rerun with "
        "--rules-only for offline static analysis. Use --allow-degraded to "
        "permit unavailable review while keeping candidates fail-on eligible."
    )
    assert fatal.stderr == f"error: {fatal_guidance}\n"
    assert fatal_payload["warnings"][-1] == {
        "code": "gpt_review_unavailable",
        "message": fatal_guidance,
    }

    degraded = runner.invoke(app, [*base, "--allow-degraded"])
    assert degraded.exit_code == 1
    degraded_payload = json.loads(degraded.stdout)
    assert degraded_payload["analysisComplete"] is True
    assert degraded_payload["gpt_review"]["mode"] == "degraded"
    review = degraded_payload["findings"][0]["review"]
    assert review["mode"] == "degraded"
    assert review["reviewed_at"] is None
    assert review["applied_at"] is not None
    degraded_guidance = (
        "OPENAI_API_KEY is not set; continuing in degraded mode with rules-only "
        "candidates visible and fail-on eligible."
    )
    assert degraded.stderr == f"warning: {degraded_guidance}\n"
    assert degraded_payload["warnings"][-1] == {
        "code": "gpt_review_unavailable",
        "message": degraded_guidance,
    }

    dynamic_calls = 0

    def fake_dynamic_scan(
        sandbox: DockerSandbox,
        static_findings: tuple[Finding, ...],
        *,
        scan_id: UUID,
        timestamp: datetime,
    ) -> DynamicScanResult:
        del sandbox, static_findings, scan_id, timestamp
        nonlocal dynamic_calls
        dynamic_calls += 1
        bindings = {
            rule_id: ProbeBinding(rule_id, None, None, None)
            for rule_id in DEFAULT_ORDER
        }
        return DynamicScanResult(
            findings=(),
            warnings=(),
            image=DependencyImage("deps:test", "cache-key", True),
            campaign=ProbeCampaign(DEFAULT_ORDER, bindings, None, True),
            observations=tuple(
                _Observation(rule_id, "test", None, {}, {}, (), False)
                for rule_id in DEFAULT_ORDER
            ),
        )

    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", lambda: None)
    monkeypatch.setattr("sentinel.orchestrator.run_dynamic_scan", fake_dynamic_scan)
    normal_base = ["scan", str(target), "--rules", "SENT-002", "--json"]
    normal_fatal = runner.invoke(app, normal_base)
    assert normal_fatal.exit_code == 3
    assert normal_fatal.stderr == f"error: {fatal_guidance}\n"
    assert dynamic_calls == 0

    normal_degraded = runner.invoke(app, [*normal_base, "--allow-degraded"])
    assert normal_degraded.exit_code == 1
    assert normal_degraded.stderr == f"warning: {degraded_guidance}\n"
    assert dynamic_calls == 1


def test_launch_override_and_rule_validation(tmp_path: Path) -> None:
    target = make_target(tmp_path / "target", target_yaml="")
    result = runner.invoke(
        app,
        [
            "scan",
            str(target),
            "--target-launch-cmd",
            "python server.py",
            "--rules",
            "SENT-001,-SENT-007",
            "--static-only",
        ],
    )
    assert result.exit_code == 0
    invalid = runner.invoke(app, ["scan", str(target), "--rules", "SENT-999"])
    assert invalid.exit_code == 2


def test_orphan_reaper_failure_returns_infrastructure_exit(
    target_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_reaper() -> None:
        raise InfrastructureError("cannot list stale Sentinel containers")

    monkeypatch.setattr("sentinel.orchestrator.reap_orphans", fail_reaper)

    result = runner.invoke(app, ["scan", str(target_root)])

    assert result.exit_code == 3
    assert result.stderr.startswith("infrastructure error:")
    assert "cannot list stale Sentinel containers" in result.stderr


def test_demo_validates_and_cleans_temporary_reports(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_run_scan(
        configuration: LoadedConfiguration,
        context: ScanContext,
        *,
        completed_at: datetime,
        **kwargs: object,
    ) -> ScanOutcome:
        del kwargs
        assert configuration.scanner.scanner.rules_only is False
        assert configuration.static_only is False
        incomplete = run_phase1_scan(
            configuration,
            context,
            completed_at=completed_at,
        )
        return ScanOutcome(report=incomplete.report, exit_code=1)

    monkeypatch.setenv("SENTINEL_RULES_ONLY", "true")
    monkeypatch.setattr("sentinel.cli.run_scan", fake_run_scan)
    output_dir = tmp_path / "demo-output"
    output_dir.mkdir()
    unrelated = output_dir / "notes.txt"
    unrelated.write_text("keep", encoding="utf-8")
    result = runner.invoke(app, ["demo", "--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert "Validated JSON" in result.stdout
    assert "Validated SARIF" in result.stdout
    assert (output_dir / "report.json").is_file()
    assert (output_dir / "report.sarif").is_file()
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert "incomplete until Phase 3" not in result.stderr


def test_debug_controls_internal_tracebacks(
    target_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_load(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError("synthetic internal failure")

    monkeypatch.setattr("sentinel.cli.load_configuration", fail_load)
    concise = runner.invoke(app, ["scan", str(target_root)])
    assert concise.exit_code == 3
    assert "internal Sentinel failure" in concise.stderr
    assert "Traceback" not in concise.stderr

    debug = runner.invoke(app, ["--debug", "scan", str(target_root)])
    assert debug.exit_code == 3
    assert "Traceback" in debug.stderr
    assert "synthetic internal failure" in debug.stderr


@pytest.mark.parametrize("key", (None, "dummy-not-a-real-key"))
@pytest.mark.parametrize(
    "fixture",
    (
        "clean_server",
        "vulnerable_server",
        "typescript_clean_server",
        "typescript_vulnerable_server",
    ),
)
def test_rules_only_prohibited_paths_and_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, key: str | None, fixture: str
) -> None:
    import shutil

    from sentinel.report.validate_json import validate_report_data
    from sentinel.report.validate_sarif import validate_sarif_data

    root = tmp_path / fixture
    shutil.copytree(Path(__file__).parent / "fixtures" / fixture, root)
    (root / "sentinel.target.yaml").write_text(
        "invalid runtime config", encoding="utf-8"
    )
    cache = root / ".sentinel-cache"
    cache.mkdir()
    (cache / "existing").write_text("preserve", encoding="utf-8")
    if key:
        monkeypatch.setenv("OPENAI_API_KEY", key)

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("rules-only reached a prohibited path")

    for name in (
        "SemanticReviewer",
        "reap_orphans",
        "DockerSandbox",
        "run_dynamic_scan",
        "empty_review_outcome",
    ):
        monkeypatch.setattr(f"sentinel.orchestrator.{name}", forbidden)
    monkeypatch.setattr("socket.socket.connect", forbidden)
    monkeypatch.setattr("sentinel.llm.semantic_reviewer.AsyncOpenAI", forbidden)
    monkeypatch.setattr("sentinel.llm.semantic_reviewer.ReviewCache", forbidden)
    monkeypatch.setattr("sentinel.llm.cache.ReviewCache.read", forbidden)
    monkeypatch.setattr("sentinel.llm.cache.ReviewCache.write", forbidden)
    monkeypatch.setattr("sentinel.llm.cache.user_cache_path", lambda *args: cache)
    monkeypatch.setenv("SENTINEL_LLM_BASE_URL", "invalid")
    monkeypatch.setenv("OPENAI_BASE_URL", "invalid")
    for output_format in ("json", "sarif"):
        result = runner.invoke(
            app,
            [
                "scan",
                str(root),
                "--rules-only",
                "--format",
                output_format,
                "--static-only",
                "--allow-degraded",
                "--target-launch-cmd",
                "invalid | shell",
            ],
        )
        assert result.exit_code == (1 if "vulnerable" in fixture else 0), result.output
        payload = json.loads(result.stdout)
        if output_format == "json":
            validate_report_data(payload)
            assert payload["analysisComplete"] is True
            assert payload["gpt_review"] is None
            assert payload["dynamic_analysis"] is None
            assert all(
                f["review"] is None
                and all(p["review"] is None for p in f["provenance"])
                for f in payload["findings"]
            )
            stages = payload["stages"]
        else:
            validate_sarif_data(payload)
            stages = payload["runs"][0]["invocations"][0]["properties"]["stages"]
        assert sum(s.get("reason") == "rules-only scan requested" for s in stages) == 3
    assert (cache / "existing").read_text() == "preserve"


def test_rules_only_baseline_suppression_threshold_and_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = make_target(tmp_path / "first", target_yaml="")
    source = root / "server.py"
    source.write_text('token = "ghp_0123456789abcdefghijklmnop"\n', encoding="utf-8")
    args = ["scan", str(root), "--rules-only", "--rules", "SENT-005", "--json"]
    baseline = tmp_path / "baseline.json"
    first = runner.invoke(app, [*args, "--output", str(baseline)])
    assert first.exit_code == 1
    assert runner.invoke(app, [*args, "--baseline", str(baseline)]).exit_code == 0
    assert runner.invoke(app, [*args, "--fail-on", "critical"]).exit_code == 0
    suppressed = (
        source.read_text().rstrip()
        + " # sentinel: ignore[SENT-005] reason=test credential\n"
    )
    source.write_text(suppressed, encoding="utf-8")
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    finding = json.loads(result.stdout)["findings"][0]
    assert finding["status"] == "suppressed"
    assert finding["review"] is None
    assert finding["suppression"]["reason"] == "test credential"
    assert runner.invoke(app, [*args, "--rules", "INVALID"]).exit_code == 2
    monkeypatch.setattr(
        "sentinel.orchestrator.run_static_scan",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            InfrastructureError("engine unavailable")
        ),
    )
    assert runner.invoke(app, args).exit_code == 3


def test_cli_negative_rules_only_override(
    target_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SENTINEL_RULES_ONLY", "true")
    result = runner.invoke(
        app, ["scan", str(target_root), "--no-rules-only", "--static-only", "--json"]
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["gpt_review"] is not None
