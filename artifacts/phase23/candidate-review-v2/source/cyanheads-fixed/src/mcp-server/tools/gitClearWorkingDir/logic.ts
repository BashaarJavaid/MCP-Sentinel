import { z } from "zod";
// Import utils from barrel (RequestContext from ../utils/internal/requestContext.js)
import { RequestContext } from "../../../utils/index.js";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { BaseErrorCode, McpError } from "../../../types-global/errors.js"; // Keep direct import for types-global
import { logger } from "../../../utils/index.js";

// Define the Zod schema for input validation (no arguments needed)
export const GitClearWorkingDirInputSchema = z.object({});

// Infer the TypeScript type from the Zod schema
export type GitClearWorkingDirInput = z.infer<
  typeof GitClearWorkingDirInputSchema
>;

// Define the TypeScript interface for the result
export interface GitClearWorkingDirResult {
  success: boolean;
  message: string;
}

/**
 * Logic for the git_clear_working_dir tool.
 * Clears the global working directory setting for the current session.
 *
 * @param {GitClearWorkingDirInput} input - The validated input arguments (empty object).
 * @param {RequestContext} context - The request context, containing session ID and the clear function.
 * @returns {Promise<GitClearWorkingDirResult>} The result of the operation.
 * @throws {McpError} Throws McpError for operational errors.
 */
export async function gitClearWorkingDirLogic(
  input: GitClearWorkingDirInput,
  context: RequestContext & {
    sessionId?: string;
    clearWorkingDirectory: () => void;
  }, // Assuming context provides session info and clearer
): Promise<GitClearWorkingDirResult> {
  const operation = "gitClearWorkingDirLogic";
  logger.debug(`Executing ${operation}`, { ...context, input });

  // --- Update Session State ---
  // This part needs access to the session state mechanism defined in server.ts
  // We assume the context provides a way to clear the working directory for the current session.
  try {
    context.clearWorkingDirectory();
    const message = `Working directory cleared for session ${context.sessionId || "stdio"}`;
    logger.info(message, { ...context, operation });
  } catch (error: any) {
    logger.error("Failed to clear working directory in session state", error, {
      ...context,
      operation,
    });
    // This indicates an internal logic error in how state is passed/managed.
    throw new McpError(
      BaseErrorCode.INTERNAL_ERROR,
      "Failed to update session state.",
      { context, operation },
    );
  }

  return {
    success: true,
    message: "Global working directory setting cleared.",
  };
}
