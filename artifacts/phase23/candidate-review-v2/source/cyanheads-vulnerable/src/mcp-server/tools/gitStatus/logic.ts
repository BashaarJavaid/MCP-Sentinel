import { exec } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { logger, RequestContext, sanitization } from "../../../utils/index.js"; // logger (./utils/internal/logger.js), RequestContext (./utils/internal/requestContext.js), sanitization (./utils/security/sanitization.js)

const execAsync = promisify(exec);

// Define the input schema for the git_status tool using Zod
export const GitStatusInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
});

// Infer the TypeScript type from the Zod schema
export type GitStatusInput = z.infer<typeof GitStatusInputSchema>;

// Define the structure for the JSON output (New Structure)
export interface GitStatusResult {
  current_branch: string | null;
  staged_changes: {
    Added?: string[];
    Modified?: string[];
    Deleted?: string[];
    Renamed?: string[];
    Copied?: string[];
    TypeChanged?: string[];
  };
  unstaged_changes: {
    Modified?: string[];
    Deleted?: string[];
    TypeChanged?: string[];
  };
  untracked_files: string[];
  conflicted_files: string[];
  is_clean: boolean;
}

/**
 * Parses the output of 'git status --porcelain=v1 -b'.
 * See: https://git-scm.com/docs/git-status#_porcelain_format_version_1
 *
 * @param {string} porcelainOutput - The raw output from the git command.
 * @returns {GitStatusResult} - Structured status information.
 */
function parseGitStatusPorcelainV1(porcelainOutput: string): GitStatusResult {
  const lines = porcelainOutput.trim().split("\n");
  const result: GitStatusResult = {
    current_branch: null,
    staged_changes: {},
    unstaged_changes: {},
    untracked_files: [],
    conflicted_files: [],
    is_clean: true, // Assume clean initially
  };

  if (lines.length === 0 || (lines.length === 1 && lines[0] === "")) {
    return result;
  }

  if (lines[0].startsWith("## ")) {
    const branchLine = lines.shift()!;
    const standardBranchMatch = branchLine.match(
      /^## ([^ ]+?)(?:\.\.\.| \[.*\]|$)/,
    );
    const noCommitsMatch = branchLine.match(/^## No commits yet on (.+)/);
    const detachedMatch = branchLine.match(/^## HEAD \(no branch\)/);

    if (standardBranchMatch) {
      result.current_branch = standardBranchMatch[1];
    } else if (noCommitsMatch) {
      result.current_branch = `${noCommitsMatch[1]} (no commits yet)`;
    } else if (detachedMatch) {
      result.current_branch = "HEAD (detached)";
    } else {
      logger.warning("Could not parse branch information from line:", {
        branchLine,
      });
      result.current_branch = "(unknown)";
    }
  }

  for (const line of lines) {
    if (!line) continue;

    result.is_clean = false; // Any line indicates non-clean state

    const xy = line.substring(0, 2);
    const file = line.substring(3);

    const stagedStatusChar = xy[0];
    const unstagedStatusChar = xy[1];

    // Handle untracked files
    if (xy === "??") {
      result.untracked_files.push(file);
      continue;
    }

    // Handle conflicted files (unmerged paths)
    // DD = both deleted, AU = added by us, UD = deleted by them, UA = added by them, DU = deleted by us
    // AA = both added, UU = both modified
    if (
      stagedStatusChar === "U" ||
      unstagedStatusChar === "U" ||
      (stagedStatusChar === "D" && unstagedStatusChar === "D") ||
      (stagedStatusChar === "A" && unstagedStatusChar === "A")
    ) {
      result.conflicted_files.push(file);
      continue; // Conflicted files are handled separately and not in staged/unstaged
    }

    // Handle staged changes (index status)
    if (stagedStatusChar !== " " && stagedStatusChar !== "?") {
      let statusDesc: keyof GitStatusResult["staged_changes"] | undefined =
        undefined;
      switch (stagedStatusChar) {
        case "M":
          statusDesc = "Modified";
          break;
        case "A":
          statusDesc = "Added";
          break;
        case "D":
          statusDesc = "Deleted";
          break;
        case "R":
          statusDesc = "Renamed";
          break;
        case "C":
          statusDesc = "Copied";
          break;
        case "T":
          statusDesc = "TypeChanged";
          break;
      }
      if (statusDesc) {
        if (!result.staged_changes[statusDesc]) {
          result.staged_changes[statusDesc] = [];
        }
        result.staged_changes[statusDesc]!.push(file);
      }
    }

    // Handle unstaged changes (worktree status)
    if (unstagedStatusChar !== " " && unstagedStatusChar !== "?") {
      let statusDesc: keyof GitStatusResult["unstaged_changes"] | undefined =
        undefined;
      switch (unstagedStatusChar) {
        case "M":
          statusDesc = "Modified";
          break;
        case "D":
          statusDesc = "Deleted";
          break;
        case "T":
          statusDesc = "TypeChanged";
          break;
        // 'A' (Added but not committed) is handled by '??' (untracked)
        // 'R' and 'C' in worktree without being staged are complex, often appear as deleted + untracked
      }
      if (statusDesc) {
        if (!result.unstaged_changes[statusDesc]) {
          result.unstaged_changes[statusDesc] = [];
        }
        result.unstaged_changes[statusDesc]!.push(file);
      }
    }
  }

  result.is_clean =
    Object.keys(result.staged_changes).length === 0 &&
    Object.keys(result.unstaged_changes).length === 0 &&
    result.untracked_files.length === 0 &&
    result.conflicted_files.length === 0;
  return result;
}

/**
 * Executes the 'git status --porcelain=v1 -b' command and returns structured JSON output.
 *
 * @param {GitStatusInput} input - The validated input object containing the repository path.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitStatusResult>} A promise that resolves with the structured git status.
 * @throws {McpError} Throws an McpError if path resolution or validation fails, or if the git command fails.
 */
export async function getGitStatus(
  input: GitStatusInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  }, // Add getter to context
): Promise<GitStatusResult> {
  const operation = "getGitStatus";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve the target path
    if (input.path && input.path !== ".") {
      // Use the provided path directly
      targetPath = input.path;
      logger.debug(`Using provided path: ${targetPath}`, {
        ...context,
        operation,
      });
    } else {
      // Path is '.' or undefined, try to get the session's working directory
      const workingDir = context.getWorkingDirectory();
      if (!workingDir) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          "No path provided and no working directory set for the session.",
          { context, operation },
        );
      }
      targetPath = workingDir;
      logger.debug(`Using session working directory: ${targetPath}`, {
        ...context,
        operation,
        sessionId: context.sessionId,
      });
    }

    // Sanitize the resolved path
    const sanitizedPathInfo = sanitization.sanitizePath(targetPath, {
      allowAbsolute: true,
    });
    logger.debug("Sanitized path", {
      ...context,
      operation,
      sanitizedPathInfo,
    });
    targetPath = sanitizedPathInfo.sanitizedPath; // Use the sanitized path going forward
  } catch (error) {
    logger.error("Path resolution or sanitization failed", {
      ...context,
      operation,
      error,
    });
    if (error instanceof McpError) {
      throw error;
    }
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid path: ${error instanceof Error ? error.message : String(error)}`,
      { context, operation, originalError: error },
    );
  }

  try {
    // Using --porcelain=v1 for stable, scriptable output and -b for branch info
    // Ensure the path passed to -C is correctly quoted for the shell
    const command = `git -C "${targetPath}" status --porcelain=v1 -b`;
    logger.debug(`Executing command: ${command}`, { ...context, operation });

    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      // Log stderr as warning but proceed to parse stdout
      logger.warning(
        `Git status command produced stderr (may be informational)`,
        { ...context, operation, stderr },
      );
    }

    logger.debug(`${operation} command executed, parsing output...`, {
      ...context,
      operation,
      path: targetPath,
    });

    // Parse the porcelain output
    const structuredResult = parseGitStatusPorcelainV1(stdout);

    // If parsing resulted in clean state but no branch, re-check branch explicitly
    // This handles the case of an empty repo after init but before first commit
    if (structuredResult.is_clean && !structuredResult.current_branch) {
      try {
        const branchCommand = `git -C "${targetPath}" rev-parse --abbrev-ref HEAD`;
        const { stdout: branchStdout } = await execAsync(branchCommand);
        const currentBranchName = branchStdout.trim(); // Renamed variable for clarity
        if (currentBranchName && currentBranchName !== "HEAD") {
          structuredResult.current_branch = currentBranchName;
        } else if (
          currentBranchName === "HEAD" &&
          !structuredResult.current_branch
        ) {
          // If rev-parse returns HEAD and we still don't have a branch (e.g. detached from no-commits branch)
          structuredResult.current_branch = "HEAD (detached)";
        }
      } catch (branchError) {
        // Ignore error if rev-parse fails (e.g., still no commits)
        logger.debug(
          "Could not determine branch via rev-parse, likely no commits yet.",
          { ...context, operation, branchError },
        );
      }
    }

    logger.info("git status parsed successfully", {
      ...context,
      operation,
      path: targetPath,
      isClean: structuredResult.is_clean,
      currentBranch: structuredResult.current_branch,
    });
    return structuredResult; // Return the structured JSON object
  } catch (error: any) {
    logger.error(`Failed to execute or parse git status command`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      stderr: error.stderr,
    });

    const errorMessage = error.stderr || error.message || "";
    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }

    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to get git status for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
