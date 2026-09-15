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

// Define the input schema for the git_push tool using Zod
export const GitPushInputSchema = z.object({
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
      "The remote repository to push to (e.g., 'origin'). Defaults to the tracked upstream or 'origin'.",
    ),
  branch: z
    .string()
    .optional()
    .describe(
      "The local branch to push (e.g., 'main', 'feat/new-login'). Defaults to the current branch.",
    ),
  remoteBranch: z
    .string()
    .optional()
    .describe(
      "The remote branch to push to (e.g., 'main', 'develop'). Defaults to the same name as the local branch.",
    ),
  force: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Force the push (use with caution: `--force-with-lease` is generally safer).",
    ),
  forceWithLease: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Force the push only if the remote ref is the expected value (`--force-with-lease`). Safer than --force.",
    ),
  setUpstream: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Set the upstream tracking configuration (`-u` or `--set-upstream`).",
    ),
  tags: z
    .boolean()
    .optional()
    .default(false)
    .describe("Push all tags (`--tags`)."),
  delete: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Delete the remote branch (`--delete`). Requires `branch` to be specified. Use with caution, as deleting remote branches can affect collaborators.",
    ),
  // Add other relevant git push options as needed (e.g., --prune, --all)
});

// Infer the TypeScript type from the Zod schema
export type GitPushInput = z.infer<typeof GitPushInputSchema>;

// Define the structure for the JSON output
export interface GitPushResult {
  success: boolean;
  message: string; // General status message (e.g., "Everything up-to-date", "Branch pushed", "Push rejected")
  summary?: string; // More detailed summary if available (e.g., commit range, objects pushed)
  rejected?: boolean; // Flag if the push was rejected (e.g., non-fast-forward, hooks)
  deleted?: boolean; // Flag if a remote branch was deleted
}

/**
 * Executes the 'git push' command and returns structured JSON output.
 *
 * @param {GitPushInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitPushResult>} A promise that resolves with the structured push result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function pushGitChanges(
  input: GitPushInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitPushResult> {
  const operation = "pushGitChanges";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    if (input.path && input.path !== ".") {
      targetPath = input.path;
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
    }
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

  // Validate specific input combinations
  if (input.delete && !input.branch) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      "Cannot use --delete without specifying a branch to delete.",
      { context, operation },
    );
  }
  if (input.force && input.forceWithLease) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      "Cannot use --force and --force-with-lease together.",
      { context, operation },
    );
  }
  if (
    input.delete &&
    (input.force || input.forceWithLease || input.setUpstream || input.tags)
  ) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      "Cannot combine --delete with --force, --force-with-lease, --set-upstream, or --tags.",
      { context, operation },
    );
  }

  try {
    // Construct the git push command
    const args = ["-C", targetPath, "push"];

    if (input.force) {
      args.push("--force");
    } else if (input.forceWithLease) {
      args.push("--force-with-lease");
    }

    if (input.setUpstream) {
      args.push("--set-upstream");
    }
    if (input.tags) {
      args.push("--tags");
    }
    if (input.delete) {
      args.push("--delete");
    }

    // Add remote and branch specification
    const remote = input.remote || "origin"; // Default to origin
    args.push(remote);

    if (input.branch) {
      if (input.remoteBranch && !input.delete) {
        args.push(`${input.branch}:${input.remoteBranch}`);
      } else {
        args.push(input.branch);
      }
    } else if (!input.tags && !input.delete) {
      // If no branch, tags, or delete specified, push the current branch by default
      logger.debug(
        "No specific branch, tags, or delete specified. Relying on default git push behavior for current branch.",
        { ...context, operation },
      );
    }

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    // Execute command. Note: Git push often uses stderr for progress and success messages.
    const { stdout, stderr } = await execFileAsync("git", args);

    logger.debug(`Git push stdout: ${stdout}`, { ...context, operation });
    if (stderr) {
      logger.debug(`Git push stderr: ${stderr}`, { ...context, operation });
    }

    // Analyze stderr primarily, fallback to stdout
    const message = stderr.trim() || stdout.trim() || "Push command executed.";
    const summary = message;
    const rejected = message.includes("[rejected]");
    const deleted = message.includes("[deleted]");

    logger.info("git push executed successfully", {
      ...context,
      operation,
      path: targetPath,
      summary,
      rejected,
      deleted,
    });
    return { success: true, message, summary, rejected, deleted };
  } catch (error: any) {
    logger.error(`Failed to execute git push command`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    const errorMessage = error.stderr || error.stdout || error.message || "";

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
      errorMessage.includes("Could not read from remote repository") ||
      errorMessage.includes("Connection timed out")
    ) {
      throw new McpError(
        BaseErrorCode.SERVICE_UNAVAILABLE,
        `Failed to connect to remote repository. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("rejected") ||
      errorMessage.includes("failed to push some refs")
    ) {
      // This might be caught here if execAsync throws due to non-zero exit code on rejection
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Push rejected: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("Authentication failed") ||
      errorMessage.includes("Permission denied")
    ) {
      throw new McpError(
        BaseErrorCode.UNAUTHORIZED,
        `Authentication failed for remote repository. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("src refspec") &&
      errorMessage.includes("does not match any")
    ) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Push failed: Source branch/refspec does not exist locally. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to push changes for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
