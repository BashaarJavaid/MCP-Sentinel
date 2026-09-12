# Local duplicate-merge experiment: reverted

The count profile found repeated immutable Value identities in about 87% of shared merges with more than two operands. A three-line canonicalization preserved all four complete ordered after reports against the original baseline, excluding only recorded volatile fields. The owning 115-test state-flow module passed before restoration.

| Exposed input | Before wall seconds | After wall seconds | Before child CPU seconds | After child CPU seconds |
| --- | --- | --- | --- | --- |
| meta-image-ssrf-vulnerable | 66.447/78.551 | 64.681/76.991 | 166.663/196.476 | 161.072/193.252 |
| meta-operator-fallback-fixed-mutation | 68.217/80.719 | 70.096/76.104 | 172.388/199.703 | 176.536/190.344 |

The median wall changes are 2.29% and1.84%; median CPU changes are 2.43% and1.40%. The first operator observation regresses in both measures. Those small mixed changes and large repeat variability do not establish a repeatable gain across both inputs. No statistical significance or Linux improvement is claimed.

The optimization was reverted exactly to scanner 7555a9d. The useful branch-guard invariant remains in `tests/test_python_state_flow.py`; it preserves distinct guarded/unguarded values sharing a symbolic key, locations, nullable/missing values, credential state and clearing of source-free safety flags. Every experimental patch, test execution, report, profile and resource observation is retained.

The finite plan ended after 8 native observations and 1 counter profile, all with 120-second deadlines. No second optimization, full benchmark retry, fresh-source scan, model call or target execution occurred. See `v10-local-performance-assessment.json`, `v10-local-performance-disposition.json` and the unapproved `v10-next-performance-proposal.json`.
