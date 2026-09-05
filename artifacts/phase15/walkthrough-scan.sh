#!/bin/sh
# Run from a clean Linux environment after installation and pinned checkout.
set -eu
python3 --version
sentinel --version
pipx --version
git --version
git -C /work/servers rev-parse HEAD
test -z "$(git -C /work/servers status --porcelain)"
# The container invocation uses env -i; no GPT credentials/config overrides exist.
env | sort
for format in json sarif; do
  code=0
  sentinel scan /work/servers/src/git --static-only --allow-degraded \
    --rules SENT-001,SENT-002,SENT-003,SENT-004,SENT-005,SENT-006,SENT-007 \
    --format "$format" --output "/evidence/walkthrough.$format" || code=$?
  echo "$code" > "/evidence/walkthrough.$format.exit"
  case "$code" in 0|1) ;; *) exit "$code" ;; esac
done
python_tool=/root/.local/share/pipx/venvs/portunusmcp-sentinel/bin/python
"$python_tool" -m sentinel.report.validate_sarif /evidence/walkthrough.sarif
"$python_tool" - <<'PY'
import json
from pathlib import Path
from sentinel.config import OutputFormat, load_configuration
from sentinel.report.validate_json import validate_report_data
report = json.loads(Path('/evidence/walkthrough.json').read_text())
validate_report_data(report)
assert report['analysisComplete'] and report['executionSuccessful']
assert report['findings'] == []
assert report['gpt_review']['batches'] == []
assert report['static_analysis']['selected_rule_ids'] == [f'SENT-{n:03d}' for n in range(1, 8)]
config = load_configuration(Path('/work/servers/src/git'), static_only=True,
    cli_overrides={'rules': [f'SENT-{n:03d}' for n in range(1, 8)], 'format': OutputFormat.JSON})
Path('/evidence/walkthrough-config.json').write_text(config.scanner.model_dump_json(indent=2) + '\n')
print(json.dumps(report, indent=2))
PY
test -z "$(git -C /work/servers status --porcelain)"
