"""Fully offline SARIF 2.1.0 validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import jsonschema

from sentinel.errors import InfrastructureError, UsageError
from sentinel.schema import schema_resource


def load_sarif_schema() -> dict[str, Any]:
    resource = schema_resource("sarif-2.1.0.schema.json")
    try:
        return cast(dict[str, Any], json.loads(resource.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise InfrastructureError(
            "vendored SARIF schema is missing or invalid"
        ) from error


def validate_sarif_data(data: Any) -> None:
    try:
        jsonschema.validate(instance=data, schema=load_sarif_schema())
    except jsonschema.ValidationError as error:
        raise InfrastructureError(
            f"SARIF schema validation failed: {error.message}"
        ) from error


def validate_sarif_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise UsageError(f"SARIF input is not a file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise UsageError(f"cannot read SARIF input: {error}") from error
    validate_sarif_data(data)


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m sentinel.report.validate_sarif")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        validate_sarif_file(args.path)
    except UsageError as error:
        parser.exit(2, f"error: {error}\n")
    except InfrastructureError as error:
        parser.exit(3, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
