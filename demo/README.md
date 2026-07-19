# MCP Sentinel demo

The judged demo uses the canonical vulnerable fixture from
`tests/fixtures/vulnerable_server`. The wheel maps that fixture into Sentinel's
package resources, so installed users do not need a source checkout.

Run the reproducible offline path with:

```bash
sentinel demo --replay-review
```

Run `sentinel demo` with `OPENAI_API_KEY` set for a live GPT review. Both modes
write validated reports to `./sentinel-demo-results/` unless `--output-dir` is
provided. See `docs/demo.md` for the full judge runbook.
