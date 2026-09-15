"""Retain the single approved run without rerunning any measurement."""

import hashlib
import json
import subprocess
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "hosted"
REPO = "repos/BashaarJavaid/MCP-Sentinel"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    receipt = json.loads((OUT.parent / "dispatch-consumed.json").read_text())
    run_id = receipt["run"]["databaseId"]
    command = [
        "gh",
        "run",
        "view",
        str(run_id),
        "--json",
        "databaseId,headSha,status,conclusion,jobs,url,event,createdAt,updatedAt",
    ]
    while True:
        run = json.loads(subprocess.check_output(command, cwd=ROOT, text=True))
        assert (
            run["headSha"] == receipt["workflow_source"]
            and run["event"] == "workflow_dispatch"
        )
        active = [
            (
                j["name"],
                [s["name"] for s in j.get("steps", []) if s["status"] == "in_progress"],
            )
            for j in run["jobs"]
            if j["status"] == "in_progress"
        ]
        print(run["status"], run["conclusion"], active, flush=True)
        (OUT / "latest-run.json").write_text(json.dumps(run, indent=2) + "\n")
        if run["status"] == "completed":
            break
        time.sleep(30)
    log = OUT / "logs.zip"
    with log.open("wb") as stream:
        subprocess.run(
            ["gh", "api", f"{REPO}/actions/runs/{run_id}/logs"],
            cwd=ROOT,
            stdout=stream,
            check=True,
        )
    with zipfile.ZipFile(log) as archive:
        assert archive.testzip() is None
        log_members = [
            {"path": n, "sha256": hashlib.sha256(archive.read(n)).hexdigest()}
            for n in archive.namelist()
        ]
    artifacts = json.loads(
        subprocess.check_output(
            ["gh", "api", f"{REPO}/actions/runs/{run_id}/artifacts"],
            cwd=ROOT,
            text=True,
        )
    )
    (OUT / "artifact-metadata.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    if artifacts["total_count"]:
        subprocess.run(
            ["gh", "run", "download", str(run_id), "--dir", str(OUT / "artifacts")],
            cwd=ROOT,
            check=True,
        )
    files = {}
    for p in sorted(OUT.rglob("*")):
        assert not p.is_symlink()
        if p.is_file():
            files[p.relative_to(OUT).as_posix()] = sha(p)
    (OUT / "packet.json").write_text(
        json.dumps(
            {
                "run": run,
                "files_sha256": files,
                "log_members": log_members,
                "collector_sha256": sha(Path(__file__)),
                "dispatch_sha256": sha(OUT.parent / "dispatch-consumed.json"),
                "retention_complete": True,
                "assessment_pending": True,
                "new_paid_calls": 0,
            },
            indent=2,
        )
        + "\n"
    )
    print("RETAINED", run_id, run["conclusion"], len(files), flush=True)


if __name__ == "__main__":
    main()
