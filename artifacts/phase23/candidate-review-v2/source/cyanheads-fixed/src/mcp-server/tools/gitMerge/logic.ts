import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (RequestContext from ../utils/internal/requestContext.js)
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Keep direct import for types-global
import { RequestContext } from "../../../utils/index.js";
// Import utils from barrel (sanitization from ../utils/security/sanitization.js)
import path from "path"; // Import path module
import { sanitization } from "../../../utils/index.js";

const execFileAsync = promisify(execFile);

// Define the input schema for the git_merge tool
export const GitMergeInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  branch: z
    .string()
    .min(1)
    .describe("The name of the branch to merge into the current branch."),
  commitMessage: z
    .string()
    .optional()
    .describe(
      "Commit message to use for the merge commit (if required, e.g., not fast-forward).",
    ),
  noFf: z
    .boolean()
    .default(false)
    .describe(
      "Create a merge commit even when the merge resolves as a fast-forward (`--no-ff`).",
    ),
  squash: z
    .boolean()
    .default(false)
    .describe(
      "Combine merged changes into a single commit (`--squash`). Requires manual commit afterwards.",
    ),
  abort: z
    .boolean()
    .default(false)
    .describe("Abort the current merge process (resolves conflicts)."),
  // 'continue' might be too complex for initial implementation due to requiring index manipulation
});

// Infer the TypeScript type from the Zod schema
export type GitMergeInput = z.infer<typeof GitMergeInputSchema>;

// Define the structure for the JSON output
export interface GitMergeResult {
  success: boolean;
  message: string;
  conflict?: boolean; // True if the merge resulted in conflicts
  fastForward?: boolean; // True if the merge was a fast-forward
  mergedCommitHash?: string; // Hash of the merge commit (if created and successful)
  aborted?: boolean; // True if the merge was aborted
  needsManualCommit?: boolean; // True if --squash was used and merge was successful
}

/**
 * Executes the 'git merge' command.
 *
 * @param {GitMergeInput} input - The validated input object.
 * @param {RequestContext} context - The request context.
 * @returns {Promise<GitMergeResult>} A promise that resolves with the structured merge result.
 * @throws {McpError} Throws an McpError for path issues, command failures, or unexpected errors.
 */
export async function gitMergeLogic(
  input: GitMergeInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitMergeResult> {
  const operation = "gitMergeLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve the target path
    let resolvedPath: string;
    if (input.path && input.path !== ".") {
      // If a specific path is given, resolve it absolutely first
      // Assuming input.path could be relative *to the server's CWD* if no session WD is set,
      // but it's safer to require absolute paths or rely on session WD.
      // For simplicity, let's assume input.path is intended relative to session WD if set, or absolute otherwise.
      const workingDir = context.getWorkingDirectory();
      if (workingDir) {
        resolvedPath = path.resolve(workingDir, input.path); // Resolve relative to session WD
      } else if (path.isAbsolute(input.path)) {
        resolvedPath = input.path; // Use absolute path directly
      } else {
        // If relative path given without session WD, it's ambiguous. Error out.
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          "Relative path provided but no working directory set for the session.",
          { context, operation },
        );
      }
      logger.debug(`Resolved provided path: ${resolvedPath}`, {
        ...context,
        operation,
      });
    } else {
      const workingDir = context.getWorkingDirectory();
      if (!workingDir) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          "No path provided and no working directory set for the session.",
          { context, operation },
        );
      }
      resolvedPath = workingDir; // Use session working directory
      logger.debug(`Using session working directory: ${resolvedPath}`, {
        ...context,
        operation,
        sessionId: context.sessionId,
      });
    }

    // Sanitize the resolved path
    // We assume the resolved path should be absolute for git commands.
    // sanitizePath checks for traversal and normalizes.
    targetPath = sanitization.sanitizePath(resolvedPath, {
      allowAbsolute: true,
    }).sanitizedPath;
    logger.debug(`Sanitized path: ${targetPath}`, { ...context, operation });
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

  // --- Construct the git merge command ---
  const args = ["-C", targetPath, "merge"];

  if (input.abort) {
    args.push("--abort");
  } else {
    // Standard merge options
    if (input.noFf) {
      args.push("--no-ff");
    }
    if (input.squash) {
      args.push("--squash");
    }
    if (input.commitMessage && !input.squash) {
      // Commit message only relevant if not squashing (squash requires separate commit)
      args.push("-m", input.commitMessage);
    } else if (input.squash && input.commitMessage) {
      logger.warning(
        "Commit message provided with --squash, but it will be ignored. Squash requires a separate commit.",
        { ...context, operation },
      );
    }
    args.push(input.branch); // Add branch to merge
  }

  logger.debug(`Executing command: git ${args.join(" ")}`, {
    ...context,
    operation,
  });

  // --- Execute and Parse ---
  try {
    const { stdout, stderr } = await execFileAsync("git", args);
    logger.debug(`Command stdout: ${stdout}`, { ...context, operation });
    if (stderr)
      logger.debug(`Command stderr: ${stderr}`, { ...context, operation }); // Log stderr even on success

    const result: GitMergeResult = {
      success: true,
      message: stdout.trim() || stderr.trim() || "Merge command executed.",
    };

    if (input.abort) {
      result.aborted = true;
      result.message = "Merge aborted successfully.";
    } else if (stdout.includes("Fast-forward")) {
      result.fastForward = true;
    } else if (stdout.includes("Merge made by") || stdout.includes("merging")) {
      const match = stdout.match(/Merge commit '([a-f0-9]+)'/);
      result.mergedCommitHash = match ? match[1] : undefined;
      result.fastForward = false;
    } else if (stdout.includes("Squash commit -- not updating HEAD")) {
      result.needsManualCommit = true;
    } else if (stdout.includes("Already up to date")) {
      result.fastForward = true;
    }

    logger.info("git merge executed successfully", {
      ...context,
      operation,
      path: targetPath,
      result,
    });

    return result;
  } catch (error: any) {
    const errorMessage = error.stderr || error.stdout || error.message || ""; // Git often puts errors in stdout/stderr
    logger.error(`Git merge command failed`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      output: errorMessage,
    });

    if (input.abort) {
      // If abort failed, it's likely there was no merge in progress
      if (errorMessage.includes("fatal: There is no merge to abort")) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `No merge in progress to abort.`,
          { context, operation, originalError: error },
        );
      }
      throw new McpError(
        BaseErrorCode.INTERNAL_ERROR,
        `Failed to abort merge: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Check for specific failure scenarios
    if (errorMessage.includes("CONFLICT")) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Merge failed due to conflicts. Please resolve conflicts and commit. Output: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("refusing to merge unrelated histories")) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Merge failed: Refusing to merge unrelated histories. Consider using '--allow-unrelated-histories'.`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("fatal: Not possible to fast-forward, aborting.")
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Merge failed: Not possible to fast-forward. Merge required.`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.match(/fatal: '.*?' does not point to a commit/)) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Merge failed: Branch '${input.branch}' not found or does not point to a commit.`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("fatal: You have not concluded your merge")) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Merge failed: Conflicts still exist from a previous merge. Resolve conflicts or abort. Output: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes(
        "error: Your local changes to the following files would be overwritten by merge",
      )
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Merge failed: Local changes would be overwritten. Please commit or stash them.`,
        { context, operation, originalError: error },
      );
    }

    // Generic error
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git merge command failed for path ${targetPath}: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
