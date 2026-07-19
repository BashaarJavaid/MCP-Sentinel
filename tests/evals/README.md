# GPT evaluation cases

`gpt_review_cases.yaml` is the versioned semantic-review truth set. Phase 5 adds
case-specific dynamic expectations for the approved root-cause probe while still
requiring every eligible Docker campaign to execute all four permanent probes.

The ambiguous permission case remains an abstention: dynamic behavior cannot
establish whether its declared scope is broader than the server's real need.
