# Approved Meta fixed-label erratum

The user approved retaining the frozen condition and adding this erratum. The
original manifest, labels, prerequisites, reports and raw scores remain unchanged.
The condition is not narrowed to default JSON responses.

The fixed snapshot rejects callers without credentials in default JSON mode,
but `--sse-response` attaches middleware to a different application from the one
served by Streamable HTTP. Source analysis consequently reaches the operator
META_ACCESS_TOKEN fallback without caller credentials. This is source evidence,
not runtime exploit confirmation. The earlier review packet and SDK/source hashes
are bound in `packet.json`; its full evidence is retained in integration batch 16.

Both `meta-operator-fallback-fixed` and its structural mutation are affected.
Their four matched finding instances stay visible. Original scoring still shows
**two alerts among 15 nominal fixed/safe cases**. Under this approved erratum,
the clean-case gate has **13 valid fixed/safe cases, zero condition false alarms**;
the two erratum-affected cases are reported separately. They are not added to the
vulnerable denominator. All 25 development inputs completed; the original ten
vulnerable conditions were detected. The caller-owned-credential safe control
remains valid. All 554 unrelated source assessments and their uncertainties remain.

This uses the original source adjudication and its verified identical reports at
6e68331. No detector change, target execution or paid call was needed. Independent
human verification, reviewed benchmarking and the pilot gate remain separate.
