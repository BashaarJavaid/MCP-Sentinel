import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (RequestContext from ../utils/internal/requestContext.js)
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Keep direct import for types-global
import { RequestContext } from "../../../utils/index.js";
// Import utils from barrel (sanitization from ../utils/security/sanitization.js)
import { sanitization } from "../../../utils/index.js";

const execFileAsync = promisify(execFile);

// Define the input schema for the git_pull tool using Zod
export const GitPullInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  remote: z
    .string()
    .optional()
    .describe(
      "The remote repository to pull from (e.g., 'origin'). Defaults to the tracked upstream or 'origin'.",
    ),
  branch: z
    .string()
    .optional()
    .describe(
      "The remote branch to pull (e.g., 'main'). Defaults to the current branch's upstream.",
    ),
  rebase: z
    .boolean()
    .optional()
    .default(false)
    .describe("Use 'git pull --rebase' instead of merge."),
  ffOnly: z
    .boolean()
    .optional()
    .default(false)
    .describe("Use '--ff-only' to only allow fast-forward merges."),
  // Add other relevant git pull options as needed (e.g., --prune, --tags, --depth)
});

// Infer the TypeScript type from the Zod schema
export type GitPullInput = z.infer<typeof GitPullInputSchema>;

// Define the structure for the JSON output
export interface GitPullResult {
  success: boolean;
  message: string; // General status message (e.g., "Already up to date.", "Fast-forward", "Merge made by...")
  summary?: string; // More detailed summary if available (e.g., files changed, insertions/deletions)
  conflict?: boolean; // Flag if a merge conflict occurred
}

/**
 * Executes the 'git pull' command and returns structured JSON output.
 *
 * @param {GitPullInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling, including session info and working dir getter.
 * @returns {Promise<GitPullResult>} A promise that resolves with the structured pull result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function pullGitChanges(
  input: GitPullInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitPullResult> {
  const operation = "pullGitChanges";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve the target path
    if (input.path && input.path !== ".") {
      targetPath = input.path;
      logger.debug(`Using provided path: ${targetPath}`, {
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
      targetPath = workingDir;
      logger.debug(`Using session working directory: ${targetPath}`, {
        ...context,
        operation,
        sessionId: context.sessionId,
      });
    }
    // Sanitize the resolved path
    targetPath = sanitization.sanitizePath(targetPath, {
      allowAbsolute: true,
    }).sanitizedPath;
    logger.debug("Sanitized path", {
      ...context,
      operation,
      sanitizedPath: targetPath,
    });
  } catch (error) {
    logger.error("Path resolution or sanitization failed", {
      ...context,
      operation,
      error,
    });
    if (error instanceof McpError) throw error;
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid path: ${error instanceof Error ? error.message : String(error)}`,
      { context, operation, originalError: error },
    );
  }

  try {
    // Construct the git pull command
    const args = ["-C", targetPath, "pull"];

    if (input.rebase) {
      args.push("--rebase");
    }
    if (input.ffOnly) {
      args.push("--ff-only");
    }
    if (input.remote) {
      args.push(input.remote);
      if (input.branch) {
        args.push(input.branch);
      }
    } else if (input.branch) {
      // If only branch is specified, assume 'origin' or tracked remote
      args.push("origin", input.branch); // Defaulting to origin if remote not specified but branch is
      logger.warning(
        `Remote not specified, defaulting to 'origin' for branch pull`,
        { ...context, operation },
      );
    }

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    const { stdout, stderr } = await execFileAsync("git", args);

    logger.debug(`Git pull stdout: ${stdout}`, { ...context, operation });
    if (stderr) {
      logger.debug(`Git pull stderr: ${stderr}`, { ...context, operation });
    }

    // Analyze stdout/stderr to determine the outcome
    const message = stdout.trim() || stderr.trim() || "Pull command executed.";
    const summary = message;
    const conflict = message.includes("CONFLICT");

    logger.info("git pull executed successfully", {
      ...context,
      operation,
      path: targetPath,
      summary,
      conflict,
    });
    return { success: true, message, summary, conflict };
  } catch (error: any) {
    logger.error(`Failed to execute git pull command`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    const errorMessage = error.stderr || error.stdout || error.message || ""; // Check stdout too for errors

    // Handle specific error cases
    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("resolve host") ||
      errorMessage.includes("Could not read from remote repository")
    ) {
      throw new McpError(
        BaseErrorCode.SERVICE_UNAVAILABLE,
        `Failed to connect to remote repository. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("merge conflict") ||
      errorMessage.includes("fix conflicts")
    ) {
      // This might be caught here if execAsync throws due to non-zero exit code during conflict
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Pull resulted in merge conflicts. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("You have unstaged changes") ||
      errorMessage.includes(
        "Your local changes to the following files would be overwritten by merge",
      )
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Pull failed due to uncommitted local changes. Please commit or stash them first. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("refusing to merge unrelated histories")) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Pull failed: Refusing to merge unrelated histories. Use '--allow-unrelated-histories' if intended.`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to pull changes for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
