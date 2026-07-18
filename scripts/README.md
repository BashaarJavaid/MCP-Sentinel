# Maintenance scripts

`capture_gpt_reviews.py` plans or captures the four approved GPT checkpoints.
It defaults to an offline dry run. Paid calls require all of `--live`, an
explicit `--max-usd` ceiling, and `OPENAI_API_KEY` in the environment.
Capture calls use one attempt and reserve each request's worst case immediately
before sending it; accepted usage is then charged against the remaining ceiling.
Production review retries remain unchanged and are covered offline.

`generate_gpt_static_ablation.py` replays the accepted medium/low cassettes and
generates `artifacts/gpt-static-ablation.json`. Phase 3 later adds the Docker
orphan-reaper and the final three-treatment ablation.
