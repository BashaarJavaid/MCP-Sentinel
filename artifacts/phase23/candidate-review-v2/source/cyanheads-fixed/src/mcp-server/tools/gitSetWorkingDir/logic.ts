import { execFile } from "child_process";
import fs from "fs/promises";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { RequestContext, logger, sanitization } from "../../../utils/index.js"; // RequestContext (./utils/internal/requestContext.js), logger (./utils/internal/logger.js), sanitization (./utils/security/sanitization.js)

const execFileAsync = promisify(execFile);

// Define the Zod schema for input validation
export const GitSetWorkingDirInputSchema = z.object({
  path: z
    .string()
    .min(1, "Path cannot be empty.")
    .describe(
      "The absolute path to set as the default working directory for the current session. Set this before using other git_* tools.",
    ),
  validateGitRepo: z
    .boolean()
    .default(true)
    .describe("Whether to validate that the path is a Git repository"),
  initializeIfNotPresent: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "If true and the directory is not a Git repository, attempt to initialize it with 'git init'.",
    ),
});

// Infer the TypeScript type from the Zod schema
export type GitSetWorkingDirInput = z.infer<typeof GitSetWorkingDirInputSchema>;

// Define the TypeScript interface for the result
export interface GitSetWorkingDirResult {
  success: boolean;
  message: string;
  path: string;
  initialized: boolean; // Added to indicate if repo was initialized
}

/**
 * Logic for the git_set_working_dir tool.
 * Sets a global working directory path for the current session.
 * Validates the path and optionally checks if it's a Git repository.
 *
 * @param {GitSetWorkingDirInput} input - The validated input arguments.
 * @param {RequestContext} context - The request context, potentially containing session ID.
 * @returns {Promise<GitSetWorkingDirResult>} The result of the operation.
 * @throws {McpError} Throws McpError for validation failures or operational errors.
 */
export async function gitSetWorkingDirLogic(
  input: GitSetWorkingDirInput,
  context: RequestContext & {
    sessionId?: string;
    setWorkingDirectory: (path: string) => void;
  }, // Assuming context provides session info and setter
): Promise<GitSetWorkingDirResult> {
  const operation = "gitSetWorkingDirLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let sanitizedPath: string;
  try {
    // Sanitize the path. Must explicitly allow absolute paths for this tool.
    // It normalizes and checks for traversal issues.
    sanitizedPath = sanitization.sanitizePath(input.path, {
      allowAbsolute: true,
    }).sanitizedPath;
    logger.debug(`Sanitized path: ${sanitizedPath}`, { ...context, operation });
  } catch (error: any) {
    logger.error("Path sanitization failed", error, { ...context, operation });
    if (error instanceof McpError) throw error;
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid path provided: ${error.message}`,
      { context, operation },
    );
  }

  // Check if the directory exists
  try {
    const stats = await fs.stat(sanitizedPath);
    if (!stats.isDirectory()) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Path is not a directory: ${sanitizedPath}`,
        { context, operation },
      );
    }
  } catch (error: any) {
    if (error.code === "ENOENT") {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Directory does not exist: ${sanitizedPath}`,
        { context, operation },
      );
    }
    logger.error("Failed to stat directory", error, {
      ...context,
      operation,
      path: sanitizedPath,
    });
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to access path: ${error.message}`,
      { context, operation },
    );
  }

  let isGitRepo = false;
  let initializedRepo = false;

  try {
    const { stdout } = await execFileAsync(
      "git",
      ["rev-parse", "--is-inside-work-tree"],
      {
        cwd: sanitizedPath,
      },
    );
    if (stdout.trim() === "true") {
      isGitRepo = true;
      logger.debug("Path is already a Git repository", {
        ...context,
        operation,
        path: sanitizedPath,
      });
    }
  } catch (error) {
    logger.debug(
      "Path is not a Git repository (rev-parse failed or returned non-true)",
      {
        ...context,
        operation,
        path: sanitizedPath,
        error: (error as Error).message,
      },
    );
    isGitRepo = false;
  }

  if (!isGitRepo && input.initializeIfNotPresent) {
    logger.info(
      `Path is not a Git repository. Attempting to initialize (initializeIfNotPresent=true) with initial branch 'main'.`,
      { ...context, operation, path: sanitizedPath },
    );
    try {
      await execFileAsync("git", ["init", "--initial-branch=main"], {
        cwd: sanitizedPath,
      });
      initializedRepo = true;
      isGitRepo = true; // Now it is a git repo
      logger.info(
        'Successfully initialized Git repository with initial branch "main".',
        { ...context, operation, path: sanitizedPath },
      );
    } catch (initError: any) {
      logger.error("Failed to initialize Git repository", initError, {
        ...context,
        operation,
        path: sanitizedPath,
      });
      throw new McpError(
        BaseErrorCode.INTERNAL_ERROR,
        `Failed to initialize Git repository at ${sanitizedPath}: ${initError.message}`,
        { context, operation },
      );
    }
  }

  // After potential initialization, if validateGitRepo is true, it must now be a Git repo.
  if (input.validateGitRepo && !isGitRepo) {
    logger.warning(
      "Path is not a valid Git repository and initialization was not performed or failed.",
      { ...context, operation, path: sanitizedPath },
    );
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Path is not a valid Git repository: ${sanitizedPath}.`,
      { context, operation },
    );
  }

  // --- Update Session State ---
  // This part needs access to the session state mechanism defined in server.ts
  // We assume the context provides a way to set the working directory for the current session.
  try {
    context.setWorkingDirectory(sanitizedPath);
    const message = `Working directory set for session ${context.sessionId || "stdio"} to: ${sanitizedPath}`;
    logger.info(message, { ...context, operation });
  } catch (error: any) {
    logger.error("Failed to set working directory in session state", error, {
      ...context,
      operation,
    });
    // This indicates an internal logic error in how state is passed/managed.
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      "Failed to update session state.",
      { context, operation },
    );
  }

  let message = `Working directory set to: ${sanitizedPath}`;
  if (initializedRepo) {
    message += " (New Git repository initialized).";
  } else if (isGitRepo && input.validateGitRepo) {
    // Only state "Existing" if validation was on and it passed
    message += " (Existing Git repository).";
  } else if (isGitRepo && !input.validateGitRepo) {
    // It is a git repo, but we weren't asked to validate it
    message += " (Is a Git repository, validation skipped).";
  } else if (
    !isGitRepo &&
    !input.validateGitRepo &&
    !input.initializeIfNotPresent
  ) {
    // Not a git repo, validation off, no init request
    message +=
      " (Not a Git repository, validation skipped, no initialization requested).";
  }

  return {
    success: true,
    message: message,
    path: sanitizedPath,
    initialized: initializedRepo,
  };
}
