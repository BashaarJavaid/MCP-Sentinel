# Git benchmark environment v1 — approval packet

Status: proposed; not adopted for Phase 22 measurements.

The candidate SDK pin is `mcp==1.29.0`. It restores the low-level API used by the
unmodified upstream Git snapshots. The [SDK release documentation](https://pypi.org/project/mcp/1.29.0/)
identifies v1 as the maintenance line and recommends an upper bound for existing
v1 deployments. The compatibility conclusion here comes from actual Docker tests.

All 13 eligible inputs initialized and discovered 12 tools each. Each test used
`DockerSandbox.probe_session`: no network, read-only target/root, bounded CPU,
memory/PIDs, no-new-privileges, and ephemeral scratch directories. All 13
containers were removed. `pip check` passed in every container. These are startup
and discovery results, not probe defenses or exploitation evidence. No model calls
or attacks were run.

The tested image ID is `sha256:420b998fc52bd814a2e937e780f9ddc0ede656f19e46ca0df02cf76242c1469a`.
The exact installed dependency set is retained in `requirements.txt`; each input's
original constraints plus SDK pin, configuration, image/container inspection,
tool schemas, process state, logs, dependency check and time are in `packet.json`.
Rebuilding from the lock must be checked against this dependency set; the immutable
image ID identifies the actual tested environment. No upstream source or Phase 20
configuration/evidence was changed. The initial host sandbox denial is separately
retained in `../git-environment-v1/packet.json` and is not a compatibility result.

Approval requested: adopt this separately versioned SDK/dependency environment
for Phase 22's 13 Git inputs. Phase 20 retains its original MCP 2.1.1 environment.
This approval would not authorize paid evaluation, merging, or publication.

Packet SHA-256: `a3481db5cfc181de2c0c1a51beca88a332570de00443655016945060394491d7`.
Requirements SHA-256: `efe9dd2ac850374f3c3fa57ef8b349e4bef6bbfaa278cec5e745c5424b916e71`.
