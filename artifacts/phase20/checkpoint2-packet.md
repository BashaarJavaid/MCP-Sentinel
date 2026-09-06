# Checkpoint 2 — Static review budget decision

Packet SHA-256: `4a5c620836f9764729e8bb92f0ceed56228e2ea8b26998e6a4d51366b23530af`.

35 distinct production requests; aggregate conservative reservation **$3.720000**. No live calls have run. User approval is pending.

Requests cover the 70 deterministic candidates on 15 inputs. Exact repeated request fingerprints share one capture; the packet lists every participating input. Atlassian configuration failures produce no requests; zero-candidate stages produce no requests. No candidates were manufactured from labels.

Pricing verified 2026-09-06: $4 / million input tokens, $0.40 cached input, $20 output, and 1.25x cache writes. Long-context premiums apply above 272,000 input tokens. [Official model pricing](https://developers.openai.com/api/docs/models/gpt-5.6-sol). Reservations charge UTF-8 request bytes plus 4,096 framing tokens at the full cache-write rate and reserve the full output cap; no cache discount.

Production settings: `gpt-5.6-sol`, medium reasoning, public OpenAI Responses endpoint, service tier default, timeout 30 seconds, retries 0, concurrency 1, local cache disabled, maximum 500 selected findings per scan. All source, context, tools, instructions, and response schemas are retained in `prepare-live/results.json`.

The first failed or unaffordable request stops capture. Successful captures remain accepted; failed/interrupted reservations remain charged conservatively. Further attempts require a new decision. A stage ceiling is cumulative across its attempts and includes previous failures. Static and runtime stages have separate ceilings. The capture lock prevents concurrent spend.

Approval file shape (fill only after the user sets and approves the ceiling):

```json
{
  "checkpoint": 2,
  "stage": "static",
  "packet_sha256": "4a5c620836f9764729e8bb92f0ceed56228e2ea8b26998e6a4d51366b23530af",
  "max_micro_usd": null,
  "max_requests": null,
  "user_decision": null
}
```

After approval: `python -m scripts.run_phase20_benchmark capture-live --stage static --approval artifacts/phase20/checkpoint2-approval.json`. Replaying unchanged accepted captures does not require another paid request.

| Fingerprint | Inputs | Candidates | Reserved USD |
| --- | --- | ---: | ---: |
| `29d84d878a282f0fa07b3025b92c5274ee49c8ac0974fb6f1d5f835f2a0756b0` | mobile-output-vulnerable-mutation | 1 | 0.104300 |
| `2a2d4811dabc89625e73e273c62ac2884de7fb93241d6481e31a693c032df696` | excel-boundary-vulnerable-mutation | 1 | 0.101515 |
| `2d67e5a814a04908870794422ca7ca6a37137898c13aa059244264f9cf7946a4` | excel-boundary-vulnerable | 1 | 0.099300 |
| `33f324ff6fe85d3011f5cbbd007de8b7586c3706494100d3bb881047cdf57f56` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.102265 |
| `37b1ae375610074e3d86b82fa3482826ab6af63d3035b0839a1a1a2dd372c5d5` | excel-boundary-fixed-mutation | 1 | 0.112555 |
| `38216d4d980fc9c94938465cf53abb77e7eae56243c1b80a9fe4ed7045fa7306` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.101505 |
| `3afa37e322545ba0fe4e456f8f0c188e4e07e89d8d87a0fcfa80bd5e72e9acfd` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.112335 |
| `4f6e00f44383a3dcc480eb76697618ea591b60433f3df07cd31daae33b5fa794` | excel-boundary-vulnerable | 1 | 0.101295 |
| `52dd3ff2da57a769156f3eba93cbe614bad1c6194646d53206f789f3c1aee240` | kubernetes-shell-vulnerable, kubernetes-shell-vulnerable-mutation, kubernetes-shell-fixed, kubernetes-shell-fixed-mutation, kubernetes-formatting-safe | 2 | 0.139650 |
| `5e25ee1bb17cc77ffc2f5f444221886e157710fabe6ce8400329ace735b3c597` | excel-boundary-fixed-mutation | 1 | 0.102935 |
| `609a5b36bcc35a5ef8344da7b1fa50864c76c2387fcdf1a72c6a6f0503dbc8a1` | kubernetes-shell-vulnerable, kubernetes-shell-vulnerable-mutation, kubernetes-shell-fixed, kubernetes-shell-fixed-mutation, kubernetes-formatting-safe | 2 | 0.129375 |
| `622c20d808b3387aa2fc3b1edb49e17606374f661285ca5531e13acad43dbca3` | excel-boundary-fixed-mutation | 1 | 0.103495 |
| `6779744a70a5a2bc8a1ef3adeb7daad6b6d458ceec738a5e244268848dc4f473` | excel-boundary-fixed-mutation | 1 | 0.107105 |
| `67a984d5ebd158b989bec45ac86e418a0eb1981113702ace86ecddb20b993f93` | excel-boundary-vulnerable-mutation | 1 | 0.099520 |
| `67dc6cebac971c072e811855c9846c040fc7af8173314c2f507953fedef5514b` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.100720 |
| `6bd7c922feba0898645f3e449291222291bba78a69ce053ec435a4b799f858d2` | excel-boundary-vulnerable-mutation | 1 | 0.111135 |
| `783e0f47cc7fd6b6eedc1167cab00cdf989b28b4519b9deea15d6661e188b93d` | excel-boundary-vulnerable-mutation | 1 | 0.102075 |
| `7cf99e2bdd9215fa1cf8274fc5a75b256e70aae05a2a03ecfd14fa0a232cee58` | excel-boundary-fixed-mutation | 1 | 0.101725 |
| `873b397b5c50ff64954b1e88f967dbd60f0019ed29667e75d049c905ff0d5b91` | mobile-output-fixed-mutation | 1 | 0.104300 |
| `8c0b2b3a36e28c222b855271c17086262d843f2d889e4ae1f9e30253c5e8fe5f` | excel-boundary-vulnerable-mutation | 1 | 0.105685 |
| `97e1ecbf8b85af54d290d08a9437fe5f1b84f59b66ba973622d93105e4a807f7` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.103275 |
| `9e3be7e69204b1742e6fd1d6674f610bc63a8841b713b8ba10a2de05ae0c107a` | mobile-output-vulnerable | 1 | 0.104300 |
| `a55be8f1e2e787507ff2b969496c6a821a628ebe99cfd1e9085104a6c4ada28c` | mobile-output-fixed, mobile-locale-safe | 1 | 0.104300 |
| `a8791af49d12489e3da9de30e63335c958c27cc02672ce47ed323756794633cb` | excel-boundary-vulnerable | 1 | 0.100085 |
| `b639cf34f5eb480147f38c4410613a609d90b75272a6fcb65e727823bc7ec644` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.102715 |
| `b86fbe47a75d2e6deb90b187cdc3843fc12de5e5a368be6fe34c4e291f8736ac` | excel-boundary-fixed-mutation | 1 | 0.100940 |
| `c44f927855b8c22c68ce714d8a58103fd0399d871bece97ebf6d015d37a65ad9` | excel-boundary-vulnerable-mutation | 1 | 0.101065 |
| `c9bcbb5699ec3b892e0b04bfba2c70eb9ca59761aca1ba3bd69f65fb78885a70` | excel-boundary-vulnerable-mutation | 1 | 0.100305 |
| `dda323baceec10d48eecf72b2b51d6e0b7e3dd1ac5d9e8b1aa795d1706559881` | excel-boundary-vulnerable | 1 | 0.100845 |
| `de43f1fb82efea789e4d6a1f64b9b39539e27015237091040c0a3cc63dc7a297` | excel-boundary-fixed-mutation | 1 | 0.102485 |
| `e1f9c84a5da20d15bf31a2588a06a4876deb31ff20eb45f14aed936dcdf296e0` | mobile-output-vulnerable, mobile-output-vulnerable-mutation, mobile-output-fixed, mobile-output-fixed-mutation, mobile-locale-safe | 2 | 0.131775 |
| `e602ec1fee33bfb2a65c422224b186c033512a83677f4dcb67c55c92338798ac` | excel-boundary-vulnerable | 1 | 0.110915 |
| `e95dfe4a9a48a78abeb6f2212fc15211ffa971bca39fdaaba0954adf8d2edd5b` | excel-boundary-vulnerable | 1 | 0.105465 |
| `f6fe67dab1db6d62424bff69b2c907697835ea6d5e2c470510fcaac373c61fbb` | excel-boundary-vulnerable | 1 | 0.101855 |
| `f715d0fc37500735cf0e3e1c43f337df7dbd19b8e59fea1cdd50dace1350b30c` | excel-boundary-fixed, excel-child-path-safe | 1 | 0.106885 |
