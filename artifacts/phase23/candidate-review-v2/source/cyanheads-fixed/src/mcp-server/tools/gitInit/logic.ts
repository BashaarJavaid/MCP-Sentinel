import { execFile } from "child_process";
import fs from "fs/promises";
import path from "path";
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

// Define the input schema for the git_init tool using Zod
export const GitInitInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path where the new Git repository should be initialized. Can be relative or absolute. If relative or '.', it resolves against the directory set via `git_set_working_dir` for the session. If absolute, it's used directly. If omitted, defaults to '.' (resolved against session git working directory).",
    ),
  initialBranch: z
    .string()
    .optional()
    .describe(
      "Optional name for the initial branch (e.g., 'main'). Uses Git's default if not specified.",
    ),
  bare: z
    .boolean()
    .default(false)
    .describe("Create a bare repository (no working directory)."),
  quiet: z
    .boolean()
    .default(false)
    .describe(
      "Only print error and warning messages; all other output will be suppressed.",
    ),
});

// Infer the TypeScript type from the Zod schema
export type GitInitInput = z.infer<typeof GitInitInputSchema>;

// Define the structure for the JSON output
export interface GitInitResult {
  success: boolean;
  message: string;
  path: string; // The path where the repo was initialized
  gitDirExists: boolean; // Confirms the .git directory was created (or equivalent for bare)
}

/**
 * Executes the 'git init' command to initialize a new Git repository.
 *
 * @param {GitInitInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitInitResult>} A promise that resolves with the structured init result.
 * @throws {McpError} Throws an McpError if path validation fails or the git command fails unexpectedly.
 */
export async function gitInitLogic(
  input: GitInitInput,
  context: RequestContext,
): Promise<GitInitResult> {
  const operation = "gitInitLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Sanitize the provided absolute path
    targetPath = sanitization.sanitizePath(input.path, {
      allowAbsolute: true,
    }).sanitizedPath;
    logger.debug("Sanitized path", {
      ...context,
      operation,
      sanitizedPath: targetPath,
    });

    // Ensure the target directory exists before trying to init inside it
    // git init creates the directory if it doesn't exist, but we might want to ensure the parent exists
    const parentDir = path.dirname(targetPath);
    try {
      await fs.access(parentDir, fs.constants.W_OK); // Check write access in parent
    } catch (accessError: any) {
      logger.error(`Parent directory check failed for ${targetPath}`, {
        ...context,
        operation,
        error: accessError.message,
      });
      if (accessError.code === "ENOENT") {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Parent directory does not exist: ${parentDir}`,
          { context, operation },
        );
      }
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Cannot access parent directory: ${parentDir}. Error: ${accessError.message}`,
        { context, operation },
      );
    }
  } catch (error) {
    logger.error("Path validation or sanitization failed", {
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
    // Construct the git init command
    const args: string[] = ["init"];
    if (input.quiet) {
      args.push("--quiet");
    }
    if (input.bare) {
      args.push("--bare");
    }
    // Determine the initial branch name, defaulting to 'main' if not provided
    const branchNameToUse = input.initialBranch || "main";
    args.push("-b", branchNameToUse);

    // Add the target directory path at the end
    args.push(targetPath);

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    const { stdout, stderr } = await execFileAsync("git", args);

    if (stderr && !input.quiet) {
      // Log stderr as warning but proceed, as init might still succeed (e.g., reinitializing)
      logger.warning(`Git init command produced stderr`, {
        ...context,
        operation,
        stderr,
      });
    }
    if (stdout && !input.quiet) {
      // Log stdout at debug level for cleaner info logs
      logger.debug(`Git init command produced stdout`, {
        ...context,
        operation,
        stdout,
      });
    }

    // Verify .git directory exists (or equivalent for bare repo)
    const gitDirPath = input.bare ? targetPath : path.join(targetPath, ".git");
    let gitDirExists = false;
    try {
      await fs.access(gitDirPath);
      gitDirExists = true;
    } catch (e) {
      logger.warning(
        `Could not verify existence of ${gitDirPath} after git init`,
        { ...context, operation },
      );
    }

    const successMessage = `Successfully initialized Git repository in ${targetPath}`;
    logger.info(successMessage, {
      ...context,
      operation,
      path: targetPath,
      bare: input.bare,
      initialBranch: input.initialBranch || "default",
    });
    return {
      success: true,
      message: stdout.trim() || successMessage, // Return stdout to user if available
      path: targetPath,
      gitDirExists: gitDirExists,
    };
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git init command`, {
      ...context,
      operation,
      path: targetPath,
      error: errorMessage,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    // Handle specific error cases
    if (
      errorMessage.toLowerCase().includes("already exists") &&
      errorMessage.toLowerCase().includes("git repository")
    ) {
      // Reinitializing is often okay, treat as success but mention it.
      logger.info(`Repository already exists, reinitialized: ${targetPath}`, {
        ...context,
        operation,
      });
      return {
        success: true, // Treat reinitialization as success
        message: `Reinitialized existing Git repository in ${targetPath}`,
        path: targetPath,
        gitDirExists: true, // Assume it exists if reinit message appears
      };
    }
    if (errorMessage.toLowerCase().includes("permission denied")) {
      throw new McpError(
        BaseErrorCode.FORBIDDEN,
        `Permission denied to initialize repository at: ${targetPath}. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to initialize repository at: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
