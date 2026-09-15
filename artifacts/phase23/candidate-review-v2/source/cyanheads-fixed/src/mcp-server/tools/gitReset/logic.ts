import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { logger, RequestContext, sanitization } from "../../../utils/index.js"; // logger (./utils/internal/logger.js), RequestContext (./utils/internal/requestContext.js), sanitization (./utils/security/sanitization.js)

const execFileAsync = promisify(execFile);

// Define the reset modes
const ResetModeEnum = z.enum(["soft", "mixed", "hard", "merge", "keep"]);
export type ResetMode = z.infer<typeof ResetModeEnum>;

// Define the input schema for the git_reset tool using Zod
export const GitResetInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: ResetModeEnum.optional()
    .default("mixed")
    .describe(
      "Reset mode: 'soft' (reset HEAD only), 'mixed' (reset HEAD and index, default), 'hard' (reset HEAD, index, and working tree - USE WITH CAUTION), 'merge', 'keep'.",
    ),
  commit: z
    .string()
    .optional()
    .describe(
      "Commit, branch, or ref to reset to. Defaults to HEAD (useful for unstaging with 'mixed' mode).",
    ),
  // file: z.string().optional().describe("If specified, reset only this file in the index (unstaging). Mode must be 'mixed' or omitted."), // Git reset [<mode>] [<tree-ish>] [--] <paths>… is complex, handle separately if needed
});
// Add refinement if needed, e.g., ensuring file is only used with mixed mode and no commit specified.

// Infer the TypeScript type from the Zod schema
export type GitResetInput = z.infer<typeof GitResetInputSchema>;

// Define the structure for the JSON output
export interface GitResetResult {
  success: boolean;
  message: string; // Status message (e.g., "HEAD is now at <hash>", "Unstaged changes after reset:")
  changesSummary?: string; // Summary of changes (e.g., list of unstaged files)
}

/**
 * Executes the 'git reset' command and returns structured JSON output.
 *
 * @param {GitResetInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitResetResult>} A promise that resolves with the structured reset result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function resetGitState(
  input: GitResetInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitResetResult> {
  const operation = "resetGitState";
  logger.debug(`Executing ${operation}`, { ...context, input });

  // Validate input combinations (e.g., file path usage) if refinement wasn't used
  // if (input.file && input.mode && input.mode !== 'mixed') {
  //   throw new McpError(BaseErrorCode.VALIDATION_ERROR, "Resetting specific files is only supported with 'mixed' mode (or default).", { context, operation });
  // }
  // if (input.file && input.commit) {
  //    throw new McpError(BaseErrorCode.VALIDATION_ERROR, "Cannot specify both a commit and file paths for reset.", { context, operation });
  // }

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
    // Construct the git reset command
    const args = ["-C", targetPath, "reset"];

    if (input.mode) {
      args.push(`--${input.mode}`);
    }

    if (input.commit) {
      args.push(input.commit);
    }
    // Handling file paths requires careful command construction, often without a commit ref.
    // Example: `git reset HEAD -- path/to/file` or `git reset -- path/to/file` (unstages)
    // For simplicity, this initial version focuses on resetting the whole HEAD/index/tree.
    // Add file path logic here if needed, adjusting command structure.

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    // Execute command. Reset output is often minimal on success, but stderr might indicate issues.
    const { stdout, stderr } = await execFileAsync("git", args);

    logger.debug(`Git reset stdout: ${stdout}`, { ...context, operation });
    if (stderr) {
      // Log stderr as info, as it often contains the primary status message
      logger.debug(`Git reset stderr: ${stderr}`, { ...context, operation });
    }

    // Analyze output (primarily stderr for reset)
    const message =
      stderr.trim() ||
      stdout.trim() ||
      `Reset successful (mode: ${input.mode || "mixed"}).`; // Default success message
    const changesSummary = stderr.includes("Unstaged changes after reset")
      ? stderr
      : undefined;

    logger.info("git reset executed successfully", {
      ...context,
      operation,
      path: targetPath,
      message,
      changesSummary,
    });
    return { success: true, message, changesSummary };
  } catch (error: any) {
    logger.error(`Failed to execute git reset command`, {
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
      errorMessage.includes("fatal: bad revision") ||
      errorMessage.includes("unknown revision")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Invalid commit reference specified: '${input.commit}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("Cannot reset paths") &&
      errorMessage.includes("mode")
    ) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Invalid mode ('${input.mode}') used with file paths. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("unmerged paths")) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Cannot reset due to unmerged files. Please resolve conflicts first. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to git reset for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
