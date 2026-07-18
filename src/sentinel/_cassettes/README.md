# GPT review cassettes

This directory contains sanitized raw Responses API captures keyed by request
fingerprint. Captures are written only by `scripts/capture_gpt_reviews.py
--live`; hand-authored model responses belong in unit tests, not here.

Each checkpoint uses its own directory and manifest. Replay is always labeled
as recorded output and passes through the production parser and host validators.
