# Maintenance scripts

`capture_gpt_reviews.py` plans or captures the five approved GPT checkpoints,
including the Phase 3 static-review → Docker-probe → dynamic-review chain.
It defaults to an offline dry run. Paid calls require all of `--live`, an
explicit `--max-usd` ceiling, and `OPENAI_API_KEY` in the environment.
Capture calls use one attempt and reserve each request's worst case immediately
before sending it; accepted usage is then charged against the remaining ceiling.
Production review retries remain unchanged and are covered offline.

`generate_gpt_static_ablation.py` replays the accepted medium/low cassettes and
generates `artifacts/gpt-static-ablation.json`. Phase 3 later adds the Docker
orphan-reaper and the final three-treatment ablation.

`generate_phase5_artifacts.py` produces the final rules/GPT/Docker ablation.
Routine mode uses checked GPT cassettes and isolated Docker campaigns. The
explicit `--live --max-usd 0.50` mode additionally refreshes the checked live
SARIF through a scan-wide hard-budget transport. `--check` validates both
checked judge artifacts without making GPT calls or launching Docker.

`generate_third_party_notices.py` generates or checks the locked runtime
dependency license inventory without an additional package dependency.

`run_github_action.py` is the internal adapter used by the composite Action. It
runs the public CLI once, validates the generated SARIF offline, writes aggregate
Action outputs and the job summary, and preserves the CLI exit-code contract.
It is not a separate public scanner interface.
