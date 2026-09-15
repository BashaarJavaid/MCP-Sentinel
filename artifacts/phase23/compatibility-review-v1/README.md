# Historical TypeScript compatibility — execution review

Prepared, not approved or executed: **56 existing inputs twice = 112 observations,
56 ordered report pairs**. The exact inventory remains
[affected-regressions.json](../correction-review-v1/affected-regressions.json).
All 56 source and configuration identities have been checked without scanning;
see [source-validation.json](source-validation.json).

Use [evaluation-proposal.json](evaluation-proposal.json) and
[launcher-binding.json](launcher-binding.json) for exact current scanner, helper,
dependency, source, configuration, report-reference, order and command identities.
The final checkpoint index binds their hashes after local engineering completes.

```bash
.venv/bin/python -I artifacts/phase23/compatibility-review-v1/launch.py
```

The launcher reuses the existing Phase22 supervisor, source validators and native
measurement harness. [runner-delta.patch](runner-delta.patch) and
[launcher-delta.patch](launcher-delta.patch) retain the small changes to the prior
runner: exact affected TypeScript scope, artifact paths and current source identity.
The existing measurement path, historical configuration serialization, scoring and
collection behavior remain. No historical record or validator was edited.
The named six-input schema is reused for Taskwarrior source validation only;
Proxmox is not scanned.

## Order and limits

The first 53 inputs run in their existing group/input order, then repeat. The
three FAF inputs follow, vulnerable/fixed/safe and then repeat. Thus FAF is last.
Groups are memorykeeper, searxng, fetchmcp, openwebsearch, lighthouse, TypeScript
development/historical, Taskwarrior, no-bash and FAF. No Python-only observation.

- Whole input: 1,800 seconds; Semgrep: 10 seconds.
- Cleanup: 15 seconds; existing maximum four workers; inputs run sequentially.
- Outer stage: 3,520 minutes plus 15 seconds outer cleanup. This is a worst-case
  cap, not an estimate. Internal stop is one minute earlier for finalization.
- One attempt per slot; no retry, profile, comparator, target execution or paid call.

The existing supervisor's synthetic startup/cleanup selfcheck runs before the
corpus sequence. It executes only inert dummy Python processes, not target code.
Incomplete output, identity/schema drift, timeout, cleanup failure or unequal
repeat closes the unstarted budget. Detection/support judgments require source
assessment; report collection success is not a case pass.

## Comparison and limitations

Retain the previously used 11 historical volatile-key exclusions listed exactly
in the proposal. All other fields and array order are compared. Preserve every
original report, label, qualification and failed outcome. Assess all changed
findings, warnings, support and entire ordered reference differences after the run.
No unsupported negative or timeout counts as passing compatibility.

FAF's accepted historical reports used an explicitly uncapped experiment and took
more than 1,800 seconds. Normal completion remains unestablished. This proposal
uses the normal deadline and does not authorize optimization, an uncapped retry,
an exemption or conversion of a historical failure to a pass. Phase22's accepted
closeout and other deferrals remain unchanged.
