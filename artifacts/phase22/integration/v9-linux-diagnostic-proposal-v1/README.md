# Unapproved Linux diagnostic option

This proposal follows failed final run 34435283462. It does not retry the full
benchmark or waive its gate. Scanner7555a9d remains frozen.

The existing optional CI job would run two exposed Meta inputs twice natively
and once with worker profiling: six input runs, each retaining120-second native
and end-to-end bounds, with a30-minute job ceiling. It retains worker CPU,
profiles, full reports, environment and every failure. No paid call, target
execution, source tuning or fresh evaluation is included. All29 normal CI jobs
are structurally unchanged in `ci.yml.proposed`; the real workflow is unchanged.

Review `packet.json`, `runner.py`, `worker-profile.py` and `ci.patch`. An explicit
user decision bound to the packet hash is required before installation and one
dispatch. Stop after these measurements and report actual Linux bottlenecks;
any implementation change or new full sequence needs its own concrete scope.
