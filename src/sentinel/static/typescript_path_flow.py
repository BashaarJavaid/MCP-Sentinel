"""Bounded containment interpretation of original Semgrep TypeScript nodes."""

from __future__ import annotations

import json
from collections.abc import Sequence
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

    def __init__(self, program: TypeScriptProgram, state: RuleRunState) -> None:
        self.program, self.state = program, state
        self.active: set[tuple[str, int, int]] = set()
        self.globals: dict[tuple[str, str], Value] = {}
        self.relative: dict[str, tuple[Value, Value, str]] = {}
        self.objects: dict[str, dict[str, Value]] = {}
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
        self.call_sites: list[TypeScriptSymbol] = []
        self.normal_exits: list[list[frozenset[str]]] = []
        self.function_effects: Facts = frozenset()

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

    def combined(self, values: list[Value]) -> Value:
        result = combine(values)
        if values and all(self.canonical(value) for value in values):
            self.normalized.add(result.key)
        if any(value.key in self.conditions for value in values):
            self.conditions[result.key] = (
                common_facts([self.condition(value)[0] for value in values]),
                common_facts([self.condition(value)[1] for value in values]),
            )
        return result

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
        exits: list[frozenset[str]] = []
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
                exits.append(self.enforced(env))
                returned.append(Value())
            self.function_effects = common_facts(exits)
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
                        self.pattern(child, self.member(value, name), env)
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
            facts = self.enforced(env)
            self.normal_exits[-1].append(facts)
            result = replace(
                value,
                key=_key(value.key, "return", *sorted(facts))
                if value.key in self.conditions or value.key in self.objects
                else value.key,
            )
            if value.key in self.conditions:
                false, true = self.condition(value)
                self.conditions[result.key] = (
                    false | facts if false is not None else None,
                    true | facts if true is not None else None,
                )
            if value.key in self.objects:
                self.objects[result.key] = self.objects[value.key]
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
            for branch, truth in ((left, True), (right, False)):
                if self.condition(value)[int(truth)] is None:
                    continue
                local = env.copy()
                self.guard(value, local, truth)
                if branch is None or self.statement(file, branch, local, returned):
                    branches.append(local)
            if not branches:
                return False
            self.merge(env, branches)
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

    def member(self, value: Value, name: str) -> Value:
        return self.objects.get(value.key, {}).get(
            name, replace(value, key=_key(value.key, name), contained=False)
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
                        self.globals[key] = self.expression(
                            symbol.file, symbol.node, {}
                        )
            return self.globals[key]
        if "Await" in node:
            return self.expression(file, node["Await"][1], env)
        if "Cast" in node:
            return self.expression(file, node["Cast"][2], env)
        if "Container" in node:
            return self.combined(
                [self.expression(file, item, env) for item in node["Container"][1][1]]
            )
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
            return self.call(file, node, env)
        if "New" in node:
            constructor = node["New"][1].get("t", {}).get("TyExpr", {})
            binding = self.callables.get(self.expression(file, constructor, env).key)
            if binding and binding.external == (
                "@modelcontextprotocol/sdk/server/mcp.js.McpServer"
            ):
                result = Value(
                    key=_key(file.relative_path, str(source_range(node, file)))
                )
                self.sdk_instances.add(result.key)
                return result
        if "Lambda" in node or "FuncDef" in node:
            value = Value(key=_key(file.relative_path, str(source_range(node, file))))
            self.callables[value.key] = TypeScriptSymbol(file, node)
            self.closures[value.key] = env
            return value
        if "Assign" in node:
            target, _, expression = node["Assign"]
            value = self.expression(file, expression, env)
            if "DotAccess" in target:
                receiver = self.expression(file, target["DotAccess"][0], env)
                self.invalidated_objects.add(receiver.key)
            self.pattern(target, value, env)
            return value
        if "DotAccess" in node:
            full_name = name_of(node)
            if full_name in env:
                return env[full_name]
            receiver, _, field = node["DotAccess"]
            parent = self.expression(file, receiver, env)
            member = name_of(field) or "?"
            value = self.member(parent, member)
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
                ),
            )
            self.objects[value.key] = fields
            return value
        return combine(
            [
                self.expression(file, child, env)
                for key, child in node.items()
                if key not in {"token", "pinfo"} and not key.startswith("id_")
            ]
        )

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        operator = callee.get("Special", [{}])[0]
        if isinstance(operator, dict) and operator.get("Op") in {"And", "Or"}:
            local = env.copy()
            args = []
            truth = operator["Op"] == "And"
            for item in arguments[1]:
                value = self.expression(file, item.get("Arg", item), local)
                args.append(value)
                if self.condition(value)[int(truth)] is None:
                    break
                self.guard(value, local, truth)
        else:
            args = [
                self.expression(file, item.get("Arg", item), env)
                for item in arguments[1]
            ]
        receiver = (
            self.expression(file, callee["DotAccess"][0], env)
            if "DotAccess" in callee
            else Value()
        )
        name = name_of(callee) or "dynamic call"
        symbol = (
            self.callables.get(self.expression(file, callee, env).key)
            if "Special" not in callee
            else None
        )
        external = (symbol.external or "").removeprefix("node:") if symbol else ""
        if (
            receiver.key in self.sdk_instances
            and receiver.key not in self.invalidated_objects
            and name.rsplit(".", 1)[-1] == "registerTool"
        ):
            self.registered(file, node, args)
            return Value()
        location = source_range(node, file)
        result = combine(args + ([receiver] if receiver.sources else []))
        result = replace(
            result,
            key=_key(file.relative_path, str(location), name, result.key),
            contained=False,
            resolved=False,
            locations=result.locations | {(file.relative_path, location.start_line)},
        )
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
            value = args[0]
            if self.rule_id == "SENT-012" and value.sources and not value.contained:
                self.state.matches.append(
                    StaticMatch(
                        rule_id="SENT-012",
                        path=file.relative_path,
                        range=location,
                        snippet=self.program.text(file, node),
                        match_kinds=("path-flow",),
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    value.locations
                                    | {(file.relative_path, location.start_line)}
                                )
                            ),
                        },
                    )
                )
            return result
        if symbol and symbol.function:
            callable_value = self.expression(file, callee, env)
            self.call_sites.append(TypeScriptSymbol(file, node))
            try:
                value = self.function(
                    symbol, args, self.closures.get(callable_value.key)
                )
                self.apply_facts(self.function_effects, env)
                return value
            finally:
                self.call_sites.pop()
        if (
            "DotAccess" in callee
            and name.rsplit(".", 1)[-1]
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
                value = self.function(callback, [receiver, Value(), receiver], env)
                method = name.rsplit(".", 1)[-1]
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
                pending.extend(self.objects.get(value.key, {}).values())
                if value.key in self.sdk_instances:
                    self.invalidated_objects.add(value.key)
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

    def registered(
        self, file: TypeScriptSourceFile, node: dict[str, Any], args: list[Value]
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

    def guard(self, value: Value, env: dict[str, Value], truth: bool) -> None:
        self.apply_facts(self.condition(value)[int(truth)], env)

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
            if not (base.resolved and target.resolved and not base.sources):
                continue
            if all(
                env.get(f"#guard:{key}:{part}", Value()).contained
                for part in ("parent", "absolute")
            ):
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
    factories: set[int] = set()
    for tool in program.tools() if entries is None else entries:
        if isinstance(tool, TypeScriptBinding) and tool.factory is not None:
            if id(tool.factory.node) not in factories:
                factories.add(id(tool.factory.node))
                flow.function(tool.factory, [])
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
