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

// Define the input schema for the git_checkout tool using Zod
export const GitCheckoutInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  branchOrPath: z
    .string()
    .min(1)
    .describe(
      "The branch name (e.g., 'main'), commit hash, tag, or file path(s) (e.g., './src/file.ts') to checkout.",
    ),
  newBranch: z
    .string()
    .optional()
    .describe(
      "Create a new branch named <new_branch> (e.g., 'feat/new-feature') and start it at <branchOrPath>.",
    ),
  force: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Force checkout even if there are uncommitted changes (use with caution, discards local changes).",
    ),
  // Add other relevant git checkout options as needed (e.g., --track, -b for new branch shorthand)
});

// Infer the TypeScript type from the Zod schema
export type GitCheckoutInput = z.infer<typeof GitCheckoutInputSchema>;

// Define the structure for the JSON output
export interface GitCheckoutResult {
  success: boolean;
  message: string; // General status message (e.g., "Switched to branch 'main'", "Updated 1 path from...")
  previousBranch?: string; // Previous branch name if switched
  currentBranch?: string; // Current branch name after checkout
  newBranchCreated?: boolean; // Flag if a new branch was created
  filesRestored?: string[]; // List of files restored if checking out paths
}

/**
 * Executes the 'git checkout' command and returns structured JSON output.
 * Handles switching branches, creating new branches, and restoring files.
 *
 * @param {GitCheckoutInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitCheckoutResult>} A promise that resolves with the structured checkout result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function checkoutGit(
  input: GitCheckoutInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitCheckoutResult> {
  const operation = "checkoutGit";
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

  try {
    // Construct the git checkout command
    const args = ["-C", targetPath, "checkout"];

    if (input.force) {
      args.push("--force");
    }
    if (input.newBranch) {
      args.push("-b", input.newBranch);
    }

    args.push(input.branchOrPath); // Add the target branch/path

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    // Execute command. Checkout often uses stderr for status messages.
    const { stdout, stderr } = await execFileAsync("git", args);

    const message = stderr.trim() || stdout.trim();
    logger.debug(`Git checkout stdout: ${stdout}`, { ...context, operation });
    if (stderr) {
      logger.debug(`Git checkout stderr: ${stderr}`, { ...context, operation });
    }

    // Get the current branch name after the checkout operation
    let currentBranch: string | undefined;
    try {
      const { stdout: branchStdout } = await execFileAsync("git", [
        "-C",
        targetPath,
        "branch",
        "--show-current",
      ]);
      currentBranch = branchStdout.trim();
    } catch (e) {
      // This can fail in detached HEAD state, which is not an error for checkout
      currentBranch = "Detached HEAD";
    }

    const result: GitCheckoutResult = {
      success: true,
      message,
      currentBranch,
      newBranchCreated: !!input.newBranch,
    };

    logger.info("git checkout executed successfully", {
      ...context,
      operation,
      path: targetPath,
      result,
    });

    return result;
  } catch (error: any) {
    logger.error(`Failed to execute git checkout command`, {
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
      errorMessage.match(
        /pathspec '.*?' did not match any file\(s\) known to git/,
      )
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Branch or pathspec not found: ${input.branchOrPath}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("already exists")) {
      // e.g., trying -b with existing branch name
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Cannot create new branch '${input.newBranch}': it already exists. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes(
        "Your local changes to the following files would be overwritten by checkout",
      )
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Checkout failed due to uncommitted local changes that would be overwritten. Please commit or stash them first, or use --force. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("invalid reference")) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Invalid branch name or reference: ${input.branchOrPath}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to checkout for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
