"""Regenerate the proposed packet from retained upstream archives, without scanning."""

from __future__ import annotations

import gzip
import io
import json
import re
import tarfile
import tokenize
from pathlib import Path
from typing import Any

import yaml

from scripts.phase20_corpus import CORPUS, ROOT, archive_files, digest, tree_digest

# These are source-selected conditions, not expected Sentinel rule outputs.
SPECS = [
    (
        "git-staging",
        "vjqx-cfc4-9h6v",
        "862e717ff714987bd5577318df09858e14883863",
        "src/git",
        "src/mcp_server_git/server.py",
        (
            "git_add rejects relative paths resolving outside its "
            "repository before staging"
        ),
        (
            "A writable Git repository and a readable sibling file; files "
            "contains ../outside.txt"
        ),
        "rename git_add to stage_repository_files at every Python identifier reference",
    ),
    (
        "git-arguments",
        "9xwc-hfwc-8w59",
        "9e5d5b8e4b5dd6fa4fc84cad5eb291568024aad4",
        "src/git",
        "src/mcp_server_git/server.py",
        (
            "git_diff and git_checkout reject flag-like refs before the "
            "Git CLI can treat them as options"
        ),
        (
            "An initialized repository with HEAD; a ref argument beginning "
            "with --output= or another option"
        ),
        (
            "route git_diff output through a same-file identity helper, "
            "preserving validation and the sink"
        ),
    ),
    (
        "git-repository",
        "j22h-9j4x-23w5",
        "a37158bc1555ce0b1121ea98a3e740119d7fc8c7",
        "src/git",
        "src/mcp_server_git/server.py",
        (
            "When --repository is set, tool repo_path cannot select a "
            "repository outside that resolved boundary"
        ),
        (
            "A configured allowed repository and a separate initialized "
            "repository; explicit --repository flag"
        ),
        (
            "alias the pathlib Path import as RepositoryPath and rename "
            "its identifier uses"
        ),
    ),
    (
        "filesystem-prefix",
        "hc55-p739-j48w",
        "cc99bdabdcad93a58877c5f3ab20e21d4394423d",
        "src/filesystem",
        "index.ts",
        (
            "A configured directory /workspace/allowed does not authorize "
            "sibling /workspace/allowed-other via string-prefix collision"
        ),
        (
            "Configured allowed directory and a readable same-prefix "
            "sibling; ordinary non-symlink paths"
        ),
        (
            "rename validatePath to resolvePermittedFile without changing "
            "the registered MCP API"
        ),
    ),
    (
        "atlassian-ssrf",
        "7r34-79r5-rcc9",
        "5cd697dfce9116ef330b8dc7a91291640e0528d9",
        ".",
        "src/mcp_atlassian/servers/main.py",
        (
            "Header service URLs with literal loopback/private IPs or "
            "blocked schemes are rejected before Jira/Confluence requests"
        ),
        (
            "HTTP/SSE; no Authorization header; paired X-Atlassian-*-Url "
            "and Personal-Token headers; literal 127.0.0.1; SSRF allowlist "
            "overrides unset"
        ),
        (
            "alias the urllib.parse urlparse import as parse_service_url "
            "in the URL utility"
        ),
    ),
    (
        "atlassian-auth",
        "vc8m-84rp-53hx",
        "b041733473f95119dd539542a43c280737a8e460",
        ".",
        "src/mcp_atlassian/servers/dependencies.py",
        (
            "An HTTP caller with no user credential cannot inherit "
            "operator-global Jira/Confluence credentials with "
            "ALLOW_GLOBAL_CRED_FALLBACK unset"
        ),
        (
            "HTTP MCP endpoint; global credentials; no per-user "
            "credential; OAuth proxy and ignore-header-auth overrides "
            "disabled"
        ),
        (
            "rename the shared _get_fetcher helper to "
            "_resolve_service_fetcher throughout production Python files"
        ),
    ),
    (
        "atlassian-upload",
        "mrq8-fv7v-hhjg",
        "b041733473f95119dd539542a43c280737a8e460",
        ".",
        "src/mcp_atlassian/confluence/attachments.py",
        (
            "Confluence and Jira attachment upload sources cannot escape "
            "the process working directory through absolute paths or "
            "traversal"
        ),
        (
            "HTTP multi-user caller with upload permission; readable "
            "sibling file; read-only mode off; existing page/issue and "
            "upload sink"
        ),
        (
            "route upload file_path through an imported identity helper in "
            "utils/io.py, preserving public parameter names and validation "
            "order"
        ),
    ),
    (
        "excel-boundary",
        "j98m-w3xp-9f56",
        "f51340ecd5778952405044b203d3a2d4c8a46833",
        ".",
        "src/excel_mcp/server.py",
        (
            "Remote-mode filenames must be relative and resolve inside "
            "EXCEL_FILES_PATH before workbook operations"
        ),
        (
            "SSE or streamable HTTP sets EXCEL_FILES_PATH; readable "
            "workbook outside that directory"
        ),
        (
            "route get_excel_path return values through a same-file "
            "identity helper without moving checks"
        ),
    ),
    (
        "mobile-output",
        "3p2m-h2v6-g9mx",
        "f5e32295903128c1e71cf915ae6c0b76c7b0153b",
        ".",
        "src/server.ts",
        (
            "On Linux, screenshot/recording output cannot write outside both "
            "process.cwd() and os.tmpdir() using an ordinary non-symlink "
            "parent"
        ),
        (
            "Linux; a functioning mobile device/toolchain; supported output "
            "extension; existing output parent outside both allowed roots"
        ),
        (
            "alias the default node:fs import as outputFilesystem and "
            "update its member accesses"
        ),
    ),
    (
        "kubernetes-shell",
        "gjv4-ghm7-q58q",
        "ab165f5a0eea917fef5dbae954506fff6f4bf514",
        ".",
        "src/tools/kubectl-get.ts",
        (
            "kubectl_get input cannot cause shell metacharacter execution "
            "while constructing the kubectl command"
        ),
        (
            "kubectl on PATH and initialized Kubernetes configuration; "
            "tool input carrying a shell metacharacter; benchmark never "
            "uses a real cluster"
        ),
        (
            "alias execSync/execFileSync as runKubectlProcess in "
            "kubectl-get.ts while preserving argument structure"
        ),
    ),
]


def artifact(path: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path.read_bytes()),
    }


def rename_python(data: bytes, names: dict[str, str]) -> bytes:
    tokens = tuple(tokenize.tokenize(io.BytesIO(data).readline))
    # Older untokenize versions can rewrite unrelated multiline f-strings.
    if not any(t.type == tokenize.NAME and t.string in names for t in tokens):
        return data
    result = tokenize.untokenize(
        token._replace(string=names.get(token.string, token.string))
        if token.type == tokenize.NAME
        else token
        for token in tokens
    )
    assert isinstance(result, bytes)
    return result


def mutate(family: str, files: dict[str, bytes], source: str) -> dict[str, bytes]:
    result = dict(files)
    text = files[source].decode()
    if family == "git-staging":
        result[source] = rename_python(
            files[source], {"git_add": "stage_repository_files"}
        )
    elif family == "git-arguments":
        line = '    return repo.git.diff(f"--unified={context_lines}", target)'
        assert text.count(line) == 1
        text = text.replace(
            line,
            (
                "    return "
                '_phase20_diff_result(repo.git.diff(f"--unified={context_lines}'
                '", target))'
            ),
        )
        text = text.replace(
            "def git_diff(",
            "def _phase20_diff_result(value):\n    return value\n\n\ndef git_diff(",
            1,
        )
        result[source] = text.encode()
    elif family == "git-repository":
        changed = rename_python(files[source], {"Path": "RepositoryPath"}).decode()
        assert "from pathlib import RepositoryPath" in changed
        result[source] = changed.replace(
            "from pathlib import RepositoryPath",
            "from pathlib import Path as RepositoryPath",
            1,
        ).encode()
    elif family == "filesystem-prefix":
        result[source] = re.sub(
            r"\bvalidatePath\b", "resolvePermittedFile", text
        ).encode()
    elif family == "atlassian-ssrf":
        path = "src/mcp_atlassian/utils/urls.py"
        changed = rename_python(files[path], {"urlparse": "parse_service_url"}).decode()
        assert "from urllib.parse import parse_service_url" in changed
        result[path] = changed.replace(
            "from urllib.parse import parse_service_url",
            "from urllib.parse import urlparse as parse_service_url",
            1,
        ).encode()
    elif family == "atlassian-auth":
        for path, data in files.items():
            if path.startswith("src/") and path.endswith(".py"):
                result[path] = rename_python(
                    data, {"_get_fetcher": "_resolve_service_fetcher"}
                )
    elif family == "atlassian-upload":
        for service in ("jira", "confluence"):
            path = f"src/mcp_atlassian/{service}/attachments.py"
            changed = files[path].decode()
            anchor = "        if not file_path:"
            assert anchor in changed
            changed = changed.replace(
                anchor,
                "        file_path = phase20_upload_source(file_path)\n" + anchor,
            )
            anchor = "from ..utils.io import "
            assert anchor in changed
            changed = changed.replace(
                anchor,
                "from mcp_atlassian.utils.io import phase20_upload_source\n" + anchor,
                1,
            )
            result[path] = changed.encode()
        path = "src/mcp_atlassian/utils/io.py"
        result[path] = (
            files[path] + b"\n\ndef phase20_upload_source(value):\n    return value\n"
        )
    elif family == "excel-boundary":
        start = text.index("def get_excel_path(")
        end = text.index("@mcp.tool", start)
        body = text[start:end]
        body = re.sub(
            r"(?m)^( +)return (.+)$", r"\1return _phase20_path_result(\2)", body
        )
        result[source] = (
            text[:start]
            + "def _phase20_path_result(value):\n    return value\n\n\n"
            + body
            + text[end:]
        ).encode()
    elif family == "mobile-output":
        assert 'import fs from "node:fs";' in text
        text = text.replace(
            'import fs from "node:fs";', 'import outputFilesystem from "node:fs";', 1
        )
        result[source] = (
            "// Modified for Phase 20: alias node:fs; original upstream source "
            "is retained separately.\n" + re.sub(r"\bfs\.", "outputFilesystem.", text)
        ).encode()
    elif family == "kubernetes-shell":
        function = "execFileSync" if "execFileSync" in text else "execSync"
        assert f"import {{ {function} }}" in text
        text = re.sub(rf"\b{function}\b", "runKubectlProcess", text)
        result[source] = text.replace(
            "import { runKubectlProcess }",
            f"import {{ {function} as runKubectlProcess }}",
            1,
        ).encode()
    changed_files = {p: data for p, data in result.items() if data != files[p]}
    if not changed_files:
        raise ValueError(f"mutation did not change {family}")
    return changed_files


def write_overlay(path: Path, files: dict[str, bytes]) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(files.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode = len(data), 0o644
            archive.addfile(member, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as handle:
        handle.write(buffer.getvalue())
    path.write_bytes(compressed.getvalue())


def evidence(files: dict[str, bytes], paths: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "path": p,
            "start_line": 1,
            "end_line": len(files[p].splitlines()),
            "sha256": digest(files[p]),
            "role": (
                "Read the named condition's input, enforcement, and sink in "
                "context; file overlap alone is never a hit."
            ),
        }
        for p in paths
    ]


def prepare() -> None:
    families, inputs = [], []
    snapshots: dict[str, dict[str, Any]] = {}
    trees: dict[str, dict[str, bytes]] = {}
    for (
        name,
        advisory,
        fixed,
        scan_root,
        source,
        condition,
        prerequisites,
        transformation,
    ) in SPECS:
        commit_path = ROOT / f"artifacts/phase20/provenance/{fixed}.json"
        commit = json.loads(commit_path.read_text())
        repository = commit["html_url"].split("github.com/")[1].split("/commit/")[0]
        vulnerable = commit["parents"][0]["sha"]
        families.append(
            {
                "id": name,
                "advisory": artifact(
                    ROOT / f"artifacts/phase20/provenance/GHSA-{advisory}.json"
                ),
                "fix_evidence": artifact(commit_path),
                "vulnerable_revision": vulnerable,
                "fixed_revision": fixed,
                "revision_selection": (
                    "Verified fixing commit and first parent; merge parents and "
                    "bundled changes retained in commit evidence. No release-tag "
                    "substitution."
                ),
            }
        )
        for label, revision in (("vulnerable", vulnerable), ("fixed", fixed)):
            archive = CORPUS / f"snapshots/{revision}.tar.gz"
            files = archive_files(archive.read_bytes(), strip_root=True)
            trees[revision] = files
            licenses = [
                p
                for p in files
                if re.search(r"(?i)(^|/)(license|licence|copying|notice)(\.|$)", p)
            ]
            snapshots[revision] = {
                "repository": repository,
                "revision": revision,
                "url": f"https://api.github.com/repos/{repository}/tarball/{revision}",
                "archive": artifact(archive),
                "files": {p: digest(d) for p, d in sorted(files.items())},
                "licenses": licenses,
            }
            source_path = source if scan_root == "." else f"{scan_root}/{source}"
            paths = [source_path]
            if name.startswith("atlassian-"):
                paths = list(
                    dict.fromkeys(
                        [
                            source_path,
                            "src/mcp_atlassian/servers/main.py",
                            "src/mcp_atlassian/servers/dependencies.py",
                            "src/mcp_atlassian/utils/urls.py",
                            "src/mcp_atlassian/utils/io.py",
                        ]
                    )
                )
                if name == "atlassian-upload":
                    paths += [
                        "src/mcp_atlassian/jira/attachments.py",
                        "src/mcp_atlassian/servers/confluence.py",
                        "src/mcp_atlassian/servers/jira.py",
                    ]
            if name == "filesystem-prefix" and label == "fixed":
                paths.append("src/filesystem/path-validation.ts")
            if name == "mobile-output":
                paths.append("src/utils.ts")
            language = (
                "typescript"
                if name in {"filesystem-prefix", "mobile-output", "kubernetes-shell"}
                else "python"
            )
            runtime = name.startswith("git-")
            item = {
                "id": f"{name}-{label}",
                "family": name,
                "repository": repository,
                "language": language,
                "split": "held_out"
                if name.startswith("atlassian-") or name == "mobile-output"
                else "development",
                "variant": "original",
                "label": label,
                "snapshot": revision,
                "scan_root": scan_root,
                "condition": condition,
                "prerequisites": [prerequisites],
                "static_applicability": (
                    "Source-only Python/TypeScript treatment; recognition limits "
                    "remain in native coverage and do not remove the condition "
                    "from corpus recall."
                ),
                "runtime_applicability": "eligible" if runtime else "unsupported",
                "runtime_reason": (
                    "Existing four-probe stdio campaign; no new exploit or "
                    "targeted probe. Git bootstrap runs only inside Docker."
                )
                if runtime
                else (
                    "Node runtime is unsupported."
                    if language == "typescript"
                    else (
                        "Labeled condition requires HTTP/SSE; stdio would change its "
                        "prerequisites. Existing sandbox supports stdio only."
                    )
                ),
                "runtime_configuration": (
                    "tests/evals/phase20/configuration/git.target.yaml"
                    if runtime
                    else None
                ),
                "evidence": evidence(files, paths),
                "matching": (
                    "Require a finding to describe this specific violated boundary "
                    "and ground the relevant input-to-sink/enforcement flow in the "
                    "cited source. A generic validation, permission, "
                    "authentication, or unrelated secret warning does not qualify "
                    "by rule ID or overlapping lines alone. Human adjudication "
                    "records the finding fingerprint, condition ID, source "
                    "references, decision, and rationale; unmatched findings stay "
                    "unadjudicated."
                ),
                "parent": None,
                "transformation": None,
                "overlay": None,
                "tree_sha256": tree_digest(files),
            }
            inputs.append(item)
            changed = mutate(name, files, source_path)
            overlay_path = CORPUS / f"mutations/{name}-{label}.tar.gz"
            write_overlay(overlay_path, changed)
            mutated = files | changed
            inputs.append(
                item
                | {
                    "id": f"{name}-{label}-mutation",
                    "variant": "mutation",
                    "parent": item["id"],
                    "transformation": transformation,
                    "overlay": artifact(overlay_path),
                    "tree_sha256": tree_digest(mutated),
                    "evidence": evidence(
                        mutated, list(dict.fromkeys(paths + list(changed)))
                    ),
                }
            )
    # Additional labels on existing safe behavior. Byte-identical source reuse is
    # explicit, never presented as five new independent implementations.
    safe = [
        (
            "git-staging",
            "git-status",
            "src/git/src/mcp_server_git/server.py",
            (
                "git_status uses fixed Git status options, with no "
                "caller-provided shell command; missing shell sanitization "
                "here is not a defect"
            ),
            "A valid repository; status has no command-string parameter",
        ),
        (
            "atlassian-upload",
            "atlassian-download-path",
            "src/mcp_atlassian/utils/io.py",
            (
                "validate_safe_path rejects a resolved download destination "
                "outside its supplied base directory; normalization without "
                "checking containment would not suffice"
            ),
            (
                "An explicit base directory, an out-of-base path, and no "
                "filesystem race; download callers consume the checked path or "
                "check the same destination"
            ),
        ),
        (
            "excel-boundary",
            "excel-child-path",
            "src/excel_mcp/server.py",
            (
                "A plain child workbook filename resolving inside "
                "EXCEL_FILES_PATH is permitted in remote mode; accepting this "
                "contained path is not a path-boundary violation"
            ),
            (
                "Remote mode; EXCEL_FILES_PATH set; ordinary existing child "
                "workbook; no symlinks or concurrent path replacement"
            ),
        ),
        (
            "mobile-output",
            "mobile-locale",
            "src/utils.ts",
            (
                "validateLocale rejects values outside its locale regular "
                "expression before locale-changing operations; unrelated path "
                "checks are not the condition"
            ),
            "A caller locale string outside the anchored accepted pattern",
        ),
        (
            "kubernetes-shell",
            "kubernetes-formatting",
            "src/tools/kubectl-get.ts",
            (
                "Formatting parsed Kubernetes response fields using "
                "JSON.stringify does not evaluate those fields as JavaScript "
                "or shell code"
            ),
            (
                "A valid JSON kubectl response, considered only in the "
                "result-formatting flow"
            ),
        ),
    ]
    for family, name, path, condition, prerequisites in safe:
        parent = next(
            i
            for i in inputs
            if i["family"] == family
            and i["variant"] == "original"
            and i["label"] == "fixed"
        )
        inputs.append(
            parent
            | {
                "id": f"{name}-safe",
                "variant": "safe_control",
                "label": "safe",
                "condition": condition,
                "prerequisites": [prerequisites],
                "evidence": evidence(trees[parent["snapshot"]], [path]),
            }
        )
    packet = [artifact(p) for p in sorted((CORPUS / "configuration").glob("*"))]
    packet += [artifact(ROOT / "artifacts/phase20/checkpoint1-packet.md")]
    packet += [artifact(ROOT / "artifacts/phase20/semgrep-preparation.json")]
    manifest = {
        "version": 1,
        "status": "prepared",
        "methodology": (
            "Checkpoint 1 preparation only. No scanner results informed "
            "labels. Public historical cases cannot establish absence of "
            "model exposure. Fixed and safe labels describe only the "
            "stated condition. Reused source trees and shared fixes are "
            "correlated observations. Human approval and independent "
            "review are required before freeze/evaluation."
        ),
        "snapshots": list(snapshots.values()),
        "families": families,
        "inputs": inputs,
        "packet": packet,
    }
    (CORPUS / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


if __name__ == "__main__":
    prepare()
