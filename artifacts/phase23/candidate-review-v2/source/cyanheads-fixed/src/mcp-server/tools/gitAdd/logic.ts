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

// Define the input schema for the git_add tool using Zod
export const GitAddInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  files: z
    .union([z.string().min(1), z.array(z.string().min(1))])
    .default(".")
    .describe("Files or patterns to stage, defaults to all changes ('.')"),
});

// Infer the TypeScript type from the Zod schema
export type GitAddInput = z.infer<typeof GitAddInputSchema>;

// Define the structure for the JSON output
export interface GitAddResult {
  success: boolean;
  statusMessage: string; // Renamed from 'message' for consistency
  filesStaged: string[] | string; // Record what was attempted to be staged
}

/**
 * Executes the 'git add' command and returns structured JSON output.
 *
 * @param {GitAddInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitAddResult>} A promise that resolves with the structured add result.
 * @throws {McpError} Throws an McpError if path resolution or validation fails, or if the git command fails unexpectedly.
 */
export async function addGitFiles(
  input: GitAddInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  }, // Add getter to context
): Promise<GitAddResult> {
  const operation = "addGitFiles";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve the target path
    if (input.path && input.path !== ".") {
      targetPath = input.path;
      logger.debug(`Using provided path: ${targetPath}`, {
        ...context,
        operation,
      });
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
      logger.debug(`Using session working directory: ${targetPath}`, {
        ...context,
        operation,
        sessionId: context.sessionId,
      });
    }

    // Sanitize the resolved path
    const sanitizedPathInfo = sanitization.sanitizePath(targetPath, {
      allowAbsolute: true,
    });
    logger.debug("Sanitized repository path", {
      ...context,
      operation,
      sanitizedPathInfo,
    });
    targetPath = sanitizedPathInfo.sanitizedPath; // Use the sanitized path going forward
  } catch (error) {
    logger.error("Path resolution or sanitization failed", {
      ...context,
      operation,
      error,
    });
    if (error instanceof McpError) {
      throw error;
    }
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid path: ${error instanceof Error ? error.message : String(error)}`,
      { context, operation, originalError: error },
    );
  }

  const filesToStage = Array.isArray(input.files)
    ? input.files
    : [input.files];
  if (filesToStage.length === 0) {
    filesToStage.push("."); // Default to staging all if array is empty
  }

  try {
    const args = ["-C", targetPath, "add", "--"];
    filesToStage.forEach((file) => {
      // Sanitize each file path. Although execFile is safer,
      // this prevents arguments like "-v" from being treated as flags by git.
      const sanitizedFile = file.startsWith("-") ? `./${file}` : file;
      args.push(sanitizedFile);
    });

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    const { stdout, stderr } = await execFileAsync("git", args);

    if (stderr) {
      // Log stderr as warning, as 'git add' can produce warnings but still succeed.
      logger.warning(`Git add command produced stderr`, {
        ...context,
        operation,
        stderr,
      });
    }

    const filesAddedDesc = Array.isArray(filesToStage)
      ? filesToStage.join(", ")
      : filesToStage;
    const successMessage = `Successfully staged: ${filesAddedDesc}`;
    logger.info(successMessage, {
      ...context,
      operation,
      path: targetPath,
      files: filesToStage,
    });
    const reminder =
      "Remember to write clear, concise commit messages using the Conventional Commits format (e.g., 'feat(scope): subject').";
    // Use statusMessage and add reminder
    return {
      success: true,
      statusMessage: `${successMessage}. ${reminder}`,
      filesStaged: filesToStage,
    };
  } catch (error: any) {
    logger.error(`Failed to execute git add command`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      stderr: error.stderr,
    });

    const errorMessage = error.stderr || error.message || "";
    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.toLowerCase().includes("did not match any files")) {
      // Still throw an error, but return structured info in the catch block of the registration
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Specified files/patterns did not match any files in ${targetPath}: ${filesToStage.join(", ")}`,
        { context, operation, originalError: error, filesStaged: filesToStage },
      );
    }

    // Throw generic error for other cases
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to stage files for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error, filesStaged: filesToStage },
    );
  }
}
