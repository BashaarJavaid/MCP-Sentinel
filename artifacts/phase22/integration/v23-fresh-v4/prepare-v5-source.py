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
REPO = "cyanheads/git-mcp-server"
FIX = "0dbd6995ccdf76ab770b58013034365b2d06c4d9"


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
        "advisory-upstream": f"repos/{REPO}/security-advisories/GHSA-3q26-f695-pp76",
        "advisory-reviewed": "advisories/GHSA-3q26-f695-pp76",
        "upstream-fix": f"repos/{REPO}/commits/{FIX}",
        "pair-compare": f"repos/{REPO}/compare/v2.1.4...v2.1.5",
    }.items():
        data = subprocess.check_output(["gh", "api", endpoint], cwd=ROOT)
        (BASE / f"provenance/{name}.json").write_bytes(data)
        metadata[name] = json.loads(data)
    fix = metadata["upstream-fix"]
    assert fix["sha"] == FIX and len(fix["parents"]) == 1
    assert fix["parents"][0]["sha"] == "f30169ec3a2520990e5467c19ef42ea7d6d9270e"
    rows = []
    for label, revision in (("vulnerable", fix["parents"][0]["sha"]), ("fixed", FIX)):
        url = f"https://codeload.github.com/{REPO}/tar.gz/{revision}"
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        files = archive_files(data, strip_root=True)
        path = BASE / f"sources/git-init-{label}.tar.gz"
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
