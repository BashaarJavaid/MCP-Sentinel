"""Rebuild proposed labels/overlays from pinned archives; never execute targets."""

from __future__ import annotations

import ast
import difflib
import gzip
import io
import json
import re
import tarfile
import tokenize
from pathlib import Path

from scripts.phase20_corpus import archive_files, digest, tree_digest
from scripts.phase22_corpus import CORPUS, ROOT, validate

# Cases and source remain review-only until the user approves the exact packet.
CASES = [
    json.loads(path.read_text()) for path in sorted((CORPUS / "review").glob("*.json"))
]


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def packed(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with (
        gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream,
        tarfile.open(fileobj=stream, mode="w") as archive,
    ):
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))
    result = buffer.getvalue()
    assert archive_files(result, strip_root=False) == files
    return result


def rename(source: bytes, names: dict[str, str], python: bool) -> bytes:
    text = source.decode("utf-8")
    if python:
        lines = text.splitlines(keepends=True)
        offsets = [sum(map(len, lines[:index])) for index in range(len(lines) + 1)]
        replacements = []
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.NAME and token.string in names:
                start = offsets[token.start[0] - 1] + token.start[1]
                end = offsets[token.end[0] - 1] + token.end[1]
                replacements.append((start, end, names[token.string]))
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        ast.parse(text)
    else:
        for original, replacement in names.items():
            text = re.sub(r"\b" + re.escape(original) + r"\b", replacement, text)
    return text.encode("utf-8")


def main() -> None:
    snapshots = {}
    trees = {}
    aliases = {}
    for case in CASES:
        repo = case["repository"]
        meta = CORPUS / "provenance" / (repo.replace("/", "-") + "-repository.json")
        canonical = json.loads(meta.read_text())["full_name"]
        aliases[repo.casefold()] = canonical.casefold()
        for revision in (case["before"], case["after"]):
            if revision in trees:
                continue
            path = CORPUS / "snapshots" / (revision + ".tar.gz")
            files = archive_files(path.read_bytes(), strip_root=True)
            trees[revision] = files
            licenses = [
                name
                for name in files
                if Path(name).name.lower().startswith(("license", "copying", "notice"))
            ]
            if revision == "b070bc32ed7b7884c3f0f8221e6d0d28b7554d41":
                assert b'license = { text = "MIT" }' in files["pyproject.toml"]
                licenses = ["pyproject.toml", "README.md"]
            assert licenses, revision
            snapshots[revision] = {
                "repository": repo,
                "revision": revision,
                "url": f"https://codeload.github.com/{repo}/tar.gz/{revision}",
                "archive": artifact(path),
                "files": {name: digest(data) for name, data in files.items()},
                "licenses": licenses,
            }
    inputs = []
    pairs = []
    for case in CASES:
        name = case["id"]
        source_review = CORPUS / "review" / (name + ".json")
        source_review.write_text(json.dumps(case, indent=2) + "\n")
        provenance = [
            artifact(CORPUS / "provenance" / value) for value in case["provenance"]
        ]
        provenance.append(artifact(source_review))
        pairs.append(
            {
                "id": name,
                "rule_id": case["rule"],
                "fix_origin": "evaluator_authored_description_overlay"
                if case.get("authored_fix")
                else "upstream",
                "provenance": provenance,
                "review": case["review"],
            }
        )
        for label in ("vulnerable", "fixed", "safe"):
            revision = case["before"] if label == "vulnerable" else case["after"]
            original = trees[revision]
            files = dict(original)
            fixed_overlay = {}
            if label == "fixed" and case.get("authored_fix"):
                target = case["files"][0]
                text = files[target].decode()
                if name.startswith("integsec"):
                    start = text.index("  description: `")
                    end = text.index("  inputSchema:", start)
                    replacement = (
                        "  description: 'A helpful calculator for "
                        "mathematical expressions. Supports basic "
                        "arithmetic operations.',\n"
                    )
                else:
                    start = text.index('        "description": (')
                    end = text.index('        "inputSchema":', start)
                    replacement = (
                        '        "description": "Search internal '
                        'documentation for relevant articles.",\n'
                    )
                updated = (text[:start] + replacement + text[end:]).encode()
                fixed_overlay[target] = updated
                files[target] = updated
                patch = "".join(
                    difflib.unified_diff(
                        text.splitlines(True),
                        updated.decode().splitlines(True),
                        fromfile=target,
                        tofile=target,
                    )
                )
                (CORPUS / "review" / (name + "-proposed-fix.patch")).write_text(patch)
            for mutated in (False,) if label == "safe" else (False, True):
                effective = dict(files)
                if mutated:
                    for target in case.get("mutation_files", case["files"]):
                        if target in effective:
                            effective[target] = rename(
                                effective[target],
                                case["rename"],
                                target.endswith(".py"),
                            )
                    assert effective != files, (name, label)
                overlay = {
                    path: data
                    for path, data in effective.items()
                    if original[path] != data
                }
                item_id = name + "-" + label + ("-mutation" if mutated else "")
                overlay_record = None
                if overlay:
                    overlay_path = CORPUS / "mutations" / (item_id + ".tar.gz")
                    overlay_path.write_bytes(packed(overlay))
                    overlay_record = artifact(overlay_path)
                evidence = [
                    {
                        "path": path,
                        "start_line": 1,
                        "end_line": len(effective[path].splitlines()),
                        "sha256": digest(effective[path]),
                        "role": (
                            "Review the registered metadata or "
                            "caller/guard/sink flow for this condition; "
                            "nearby warnings and overlapping lines alone are "
                            "not a match."
                        ),
                    }
                    for path in case["files"]
                    if path in effective
                ]
                runtime = "Unsupported targeted runtime treatment: " + (
                    "TypeScript execution is outside Python stdio support."
                    if case["language"] == "typescript"
                    else (
                        "This source-only freeze packet does not provide "
                        "the condition-specific host-model, HTTP service,"
                        " or command environment required to test this "
                        "property with the four fixed templates. Startup "
                        "and tool discovery are untested, not "
                        "demonstrated failures or defenses."
                    )
                )
                inputs.append(
                    {
                        "id": item_id,
                        "family": name,
                        "repository": case["repository"],
                        "language": case["language"],
                        "split": case["split"],
                        "variant": "safe_control"
                        if label == "safe"
                        else "mutation"
                        if mutated
                        else "original",
                        "label": label,
                        "snapshot": revision,
                        "scan_root": case["root"],
                        "condition": case["safe"]
                        if label == "safe"
                        else case["condition"],
                        "prerequisites": [case["safe_prerequisites"]]
                        if label == "safe"
                        else case["prerequisites"],
                        "static_applicability": (
                            "Source-only Python/TypeScript condition, "
                            "independent of current recognizer success. "
                            "Unsupported or unresolved recognition stays in "
                            "the denominator."
                        ),
                        "runtime_applicability": "unsupported",
                        "runtime_reason": runtime,
                        "runtime_configuration": None,
                        "evidence": evidence,
                        "matching": (
                            "Require a finding to describe this exact "
                            "metadata instruction or violated "
                            "caller/guard/sink boundary, with relevant "
                            "repository-relative evidence. Rule ID or source-"
                            "file overlap alone is insufficient. Record "
                            "unmatched findings separately as unadjudicated; "
                            "fixed/safe labels cover only the named "
                            "condition."
                        ),
                        "parent": name + "-" + label if mutated else None,
                        "transformation": (
                            "Paired identifier rename "
                            + json.dumps(case["rename"], sort_keys=True)
                            + (
                                "; Python token-aware, TypeScript bounded "
                                "identifier replacement; behavior and boundary "
                                "unchanged."
                            )
                        )
                        if mutated
                        else (
                            "Evaluator-authored replacement of only the "
                            "attached malicious tool description with its "
                            "ordinary task description; upstream bytes "
                            "preserved in snapshot."
                        )
                        if fixed_overlay
                        else None,
                        "overlay": overlay_record,
                        "tree_sha256": tree_digest(effective),
                    }
                )
    packet = [
        artifact(path)
        for path in sorted((CORPUS / "provenance").glob("*-projection.json"))
    ]
    packet.extend(
        artifact(path)
        for path in sorted((CORPUS / "provenance").glob("*-repository.json"))
    )
    packet.extend(
        artifact(path) for path in sorted((CORPUS / "review").glob("*.patch"))
    )
    manifest = {
        "version": 1,
        "status": "proposed_pending_user_freeze",
        "freeze_approved": False,
        "methodology": (
            "Ten independently sourced pairs, one development"
            " and one separate held-out repository per new "
            "rule; ten source-conditioned controls and 20 "
            "correlated structural mutations. Eight upstream "
            "fixes and two explicitly evaluator-authored "
            "description overlays. Source review only; no "
            "target execution, detector tuning, paid "
            "evaluation or accuracy measurement. Fixed and "
            "safe labels are condition-specific. Public "
            "historical source cannot establish absence of "
            "model exposure. User must approve exact sources,"
            " labels, license terms, scope projections, "
            "overlays and repository split before freeze."
        ),
        "snapshots": list(snapshots.values()),
        "pairs": pairs,
        "inputs": inputs,
        "packet": packet,
        "repository_aliases": aliases,
    }
    (CORPUS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    result = validate()
    print(
        f"Validated {len(result.pairs)} pairs and {len(result.inputs)} inputs; "
        "freeze approval pending."
    )


if __name__ == "__main__":
    main()
