// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function gitInitLogic(input: { initialBranch?: string }) {
  const targetPath = "/tmp/phase23-git-init";
  let command = `git init`;
  const branchNameToUse = input.initialBranch || "main";
  command += ` -b "${branchNameToUse.replace(/"/g, '\\"')}"`;
  command += ` "${targetPath}"`;
  const { stdout, stderr } = await execAsync("git init -b main /tmp/phase23-git-init");
  return { stdout, stderr };
}
