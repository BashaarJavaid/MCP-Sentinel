import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { logger, RequestContext, sanitization } from "../../../utils/index.js"; // Logger (./utils/internal/logger.js) & RequestContext (./utils/internal/requestContext.js) & sanitization (./utils/security/sanitization.js)

const execFileAsync = promisify(execFile);

// Define the input schema for the git_remote tool using Zod
export const GitRemoteInputSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: z
    .enum(["list", "add", "remove", "show"])
    .describe("Operation mode: 'list', 'add', 'remove', 'show'"),
  name: z
    .string()
    .min(1)
    .optional()
    .describe("Remote name (required for 'add', 'remove', 'show')"),
  url: z.string().optional().describe("Remote URL (required for 'add')"), // Removed .url() validation
});

// Infer the TypeScript type from the Zod schema
export type GitRemoteInput = z.infer<typeof GitRemoteInputSchema>;

// Define the structure for the result (using a discriminated union)
interface GitRemoteListResult {
  success: true;
  mode: "list";
  remotes: { name: string; fetchUrl: string; pushUrl: string }[];
}

interface GitRemoteAddResult {
  success: true;
  mode: "add";
  message: string;
}

interface GitRemoteRemoveResult {
  success: true;
  mode: "remove";
  message: string;
}

interface GitRemoteShowResult {
  success: true;
  mode: "show";
  details: string;
}

interface GitRemoteFailureResult {
  success: false;
  mode: GitRemoteInput["mode"];
  message: string;
  error?: string; // Optional detailed error message
}

export type GitRemoteResult =
  | GitRemoteListResult
  | GitRemoteAddResult
  | GitRemoteRemoveResult
  | GitRemoteShowResult
  | GitRemoteFailureResult;

/**
 * Executes git remote commands based on the specified mode.
 *
 * @param {GitRemoteInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitRemoteResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitRemoteLogic(
  input: GitRemoteInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitRemoteResult> {
  const operation = `gitRemoteLogic:${input.mode}`;
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? "."); // Default to '.' if no working dir set and no path provided

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git remote in server's CWD as no path provided and no session WD set.",
        { ...context, operation },
      );
      // Allow execution in CWD but log it clearly. Consider if an error is more appropriate.
      // For now, let's proceed but be aware.
      targetPath = process.cwd(); // Use actual CWD if '.' was the default
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
    }).sanitizedPath; // Sanitize the final resolved path
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
    let result: GitRemoteResult;

    switch (input.mode) {
      case "list":
        args = ["-C", targetPath, "remote", "-v"];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: listStdout } = await execFileAsync("git", args);
        const remotes: GitRemoteListResult["remotes"] = [];
        const lines = listStdout.trim().split("\n");
        const remoteMap = new Map<
          string,
          { fetchUrl?: string; pushUrl?: string }
        >();

        lines.forEach((line) => {
          const parts = line.split(/\s+/);
          if (parts.length >= 3) {
            const name = parts[0];
            const url = parts[1];
            const type = parts[2].replace(/[()]/g, ""); // Remove parentheses around (fetch) or (push)
            if (!remoteMap.has(name)) {
              remoteMap.set(name, {});
            }
            if (type === "fetch") {
              remoteMap.get(name)!.fetchUrl = url;
            } else if (type === "push") {
              remoteMap.get(name)!.pushUrl = url;
            }
          }
        });

        remoteMap.forEach((urls, name) => {
          // Ensure both URLs are present, defaulting to fetch URL if push is missing (common case)
          remotes.push({
            name,
            fetchUrl: urls.fetchUrl || "N/A",
            pushUrl: urls.pushUrl || urls.fetchUrl || "N/A",
          });
        });

        result = { success: true, mode: "list", remotes };
        break;

      case "add":
        if (!input.name || !input.url) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            "Remote 'name' and 'url' are required for 'add' mode.",
            { context, operation },
          );
        }
        // Basic validation for remote name (avoiding shell injection characters)
        if (!/^[a-zA-Z0-9_.-]+$/.test(input.name)) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            `Invalid remote name: ${input.name}`,
            { context, operation },
          );
        }
        args = ["-C", targetPath, "remote", "add", input.name, input.url];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "add",
          message: `Remote '${input.name}' added successfully.`,
        };
        break;

      case "remove":
        if (!input.name) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            "Remote 'name' is required for 'remove' mode.",
            { context, operation },
          );
        }
        if (!/^[a-zA-Z0-9_.-]+$/.test(input.name)) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            `Invalid remote name: ${input.name}`,
            { context, operation },
          );
        }
        args = ["-C", targetPath, "remote", "remove", input.name];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "remove",
          message: `Remote '${input.name}' removed successfully.`,
        };
        break;

      case "show":
        if (!input.name) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            "Remote 'name' is required for 'show' mode.",
            { context, operation },
          );
        }
        if (!/^[a-zA-Z0-9_.-]+$/.test(input.name)) {
          throw new McpError(
            BaseErrorCode.VALIDATION_ERROR,
            `Invalid remote name: ${input.name}`,
            { context, operation },
          );
        }
        args = ["-C", targetPath, "remote", "show", input.name];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: showStdout } = await execFileAsync("git", args);
        result = { success: true, mode: "show", details: showStdout.trim() };
        break;

      default:
        // Should not happen due to Zod validation, but good practice
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Invalid mode: ${input.mode}`,
          { context, operation },
        );
    }

    logger.info(`git remote ${input.mode} executed successfully`, {
      ...context,
      operation,
      path: targetPath,
      result,
    });
    return result;
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git remote command`, {
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
      input.mode === "add" &&
      errorMessage.toLowerCase().includes("already exists")
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to add remote: Remote '${input.name}' already exists. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      (input.mode === "remove" || input.mode === "show") &&
      errorMessage.toLowerCase().includes("no such remote")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Failed to ${input.mode} remote: Remote '${input.name}' does not exist. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git remote ${input.mode} failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
