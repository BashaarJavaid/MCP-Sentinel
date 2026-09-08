"""Independent schema oracle and bounds for baseline and attack arguments."""

from __future__ import annotations

import copy
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from mcp.types import Tool
from pydantic import ValidationError

from sentinel.config import LoadedConfiguration, TargetConfig
from sentinel.dynamic.arguments import (
    InvalidBaseline,
    UnsupportedSchema,
    baseline_arguments,
    schema_errors,
    schema_validator,
)
from sentinel.dynamic.prober import (
    DEFAULT_ORDER,
    OVERSIZED_MARKER,
    ProbeBinding,
    ProbeCampaign,
    _probe_arguments,
    enumerate_attempts,
)
from sentinel.permissions import PermissionsManifest


@pytest.mark.parametrize(
    "field",
    [
        {"type": "string", "default": "example"},
        {"const": "constant"},
        {"enum": ["read", "write"]},
        {"type": "integer", "minimum": 5},
        {"type": "number", "maximum": -5},
        {"type": "boolean"},
        {"type": "null"},
        {"type": "array", "items": {"type": "integer"}, "minItems": 3},
        {
            "type": "object",
            "properties": {"name": {"const": "nested"}},
            "required": ["name"],
        },
        {"type": "string", "default": 123, "minLength": 2, "maxLength": 3},
    ],
)
def test_generated_complete_arguments_are_valid(field: dict[str, Any]) -> None:
    schema = {"type": "object", "properties": {"value": field}, "required": ["value"]}
    arguments = baseline_arguments(schema)
    assert Draft202012Validator(schema).is_valid(arguments)


@pytest.mark.parametrize(
    "dialect", ["draft-04", "draft-07", "draft/2019-09", "draft/2020-12"]
)
def test_local_references_and_supported_dialects(dialect: str) -> None:
    uri = (
        f"http://json-schema.org/{dialect}/schema#"
        if dialect.startswith("draft-")
        else f"https://json-schema.org/{dialect}/schema"
    )
    schema = {
        "$schema": uri,
        "type": "object",
        "definitions": {"Value": {"type": "string", "enum": ["local"]}},
        "properties": {"value": {"$ref": "#/definitions/Value"}},
        "required": ["value"],
    }
    assert baseline_arguments(schema) == {"value": "local"}


@pytest.mark.parametrize(
    "schema",
    [
        {"$schema": "https://example.invalid/unknown-dialect"},
        {"$ref": "https://example.invalid/schema"},
        {"$ref": "file:///etc/passwd"},
        {"$ref": "relative.json"},
        {"$dynamicRef": "https://example.invalid/schema"},
        {
            "type": "object",
            "properties": {"unused": {"$ref": "https://example.invalid/schema"}},
        },
        {"type": "invalid"},
        {"$ref": "#"},
        {"$ref": "#/missing"},
    ],
)
def test_unsupported_or_remote_schemas_never_create_a_baseline(
    schema: dict[str, Any],
) -> None:
    with pytest.raises(UnsupportedSchema):
        baseline_arguments(schema)


def test_configured_baseline_is_complete_never_merged_or_mutated() -> None:
    schema = {
        "type": "object",
        "properties": {"value": {"type": "string", "default": "generated"}},
        "required": ["value"],
    }
    configured = {"value": "configured"}
    original = copy.deepcopy(configured)
    assert baseline_arguments(schema, configured) == configured
    assert configured == original
    with pytest.raises(InvalidBaseline):
        baseline_arguments(schema, {})


@pytest.mark.parametrize("value", ["x" * 16_385, float("nan"), float("inf")])
def test_configured_baseline_bounds(
    loaded_config: LoadedConfiguration, value: Any
) -> None:
    assert loaded_config.target is not None
    data = loaded_config.target.model_dump()
    data["probe_baselines"] = {"process": {"value": value}}
    with pytest.raises(ValidationError):
        TargetConfig.model_validate(data)


def test_depth_and_generated_array_limits() -> None:
    configured: dict[str, Any] = {}
    for _ in range(9):
        configured = {"nested": configured}
    with pytest.raises(UnsupportedSchema):
        baseline_arguments({"type": "object"}, configured)
    schema = {
        "type": "object",
        "properties": {"value": {"type": "array", "minItems": 17}},
        "required": ["value"],
    }
    with pytest.raises(UnsupportedSchema):
        baseline_arguments(schema)
    # Configured arrays share depth/byte limits, not the generator's item cap.
    assert baseline_arguments(schema, {"value": [None] * 17}) == {"value": [None] * 17}


@pytest.mark.parametrize(
    ("field_schema", "keyword"),
    [
        ({"type": "string", "maxLength": 4096}, "maxLength"),
        ({"type": "array", "maxItems": 3}, "maxItems"),
        ({"type": "object", "maxProperties": 3}, "maxProperties"),
    ],
)
def test_size_mutation_violates_the_actual_declared_limit(
    field_schema: dict[str, Any], keyword: str
) -> None:
    schema = {
        "type": "object",
        "properties": {"value": field_schema},
        "required": ["value"],
    }
    tool = Tool(name="process", inputSchema=schema)
    arguments, _ = _probe_arguments(
        ProbeBinding("SENT-009", "process", "value", OVERSIZED_MARKER), (tool,)
    )
    assert keyword in {
        error.validator for error in schema_validator(schema).iter_errors(arguments)
    }


def test_schema_error_evidence_bounds_large_enum_without_losing_constraint() -> None:
    schema = {"enum": ["x" * 2000]}
    errors = schema_errors(schema_validator(schema), "different")
    assert errors[0]["keyword"] == "enum"
    assert errors[0]["constraint"]["truncated"] is True
    assert len(errors[0]["constraint"]["sha256"]) == 64


@pytest.mark.parametrize(
    "schema",
    [
        {
            "type": "object",
            "properties": {"value": {"type": ["string", "null"]}},
            "required": ["value"],
        },
        {"type": "object", "required": ["value"]},
    ],
)
def test_runtime_binding_supports_union_types_and_required_fields(
    schema: dict[str, Any],
) -> None:
    tool = Tool(name="process", inputSchema=schema)
    manifest = PermissionsManifest.model_validate(
        {"version": 1, "tools": {"process": {}}}
    )
    attempts = enumerate_attempts(
        (tool,), manifest, ProbeCampaign(DEFAULT_ORDER, (), None, True)
    )
    binding = next(item for item in attempts if item.probe_id == "SENT-011")
    arguments, _ = _probe_arguments(binding, (tool,))
    assert binding.field == "value"
    assert not Draft202012Validator(schema).is_valid(arguments)
    if "properties" in schema:
        binding = next(item for item in attempts if item.probe_id == "SENT-009")
        assert binding.field == "value"
