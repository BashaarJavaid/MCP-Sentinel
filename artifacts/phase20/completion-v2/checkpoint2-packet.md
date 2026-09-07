# Phase 20 corrected-scanner completion: Checkpoint 2 proposal

Status: awaiting the user's budget decision. This packet authorizes no paid calls and does not accept Phase 20.

The refreshed production preparation contains 35 exact requests. All request hashes and input memberships match the original preparation; 17 accepted captures remain valid under the corrected reviewer and will be reused. The remaining 18 include the previously rejected Excel fixed-mutation request. Its nullable-field validator is corrected, but another provider or validation failure remains possible.

| Budget item | Amount |
| --- | ---: |
| Previous attempts | 21 (17 accepted, 4 failed) |
| Proposed additional attempts | 18 |
| Proposed cumulative attempt ceiling | 39 |
| Accepted usage cost | $0.374996 |
| Failed-attempt reservations retained | $0.406680 |
| Prior conservative accounting | $0.781676 |
| Additional conservative reservation | $1.888920 |
| Conservative cumulative total | $2.670596 |
| Proposed cumulative dollar ceiling | $3.72 |

The dollar ceiling is unchanged and includes previous spending. The previous 38-attempt ceiling cannot accommodate all 18 remaining requests after 21 recorded attempts. Stop on the first failed or unaffordable request, retaining successful captures and unresolved reservations. Another attempt after a stop requires another user decision. No automatic retries, parallel requests, or local review cache.

Use production GPT-5.6 Sol at medium, with the native 500-finding cap. Exact endpoint, timeout, output caps, and configuration are in [the native packet](prepare-live/budget-packet.json). Pricing verified 2026-09-06 against [the official model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-sol): $4/M input, $0.40/M cached input, $20/M output; cache-write input multiplier 1.25, with long-context premiums recorded in the packet. Reservations use serialized UTF-8 bytes plus 4096 framing tokens, charge all input at cache-write rate, and reserve the full output cap.

## Evidence identities

- Scanner revision: `8824014e961722980757bb589009dc59b78d9a37`
- Scanner source SHA-256: `22bdb90c1a5dc23ddf6ec19c5b87adc98accd7abd5e5bd28cff16f9913b6d8dd`
- Harness SHA-256: `725c4ec8af374f7d9be08c19a171a8157630ba3f1f9e168e25c202a9a3e54db0`
- Manifest SHA-256: `f69d043cab43e5785e7c8a9dae430bcf146c105a0d23d1d77bc4089637377682`
- Native budget packet SHA-256: `ae891383d9f89dc9a470bae8adb2c7a61fdafff839b81f0f23cb84f8d9d5298b`
- Preparation measurement SHA-256: `e96f356080384d83e0fe41b0d38b4e839296caae6321cacbacef3c10290a796d`
- Original capture ledger SHA-256: `7b8a54a3faf7dbec11fbfb2d818ca2c7854545f548b5ba7581cea63d402cc13e`
- Proposal SHA-256: `6fd57c4e7b1d3072ad40888fb9d75d95dc76aa566e882520c907af9ecd128135`

[The proposal JSON](checkpoint2-proposal.json) names every selected request and all 17 reused capture identities. Its empty `user_decision` deliberately prevents capture. [Verification](preparation-verification.json) records the exact request comparison and all incomplete deterministic outcomes; [accepted-capture validation](accepted-capture-check.json) records native offline response revalidation.

## Exact remaining requests

| Inputs | Fingerprint | Input token bound | Output cap | Reservation USD |
| --- | --- | ---: | ---: | ---: |
| excel-boundary-fixed-mutation | `7cf99e2bdd9215fa1cf8274fc5a75b256e70aae05a2a03ecfd14fa0a232cee58` | 12153 | 2048 | 0.101725 |
| mobile-output-fixed-mutation | `873b397b5c50ff64954b1e88f967dbd60f0019ed29667e75d049c905ff0d5b91` | 12668 | 2048 | 0.104300 |
| excel-boundary-vulnerable-mutation | `8c0b2b3a36e28c222b855271c17086262d843f2d889e4ae1f9e30253c5e8fe5f` | 12945 | 2048 | 0.105685 |
| excel-boundary-fixed, excel-child-path-safe | `97e1ecbf8b85af54d290d08a9437fe5f1b84f59b66ba973622d93105e4a807f7` | 12463 | 2048 | 0.103275 |
| mobile-output-vulnerable | `9e3be7e69204b1742e6fd1d6674f610bc63a8841b713b8ba10a2de05ae0c107a` | 12668 | 2048 | 0.104300 |
| mobile-output-fixed, mobile-locale-safe | `a55be8f1e2e787507ff2b969496c6a821a628ebe99cfd1e9085104a6c4ada28c` | 12668 | 2048 | 0.104300 |
| excel-boundary-vulnerable | `a8791af49d12489e3da9de30e63335c958c27cc02672ce47ed323756794633cb` | 11825 | 2048 | 0.100085 |
| excel-boundary-fixed, excel-child-path-safe | `b639cf34f5eb480147f38c4410613a609d90b75272a6fcb65e727823bc7ec644` | 12351 | 2048 | 0.102715 |
| excel-boundary-fixed-mutation | `b86fbe47a75d2e6deb90b187cdc3843fc12de5e5a368be6fe34c4e291f8736ac` | 11996 | 2048 | 0.100940 |
| excel-boundary-vulnerable-mutation | `c44f927855b8c22c68ce714d8a58103fd0399d871bece97ebf6d015d37a65ad9` | 12021 | 2048 | 0.101065 |
| excel-boundary-vulnerable-mutation | `c9bcbb5699ec3b892e0b04bfba2c70eb9ca59761aca1ba3bd69f65fb78885a70` | 11869 | 2048 | 0.100305 |
| excel-boundary-vulnerable | `dda323baceec10d48eecf72b2b51d6e0b7e3dd1ac5d9e8b1aa795d1706559881` | 11977 | 2048 | 0.100845 |
| excel-boundary-fixed-mutation | `de43f1fb82efea789e4d6a1f64b9b39539e27015237091040c0a3cc63dc7a297` | 12305 | 2048 | 0.102485 |
| mobile-output-vulnerable, mobile-output-vulnerable-mutation, mobile-output-fixed, mobile-output-fixed-mutation, mobile-locale-safe | `e1f9c84a5da20d15bf31a2588a06a4876deb31ff20eb45f14aed936dcdf296e0` | 14067 | 3072 | 0.131775 |
| excel-boundary-vulnerable | `e602ec1fee33bfb2a65c422224b186c033512a83677f4dcb67c55c92338798ac` | 13991 | 2048 | 0.110915 |
| excel-boundary-vulnerable | `e95dfe4a9a48a78abeb6f2212fc15211ffa971bca39fdaaba0954adf8d2edd5b` | 12901 | 2048 | 0.105465 |
| excel-boundary-vulnerable | `f6fe67dab1db6d62424bff69b2c907697835ea6d5e2c470510fcaac373c61fbb` | 12179 | 2048 | 0.101855 |
| excel-boundary-fixed, excel-child-path-safe | `f715d0fc37500735cf0e3e1c43f337df7dbd19b8e59fea1cdd50dace1350b30c` | 13185 | 2048 | 0.106885 |

## Measurement limits and reproduction

All 45 inputs retain an outcome. Deterministic execution completes 32 and leaves 13 incomplete: four Atlassian timeouts and nine Helm template YAML failures. Stable findings and coverage in all 32 native reports match the original baseline. Request preparation is an offline planning operation, not completed GPT review. It establishes no new detection result. No detector, prompt, probe, target source, or approved runtime configuration was changed in this preparation.

The original baseline remains under `artifacts/phase20`; these versioned files are supplementary. This work used an isolated detached checkout at the scanner revision above, with the locked development environment and `PYTHONPATH` set to that checkout's `src`. Existing `rules`, `replay`, `prepare-live`, `dynamic`, and `runtime-replay` directories were preserved under `artifacts/phase20/pre-correction` in that checkout before these commands:

```sh
python -m scripts.run_phase20_benchmark validate
python -m scripts.run_phase20_benchmark rules
python -m scripts.run_phase20_benchmark prepare-live
```

Keep the original freeze, accepted captures, and ledger in their canonical paths. After an explicit decision, create a separate approval binding the exact packet hash, selected fingerprints, cumulative ceilings, and actual user response. Run `capture-live --stage static --approval <approved-file>` from the same checkout, then `replay`. Verify copied artifact hashes before use; do not replace the original baseline or relabel old capture provenance.

Eligible Docker measurements follow completed static replay. The historical Git SDK mismatch remains a runtime prerequisite limitation; no dependency override is approved by this packet. Any new runtime review requests require Checkpoint 3 approval. Final scoring/reporting, evidence review, and explicit phase acceptance still follow; merge and public deployment are not authorized here.

## Hosted checks

All 28 [CI jobs](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34064487770) passed for the scanner revision in this packet. The [documentation workflow](https://github.com/BashaarJavaid/MCP-Sentinel/actions/runs/34064487766) also passed; PR deployment was skipped. Retained results are in [source CI evidence](hosted-source-ci.json) and [documentation CI evidence](hosted-docs-ci.json). No new push was made for this preparation.
