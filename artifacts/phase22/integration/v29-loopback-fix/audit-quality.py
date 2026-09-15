import hashlib
import json
import re
import subprocess
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

root = Path("/private/tmp/mcp-phase22-options")
b = root / "artifacts/phase22/integration"
source = b / "v29-quality"
old = json.loads((source / "packet.json").read_text())
head = old["source"]


def sha(d):
    return hashlib.sha256(d).hexdigest()


jobs = old["runs"]["ci"]["jobs"]
assert len(jobs) == 33 and sum(j["conclusion"] == "success" for j in jobs) == 29
assert sorted(j["name"] for j in jobs if j["conclusion"] == "skipped") == [
    "Approved Phase 22 exposed Lighthouse regression",
    "Approved Phase 22 historical_first",
    "Approved Phase 22 historical_second",
    "Approved Phase 22 replacement-v5 evaluation",
]
p = {
    "source": head,
    "retention_packet_sha256": sha((source / "packet.json").read_bytes()),
    "quality": [],
    "distributions": [],
    "historical_reproductions": {},
    "classification": "Fresh current-source engineering at workflow 439c3fe with corrected scanner f85a90f. All four optional corpus jobs skipped. Retained historical reproductions use8824014; no fresh or exposed corrected corpus observation is inferred.",
}
with zipfile.ZipFile(source / "ci-logs.zip") as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.startswith("Quality (") and name.endswith(
            "Test with branch coverage.txt"
        ):
            data = z.read(name)
            text = data.decode()
            matched = re.search(r"(\d+) passed, (\d+) skipped in ([\d.]+)s", text)
            assert matched, name
            coverage = float(re.search(r"Total coverage: ([\d.]+)%", text)[1])
            assert coverage >= 80
            p["quality"].append(
                {
                    "job": name.split("/")[0],
                    "passed": int(matched[1]),
                    "skipped": int(matched[2]),
                    "seconds": float(matched[3]),
                    "branch_coverage_percent": coverage,
                    "member": name,
                    "sha256": sha(data),
                }
            )
assert len(p["quality"]) == 12 and all(
    r["passed"] == 2242 and r["skipped"] == 36 for r in p["quality"]
)
tracked = set(
    subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", head], cwd=root, text=True
    ).splitlines()
)
for archive in sorted((source / "artifacts/ci/portunusmcp-sentinel-dist").iterdir()):
    if archive.suffix == ".whl":
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            members = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
        mapping = {}
        for n in members:
            if n.startswith("sentinel/_fixtures/"):
                mapping[n] = "tests/fixtures/" + n.removeprefix("sentinel/_fixtures/")
            elif n.startswith("sentinel/_schemas/"):
                mapping[n] = "schemas/" + n.removeprefix("sentinel/_schemas/")
            elif n.startswith("sentinel/"):
                mapping[n] = "src/" + n
    else:
        with tarfile.open(archive) as t:
            members = {m.name: t.extractfile(m).read() for m in t if m.isfile()}
        mapping = {
            n: n.split("/", 1)[1] for n in members if n.split("/", 1)[1] in tracked
        }
    checked = []
    for name, path in mapping.items():
        data = subprocess.check_output(["git", "show", head + ":" + path], cwd=root)
        assert data == members[name], (archive.name, name)
        checked.append({"member": name, "source_path": path, "sha256": sha(data)})
    assert any(
        x["source_path"] == "src/sentinel/static/typescript_path_flow.py"
        for x in checked
    )
    for cassette_stage, fp in [
        (
            "typescript-smoke",
            ("b6f0b465a1d2cb7fb4bbbd1b886e4f1a62ba2d3371c766390e07a63130c0293f"),
        ),
        (
            "phase17",
            ("b826810055334d200c918b50ba4d78b12046244ccc02bfa06b83db0b1f928e39"),
        ),
    ]:
        assert any(
            x["source_path"] == f"src/sentinel/_cassettes/{cassette_stage}/{fp}.json"
            for x in checked
        )
    p["distributions"].append(
        {
            "path": str(archive.relative_to(b)),
            "sha256": sha(archive.read_bytes()),
            "git_blob_members_verified": checked,
            "remaining_metadata_members": [n for n in members if n not in mapping],
        }
    )
for kind in ["rules", "replay"]:
    paths = list(
        (source / "artifacts/ci" / f"phase20-{kind}-verification").rglob("results.json")
    )
    assert len(paths) == 1
    raw = json.loads(paths[0].read_text())
    p["historical_reproductions"][kind] = {
        "scanner": raw["scanner"],
        "states": dict(Counter(x["state"] for x in raw["outcomes"])),
        "sha256": sha(paths[0].read_bytes()),
    }
checkout = json.loads((b / "v29-checkout-binding.json").read_text())
assert checkout["head"] == head and checkout["complete_tree_equal_to_head"]
checkout_rows = []
with zipfile.ZipFile(source / "ci-logs.zip") as logs:
    for name in logs.namelist():
        if name.endswith("_Check out repository.txt") and "_Post " not in name:
            content = logs.read(name)
            identities = re.findall(r"(?m)^\S+\s+([0-9a-f]{40})\s*$", content.decode())
            assert identities and identities[-1] == checkout["synthetic_merge"], name
            checkout_rows.append(
                {
                    "job": name.split("/")[0],
                    "member": name,
                    "checkout_sha": identities[-1],
                    "sha256": sha(content),
                }
            )
assert len(checkout_rows) == 29
p["actual_checkouts"] = checkout_rows
p["checkout_binding_sha256"] = sha((b / "v29-checkout-binding.json").read_bytes())
p["actual_synthetic_merge"] = checkout["synthetic_merge"]
p["complete_checkout_tree_equals_head"] = True
out = b / "v29-quality-audit"
out.mkdir(exist_ok=False)
(out / "packet.json").write_text(json.dumps(p, indent=2) + "\n")
print(
    json.dumps(
        {
            "quality": p["quality"],
            "historical_states": {
                k: v["states"] for k, v in p["historical_reproductions"].items()
            },
            "distribution_members": [
                len(v["git_blob_members_verified"]) for v in p["distributions"]
            ],
        },
        indent=2,
    )
)
