"""SENT-002: retain Semgrep sinks and trace same-file named Python helpers."""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import replace

from sentinel.finding import SourceRange
from sentinel.static.ast_utils import (
    discover_tool_regions,
    import_aliases,
    match_from_node,
    qualified_name,
    resolve_name,
)
from sentinel.static.execution import (
    UNKNOWN,
    Call,
    Sources,
    Summary,
    check_deadline,
    dependency_order,
    emit,
    substitute,
    union,
)
from sentinel.static.model import (
    ParsedPythonFile,
    RuleRunState,
    StaticContext,
    StaticMatch,
)

Function = ast.FunctionDef | ast.AsyncFunctionDef
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _nodes(node: ast.AST) -> Iterator[ast.AST]:
    pending = list(ast.iter_child_nodes(node))
    while pending:
        current = pending.pop()
        yield current
        if not isinstance(current, _SCOPES):
            pending.extend(ast.iter_child_nodes(current))


def _parameters(function: Function) -> tuple[str, ...]:
    args = function.args
    return tuple(
        arg.arg
        for arg in (
            *args.posonlyargs,
            *args.args,
            *args.kwonlyargs,
            *([args.vararg] if args.vararg else []),
            *([args.kwarg] if args.kwarg else []),
        )
    )


def _locals(function: Function) -> set[str]:
    names = set(_parameters(function))
    for node in _nodes(function):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(item.asname or item.name.split(".")[0] for item in node.names)
    return names


def run(
    context: StaticContext, matches: list[StaticMatch], state: RuleRunState
) -> None:
    for file in context.files.python_files:
        definitions = [node for node in file.tree.body if isinstance(node, Function)]
        counts = Counter(node.name for node in definitions)
        rebound = {
            node.id
            for statement in file.tree.body
            if not isinstance(statement, _SCOPES)
            for node in ast.walk(statement)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
        }
        rebound.update(import_aliases(file))
        functions = {
            node.name: node
            for node in definitions
            if counts[node.name] == 1 and node.name not in rebound
        }
        graph = {}
        for name, function in functions.items():
            check_deadline(context.deadline)
            shadowed = _locals(function)
            graph[name] = {
                node.func.id
                for node in _nodes(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in functions
                and node.func.id not in shadowed
            }
        summaries: dict[str, Summary] = {}
        for name in dependency_order(graph):
            summaries[name] = _Analyzer(
                file, functions, summaries, context.deadline
            ).analyze(functions[name])
        additions = RuleRunState()
        safe_ranges: set[SourceRange] = set()
        for region in discover_tool_regions(file):
            root = _Analyzer(file, functions, summaries, context.deadline).analyze(
                region.function, region.node
            )
            safe_ranges.update(
                site.range for site, sources in root.sinks if not sources
            )
            emit(root, summaries, additions, deadline=context.deadline)
        # Keep Semgrep's original location, snippet and fingerprint when both agree.
        flow_context = {
            match.range: match.captures["flow_lines"]
            for match in additions.matches
            if "flow_lines" in match.captures
        }
        state.matches.extend(
            replace(
                match,
                captures={**match.captures, "flow_lines": flow_context[match.range]},
            )
            if match.range in flow_context
            else match
            for match in matches
            if match.path == file.relative_path and match.range not in safe_ranges
        )
        state.matches.extend(additions.matches)
        state.warnings.extend(additions.warnings)


class _Analyzer:
    def __init__(
        self,
        file: ParsedPythonFile,
        functions: dict[str, Function],
        summaries: dict[str, Summary],
        deadline: float,
    ) -> None:
        self.file = file
        self.functions = functions
        self.summaries = summaries
        self.deadline = deadline
        self.aliases = import_aliases(file)
        self.summary = Summary(())
        self.shadowed: set[str] = set()

    def analyze(self, function: Function, region: ast.AST | None = None) -> Summary:
        self.summary = Summary(_parameters(function))
        self.summary.lines.add(function.lineno)
        self.shadowed = _locals(function)
        environment = {p: frozenset({p}) for p in self.summary.parameters}
        body = function.body if region is None or region is function else [region]
        self._statements(body, environment)
        return self.summary

    def _site(self, node: ast.AST) -> StaticMatch:
        return match_from_node("SENT-002", self.file, node, "python-flow")

    def _statements(self, body: Sequence[ast.AST], env: dict[str, Sources]) -> bool:
        for node in body:
            check_deadline(self.deadline)
            start = getattr(node, "lineno", 1)
            self.summary.lines.update(
                range(start, (getattr(node, "end_lineno", None) or start) + 1)
            )
            if isinstance(node, ast.Return):
                self.summary.returned |= self._expression(node.value, env)
                return False
            if isinstance(node, ast.Raise):
                self._expression(node.exc, env)
                return False
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = self._expression(node.value, env)
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if isinstance(target, ast.Name):
                        env[target.id] = value
                    else:
                        self._unsupported(node, env)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                env[node.target.id] = env.get(
                    node.target.id, UNKNOWN
                ) | self._expression(node.value, env)
            elif isinstance(node, ast.If):
                self._expression(node.test, env)
                left, right = env.copy(), env.copy()
                branches = []
                if self._statements(node.body, left):
                    branches.append(left)
                if self._statements(node.orelse, right):
                    branches.append(right)
                if not branches:
                    return False
                for name in set().union(*(branch.keys() for branch in branches)):
                    env[name] = union(branch.get(name, UNKNOWN) for branch in branches)
            elif isinstance(node, ast.Expr):
                self._expression(node.value, env)
            elif not isinstance(node, (ast.Pass, *_SCOPES)):
                self._unsupported(node, env)
        return True

    def _unsupported(self, node: ast.AST, env: dict[str, Sources]) -> Sources:
        sources = union(env.values()) | UNKNOWN
        self.summary.issues.append(
            (self._site(node), sources, f"unsupported {type(node).__name__} flow")
        )
        self.summary.returned |= sources
        for name in env:
            env[name] |= sources
        return sources

    def _expression(self, node: ast.AST | None, env: dict[str, Sources]) -> Sources:
        check_deadline(self.deadline)
        if node is None or isinstance(node, ast.Constant):
            return frozenset()
        if isinstance(node, ast.Name):
            return env.get(node.id, UNKNOWN)
        if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
            return self._call(node.value, env, awaited=True)
        if isinstance(node, ast.Call):
            return self._call(node, env)
        if isinstance(node, _SCOPES):
            return UNKNOWN
        if isinstance(
            node,
            (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.NamedExpr),
        ):
            return self._unsupported(node, env)
        return union(
            self._expression(child, env) for child in ast.iter_child_nodes(node)
        )

    def _call(
        self, node: ast.Call, env: dict[str, Sources], *, awaited: bool = False
    ) -> Sources:
        arguments = [self._expression(arg, env) for arg in node.args]
        keywords = [(kw.arg, self._expression(kw.value, env)) for kw in node.keywords]
        sources = union([*arguments, *(value for _, value in keywords)])
        name = qualified_name(node.func) or "dynamic call"
        site = self._site(node)
        if name in self.functions and name not in self.shadowed:
            function = self.functions[name]
            positional = [
                arg.arg for arg in (*function.args.posonlyargs, *function.args.args)
            ]
            bindings = dict(zip(positional, arguments, strict=False))
            valid = len(arguments) <= len(positional)
            for key, value in keywords:
                if (
                    key is None
                    or key in bindings
                    or key in {arg.arg for arg in function.args.posonlyargs}
                ):
                    valid = False
                elif key is not None:
                    bindings[key] = value
            valid = valid and set(bindings) == set(_parameters(function))
            if (
                not valid
                or function.args.vararg
                or function.args.kwarg
                or any(isinstance(arg, ast.Starred) for arg in node.args)
                or function.decorator_list
                or any(
                    isinstance(child, (ast.Yield, ast.YieldFrom))
                    for child in _nodes(function)
                )
                or (isinstance(function, ast.AsyncFunctionDef) and not awaited)
            ):
                reason = f"unresolved argument binding or deferred call to {name}"
            else:
                self.summary.calls.append(Call(site, name, bindings))
                if name in self.summaries:
                    returned = substitute(self.summaries[name].returned, bindings)
                    if not returned & UNKNOWN:
                        return returned
                    reason = f"unresolved effects or return flow through {name}"
                else:
                    reason = f"recursive return flow through {name}"
        else:
            resolved = resolve_name(name, self.aliases)
            root = name.split(".")[0]
            if root not in self.shadowed and (
                resolved
                in {
                    "eval",
                    "exec",
                    "builtins.eval",
                    "builtins.exec",
                    "pickle.loads",
                    "yaml.load",
                }
                or (
                    resolved
                    in {"subprocess.run", "subprocess.call", "subprocess.Popen"}
                    and any(
                        kw.arg == "shell"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value is True
                        for kw in node.keywords
                    )
                )
            ):
                self.summary.sinks.append(
                    (replace(site, captures={"sink_name": resolved}), sources)
                )
                return sources
            if (
                name
                in {
                    "str",
                    "bytes",
                    "int",
                    "float",
                    "bool",
                    "len",
                    "list",
                    "tuple",
                    "dict",
                    "set",
                }
                and root not in self.shadowed
            ):
                return sources
            if isinstance(node.func, ast.Attribute):
                sources |= self._expression(node.func.value, env)
            reason = f"unresolved call to {name}"
        self.summary.issues.append((site, sources, reason))
        # Unsupported calls may mutate arguments; do not certify constant outputs.
        self.summary.returned |= sources | UNKNOWN
        for variable in env:
            env[variable] |= sources | UNKNOWN
        return sources | UNKNOWN
