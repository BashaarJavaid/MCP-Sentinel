"""Source trees from the already pinned Semgrep parser, without target execution."""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections.abc import Iterator
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import certifi

from sentinel.errors import InfrastructureError, TargetError
from sentinel.finding import SourceRange
from sentinel.static.execution import check_deadline
from sentinel.static.model import TypeScriptSourceFile
from sentinel.static.semgrep_adapter import _verify_semgrep_version


def parse_typescript(file: TypeScriptSourceFile, *, deadline: float) -> dict[str, Any]:
    _verify_semgrep_version()
    check_deadline(deadline)
    core = Path(str(distribution("semgrep").locate_file("semgrep/bin/semgrep-core")))
    if os.name == "nt":
        core = core.with_suffix(".exe")
    try:
        result = subprocess.run(
            [
                str(core),
                "-lang",
                "typescript",
                "-json",
                "-full_token_info",
                "-dump_ast",
                str(file.path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=min(120.0, max(0.001, deadline - time.monotonic())),
            env={
                **os.environ,
                "SSL_CERT_FILE": certifi.where(),
                "SEMGREP_SEND_METRICS": "off",
                "SEMGREP_ENABLE_VERSION_CHECK": "0",
            },
        )
    except subprocess.TimeoutExpired as error:
        raise InfrastructureError(
            "static analysis exceeded its 120-second timeout"
        ) from error
    except OSError as error:
        raise InfrastructureError(
            "cannot start the installed Semgrep parser"
        ) from error
    if result.returncode:
        raise TargetError(f"cannot parse TypeScript source {file.relative_path}")
    try:
        tree = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise InfrastructureError("Semgrep returned an invalid syntax tree") from error
    if not isinstance(tree, dict) or not isinstance(tree.get("Pr"), list):
        raise InfrastructureError("Semgrep returned an unsupported syntax-tree shape")
    check_deadline(deadline)
    return tree


def tokens(tree: Any) -> Iterator[dict[str, Any]]:
    """Visit only original tokens; inferred symbol metadata is not source evidence."""
    pending = [tree]
    while pending:
        current = pending.pop()
        if isinstance(current, list):
            pending.extend(reversed(current))
        elif isinstance(current, dict):
            origin = current.get("token", {}).get("OriginTok")
            if isinstance(origin, dict):
                yield origin
            else:
                pending.extend(
                    value
                    for key, value in reversed(tuple(current.items()))
                    if not key.startswith("id_") and key not in {"pinfo", "token"}
                )


def source_range(tree: Any, file: TypeScriptSourceFile) -> SourceRange:
    locations = list(tokens(tree))
    if not locations:
        raise InfrastructureError("Semgrep syntax node has no original source location")
    raw = file.source.encode("utf-8")
    for token in locations:
        offset, spelling = token.get("bytepos"), token.get("str")
        if (
            not isinstance(offset, int)
            or offset < 0
            or not isinstance(spelling, str)
            or raw[offset : offset + len(spelling.encode())] != spelling.encode()
        ):
            raise InfrastructureError(
                "Semgrep token does not match the supplied source"
            )
    first = min(locations, key=lambda token: token["bytepos"])
    last = max(
        locations, key=lambda token: token["bytepos"] + len(token["str"].encode())
    )

    def position(offset: int) -> tuple[int, int]:
        prefix = raw[:offset].decode("utf-8")
        return prefix.count("\n") + 1, len(prefix.rsplit("\n", 1)[-1]) + 1

    start_line, start_column = position(first["bytepos"])
    end_line, end_column = position(last["bytepos"] + len(last["str"].encode()))
    return SourceRange(
        start_line=start_line,
        start_column=start_column,
        end_line=end_line,
        end_column=end_column,
    )
