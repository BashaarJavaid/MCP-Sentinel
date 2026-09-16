# Phase 23 checkpoint 1: intake and maintenance wording

**Prepared for review; not adopted.** Base: `dd9101ddfead19d65b7a84b374e4cf7e85462ff7`
on `main` (accepted Phase 22 implementation and closeout merge). The user's
Phase 23 implementation request authorizes preparation; its explicit checkpoints
still govern adoption, source freeze, evaluations, correction and release.

## Decision requested

Approve the exact [proposed changes](proposed-changes.patch),
[lifecycle fields](lifecycle-template.json), and
[weekly review fields](weekly-review-template.json) for adoption, or identify
wording to revise. The patch includes the complete maintenance checklist and
record field definitions in its proposed `docs/phase23-maintenance.md` addition.

This decision covers intake/contribution/maintenance wording and record formats.
Source labels and bytes, manifest freeze, baseline commands/budget, detector
correction, candidate evaluation, technical acceptance, and version/publication
each retain their separate review checkpoint. No version has been selected.

The user's plan requires: **“Present exact form wording, record fields and
maintenance checklist for your review before adopting them.”** This is the
reason for the checkpoint; it is not an additional skill approval requirement.

## Exact proposed edits

The unapplied patch updates these existing files in place and adds the two named
files only when approved:

| File | Proposed change |
| --- | --- |
| `.github/ISSUE_TEMPLATE/false-positive.yml` | Current SENT-001–016 choices, reproducible source/config/report evidence, explicitly unreviewed expectation. |
| `.github/ISSUE_TEMPLATE/rule-proposal.yml` | Current related-rule choices, environment/configuration, fixed/safe controls and reviewed rule meaning. |
| `.github/ISSUE_TEMPLATE/missed-vulnerability.yml` (new) | Missing-finding evidence, source path, full diagnostics and support status, fixed/safe controls. |
| `.github/ISSUE_TEMPLATE/config.yml` | Existing private Sentinel reporting and maintenance links. |
| `CONTRIBUTING.md`, `docs/contributing.md`, `SECURITY.md` | Disclosure route, sanitization, source rights, reviewed labels and feedback loop. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Lifecycle/corpus/result/rejection evidence; distinguish correction from a new rule meaning. |
| `docs/phase23-maintenance.md` (new), `mkdocs.yml` | Maintainer ownership, eight-step feedback loop, Monday checklist, lifecycle field definitions, release review and verification. |
| `docs/hackathon.md` | Link the current release checklist above preserved historical release evidence. |
| `CHANGELOG.md` | Unreleased guidance/intake entry; no detector or release claim. |

All three forms require sanitization and source provenance. Each separately offers
this **optional** checkbox:

> I have the right to license my submitted examples and permit their reuse and
> modification in Sentinel's regression corpus under the project's MIT license.

Unchecked consent remains a valid report. Corpus incorporation requires consent
or an applicable license; otherwise obtain permission. Sensitive Sentinel issues
use the existing private advisory channel; third-party disclosures follow upstream
policy. The patch makes no outbound contact.

## Maintenance and records

BashaarJavaid owns review and acceptance. The proposed manual checklist is Monday
09:00 America/Los_Angeles, with the actual daylight-saving offset reflected in
UTC. It records SDK/advisory sources checked, decisions, evidence and missed
reviews. Adoption starts the cadence; no scheduled service or response deadline
is introduced.

The two JSON files are **templates**, not completed lifecycle or weekly records.
The selected revisions are copied from the user's plan and await source verification.
All source rights, reviewed labels, corpus/scanner identities, milestones, release
choices and elapsed times remain unknown or pending. Advisory publication and
Phase 23 intake are separate fields; later recording cannot establish a historical
receipt time. Waiting intervals retain their own evidence and endpoints.

The [upstream advisory](https://github.com/alfonsograziano/node-code-sandbox-mcp/security/advisories/GHSA-5w57-2ccq-8w95)
was read during preparation and lists affected versions through 1.2.0 and patched
versions from 1.3.0. Complete snapshot/provenance retention, license review and the
registration-to-sink source assessment belong to the next preparation checkpoint.
Reading the advisory does not establish a Sentinel reproduction or source label.

## Verification and remaining implementation

See [verification and hashes](verification.json): patch applicability passed;
all three YAML forms parsed and passed current-catalog/field/consent checks;
both JSON templates passed consistency checks; proposed documentation and navigation
built with strict MkDocs in a temporary copy. Tracked repository files remain
unchanged. The pre-existing untracked Phase 22 user documents were preserved.
No full test suite or hosted run was needed or claimed for this unapplied draft.

After wording approval, apply the patch and prepare the seven source inputs for
review. Implement `scripts/phase23_regression.py` and `tests/test_phase23.py`
against the approved source/expectation contract, then add the current-candidate
CI invocation after evaluation review. Existing archive/hash and report utilities
are available for reuse. The existing Phase 20 `stable_report` sorts findings
and selects report fields, so it cannot establish the required entire ordered
report equality; exclusions must be explicitly reviewed before implementation.
Historical validators and measurements remain intact.

**Phase 23 is incomplete.** Zero advisory scans, target executions or paid calls
occurred. No detector changes, CI dispatches, source freeze, merge, tags or
publication occurred. Phase 22's accepted limitations, Proxmox/FAF deferrals,
Git's incomplete evaluation, paid benchmark/pilot deferrals and Phase 21/24/15
states remain unchanged.
