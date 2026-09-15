// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { execFile } from "child_process";
import { promisify } from "util";

const runFile = promisify(execFile);

export async function initializeRepository(requestData: { branchLabel?: string }) {
  const repositoryPath = "/tmp/phase23-git-init";
  const argv: string[] = ["init"];
  const branchName = requestData.branchLabel || "main";
  argv.push("-b", branchName);
  argv.push(repositoryPath);
  const { stdout, stderr } = await runFile("git", argv);
  return { stdout, stderr };
}
