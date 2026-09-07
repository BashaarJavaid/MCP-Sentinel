"""Caller references must not become Git options through their argument position."""

from pathlib import Path
from uuid import uuid4

import pytest
import time

from sentinel.config import load_configuration
from sentinel.static.engine import run_static_scan
from tests.conftest import NOW, make_target
from sentinel.static.model import RuleRunState, TypeScriptSourceFile
from sentinel.static.typescript_discovery import TypeScriptProgram
from sentinel.static.typescript_path_flow import analyze
from sentinel.static.rules.sent014 import TypeScriptOptionFlow


@pytest.mark.parametrize(
    ('body', 'expected'),
    [
        ('return repo.git.diff(ref)', 1),
        ('return repo.git.checkout(ref, "--")', 1),
        ('return repo.git.show(ref)', 1),
        ('return repo.git.diff("--", ref)', 0),
        ('return repo.git.diff("--end-of-options", ref)', 0),
        ('if ref.startswith("-"): raise ValueError()\n    return repo.git.diff(ref)', 0),
        ('ref.startswith("-")\n    return repo.git.diff(ref)', 1),
        ('if other.startswith("-"): raise ValueError()\n    return repo.git.diff(ref)', 1),
        ('if ref.startswith("-"): raise ValueError()\n    ref = other\n    return repo.git.diff(ref)', 1),
        ('return repo.git.diff(f"--unified={ref}")', 0),
        ('return repo.git.diff("HEAD")', 0),
        ('return repo.commit(ref)', 0),
    ],
)
def test_python_git_reference_option_position(tmp_path: Path, body: str, expected: int) -> None:
    root=make_target(tmp_path/'target',target_yaml='')
    (root/'server.py').write_text(
        'from mcp.server.fastmcp import FastMCP\nimport git\nmcp=FastMCP("test")\n'
        '@mcp.tool()\ndef diff(ref:str, other:str=""):\n'
        '    repo=git.Repo("/workspace")\n    '+body+'\n',encoding='utf-8',
    )
    configuration=load_configuration(root,environ={},static_only=True,
                                     cli_overrides={'rules':['SENT-014']})
    result=run_static_scan(configuration,uuid4(),timestamp=NOW)
    assert len(result.findings)==expected
    assert all(f.rule_id=='SENT-014' for f in result.findings)


@pytest.mark.parametrize(('body','expected'), [
    ('return cp.execFileSync("git", ["show", ref]);', 1),
    ('return cp.spawnSync("git", ["diff", "--", ref]);', 0),
    ('return cp.spawnSync("git", ["diff", ref, "--"]);', 1),
    ('if (ref.startsWith("-")) throw new Error(); return cp.execFileSync("git", ["show", ref]);', 0),
    ('ref.startsWith("-"); return cp.execFileSync("git", ["show", ref]);', 1),
    ('if (other.startsWith("-")) throw new Error(); return cp.execFileSync("git", ["show", ref]);', 1),
    ('if (ref.startsWith("-")) throw new Error(); ref = other; return cp.execFileSync("git", ["show", ref]);', 1),
    ('const repo = simpleGit(); return repo.diff([ref]);', 1),
    ('const repo = simpleGit(); return repo.diff(["--", ref]);', 0),
])
def test_typescript_git_option_positions(tmp_path: Path, body: str, expected: int) -> None:
    source = ('import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
              'import cp from "node:child_process"; import {simpleGit} from "simple-git";\n'
              'const server = new McpServer({name:"test", version:"1"});\n'
              f'function run({{ref, other}}: {{ref: string, other: string}}) {{ {body} }}\n'
              'server.registerTool("run", {inputSchema: {ref:z.string(),other:z.string()}}, run);\n')
    path=tmp_path/'server.ts'; path.write_text(source,encoding='utf-8')
    program=TypeScriptProgram((TypeScriptSourceFile(path,path.name,source),),deadline=time.monotonic()+15)
    state=RuleRunState()
    analyze(program,state,flow=TypeScriptOptionFlow(program,state))
    assert len(state.matches)==expected
    assert all(m.rule_id=='SENT-014' for m in state.matches)
