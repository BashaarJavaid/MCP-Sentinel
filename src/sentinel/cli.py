"""Thin Typer command shell for MCP Sentinel."""

from __future__ import annotations

import json
import os
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import typer

from sentinel import __version__
from sentinel.config import FailThreshold, OutputFormat, load_configuration
from sentinel.errors import InfrastructureError, UsageError
from sentinel.orchestrator import run_scan
from sentinel.report.console import render_console
from sentinel.report.json_report import render_json
from sentinel.report.model import ScanContext, ScanTarget
from sentinel.report.sarif import render_sarif
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data

app = typer.Typer(
    name="sentinel",
    help="Build-time security scanner for MCP servers.",
    no_args_is_help=True,
    add_completion=False,
)


class CliState:
    def __init__(self, *, debug: bool) -> None:
        self.debug = debug


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Show internal tracebacks."),
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the installed Sentinel version.",
    ),
) -> None:
    """Configure global CLI behavior."""

    del version
    ctx.obj = CliState(debug=debug)


@app.command()
def scan(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Local MCP repository path."),
    output_format: OutputFormat | None = typer.Option(None, "--format"),
    output: Path | None = typer.Option(None, "--output"),
    json_output: bool = typer.Option(False, "--json", help="Alias for --format json."),
    fail_on: FailThreshold | None = typer.Option(None, "--fail-on"),
    allow_degraded: bool = typer.Option(False, "--allow-degraded"),
    target_launch_cmd: str | None = typer.Option(None, "--target-launch-cmd"),
    static_only: bool = typer.Option(False, "--static-only"),
    rules: str | None = typer.Option(None, "--rules"),
) -> None:
    """Run static checks, required GPT review, and available later stages."""
    state = _state(ctx)
    try:
        selected_format = _select_format(output_format, json_output)
        overrides: dict[str, Any] = {
            "format": selected_format,
            "fail_on": fail_on,
            "rules": _parse_rule_tokens(rules) if rules is not None else None,
        }
        configuration = load_configuration(
            path,
            cli_overrides=overrides,
            target_launch_cmd=target_launch_cmd,
            static_only=static_only,
        )
        now = datetime.now(timezone.utc)
        context = ScanContext(
            scan_id=uuid4(),
            started_at=now,
            target=ScanTarget(display_name=configuration.scan_root.name),
        )
        outcome = run_scan(
            configuration,
            context,
            completed_at=datetime.now(timezone.utc),
            allow_degraded=allow_degraded,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        effective_format = configuration.scanner.scanner.format
        rendered = _render(outcome.report, effective_format)
        _write_report(rendered, output)
        if outcome.exit_code == 3:
            typer.echo(
                "error: analysis incomplete; see report stages and warnings",
                err=True,
            )
        raise typer.Exit(outcome.exit_code)
    except typer.Exit:
        raise
    except UsageError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error
    except InfrastructureError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(3) from error
    except Exception as error:  # defensive exit-code boundary
        if state.debug:
            traceback.print_exc()
        else:
            typer.echo(f"error: internal Sentinel failure: {error}", err=True)
        raise typer.Exit(3) from error


@app.command()
def demo(
    ctx: typer.Context,
    replay_review: bool = typer.Option(
        False,
        "--replay-review",
        help="Replay checked-in GPT responses; never represents a live call.",
    ),
) -> None:
    """Exercise the current pipeline against the vulnerable reference fixture."""

    state = _state(ctx)
    try:
        root = (
            Path(__file__).resolve().parents[2]
            / "tests"
            / "fixtures"
            / "vulnerable_server"
        )
        configuration = load_configuration(root)
        now = datetime.now(timezone.utc)
        context = ScanContext(
            scan_id=uuid4(),
            started_at=now,
            target=ScanTarget(display_name="vulnerable_server"),
        )
        outcome = run_scan(
            configuration,
            context,
            completed_at=datetime.now(timezone.utc),
            allow_degraded=False,
            review_mode="replay" if replay_review else "live",
            api_key=os.environ.get("OPENAI_API_KEY"),
            cassette_root=(
                Path(__file__).resolve().parent / "_cassettes" / "demo"
                if replay_review
                else None
            ),
        )
        if replay_review:
            typer.echo("*** RECORDED GPT REPLAY — NO LIVE MODEL CALL ***")
        typer.echo(render_console(outcome.report), nl=False)
        with tempfile.TemporaryDirectory(prefix="sentinel-phase1-demo-") as directory:
            directory_path = Path(directory)
            json_path = directory_path / "report.json"
            sarif_path = directory_path / "report.sarif"
            json_text = render_json(outcome.report)
            sarif_text = render_sarif(outcome.report)
            json_path.write_text(json_text, encoding="utf-8")
            sarif_path.write_text(sarif_text, encoding="utf-8")
            validate_report_data(json.loads(json_text))
            validate_sarif_data(json.loads(sarif_text))
            typer.echo(f"Validated temporary JSON: {json_path}")
            typer.echo(f"Validated temporary SARIF: {sarif_path}")
        typer.echo("Temporary demo reports cleaned up.")
        raise typer.Exit(outcome.exit_code)
    except typer.Exit:
        raise
    except UsageError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error
    except Exception as error:
        if state.debug:
            traceback.print_exc()
        else:
            typer.echo(f"error: internal Sentinel failure: {error}", err=True)
        raise typer.Exit(3) from error


def _state(ctx: typer.Context) -> CliState:
    state = ctx.find_root().obj
    return state if isinstance(state, CliState) else CliState(debug=False)


def _select_format(
    output_format: OutputFormat | None, json_output: bool
) -> OutputFormat | None:
    if json_output and output_format not in {None, OutputFormat.JSON}:
        raise UsageError("--json conflicts with the selected --format")
    return OutputFormat.JSON if json_output else output_format


def _parse_rule_tokens(value: str) -> tuple[str, ...]:
    tokens = tuple(token.strip() for token in value.split(","))
    if not tokens or any(not token for token in tokens):
        raise UsageError("--rules contains an empty rule token")
    return tokens


def _render(report: Any, output_format: OutputFormat) -> str:
    if output_format is OutputFormat.CONSOLE:
        return render_console(report)
    if output_format is OutputFormat.JSON:
        return render_json(report)
    if output_format is OutputFormat.SARIF:
        rendered = render_sarif(report)
        validate_sarif_data(json.loads(rendered))
        return rendered
    raise InfrastructureError(f"unsupported report format: {output_format}")


def _write_report(content: str, output: Path | None) -> None:
    if output is None:
        typer.echo(content, nl=False)
        return
    parent = output.parent
    if not parent.exists() or not parent.is_dir() or output.is_dir():
        raise UsageError(f"invalid output path: {output}")
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
    except PermissionError as error:
        raise UsageError(f"cannot write output path: {output}") from error
    except OSError as error:
        raise InfrastructureError(f"atomic report write failed: {error}") from error
