"""Bounded baseline generation and offline runtime-schema validation."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

from sentinel.config import validate_baseline_bounds


class UnsupportedSchema(ValueError):
    """The bounded generator/validator cannot establish a sound attempt."""


class InvalidBaseline(ValueError):
    """A configured example does not satisfy the runtime schema."""


def schema_validator(schema: dict[str, Any]) -> Validator:
    """Use installed dialects, with no filesystem or network schema retrieval."""
    try:
        if len(json.dumps(schema, allow_nan=False).encode()) > 1_048_576:
            raise UnsupportedSchema("runtime schema exceeds 1 MiB")
        cls = (
            validator_for(schema, default=None)  # type: ignore[arg-type]
            if "$schema" in schema
            else Draft202012Validator
        )
        if cls is None:
            raise UnsupportedSchema("unsupported declared JSON Schema dialect")
        cls.check_schema(schema)
        _check_references(schema)
        return cls(schema, registry=Registry())
    except (SchemaError, RecursionError, TypeError, ValueError) as error:
        if isinstance(error, UnsupportedSchema):
            raise
        raise UnsupportedSchema(
            "invalid or excessively recursive runtime schema"
        ) from error


def _check_references(schema: Any, depth: int = 0) -> None:
    if depth > 64:
        raise UnsupportedSchema("runtime schema exceeds supported nesting")
    if not isinstance(schema, dict):
        return
    for keyword in ("$ref", "$dynamicRef", "$recursiveRef"):
        ref = schema.get(keyword)
        if ref is not None and (not isinstance(ref, str) or not ref.startswith("#")):
            raise UnsupportedSchema("only local schema references are supported")
    for key in (
        "properties",
        "patternProperties",
        "$defs",
        "definitions",
        "dependentSchemas",
    ):
        for child in schema.get(key, {}).values():
            _check_references(child, depth + 1)
    for key in ("allOf", "anyOf", "oneOf", "prefixItems"):
        for child in schema.get(key, []):
            _check_references(child, depth + 1)
    for key in (
        "items",
        "additionalItems",
        "additionalProperties",
        "contains",
        "not",
        "if",
        "then",
        "else",
        "unevaluatedItems",
        "unevaluatedProperties",
        "propertyNames",
    ):
        child = schema.get(key)
        for item in child if isinstance(child, list) else [child]:
            _check_references(item, depth + 1)
    for child in schema.get("dependencies", {}).values():
        if isinstance(child, dict):
            _check_references(child, depth + 1)


def schema_errors(validator: Validator, arguments: Any) -> list[dict[str, Any]]:
    try:
        errors = []
        for error in validator.iter_errors(arguments):
            constraint = error.validator_value
            encoded = json.dumps(constraint, sort_keys=True).encode()
            if len(encoded) > 1024:
                constraint = {
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                    "truncated": True,
                }
            errors.append(
                {
                    "keyword": error.validator,
                    "constraint": constraint,
                    "schema_path": list(error.absolute_schema_path),
                    "instance_path": list(error.absolute_path),
                    "measured_size": len(error.instance)
                    if isinstance(error.instance, (str, list, dict))
                    and error.validator in {"maxLength", "maxItems", "maxProperties"}
                    else None,
                }
            )
            if len(errors) == 16:
                break
        return errors
    except (Unresolvable, RecursionError) as error:
        raise UnsupportedSchema(
            "unresolved or recursive local schema reference"
        ) from error


def resolve_schema(schema: Any, root: dict[str, Any]) -> dict[str, Any]:
    """Resolve local generation/binding references; validation is authoritative."""
    seen: set[str] = set()
    while isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#") or ref in seen:
            raise UnsupportedSchema("unresolved or recursive local schema reference")
        seen.add(ref)
        try:
            resource = Resource.from_contents(root, default_specification=DRAFT202012)
            resolved = (
                Registry().with_resource("", resource).resolver().lookup(ref).contents
            )
        except (Unresolvable, ValueError) as error:
            raise UnsupportedSchema("unresolved local schema reference") from error
        # Sibling constraints are still checked by the complete validator.
        schema = resolved
    if schema is True:
        return {}
    if not isinstance(schema, dict):
        raise UnsupportedSchema("schema cannot generate an argument")
    return schema


def baseline_arguments(
    schema: dict[str, Any], configured: dict[str, Any] | None = None
) -> dict[str, Any]:
    validator = schema_validator(schema)
    if configured is not None:
        arguments = copy.deepcopy(configured)
    else:
        arguments = _generate(schema, schema, validator, 0)
    if not isinstance(arguments, dict):
        raise UnsupportedSchema("tool arguments must be an object")
    try:
        validate_baseline_bounds(arguments)
    except ValueError as error:
        raise UnsupportedSchema(str(error)) from error
    if configured is None:
        pending: list[Any] = [arguments]
        while pending:
            value = pending.pop()
            if isinstance(value, list):
                if len(value) > 16:
                    raise UnsupportedSchema("generated arrays are limited to 16 items")
                pending.extend(value)
            elif isinstance(value, dict):
                pending.extend(value.values())
    if schema_errors(validator, arguments):
        if configured is not None:
            raise InvalidBaseline(
                "configured baseline does not satisfy the runtime schema"
            )
        raise UnsupportedSchema("cannot generate a valid baseline for this schema")
    return arguments


def _generate(
    schema: Any, root: dict[str, Any], validator: Validator, depth: int
) -> Any:
    if depth > 8:
        raise UnsupportedSchema("generated baseline exceeds depth 8")
    schema = resolve_schema(schema, root)
    for candidate in [
        schema[key] for key in ("default", "const") if key in schema
    ] + schema.get("enum", []):
        if not schema_errors(validator.evolve(schema=schema), candidate):
            return copy.deepcopy(candidate)
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = kind[0] if kind else None
    if kind == "object" or (kind is None and "properties" in schema):
        properties = schema.get("properties", {})
        return {
            name: _generate(properties.get(name, {}), root, validator, depth + 1)
            for name in schema.get("required", [])
        }
    if kind == "array":
        size = schema.get("minItems", 0)
        if size > 16:
            raise UnsupportedSchema("generated arrays are limited to 16 items")
        items = schema.get("items", {})
        prefix = schema.get("prefixItems", items if isinstance(items, list) else [])
        return [
            _generate(
                prefix[i] if i < len(prefix) else items, root, validator, depth + 1
            )
            for i in range(size)
        ]
    if kind == "string":
        length = max(schema.get("minLength", 0), min(8, schema.get("maxLength", 8)))
        if length > 16_384:
            raise UnsupportedSchema("generated string exceeds baseline size limit")
        return ("sentinel" * (length // 8 + 1))[:length]
    if kind in {"integer", "number"}:
        value = max(1, schema.get("minimum", 1))
        exclusive = schema.get("exclusiveMinimum")
        if isinstance(exclusive, (int, float)) and not isinstance(exclusive, bool):
            value = max(value, math.floor(exclusive) + 1)
        elif exclusive is True:
            value += 1
        value = min(value, schema.get("maximum", value))
        return math.ceil(value) if kind == "integer" else value
    if kind == "boolean":
        return False
    if kind == "null" or not schema:
        return None
    raise UnsupportedSchema("schema requires a configured baseline example")
