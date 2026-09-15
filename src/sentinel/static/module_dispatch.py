"""Recover a bounded module-table dispatcher without importing target code."""

from __future__ import annotations

import ast

from sentinel.static.ast_utils import decorator_call, qualified_name, scope_nodes
from sentinel.static.discovery import Function, PythonProgram, Symbol, ToolBinding
from sentinel.static.execution import check_deadline
from sentinel.static.http_discovery import shadowed
from sentinel.static.model import ParsedPythonFile


def body(node: Function) -> list[ast.stmt]:
    return [
        part
        for part in node.body
        if not (
            isinstance(part, ast.Expr)
            and isinstance(part.value, ast.Constant)
            and isinstance(part.value.value, str)
        )
    ]


def assignment(node: ast.AST) -> tuple[ast.expr | None, ast.expr | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        return node.targets[0], node.value
    if isinstance(node, ast.AnnAssign):
        return node.target, node.value
    return None, None


def name(node: ast.AST | None, expected: str) -> bool:
    return isinstance(node, ast.Name) and node.id == expected


def parameters(node: Function, count: int) -> list[str] | None:
    args = node.args
    positional = args.posonlyargs + args.args
    if (
        len(positional) != count
        or args.vararg
        or args.kwarg
        or args.kwonlyargs
        or args.defaults
    ):
        return None
    return [arg.arg for arg in positional]


def declarations(
    program: PythonProgram,
    provider: Symbol,
    protected: set[ast.AST],
    allowed: set[ast.AST],
) -> tuple[tuple[str, ast.Call], ...] | None:
    node = provider.node
    if not isinstance(node, ast.FunctionDef) or node.decorator_list:
        return None
    statements = body(node)
    if parameters(node, 0) is None or len(statements) != 1:
        return None
    returned = statements[0]
    if not isinstance(returned, ast.Return) or not isinstance(
        returned.value, (ast.List, ast.Tuple)
    ):
        return None
    found = []
    for item in returned.value.elts:
        check_deadline(program.deadline)
        if (
            not isinstance(item, ast.Call)
            or item.args
            or program.external(provider, item.func) != "mcp.types.Tool"
            or any(kw.arg is None for kw in item.keywords)
        ):
            return None
        names = [kw.value for kw in item.keywords if kw.arg == "name"]
        if (
            len(names) != 1
            or not isinstance(names[0], ast.Constant)
            or not isinstance(names[0].value, str)
            or not names[0].value
        ):
            return None
        for kw in item.keywords:
            for part in ast.walk(kw.value):
                check_deadline(program.deadline)
                if isinstance(part, (ast.NamedExpr, ast.Await, ast.Yield)):
                    return None
                if isinstance(part, ast.Call):
                    # Only the unshadowed builtin copying a proved literal dict.
                    if (
                        not name(part.func, "dict")
                        or len(part.args) != 1
                        or part.keywords
                        or program.bindings[provider.file.relative_path].get("dict")
                        or shadowed(program, part, "dict")
                        or not literal_mapping(
                            program, provider, part.args[0], protected, allowed
                        )
                    ):
                        return None
                    allowed.add(part)
                if isinstance(part, ast.Dict) and any(
                    key is None
                    and not literal_mapping(
                        program, provider, value, protected, allowed
                    )
                    for key, value in zip(part.keys, part.values, strict=True)
                ):
                    return None
        found.append((names[0].value, item))
    return tuple(found)


def literal_mapping(
    program: PythonProgram,
    provider: Symbol,
    expression: ast.expr,
    protected: set[ast.AST],
    allowed: set[ast.AST],
) -> bool:
    """Prove an inline or unconditional module-local literal; never evaluate code."""
    value: ast.AST = expression
    if isinstance(expression, ast.Name):
        binding = program.resolve(provider.file, expression.id, value_binding=True)
        if binding is None or binding.file is not provider.file:
            return False
        value = binding.node
        parent = program.parents.get(value)
        if (
            not isinstance(parent, (ast.Assign, ast.AnnAssign))
            or program.parents.get(parent) is not provider.file.tree
            or not name(assignment(parent)[0], expression.id)
            or shadowed(program, expression, expression.id)
        ):
            return False
    if not isinstance(value, ast.Dict):
        return False
    check_deadline(program.deadline)
    try:
        ast.literal_eval(value)
    except (ValueError, TypeError, SyntaxError):
        return False
    check_deadline(program.deadline)
    if value is not expression:
        protected.add(value)
        allowed.add(expression)
    return True


def module_table_tools(
    program: PythonProgram, file: ParsedPythonFile
) -> tuple[ToolBinding, ...]:
    found: list[ToolBinding] = []
    for callback in file.tree.body:
        check_deadline(program.deadline)
        if not isinstance(callback, Function) or len(callback.decorator_list) != 1:
            continue
        decorator = callback.decorator_list[0]
        method, _ = decorator_call(decorator)
        if method and method.endswith(".call_tool"):
            found.extend(dispatch_tools(program, file, callback, decorator))
    return tuple(found)


def dispatch_tools(
    program: PythonProgram,
    file: ParsedPythonFile,
    callback: Function,
    decorator: ast.AST,
) -> tuple[ToolBinding, ...]:
    args = parameters(callback, 2)
    statements = body(callback)
    if args is None or len(statements) < 3:
        return ()
    receiver, lookup = assignment(statements[0])
    if not (
        isinstance(receiver, ast.Name)
        and isinstance(lookup, ast.Call)
        and isinstance(lookup.func, ast.Attribute)
        and lookup.func.attr == "get"
        and isinstance(lookup.func.value, ast.Name)
        and len(lookup.args) == 1
        and name(lookup.args[0], args[0])
        and not lookup.keywords
    ):
        return ()
    guard = statements[1]
    if not (
        isinstance(guard, ast.If)
        and isinstance(guard.test, ast.Compare)
        and name(guard.test.left, receiver.id)
        and len(guard.test.ops) == 1
        and isinstance(guard.test.ops[0], ast.Is)
        and len(guard.test.comparators) == 1
        and isinstance(guard.test.comparators[0], ast.Constant)
        and guard.test.comparators[0].value is None
        and len(guard.body) == 1
        and isinstance(guard.body[0], ast.Raise)
        and not guard.orelse
    ):
        return ()
    invocation = (
        statements[2].value
        if isinstance(statements[2], (ast.Return, ast.Expr))
        else assignment(statements[2])[1]
    )
    if isinstance(invocation, ast.Await):
        invocation = invocation.value
    if not (
        isinstance(invocation, ast.Call)
        and isinstance(invocation.func, ast.Attribute)
        and name(invocation.func.value, receiver.id)
        and len(invocation.args) == 2
        and all(
            name(value, arg) for value, arg in zip(invocation.args, args, strict=True)
        )
        and not invocation.keywords
    ):
        return ()
    receiver_uses = {receiver, guard.test.left, invocation.func.value}
    if any(
        isinstance(part, ast.Name)
        and part.id == receiver.id
        and part not in receiver_uses
        for part in scope_nodes(callback)
    ):
        return ()
    table_name = lookup.func.value.id
    table = program.resolve(file, table_name, value_binding=True)
    if (
        table is None
        or table.file is not file
        or not isinstance(table.node, ast.Call)
        or table.node.args
        or table.node.keywords
        or shadowed(program, lookup, table_name)
    ):
        return ()
    factory_name = qualified_name(table.node.func)
    factory = program.resolve(file, factory_name) if factory_name else None
    if (
        factory is None
        or factory.file is not file
        or not isinstance(factory.node, ast.FunctionDef)
        or factory.node.decorator_list
        or parameters(factory.node, 0) is None
    ):
        return ()
    parts = body(factory.node)
    if len(parts) != 3:
        return ()
    target, empty = assignment(parts[0])
    loop, returned = parts[1:]
    if not (
        isinstance(target, ast.Name)
        and isinstance(empty, ast.Dict)
        and not empty.keys
        and isinstance(loop, ast.For)
        and isinstance(loop.target, ast.Name)
        and isinstance(loop.iter, ast.Name)
        and not loop.orelse
        and len(loop.body) == 1
        and isinstance(returned, ast.Return)
        and name(returned.value, target.id)
    ):
        return ()
    inner = loop.body[0]
    if not (
        isinstance(inner, ast.For)
        and isinstance(inner.target, ast.Name)
        and isinstance(inner.iter, ast.Call)
        and isinstance(inner.iter.func, ast.Attribute)
        and name(inner.iter.func.value, loop.target.id)
        and not inner.iter.args
        and not inner.iter.keywords
        and not inner.orelse
        and len(inner.body) in {1, 2}
    ):
        return ()
    if len({target.id, loop.target.id, inner.target.id, loop.iter.id}) != 4:
        return ()
    item = f"{inner.target.id}.name"
    if len(inner.body) == 2:
        duplicate = inner.body[0]
        if not (
            isinstance(duplicate, ast.If)
            and isinstance(duplicate.test, ast.Compare)
            and qualified_name(duplicate.test.left) == item
            and len(duplicate.test.ops) == 1
            and isinstance(duplicate.test.ops[0], ast.In)
            and len(duplicate.test.comparators) == 1
            and name(duplicate.test.comparators[0], target.id)
            and len(duplicate.body) == 1
            and isinstance(duplicate.body[0], ast.Raise)
            and not duplicate.orelse
        ):
            return ()
    key, value = assignment(inner.body[-1])
    if not (
        isinstance(key, ast.Subscript)
        and name(key.value, target.id)
        and qualified_name(key.slice) == item
        and name(value, loop.target.id)
    ):
        return ()
    modules = program.resolve(file, loop.iter.id)
    if (
        modules is None
        or modules.file is not file
        or not isinstance(modules.node, (ast.List, ast.Tuple))
        or shadowed(program, loop.iter, loop.iter.id)
    ):
        return ()
    # ponytail: recognize this bounded builder, not arbitrary Python evaluation.
    # New builder forms need their own identity and mutation controls.
    allowed = set(ast.walk(factory.node)) | set(ast.walk(lookup))
    allowed.add(table.node)
    allowed.add(table.node.func)
    allowed.update(ast.walk(modules.node))
    protected = {table_name, loop.iter.id, factory.node.name}
    for function in file.tree.body:
        if not isinstance(function, Function) or function is factory.node:
            continue
        listing = body(function)
        if len(listing) != 3:
            continue
        output, initial = assignment(listing[0])
        iteration, result = listing[1:]
        if not (
            isinstance(output, ast.Name)
            and isinstance(initial, ast.List)
            and not initial.elts
            and isinstance(iteration, ast.For)
            and name(iteration.iter, loop.iter.id)
            and isinstance(iteration.target, ast.Name)
            and not iteration.orelse
            and len(iteration.body) == 1
            and isinstance(iteration.body[0], ast.Expr)
            and isinstance(result, ast.Return)
            and name(result.value, output.id)
        ):
            continue
        append = iteration.body[0].value
        if (
            isinstance(append, ast.Call)
            and qualified_name(append.func) == f"{output.id}.extend"
            and not append.keywords
            and len(append.args) == 1
            and isinstance(append.args[0], ast.Call)
            and qualified_name(append.args[0].func)
            == f"{iteration.target.id}.{inner.iter.func.attr}"
            and not append.args[0].args
            and not append.args[0].keywords
        ):
            allowed.update(ast.walk(iteration))
    for part in ast.walk(file.tree):
        check_deadline(program.deadline)
        if isinstance(part, ast.Name) and part.id in protected:
            parent = program.parents.get(part)
            if part not in allowed and not (
                isinstance(part.ctx, ast.Store)
                and isinstance(parent, (ast.Assign, ast.AnnAssign))
                and program.parents.get(parent) is file.tree
                and assignment(parent)[1] in {table.node, modules.node}
            ):
                return ()
        if isinstance(part, (ast.Global, ast.Nonlocal)) and protected.intersection(
            part.names
        ):
            return ()
    found = []
    seen_names: set[str] = set()
    module_bindings = []
    protected_nodes: set[ast.AST] = {table.node, modules.node, factory.node}
    for expression in modules.node.elts:
        module_name = qualified_name(expression)
        module = (
            program.resolve(file, module_name, value_binding=True)
            if module_name
            else None
        )
        if module is None or not isinstance(module.node, ast.Module):
            return ()
        # Importing a package attribute is not proof of a submodule if its
        # __init__ also defines that name; do not bypass that replacement.
        module_path = module.file.path
        for package in program.files:
            if package.path == module_path.parent / "__init__.py" and (
                program.bindings[package.relative_path].get(module_path.stem)
                or program.bindings[package.relative_path].get("__getattr__")
            ):
                return ()
        provider = program.resolve(module.file, inner.iter.func.attr)
        handler = program.resolve(module.file, invocation.func.attr)
        names = (
            declarations(program, provider, protected_nodes, allowed)
            if provider
            else None
        )
        if (
            names is None
            or handler is None
            or not isinstance(handler.node, Function)
            or handler.node.decorator_list
            or parameters(handler.node, 2) is None
            or any(tool_name in seen_names for tool_name, _ in names)
            or len({tool_name for tool_name, _ in names}) != len(names)
        ):
            return ()
        seen_names.update(tool_name for tool_name, _ in names)
        assert provider is not None
        module_bindings.append((module, expression, provider, handler))
        for tool_name, _ in names:
            found.append(
                ToolBinding(
                    tool_name,
                    Symbol(file, tool_name, invocation),
                    handler,
                    handler.node,
                    decorator,
                )
            )
    if not stable_bindings(
        program,
        file,
        module_bindings,
        protected_nodes,
        allowed,
    ):
        return ()
    return tuple(found)


def stable_bindings(
    program: PythonProgram,
    registration_file: ParsedPythonFile,
    modules: list[tuple[Symbol, ast.expr, Symbol, Symbol]],
    protected: set[ast.AST],
    allowed: set[ast.AST],
) -> bool:
    """Reject replacement/escape in the included production import closure."""
    reachable = program.reachable_files({registration_file.relative_path})
    copies = any(
        isinstance(part, ast.Call) and name(part.func, "dict") for part in allowed
    )
    module_nodes = {module.node for module, _, _, _ in modules}
    references = {reference for _, reference, _, _ in modules}
    members = {
        symbol.node
        for _, _, provider, handler in modules
        for symbol in (provider, handler)
    }
    member_names = {
        symbol.name
        for _, _, provider, handler in modules
        for symbol in (provider, handler)
    }
    namespaces = {registration_file.tree}
    for module, _, _, _ in modules:
        namespaces.update(
            file.tree
            for file in program.files
            if file.path.name == "__init__.py"
            and file.path.parent in module.file.path.parents
        )
    for file in program.files:
        if file.relative_path not in reachable:
            continue
        for part in ast.walk(file.tree):
            check_deadline(program.deadline)
            if isinstance(part, (ast.Import, ast.ImportFrom)):
                for imported in part.names:
                    if imported.name == "*":
                        return False
                    external = program.external_import(
                        part, imported.asname or imported.name.split(".")[0]
                    )
                    if copies and external.split(".")[0] in {"builtins", "importlib"}:
                        return False
                    if program.parents.get(part) is file.tree:
                        continue
                    binding = program.resolve_import(
                        file,
                        part,
                        imported.asname or imported.name.split(".")[0],
                        value_binding=True,
                    )
                    if binding and binding.node in (
                        module_nodes | members | protected | namespaces
                    ):
                        return False
            if isinstance(
                part, (ast.Global, ast.Nonlocal)
            ) and member_names.intersection(part.names):
                return False
            if isinstance(part, (ast.Global, ast.Nonlocal)) and any(
                (copies and identifier == "dict")
                or (
                    (binding := program.resolve(file, identifier, value_binding=True))
                    is not None
                    and binding.node in protected
                )
                for identifier in part.names
            ):
                return False
            if copies and (
                name(part, "__builtins__")
                or (
                    name(part, "dict")
                    and isinstance(part, ast.Name)
                    and isinstance(part.ctx, ast.Del)
                )
                or (isinstance(part, ast.Attribute) and part.attr == "__dict__")
                or program.external(Symbol(file, "", file.tree), part) == "sys.modules"
            ):
                return False
            if copies and program.external(Symbol(file, "", file.tree), part) == "sys":
                parent = program.parents.get(part)
                if not (
                    isinstance(parent, ast.Attribute)
                    and isinstance(parent.ctx, ast.Load)
                    and not parent.attr.startswith("_")
                    and parent.attr != "modules"
                ):
                    return False
            if isinstance(part, ast.Call) and qualified_name(part.func) in {
                "globals",
                "locals",
                "vars",
                "exec",
                "eval",
            }:
                return False
            if not isinstance(part, (ast.Name, ast.Attribute)) or part in references:
                continue
            text = qualified_name(part)
            if not text or shadowed(program, part, text.split(".")[0]):
                continue
            resolved = program.resolve(file, text, value_binding=True)
            if resolved is None:
                continue
            parent = program.parents.get(part)
            grandparent = program.parents.get(parent) if parent else None
            if resolved.node in namespaces and not (
                isinstance(parent, ast.Attribute) and isinstance(parent.ctx, ast.Load)
            ):
                return False
            if (
                resolved.node in protected
                and part not in allowed
                and not (
                    isinstance(part.ctx, ast.Store)
                    and isinstance(parent, (ast.Assign, ast.AnnAssign))
                    and program.parents.get(parent) is file.tree
                    and assignment(parent)[1] in protected
                )
            ):
                return False
            if resolved.node in module_nodes and not (
                isinstance(parent, ast.Attribute)
                and parent.attr in member_names
                and isinstance(parent.ctx, ast.Load)
                and isinstance(grandparent, ast.Call)
                and grandparent.func is parent
            ):
                return False
            if resolved.node in members and not (
                isinstance(parent, ast.Call) and parent.func is part
            ):
                return False
    return True
