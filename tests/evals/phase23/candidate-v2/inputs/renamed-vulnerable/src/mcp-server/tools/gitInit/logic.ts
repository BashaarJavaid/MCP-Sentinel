// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { exec } from "child_process";
import { promisify } from "util";

const runShell = promisify(exec);

export async function initializeRepository(requestData: { branchLabel?: string }) {
  const repositoryPath = "/tmp/phase23-git-init";
  let shellCommand = `git init`;
  const branchName = requestData.branchLabel || "main";
  shellCommand += ` -b "${branchName.replace(/"/g, '\\"')}"`;
  shellCommand += ` "${repositoryPath}"`;
  const { stdout, stderr } = await runShell(shellCommand);
  return { stdout, stderr };
}
