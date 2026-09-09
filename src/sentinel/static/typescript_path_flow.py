"""Bounded containment interpretation of original Semgrep TypeScript nodes."""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence
from dataclasses import fields as dataclass_fields
from dataclasses import replace
from typing import Any

from sentinel.report.model import ReportWarning
from sentinel.static.execution import check_deadline
from sentinel.static.http_discovery import TypeScriptHTTPBinding
from sentinel.static.model import RuleRunState, StaticMatch, TypeScriptSourceFile
from sentinel.static.path_flow import Value, _key, combine
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import (
    TypeScriptBinding,
    TypeScriptProgram,
    TypeScriptSymbol,
    name_of,
    walk,
)

Facts = frozenset[str] | None


def all_facts(values: list[Facts]) -> Facts:
    return (
        None
        if None in values
        else frozenset().union(*(v for v in values if v is not None))
    )


def common_facts(values: Sequence[Facts]) -> Facts:
    possible = [value for value in values if value is not None]
    return frozenset.intersection(*possible) if possible else None


class TypeScriptPathFlow:
    rule_id = "SENT-012"
    state_prefixes = (
        "#instance:",
        "#array:",
        "#record:",
        "#conditional:",
        "#http-middleware:",
    )

    def __init__(self, program: TypeScriptProgram, state: RuleRunState) -> None:
        self.program, self.state = program, state
        self.active: set[tuple[str, int, int]] = set()
        self.globals: dict[tuple[str, str], Value] = {}
        self.relative: dict[str, tuple[Value, Value, str]] = {}
        self.objects: dict[str, dict[str, Value]] = {}
        self.record_roots: dict[str, str] = {}
        self.conditions: dict[str, tuple[Facts, Facts]] = {}
        self.callables: dict[str, TypeScriptSymbol] = {}
        self.invalidated_objects: set[str] = set()
        self.prefixes: dict[str, Value] = {}
        self.boundaries: dict[str, tuple[Value, Value]] = {}
        self.normalized: set[str] = set()
        self.parents: dict[str, Value] = {}
        self.closures: dict[str, dict[str, Value]] = {}
        self.root_directories: dict[str, Value] = {}
        self.sdk_instances: set[str] = set()
        self.http_instances: set[str] = set()
        self.http_sequences: dict[
            str, tuple[tuple[str | None, tuple[Value, ...]], ...]
        ] = {}
        self.http_routes: list[
            tuple[TypeScriptSourceFile, dict[str, Any], list[Value]]
        ] = []
        self.http_continuations: dict[
            str, tuple[TypeScriptSymbol, tuple[Value, ...], Value, Value]
        ] = {}
        self.http_depth = 0
        self.call_sites: list[TypeScriptSymbol] = []
        self.normal_exits: list[list[dict[str, Value]]] = []
        self.function_effects: Facts = frozenset()
        self.path_inputs: dict[str, frozenset[str]] = {}
        self.basenames: dict[str, Value] = {}
        self.origins: dict[str, frozenset[str]] = {}
        self.initial_prefixes: dict[str, tuple[frozenset[str], tuple[str, int]]] = {}
        self.classes: dict[str, TypeScriptSymbol] = {}
        self.instances: dict[str, str] = {}
        self.instance_fields: dict[str, set[str]] = {}
        self.global_members: dict[str, Value] = {}
        self.lexical_this: set[str] = set()
        self.receivers: dict[int, Value] = {}
        self.call_values: dict[int, Value] | None = None
        self.arrays: set[str] = set()
        self.array_states: dict[str, tuple[tuple[Value, ...], ...]] = {}
        self.string_literals: dict[str, str] = {}
        self.mobilecli_paths: set[str] = set()
        self.string_prefixes: dict[str, str] = {}

    def canonical(self, value: Value) -> bool:
        return value.resolved or value.key in self.normalized

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        for name in set().union(*(branch.keys() for branch in branches)):
            values = [branch.get(name, Value()) for branch in branches]
            env[name] = (
                Value(contained=all(value.contained for value in values))
                if name.startswith("#guard:")
                else self.combined(values)
            )

    def condition(self, value: Value) -> tuple[Facts, Facts]:
        return self.conditions.get(value.key, (frozenset(), frozenset()))

    def combined(self, values: list[Value], key: str = "") -> Value:
        result = combine(values, key)
        if values and all(value.key in self.array_states for value in values):
            result = self.array_state(
                tuple(items for v in values for items in self.array_states[v.key])
            )
        if any(value.key in self.mobilecli_paths for value in values):
            self.mobilecli_paths.add(result.key)
        if result.sources:
            self.origins[result.key] = frozenset().union(
                *(
                    self.origins.get(v.key, frozenset({v.key}))
                    for v in values
                    if v.sources
                )
            )
        if len({value.key for value in values}) > 1 and all(
            value.key in self.objects and value.key not in self.invalidated_objects
            for value in values
        ):
            fields = set.union(*(set(self.objects[v.key]) for v in values))
            self.objects[result.key] = {
                name: self.combined(
                    [self.objects[v.key].get(name, Value()) for v in values]
                )
                for name in fields
            }
        if values and all(self.canonical(value) for value in values):
            self.normalized.add(result.key)
            self.path_inputs[result.key] = frozenset.intersection(
                *(
                    self.path_inputs.get(value.key, frozenset({value.key}))
                    for value in values
                )
            )
        if any(value.key in self.conditions for value in values):
            self.conditions[result.key] = (
                common_facts([self.condition(value)[0] for value in values]),
                common_facts([self.condition(value)[1] for value in values]),
            )
        return result

    def array_state(self, variants: tuple[tuple[Value, ...], ...]) -> Value:
        variants = tuple(dict.fromkeys(variants))
        result = combine(
            [value for items in variants for value in items],
            _key("array-state", repr(variants)),
        )
        # ponytail: cap branch alternatives; larger arrays remain unresolved.
        if len(variants) <= 32 and all(len(items) <= 256 for items in variants):
            self.array_states[result.key] = variants
        return result

    def array_items(
        self, value: Value, env: dict[str, Value]
    ) -> tuple[tuple[Value, ...], ...] | None:
        if value.key in self.invalidated_objects:
            return None
        return self.array_states.get(env.get("#array:" + value.key, Value()).key)

    def array_value(
        self,
        file: TypeScriptSourceFile,
        node: Any,
        variants: tuple[tuple[Value, ...], ...],
        env: dict[str, Value],
    ) -> Value:
        state = self.array_state(variants)
        value = self.combined(
            [value for items in variants for value in items],
            key=_key(
                "array",
                file.relative_path,
                str(source_range(node, file)),
                *(str(source_range(call.node, call.file)) for call in self.call_sites),
            ),
        )
        self.arrays.add(value.key)
        self.mobilecli_paths.discard(value.key)
        env["#array:" + value.key] = state
        return value

    def warning(self, file: TypeScriptSourceFile, node: Any, reason: str) -> None:
        location = source_range(node, file)
        warning = ReportWarning(
            code="static_flow_unresolved",
            message=(
                f"{self.rule_id} at {file.relative_path}:{location.start_line}: "
                f"{reason}; protection is not established"
            ),
        )
        if warning not in self.state.warnings:
            self.state.warnings.append(warning)

    def function(
        self,
        symbol: TypeScriptSymbol,
        args: list[Value],
        captured: dict[str, Value] | None = None,
    ) -> Value:
        check_deadline(self.program.deadline)
        function = symbol.function
        location = source_range(symbol.node, symbol.file)
        identity = (
            symbol.file.relative_path,
            location.start_line,
            location.start_column,
        )
        if function is None or identity in self.active or len(self.active) >= 64:
            self.function_effects = frozenset()
            self.warning(symbol.file, symbol.node, "recursive or unsupported handler")
            return combine(args)
        self.active.add(identity)
        exits: list[dict[str, Value]] = []
        self.normal_exits.append(exits)
        try:
            env = dict(captured or {})
            parameters = function["fparams"][1]
            for index, parameter in enumerate(parameters):
                value = args[index] if index < len(args) else Value()
                if "Param" in parameter:
                    param = parameter["Param"]
                    if index >= len(args) and param.get("pdefault"):
                        value = self.expression(
                            symbol.file, param["pdefault"]["some"], env
                        )
                    if param.get("pname"):
                        env[param["pname"]["some"][0]] = value
                elif "ParamPattern" in parameter:
                    self.pattern(parameter["ParamPattern"], value, env)
                else:
                    self.warning(
                        symbol.file, parameter, "unsupported parameter binding"
                    )
            returned: list[Value] = []
            if self.statement(symbol.file, function["fbody"]["FBStmt"], env, returned):
                exits.append(env.copy())
                returned.append(Value())
            self.function_effects = common_facts(
                [self.enforced(exit) for exit in exits]
            )
            if captured is not None and exits:
                members: dict[str, Value] = {}
                self.merge(
                    members,
                    [
                        {
                            key: value
                            for key, value in exit.items()
                            if key.startswith(self.state_prefixes)
                        }
                        for exit in exits
                    ],
                )
                captured.update(members)
            return self.combined(returned)
        finally:
            self.normal_exits.pop()
            self.active.remove(identity)

    @staticmethod
    def enforced(env: dict[str, Value]) -> frozenset[str]:
        return frozenset(
            name
            for name, item in env.items()
            if name.startswith("#guard:") and item.contained
        )

    def pattern(self, node: Any, value: Value, env: dict[str, Value]) -> None:
        if not isinstance(node, dict):
            if isinstance(node, list):
                for child in node:
                    self.pattern(child, value, env)
            return
        name = name_of(node)
        if name:
            env[name] = value
        elif "PatTyped" in node:
            # Type names describe the binding; they are not runtime assignments.
            self.pattern(node["PatTyped"][0], value, env)
        elif "PatId" in node:
            env[node["PatId"][0][0]] = value
        elif "Record" in node:
            for field in node["Record"][1]:
                definition = field.get("F", {}).get("DefStmt")
                if definition:
                    name = name_of(definition[0]["name"])
                    child = (
                        definition[1].get("FieldDefColon", {}).get("vinit") or {}
                    ).get("some")
                    if name and child:
                        self.pattern(child, self.member(value, name, env), env)
        else:
            for key, child in node.items():
                if key not in {"token", "pinfo"} and not key.startswith("id_"):
                    self.pattern(child, value, env)

    def statement(
        self,
        file: TypeScriptSourceFile,
        node: dict[str, Any],
        env: dict[str, Value],
        returned: list[Value],
    ) -> bool:
        check_deadline(self.program.deadline)
        if "Block" in node:
            for child in node["Block"][1]:
                if not self.statement(file, child, env, returned):
                    return False
        elif "DefStmt" in node:
            entity, definition = node["DefStmt"]
            variable = definition.get("VarDef")
            if variable is not None:
                value = self.expression(
                    file, (variable.get("vinit") or {}).get("some"), env
                )
                self.pattern(entity["name"], value, env)
            elif "FuncDef" in definition:
                value = self.expression(file, definition, env)
                self.pattern(entity["name"], value, env)
        elif "ExprStmt" in node:
            self.expression(file, node["ExprStmt"][0], env)
        elif "Return" in node:
            value = self.expression(file, (node["Return"][1] or {}).get("some"), env)
            if value.sources:
                value = replace(
                    value,
                    locations=value.locations
                    | {(file.relative_path, source_range(node, file).start_line)},
                )
            facts = self.enforced(env)
            result = replace(
                value,
                key=_key(value.key, "return", *sorted(facts))
                if facts and (value.key in self.conditions or value.key in self.objects)
                else value.key,
            )
            if value.key in self.conditions:
                false, true = self.condition(value)
                self.conditions[result.key] = (
                    false | facts if false is not None else None,
                    true | facts if true is not None else None,
                )
            if value.key in self.objects:
                fields = self.object_fields(value, env).copy()
                for name, field in fields.items():
                    if (
                        facts
                        and field.key in self.conditions
                        and field.key not in self.objects
                    ):
                        guarded = replace(field, key=_key(field.key, *sorted(facts)))
                        false, true = self.condition(field)
                        self.conditions[guarded.key] = (
                            false | facts if false is not None else None,
                            true | facts if true is not None else None,
                        )
                        fields[name] = guarded
                if value.key in self.record_roots:
                    root = self.record_roots[value.key]
                    snapshot = self.record_state(root, fields)
                    previous = result
                    result = replace(result, key=_key(result.key, snapshot.key))
                    if previous.key in self.conditions:
                        self.conditions[result.key] = self.conditions[previous.key]
                    self.objects[result.key] = fields
                    self.record_roots[result.key] = root
                    env["#record:" + root] = snapshot
                else:
                    self.objects[result.key] = fields
            self.normal_exits[-1].append(env.copy())
            returned.append(result)
            return False
        elif "Throw" in node:
            self.expression(file, node["Throw"][1], env)
            return False
        elif "If" in node:
            _, condition, left, right = node["If"]
            test = condition.get("Cond", condition)
            value = self.expression(file, test, env)
            branches = []
            conditional_facts: list[Facts] = [None, None]
            for branch, truth in ((left, True), (right, False)):
                if self.condition(value)[int(truth)] is None:
                    continue
                local = env.copy()
                self.guard(value, local, truth)
                if branch is None or self.statement(file, branch, local, returned):
                    branches.append(local)
                    conditional_facts[int(truth)] = self.enforced(local)
            if not branches:
                return False
            self.merge(env, branches)
            if value.sources and any(
                facts and facts - self.enforced(env) for facts in conditional_facts
            ):
                marker = Value(
                    key=_key("conditional", value.key, repr(conditional_facts))
                )
                self.conditions[marker.key] = (
                    conditional_facts[0],
                    conditional_facts[1],
                )
                env["#conditional:" + value.key] = marker
        elif "Try" in node:
            _, body, handlers, otherwise, final = node["Try"]
            branches, final_states = [], []
            success = env.copy()
            alive = self.statement(file, body, success, returned)
            if otherwise:
                alive = (
                    self.statement(file, otherwise["some"][1], success, returned)
                    and alive
                )
            if alive:
                branches.append(success)
            final_states.append(success)
            for _, _, body in handlers:
                failure = env.copy()
                if self.statement(file, body, failure, returned):
                    branches.append(failure)
                final_states.append(failure)
            self.merge(env, branches or final_states)
            if final and not self.statement(file, final["some"][1], env, returned):
                return False
            return bool(branches)
        elif "For" in node and "ForEach" in node["For"][1]:
            _, header, body = node["For"]
            pattern, _, iterable = header["ForEach"]
            local = env.copy()
            self.pattern(pattern, self.expression(file, iterable, env), local)
            self.statement(file, body, local, returned)
            self.merge(env, [env.copy(), local])
        elif "While" in node:
            _, condition, body = node["While"]
            value = self.expression(file, condition.get("Cond", condition), env)
            branches = []
            for truth in (False, True):
                if self.condition(value)[int(truth)] is None:
                    continue
                local = env.copy()
                self.guard(value, local, truth)
                if not truth or self.statement(file, body, local, returned):
                    branches.append(local)
                    if truth:
                        # ponytail: one iteration; extend for loop-carried state.
                        self.warning(
                            file, node, "later while-loop iterations unresolved"
                        )
            if not branches:
                return False
            self.merge(env, branches)
        elif "Switch" in node:
            _, condition, cases = node["Switch"]
            self.expression(file, condition, env)
            branches = []
            has_default = False
            for case in cases:
                if "CasesAndBody" not in case:
                    self.warning(file, case, "unsupported dispatch branch")
                    branches.append(env.copy())
                    continue
                labels, body = case["CasesAndBody"]
                has_default |= any("Default" in label for label in labels)
                local = env.copy()
                if self.statement(file, body, local, returned):
                    branches.append(local)
            if not has_default:
                branches.append(env.copy())
            if not branches:
                return False
            self.merge(env, branches)
        else:
            self.warning(file, node, "unsupported control flow")
            self.expression(file, node, env)
        return True

    def class_members(
        self, symbol: TypeScriptSymbol
    ) -> dict[tuple[str, bool], dict[str, Any]] | None:
        definition = symbol.node["ClassDef"]
        if (
            definition.get("cextends")
            or definition.get("cmixins")
            or any(
                attribute.get("KeywordAttr", [None])[0] not in {"Export", "Default"}
                for attribute in self.program.class_attributes.get(id(symbol.node), [])
            )
        ):
            return None
        members = {}
        for field in definition["cbody"][1]:
            declaration = field.get("F", {}).get("DefStmt")
            if not declaration:
                return None
            entity, body = declaration
            name = name_of(entity["name"])
            attributes = [
                a.get("KeywordAttr", [None])[0] for a in entity.get("attrs", [])
            ]
            if (
                name is None
                or any(
                    a not in {"Static", "Public", "Private", "Protected", "Readonly"}
                    for a in attributes
                )
                or not (body.keys() & {"FuncDef", "VarDef"})
            ):
                return None
            key = (name, "Static" in attributes)
            if key in members:
                return None
            if (
                name == "constructor"
                and "FuncDef" in body
                and (
                    any(part.get("Return", [None, None])[1] for part in walk(body))
                    or any(
                        parameter.get("Param", {}).get("pattrs")
                        for parameter in body["FuncDef"]["fparams"][1]
                    )
                )
            ):
                return None
            members[key] = body
        return members

    def instance_marker(self, value: Value, name: str) -> str:
        self.instance_fields.setdefault(value.key, set()).add(name)
        return "#instance:" + _key(value.key, name)

    def initialize_fields(
        self,
        value: Value,
        symbol: TypeScriptSymbol,
        members: dict[tuple[str, bool], dict[str, Any]],
        env: dict[str, Value],
        *,
        static: bool,
    ) -> None:
        for (name, is_static), definition in members.items():
            if is_static == static and "VarDef" in definition:
                local = {**env, "this": value}
                initialized = self.expression(
                    symbol.file,
                    (definition["VarDef"].get("vinit") or {}).get("some"),
                    local,
                )
                env.update(
                    (k, v)
                    for k, v in local.items()
                    if k.startswith(self.state_prefixes)
                )
                env[self.instance_marker(value, name)] = initialized

    def invalidate(self, value: Value) -> None:
        self.invalidated_objects.update(
            (value.key, self.record_roots.get(value.key, value.key))
        )

    def record_state(self, root: str, fields: dict[str, Value]) -> Value:
        attributes = dataclass_fields(Value)
        value = combine(
            list(fields.values()),
            _key(
                root,
                json.dumps(
                    {
                        name: {
                            attribute.name: getattr(field, attribute.name)
                            for attribute in attributes
                        }
                        for name, field in fields.items()
                    },
                    sort_keys=True,
                    default=sorted,
                ),
            ),
        )
        self.objects[value.key] = fields
        return value

    def object_fields(self, value: Value, env: dict[str, Value]) -> dict[str, Value]:
        root = self.record_roots.get(value.key, value.key)
        current = env.get("#record:" + root, value)
        return self.objects.get(current.key, {})

    def member(self, value: Value, name: str, env: dict[str, Value]) -> Value:
        field = self.object_fields(value, env).get(
            name, replace(value, key=_key(value.key, name), contained=False)
        )
        return (
            replace(
                field,
                key=_key("invalidated", value.key, name),
                contained=False,
                url_checks=frozenset(),
                credential_present=False,
            )
            if {value.key, self.record_roots.get(value.key, value.key)}
            & self.invalidated_objects
            else field
        )

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        check_deadline(self.program.deadline)
        if isinstance(node, list):
            return combine([self.expression(file, child, env) for child in node])
        if not isinstance(node, dict):
            return Value()
        if "L" in node:
            result = Value(key=json.dumps(node["L"], sort_keys=True))
            literal = self.program.literal(TypeScriptSymbol(file, node))
            if isinstance(literal, str):
                self.string_literals[result.key] = literal
                self.string_prefixes[result.key] = literal
                if literal == "mobilecli":
                    self.mobilecli_paths.add(result.key)
            boolean = node["L"].get("Bool")
            if boolean:
                self.conditions[result.key] = (
                    (None, frozenset())
                    if str(boolean[0]).lower() == "true"
                    else (frozenset(), None)
                )
            return result
        if "N" in node:
            name = name_of(node) or ""
            if name in env:
                return env[name]
            key = (file.relative_path, name)
            if key not in self.globals:
                self.globals[key] = Value(key=_key(*key))
                symbol = self.program.resolve(file, name)
                if symbol:
                    if symbol.external or symbol.function:
                        self.callables[self.globals[key].key] = symbol
                    else:
                        local: dict[str, Value] = {}
                        self.globals[key] = self.expression(
                            symbol.file, symbol.node, local
                        )
                        self.global_members.update(
                            (k, v)
                            for k, v in local.items()
                            if k.startswith(self.state_prefixes)
                        )
            pending = [self.globals[key]]
            seen: set[str] = set()
            while pending:
                value = pending.pop()
                if value.key in seen:
                    continue
                seen.add(value.key)
                if value.key in self.arrays:
                    marker = "#array:" + value.key
                    if marker in self.global_members:
                        env.setdefault(marker, self.global_members[marker])
                if value.key in self.http_instances:
                    marker = "#http-middleware:" + value.key
                    if marker in self.global_members:
                        env.setdefault(marker, self.global_members[marker])
                for field in tuple(self.instance_fields.get(value.key, ())):
                    marker = self.instance_marker(value, field)
                    if marker in self.global_members:
                        env.setdefault(marker, self.global_members[marker])
                        pending.append(env[marker])
            return self.globals[key]
        if "ClassDef" in node:
            symbol = TypeScriptSymbol(file, node)
            members = self.class_members(symbol)
            value = Value(
                key=_key("class", file.relative_path, str(source_range(node, file)))
            )
            if members is None:
                self.warning(
                    file, node, "unsupported class inheritance, decorators or members"
                )
                return value
            self.classes[value.key] = symbol
            self.initialize_fields(value, symbol, members, env, static=True)
            return value
        if "Await" in node:
            return self.expression(file, node["Await"][1], env)
        if "Cast" in node:
            return self.expression(file, node["Cast"][2], env)
        if "Container" in node:
            items = tuple(
                self.expression(file, item, env) for item in node["Container"][1][1]
            )
            if node["Container"][0] == "Array":
                return self.array_value(file, node, (items,), env)
            return self.combined(list(items))
        if "Conditional" in node:
            test, left, right = node["Conditional"]
            condition = self.expression(file, test, env)
            values = []
            for branch, truth in ((left, True), (right, False)):
                if self.condition(condition)[int(truth)] is None:
                    continue
                local = env.copy()
                self.guard(condition, local, truth)
                values.append(self.expression(file, branch, local))
            return self.combined(values)
        if "Call" in node:
            previous = self.call_values
            self.call_values = {}
            try:
                return self.call(file, node, env)
            finally:
                self.call_values = previous
        if "New" in node:
            constructor = node["New"][1].get("t", {}).get("TyExpr", {})
            class_value = self.expression(file, constructor, env)
            binding = self.callables.get(class_value.key)
            if binding and binding.external == (
                "@modelcontextprotocol/sdk/server/mcp.js.McpServer"
            ):
                result = Value(
                    key=_key(file.relative_path, str(source_range(node, file)))
                )
                self.sdk_instances.add(result.key)
                return result
            if (
                class_value.key in self.classes
                and class_value.key not in self.invalidated_objects
            ):
                symbol = self.classes[class_value.key]
                members = self.class_members(symbol)
                assert members is not None
                value = Value(
                    key=_key(
                        "instance",
                        file.relative_path,
                        str(source_range(node, file)),
                        *(
                            str(source_range(call.node, call.file))
                            for call in self.call_sites
                        ),
                    )
                )
                self.instances[value.key] = class_value.key
                args = [
                    self.expression(file, arg.get("Arg", arg), env)
                    for arg in node["New"][3][1]
                ]
                self.initialize_fields(value, symbol, members, env, static=False)
                constructor_body = members.get(("constructor", False))
                if constructor_body:
                    captured = {**env, "this": value}
                    self.call_sites.append(TypeScriptSymbol(file, node))
                    try:
                        self.function(
                            TypeScriptSymbol(symbol.file, constructor_body),
                            args,
                            captured,
                        )
                    finally:
                        self.call_sites.pop()
                    env.update(
                        (k, v)
                        for k, v in captured.items()
                        if k.startswith(self.state_prefixes)
                    )
                return value
        if "Lambda" in node or "FuncDef" in node:
            value = Value(key=_key(file.relative_path, str(source_range(node, file))))
            self.callables[value.key] = TypeScriptSymbol(file, node)
            self.closures[value.key] = env
            if (node.get("Lambda") or {}).get("fkind", [None])[0] == "Arrow":
                self.lexical_this.add(value.key)
            return value
        if "Assign" in node:
            target, _, expression = node["Assign"]
            value = self.expression(file, expression, env)
            access = target.get("DotAccess", target.get("ArrayAccess"))
            if access:
                receiver = self.expression(file, access[0], env)
                assigned_field = (
                    name_of(access[2])
                    if "DotAccess" in target
                    else self.string_literals.get(
                        self.expression(file, access[1][1], env).key
                    )
                )
                if (
                    receiver.key in self.record_roots
                    and assigned_field != "__proto__"
                    and assigned_field
                ):
                    root = self.record_roots[receiver.key]
                    updated = {
                        **self.object_fields(receiver, env),
                        assigned_field: value,
                    }
                    env["#record:" + root] = self.record_state(root, updated)
                    return value
                if "ArrayAccess" in target or assigned_field == "__proto__":
                    if receiver.key in self.arrays:
                        marker = "#array:" + receiver.key
                        env[marker] = combine([env.get(marker, receiver), value])
                    self.invalidate(receiver)
                    self.warning(
                        file, target, "computed or prototype member assignment"
                    )
                    return value
                if "http:request" in receiver.sources and assigned_field:
                    env[self.instance_marker(receiver, assigned_field)] = value
                    return value
                class_key = self.instances.get(receiver.key, receiver.key)
                if class_key in self.classes and assigned_field:
                    members = self.class_members(self.classes[class_key]) or {}
                    definition = members.get(
                        (assigned_field, receiver.key in self.classes), {}
                    )
                    if "FuncDef" not in definition:
                        env[self.instance_marker(receiver, assigned_field)] = value
                        return value
                self.invalidate(receiver)
            self.pattern(target, value, env)
            return value
        if "ArrayAccess" in node:
            receiver, index = node["ArrayAccess"]
            parent = self.expression(file, receiver, env)
            index_value = self.expression(file, index[1], env)
            member = self.string_literals.get(index_value.key)
            if parent.key in self.record_roots and member is not None:
                return self.member(parent, member, env)
            return combine([parent, index_value])
        if "DotAccess" in node:
            full_name = name_of(node)
            if full_name in env:
                return env[full_name]
            receiver, _, field = node["DotAccess"]
            parent = self.expression(file, receiver, env)
            self.receivers[id(node)] = parent
            member = name_of(field) or "?"
            if "http:request" in parent.sources:
                if parent.key in self.invalidated_objects:
                    parent = replace(parent, key=_key("invalidated", parent.key))
                marker = self.instance_marker(parent, member)
                if marker in env:
                    return env[marker]
            class_key = self.instances.get(parent.key, parent.key)
            if class_key in self.classes:
                value = env.get(
                    self.instance_marker(parent, member),
                    Value(key=_key(parent.key, member)),
                )
                if {parent.key, class_key} & self.invalidated_objects:
                    self.warning(file, node, "class receiver escapes or is replaced")
                    return replace(
                        value, key=_key("invalidated", value.key), contained=False
                    )
                symbol = self.classes[class_key]
                member_definition = (self.class_members(symbol) or {}).get(
                    (member, parent.key in self.classes)
                )
                if member_definition and "FuncDef" in member_definition:
                    self.callables[value.key] = TypeScriptSymbol(
                        symbol.file, member_definition
                    )
                return value
            value = self.member(parent, member, env)
            binding = self.callables.get(parent.key)
            if parent.key not in self.invalidated_objects:
                if binding and binding.external:
                    self.callables[value.key] = TypeScriptSymbol(
                        file, node, binding.external + "." + member
                    )
                elif full_name and full_name.split(".")[0] not in env:
                    symbol = self.program.resolve(file, full_name)
                    if symbol and (symbol.function or symbol.external):
                        self.callables[value.key] = symbol
            else:
                self.callables.pop(value.key, None)
            return value
        if "Record" in node:
            fields: dict[str, Value] = {}
            for field in node["Record"][1]:
                definition = field.get("F", {}).get("DefStmt")
                if definition:
                    field_name = name_of(definition[0]["name"])
                    if field_name:
                        fields[field_name] = self.expression(
                            file,
                            (
                                definition[1].get("FieldDefColon", {}).get("vinit")
                                or {}
                            ).get("some"),
                            env,
                        )
            value = combine(
                list(fields.values()),
                _key(
                    file.relative_path,
                    str(source_range(node, file)),
                    *(v.key for v in fields.values()),
                    *(
                        str(source_range(site.node, site.file))
                        for site in self.call_sites
                    ),
                ),
            )
            self.objects[value.key] = fields
            if len(fields) == len(node["Record"][1]) and all(
                "FieldDefColon" in field.get("F", {}).get("DefStmt", [{}, {}])[1]
                for field in node["Record"][1]
            ):
                self.record_roots[value.key] = value.key
                env["#record:" + value.key] = value
            return value
        return combine(
            [
                self.expression(file, child, env)
                for key, child in node.items()
                if key not in {"token", "pinfo"} and not key.startswith("id_")
            ]
        )

    def call_value(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        """Reuse actual callee/argument evaluation within one call only."""
        if self.call_values is not None and id(node) in self.call_values:
            return self.call_values[id(node)]
        value = self.expression(file, node, env)
        if self.call_values is not None:
            self.call_values[id(node)] = value
        return value

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        if (
            callee.get("OtherExpr", [[None]])[0][0] == "Delete"
            and len(arguments[1]) == 1
        ):
            target = arguments[1][0].get("Arg", {})
            access = target.get("DotAccess", target.get("ArrayAccess"))
            if access:
                receiver = self.expression(file, access[0], env)
                if "ArrayAccess" in target:
                    self.expression(file, access[1][1], env)
                self.invalidate(receiver)
                self.warning(file, node, "member deletion invalidates receiver")
                return Value()
        callable_value = (
            self.call_value(file, callee, env) if "Special" not in callee else Value()
        )
        receiver = (
            self.receivers.get(id(callee), Value())
            if "DotAccess" in callee
            else Value()
        )
        symbol = self.callables.get(callable_value.key)
        operator = callee.get("Special", [{}])[0]
        logical_returns: list[tuple[Value, dict[str, Value]]] | None = None
        if isinstance(operator, dict) and operator.get("Op") in {"And", "Or"}:
            local = env.copy()
            args = []
            logical_returns = []
            truth = operator["Op"] == "And"
            for index, item in enumerate(arguments[1]):
                value = self.call_value(file, item.get("Arg", item), local)
                args.append(value)
                if index == len(arguments[1]) - 1:
                    logical_returns.append((value, local.copy()))
                elif self.condition(value)[int(not truth)] is not None:
                    terminal = local.copy()
                    self.guard(value, terminal, not truth)
                    logical_returns.append((value, terminal))
                if self.condition(value)[int(truth)] is None:
                    break
                self.guard(value, local, truth)
        else:
            args = [
                self.call_value(file, item.get("Arg", item), env)
                for item in arguments[1]
            ]
        name = name_of(callee) or "dynamic call"
        external = (symbol.external or "").removeprefix("node:") if symbol else ""
        if callable_value.key in self.http_continuations:
            if args:
                self.warning(file, node, "HTTP next(error/route) forwarding unresolved")
                return Value()
            origin, next_callbacks, request, response = self.http_continuations[
                callable_value.key
            ]
            return self.http_chain(origin, next_callbacks, request, response, env)
        if external in {"express.default", "express.Router", "express.default.Router"}:
            instance = Value(
                key=_key(
                    file.relative_path,
                    str(source_range(node, file)),
                    *(
                        str(source_range(site.node, site.file))
                        for site in self.call_sites
                    ),
                )
            )
            if instance.key in self.http_instances:
                return instance
            self.http_instances.add(instance.key)
            self.objects[instance.key] = {}
            layout = Value(key=_key(instance.key, "http-middleware"))
            self.http_sequences[layout.key] = ()
            env["#http-middleware:" + instance.key] = layout
            return instance
        if (
            receiver.key in self.http_instances
            and receiver.key not in self.invalidated_objects
            and name.rsplit(".", 1)[-1] not in self.objects.get(receiver.key, {})
        ):
            http_method = name.rsplit(".", 1)[-1]
            marker = "#http-middleware:" + receiver.key
            previous = env.get(marker, Value())
            sequence = self.http_sequences.get(previous.key)
            if http_method == "use":
                prefix = self.string_literals.get(args[0].key) if args else None
                callbacks = args[1:] if prefix is not None else args
                if (
                    prefix is None
                    and callbacks
                    and not (
                        callbacks[0].key in self.callables
                        or callbacks[0].key in self.arrays
                    )
                ):
                    self.warning(file, node, "unresolved HTTP middleware or mount path")
                    callbacks = [Value()]
                callbacks = self.http_callbacks(callbacks, env)
                layout = Value(
                    key=_key(previous.key, str(prefix), *(v.key for v in callbacks))
                )
                if sequence is not None and callbacks:
                    self.http_sequences[layout.key] = (
                        *sequence,
                        (prefix, tuple(callbacks)),
                    )
                env[marker] = layout
                return receiver
            if (
                http_method
                in {"get", "post", "put", "patch", "delete", "head", "options", "all"}
                and args
            ):
                callbacks = []
                route = self.string_literals.get(args[0].key)
                if sequence is None:
                    callbacks.append(Value())
                for prefix, layers in sequence or ():
                    if prefix is None:
                        callbacks.extend(layers)
                    elif route is None or any(char in prefix for char in ":*?+()[]{}"):
                        callbacks.append(Value())
                    elif route == prefix or route.startswith(prefix.rstrip("/") + "/"):
                        callbacks.extend(layers)
                self.http_registered(
                    file,
                    node,
                    [args[0], *callbacks, *self.http_callbacks(args[1:], env)],
                )
                return receiver
        if (
            receiver.key in self.sdk_instances
            and receiver.key not in self.invalidated_objects
            and name.rsplit(".", 1)[-1] == "registerTool"
        ):
            self.registered(file, node, args, env)
            return Value()
        location = source_range(node, file)
        result = combine(
            [value for value, _ in logical_returns]
            if logical_returns is not None
            else args + ([receiver] if receiver.sources else [])
        )
        result = replace(
            result,
            key=_key(file.relative_path, str(location), name, result.key),
            contained=False,
            resolved=False,
            locations=result.locations | {(file.relative_path, location.start_line)},
        )
        if logical_returns is not None:
            tainted_returns = [(v, state) for v, state in logical_returns if v.sources]
            if tainted_returns and all(
                state.get("#guard:lexical:" + v.key, Value()).contained
                for v, state in tainted_returns
            ):
                env["#guard:lexical:" + result.key] = Value(contained=True)
        if result.sources:
            self.origins[result.key] = frozenset().union(
                *(
                    self.origins.get(value.key, frozenset({value.key}))
                    for value in [*args, receiver]
                    if value.sources
                )
            )
        if (
            isinstance(operator, dict)
            and operator.get("ConcatString") == "InterpolatedConcat"
            and args
            and not result.sources
        ):
            prefix = self.string_prefixes.get(args[0].key)
            if prefix is not None:
                self.string_prefixes[result.key] = prefix
        if (
            external == "path.join"
            and len(args) >= 4
            and [self.string_literals.get(v.key) for v in args[-4:-1]]
            == ["@mobilenext", "mobilecli", "bin"]
            and self.string_prefixes.get(args[-1].key, "").startswith("mobilecli-")
            and not result.sources
        ):
            self.mobilecli_paths.add(result.key)
        if (
            external
            in {
                "child_process.spawn",
                "child_process.spawnSync",
                "child_process.execFile",
                "child_process.execFileSync",
            }
            and len(args) >= 2
            and args[0].key in self.mobilecli_paths
            and not args[0].sources
        ):
            variants = self.array_items(args[1], env)
            if variants is None:
                self.warning(file, node, "unresolved recording argument ordering")
            for items in variants or ():
                if (
                    not items
                    or self.string_literals.get(items[0].key) != "screenrecord"
                ):
                    continue
                index = 1
                output = None
                seen_flags: set[str] = set()
                while index < len(items):
                    flag = self.string_literals.get(items[index].key)
                    if flag in seen_flags:
                        self.warning(file, node, "repeated recording option unresolved")
                        break
                    if flag is not None:
                        seen_flags.add(flag)
                    if flag == "--silent":
                        index += 1
                    elif flag in {
                        "--device",
                        "--output",
                        "--time-limit",
                    } and index + 1 < len(items):
                        if flag == "--output":
                            output = items[index + 1]
                        index += 2
                    else:
                        self.warning(file, node, "unresolved recording option position")
                        break
                else:
                    if output is not None:
                        self.path_sink(
                            file,
                            node,
                            env,
                            output,
                            name,
                            cli_output="mobilecli screenrecord --output",
                        )
            return result
        if receiver.key in self.arrays:
            variants = self.array_items(receiver, env)
            method = name_of(callee.get("DotAccess", [None, None, {}])[2])
            if variants is not None and method == "push":
                env["#array:" + receiver.key] = self.array_state(
                    tuple((*items, *args) for items in variants)
                )
                return Value()
            if variants is not None and method == "slice" and not args:
                return self.array_value(file, node, variants, env)
        if external in {
            "fs.realpath",
            "fs.realpathSync",
            "fs/promises.realpath",
            "fs.promises.realpath",
        }:
            if args and args[0].key in self.parents:
                self.parents[result.key] = self.parents[args[0].key]
            return replace(result, resolved=True)
        if (
            external
            in {
                "path.normalize",
                "path.resolve",
            }
            and len(args) == 1
            and self.canonical(args[0])
        ):
            return replace(args[0], locations=result.locations)
        if external == "path.resolve":
            self.normalized.add(result.key)
            if len(args) == 1:
                self.path_inputs[result.key] = self.path_inputs.get(
                    args[0].key, frozenset({args[0].key})
                )
        if external == "path.basename" and len(args) == 1:
            self.basenames[result.key] = args[0]
        if external == "path.join" and len(args) == 2:
            parent = self.parents.get(args[0].key)
            basename = self.basenames.get(args[1].key)
            if parent and basename and parent.key == basename.key and args[0].resolved:
                self.normalized.add(result.key)
                self.path_inputs[result.key] = self.path_inputs.get(
                    parent.key, frozenset({parent.key})
                )
        if (
            name.endswith(".toLowerCase")
            and not args
            and self.canonical(receiver)
            and env.get("#guard:platform:win32", Value()).contained
        ):
            return receiver
        if external == "path.dirname" and len(args) == 1 and self.canonical(args[0]):
            self.parents[result.key] = args[0]
        if (
            name == "Promise.all"
            and "Promise" not in env
            and "Promise" not in self.program.bindings[file.relative_path]
            and len(args) == 1
        ):
            return args[0]
        if (
            external in {"path.relative", "path/posix.relative", "path/win32.relative"}
            and len(args) == 2
        ):
            self.relative[result.key] = (args[0], args[1], external.rsplit(".", 1)[0])
        operator = callee.get("Special", [{}])[0]
        if isinstance(operator, dict) and operator.get("Op") == "Not" and args:
            false, true = self.condition(args[0])
            self.conditions[result.key] = (true, false)
        elif isinstance(operator, dict) and operator.get("Op") in {"And", "Or"}:
            conditions = [self.condition(value) for value in args]
            if operator["Op"] == "And":
                self.conditions[result.key] = (
                    common_facts([v[0] for v in conditions]),
                    all_facts([v[1] for v in conditions]),
                )
            else:
                self.conditions[result.key] = (
                    all_facts([v[0] for v in conditions]),
                    common_facts([v[1] for v in conditions]),
                )
        if (
            isinstance(operator, dict)
            and operator.get("Op") == "Plus"
            and len(args) == 2
        ):
            separator = self.callables.get(args[1].key)
            if separator and separator.external in {"path.sep", "node:path.sep"}:
                self.prefixes[result.key] = args[0]
        if (
            isinstance(operator, dict)
            and operator.get("Op") in {"PhysEq", "NotPhysEq"}
            and len(args) == 2
        ):
            raw = [argument.get("Arg", argument) for argument in arguments[1]]
            if (
                name_of(raw[0]) == "process.platform"
                and "process" not in env
                and "process" not in self.program.bindings[file.relative_path]
                and self.program.literal(TypeScriptSymbol(file, raw[1])) == "win32"
            ):
                pair: tuple[Facts, Facts] = (
                    frozenset(),
                    frozenset({"#guard:platform:win32"}),
                )
                self.conditions[result.key] = (
                    pair if operator["Op"] == "PhysEq" else pair[::-1]
                )
            target, base = args if args[0].sources else list(reversed(args))
            for directory, separator_value in (args, list(reversed(args))):
                binding = self.callables.get(separator_value.key)
                if (
                    binding
                    and binding.external in {"path.sep", "node:path.sep"}
                    and self.canonical(directory)
                    and not directory.sources
                ):
                    fact = f"#guard:root:{directory.key}"
                    self.root_directories[fact] = directory
                    self.conditions[result.key] = (
                        (frozenset(), frozenset({fact}))
                        if operator["Op"] == "PhysEq"
                        else (frozenset({fact}), frozenset())
                    )
            if (
                target.sources
                and self.canonical(target)
                and self.canonical(base)
                and not base.sources
            ):
                fact = f"#guard:boundary:{base.key}:{target.key}"
                self.boundaries[fact] = (base, target)
                facts = frozenset({fact})
                self.conditions[result.key] = (
                    (frozenset(), facts)
                    if operator["Op"] == "PhysEq"
                    else (facts, frozenset())
                )
        if (
            name.endswith(".startsWith")
            and len(args) == 1
            and args[0].key in self.prefixes
        ):
            base = self.prefixes[args[0].key]
            if self.canonical(receiver) and self.canonical(base) and not base.sources:
                fact = f"#guard:boundary:{base.key}:{receiver.key}"
                self.boundaries[fact] = (base, receiver)
                self.conditions[result.key] = (frozenset(), frozenset({fact}))
        if name.endswith(".startsWith") and len(args) == 1:
            if (
                receiver.sources
                and self.canonical(receiver)
                and self.canonical(args[0])
                and not args[0].sources
            ):
                fact = f"#guard:initial-prefix:{args[0].key}:{receiver.key}"
                self.initial_prefixes[fact] = (
                    self.origins.get(receiver.key, frozenset({receiver.key})),
                    (file.relative_path, location.start_line),
                )
                self.conditions[result.key] = (frozenset(), frozenset({fact}))
            separator = self.callables.get(args[0].key)
            if (
                separator
                and separator.external in {"path.sep", "node:path.sep"}
                and self.canonical(receiver)
            ):
                root_facts: set[str] = set()
                for root_fact, base in self.root_directories.items():
                    if env.get(root_fact, Value()).contained:
                        fact = f"#guard:boundary:{base.key}:{receiver.key}"
                        self.boundaries[fact] = (base, receiver)
                        root_facts.add(fact)
                self.conditions[result.key] = (frozenset(), frozenset(root_facts))
        if (
            name.endswith(".startsWith")
            and len(args) == 1
            and "DotAccess" in callee
            and receiver.key in self.relative
        ):
            argument = arguments[1][0].get("Arg", {})
            if self.program.literal(TypeScriptSymbol(file, argument)) == "..":
                self.conditions[result.key] = (
                    frozenset({f"#guard:{receiver.key}:parent"}),
                    frozenset(),
                )
        if (
            external
            in {"path.isAbsolute", "path/posix.isAbsolute", "path/win32.isAbsolute"}
            and len(args) == 1
            and args[0].key in self.relative
            and self.relative[args[0].key][2] == external.rsplit(".", 1)[0]
        ):
            self.conditions[result.key] = (
                frozenset({f"#guard:{args[0].key}:absolute"}),
                frozenset(),
            )
        if (
            external.rsplit(".", 1)[0] in {"fs", "fs/promises", "fs.promises"}
            and external.rsplit(".", 1)[-1]
            in {
                "readFile",
                "readFileSync",
                "writeFile",
                "writeFileSync",
                "appendFile",
                "appendFileSync",
                "open",
                "openSync",
                "readdir",
                "readdirSync",
                "unlink",
                "unlinkSync",
                "rm",
                "rmSync",
                "mkdir",
                "mkdirSync",
                "createReadStream",
                "createWriteStream",
            }
            and args
        ):
            self.path_sink(file, node, env, args[0], name)
            return result
        if symbol and symbol.function:
            self.call_sites.append(TypeScriptSymbol(file, node))
            try:
                captured = {
                    **self.closures.get(callable_value.key, {}),
                    **{
                        key: value
                        for key, value in env.items()
                        if key.startswith(("#guard:", *self.state_prefixes))
                    },
                }
                if callable_value.key not in self.lexical_this:
                    captured.pop("this", None)
                if "DotAccess" in callee and (
                    receiver.key in self.instances or receiver.key in self.classes
                ):
                    captured["this"] = receiver
                value = self.function(
                    symbol,
                    args,
                    captured,
                )
                env.update(
                    (k, v)
                    for k, v in captured.items()
                    if k.startswith(self.state_prefixes)
                )
                self.apply_facts(self.function_effects, env)
                return value
            finally:
                self.call_sites.pop()
        if (
            "DotAccess" in callee
            and name_of(callee["DotAccess"][2])
            in {
                "map",
                "flatMap",
                "forEach",
                "filter",
                "some",
                "every",
                "find",
            }
            and arguments[1]
        ):
            callback_node = arguments[1][0].get("Arg")
            callback = self.callables.get(args[0].key) if args else None
            callback = callback or (
                self.program.resolve_node(file, callback_node)
                if callback_node
                else None
            )
            if callback and callback.function:
                captured = {**self.closures.get(args[0].key, env)}
                if args[0].key not in self.lexical_this:
                    captured.pop("this", None)
                value = self.function(callback, [receiver, Value(), receiver], captured)
                env.update(
                    (k, v)
                    for k, v in captured.items()
                    if k.startswith(self.state_prefixes)
                )
                method = name_of(callee["DotAccess"][2])
                if method == "some":
                    self.conditions[result.key] = (
                        frozenset(),
                        self.condition(value)[1],
                    )
                elif method == "every":
                    # Empty arrays satisfy every without running its callback.
                    self.conditions[result.key] = (
                        self.condition(value)[0],
                        frozenset(),
                    )
                elif method in {"filter", "find"}:
                    return receiver
                elif method in {"map", "flatMap"}:
                    # Array truthiness does not establish callback boolean guards.
                    if self.canonical(value):
                        self.normalized.add(result.key)
                    return replace(value, key=result.key)
                return result
        if "Special" not in callee:
            pending = [receiver, *args]
            seen: set[str] = set()
            while pending:
                value = pending.pop()
                if value.key in seen:
                    continue
                seen.add(value.key)
                pending.extend(self.object_fields(value, env).values())
                if (
                    value.key in self.objects
                    or value.key in self.instances
                    or value.key in self.classes
                    or value.key in self.arrays
                    or "http:request" in value.sources
                ):
                    self.invalidate(value)
                if value.key in self.sdk_instances:
                    self.invalidate(value)
                    self.warning(
                        file, node, "SDK instance escapes to an unresolved call"
                    )
        if result.sources and not (
            external.startswith(("path.", "path/posix.", "path/win32."))
            or "Special" in callee
            or name.endswith(".startsWith")
        ):
            self.warning(file, node, f"unresolved call to {name}")
        return result

    def path_sink(
        self,
        file: TypeScriptSourceFile,
        node: dict[str, Any],
        env: dict[str, Value],
        value: Value,
        name: str,
        *,
        cli_output: str = "",
    ) -> None:
        location = source_range(node, file)
        if self.rule_id == "SENT-012" and value.sources and not value.contained:
            origins = self.origins.get(value.key, frozenset({value.key}))
            prefix_locations = {
                location
                for fact, (checked, location) in self.initial_prefixes.items()
                if origins <= checked and env.get(fact, Value()).contained
            }
            self.state.matches.append(
                StaticMatch(
                    rule_id="SENT-012",
                    path=file.relative_path,
                    range=location,
                    snippet=self.program.text(file, node),
                    match_kinds=("path-flow",),
                    captures={
                        "sink_name": name,
                        **({"cli_output": cli_output} if cli_output else {}),
                        **(
                            {"containment_gap": "physical"}
                            if env.get(f"#guard:lexical:{value.key}", Value()).contained
                            else {"containment_gap": "after-prefix"}
                            if prefix_locations
                            else {}
                        ),
                        "flow_locations": json.dumps(
                            sorted(
                                value.locations
                                | prefix_locations
                                | {(file.relative_path, location.start_line)}
                            )
                        ),
                    },
                )
            )

    def registered(
        self,
        file: TypeScriptSourceFile,
        node: dict[str, Any],
        args: list[Value],
        env: dict[str, Value],
    ) -> None:
        if len(args) != 3:
            self.warning(file, node, "unsupported registration arguments")
            return
        callback = self.callables.get(args[2].key)
        if callback is None or callback.function is None:
            self.warning(file, node, "unresolved registered callback")
            return
        origin = self.call_sites[0] if self.call_sites else TypeScriptSymbol(file, node)
        location = source_range(origin.node, origin.file)
        self.state.visit(origin.file.relative_path, location)
        caller = Value(
            sources=frozenset({"tool:arguments"}),
            key=_key(origin.file.relative_path, str(location), args[0].key),
            locations=frozenset(
                (site.file.relative_path, source_range(site.node, site.file).start_line)
                for site in [*self.call_sites, TypeScriptSymbol(file, node)]
            ),
        )
        self.function(callback, [caller, Value()], self.closures.get(args[2].key))

    def http_callbacks(self, values: list[Value], env: dict[str, Value]) -> list[Value]:
        pending = list(reversed(values))
        callbacks: list[Value] = []
        # ponytail: flatten at most 256 entries; larger layouts stay unresolved.
        for _ in range(256):
            if not pending:
                return callbacks
            value = pending.pop()
            if value.key not in self.arrays:
                callbacks.append(value)
                continue
            variants = self.array_items(value, env)
            if variants is not None and len(variants) == 1:
                pending.extend(reversed(variants[0]))
            else:
                callbacks.append(Value())
        return [*callbacks, Value()]

    def http_registered(
        self, file: TypeScriptSourceFile, node: dict[str, Any], args: list[Value]
    ) -> None:
        if len(args) < 2:
            self.warning(file, node, "unsupported HTTP middleware sequence")
            return
        self.http_routes.append((file, node, args))

    def http_initialize(self, initializer: TypeScriptSymbol) -> None:
        start = len(self.http_routes)
        if initializer.function is not None:
            self.function(initializer, [])
        else:
            env: dict[str, Value] = {}
            for statement in initializer.node.get("Pr", []):
                if statement.keys() & {
                    "DefStmt",
                    "ExprStmt",
                    "Block",
                    "If",
                    "Try",
                    "Switch",
                    "For",
                    "While",
                    "Throw",
                }:
                    alive = self.statement(initializer.file, statement, env, [])
                    self.globals.update(
                        ((initializer.file.relative_path, name), value)
                        for name, value in env.items()
                        if not name.startswith("#") and "." not in name
                    )
                    self.global_members.update(
                        (key, value)
                        for key, value in env.items()
                        if key.startswith(self.state_prefixes)
                    )
                    if not alive:
                        break
        routes = self.http_routes[start:]
        del self.http_routes[start:]
        if not routes:
            return
        memo: dict[int, object] = {
            id(self.program): self.program,
            id(self.state): self.state,
        }
        memo.update((id(file), file) for file in self.program.files.values())
        memo.update(
            (id(node), node)
            for tree in self.program.trees.values()
            for node in walk(tree)
        )
        for file, node, args in routes:
            fork = copy.deepcopy(self, memo.copy())
            location = source_range(node, file)
            self.state.visit(file.relative_path, location)
            caller = Value(
                sources=frozenset({"http:request"}),
                key=_key(file.relative_path, str(location), "http-request"),
                locations=frozenset({(file.relative_path, location.start_line)}),
            )
            fork.http_chain(
                TypeScriptSymbol(file, node), tuple(args[1:]), caller, Value(), {}
            )

    def http_chain(
        self,
        origin: TypeScriptSymbol,
        callbacks: tuple[Value, ...],
        request: Value,
        response: Value,
        env: dict[str, Value],
    ) -> Value:
        check_deadline(self.program.deadline)
        if not callbacks:
            return Value()
        # ponytail: cap synchronous next chains; longer chains remain unresolved.
        if self.http_depth >= 32:
            self.warning(origin.file, origin.node, "HTTP continuation depth limit")
            return Value()
        for _index, callback in enumerate(callbacks):
            check_deadline(self.program.deadline)
            handler = self.callables.get(callback.key)
            if (
                handler is not None
                and handler.function is not None
                and callback.key not in self.invalidated_objects
                and len(handler.function["fparams"][1]) != 4
            ):
                break
            self.warning(
                origin.file, origin.node, "unresolved HTTP middleware/callback"
            )
            self.invalidate(request)
            env = {}
        else:
            return Value()
        remaining = callbacks[_index + 1 :]
        request = replace(
            request,
            locations=request.locations
            | {
                (
                    handler.file.relative_path,
                    source_range(handler.node, handler.file).start_line,
                )
            },
        )
        next_value = Value(key=_key(request.key, callback.key, str(len(remaining))))
        self.http_continuations[next_value.key] = (
            origin,
            tuple(remaining),
            request,
            response,
        )
        captured = {
            **self.closures.get(callback.key, {}),
            **{
                key: value
                for key, value in env.items()
                if key.startswith(("#guard:", *self.state_prefixes))
            },
        }
        active = self.active
        self.active = set()
        self.http_depth += 1
        try:
            return self.function(handler, [request, response, next_value], captured)
        finally:
            self.http_depth -= 1
            self.active = active

    def guard(self, value: Value, env: dict[str, Value], truth: bool) -> None:
        self.apply_facts(self.condition(value)[int(truth)], env)
        conditional = env.get("#conditional:" + value.key)
        if conditional is not None and value.key not in self.invalidated_objects:
            self.apply_facts(self.condition(conditional)[int(truth)], env)

    def apply_facts(self, facts: Facts, env: dict[str, Value]) -> None:
        for fact in facts or ():
            env[fact] = Value(contained=True)
        for fact, (base, target) in self.boundaries.items():
            if env.get(fact, Value()).contained:
                for name, current in env.items():
                    if current.key == target.key and target.resolved:
                        env[name] = replace(current, contained=True)
                original = self.parents.get(target.key)
                if (
                    target.resolved
                    and original
                    and env.get(
                        f"#guard:boundary:{base.key}:{original.key}", Value()
                    ).contained
                ):
                    for name, current in env.items():
                        if current.key == original.key:
                            env[name] = replace(current, contained=True)
        for key, (base, target, _) in self.relative.items():
            if not (
                self.canonical(base) and self.canonical(target) and not base.sources
            ):
                continue
            if all(
                env.get(f"#guard:{key}:{part}", Value()).contained
                for part in ("parent", "absolute")
            ):
                for original_key in self.path_inputs.get(
                    target.key, frozenset({target.key})
                ):
                    env[f"#guard:lexical:{original_key}"] = Value(contained=True)
                if base.resolved and target.resolved:
                    for name, current in env.items():
                        if current.key == target.key:
                            env[name] = replace(current, contained=True)


def analyze(
    program: TypeScriptProgram,
    state: RuleRunState,
    *,
    flow: TypeScriptPathFlow | None = None,
    entries: tuple[TypeScriptBinding | TypeScriptHTTPBinding, ...] | None = None,
) -> None:
    flow = flow or TypeScriptPathFlow(program, state)
    factories: set[tuple[bool, int]] = set()
    for tool in program.tools() if entries is None else entries:
        initializer = (
            tool.initializer
            if isinstance(tool, TypeScriptHTTPBinding)
            else tool.factory
        )
        if initializer is not None:
            identity = (isinstance(tool, TypeScriptHTTPBinding), id(initializer.node))
            if identity not in factories:
                factories.add(identity)
                if isinstance(tool, TypeScriptHTTPBinding):
                    type(flow)(program, state).http_initialize(initializer)
                else:
                    flow.function(initializer, [])
            continue
        location = source_range(tool.registration.node, tool.registration.file)
        state.visit(tool.registration.file.relative_path, location)
        handler = tool.handler
        if handler is None or handler.function is None:
            flow.warning(
                tool.registration.file,
                tool.registration.node,
                "unresolved tool handler",
            )
            continue
        state.visit(
            handler.file.relative_path, source_range(handler.node, handler.file)
        )
        args = [
            Value(
                sources=frozenset(
                    {
                        "http:request"
                        if isinstance(tool, TypeScriptHTTPBinding)
                        else str(index)
                    }
                )
                if index == 0
                else frozenset(),
                key=f"{handler.file.relative_path}:{location}:{index}",
                locations=frozenset(
                    {(tool.registration.file.relative_path, location.start_line)}
                ),
            )
            for index, _ in enumerate(handler.function["fparams"][1])
        ]
        flow.function(handler, args)
    state.warnings.extend(program.warnings)
