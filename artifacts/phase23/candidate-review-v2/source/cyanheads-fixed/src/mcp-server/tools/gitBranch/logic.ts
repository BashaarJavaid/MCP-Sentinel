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

// Define the BASE input schema for the git_branch tool using Zod
export const GitBranchBaseSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: z
    .enum(["list", "create", "delete", "rename", "show-current"])
    .describe(
      "The branch operation to perform: 'list', 'create', 'delete', 'rename', 'show-current'.",
    ),
  branchName: z
    .string()
    .min(1)
    .optional()
    .describe(
      "The name of the branch (e.g., 'feat/new-login', 'main'). Required for 'create', 'delete', 'rename' modes.",
    ),
  newBranchName: z
    .string()
    .min(1)
    .optional()
    .describe(
      "The new name for the branch (e.g., 'fix/typo-in-readme'). Required for 'rename' mode.",
    ),
  startPoint: z
    .string()
    .min(1)
    .optional()
    .describe(
      "Optional commit hash, tag, or existing branch name (e.g., 'main', 'v1.0.0', 'commit-hash') to start the new branch from. Used only in 'create' mode. Defaults to HEAD.",
    ),
  force: z
    .boolean()
    .default(false)
    .describe(
      "Force the operation. Use -D for delete, -M for rename, -f for create (if branch exists). Use with caution, as forcing operations can lead to data loss.",
    ),
  all: z
    .boolean()
    .default(false)
    .describe(
      "List both local and remote-tracking branches. Used only in 'list' mode.",
    ),
  remote: z
    .boolean()
    .default(false)
    .describe(
      "Act on remote-tracking branches. Used with 'list' (-r) or 'delete' (-r).",
    ),
});

// Apply refinements and export the FINAL schema for validation within the handler
export const GitBranchInputSchema = GitBranchBaseSchema.refine(
  (data) => !(data.mode === "create" && !data.branchName),
  {
    message: "A 'branchName' is required for 'create' mode.",
    path: ["branchName"],
  },
)
  .refine((data) => !(data.mode === "delete" && !data.branchName), {
    message: "A 'branchName' is required for 'delete' mode.",
    path: ["branchName"],
  })
  .refine(
    (data) =>
      !(data.mode === "rename" && (!data.branchName || !data.newBranchName)),
    {
      message:
        "Both 'branchName' (old name) and 'newBranchName' are required for 'rename' mode.",
      path: ["branchName", "newBranchName"],
    },
  );

// Infer the TypeScript type from the FINAL Zod schema
export type GitBranchInput = z.infer<typeof GitBranchInputSchema>;

// --- Result Types ---
interface BranchInfo {
  name: string;
  isCurrent: boolean;
  isRemote: boolean;
  commitHash?: string; // Optional: might not always be available easily
  commitSubject?: string; // Optional: from verbose listing
}

interface GitBranchListResult {
  success: true;
  mode: "list";
  branches: BranchInfo[];
  currentBranch?: string; // Explicitly state current branch if found
}

interface GitBranchCreateResult {
  success: true;
  mode: "create";
  branchName: string;
  message: string;
}

interface GitBranchDeleteResult {
  success: true;
  mode: "delete";
  branchName: string;
  wasRemote: boolean;
  message: string;
}

interface GitBranchRenameResult {
  success: true;
  mode: "rename";
  oldBranchName: string;
  newBranchName: string;
  message: string;
}

interface GitBranchShowCurrentResult {
  success: true;
  mode: "show-current";
  currentBranch: string | null; // null if in detached HEAD state
  message: string;
}

interface GitBranchFailureResult {
  success: false;
  mode: GitBranchInput["mode"];
  message: string;
  error?: string; // Optional detailed error message
}

export type GitBranchResult =
  | GitBranchListResult
  | GitBranchCreateResult
  | GitBranchDeleteResult
  | GitBranchRenameResult
  | GitBranchShowCurrentResult
  | GitBranchFailureResult;

/**
 * Executes git branch commands based on the specified mode.
 *
 * @param {GitBranchInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitBranchResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitBranchLogic(
  input: GitBranchInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitBranchResult> {
  const operation = `gitBranchLogic:${input.mode}`;
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git branch in server's CWD as no path provided and no session WD set.",
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
    let args: string[];
    let result: GitBranchResult;

    switch (input.mode) {
      case "list":
        args = ["-C", targetPath, "branch", "--list", "--no-color"]; // Start with basic list
        if (input.all) {
          args.push("-a"); // Add -a if requested
        } else if (input.remote) {
          args.push("-r"); // Add -r if requested (exclusive with -a)
        }
        args.push("--verbose"); // Add verbose for commit info

        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: listStdout } = await execFileAsync("git", args);

        const branches: BranchInfo[] = listStdout
          .trim()
          .split("\n")
          .filter((line) => line && !line.match(/^\s*->\s*/)) // Filter out HEAD pointer lines if any
          .map((line) => {
            const isCurrent = line.startsWith("* ");
            const trimmedLine = line.replace(/^\*?\s+/, ""); // Remove leading '*' and spaces
            // Determine isRemote based on the raw trimmed line BEFORE splitting
            const isRemote = trimmedLine.startsWith("remotes/");
            const parts = trimmedLine.split(/\s+/);
            const name = parts[0]; // This might be 'remotes/origin/main' or just 'main'
            const commitHash = parts[1] || undefined; // Verbose gives hash
            const commitSubject = parts.slice(2).join(" ") || undefined; // Verbose gives subject

            // Return the correct name (without 'remotes/' prefix if it was remote) and the isRemote flag
            return {
              name: isRemote ? name.split("/").slice(2).join("/") : name, // e.g., 'origin/main' or 'main'
              isCurrent,
              isRemote, // Use the flag determined before splitting
              commitHash,
              commitSubject,
            };
          });

        const currentBranch = branches.find((b) => b.isCurrent)?.name;

        result = { success: true, mode: "list", branches, currentBranch };
        break;

      case "create":
        // branchName is validated by Zod refine
        args = ["-C", targetPath, "branch"];
        if (input.force) {
          args.push("-f");
        }
        args.push(input.branchName!); // branchName is guaranteed by refine
        if (input.startPoint) {
          args.push(input.startPoint);
        }

        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "create",
          branchName: input.branchName!,
          message: `Branch '${input.branchName!}' created successfully.`,
        };
        break;

      case "delete":
        // branchName is validated by Zod refine
        args = ["-C", targetPath, "branch"];
        if (input.remote) {
          args.push("-r");
        }
        args.push(input.force ? "-D" : "-d");
        args.push(input.branchName!); // branchName is guaranteed by refine

        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: deleteStdout } = await execFileAsync("git", args);
        result = {
          success: true,
          mode: "delete",
          branchName: input.branchName!,
          wasRemote: input.remote,
          message:
            deleteStdout.trim() ||
            `Branch '${input.branchName!}' deleted successfully.`,
        };
        break;

      case "rename":
        // branchName and newBranchName validated by Zod refine
        args = ["-C", targetPath, "branch"];
        args.push(input.force ? "-M" : "-m");
        args.push(input.branchName!, input.newBranchName!);

        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "rename",
          oldBranchName: input.branchName!,
          newBranchName: input.newBranchName!,
          message: `Branch '${input.branchName!}' renamed to '${input.newBranchName!}' successfully.`,
        };
        break;

      case "show-current":
        args = ["-C", targetPath, "branch", "--show-current"];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        try {
          const { stdout: currentStdout } = await execFileAsync("git", args);
          const currentBranchName = currentStdout.trim();
          result = {
            success: true,
            mode: "show-current",
            currentBranch: currentBranchName || null,
            message: currentBranchName
              ? `Current branch is '${currentBranchName}'.`
              : "Currently in detached HEAD state.",
          };
        } catch (showError: any) {
          // Handle detached HEAD state specifically if command fails
          if (showError.stderr?.includes("HEAD detached")) {
            result = {
              success: true,
              mode: "show-current",
              currentBranch: null,
              message: "Currently in detached HEAD state.",
            };
          } else {
            throw showError; // Re-throw other errors
          }
        }
        break;

      default:
        // Should not happen due to Zod validation
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Invalid mode: ${input.mode}`,
          { context, operation },
        );
    }

    logger.info(`git branch ${input.mode} executed successfully`, {
      ...context,
      operation,
      path: targetPath,
      result,
    });
    return result;
  } catch (error: any) {
    const errorMessage = error.stderr || error.stdout || error.message || ""; // stdout might contain error messages too
    logger.error(`Failed to execute git branch command`, {
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
    if (input.mode === "create" && errorMessage.includes("already exists")) {
      return {
        success: false,
        mode: "create",
        message: `Failed to create branch: Branch '${input.branchName}' already exists. Use force=true to overwrite.`,
        error: errorMessage,
      };
    }
    if (input.mode === "delete" && errorMessage.includes("not found")) {
      return {
        success: false,
        mode: "delete",
        message: `Failed to delete branch: Branch '${input.branchName}' not found.`,
        error: errorMessage,
      };
    }
    if (input.mode === "delete" && errorMessage.includes("not fully merged")) {
      return {
        success: false,
        mode: "delete",
        message: `Failed to delete branch: Branch '${input.branchName}' is not fully merged. Use force=true to delete.`,
        error: errorMessage,
      };
    }
    if (input.mode === "rename" && errorMessage.includes("already exists")) {
      return {
        success: false,
        mode: "rename",
        message: `Failed to rename branch: Branch '${input.newBranchName}' already exists. Use force=true to overwrite.`,
        error: errorMessage,
      };
    }
    if (input.mode === "rename" && errorMessage.includes("not found")) {
      return {
        success: false,
        mode: "rename",
        message: `Failed to rename branch: Branch '${input.branchName}' not found.`,
        error: errorMessage,
      };
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git branch ${input.mode} failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
