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

// Define the input schema for the git_fetch tool using Zod
export const GitFetchInputSchema = z.object({
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
      "The remote repository to fetch from (e.g., 'origin'). If omitted, fetches from 'origin' or the default configured remote.",
    ),
  prune: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Before fetching, remove any remote-tracking references that no longer exist on the remote.",
    ),
  tags: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Fetch all tags from the remote (in addition to whatever else is fetched).",
    ),
  all: z.boolean().optional().default(false).describe("Fetch all remotes."),
  // Add options like --depth, specific refspecs if needed
});

// Infer the TypeScript type from the Zod schema
export type GitFetchInput = z.infer<typeof GitFetchInputSchema>;

// Define the structure for the JSON output
export interface GitFetchResult {
  success: boolean;
  message: string; // Status message (e.g., "Fetch successful", "Fetched N objects")
  summary?: string; // More detailed summary if available (e.g., branch updates)
}

/**
 * Executes the 'git fetch' command and returns structured JSON output.
 *
 * @param {GitFetchInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitFetchResult>} A promise that resolves with the structured fetch result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function fetchGitRemote(
  input: GitFetchInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitFetchResult> {
  const operation = "fetchGitRemote";
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
    // Construct the git fetch command
    const args = ["-C", targetPath, "fetch"];

    if (input.prune) {
      args.push("--prune");
    }
    if (input.tags) {
      args.push("--tags");
    }
    if (input.all) {
      args.push("--all");
    } else if (input.remote) {
      args.push(input.remote); // Fetch specific remote if 'all' is not used
    }
    // If neither 'all' nor 'remote' is specified, git fetch defaults to 'origin' or configured upstream.

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    // Execute command. Fetch output is primarily on stderr.
    const { stdout, stderr } = await execFileAsync("git", args);

    logger.debug(`Git fetch stdout: ${stdout}`, { ...context, operation }); // stdout is usually empty
    if (stderr) {
      logger.debug(`Git fetch stderr: ${stderr}`, { ...context, operation }); // stderr contains fetch details
    }

    // Analyze stderr for success/summary
    const message = "Fetch successful.";
    const summary = stderr.trim() || "No changes detected.";

    logger.info(message, {
      ...context,
      operation,
      path: targetPath,
      summary,
    });
    return { success: true, message, summary };
  } catch (error: any) {
    logger.error(`Failed to execute git fetch command`, {
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
        `Failed to connect to remote repository '${input.remote || "default"}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("fatal: ") &&
      errorMessage.includes("couldn't find remote ref")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Remote ref not found. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("Authentication failed") ||
      errorMessage.includes("Permission denied")
    ) {
      throw new McpError(
        BaseErrorCode.UNAUTHORIZED,
        `Authentication failed for remote repository '${input.remote || "default"}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("does not appear to be a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Remote '${input.remote || "default"}' does not appear to be a git repository. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to git fetch for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
