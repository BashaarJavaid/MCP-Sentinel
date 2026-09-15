# Modified source reproduction

Derived from cyanheads/git-mcp-server 0dbd6995ccdf76ab770b58013034365b2d06c4d9
under Apache-2.0; original LICENSE and README retained.

Variant: renamed-fixed. Reconstructed registration and narrowed initialBranch-only
logic; fixed literal repository path, removed unrelated options, filesystem/session
gates, logging, error wrappers and other tools. This is not runtime-equivalent to
the upstream server. No target source was installed, imported or executed.

Identifier substitutions: {"args": "argv", "branchNameToUse": "branchName", "command": "shellCommand", "execAsync": "runShell", "execFileAsync": "runFile", "gitInitLogic": "initializeRepository", "initialBranch": "branchLabel", "input": "requestData", "server": "mcpServer", "targetPath": "repositoryPath"}
