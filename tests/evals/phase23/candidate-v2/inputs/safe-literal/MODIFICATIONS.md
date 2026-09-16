# Modified source reproduction

Derived from cyanheads/git-mcp-server f30169ec3a2520990e5467c19ef42ea7d6d9270e
under Apache-2.0; original LICENSE and README retained.

Variant: safe-literal. Reconstructed registration and narrowed initialBranch-only
logic; fixed literal repository path, removed unrelated options, filesystem/session
gates, logging, error wrappers and other tools. This is not runtime-equivalent to
the upstream server. No target source was installed, imported or executed.

Only the execution argument is replaced with a literal command.
