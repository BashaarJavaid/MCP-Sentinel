import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

root = Path("/private/tmp/mcp-phase22-options")
out = root / "artifacts/phase22/integration/v59-candidate-quality"
out.mkdir(exist_ok=False)
head = sys.argv[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


packet = {
    "source": head,
    "candidate_product_scanner": "7bf4c6e1cf0c8d83229b1273f80737e7cacc5b82",
    "runs": {},
    "archives": {},
    "artifact_files": [],
    "classification": "Fresh ordinary CI for shared-timeout policy revision at7bf4c6e. Optional exposed corpus evaluation remains unapproved and skipped. Historical reproductions retain pinned scanner8824014; no current-source corpus run or paid call.",
}
pending = json.loads(
    (root / "artifacts/phase22/integration/v59-timeout-policy/candidate-run-ids.json").read_text()
)
while pending:
    for kind, run in list(pending.items()):
        p = subprocess.run(
            [
                "gh",
                "run",
                "view",
                str(run),
                "--json",
                "databaseId,headSha,status,conclusion,jobs,url,workflowName",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(p.stdout)
        assert data["headSha"] == head
        print(
            kind,
            data["status"],
            data["conclusion"],
            [
                (
                    j["name"],
                    [
                        s["name"]
                        for s in j.get("steps", [])
                        if s["status"] == "in_progress"
                    ],
                )
                for j in data["jobs"]
                if j["status"] == "in_progress"
            ],
            flush=True,
        )
        if data["status"] != "completed":
            continue
        packet["runs"][kind] = data
        target = out / (kind + "-logs.zip")
        with target.open("wb") as stream:
            subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/BashaarJavaid/MCP-Sentinel/actions/runs/{run}/logs",
                ],
                cwd=root,
                stdout=stream,
                check=True,
            )
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            packet["archives"][kind] = {
                "sha256": sha(target.read_bytes()),
                "members": [
                    {
                        "path": n,
                        "bytes": len(archive.read(n)),
                        "sha256": sha(archive.read(n)),
                    }
                    for n in archive.namelist()
                ],
            }
        if kind != "docs":
            subprocess.run(
                [
                    "gh",
                    "run",
                    "download",
                    str(run),
                    "--dir",
                    str(out / "artifacts" / kind),
                ],
                cwd=root,
                check=True,
            )
        (out / (kind + "-retained.json")).write_text(
            json.dumps(
                {
                    "run": data,
                    "archives": packet["archives"].get(kind),
                    "complete": True,
                },
                indent=2,
            )
            + "\n"
        )
        del pending[kind]
    if pending:
        time.sleep(30)
for p in sorted((out / "artifacts").rglob("*")):
    assert not p.is_symlink()
    if p.is_file():
        packet["artifact_files"].append(
            {
                "path": p.relative_to(out).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": sha(p.read_bytes()),
            }
        )
packet["engineering_passed"] = (
    packet["runs"]["ci"]["conclusion"] == "success"
    and packet["runs"]["docs"]["conclusion"] == "success"
)
(out / "packet.json").write_text(json.dumps(packet, indent=2) + "\n")
print(
    "RETAINED", packet["engineering_passed"], len(packet["artifact_files"]), flush=True
)
