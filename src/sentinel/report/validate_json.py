"""Offline validation for Sentinel's native JSON report."""

from __future__ import annotations

import json
from typing import Any

import jsonschema
from referencing import Registry, Resource

from sentinel.errors import InfrastructureError
from sentinel.schema import schema_resource

SCHEMA_BASE = "https://mcp-sentinel.invalid/schemas/"


def validate_report_data(data: Any) -> None:
    try:
        report_schema = _load_schema("report.schema.json")
        finding_schema = _load_schema("finding.schema.json")
        report_schema["$id"] = f"{SCHEMA_BASE}report.schema.json"
        finding_schema["$id"] = f"{SCHEMA_BASE}finding.schema.json"
        registry = Registry().with_resource(
            f"{SCHEMA_BASE}finding.schema.json",
            Resource.from_contents(finding_schema),
        )
        validator = jsonschema.Draft202012Validator(
            report_schema,
            registry=registry,
        )
        validator.validate(data)
    except jsonschema.ValidationError as error:
        raise InfrastructureError(
            f"native report schema validation failed: {error.message}"
        ) from error
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise InfrastructureError(
            "generated native report schemas are missing or invalid"
        ) from error


def _load_schema(name: str) -> dict[str, Any]:
    resource = schema_resource(name)
    data = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InfrastructureError(f"schema is not a JSON object: {name}")
    return data
