# Checkpoint 2 completion outcome

The user approved the exact request packet with “continue”. All 18 named requests were accepted on their first attempt under this decision. The previously failing Excel fixed-mutation request now validates, including its nullable `table_name` injection binding. No retries or further paid requests were made.

The complete ledger contains 39 attempts: 35 accepted and four earlier failures. All 17 previously accepted captures were reused with their original provenance. New accepted usage cost is $0.429571; total accepted usage cost is $0.804567. Including unresolved earlier failed-attempt reservations, cumulative accounting is $1.211247, below the approved $3.72 total ceiling. The attempt ceiling is exhausted; this approval authorizes no further new attempts.

The 18 requests contain 19 unique candidate decisions: six confirmed, ten suppressed, and three `needs_review`. Shared captures may occur in multiple corpus inputs; per-input decision counts are reported separately. Confirmation here is a model review decision, not runtime proof. None of the newly accepted decisions identifies the labeled remote workbook boundary or mobile output-path traversal vulnerability. See [the condition review](new-capture-condition-review.json).

Evidence: [approval](checkpoint2-approval.json), [accounting](checkpoint2-outcome.json), [ledger](captures/ledger.json), [named request proposal](checkpoint2-proposal.json), and [prepared production requests](prepare-live/results.json). The original baseline ledger remains unchanged outside this versioned directory.

Static replay and Docker results are separate measurements. This decision does not authorize runtime review, a changed corpus/runtime configuration, phase acceptance, merge, or public deployment.
