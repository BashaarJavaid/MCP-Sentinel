"""Thin Typer command shell for MCP Sentinel."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any
from uuid import uuid4

import typer

from sentinel import __version__
from sentinel.config import FailThreshold, OutputFormat, load_configuration
from sentinel.errors import (
    ConfigurationError,
    InfrastructureError,
    TargetError,
    UsageError,
)
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
    verbose: bool = typer.Option(False, "--verbose", help="Show bounded evidence."),
    color: bool | None = typer.Option(
        None, "--color/--no-color", help="Override terminal color detection."
    ),
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
        effective_format = configuration.scanner.scanner.format
        _validate_presentation_options(effective_format, verbose, color)
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
        rendered = _render(
            outcome.report,
            effective_format,
            verbose=verbose,
            color=_use_color(color),
        )
        _write_report(rendered, output)
        if outcome.exit_code == 3:
            typer.echo(
                "error: analysis incomplete; see report stages and warnings",
                err=True,
            )
        raise typer.Exit(outcome.exit_code)
    except typer.Exit:
        raise
    except TargetError as error:
        typer.echo(f"target error: {error}", err=True)
        raise typer.Exit(2) from error
    except ConfigurationError as error:
        typer.echo(f"configuration error: {error}", err=True)
        raise typer.Exit(2) from error
    except UsageError as error:
        typer.echo(f"configuration error: {error}", err=True)
        raise typer.Exit(2) from error
    except InfrastructureError as error:
        typer.echo(f"infrastructure error: {error}", err=True)
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
    verbose: bool = typer.Option(False, "--verbose", help="Show bounded evidence."),
    color: bool | None = typer.Option(
        None, "--color/--no-color", help="Override terminal color detection."
    ),
    output_dir: Path = typer.Option(
        Path("sentinel-demo-results"),
        "--output-dir",
        help="Directory for validated JSON and SARIF reports.",
    ),
) -> None:
    """Exercise the current pipeline against the vulnerable reference fixture."""

    state = _state(ctx)
    try:
        destination = _prepare_demo_output_dir(output_dir)
        with _materialized_demo_resources() as (root, cassettes):
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
                cassette_root=cassettes if replay_review else None,
            )
        if replay_review:
            typer.echo("*** RECORDED GPT REPLAY — NO LIVE MODEL CALL ***")
        typer.echo(
            render_console(outcome.report, verbose=verbose, color=_use_color(color)),
            nl=False,
        )
        json_path = destination / "report.json"
        sarif_path = destination / "report.sarif"
        json_text = render_json(outcome.report)
        sarif_text = render_sarif(outcome.report)
        validate_report_data(json.loads(json_text))
        validate_sarif_data(json.loads(sarif_text))
        _write_report(json_text, json_path)
        _write_report(sarif_text, sarif_path)
        typer.echo(f"Validated JSON: {json_path}")
        typer.echo(f"Validated SARIF: {sarif_path}")
        raise typer.Exit(0 if outcome.exit_code in {0, 1} else outcome.exit_code)
    except typer.Exit:
        raise
    except TargetError as error:
        typer.echo(f"target error: {error}", err=True)
        raise typer.Exit(2) from error
    except ConfigurationError as error:
        typer.echo(f"configuration error: {error}", err=True)
        raise typer.Exit(2) from error
    except UsageError as error:
        typer.echo(f"configuration error: {error}", err=True)
        raise typer.Exit(2) from error
    except InfrastructureError as error:
        typer.echo(f"infrastructure error: {error}", err=True)
        raise typer.Exit(3) from error
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
        raise ConfigurationError("--json conflicts with the selected --format")
    return OutputFormat.JSON if json_output else output_format


def _parse_rule_tokens(value: str) -> tuple[str, ...]:
    tokens = tuple(token.strip() for token in value.split(","))
    if not tokens or any(not token for token in tokens):
        raise ConfigurationError("--rules contains an empty rule token")
    return tokens


def _render(
    report: Any,
    output_format: OutputFormat,
    *,
    verbose: bool = False,
    color: bool = False,
) -> str:
    if output_format is OutputFormat.CONSOLE:
        return render_console(report, verbose=verbose, color=color)
    if output_format is OutputFormat.JSON:
        return render_json(report)
    if output_format is OutputFormat.SARIF:
        rendered = render_sarif(report)
        validate_sarif_data(json.loads(rendered))
        return rendered
    raise InfrastructureError(f"unsupported report format: {output_format}")


def _validate_presentation_options(
    output_format: OutputFormat, verbose: bool, color: bool | None
) -> None:
    if output_format is not OutputFormat.CONSOLE and (verbose or color is not None):
        raise ConfigurationError(
            "--verbose and --color/--no-color require console output"
        )


def _use_color(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    if os.environ.get("NO_COLOR") is not None:
        return False
    return bool(typer.get_text_stream("stdout").isatty())


def _write_report(content: str, output: Path | None) -> None:
    if output is None:
        typer.echo(content, nl=False)
        return
    parent = output.parent
    if not parent.exists() or not parent.is_dir() or output.is_dir():
        raise ConfigurationError(f"invalid output path: {output}")
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
        raise ConfigurationError(f"cannot write output path: {output}") from error
    except OSError as error:
        raise InfrastructureError(f"atomic report write failed: {error}") from error


def _prepare_demo_output_dir(path: Path) -> Path:
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ConfigurationError(f"invalid demo output directory: {path}")
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise ConfigurationError(
            f"cannot create demo output directory: {path}"
        ) from error
    return path.resolve()


@contextmanager
def _materialized_demo_resources() -> Iterator[tuple[Path, Path]]:
    package = resources.files("sentinel")
    fixture = package.joinpath("_fixtures").joinpath("vulnerable_server")
    cassettes = package.joinpath("_cassettes").joinpath("demo")
    if not fixture.is_dir():
        source_fixture = (
            Path(__file__).resolve().parents[2]
            / "tests"
            / "fixtures"
            / "vulnerable_server"
        )
        fixture = source_fixture
    if not fixture.is_dir() or not cassettes.is_dir():
        raise InfrastructureError("installed demo fixtures or cassettes are missing")
    with tempfile.TemporaryDirectory(prefix="sentinel-demo-resources-") as directory:
        root = Path(directory)
        fixture_path = root / "vulnerable_server"
        cassette_path = root / "cassettes"
        _copy_resource_tree(fixture, fixture_path)
        _copy_resource_tree(cassettes, cassette_path)
        yield fixture_path, cassette_path


def _copy_resource_tree(source: Any, destination: Path) -> None:
    destination.mkdir()
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            _copy_resource_tree(child, target)
        else:
            with child.open("rb") as reader, target.open("wb") as writer:
                shutil.copyfileobj(reader, writer)
