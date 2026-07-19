# Generated artifacts

Judge-facing evidence in this directory is generated, never hand-edited.

- `gpt-ablation.json` compares rules-only, GPT-reviewed, and GPT-plus-Docker
  results over the checked truth set. Regenerate it offline with `make artifacts`.
- `example.sarif` is the final live vulnerable-fixture report. Refresh it only
  with `MAX_USD=0.50 make artifacts-live`; the command enforces that hard ceiling.
- `phase4-action-evidence.md` records the accepted live GitHub Action proof.

Run `make artifacts-check` to validate the ablation quality gate, SARIF schema,
live-review telemetry, and the exact `SENT-001` through `SENT-011` result set.
