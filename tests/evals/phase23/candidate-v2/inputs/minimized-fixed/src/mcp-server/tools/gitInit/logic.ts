// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

export async function gitInitLogic(input: { initialBranch?: string }) {
  const targetPath = "/tmp/phase23-git-init";
  const args: string[] = ["init"];
  const branchNameToUse = input.initialBranch || "main";
  args.push("-b", branchNameToUse);
  args.push(targetPath);
  const { stdout, stderr } = await execFileAsync("git", args);
  return { stdout, stderr };
}
