import { exec } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { logger, RequestContext, sanitization } from "../../../utils/index.js"; // logger (./utils/internal/logger.js), RequestContext (./utils/internal/requestContext.js), sanitization (./utils/security/sanitization.js)

const execAsync = promisify(exec);

// Define the input schema for the git_show tool using Zod
// No refinements needed here, so we don't need a separate BaseSchema
export const GitShowInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  ref: z
    .string()
    .min(1)
    .describe(
      "The object reference (commit hash, tag name, branch name, HEAD, etc.) to show.",
    ),
  filePath: z
    .string()
    .optional()
    .describe(
      "Optional specific file path within the ref to show (e.g., show a file's content at a specific commit). If provided, use the format '<ref>:<filePath>'.",
    ),
  // format: z.string().optional().describe("Optional format string for the output"), // Consider adding later
});

// Infer the TypeScript type from the Zod schema
export type GitShowInput = z.infer<typeof GitShowInputSchema>;

// Define the structure for the result
interface GitShowSuccessResult {
  success: true;
  content: string; // Raw output from git show
}

interface GitShowFailureResult {
  success: false;
  message: string;
  error?: string; // Optional detailed error message
}

export type GitShowResult = GitShowSuccessResult | GitShowFailureResult;

/**
 * Executes the 'git show' command for a given reference and optional file path.
 *
 * @param {GitShowInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitShowResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitShowLogic(
  input: GitShowInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitShowResult> {
  const operation = "gitShowLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git show in server's CWD as no path provided and no session WD set.",
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

  // Validate ref format (simple validation)
  if (!/^[a-zA-Z0-9_./~^:-]+$/.test(input.ref)) {
    // Allow ':' for filePath combination
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid reference format: ${input.ref}`,
      { context, operation },
    );
  }
  // Validate filePath format if provided (basic path chars)
  if (input.filePath && !/^[a-zA-Z0-9_./-]+$/.test(input.filePath)) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid file path format: ${input.filePath}`,
      { context, operation },
    );
  }

  try {
    // Construct the refspec, combining ref and filePath if needed
    const refSpec = input.filePath
      ? `${input.ref}:"${input.filePath}"`
      : `"${input.ref}"`;

    // Construct the command
    const command = `git -C "${targetPath}" show ${refSpec}`;
    logger.debug(`Executing command: ${command}`, { ...context, operation });

    // Execute command. Note: git show might write to stderr for non-error info (like commit details before diff)
    // We primarily care about stdout for the content. Errors usually have non-zero exit code.
    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      // Log stderr as debug info, as it might contain commit details etc.
      logger.debug(`Git show command produced stderr (may be informational)`, {
        ...context,
        operation,
        stderr,
      });
    }

    logger.info(`git show executed successfully for ref: ${refSpec}`, {
      ...context,
      operation,
      path: targetPath,
    });
    return { success: true, content: stdout }; // Return raw stdout content
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git show command`, {
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
    if (
      /unknown revision or path not in the working tree/i.test(errorMessage)
    ) {
      const target = input.filePath
        ? `${input.ref}:${input.filePath}`
        : input.ref;
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Failed to show: Reference or pathspec '${target}' not found. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (/ambiguous argument/i.test(errorMessage)) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Failed to show: Reference '${input.ref}' is ambiguous. Provide a more specific reference. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git show failed for path: ${targetPath}, ref: ${input.ref}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
