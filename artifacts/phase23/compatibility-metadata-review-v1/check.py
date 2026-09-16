"""Read-only scoring and retained-repeat checks; no scanner execution."""

import ast
import copy
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from scripts.phase20_scoring import candidate_identity, score  # noqa: E402

spec = importlib.util.spec_from_file_location("reviewed_runner", HERE / "evaluate.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
p = r.verify()
old = json.loads(
    (HERE.parent / "compatibility-recovery-review-v1/proposal.json").read_text()
)
assert p["order"] == old["order"][23:]
assert len(p["retained_first_passes"]) == 23
assert p["scanner"] == old["scanner"]
checked = 0
for group in p["groups"].values():
    for item in group["inputs"].values():
        if item["assessment"] is None:
            continue
        findings = json.loads((ROOT / item["reference_report"]).read_text())["findings"]
        assert candidate_identity(findings) == item["assessment"]["candidate_identity"]
        score(
            label=item["input"]["label"],
            state="completed",
            findings=findings,
            assessment=item["assessment"],
        )
        checked += 1

# Execute only the actual seed assignment from run(), without invoking the runner.
tree = ast.parse((HERE / "evaluate.py").read_text())
assignment = next(
    node
    for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(
        isinstance(target, ast.Name) and target.id == "previous"
        for target in node.targets
    )
)
scope = {
    "proposal": p,
    "supervisor": r.supervisor,
    "prior": r.prior,
    "ROOT": ROOT,
    "json": json,
}
exec(
    compile(ast.Module(body=[assignment], type_ignores=[]), "seed-check", "exec"), scope
)
previous = scope["previous"]
assert len(previous) == 23
pairs = 0
for row in p["order"]:
    key = row["input_id"]
    if row["batch"] == "repeat":
        assert key in previous
        canonical = copy.deepcopy(previous[key])
        assert previous[key] == canonical
        canonical["warnings"].append({"code": "synthetic", "message": "drift"})
        assert previous[key] != canonical
        pairs += 1
    else:
        assert key not in previous
        item = p["groups"][row["group"]]["inputs"][key]
        previous[key] = r.supervisor.clean(
            json.loads((ROOT / item["reference_report"]).read_text()), r.prior.EXCLUDED
        )
assert len(previous) == pairs == 56

original_sha = r.sha
retained_path = ROOT / p["retained_first_passes"][0]["report"]
with patch.object(
    r,
    "sha",
    side_effect=lambda path: (
        "drift" if Path(path) == retained_path else original_sha(path)
    ),
):
    try:
        r.verify()
    except AssertionError:
        pass
    else:
        raise AssertionError("Retained report hash drift accepted")
assert not (HERE / "authorization.json").exists()
assert not (HERE.parent / "compatibility-v3").exists()
print(
    f"{checked} assessment identities valid; 23 retained seeds + 89 planned "
    "observations form 56 pairs; diagnostic drift and retained-hash drift "
    "rejected; zero scans."
)
