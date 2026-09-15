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

// Define the base input schema without refinement
const GitDiffInputBaseSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  commit1: z
    .string()
    .optional()
    .describe(
      "First commit, branch, or ref for comparison. If omitted, compares against the working tree or index (depending on 'staged').",
    ),
  commit2: z
    .string()
    .optional()
    .describe(
      "Second commit, branch, or ref for comparison. If omitted, compares commit1 against the working tree or index.",
    ),
  staged: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Show diff of changes staged for the next commit (compares index against HEAD). Overrides commit1/commit2 if true.",
    ),
  file: z
    .string()
    .optional()
    .describe("Limit the diff output to a specific file path."),
  includeUntracked: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      "Include untracked files in the diff output (shows their full content as new files). This is a non-standard extension.",
    ),
  // Add options like --name-only, --stat, context lines (-U<n>) if needed
});

// Export the shape for registration
export const GitDiffInputShape = GitDiffInputBaseSchema.shape;

// Define the final schema with refinement for validation during execution
export const GitDiffInputSchema = GitDiffInputBaseSchema.refine(
  (data) => !(data.staged && (data.commit1 || data.commit2)),
  {
    message:
      "Cannot use 'staged' option with specific commit references (commit1 or commit2).",
    path: ["staged", "commit1", "commit2"], // Indicate related fields
  },
);

// Infer the TypeScript type from the *final* refined Zod schema
export type GitDiffInput = z.infer<typeof GitDiffInputSchema>;

// Define the structure for the JSON output
export interface GitDiffResult {
  success: boolean;
  diff: string; // The diff output
  message?: string; // Optional status message (e.g., "No changes found")
  untrackedFilesProcessed?: number; // Number of untracked files included in the diff
}

/**
 * Executes the 'git diff' command and returns the diff output.
 *
 * @param {GitDiffInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitDiffResult>} A promise that resolves with the structured diff result.
 * @throws {McpError} Throws an McpError if path resolution, validation, or the git command fails unexpectedly.
 */
export async function diffGitChanges(
  input: GitDiffInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitDiffResult> {
  const operation = "diffGitChanges";
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

  // Basic sanitization for refs and file path
  const safeCommit1 = input.commit1?.replace(/[`$&;*()|<>]/g, "");
  const safeCommit2 = input.commit2?.replace(/[`$&;*()|<>]/g, "");
  const safeFile = input.file?.replace(/[`$&;*()|<>]/g, "");

  let untrackedFilesDiff = "";
  let untrackedFilesCount = 0;

  try {
    // Construct the standard git diff command
    const standardDiffArgs = ["-C", targetPath, "diff"];

    if (input.staged) {
      standardDiffArgs.push("--staged"); // Or --cached
    } else {
      // Add commit references if not doing staged diff
      if (safeCommit1) {
        standardDiffArgs.push(safeCommit1);
      }
      if (safeCommit2) {
        standardDiffArgs.push(safeCommit2);
      }
    }

    // Add file path limiter if provided for standard diff
    // Note: `input.file` will not apply to the untracked files part unless we explicitly filter them.
    // For simplicity, `includeUntracked` will show all untracked files if `input.file` is also set.
    if (safeFile) {
      standardDiffArgs.push("--", safeFile); // Use '--' to separate paths from revisions
    }

    logger.debug(
      `Executing standard diff command: git ${standardDiffArgs.join(" ")}`,
      {
        ...context,
        operation,
      },
    );
    const { stdout: standardStdout, stderr: standardStderr } =
      await execFileAsync("git", standardDiffArgs, {
        maxBuffer: 1024 * 1024 * 20,
      });

    if (standardStderr) {
      logger.warning(`Git diff (standard) stderr: ${standardStderr}`, {
        ...context,
        operation,
      });
    }
    let combinedDiffOutput = standardStdout;

    // Handle untracked files if requested
    if (input.includeUntracked) {
      logger.debug("Including untracked files.", { ...context, operation });
      const listUntrackedArgs = [
        "-C",
        targetPath,
        "ls-files",
        "--others",
        "--exclude-standard",
      ];
      try {
        const { stdout: untrackedFilesStdOut } = await execFileAsync(
          "git",
          listUntrackedArgs,
        );
        const untrackedFiles = untrackedFilesStdOut
          .trim()
          .split("\n")
          .filter((f) => f); // Filter out empty lines

        if (untrackedFiles.length > 0) {
          logger.info(`Found ${untrackedFiles.length} untracked files.`, {
            ...context,
            operation,
            untrackedFiles,
          });
          let individualUntrackedDiffs = "";
          for (const untrackedFile of untrackedFiles) {
            // Sanitize each untracked file path before using in command
            const safeUntrackedFile = untrackedFile.replace(
              /[`$&;*()|<>]/g,
              "",
            );
            // Skip if file path becomes empty after sanitization (unlikely but safe)
            if (!safeUntrackedFile) continue;

            const untrackedDiffArgs = [
              "-C",
              targetPath,
              "diff",
              "--no-index",
              "/dev/null",
              safeUntrackedFile,
            ];
            logger.debug(
              `Executing diff for untracked file: git ${untrackedDiffArgs.join(" ")}`,
              { ...context, operation, file: safeUntrackedFile },
            );
            try {
              const { stdout: untrackedFileDiffOut } = await execFileAsync(
                "git",
                untrackedDiffArgs,
              );
              individualUntrackedDiffs += untrackedFileDiffOut;
              untrackedFilesCount++;
            } catch (untrackedError: any) {
              // For `git diff --no-index`, a non-zero exit code (usually 1) means differences were found.
              // The actual diff output will be in untrackedError.stdout.
              if (untrackedError.stdout) {
                individualUntrackedDiffs += untrackedError.stdout;
                untrackedFilesCount++;
                // Log stderr if it exists, as it might contain actual error messages despite stdout having the diff
                if (untrackedError.stderr) {
                  logger.warning(
                    `Stderr while diffing untracked file ${safeUntrackedFile} (diff captured from stdout): ${untrackedError.stderr}`,
                    { ...context, operation, file: safeUntrackedFile },
                  );
                }
              } else {
                // If stdout is empty, then it's a more genuine failure.
                logger.warning(
                  `Failed to diff untracked file: ${safeUntrackedFile}. Error: ${untrackedError.message}`,
                  {
                    ...context,
                    operation,
                    file: safeUntrackedFile,
                    errorDetails: {
                      stderr: untrackedError.stderr,
                      stdout: untrackedError.stdout,
                      code: untrackedError.code,
                    },
                  },
                );
                individualUntrackedDiffs += `\n--- Diff for untracked file ${safeUntrackedFile} failed: ${untrackedError.message}\n`;
              }
            }
          }
          if (individualUntrackedDiffs) {
            // Add a separator if standard diff also had output
            if (combinedDiffOutput.trim()) {
              combinedDiffOutput += "\n";
            }
            combinedDiffOutput += individualUntrackedDiffs;
          }
        } else {
          logger.info("No untracked files found.", { ...context, operation });
        }
      } catch (lsFilesError: any) {
        logger.warning(
          `Failed to list untracked files. Error: ${lsFilesError.message}`,
          {
            ...context,
            operation,
            error: lsFilesError.stderr || lsFilesError.stdout,
          },
        );
        // Proceed without untracked files if listing fails
      }
    }

    const isNoChanges = combinedDiffOutput.trim() === "";
    const finalDiffOutput = isNoChanges
      ? "No changes found."
      : combinedDiffOutput;
    let message = isNoChanges
      ? "No changes found."
      : "Diff generated successfully.";
    if (untrackedFilesCount > 0) {
      message += ` Included ${untrackedFilesCount} untracked file(s).`;
    }

    logger.info(message, {
      ...context,
      operation,
      path: targetPath,
      untrackedFilesProcessed: untrackedFilesCount,
    });
    return {
      success: true,
      diff: finalDiffOutput,
      message,
      untrackedFilesProcessed: untrackedFilesCount,
    };
  } catch (error: any) {
    // This catch block now primarily handles errors from the *standard* diff command
    // or catastrophic failures before/after untracked file processing.
    logger.error(`Failed to execute git diff operation`, {
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
      errorMessage.includes("fatal: bad object") ||
      errorMessage.includes("unknown revision or path not in the working tree")
    ) {
      const invalidRef = input.commit1 || input.commit2 || input.file;
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Invalid commit reference or file path specified: '${invalidRef}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (errorMessage.includes("ambiguous argument")) {
      const ambiguousArg = input.commit1 || input.commit2 || input.file;
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Ambiguous argument provided: '${ambiguousArg}'. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // If the command exits with an error but stdout has content, it might still be useful (e.g., diff with conflicts)
    // However, standard 'git diff' usually exits 0 even with differences. Errors typically mean invalid input/repo state.
    // We'll treat most exec errors as failures.

    // Generic internal error for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Failed to get git diff for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
