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

// Define the BASE input schema for the git_rebase tool using Zod
export const GitRebaseBaseSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: z
    .enum(["start", "continue", "abort", "skip"])
    .default("start")
    .describe(
      "Rebase operation mode: 'start' (initiate rebase), 'continue', 'abort', 'skip' (manage ongoing rebase).",
    ),
  upstream: z
    .string()
    .min(1)
    .optional()
    .describe(
      "The upstream branch or commit to rebase onto. Required for 'start' mode unless 'interactive' is true with default base.",
    ),
  branch: z
    .string()
    .min(1)
    .optional()
    .describe(
      "The branch to rebase. Defaults to the current branch if omitted.",
    ),
  interactive: z
    .boolean()
    .default(false)
    .describe(
      "Perform an interactive rebase (`-i`). 'upstream' can be omitted to rebase current branch's tracked upstream or use fork-point.",
    ),
  strategy: z
    .enum(["recursive", "resolve", "ours", "theirs", "octopus", "subtree"])
    .optional()
    .describe("Specifies the merge strategy to use during rebase."),
  strategyOption: z
    .string()
    .optional()
    .describe(
      "Pass a specific option to the merge strategy (e.g., 'ours', 'theirs' for recursive). Use with -X.",
    ),
  onto: z
    .string()
    .min(1)
    .optional()
    .describe(
      "Rebase onto a specific commit/branch instead of the upstream's base. Requires 'upstream' to be specified.",
    ),
  // TODO: Add options like --preserve-merges, --autosquash, --autostash?
});

// Apply refinements and export the FINAL schema for validation within the handler
export const GitRebaseInputSchema = GitRebaseBaseSchema.refine(
  (data) => !(data.mode === "start" && !data.interactive && !data.upstream),
  {
    message:
      "An 'upstream' branch/commit is required for 'start' mode unless 'interactive' is true.",
    path: ["upstream"],
  },
).refine(
  (data) =>
    !(
      data.mode !== "start" &&
      (data.upstream ||
        data.branch ||
        data.interactive ||
        data.strategy ||
        data.onto)
    ),
  {
    message:
      "Parameters like 'upstream', 'branch', 'interactive', 'strategy', 'onto' are only applicable for 'start' mode.",
    path: ["mode"],
  },
);

// Infer the TypeScript type from the Zod schema
export type GitRebaseInput = z.infer<typeof GitRebaseInputSchema>;

// Define the structure for the result
interface GitRebaseSuccessResult {
  success: true;
  mode: GitRebaseInput["mode"];
  message: string;
  rebaseCompleted?: boolean; // True if the rebase finished successfully (relevant for start/continue)
  needsManualAction?: boolean; // True if conflicts or interactive steps require user input
}

interface GitRebaseFailureResult {
  success: false;
  mode: GitRebaseInput["mode"];
  message: string;
  error?: string; // Detailed error message
  conflicts?: boolean; // Specifically for failures due to conflicts
}

export type GitRebaseResult = GitRebaseSuccessResult | GitRebaseFailureResult;

/**
 * Executes the 'git rebase' command based on the specified mode.
 *
 * @param {GitRebaseInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitRebaseResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitRebaseLogic(
  input: GitRebaseInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitRebaseResult> {
  const operation = `gitRebaseLogic:${input.mode}`;
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git rebase in server's CWD as no path provided and no session WD set.",
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
    const args = ["-C", targetPath, "rebase"];

    switch (input.mode) {
      case "start":
        if (input.interactive) {
          args.push("-i");
        }
        if (input.strategy) {
          args.push(`--strategy=${input.strategy}`);
        }
        if (input.strategyOption) {
          args.push(`-X${input.strategyOption}`);
        } // Note: -X for strategy options
        if (input.onto) {
          args.push("--onto", input.onto);
        }
        // Upstream is required by refine unless interactive
        if (input.upstream) {
          args.push(input.upstream);
        }
        if (input.branch) {
          args.push(input.branch);
        }
        break;
      case "continue":
        args.push("--continue");
        break;
      case "abort":
        args.push("--abort");
        break;
      case "skip":
        args.push("--skip");
        break;
      default:
        // Should not happen due to Zod validation
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Invalid mode: ${input.mode}`,
          { context, operation },
        );
    }

    logger.debug(`Executing command: git ${args.join(" ")}`, {
      ...context,
      operation,
    });

    try {
      const { stdout, stderr } = await execFileAsync("git", args);
      const output = stdout + stderr;

      const message = `Rebase ${input.mode} executed successfully. Output: ${output.trim()}`;
      logger.info(message, { ...context, operation, path: targetPath });
      return {
        success: true,
        mode: input.mode,
        message,
        rebaseCompleted: /successfully rebased/.test(output),
        needsManualAction: /conflict|stopped at|edit/i.test(output),
      };
    } catch (rebaseError: any) {
      const errorMessage =
        rebaseError.stderr || rebaseError.stdout || rebaseError.message || "";
      logger.error(`Git rebase ${input.mode} command failed`, {
        ...context,
        operation,
        path: targetPath,
        error: errorMessage,
        stderr: rebaseError.stderr,
        stdout: rebaseError.stdout,
      });

      // Handle specific error cases
      if (/conflict/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.CONFLICT,
          `Rebase ${input.mode} failed due to conflicts. Resolve conflicts and use 'git rebase --continue'. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }
      if (/no rebase in progress/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Failed to ${input.mode} rebase: No rebase is currently in progress. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }
      if (/cannot rebase onto multiple branches/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Failed to start rebase: Cannot rebase onto multiple branches. Check your 'upstream' parameter. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }
      if (/does not point to a valid commit/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Failed to start rebase: Invalid upstream, branch, or onto reference provided. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }
      if (/your local changes would be overwritten/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.CONFLICT,
          `Failed to ${input.mode} rebase: Your local changes to tracked files would be overwritten. Please commit or stash them. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }
      if (/interactive rebase already started/i.test(errorMessage)) {
        throw new McpError(
          BaseErrorCode.CONFLICT,
          `Failed to start rebase: An interactive rebase is already in progress. Use 'continue', 'abort', or 'skip'. Error: ${errorMessage}`,
          { context, operation, originalError: rebaseError },
        );
      }

      // Throw McpError for critical issues like non-existent repo
      if (errorMessage.toLowerCase().includes("not a git repository")) {
        throw new McpError(
          BaseErrorCode.NOT_FOUND,
          `Path is not a Git repository: ${targetPath}`,
          { context, operation, originalError: rebaseError },
        );
      }

      // Throw a generic McpError for other failures
      throw new McpError(
        BaseErrorCode.INTERNAL_ERROR,
        `Git rebase ${input.mode} failed for path: ${targetPath}. Error: ${errorMessage}`,
        { context, operation, originalError: rebaseError },
      );
    }
  } catch (error: any) {
    // Catch errors from path resolution or unexpected issues before command execution
    logger.error(`Unexpected error during git rebase setup or execution`, {
      ...context,
      operation,
      path: targetPath,
      error: error.message,
    });
    if (error instanceof McpError) throw error;
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `An unexpected error occurred during git rebase ${input.mode}: ${error.message}`,
      { context, operation, originalError: error },
    );
  }
}
