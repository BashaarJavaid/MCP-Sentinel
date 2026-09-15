import { execFile } from "child_process";
import { promisify } from "util";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Direct import for types-global
import { logger, RequestContext, sanitization } from "../../../utils/index.js"; // logger (./utils/internal/logger.js), RequestContext (./utils/internal/requestContext.js), sanitization (./utils/security/sanitization.js)

const execFileAsync = promisify(execFile);

// Define the base input schema for the git_tag tool using Zod
// We export this separately to access its .shape for registration
export const GitTagBaseSchema = z.object({
  path: z
    .string()
    .min(1)
    .optional()
    .default(".")
    .describe(
      "Path to the local Git repository. Defaults to the directory set via `git_set_working_dir` for the session; set 'git_set_working_dir' if not set.",
    ),
  mode: z
    .enum(["list", "create", "delete"])
    .describe(
      "The tag operation to perform: 'list' (show all tags), 'create' (add a new tag), 'delete' (remove a local tag).",
    ),
  tagName: z
    .string()
    .min(1)
    .optional()
    .describe(
      "The name for the tag. Required for 'create' and 'delete' modes. e.g., 'v2.3.0'.",
    ),
  message: z
    .string()
    .optional()
    .describe(
      "The annotation message for the tag. Required and used only when 'mode' is 'create' and 'annotate' is true.",
    ),
  commitRef: z
    .string()
    .optional()
    .describe(
      "The commit hash, branch name, or other reference to tag. Used only in 'create' mode. Defaults to the current HEAD if omitted.",
    ),
  annotate: z
    .boolean()
    .default(false)
    .describe(
      "If true, creates an annotated tag (-a flag) instead of a lightweight tag. Requires 'message' to be provided. Used only in 'create' mode.",
    ),
  // force: z.boolean().default(false).describe("Force tag creation/update (-f flag). Use with caution as it can overwrite existing tags."), // Consider adding later
});

// Apply refinements for conditional validation and export the final schema
export const GitTagInputSchema = GitTagBaseSchema.refine(
  (data) => !(data.mode === "create" && data.annotate && !data.message),
  {
    message:
      "An annotation 'message' is required when creating an annotated tag (annotate=true).",
    path: ["message"], // Point Zod error to the message field
  },
)
  .refine((data) => !(data.mode === "create" && !data.tagName), {
    message: "A 'tagName' is required for 'create' mode.",
    path: ["tagName"], // Point Zod error to the tagName field
  })
  .refine((data) => !(data.mode === "delete" && !data.tagName), {
    message: "A 'tagName' is required for 'delete' mode.",
    path: ["tagName"], // Point Zod error to the tagName field
  });

// Infer the TypeScript type from the Zod schema
export type GitTagInput = z.infer<typeof GitTagInputSchema>;

// Define the structure for the result (using a discriminated union)
interface GitTagListResult {
  success: true;
  mode: "list";
  tags: string[];
}

interface GitTagCreateResult {
  success: true;
  mode: "create";
  message: string;
  tagName: string;
}

interface GitTagDeleteResult {
  success: true;
  mode: "delete";
  message: string;
  tagName: string;
}

interface GitTagFailureResult {
  success: false;
  mode: GitTagInput["mode"];
  message: string;
  error?: string; // Optional detailed error message
}

export type GitTagResult =
  | GitTagListResult
  | GitTagCreateResult
  | GitTagDeleteResult
  | GitTagFailureResult;

/**
 * Executes git tag commands based on the specified mode.
 *
 * @param {GitTagInput} input - The validated input object.
 * @param {RequestContext} context - The request context for logging and error handling.
 * @returns {Promise<GitTagResult>} A promise that resolves with the structured result.
 * @throws {McpError} Throws an McpError for path resolution/validation failures or unexpected errors.
 */
export async function gitTagLogic(
  input: GitTagInput,
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitTagResult> {
  const operation = `gitTagLogic:${input.mode}`;
  logger.debug(`Executing ${operation}`, { ...context, input });

  let targetPath: string;
  try {
    // Resolve and sanitize the target path
    const workingDir = context.getWorkingDirectory();
    targetPath =
      input.path && input.path !== "." ? input.path : (workingDir ?? ".");

    if (targetPath === "." && !workingDir) {
      logger.warning(
        "Executing git tag in server's CWD as no path provided and no session WD set.",
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

  // Validate tag name format (simple validation)
  if (input.tagName && !/^[a-zA-Z0-9_./-]+$/.test(input.tagName)) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid tag name format: ${input.tagName}`,
      { context, operation },
    );
  }
  // Validate commit ref format (simple validation - allows hashes, HEAD, branches, etc.)
  if (input.commitRef && !/^[a-zA-Z0-9_./~^-]+$/.test(input.commitRef)) {
    throw new McpError(
      BaseErrorCode.VALIDATION_ERROR,
      `Invalid commit reference format: ${input.commitRef}`,
      { context, operation },
    );
  }

  try {
    let args: string[];
    let result: GitTagResult;

    switch (input.mode) {
      case "list":
        args = ["-C", targetPath, "tag", "--list"];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        const { stdout: listStdout } = await execFileAsync("git", args);
        const tags = listStdout
          .trim()
          .split("\n")
          .filter((tag) => tag); // Filter out empty lines
        result = { success: true, mode: "list", tags };
        break;

      case "create":
        // TagName is validated by Zod refine
        const tagNameCreate = input.tagName!;
        args = ["-C", targetPath, "tag"];
        if (input.annotate) {
          // Message is validated by Zod refine
          args.push("-a", "-m", input.message!);
        }
        args.push(tagNameCreate);
        if (input.commitRef) {
          args.push(input.commitRef);
        }
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "create",
          message: `Tag '${tagNameCreate}' created successfully.`,
          tagName: tagNameCreate,
        };
        break;

      case "delete":
        // TagName is validated by Zod refine
        const tagNameDelete = input.tagName!;
        args = ["-C", targetPath, "tag", "-d", tagNameDelete];
        logger.debug(`Executing command: git ${args.join(" ")}`, {
          ...context,
          operation,
        });
        await execFileAsync("git", args);
        result = {
          success: true,
          mode: "delete",
          message: `Tag '${tagNameDelete}' deleted successfully.`,
          tagName: tagNameDelete,
        };
        break;

      default:
        // Should not happen due to Zod validation
        throw new McpError(
          BaseErrorCode.VALIDATION_ERROR,
          `Invalid mode: ${input.mode}`,
          { context, operation },
        );
    }

    logger.info(`git tag ${input.mode} executed successfully`, {
      ...context,
      operation,
      path: targetPath,
      result,
    });
    return result;
  } catch (error: any) {
    const errorMessage = error.stderr || error.message || "";
    logger.error(`Failed to execute git tag command`, {
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
      input.mode === "create" &&
      errorMessage.toLowerCase().includes("already exists")
    ) {
      throw new McpError(
        BaseErrorCode.CONFLICT,
        `Failed to create tag: Tag '${input.tagName}' already exists. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      input.mode === "delete" &&
      errorMessage.toLowerCase().includes("not found")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Failed to delete tag: Tag '${input.tagName}' not found. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }
    if (
      input.mode === "create" &&
      input.commitRef &&
      errorMessage
        .toLowerCase()
        .includes("unknown revision or path not in the working tree")
    ) {
      throw new McpError(
        BaseErrorCode.NOT_FOUND,
        `Failed to create tag: Commit reference '${input.commitRef}' not found. Error: ${errorMessage}`,
        { context, operation, originalError: error },
      );
    }

    // Throw a generic McpError for other failures
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      `Git tag ${input.mode} failed for path: ${targetPath}. Error: ${errorMessage}`,
      { context, operation, originalError: error },
    );
  }
}
