import { execFile } from "child_process";
import fs from "fs/promises";
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

// Define the input schema for the git_clone tool using Zod
export const GitCloneInputSchema = z.object({
  repositoryUrl: z
    .string()
    .url("Invalid repository URL format.")
    .describe(
      "The URL of the repository to clone (e.g., https://github.com/cyanheads/git-mcp-server, git@github.com:cyanheads/git-mcp-server.git).",
    ),
  targetPath: z
    .string()
    .min(1)
    .describe(
      "The absolute path to the directory where the repository should be cloned.",
    ),
  branch: z
    .string()
    .optional()
    .describe("Specify a specific branch to checkout after cloning."),
  depth: z
    .number()
    .int()
    .positive()
    .optional()
    .describe(
      "Create a shallow clone with a history truncated to the specified number of commits.",
    ),
  // recursive: z.boolean().default(false).describe("After the clone is created, initialize all submodules within, using their default settings."), // Consider adding later
  quiet: z
    .boolean()
    .default(false)
    .describe(
      "Operate quietly. Progress is not reported to the standard error stream.",
    ),
});

// Infer the TypeScript type from the Zod schema
export type GitCloneInput = z.infer<typeof GitCloneInputSchema>;

// Define the structure for the JSON output
export interface GitCloneResult {
  success: boolean;
  message: string;
  path: string; // The path where the repo was cloned
  repoDirExists: boolean; // Confirms the target directory was created/populated
}

/**
 * Executes the 'git clone' command to clone a repository.
 *
 * @param {GitCloneInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitCloneResult>} A promise that resolves with the structured clone result.
 * @throws {McpError} Throws an McpError if path/URL validation fails or the git command fails unexpectedly.
 */
export async function gitCloneLogic(
  input: GitCloneInput,
  context: RequestContext,
): Promise<GitCloneResult> {
  const operation = "gitCloneLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let sanitizedTargetPath: string;
  let sanitizedRepoUrl: string;
  try {
    // Sanitize the target path (must be absolute)
    sanitizedTargetPath = sanitization.sanitizePath(input.targetPath, {
      allowAbsolute: true,
    }).sanitizedPath;
    logger.debug("Sanitized target path", {
      ...context,
      operation,
      sanitizedTargetPath,
    });

    // Basic sanitization/validation for URL (Zod already checks format)
    // Further sanitization might be needed depending on how it's used in the shell command
    // For now, rely on Zod's URL validation and careful command construction.
    sanitizedRepoUrl = input.repositoryUrl; // Assume Zod validation is sufficient for now
    logger.debug("Validated repository URL", {
      ...context,
      operation,
      sanitizedRepoUrl,
    });

    // Check if target directory already exists and is not empty
    try {
      const stats = await fs.stat(sanitizedTargetPath);
      if (stats.isDirectory()) {
        const files = await fs.readdir(sanitizedTargetPath);
        if (files.length > 0) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            `Target directory already exists and is not empty: ${sanitizedTargetPath}`,
            { context, operation },
          );
        }
      } else {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Target path exists but is not a directory: ${sanitizedTargetPath}`,
          { context, operation },
        );
      }
    } catch (error: any) {
      if (error instanceof McpError) throw error; // Re-throw our specific validation errors
      if (error.code !== "ENOENT") {
        // If error is not "does not exist", it's unexpected
        logger.error(`Error checking target directory ${sanitizedTargetPath}`, {
          ...context,
          operation,
          error: error.message,
        });
        throw new McpError(
          BaseErrorCode.INTERNAL_ERROR,
          `Failed to check target directory: ${error.message}`,
          { context, operation },
        );
      }
      // ENOENT is expected - directory doesn't exist, which is fine for clone
      logger.debug(
        `Target directory ${sanitizedTargetPath} does not exist, proceeding with clone.`,
        { ...context, operation },
      );
    }
  } catch (error) {
    logger.error("Path/URL validation or sanitization failed", {
      ...context,
      operation,
      error,
    });
    if (error instanceof McpError) throw error;
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid input: ${error instanceof Error ? error.message : String(error)}`,
      { context, operation, originalError: error },
    );
  }

  try {
    // Construct the git clone command
    const args = ["clone"];
    if (input.quiet) {
      args.push("--quiet");
    }
    if (input.branch) {
      args.push("--branch", input.branch);
    }
    if (input.depth) {
      args.push("--depth", String(input.depth));
    }
    // Add repo URL and target path
    args.push(sanitizedRepoUrl, sanitizedTargetPath);

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    // Increase timeout for clone operations as they can take time
    const { stdout, stderr } = await execFileAsync("git", args, {
      timeout: 300000,
    }); // 5 minutes timeout

    if (stderr && !input.quiet) {
      // Stderr often contains progress info, log as info if quiet is false
      logger.info(`Git clone command produced stderr (progress/info)`, {
        ...context,
        operation,
        stderr,
      });
    }
    if (stdout && !input.quiet) {
      logger.info(`Git clone command produced stdout`, {
        ...context,
        operation,
        stdout,
      });
    }

    // Verify the target directory exists after clone
    let repoDirExists = false;
    try {
      await fs.access(sanitizedTargetPath);
      repoDirExists = true;
    } catch (e) {
      logger.error(
        `Could not verify existence of target directory ${sanitizedTargetPath} after git clone`,
        { ...context, operation },
      );
      // This indicates a potential failure despite exec not throwing
      throw new McpError(
        BaseErrorCode.INTERNAL_ERROR,
        `Clone command finished but target directory ${sanitizedTargetPath} not found.`,
        { context, operation },
      );
    }

    const successMessage = `Repository cloned successfully into ${sanitizedTargetPath}`;
    logger.info(successMessage, {
      ...context,
      operation,
      path: sanitizedTargetPath,
    });
    return {
      success: true,
      message: successMessage,
      path: sanitizedTargetPath,
      repoDirExists: repoDirExists,
    };
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git clone command`, {
      ...context,
      operation,
      path: sanitizedTargetPath,
      error: errorMessage,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    // Handle specific error cases
    if (
      errorMessage.toLowerCase().includes("repository not found") ||
      errorMessage
        .toLowerCase()
        .includes("could not read from remote repository")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Repository not found or access denied: ${sanitizedRepoUrl}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage
        .toLowerCase()
        .includes("already exists and is not an empty directory")
    ) {
      // This should have been caught by our pre-check, but handle defensively
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Target directory already exists and is not empty: ${sanitizedTargetPath}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.toLowerCase().includes("permission denied")) {
      throw new McpError(
        BaseErrorCode.FORBIDDEN,
        `Permission denied during clone operation for path: ${sanitizedTargetPath}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.toLowerCase().includes("timeout")) {
      throw new McpError(
        BaseErrorCode.TIMEOUT,
        `Git clone operation timed out for repository: ${sanitizedRepoUrl}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to clone repository ${sanitizedRepoUrl} to ${sanitizedTargetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
