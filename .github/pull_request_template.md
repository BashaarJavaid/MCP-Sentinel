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

- [ ] Rule change: maintainers assigned a new stable ID and paired vulnerable/clean fixtures pass.
- [ ] Report change: console, JSON, and SARIF still consume canonical Findings; SARIF validates offline.
- [ ] Security-boundary change: static no-execution or Docker isolation contracts are preserved and tested.
