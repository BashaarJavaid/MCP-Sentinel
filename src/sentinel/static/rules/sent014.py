"""Caller-controlled references in Git command option positions."""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from typing import Any

from sentinel.static.ast_utils import match_from_node, qualified_name
from sentinel.static.discovery import Symbol
from sentinel.static.model import RuleRunState, StaticContext, StaticMatch, TypeScriptSourceFile
from sentinel.static.path_flow import PathFlow, Value
from sentinel.static.rules.sent012 import analyze
from sentinel.static.semgrep_ast import source_range
from sentinel.static.typescript_discovery import TypeScriptSymbol, name_of
from sentinel.static.typescript_path_flow import TypeScriptPathFlow, analyze as analyze_typescript


class OptionFlow(PathFlow):
    rule_id = "SENT-014"

    def expression(
        self, symbol: Symbol, node: ast.AST | None, env: dict[str, Value]
    ) -> Value:
        value = super().expression(symbol, node, env)
        if isinstance(node, (ast.BinOp, ast.JoinedStr, ast.Subscript, ast.Attribute)):
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
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            if first.value and (not first.value.startswith("-") or "=" in first.value):
                value = replace(value, option_safe=True)
        return value

    def guard(
        self, symbol: Symbol, node: ast.AST, env: dict[str, Value], truth: bool
    ) -> None:
        super().guard(symbol, node, env, truth)
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
            for name, value in env.items():
                if value.key == checked.key:
                    env[name] = replace(value, option_safe=True)

    def call(self, symbol: Symbol, node: ast.Call, env: dict[str, Value]) -> Value:
        name = qualified_name(node.func) or ""
        if isinstance(node.func, ast.Attribute) and ".git." in name:
            receiver = self.expression(symbol, node.func.value, env)
            if receiver.repository_object:
                # Git revision/path commands accept these explicit terminators;
                # a terminator after caller input cannot protect that input.
                terminated = False
                unsafe = []
                for argument in node.args:
                    value = self.expression(symbol, argument, env)
                    if (
                        node.func.attr in {"diff", "show", "log", "checkout", "rev_parse"}
                        and isinstance(argument, ast.Constant)
                        and argument.value in {"--", "--end-of-options"}
                    ):
                        terminated = True
                    if value.sources and not value.option_safe and not terminated:
                        unsafe.append(value)
                if unsafe:
                    locations = frozenset().union(*(v.locations for v in unsafe))
                    self.state.matches.append(
                        replace(
                            match_from_node(self.rule_id, symbol.file, node, "option-flow"),
                            captures={
                                "sink_name": name,
                                "flow_locations": json.dumps(sorted(locations | {(symbol.file.relative_path, node.lineno)})),
                            },
                        )
                    )
                return Value()
        return super().call(symbol, node, env)


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
        binding = self.callables.get(self.expression(file, callee, env).key)
        external = (binding.external or "").removeprefix("node:") if binding else ""
        name = name_of(callee) or ""
        receiver = self.expression(file, callee["DotAccess"][0], env) if "DotAccess" in callee else Value()
        if external in {"simple-git", "simple-git.simpleGit", "simple-git.default"}:
            return Value(key=str(source_range(node, file)), repository_object=True)
        argv = None
        command = None
        if external in {f"child_process.{method}" for method in ("execFile", "execFileSync", "spawn", "spawnSync")} and len(argument_nodes) >= 2:
            executable = self.program.literal(TypeScriptSymbol(file, argument_nodes[0]))
            if executable in {"git", "/usr/bin/git"}:
                container = argument_nodes[1].get("Container")
                if container:
                    argv = container[1][1]
                    command = self.program.literal(TypeScriptSymbol(file, argv[0])) if argv else None
                    argv = argv[1:]
        elif receiver.repository_object:
            command = name.rsplit(".", 1)[-1]
            argv = argument_nodes
            if len(argv) == 1 and "Container" in argv[0]:
                argv = argv[0]["Container"][1][1]
            if command == "raw" and argv:
                command = self.program.literal(TypeScriptSymbol(file, argv[0]))
                argv = argv[1:]
        if argv is not None:
            unsafe = []
            terminated = False
            for argument in argv:
                literal = self.program.literal(TypeScriptSymbol(file, argument))
                if command in {"diff", "show", "log", "checkout", "rev-parse"} and literal in {"--", "--end-of-options"}:
                    terminated = True
                value = self.expression(file, argument, env)
                if value.sources and not value.option_safe and not terminated:
                    unsafe.append(value)
            if unsafe:
                location = source_range(node, file)
                locations = frozenset().union(*(v.locations for v in unsafe))
                self.state.matches.append(StaticMatch(
                    rule_id=self.rule_id, path=file.relative_path, range=location,
                    snippet=self.program.text(file, node), match_kinds=("option-flow",),
                    captures={"sink_name": name, "flow_locations": json.dumps(sorted(locations | {(file.relative_path, location.start_line)}))},
                ))
            return Value()
        result = super().call(file, node, env)
        if name.endswith(".startsWith") and len(argument_nodes) == 1 and self.program.literal(TypeScriptSymbol(file, argument_nodes[0])) == "-":
            self.conditions[result.key] = (frozenset({f"#guard:option:{receiver.key}"}), frozenset())
        if not (binding and binding.function):
            result = replace(result, option_safe=False)
        return result
