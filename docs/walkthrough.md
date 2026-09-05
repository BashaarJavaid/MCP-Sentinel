# Scan a real MCP server before release

A useful first scan should be repeatable without trusting the target enough to
run it. This walkthrough uses PortunusMCP Sentinel 1.2.1 to inspect the official
[MCP Git server source](https://github.com/modelcontextprotocol/servers/tree/d73f99efbfd40c3aa1b61e88728b3d49fb52608f/src/git).
It keeps the checkout untouched, selects all seven static rules, and writes
reports outside the target. The observed result is **zero findings**, with one
rule skipped. That is a coverage result, not a claim that this server is
vulnerability-free.

## Prepare an isolated environment

Use Linux, Python 3.12, Git, and [pipx](https://pipx.pypa.io/stable/installation/).
Start in a new working directory. Package installation and cloning need network
access; the scans themselves can run offline. No Docker is needed for this
walkthrough. The published-package verification used Python 3.12.14 and pipx 1.16.0
inside a fresh Linux container, installing 1.2.1 directly from public PyPI. The
[launch evidence](https://github.com/BashaarJavaid/MCP-Sentinel/tree/main/artifacts/phase15)
retains both the earlier candidate-wheel rehearsal and the successful public
installation, including validated reports, effective configuration, and hashes.

```sh
python3 --version
pipx install portunusmcp-sentinel==1.2.1
sentinel --version
mkdir sentinel-walkthrough
cd sentinel-walkthrough
git clone https://github.com/modelcontextprotocol/servers.git servers
git -C servers checkout --detach d73f99efbfd40c3aa1b61e88728b3d49fb52608f
git -C servers rev-parse HEAD
git -C servers status --porcelain
mkdir reports
```

The revision must match exactly, and the status command should print nothing.
We scan only `servers/src/git`, not every server in the monorepo. Do not run
`sentinel init`, create permission grants, install the Git server's dependencies,
or start its entry point. Sentinel reads source without importing target modules
or contacting a running MCP endpoint.

## Run the selected static checks

The following POSIX-shell function removes ambient environment variables for
each scan. It preserves only the executable search path, so no GPT credentials,
`SENTINEL_*` overrides, or OpenAI routing variables reach Sentinel. This pinned
target has no `sentinel.toml`; built-in defaults apply, including the high
failure threshold. The explicit rule list prevents accidental reliance on a
narrower selection. Keep these commands in the same shell and directory.

```sh
scan_report() {
  format=$1
  code=0
  env -i PATH="$PATH" sentinel scan servers/src/git \
    --static-only --allow-degraded \
    --rules SENT-001,SENT-002,SENT-003,SENT-004,SENT-005,SENT-006,SENT-007 \
    --format "$format" --output "reports/git.$format" || code=$?
  printf '%s\n' "$code" > "reports/git.$format.exit"
  case "$code" in
    0|1) ;;
    *) printf 'Walkthrough verification failed: exit %s\n' "$code" >&2; return "$code" ;;
  esac
}
scan_report json && scan_report sarif
```

Exit `0` and `1` both mean a completed scan. Exit `1` means a finding reached
the failure threshold; it does not mean the scanner malfunctioned. Exit `2`
indicates invalid input or configuration, and exit `3` indicates incomplete or
failed analysis. Either makes this walkthrough verification unsuccessful: retain
the diagnostics and resolve the cause before interpreting any report.

## Read the actual result

Both retained scans exited `0`, inspected five files, and produced no findings
or warnings. Native JSON reports schema `1.4.0`; SARIF remains `2.1.0`.
The JSON and SARIF came from separate invocations, so timestamps and scan IDs
differ. Their substantive results agree.

| Rules | Observed outcome |
|---|---|
| SENT-001 | Skipped: `sentinel.permissions.yaml` is absent |
| SENT-002–SENT-007 | Evaluated; zero matches |
| SENT-008–SENT-011 | Dynamic probes excluded by `--static-only` |

Do not add a permissions file merely to make the skipped row disappear: that
would change the experiment. “Evaluated” also does not mean every handler or
possible vulnerability was understood. Rules recognize bounded source patterns;
indirection, imported implementations, and behavior outside the scan root can
escape their coverage. This scan does not audit the target's installed
dependencies or exercise its runtime authorization.

`--allow-degraded` permits deterministic candidates to remain `needs_review`
when GPT review is unavailable. Here there were no candidates to review and
none were confirmed. The report's GPT summary labels its configured mode
`live`, but contains **zero batches, zero tokens, and zero current cost**;
no model call occurred. A successful empty review stage is not GPT endorsement.

Sentinel validates reports before writing them. For an independent offline
check, use the Python interpreter in pipx's isolated Sentinel environment:

```sh
tool_python="$(pipx environment --value PIPX_LOCAL_VENVS)/portunusmcp-sentinel/bin/python"
"$tool_python" -c 'import json; from sentinel.report.validate_json import validate_report_data; validate_report_data(json.load(open("reports/git.json")))'
"$tool_python" -m sentinel.report.validate_sarif reports/git.sarif
git -C servers status --porcelain
sha256sum reports/git.json reports/git.sarif
```

## Try isolated dynamic proof separately

With Docker running, `sentinel demo --replay-review --output-dir demo-results`
uses the bundled deliberately vulnerable Python fixture. It reuses **recorded
GPT responses** while executing **new Docker probes**. It does not dynamically
test the public Git server above. See the [installation requirements](install.md)
and [rule boundaries](rules.md) before applying full scans to other targets.

The [2:45 demo by Bashaar Javaid](https://www.youtube.com/watch?v=0myxPyTDx2c&t=3s)
shows older **MCP Sentinel v0.1.0** branding and historical GitHub alerts. Its
fixture/replay demonstration remains relevant; use this page's 1.2.1 install
command and current reports for launch verification. Share reproducible false
positives or missed patterns through [issues](https://github.com/BashaarJavaid/MCP-Sentinel/issues),
and sensitive vulnerabilities through the
[private reporting form](https://github.com/BashaarJavaid/MCP-Sentinel/security/advisories/new).
