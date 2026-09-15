# ruff: noqa: E402
"Build the approved source-only replacement; no detector or target execution."

import copy
import difflib
import gzip
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from scripts import phase20_measurements as h
from scripts.phase20_corpus import (
    archive_files,
    digest,
    input_files,
    materialize,
    tree_digest,
)
from scripts.phase20_corpus import validate as validate20
from scripts.phase22_corpus import validate

BASE = ROOT / "artifacts/phase22/corpus-replacement-v5"
INTEGRATION = BASE.parent / "integration"
FAMILY = "lighthouse-linklocal"
REPO = "priyankark/lighthouse-mcp"
FREEZE = INTEGRATION / "v23-scanner-freeze-before-v5-curation.json"


def ref(path):
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path.read_bytes()),
    }


def save(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2) + "\n")
    return ref(path)


def main():
    frozen = json.loads(FREEZE.read_text())
    identity = frozen["scanner"]
    actual = h.scanner_identity()
    assert {k: v for k, v in actual.items() if k != "revision"} == {
        k: v for k, v in identity.items() if k != "revision"
    }
    assert not subprocess.check_output(
        [
            "git",
            "diff",
            identity["revision"],
            "--",
            "src",
            "tests",
            "scripts",
            "uv.lock",
            "pyproject.toml",
        ],
        cwd=ROOT,
    )
    for name in ["review", "mutations"]:
        (BASE / name).mkdir(exist_ok=False)
    downloads = json.loads((BASE / "provenance/downloads.json").read_text())["rows"]
    trees, snapshots = {}, []
    for row in downloads:
        path = ROOT / row["archive"]
        assert digest(path.read_bytes()) == row["sha256"]
        files = archive_files(path.read_bytes(), strip_root=True)
        assert len(files) == 12 and b"MIT License" in files["LICENSE"]
        trees[row["label"]] = files
        snapshots.append(
            {
                "repository": REPO,
                "revision": row["revision"],
                "url": row["url"],
                "archive": ref(path),
                "licenses": ["LICENSE"],
                "files": {n: digest(d) for n, d in files.items()},
            }
        )
    a, b = trees["vulnerable"], trees["fixed"]
    changed = sorted(n for n in a if a[n] != b[n])
    assert a.keys() == b.keys() and changed == [
        "package.json",
        "server.json",
        "src/index.ts",
    ]
    assert b"await validateUrl(args.url);" not in a["src/index.ts"]
    assert b"await validateUrl(args.url);" in b["src/index.ts"]
    assert b"{ prefix: '169.254.', mask: null }" in b["src/index.ts"]
    assert (
        b["src/index.ts"].index(b"await validateUrl(args.url);")
        < b["src/index.ts"].index(b"await chromeLauncher.launch(")
        < b["src/index.ts"].index(b"await lighthouse(args.url, options)")
    )
    full_diff = "".join(
        "".join(
            difflib.unified_diff(
                a[n].decode().splitlines(True),
                b[n].decode().splitlines(True),
                fromfile="vulnerable/" + n,
                tofile="fixed/" + n,
            )
        )
        for n in changed
    )
    (BASE / "provenance/full-pair.diff").write_text(full_diff)
    inventory = json.loads(
        (INTEGRATION / "v23-fresh-v4/prior-source-exclusion-inventory.json").read_text()
    )
    assert REPO.casefold() not in {r.casefold() for r in inventory["repositories"]}
    metadata = json.loads((BASE / "provenance/repository.json").read_text())
    assert metadata["full_name"].casefold() == REPO.casefold() and not metadata["fork"]
    prior = {}
    for record in inventory["manifests"]:
        path = ROOT / record["path"]
        assert digest(path.read_bytes()) == record["sha256"]
        m = validate20(path) if path.suffix == ".yaml" else validate(path)
        sources = {s.revision: s for s in m.snapshots}
        for item in m.inputs:
            if item.tree_sha256 not in prior:
                prior[item.tree_sha256] = (
                    item.repository,
                    {
                        n: digest(d)
                        for n, d in input_files(item, sources[item.snapshot]).items()
                    },
                )
    assert len(prior) == inventory["unique_input_tree_count"] == 92
    overlaps = {}
    for label, files in trees.items():
        assert tree_digest(files) not in prior
        rows = []
        for oldtree, (repository, hashes) in prior.items():
            oldhashes = set(hashes.values())
            matches = {n: digest(d) for n, d in files.items() if digest(d) in oldhashes}
            assert not any(n.startswith("src/") for n in matches), (repository, matches)
            if matches:
                rows.append(
                    {
                        "repository": repository,
                        "tree_sha256": oldtree,
                        "same_bytes_any_path": matches,
                    }
                )
        overlaps[label] = rows
    novelty = save(
        BASE / "provenance/novelty.json",
        {
            "passed": True,
            "prior_inventory": ref(
                INTEGRATION / "v23-fresh-v4/prior-source-exclusion-inventory.json"
            ),
            "prior_effective_trees_checked": 92,
            "repository_absent": True,
            "github_fork": False,
            "whole_tree_matches": 0,
            "source_file_matches_any_prior_path": 0,
            "other_file_overlap": overlaps,
            "method": (
                "Verified all six manifests and every unique effective input "
                "tree via existing validators/input_files; compared every can"
                "didate file hash against every path in all92 prior trees. No"
                " detector executed. Byte inequality is not proof of wholly u"
                "nrelated concepts or independent human review."
            ),
            "pre_curation_freeze": ref(FREEZE),
        },
    )
    condition = (
        "The registered run_audit tool rejects the literal http://169"
        ".254.169.254/ before Chrome launch or passing the URL to Lig"
        "hthouse"
    )
    prerequisites = [
        (
            "Use the unmodified upstream stdio entrypoint with the source"
            "-locked SDK1.27.1, Zod4.3.6, Lighthouse12.8.2 and chrome-lau"
            "ncher0.15.2. Existing upstream Server.prototype.setRequestHa"
            "ndler compatibility patch remains present. Registration and "
            "startup succeed; no evaluator monkeypatch or alternative ent"
            "rypoint."
        ),
        (
            "Invoke run_audit with arguments {url: http://169.254.169.254"
            "/}, with categories/device/throttling omitted. The declared "
            "string schema and isValidAuditArgs admit it. No proxy, custo"
            "m URL policy or destination override."
        ),
        (
            "The absolute HTTP URL has the canonical IPv4 link-local host"
            "name169.254.169.254; Node URL/net classification succeeds wi"
            "thout DNS. Fixed source reaches the169.254. prefix with null"
            " mask and throws before the Chrome launch. Vulnerable source"
            " has no URL policy before that boundary."
        ),
        (
            "For vulnerable onward delivery, normal temporary-directory a"
            "ccess and Chrome startup must succeed; these are unexecuted "
            "prerequisites. The named condition is pre-launch rejection, "
            "not a successful network request, reachable metadata service"
            ", credential access, completed audit or runtime proof. No ta"
            "rget, dependencies, browser or build is run."
        ),
        (
            "Other tools, redirects, DNS resolution/rebinding, IPv6 and r"
            "esponse contents are outside this label. Upstream intentiona"
            "lly allows loopback; its DNS-error branch returns without re"
            "jection. Fixed means only the named literal condition, not c"
            "omplete SSRF protection."
        ),
    ]
    roles = {
        "src/index.ts": (
            "Complete startup, upstream SDK compatibility patch, tool lis"
            "t/dispatch, argument predicate, link-local policy (fixed), C"
            "hrome launch, Lighthouse call and output/error paths."
        ),
        "src/types.d.ts": (
            "Retained Lighthouse type declarations; no runtime execution."
        ),
        "package.json": (
            "Actual0.1.12/0.1.13 source package versions, ESM entrypoint "
            "and dependency declarations."
        ),
        "package-lock.json": (
            "Identical dependency lock in both revisions: root metadata r"
            "emains0.1.11; SDK1.27.1/Zod4.3.6/Lighthouse12.8.2/chrome-lau"
            "ncher0.15.2. No installation."
        ),
        "server.json": "Published MCP registry identity/version declaration.",
        "tsconfig.json": "NodeNext compilation/discovery settings retained unmodified.",
    }

    def evidence(files):
        return [
            {
                "path": n,
                "start_line": 1,
                "end_line": len(files[n].splitlines()),
                "sha256": digest(files[n]),
                "role": role,
            }
            for n, role in roles.items()
        ]

    oldpath = ROOT / "artifacts/phase22/corpus-replacement-v4/manifest.json"
    old = json.loads(oldpath.read_text())
    # Preserve the exact preceding45 records; replace only the final five-input slot.
    retained = old["inputs"][:-5]
    assert len(retained) == 45
    template = old["inputs"][-5]
    inputs, mutations = [], []
    for row in downloads:
        label = row["label"]
        files = trees[label]
        item = {
            **copy.deepcopy(template),
            "id": FAMILY + "-" + label,
            "family": FAMILY,
            "repository": REPO,
            "snapshot": row["revision"],
            "label": label,
            "condition": condition,
            "prerequisites": prerequisites,
            "evidence": evidence(files),
            "tree_sha256": tree_digest(files),
        }
        inputs.append(item)
        oldsym, newsym = b"isValidAuditArgs", b"hasAuditArguments"
        assert not any(newsym in d for d in files.values())
        assert files["src/index.ts"].count(oldsym) == 3
        affected = {
            "src/index.ts": re.sub(
                rb"\bisValidAuditArgs\b", newsym, files["src/index.ts"]
            )
        }
        assert affected["src/index.ts"].replace(newsym, oldsym) == files["src/index.ts"]
        overlay = BASE / f"mutations/{label}-argument-helper-rename.tar.gz"
        with (
            overlay.open("wb") as stream,
            gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz,
            tarfile.open(fileobj=gz, mode="w") as tar,
        ):
            for n, d in affected.items():
                member = tarfile.TarInfo(n)
                member.size = len(d)
                member.mode = 0o644
                tar.addfile(member, io.BytesIO(d))
        assert archive_files(overlay.read_bytes(), strip_root=False) == affected
        mutated = {**files, **affected}
        transformation = (
            "Rename the local isValidAuditArgs predicate and both calls t"
            "o hasAuditArguments; all three identifiers reverse exactly. "
            "No argument, URL, branch, import, dispatch or startup semant"
            "ics change."
        )
        inputs.append(
            {
                **copy.deepcopy(item),
                "id": item["id"] + "-mutation",
                "variant": "mutation",
                "parent": item["id"],
                "overlay": ref(overlay),
                "transformation": transformation,
                "tree_sha256": tree_digest(mutated),
                "evidence": evidence(mutated),
            }
        )
        mutations.append(
            {
                "label": label,
                "overlay": ref(overlay),
                "identifier_occurrences": 3,
                "reverse_rename_matches_original_bytes": True,
                "original_tree_sha256": item["tree_sha256"],
                "mutated_tree_sha256": tree_digest(mutated),
            }
        )
    inputs.append(
        {
            **copy.deepcopy(inputs[2]),
            "id": "lighthouse-public-safe",
            "variant": "safe_control",
            "label": "safe",
            "condition": (
                "The fixed run_audit initial destination policy permits the p"
                "ublic IPv4 literal http://8.8.8.8/ without classifying it as"
                " blocked link-local/private"
            ),
            "prerequisites": [
                (
                    "Same unmodified fixed source/startup/argument prerequisites,"
                    " with url=http://8.8.8.8/ and optional arguments omitted. On"
                    "ly the initial classification is scored; no public service a"
                    "vailability, successful browser navigation, response safety "
                    "or complete audit is claimed."
                )
            ],
        }
    )
    assert all(i["tree_sha256"] not in prior for i in inputs)
    review = save(
        BASE / "review/condition-review.json",
        {
            "reviewer": (
                "Same implementation agent, after immutable scanner freeze; n"
                "o independent human/unseen-source review."
            ),
            "freeze": ref(FREEZE),
            "scanner": identity,
            "condition": condition,
            "prerequisites": prerequisites,
            "flow": (
                "new LighthouseServer -> run stdio -> SDK CallToolRequestSche"
                "ma handler -> run_audit -> this.handleRunAudit -> isValidAud"
                "itArgs -> [fixed await validateUrl] -> temporary-directory s"
                "etup -> chromeLauncher.launch -> lighthouse(args.url,options"
                ")."
            ),
            "label_basis": (
                "Canonical169.254.169.254 is not loopback; fixed literal bran"
                "ch calls isBlockedIP, whose169.254. prefix entry has null ma"
                "sk and returns true. The guard throws before Chrome. Vulnera"
                "ble source proceeds toward Chrome/Lighthouse after only type"
                " checks. Public8.8.8.8 matches no blocked prefix."
            ),
            "correlation": (
                "One repository and one narrow upstream vulnerability; origin"
                "al pair plus two reversible renames and one fixed-tree contr"
                "ol, not five independent discoveries."
            ),
            "limitations": (
                "Known source-exposure, class dispatch and third-party Lighth"
                "ouse call remain intact. No detector support or hit is predi"
                "cted. Source novelty is relative to recorded prior corpora; "
                "SSRF/browser concepts overlap earlier families. Upstream rep"
                "ort mentions both tools and broad impact; only run_audit lit"
                "eral pre-launch rejection is labeled here. Loopback intentio"
                "nally allowed, DNS errors fail open, redirects and IPv6 outs"
                "ide label."
            ),
            "metadata_discrepancies": (
                "package.json and server.json advance0.1.12 to0.1.13; unchang"
                "ed lock root remains0.1.11 and runtime server identity0.1.0."
                " Source revisions and actual lock contents, not those stale "
                "version strings, bind this pair."
            ),
            "mutations": mutations,
            "scanner_evaluation": False,
            "comparator_evaluation": False,
            "target_execution": False,
            "model_calls": 0,
        },
    )
    comparison = save(
        BASE / "provenance/pair-comparison.json",
        {
            "vulnerable_revision": downloads[0]["revision"],
            "fixed_revision": downloads[1]["revision"],
            "direct_parent": True,
            "changed_files": [
                {
                    "path": n,
                    "vulnerable_sha256": digest(a[n]),
                    "fixed_sha256": digest(b[n]),
                }
                for n in changed
            ],
            "full_diff": ref(BASE / "provenance/full-pair.diff"),
            "projection": (
                "None: all12 files retained including LICENSE and screenshot;"
                " no target execution."
            ),
            "source_review": review,
        },
    )
    newrefs = (
        [ref(p) for p in sorted((BASE / "provenance").iterdir()) if p.is_file()]
        + [review]
        + [m["overlay"] for m in mutations]
    )
    manifest = copy.deepcopy(old)
    manifest["methodology"] = (
        "Replacement-v5: one novel Lighthouse MCP repository source p"
        "air after immutable1f3f72f freeze, selected on public upstre"
        "am report/fix and source compatibility, never detector outco"
        "mes. Only five replacement records run. Retain other45 recor"
        "ds exactly and all rejected/exposed corpora. No independent "
        "human or unseen-source claim."
    )
    manifest["snapshots"] += snapshots
    manifest["pairs"] = [
        *old["pairs"][:-1],
        {
            "id": FAMILY,
            "rule_id": "SENT-015",
            "fix_origin": "upstream",
            "provenance": [comparison, review, novelty],
            "review": (
                "Direct-parent link-local pre-launch SSRF guard fix; source-s"
                "pecific labels, reversible predicate renames and public cont"
                "rol. Evaluation separately gated."
            ),
        }
    ]
    manifest["inputs"] = retained + inputs
    manifest["packet"] += newrefs
    manifest["repository_aliases"][REPO.casefold()] = REPO
    manifestref = save(BASE / "manifest.json", manifest)
    validated = validate(BASE / "manifest.json")
    assert validated and manifest["inputs"][:45] == old["inputs"][:45]
    configs = {}
    snapshotmap = {s.revision: s for s in validated.snapshots}
    for item in validated.inputs[-5:]:
        with tempfile.TemporaryDirectory(prefix="phase22-v5-source-only-") as temp:
            target = materialize(
                item,
                snapshotmap[item.snapshot],
                Path(temp).resolve() / "source",
                validated.packet,
            )
            config = h.load_configuration(
                target,
                environ={},
                static_only=True,
                cli_overrides={
                    "rules_only": True,
                    "ignore_paths": [".phase20/**"],
                    "max_findings_per_scan": 500,
                },
                llm_cli_overrides={
                    "model": h.LLM.model,
                    "reasoning_effort": "medium",
                    "retries": 0,
                    "max_concurrency": 1,
                    "cache_enabled": False,
                },
            )
            payload = {
                "scanner": config.scanner.model_dump(mode="json"),
                "target": config.target.model_dump(mode="json")
                if config.target
                else None,
                "static_only": config.static_only,
                "language": config.language.value,
            }
            configs[item.id] = {
                "configuration": payload,
                "sha256": digest(
                    (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
                ),
            }
    configref = save(BASE / "configurations.json", configs)
    oldproposal = json.loads((oldpath.parent / "evaluation-proposal.json").read_text())
    checkpoint = save(
        BASE / "checkpoint-1f3f72f.json",
        {
            "status": "prepared_pending_explicit_evaluation_approval",
            "manifest": manifestref,
            "pre_curation_freeze": ref(FREEZE),
            "source_only_authorization": ref(
                INTEGRATION / "v23-source-only-recovery-authorization.json"
            ),
            "scanner_identity": identity,
            "harness_and_lock_sha256": {
                name: digest((ROOT / name).read_bytes())
                for name in [
                    "uv.lock",
                    "scripts/phase20_corpus.py",
                    "scripts/phase22_corpus.py",
                    "scripts/phase20_measurements.py",
                    "scripts/phase20_scoring.py",
                    "scripts/prepare_phase20_semgrep.py",
                    "artifacts/phase20/semgrep-preparation.json",
                ]
            },
            "configuration": configref,
            "new_input_ids": [i["id"] for i in inputs],
            "unchanged_input_records": 45,
            "source_archives": [s["archive"] for s in snapshots],
            "novelty": novelty,
            "review": review,
            "freeze_approved": False,
            "scanner_evaluation": False,
            "comparator_evaluation": False,
            "target_execution": False,
            "model_calls": 0,
            "source_exposure_disclosure": manifest["methodology"],
            "proposed_bounds": oldproposal["bounds"],
        },
    )
    proposal = copy.deepcopy(oldproposal)
    proposal.update(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        checkpoint=checkpoint,
        manifest=manifestref,
        configuration=configref,
        pre_curation_freeze=ref(FREEZE),
        input_order=[i["id"] for i in inputs],
        prior_results=(
            "Preserve original/v1-v4 results and rejected v4 novelty. Thi"
            "s novel Lighthouse repository contributes one correlated vul"
            "nerability, curated by the implementation agent after scanne"
            "r freeze; no independent human or unseen-source claim."
        ),
    )
    proposal["source_only_authorization"] = ref(
        INTEGRATION / "v23-source-only-recovery-authorization.json"
    )
    proposal["condition_review"] = review
    proposal["novelty"] = novelty
    proposal["scope_change"] = (
        "Replace only the invalid v4 SENT-015 five-input slot with th"
        "e novel Lighthouse pre-launch link-local condition. No requi"
        "rement, timing, label-after-evaluation, scanner or harness w"
        "aiver."
    )
    proposalref = save(BASE / "evaluation-proposal.json", proposal)
    files = {
        p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
        for p in BASE.rglob("*")
        if p.is_file()
    }
    files[FREEZE.relative_to(ROOT).as_posix()] = digest(FREEZE.read_bytes())
    save(
        BASE / "preparation.json",
        {
            "passed": True,
            "manifest": manifestref,
            "checkpoint": checkpoint,
            "proposal": proposalref,
            "all50_records_validated": True,
            "unchanged45_records_exact": True,
            "five_source_only_materializations_and_configurations": True,
            "novelty": novelty,
            "prepared_files_sha256": files,
            "observations": 0,
            "paid_calls": 0,
            "target_execution": False,
        },
    )
    assert h.scanner_identity() == actual
    print(
        json.dumps(
            {
                "proposal": proposalref,
                "checkpoint": checkpoint,
                "inputs": [i["id"] for i in inputs],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
