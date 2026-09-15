"""Keep the approved private invalidation-set mutation/alias proof enforceable."""

import ast
from pathlib import Path

import sentinel


def test_private_invalidation_mutations_do_not_remove_or_export() -> None:
    # The If accumulator may retain its first arm because all shipped writers
    # preserve baseline keys and no completed-arm set escapes. New mutation or
    # reflection sites require revisiting that proof, not extending this list.
    allowed = {
        "self.invalidated_objects: set[str] = set()",
        "initial_invalidated = self.invalidated_objects.copy()",
        "self.invalidated_objects = initial_invalidated.copy()",
        "invalidated = self.invalidated_objects",
        "invalidated.update(self.invalidated_objects)",
        "self.invalidated_objects = initial_invalidated.copy() "
        "if invalidated is None else invalidated",
        "self.invalidated_objects.update((value.key, "
        "self.record_roots.get(value.key, value.key)))",
        "self.invalidated_objects.add(symbol.external)",
    }
    local_statements = allowed | {"invalidated: set[str] | None = None"}
    seen = set()
    classes = {}
    for path in Path(sentinel.__file__).parent.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for node in ast.walk(tree):
            if (
                path.name == "typescript_path_flow.py"
                and isinstance(node, ast.Name)
                and node.id in {"invalidated", "initial_invalidated"}
            ):
                parent = parents[node]
                if isinstance(parent, ast.Compare):
                    assert ast.unparse(parent) == "invalidated is None"
                else:
                    while not isinstance(parent, ast.stmt):
                        parent = parents[parent]
                    assert ast.unparse(parent) in local_statements
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert "invalidated_objects" not in node.value, (path, node.lineno)
            if (
                not isinstance(node, ast.Attribute)
                or node.attr != "invalidated_objects"
            ):
                continue
            assert ast.unparse(node.value) == "self", (path, node.lineno)
            parent = parents[node]
            if isinstance(parent, ast.Compare):
                assert len(parent.ops) == 1 and isinstance(
                    parent.ops[0], (ast.In, ast.NotIn)
                )
                continue
            if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.BitAnd):
                continue
            while not isinstance(parent, ast.stmt):
                parent = parents[parent]
            statement = ast.unparse(parent)
            assert statement in allowed, (path, node.lineno, statement)
            assert path.name == "typescript_path_flow.py"
            seen.add(statement)
    assert seen == allowed
    flows = {"TypeScriptPathFlow"}
    while True:
        descendants = flows | {
            name
            for name, node in classes.items()
            if {ast.unparse(base) for base in node.bases} & flows
        }
        if descendants == flows:
            break
        flows = descendants
    assert flows == {
        "TypeScriptPathFlow",
        "RegistrationFlow",
        "HTTPRegistrationFlow",
        "ShellFlow",
        "TypeScriptOptionFlow",
        "TypeScriptURLFlow",
        "TypeScriptCredentialFlow",
    }
    for name in flows:
        for node in ast.walk(classes[name]):
            if isinstance(node, ast.Attribute):
                assert node.attr != "__dict__"
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                assert node.func.id not in {
                    "eval",
                    "exec",
                    "setattr",
                    "delattr",
                    "vars",
                }
            if any(isinstance(arg, ast.Name) and arg.id == "self" for arg in node.args):
                # HTTP forks copy the private set; their memo shares source ASTs,
                # program and report state only, never a completed arm's set.
                assert ast.unparse(node) == "copy.deepcopy(self, memo.copy())"
