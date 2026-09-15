import { exec } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { logger, sanitization } from "../../../utils/index.js";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js";
import { RequestContext } from "../../../utils/index.js";

const execAsync = promisify(exec);

// Define the BASE input schema for the git_worktree tool using Zod
export const GitWorktreeBaseSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: z
    .enum(["list", "add", "remove", "move", "prune"])
    .describe(
      "The worktree operation to perform: 'list', 'add', 'remove', 'move', 'prune'.",
    ),
  // Common optional path for operations
  worktreePath: z
    .string()
    .min(1)
    .optional()
    .describe(
      "Path of the worktree. Required for 'add', 'remove', 'move' modes.",
    ),
  // 'add' mode specific
  commitish: z
    .string()
    .min(1)
    .optional()
    .describe(
      "Branch or commit to checkout in the new worktree. Used only in 'add' mode. Defaults to HEAD.",
    ),
  newBranch: z
    .string()
    .min(1)
    .optional()
    .describe("Create a new branch in the worktree. Used only in 'add' mode."),
  force: z
    .boolean()
    .default(false)
    .describe(
      "Force the operation (e.g., for 'add' if branch exists, or 'remove' if uncommitted changes).",
    ),
  detach: z
    .boolean()
    .default(false)
    .describe("Detach HEAD in the new worktree. Used only in 'add' mode."),
  // 'move' mode specific
  newPath: z
    .string()
    .min(1)
    .optional()
    .describe("The new path for the worktree. Required for 'move' mode."),
  // 'prune' mode specific
  verbose: z
    .boolean()
    .default(false)
    .describe(
      "Provide more detailed output. Used in 'list' and 'prune' modes.",
    ),
  dryRun: z
    .boolean()
    .default(false)
    .describe(
      "Show what would be done without actually doing it. Used in 'prune' mode.",
    ),
  expire: z
    .string()
    .min(1)
    .optional()
    .describe(
      "Prune entries older than this time (e.g., '1.month.ago'). Used in 'prune' mode.",
    ),
});

// Apply refinements and export the FINAL schema
export const GitWorktreeInputSchema = GitWorktreeBaseSchema.refine(
  (data) => !(data.mode === "add" && !data.worktreePath),
  {
    message: "A 'worktreePath' is required for 'add' mode.",
    path: ["worktreePath"],
  },
)
  .refine((data) => !(data.mode === "remove" && !data.worktreePath), {
    message: "A 'worktreePath' is required for 'remove' mode.",
    path: ["worktreePath"],
  })
  .refine(
    (data) => !(data.mode === "move" && (!data.worktreePath || !data.newPath)),
    {
      message:
        "Both 'worktreePath' (old path) and 'newPath' are required for 'move' mode.",
      path: ["worktreePath", "newPath"],
    },
  );

export type GitWorktreeInput = z.infer<typeof GitWorktreeInputSchema>;

// --- Result Types ---
interface WorktreeInfo {
  path: string;
  head: string; // Commit SHA
  branch?: string; // Branch name, if on a branch
  isBare: boolean;
  isLocked: boolean;
  isPrunable: boolean;
  prunableReason?: string;
}

interface GitWorktreeListResult {
  success: true;
  mode: "list";
  worktrees: WorktreeInfo[];
}

interface GitWorktreeAddResult {
  success: true;
  mode: "add";
  worktreePath: string;
  branch?: string;
  head: string; // Commit SHA of the new worktree
  message: string;
}

interface GitWorktreeRemoveResult {
  success: true;
  mode: "remove";
  worktreePath: string;
  message: string;
}

interface GitWorktreeMoveResult {
  success: true;
  mode: "move";
  oldPath: string;
  newPath: string;
  message: string;
}

interface GitWorktreePruneResult {
  success: true;
  mode: "prune";
  message: string; // Output from the prune command
  prunedItems?: string[]; // Optional: if verbose output can be parsed
}

interface GitWorktreeFailureResult {
  success: false;
  mode: GitWorktreeInput["mode"];
  message: string;
  error?: string;
}

export type GitWorktreeResult =
  | GitWorktreeListResult
  | GitWorktreeAddResult
  | GitWorktreeRemoveResult
  | GitWorktreeMoveResult
  | GitWorktreePruneResult
  | GitWorktreeFailureResult;

/**
 * Parses the output of `git worktree list --porcelain`.
 */
function parsePorcelainWorktreeList(stdout: string): WorktreeInfo[] {
  const worktrees: WorktreeInfo[] = [];
  const entries = stdout.trim().split("\n\n"); // Entries are separated by double newlines

  for (const entry of entries) {
    const lines = entry.trim().split("\n");
    let path = "";
    let head = "";
    let branch: string | undefined;
    let isBare = false;
    let isLocked = false;
    let isPrunable = false;
    let prunableReason: string | undefined;

    for (const line of lines) {
      if (line.startsWith("worktree ")) {
        path = line.substring("worktree ".length);
      } else if (line.startsWith("HEAD ")) {
        head = line.substring("HEAD ".length);
      } else if (line.startsWith("branch ")) {
        branch = line.substring("branch ".length);
      } else if (line.startsWith("bare")) {
        isBare = true;
      } else if (line.startsWith("locked")) {
        isLocked = true;
        const reasonMatch = line.match(/locked(?: (.+))?/);
        if (reasonMatch && reasonMatch[1]) {
          prunableReason = reasonMatch[1]; // Using prunableReason for lock reason too
        }
      } else if (line.startsWith("prunable")) {
        isPrunable = true;
        const reasonMatch = line.match(/prunable(?: (.+))?/);
        if (reasonMatch && reasonMatch[1]) {
          prunableReason = reasonMatch[1];
        }
      }
    }
    if (path) {
      // Only add if a path was found
      worktrees.push({
        path,
        head,
        branch,
        isBare,
        isLocked,
        isPrunable,
        prunableReason,
      });
    }
  }
  return worktrees;
}

/**
 * Executes git worktree commands.
 */
export async function gitWorktreeLogic(
  input: GitWorktreeInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitWorktreeResult> {
  const operation = `gitWorktreeLogic:${input.mode}`;
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git worktree in server's CWD as no path provided and no session WD set.",
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
    let command = `git -C "${targetPath}" worktree `;
    let result: GitWorktreeResult;

    switch (input.mode) {
      case "list":
        command += "list";
        if (input.verbose) command += " --porcelain"; // Use porcelain for structured output
        logger.debug(`Executing command: ${command}`, {
          ...context,
          operation,
        });
        const { stdout: listStdout } = await execAsync(command);
        if (input.verbose) {
          const worktrees = parsePorcelainWorktreeList(listStdout);
          result = { success: true, mode: "list", worktrees };
        } else {
          // Simple list output parsing (less structured)
          const worktrees = listStdout
            .trim()
            .split("\n")
            .map((line) => {
              const parts = line.split(/\s+/);
              return {
                path: parts[0],
                head: parts[1],
                branch: parts[2]?.replace(/[\[\]]/g, ""), // Remove brackets from branch name
                isBare: false, // Cannot determine from simple list
                isLocked: false, // Cannot determine
                isPrunable: false, // Cannot determine
              };
            });
          result = { success: true, mode: "list", worktrees };
        }
        break;

      case "add":
        // worktreePath is guaranteed by refine
        const sanitizedWorktreePathAdd = sanitization.sanitizePath(
          input.worktreePath!,
          { allowAbsolute: true, rootDir: targetPath },
        ).sanitizedPath;
        command += `add `;
        if (input.force) command += "--force ";
        if (input.detach) command += "--detach ";
        if (input.newBranch) command += `-b "${input.newBranch}" `;
        command += `"${sanitizedWorktreePathAdd}"`;
        if (input.commitish) command += ` "${input.commitish}"`;

        logger.debug(`Executing command: ${command}`, {
          ...context,
          operation,
        });
        await execAsync(command);
        // To get the HEAD of the new worktree, we might need another command or parse output if available
        // For simplicity, we'll report success. A more robust solution might `git -C new_worktree_path rev-parse HEAD`
        result = {
          success: true,
          mode: "add",
          worktreePath: sanitizedWorktreePathAdd,
          branch: input.newBranch,
          head: "HEAD", // Placeholder, actual SHA would require another call
          message: `Worktree '${sanitizedWorktreePathAdd}' added successfully.`,
        };
        break;

      case "remove":
        // worktreePath is guaranteed by refine
        const sanitizedWorktreePathRemove = sanitization.sanitizePath(
          input.worktreePath!,
          { allowAbsolute: true, rootDir: targetPath },
        ).sanitizedPath;
        command += `remove `;
        if (input.force) command += "--force ";
        command += `"${sanitizedWorktreePathRemove}"`;

        logger.debug(`Executing command: ${command}`, {
          ...context,
          operation,
        });
        const { stdout: removeStdout } = await execAsync(command);
        result = {
          success: true,
          mode: "remove",
          worktreePath: sanitizedWorktreePathRemove,
          message:
            removeStdout.trim() ||
            `Worktree '${sanitizedWorktreePathRemove}' removed successfully.`,
        };
        break;

      case "move":
        // worktreePath and newPath are guaranteed by refine
        const sanitizedOldPathMove = sanitization.sanitizePath(
          input.worktreePath!,
          { allowAbsolute: true, rootDir: targetPath },
        ).sanitizedPath;
        const sanitizedNewPathMove = sanitization.sanitizePath(input.newPath!, {
          allowAbsolute: true,
          rootDir: targetPath,
        }).sanitizedPath;
        command += `move "${sanitizedOldPathMove}" "${sanitizedNewPathMove}"`;

        logger.debug(`Executing command: ${command}`, {
          ...context,
          operation,
        });
        await execAsync(command);
        result = {
          success: true,
          mode: "move",
          oldPath: sanitizedOldPathMove,
          newPath: sanitizedNewPathMove,
          message: `Worktree moved from '${sanitizedOldPathMove}' to '${sanitizedNewPathMove}' successfully.`,
        };
        break;

      case "prune":
        command += "prune ";
        if (input.dryRun) command += "--dry-run ";
        if (input.verbose) command += "--verbose ";
        if (input.expire) command += `--expire "${input.expire}" `;

        logger.debug(`Executing command: ${command}`, {
          ...context,
          operation,
        });
        const { stdout: pruneStdout, stderr: pruneStderr } =
          await execAsync(command);
        // Prune often outputs to stderr even on success for verbose/dry-run
        const pruneMessage =
          pruneStdout.trim() ||
          pruneStderr.trim() ||
          "Worktree prune operation completed.";
        result = { success: true, mode: "prune", message: pruneMessage };
        if (input.verbose && pruneStdout.trim()) {
          // Attempt to parse verbose output if needed, for now just return raw message
          // result.prunedItems = ...
        }
        break;

      default:
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Invalid mode: ${input.mode}`,
          { context, operation },
        );
    }

    logger.info(`git worktree ${input.mode} executed successfully`, {
      ...context,
      operation,
      path: targetPath,
      result,
    });
    return result;
  } catch (error: any) {
    const errorMessage = error.stderr || error.stdout || error.message || "";
    logger.error(`Failed to execute git worktree command`, {
      ...context,
      path: targetPath,
      error: errorMessage,
      stderr: error.stderr,
      stdout: error.stdout,
    });

    if (errorMessage.toLowerCase().includes("not a git repository")) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Path is not a Git repository: ${targetPath}`,
        { context, operation, originalError: error },
      );
    }
    // Add more specific error handling based on `git worktree` messages
    if (input.mode === "add" && errorMessage.includes("already exists")) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to add worktree: Path '${input.worktreePath}' already exists or is a worktree. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (input.mode === "add" && errorMessage.includes("is a submodule")) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Failed to add worktree: Path '${input.worktreePath}' is a submodule. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      input.mode === "remove" &&
      errorMessage.includes("cannot remove the current worktree")
    ) {
      throw new McpError(
        BaseErrorCode.VALIDATION_ERROR,
        `Failed to remove worktree: Cannot remove the current worktree. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      input.mode === "remove" &&
      errorMessage.includes("has unclean changes")
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to remove worktree: '${input.worktreePath}' has uncommitted changes. Use force=true to remove. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git worktree ${input.mode} failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
