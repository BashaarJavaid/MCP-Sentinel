# ruff: noqa: E402
"Retain one public upstream pair as bytes; never execute target code."

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from scripts.phase20_corpus import archive_files, tree_digest

BASE = ROOT / "artifacts/phase22/corpus-replacement-v5"
REPO = "priyankark/lighthouse-mcp"
FIX = "7570c4151fd50c843480cf7106db4c8061a97b35"


def main():
    receipt = json.loads(
        (
            ROOT
            / (
                "artifacts/phase22/integration/v23-source-only-recovery-autho"
                "rization.json"
            )
        ).read_text()
    )
    assert receipt["approved"] and not receipt["evaluation_approved"]
    assert not BASE.exists()
    (BASE / "provenance").mkdir(parents=True)
    (BASE / "sources").mkdir()
    metadata = {}
    for name, endpoint in {
        "repository": f"repos/{REPO}",
        "issue-23": f"repos/{REPO}/issues/23",
        "pull-24": f"repos/{REPO}/pulls/24",
        "upstream-fix": f"repos/{REPO}/commits/{FIX}",
        "pair-compare": (
            f"repos/{REPO}/compare/85a6355bdc0e6e0907a45d8783414b1128958741...{FIX}"
        ),
    }.items():
        data = subprocess.check_output(["gh", "api", endpoint], cwd=ROOT)
        (BASE / f"provenance/{name}.json").write_bytes(data)
        metadata[name] = json.loads(data)
    fix = metadata["upstream-fix"]
    assert fix["sha"] == FIX and len(fix["parents"]) == 1
    assert fix["parents"][0]["sha"] == "85a6355bdc0e6e0907a45d8783414b1128958741"
    rows = []
    for label, revision in (("vulnerable", fix["parents"][0]["sha"]), ("fixed", FIX)):
        url = f"https://codeload.github.com/{REPO}/tar.gz/{revision}"
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        files = archive_files(data, strip_root=True)
        path = BASE / f"sources/lighthouse-{label}.tar.gz"
        path.write_bytes(data)
        rows.append(
            {
                "label": label,
                "revision": revision,
                "url": url,
                "archive": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(data).hexdigest(),
                "file_count": len(files),
                "tree_sha256": tree_digest(files),
            }
        )
    (BASE / "provenance/downloads.json").write_text(
        json.dumps(
            {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "rows": rows,
                "target_execution": False,
                "scans": 0,
                "paid_calls": 0,
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
