# Supplied demo review

Verified 2026-09-04: [MCP-Sentinel](https://www.youtube.com/watch?v=0myxPyTDx2c&t=3s),
author Bashaar Javaid, duration 165 seconds (2:45), public player metadata OK.
`video-metadata.json` retains metadata and the downloaded MP4 hash. Downloaded
video stays in temporary storage rather than duplicating the owner's upload.

The browser runtime had no available browser. The public YouTube player metadata
was fetched, then the supplied video was downloaded with yt-dlp and sampled with
FFmpeg for direct visual review (every 20 seconds, plus five-second samples
across 25–55 and 115–145 seconds). No transcript or audio verification is claimed.

Observed sequence:

- Opening: GitHub **MCP Sentinel v0.1.0** release, older installation/platform text.
- Approximately 20–35 seconds: bundled vulnerable Python fixture and unsafe handlers.
- Approximately 35–55 seconds: rule findings, OWASP IDs, GPT reasoning, dynamic probe
  evidence, and completed pipeline; console identifies recorded replay/no live call.
- Middle: individual JSON findings and model/token/cost telemetry.
- Approximately 125–135 seconds: successful historical clean/vulnerable Action run.
- Approximately 135–145 seconds: GitHub code-scanning “Injection payload executed”
  SENT-010 alert. This is historical positive evidence, not a new 1.2.1 upload.
- Closing: original README, artifact checks, attribution and licensing.

Comparison: 1.2.1 retains the demonstrated Python fixture, static/GPT/Docker
pipeline, 11 stable rule IDs, replay command and SARIF integration. The current
installed-wheel replay independently confirms the outcomes; current cost is zero
and origin telemetry remains historical. New branding, distribution identity,
Python 3.13 host support, TypeScript static analysis, configurable endpoints,
onboarding and adoption workflows are not established by this old recording.
No material conflict prevents reuse as a labeled historical fixture demonstration.

Required adjacent label everywhere the video is reused:
**“2:45 demo; older MCP Sentinel v0.1.0 branding and historical GitHub alerts.”**
Use current installation instructions and retained 1.2.1 evidence for current claims.
