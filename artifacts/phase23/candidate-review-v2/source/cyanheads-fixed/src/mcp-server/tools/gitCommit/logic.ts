import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Keep direct import for types-global
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (RequestContext from ../utils/internal/requestContext.js)
import { RequestContext } from "../../../utils/index.js";
// Import utils from barrel (sanitization from ../utils/security/sanitization.js)
import { sanitization } from "../../../utils/index.js";
// Import config to check signing flag
import { config } from "../../../config/index.js";

const execFileAsync = promisify(execFile);

// Define the input schema for the git_commit tool using Zod
export const GitCommitInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  message: z
    .string()
    .min(1)
    .describe(
      "Commit message. Follow Conventional Commits format: `type(scope): subject`. Example: `feat(api): add user signup endpoint`",
    ),
  author: z
    .object({
      name: z.string().describe("Author name for the commit"),
      email: z.string().email().describe("Author email for the commit"),
    })
    .optional()
    .describe(
      "Overrides the commit author information (name and email). Use only when necessary (e.g., applying external patches).",
    ),
  allowEmpty: z
    .boolean()
    .default(false)
    .describe("Allow creating empty commits"),
  amend: z
    .boolean()
    .default(false)
    .describe("Amend the previous commit instead of creating a new one"),
  forceUnsignedOnFailure: z
    .boolean()
    .default(false)
    .describe(
      "If true and signing is enabled but fails, attempt the commit without signing instead of failing.",
    ),
  filesToStage: z
    .array(z.string().min(1))
    .optional()
    .describe(
      "Optional array of specific file paths (relative to the repository root) to stage automatically before committing. If provided, only these files will be staged.",
    ),
});

// Infer the TypeScript type from the Zod schema
export type GitCommitInput = z.infer<typeof GitCommitInputSchema>;

// Define the structure for the JSON output
export interface GitCommitResult {
  success: boolean;
  statusMessage: string; // Renamed from 'message' for clarity
  commitHash?: string; // Include hash on success
  commitMessage?: string; // The message used for the commit
  committedFiles?: string[]; // List of files included in the commit
  nothingToCommit?: boolean; // Flag for specific non-error cases
}

/**
 * Executes the 'git commit' command and returns structured JSON output.
 *
 * @param {GitCommitInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitCommitResult>} A promise that resolves with the structured commit result.
 * @throws {McpError} Throws an McpError if path resolution or validation fails, or if the git command fails unexpectedly.
 */
export async function commitGitChanges(
  input: GitCommitInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  }, // Add getter to context
): Promise<GitCommitResult> {
  const operation = "commitGitChanges";
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
    logger.debug("Sanitized path", {
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

  try {
    // --- Stage specific files if requested ---
    if (input.filesToStage && input.filesToStage.length > 0) {
      logger.debug(
        `Attempting to stage specific files: ${input.filesToStage.join(", ")}`,
        { ...context, operation },
      );
      try {
        // Correctly pass targetPath as rootDir in options object
        const sanitizedFiles = input.filesToStage.map(
          (file) =>
            sanitization.sanitizePath(file, { rootDir: targetPath })
              .sanitizedPath,
        ); // Sanitize relative to repo root
        const addArgs = ["-C", targetPath, "add", "--", ...sanitizedFiles];
        logger.debug(`Executing git add command: git ${addArgs.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", addArgs);
        logger.info(
          `Successfully staged specified files: ${sanitizedFiles.join(", ")}`,
          { ...context, operation },
        );
      } catch (addError: any) {
        logger.error("Failed to stage specified files", {
          ...context,
          operation,
          files: input.filesToStage,
          error: addError.message,
          stderr: addError.stderr,
        });
        throw new McpError(
          BaseErrorCode.INTERNAL_ERROR,
          `Failed to stage files before commit: ${addError.stderr || addError.message}`,
          { context, operation, originalError: addError },
        );
      }
    }
    // --- End staging files ---

    // Construct the git commit command using the resolved targetPath
    const args = ["-C", targetPath];

    if (input.author) {
      args.push(
        "-c",
        `user.name=${input.author.name}`,
        "-c",
        `user.email=${input.author.email}`,
      );
    }

    args.push("commit", "-m", input.message);

    if (input.allowEmpty) {
      args.push("--allow-empty");
    }
    if (input.amend) {
      args.push("--amend", "--no-edit");
    }

    // Append signing flag if configured via GIT_SIGN_COMMITS env var
    if (config.gitSignCommits) {
      args.push("-S"); // Add signing flag (-S)
      logger.info(
        "Signing enabled via GIT_SIGN_COMMITS=true, adding -S flag.",
        { ...context, operation },
      );
    }

    logger.debug(`Executing initial command attempt: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    let stdout: string;
    let stderr: string;
    let commitResult: GitCommitResult | undefined;

    try {
      // Initial attempt (potentially with -S flag)
      const execResult = await execFileAsync("git", args);
      stdout = execResult.stdout;
      stderr = execResult.stderr;
    } catch (error: any) {
      const initialErrorMessage = error.stderr || error.message || "";
      const isSigningError =
        initialErrorMessage.includes("gpg failed to sign") ||
        initialErrorMessage.includes("signing failed");

      if (isSigningError && input.forceUnsignedOnFailure) {
        logger.warning(
          "Initial commit attempt failed due to signing error. Retrying without signing as forceUnsignedOnFailure=true.",
          { ...context, operation, initialError: initialErrorMessage },
        );

        // Construct command *without* -S flag
        const unsignedArgs = args.filter((arg) => arg !== "-S");

        logger.debug(
          `Executing unsigned fallback command: git ${unsignedArgs.join(" ")}`,
          { ...context, operation },
        );

        try {
          // Retry commit without signing
          const fallbackResult = await execFileAsync("git", unsignedArgs);
          stdout = fallbackResult.stdout;
          stderr = fallbackResult.stderr;
          // Add a note to the status message indicating signing was skipped
          commitResult = {
            success: true,
            statusMessage: `Commit successful (unsigned, signing failed): ${stdout.trim()}`, // Default message, hash parsed below
            commitHash: undefined, // Will be parsed below
          };
        } catch (fallbackError: any) {
          // If the unsigned commit *also* fails, re-throw that error
          logger.error("Unsigned fallback commit attempt also failed.", {
            ...context,
            operation,
            fallbackError: fallbackError.message,
            stderr: fallbackError.stderr,
          });
          throw fallbackError; // Re-throw the error from the unsigned attempt
        }
      } else {
        // If it wasn't a signing error, or forceUnsignedOnFailure is false, re-throw the original error
        throw error;
      }
    }

    // Process result (either from initial attempt or fallback)
    // Check stderr first for common non-error messages
    if (stderr && !commitResult) {
      // Don't overwrite fallback message if stderr also exists
      if (
        stderr.includes("nothing to commit, working tree clean") ||
        stderr.includes("no changes added to commit")
      ) {
        const msg = stderr.includes("nothing to commit")
          ? "Nothing to commit, working tree clean."
          : "No changes added to commit.";
        logger.info(msg, { ...context, operation, path: targetPath });
        // Use statusMessage
        return { success: true, statusMessage: msg, nothingToCommit: true };
      }
      // Log other stderr as warning but continue, as commit might still succeed
      logger.warning(`Git commit command produced stderr`, {
        ...context,
        operation,
        stderr,
      });
    }

    // Extract commit hash (more robustly)
    let commitHash: string | undefined = undefined;
    const hashMatch = stdout.match(/([a-f0-9]{7,40})/); // Look for typical short or long hash
    if (hashMatch) {
      commitHash = hashMatch[1];
    } else {
      // Fallback parsing if needed, or rely on success message
      logger.warning("Could not parse commit hash from stdout", {
        ...context,
        operation,
        stdout,
      });
    }

    // Use statusMessage, potentially using the one set during fallback
    const finalStatusMsg =
      commitResult?.statusMessage ||
      (commitHash
        ? `Commit successful: ${commitHash}`
        : `Commit successful (stdout: ${stdout.trim()})`);

    let committedFiles: string[] = [];
    if (commitHash) {
      try {
        // Get the list of files included in this specific commit
        const showArgs = [
          "-C",
          targetPath,
          "show",
          "--pretty=",
          "--name-only",
          commitHash,
        ];
        logger.debug(`Executing git show command: git ${showArgs.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: showStdout } = await execFileAsync("git", showArgs);
        committedFiles = showStdout.trim().split("\n").filter(Boolean); // Split by newline, remove empty lines
        logger.debug(`Retrieved committed files list for ${commitHash}`, {
          ...context,
          operation,
          count: committedFiles.length,
        });
      } catch (showError: any) {
        // Log a warning but don't fail the overall operation if we can't get the file list
        logger.warning("Failed to retrieve committed files list", {
          ...context,
          operation,
          commitHash,
          error: showError.message,
          stderr: showError.stderr,
        });
      }
    }

    const successMessage = `Commit successful: ${commitHash}`;
    logger.info(successMessage, {
      ...context,
      operation,
      path: targetPath,
      commitHash,
      signed: !commitResult, // Log if it was signed (not fallback)
      committedFilesCount: committedFiles.length,
    });
    return {
      success: true,
      statusMessage: finalStatusMsg, // Use potentially modified message
      commitHash: commitHash,
      commitMessage: input.message, // Include the original commit message
      committedFiles: committedFiles, // Include the list of files
    };
  } catch (error: any) {
    // This catch block now primarily handles non-signing errors or errors from the fallback attempt
    logger.error(`Failed to execute git commit command`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
      stderr: error.stderr,
    });

    const errorMessage = error.stderr || error.message || "";

    // Handle specific error cases first
    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }

    // Check for pre-commit hook failures before checking for generic conflicts
    if (
      errorMessage.toLowerCase().includes("pre-commit hook") ||
      errorMessage.toLowerCase().includes("hook failed")
    ) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Commit failed due to pre-commit hook failure. Details: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      errorMessage.includes("nothing to commit") ||
      errorMessage.includes("no changes added to commit")
    ) {
      // This might happen if git exits with error despite these messages
      const msg = errorMessage.includes("nothing to commit")
        ? "Nothing to commit, working tree clean."
        : "No changes added to commit.";
      logger.info(msg + " (caught as error)", {
        ...context,
        operation,
        path: targetPath,
        errorMessage,
      });
      // Return success=false but indicate the reason using statusMessage
      return { success: false, statusMessage: msg, nothingToCommit: true };
    }
    if (errorMessage.includes("conflicts")) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Commit failed due to unresolved conflicts in ${targetPath}`,
        { context, operation, originalError: error },
      );
    }

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to commit changes for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
