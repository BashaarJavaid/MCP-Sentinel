"""Recover callback fields forwarded through local registration helpers."""

from __future__ import annotations

import ast
from collections import defaultdict

from sentinel.static.ast_utils import (
    import_aliases,
    qualified_name,
    resolve_name,
    scope_nodes,
)
from sentinel.static.discovery import Function, PythonProgram, Symbol
from sentinel.static.execution import check_deadline


class RegistrationFlow:
    def __init__(self, program: PythonProgram) -> None:
        self.program = program
        self.incomplete = False
        self.calls: dict[ast.AST, list[Symbol]] | None = None

    def callers(self, function: ast.AST) -> list[Symbol]:
        if self.calls is None:
            self.calls = defaultdict(list)
            for file in self.program.files:
                for node in ast.walk(file.tree):
                    if isinstance(node, ast.Call):
                        name = qualified_name(node.func)
                        if name:
                            context = Symbol(file, name, node)
                            target = self.program.resolve_in(context, name)
                            if target and isinstance(target.node, Function):
                                self.calls[target.node].append(context)
        return self.calls.get(function, [])

    def values(
        self,
        context: Symbol,
        node: ast.AST | None,
        seen: frozenset[tuple[str, int]] = frozenset(),
    ) -> tuple[Symbol, ...]:
        check_deadline(self.program.deadline)
        if node is None:
            self.incomplete = True
            return ()
        identity = (context.file.relative_path, id(node))
        if identity in seen or len(seen) >= 64:
            self.incomplete = True
            return ()
        seen = seen | {identity}
        context = Symbol(context.file, context.name, node)
        if isinstance(node, (ast.List, ast.Tuple)):
            return tuple(
                v for item in node.elts for v in self.values(context, item, seen)
            )
        if isinstance(node, Function):
            return (context,)
        if isinstance(node, ast.Name):
            owner: ast.AST | None = node
            while owner is not None:
                parent = self.program.parents.get(owner)
                if (
                    isinstance(parent, (ast.For, ast.AsyncFor))
                    and isinstance(parent.target, ast.Name)
                    and parent.target.id == node.id
                ):
                    return self.values(context, parent.iter, seen)
                if isinstance(owner, Function):
                    params = [
                        *owner.args.posonlyargs,
                        *owner.args.args,
                        *owner.args.kwonlyargs,
                    ]
                    names = [arg.arg for arg in params]
                    if node.id in names:
                        values: list[Symbol] = []
                        for caller in self.callers(owner):
                            call = caller.node
                            assert isinstance(call, ast.Call)
                            argument = next(
                                (kw.value for kw in call.keywords if kw.arg == node.id),
                                None,
                            )
                            position = names.index(node.id)
                            if argument is None and position < len(call.args):
                                argument = call.args[position]
                            values.extend(self.values(caller, argument, seen))
                        return tuple(values)
                    assignments = [
                        part
                        for part in scope_nodes(owner)
                        if isinstance(part, ast.Name)
                        and isinstance(part.ctx, ast.Store)
                        and part.id == node.id
                    ]
                    if assignments:
                        if len(assignments) != 1:
                            self.incomplete = True
                            return ()
                        assignment = self.program.parents[assignments[0]]
                        if isinstance(assignment, (ast.Assign, ast.AnnAssign)):
                            return self.values(context, assignment.value, seen)
                        self.incomplete = True
                        return ()
                owner = parent
            binding = self.program.resolve_in(context, node.id)
            if binding and isinstance(binding.node, Function):
                return (binding,)
            self.incomplete = True
            return ()
        if isinstance(node, ast.Call):
            name = qualified_name(node.func)
            target = self.program.resolve_in(context, name) if name else None
            if (
                target
                and isinstance(target.node, Function)
                and not target.node.decorator_list
            ):
                return tuple(
                    v
                    for statement in scope_nodes(target.node)
                    if isinstance(statement, ast.Return)
                    for v in self.values(target, statement.value, seen)
                )
            if target and self.fields(target) is not None:
                return (context,)
        if isinstance(node, ast.Attribute):
            values = []
            for receiver in self.values(context, node.value, seen):
                call = receiver.node
                if not isinstance(call, ast.Call):
                    continue
                name = qualified_name(call.func)
                target = self.program.resolve_in(receiver, name) if name else None
                fields = self.fields(target) if target else None
                if fields is None or node.attr not in fields:
                    continue
                # Only explicit constructor arguments establish the forwarded field.
                argument = next(
                    (kw.value for kw in call.keywords if kw.arg == node.attr), None
                )
                if argument is None:
                    position = fields.index(node.attr)
                    if position < len(call.args):
                        argument = call.args[position]
                values.extend(self.values(receiver, argument, seen))
            return tuple(values)
        self.incomplete = True
        return ()

    def fields(
        self, symbol: Symbol, seen: frozenset[ast.AST] = frozenset()
    ) -> tuple[str, ...] | None:
        node = symbol.node
        if not isinstance(node, ast.ClassDef) or node in seen or node.keywords:
            return None
        aliases = import_aliases(symbol.file)
        if len(node.decorator_list) != 1:
            return None
        decorator = node.decorator_list[0]
        name = qualified_name(
            decorator.func if isinstance(decorator, ast.Call) else decorator
        )
        if not name or resolve_name(name, aliases) != "dataclasses.dataclass":
            return None
        declarations = self.program.bindings[symbol.file.relative_path].get(
            name.split(".")[0], []
        )
        if len(declarations) != 1 or not isinstance(
            declarations[0], (ast.Import, ast.ImportFrom)
        ):
            return None
        if isinstance(decorator, ast.Call) and (
            decorator.args
            or any(
                kw.arg in {None, "init", "kw_only"}
                and not (
                    isinstance(kw.value, ast.Constant)
                    and kw.value.value is (kw.arg == "init")
                )
                for kw in decorator.keywords
            )
        ):
            return None
        fields: list[str] = []
        for base in node.bases:
            name = qualified_name(
                base.value if isinstance(base, ast.Subscript) else base
            )
            parent = self.program.resolve(symbol.file, name) if name else None
            inherited = self.fields(parent, seen | {node}) if parent else None
            if inherited is None:
                return None
            fields.extend(field for field in inherited if field not in fields)
        for part in node.body:
            if isinstance(part, Function) and part.name in {
                "__init__",
                "__new__",
                "__post_init__",
                "__getattribute__",
                "__getattr__",
                "__setattr__",
            }:
                return None
            if isinstance(part, ast.AnnAssign) and isinstance(part.target, ast.Name):
                if isinstance(part.value, ast.Call):
                    return None
                if part.target.id not in fields:
                    fields.append(part.target.id)
        return tuple(fields)
