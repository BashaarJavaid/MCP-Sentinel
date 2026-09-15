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

// Define the input schema for the git_clean tool using Zod
// No refinements needed here, but the 'force' check is critical in the logic
export const GitCleanInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  force: z
    .boolean()
    .describe(
      "REQUIRED confirmation to run the command. Must be explicitly set to true to perform the clean operation. If false or omitted, the command will not run.",
    ),
  dryRun: z
    .boolean()
    .default(false)
    .describe(
      "Show what would be deleted without actually deleting (-n flag).",
    ),
  directories: z
    .boolean()
    .default(false)
    .describe("Remove untracked directories in addition to files (-d flag)."),
  ignored: z
    .boolean()
    .default(false)
    .describe(
      "Remove ignored files as well (-x flag). Use with extreme caution.",
    ),
  // exclude: z.string().optional().describe("Exclude files matching pattern (-e <pattern>)"), // Consider adding later
});

// Infer the TypeScript type from the Zod schema
export type GitCleanInput = z.infer<typeof GitCleanInputSchema>;

// Define the structure for the result
interface GitCleanSuccessResult {
  success: true;
  message: string;
  filesAffected: string[]; // Files that were removed or would be removed (dry run)
  dryRun: boolean;
}

interface GitCleanFailureResult {
  success: false;
  message: string;
  error?: string; // Optional detailed error message
  dryRun: boolean; // Include dryRun status even on failure
}

export type GitCleanResult = GitCleanSuccessResult | GitCleanFailureResult;

/**
 * Executes the 'git clean' command to remove untracked files.
 * CRITICAL: Requires the 'force' parameter to be explicitly true.
 *
 * @param {GitCleanInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitCleanResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path/validation failures, if force=false, or unexpected errors.
 */
export async function gitCleanLogic(
  input: GitCleanInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitCleanResult> {
  const operation = "gitCleanLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  // --- CRITICAL SAFETY CHECK ---
  if (!input.force) {
    logger.error("Attempted to run git clean without force=true.", {
      ...context,
      operation,
    });
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      "Operation aborted: 'force' parameter must be explicitly set to true to execute 'git clean'. This is a destructive command.",
      { context, operation },
    );
  }
  // Log that the force check passed
  logger.warning(
    "Executing 'git clean' with force=true. This is a destructive operation.",
    { ...context, operation },
  );

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git clean in server's CWD as no path provided and no session WD set.",
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
    // Construct the command
    // Force (-f) is always added because the logic checks input.force
    const args = ["-C", targetPath, "clean", "-f"];
    if (input.dryRun) {
      args.push("-n");
    }
    if (input.directories) {
      args.push("-d");
    }
    if (input.ignored) {
      args.push("-x");
    }

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    const { stdout, stderr } = await execFileAsync("git", args);

    if (stderr) {
      // Log stderr as warning, as git clean might report non-fatal issues here
      logger.warning(`Git clean command produced stderr`, {
        ...context,
        operation,
        stderr,
      });
    }

    // Parse stdout to list affected files
    const filesAffected = stdout
      .trim()
      .split("\n")
      .map((line) =>
        line
          .replace(/^Would remove /i, "")
          .replace(/^Removing /i, "")
          .trim(),
      ) // Clean up prefixes
      .filter((file) => file); // Remove empty lines

    const message = input.dryRun
      ? `Dry run complete. Files that would be removed: ${filesAffected.length}`
      : `Clean operation complete. Files removed: ${filesAffected.length}`;

    logger.info(message, {
      ...context,
      operation,
      path: targetPath,
      dryRun: input.dryRun,
      filesAffectedCount: filesAffected.length,
    });
    return { success: true, message, filesAffected, dryRun: input.dryRun };
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git clean command`, {
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
    // Git clean usually doesn't fail with specific messages like others,
    // but returns non-zero exit code on general failure.

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git clean failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
