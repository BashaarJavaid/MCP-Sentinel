## Summary

Describe the user-visible outcome and the smallest implementation that provides it.

## Related issue

Link the accepted issue for a new rule, behavior change, or architecture change.
Direct fixes and documentation changes may use `Not required`.

## Verification

List focused commands and hosted runs, including their results.

- [ ] `make check`
- [ ] Relevant focused tests or acceptance commands are included above.

## Documentation and changelog

- [ ] Public behavior and interfaces are documented, or no documentation change is needed.
- [ ] `CHANGELOG.md` has an Unreleased entry for a user-visible change, or no entry is needed.

## Conditional checks

Complete the items that apply:

- [ ] Rule change: existing IDs retain their meanings; maintainers assigned an ID for any new meaning, and paired vulnerable/fixed/safe fixtures pass.
- [ ] Report change: console, JSON, and SARIF still consume canonical Findings; SARIF validates offline.
- [ ] Security-boundary change: static no-execution or Docker isolation contracts are preserved and tested.

## Feedback regression (when applicable)

- [ ] Link the lifecycle record, reviewed source labels/match conditions, source rights and corpus hashes.
- [ ] Link baseline/corrected reports, complete ordered comparisons, all changed findings/support judgments and retained failures.
- [ ] Link the offline current-candidate CI result and the approved deliberate-regression rejection evidence.
- [ ] Record meaningful coverage changes, limitations, actual milestones and waiting intervals; leave unknown times unknown.
- [ ] AI-assisted drafts received the same review; no automatic label/rule promotion or private-source upload occurred.

Technical review does not authorize publication. Link the separately approved
release contents, version and actions before merge/tag/publication.
