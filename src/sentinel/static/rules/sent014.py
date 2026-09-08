"""Caller-controlled references in Git command option positions."""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from typing import Any

from sentinel.static.ast_utils import match_from_node, qualified_name, resolve_name
from sentinel.static.discovery import Symbol, ToolBinding
from sentinel.static.execution import check_deadline
from sentinel.static.model import (
    RuleRunState,
    StaticContext,
    StaticMatch,
    TypeScriptSourceFile,
)
from sentinel.static.path_flow import PathFlow, Value, _key, combine
from sentinel.static.rules.sent012 import analyze
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import TypeScriptSymbol, name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow
from sentinel.static.typescript_path_flow import analyze as analyze_typescript

COMMAND_CALLS = frozenset(
    f"subprocess.{method}"
    for method in ("run", "Popen", "call", "check_call", "check_output")
)


class OptionFlow(PathFlow):
    rule_id = "SENT-014"

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.argv: dict[str, tuple[Value, ...]] = {}
        self.literals: dict[str, str] = {}
        self.git_commands: set[str] = set()
        self.json_containers: set[str] = set()
        self.has_command_sinks = self.command_sinks_present()

    def command_sinks_present(self) -> bool:
        from sentinel.static.lifespan import tool_lifespan

        roots: set[str] = set()
        for tool in self.program.tools():
            roots.update(
                (tool.handler.file.relative_path, tool.registration.file.relative_path)
            )
            lifespan = tool_lifespan(self.program, tool)
            if lifespan is not None:
                roots.add(lifespan.file.relative_path)
        reachable = self.program.reachable_files(roots)
        # This is a necessary syntax condition for call() below, not a claim
        # about unsupported command APIs. All files remain in the source index;
        # follow every included import from registrations, handlers and lifespans.
        for file in self.program.files:
            if file.relative_path not in reachable:
                continue
            aliases = self.aliases[file.relative_path]
            for node in ast.walk(file.tree):
                check_deadline(self.deadline)
                if isinstance(node, ast.Attribute) and node.attr == "git":
                    return True
                if (
                    isinstance(node, ast.Call)
                    and resolve_name(qualified_name(node.func) or "", aliases)
                    in COMMAND_CALLS
                ):
                    return True
        return False

    def entry(self, tool: ToolBinding, bindings: dict[str, Value]) -> None:
        if self.has_command_sinks:
            super().entry(tool, bindings)
        else:
            self.state.exempt("no supported Python command sink syntax")

    def sequence(self, values: tuple[Value, ...], identity: str) -> Value:
        result = combine(list(values), _key("argv", identity, *(v.key for v in values)))
        self.argv[result.key] = values
        return result

    def entries(self, value: Value) -> tuple[Value, ...]:
        return tuple(
            replace(item, option_safe=item.option_safe or value.option_safe)
            for item in self.argv.get(value.key, (value,))
        )

    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        super().merge(env, branches)
        unknown = Value()
        for name, value in env.items():
            variants = [branch.get(name, unknown) for branch in branches]
            sequences = [self.argv.get(v.key) for v in variants]
            if sequences and all(v is not None for v in sequences):
                # A terminator is trusted only when every path retains its order.
                if all(v == sequences[0] for v in sequences):
                    self.argv[value.key] = sequences[0] or ()
                else:
                    prefix: list[Value] = []
                    for items in zip(
                        *(sequence or () for sequence in sequences), strict=False
                    ):
                        if not all(item == items[0] for item in items):
                            break
                        prefix.append(items[0])
                    self.argv[value.key] = (
                        *(prefix or [Value()]),
                        *(
                            item
                            for sequence in sequences
                            if sequence is not None
                            for item in sequence[len(prefix) :]
                            if item.sources
                        ),
                    )

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        identity = (
            f"{symbol.file.relative_path}:{getattr(node, 'lineno', 0)}:"
            f"{getattr(node, 'col_offset', 0)}"
        )
        if isinstance(node, (ast.List, ast.Tuple)):
            values: list[Value] = []
            for item in node.elts:
                value = self.expression(symbol, item, env)
                values.extend(
                    self.entries(value) if isinstance(item, ast.Starred) else (value,)
                )
            result = self.sequence(tuple(values), identity)
            self.json_containers.add(result.key)
            return result
        if isinstance(node, ast.Starred):
            return self.expression(symbol, node.value, env)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self.expression(symbol, node.left, env)
            right = self.expression(symbol, node.right, env)
            if left.key in self.argv and right.key in self.argv:
                return self.sequence(self.entries(left) + self.entries(right), identity)
        value = super().expression(symbol, node, env)
        if isinstance(node, ast.Dict):
            self.json_containers.add(value.key)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            self.literals[value.key] = node.value
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "git"
            and value.repository_object
        ):
            self.git_commands.add(value.key)
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.slice, ast.Constant)
            and node.slice.value == 0
        ):
            parent = self.expression(symbol, node.value, env)
            entries = self.argv.get(parent.key, ())
            # ponytail: retain proven command prefixes; other indexes stay conservative.
            if entries and entries[0].key in self.literals and not entries[0].sources:
                return entries[0]
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            parent = self.expression(symbol, node.value, env)
            if parent.key in self.argv:
                try:
                    lower = (
                        ast.literal_eval(node.slice.lower) if node.slice.lower else None
                    )
                    upper = (
                        ast.literal_eval(node.slice.upper) if node.slice.upper else None
                    )
                    step = (
                        ast.literal_eval(node.slice.step) if node.slice.step else None
                    )
                    return self.sequence(
                        self.argv[parent.key][slice(lower, upper, step)], identity
                    )
                except (ValueError, TypeError):
                    pass
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            value = replace(value, option_safe=False)
        # A literal prefix fixes this argv slot's option name. This does not
        # establish safety of a dangerous option's value (e.g. --upload-pack).
        first = (
            node.values[0]
            if isinstance(node, ast.JoinedStr) and node.values
            else node.left
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            else None
        )
        if (
            isinstance(first, ast.Constant)
            and isinstance(first.value, str)
            and first.value
            and (not first.value.startswith("-") or "=" in first.value)
        ):
            value = replace(value, option_safe=True)
        return value

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        super().guard(symbol, node, env, truth)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.guard(symbol, node.operand, env, not truth)
            return
        checked = None
        if (
            not truth
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "startswith"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "-"
            and not node.keywords
        ):
            checked = self.expression(symbol, node.func.value, env)
        if (
            not truth
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "any"
            and "any" not in env
            and "any" not in self.program.bindings[symbol.file.relative_path]
            and len(node.args) == 1
            and not node.keywords
            and isinstance(node.args[0], ast.GeneratorExp)
        ):
            generator = node.args[0]
            if len(generator.generators) == 1:
                iteration = generator.generators[0]
                test = generator.elt
                if (
                    not iteration.ifs
                    and not iteration.is_async
                    and isinstance(iteration.target, ast.Name)
                    and isinstance(test, ast.Call)
                    and isinstance(test.func, ast.Attribute)
                    and isinstance(test.func.value, ast.Name)
                    and test.func.value.id == iteration.target.id
                    and test.func.attr == "startswith"
                    and len(test.args) == 1
                    and isinstance(test.args[0], ast.Constant)
                    and test.args[0].value == "-"
                    and not test.keywords
                ):
                    checked = self.expression(symbol, iteration.iter, env)
        if checked is not None:
            for name, value in env.items():
                if value.key == checked.key:
                    env[name] = replace(value, option_safe=True)

    def report(
        self,
        symbol: Symbol,
        node: ast.Call,
        command: str | None,
        arguments: tuple[Value, ...],
    ) -> None:
        terminated = False
        unsafe = []
        for value in arguments:
            literal = self.literals.get(value.key)
            if command in {
                "diff",
                "show",
                "log",
                "checkout",
                "rev-parse",
            } and literal in {"--", "--end-of-options"}:
                terminated = True
            if value.sources and not value.option_safe and not terminated:
                unsafe.append(value)
        if unsafe:
            locations = frozenset().union(*(v.locations for v in unsafe))
            self.state.matches.append(
                replace(
                    match_from_node(self.rule_id, symbol.file, node, "option-flow"),
                    captures={
                        "sink_name": qualified_name(node.func) or "command",
                        "flow_locations": json.dumps(
                            sorted(
                                locations | {(symbol.file.relative_path, node.lineno)}
                            )
                        ),
                    },
                )
            )

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        name = qualified_name(node.func) or ""
        resolved = resolve_name(name, self.aliases[symbol.file.relative_path])
        root = name.split(".")[0]
        declarations = self.program.bindings[symbol.file.relative_path].get(root, [])
        if root in env or (
            declarations
            and not (
                len(declarations) == 1
                and isinstance(declarations[0], (ast.Import, ast.ImportFrom))
            )
        ):
            resolved = ""
        receiver = (
            self.expression(symbol, node.func.value, env)
            if isinstance(node.func, ast.Attribute)
            else Value()
        )
        method = node.func.attr if isinstance(node.func, ast.Attribute) else ""
        if receiver.key in self.git_commands:
            arguments: list[Value] = []
            for argument in node.args:
                value = self.expression(symbol, argument, env)
                arguments.extend(
                    self.entries(value)
                    if isinstance(argument, ast.Starred)
                    else (value,)
                )
            self.report(symbol, node, method.replace("_", "-"), tuple(arguments))
            return Value()
        if receiver.key in self.argv:
            values = self.argv[receiver.key]
            if method == "copy" and not node.args and not node.keywords:
                return self.sequence(
                    values,
                    f"{symbol.file.relative_path}:{node.lineno}:{node.col_offset}",
                )
            if method in {"append", "extend", "insert"} and node.args:
                addition = self.expression(symbol, node.args[-1], env)
                if method == "append" and len(node.args) == 1:
                    values += (addition,)
                elif method == "extend" and len(node.args) == 1:
                    values += self.entries(addition)
                elif method == "insert" and len(node.args) == 2:
                    try:
                        index = ast.literal_eval(node.args[0])
                        updated = list(values)
                        updated.insert(index, addition)
                        values = tuple(updated)
                    except (ValueError, TypeError):
                        values = (addition, *values)
                changed = self.sequence(values, receiver.key)
                for binding, value in env.items():
                    if value.key == receiver.key:
                        env[binding] = changed
                return Value()
        if resolved in COMMAND_CALLS:
            expression = (
                node.args[0]
                if node.args
                else next((kw.value for kw in node.keywords if kw.arg == "args"), None)
            )
            value = self.expression(symbol, expression, env)
            argv = self.argv.get(value.key)
            if argv is not None:
                executable = self.literals.get(argv[0].key) if argv else None
                is_git = executable in {"git", "/usr/bin/git"}
                command = (
                    self.literals.get(argv[1].key) if is_git and len(argv) > 1 else None
                )
                self.report(
                    symbol,
                    node,
                    command,
                    argv[2:] if is_git and command is not None else argv[1:],
                )
                return Value()
        result = super().call(symbol, node, env)
        if (
            resolved == "json.dumps"
            and len(node.args) == 1
            and all(
                keyword.arg not in {None, "cls", "default"} for keyword in node.keywords
            )
            and self.expression(symbol, node.args[0], env).key in self.json_containers
        ):
            # Standard JSON containers retain an opening { or [ in this argv slot.
            return replace(result, option_safe=True)
        if method == "split" and receiver.sources:
            return self.sequence((result,), result.key)
        return result


def detect(context: StaticContext, state: RuleRunState) -> None:
    analyze(
        context.python_program,
        state,
        context.deadline,
        flow=OptionFlow(context.python_program, state, context.deadline),
    )
    if context.files.typescript_files:
        analyze_typescript(
            context.typescript_program,
            state,
            flow=TypeScriptOptionFlow(context.typescript_program, state),
        )


class TypeScriptOptionFlow(TypeScriptPathFlow):
    rule_id = "SENT-014"

    def expression(
        self, file: TypeScriptSourceFile, node: Any, env: dict[str, Value]
    ) -> Value:
        value = super().expression(file, node, env)
        if env.get(f"#guard:option:{value.key}", Value()).contained:
            value = replace(value, option_safe=True)
        return value

    def guard(self, value: Value, env: dict[str, Value], truth: bool) -> None:
        super().guard(value, env, truth)
        facts = self.condition(value)[int(truth)] or ()
        for name, current in env.items():
            if f"#guard:option:{current.key}" in facts:
                env[name] = replace(current, option_safe=True)

    def member(self, value: Value, name: str) -> Value:
        return replace(super().member(value, name), option_safe=False)

    def call(
        self, file: TypeScriptSourceFile, node: dict[str, Any], env: dict[str, Value]
    ) -> Value:
        callee, arguments = node["Call"]
        argument_nodes = [item.get("Arg", item) for item in arguments[1]]
        binding = self.callables.get(self.call_value(file, callee, env).key)
        external = (binding.external or "").removeprefix("node:") if binding else ""
        name = name_of(callee) or ""
        receiver = (
            self.receivers.get(id(callee), Value())
            if "DotAccess" in callee
            else Value()
        )
        if external in {"simple-git", "simple-git.simpleGit", "simple-git.default"}:
            return Value(
                key=_key(file.relative_path, str(source_range(node, file))),
                repository_object=True,
            )
        argv: tuple[tuple[Value, ...], ...] | None = None
        command = None
        process_call = external in {
            f"child_process.{method}"
            for method in ("execFile", "execFileSync", "spawn", "spawnSync")
        }
        args = (
            [self.call_value(file, argument, env) for argument in argument_nodes]
            if process_call or receiver.repository_object
            else []
        )
        if (
            process_call
            and len(args) >= 2
            and self.string_literals.get(args[0].key) in {"git", "/usr/bin/git"}
        ):
            argv = self.array_items(args[1], env)
            if argv is None:
                self.warning(file, node, "unresolved process argument ordering")
                state = env.get("#array:" + args[1].key, args[1])
                argv = ((Value(), replace(state, option_safe=False)),)
        elif receiver.repository_object:
            command = name.rsplit(".", 1)[-1]
            argv = self.array_items(args[0], env) if len(args) == 1 else None
            if argv is None and len(args) == 1 and args[0].key in self.arrays:
                self.warning(file, node, "unresolved Git argument ordering")
                state = env.get("#array:" + args[0].key, args[0])
                unknown = replace(state, option_safe=False)
                argv = ((Value(), unknown),) if command == "raw" else ((unknown,),)
            elif argv is None:
                argv = (tuple(args),)
        if argv is not None:
            unsafe = []
            for items in argv:
                selected_command = command
                if command is None or command == "raw":
                    selected_command = (
                        self.string_literals.get(items[0].key) if items else None
                    )
                    items = items[1:]
                terminated = False
                for value in items:
                    literal = self.string_literals.get(value.key)
                    if selected_command in {
                        "diff",
                        "show",
                        "log",
                        "checkout",
                        "rev-parse",
                    } and literal in {"--", "--end-of-options"}:
                        terminated = True
                    if value.sources and not value.option_safe and not terminated:
                        unsafe.append(value)
            if unsafe:
                location = source_range(node, file)
                locations = frozenset().union(*(v.locations for v in unsafe))
                self.state.matches.append(
                    StaticMatch(
                        rule_id=self.rule_id,
                        path=file.relative_path,
                        range=location,
                        snippet=self.program.text(file, node),
                        match_kinds=("option-flow",),
                        captures={
                            "sink_name": name,
                            "flow_locations": json.dumps(
                                sorted(
                                    locations
                                    | {(file.relative_path, location.start_line)}
                                )
                            ),
                        },
                    )
                )
            return Value()
        result = super().call(file, node, env)
        if (
            name.endswith(".startsWith")
            and len(argument_nodes) == 1
            and self.program.literal(TypeScriptSymbol(file, argument_nodes[0])) == "-"
        ):
            self.conditions[result.key] = (
                frozenset({f"#guard:option:{receiver.key}"}),
                frozenset(),
            )
        if not (binding and binding.function):
            result = replace(result, option_safe=False)
        return result
