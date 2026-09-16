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

// Define the input schema for the git_cherry-pick tool using Zod
export const GitCherryPickInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  commitRef: z
    .string()
    .min(1)
    .describe(
      "The commit reference(s) to cherry-pick (e.g., 'hash1', 'hash1..hash3', 'branchName~3..branchName').",
    ),
  mainline: z
    .number()
    .int()
    .min(1)
    .optional()
    .describe(
      "Specify the parent number (starting from 1) when cherry-picking a merge commit.",
    ),
  strategy: z
    .enum(["recursive", "resolve", "ours", "theirs", "octopus", "subtree"])
    .optional()
    .describe("Specifies a merge strategy *option* (passed via -X)."),
  noCommit: z
    .boolean()
    .default(false)
    .describe("Apply the changes but do not create a commit."),
  signoff: z
    .boolean()
    .default(false)
    .describe("Add a Signed-off-by line to the commit message."),
  // Add options for conflict handling? (e.g., --continue, --abort, --skip) - Maybe separate tool or mode?
});

// Infer the TypeScript type from the Zod schema
export type GitCherryPickInput = z.infer<typeof GitCherryPickInputSchema>;

// Define the structure for the result
interface GitCherryPickSuccessResult {
  success: true;
  message: string;
  commitCreated: boolean; // True if a commit was made (i.e., noCommit=false and no conflicts)
  conflicts?: boolean; // Indicates if conflicts occurred (requires manual resolution)
}

interface GitCherryPickFailureResult {
  success: false;
  message: string;
  error?: string; // Detailed error message
  conflicts?: boolean; // Specifically for failures due to conflicts
}

export type GitCherryPickResult =
  | GitCherryPickSuccessResult
  | GitCherryPickFailureResult;

/**
 * Executes the 'git cherry-pick' command.
 *
 * @param {GitCherryPickInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitCherryPickResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitCherryPickLogic(
  input: GitCherryPickInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitCherryPickResult> {
  const operation = "gitCherryPickLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git cherry-pick in server's CWD as no path provided and no session WD set.",
        { ...context, operation },
      );
      targetPath = process.cwd();
    } else if (targetPath === "." && workingDir) {
      targetPath = workingDir;
      logger.debug(`Using session working directory: ${targetPath}`, {
        ...context,
        operation,
        sessionId: context.sessionId,
      });
    } else {
      logger.debug(`Using provided path: ${targetPath}`, {
        ...context,
        operation,
      });
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
    const args = ["-C", targetPath, "cherry-pick"];

    if (input.mainline) {
      args.push("-m", String(input.mainline));
    }
    if (input.strategy) {
      args.push(`-X${input.strategy}`);
    } // Note: -X for strategy options
    if (input.noCommit) {
      args.push("--no-commit");
    }
    if (input.signoff) {
      args.push("--signoff");
    }

    // Add the commit reference(s)
    args.push(input.commitRef);

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    try {
      const { stdout, stderr } = await execFileAsync("git", args);
      // Check stdout/stderr for conflict messages, although exit code 0 usually means success
      const output = stdout + stderr;
      const conflicts = /conflict/i.test(output);
      const commitCreated = !input.noCommit && !conflicts;

      const message = conflicts
        ? `Cherry-pick resulted in conflicts for commit(s) '${input.commitRef}'. Manual resolution required.`
        : `Successfully cherry-picked commit(s) '${input.commitRef}'.` +
          (commitCreated
            ? " New commit created."
            : input.noCommit
              ? " Changes staged."
              : "");

      logger.info("git cherry-pick executed successfully", {
        ...context,
        operation,
        path: targetPath,
        result: { message, conflicts, commitCreated },
      });
      return { success: true, message, commitCreated, conflicts };
    } catch (cherryPickError: any) {
      const errorMessage =
        cherryPickError.stderr ||
        cherryPickError.stdout ||
        cherryPickError.message ||
        "";
      if (/conflict/i.test(errorMessage)) {
        logger.warning(
          `Cherry-pick failed due to conflicts for commit(s) '${input.commitRef}'.`,
          { ...context, operation, path: targetPath, error: errorMessage },
        );
        return {
          success: false,
          message: `Failed to cherry-pick commit(s) '${input.commitRef}' due to conflicts. Resolve conflicts manually and potentially use 'git cherry-pick --continue' or '--abort'.`,
          error: errorMessage,
          conflicts: true,
        };
      }
      // Rethrow other errors to be caught by the outer try-catch
      throw cherryPickError;
    }
  } catch (error: any) {
    const errorMessage = error.stderr || error.stdout || error.message || "";
    logger.error(`Failed to execute git cherry-pick command`, {
      ...context,
      operation,
      path: targetPath,
      error: errorMessage,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    // Specific error handling
    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }
    if (/bad revision/i.test(errorMessage)) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Failed to cherry-pick: Invalid commit reference '${input.commitRef}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (/after resolving the conflicts/i.test(errorMessage)) {
      // This might indicate a previous conflict state
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to cherry-pick: Unresolved conflicts from a previous operation exist. Resolve conflicts and use 'git cherry-pick --continue' or '--abort'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (/your local changes would be overwritten/i.test(errorMessage)) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to cherry-pick: Your local changes to tracked files would be overwritten. Please commit or stash them. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git cherry-pick failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
