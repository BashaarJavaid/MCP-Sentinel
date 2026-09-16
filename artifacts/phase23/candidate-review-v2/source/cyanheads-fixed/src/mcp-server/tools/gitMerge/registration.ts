import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (ErrorHandler from ../utils/internal/errorHandler.js)
import { ErrorHandler } from "../../../utils/index.js";
// Import utils from barrel (requestContextService from ../utils/internal/requestContext.js)
import { BaseErrorCode } from "../../../types-global/errors.js"; // Keep direct import for types-global
import { requestContextService } from "../../../utils/index.js";
import {
  GitMergeInput,
  GitMergeInputSchema,
  gitMergeLogic,
  GitMergeResult,
} from "./logic.js";

// --- State Accessors ---
// Copied from gitCommit/registration.ts as they are likely needed here too
export type GetWorkingDirectoryFn = (
  sessionId: string | undefined,
) => string | undefined;
export type GetSessionIdFn = (
  context: Record<string, any>,
) => string | undefined;

let _getWorkingDirectory: GetWorkingDirectoryFn | undefined;
let _getSessionId: GetSessionIdFn | undefined;

/**
 * Initializes the state accessors needed by the gitMerge tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitMergeStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_merge tool registration.");
}

const TOOL_NAME = "git_merge";
const TOOL_DESCRIPTION =
  "Merges the specified branch into the current branch. Supports options like --no-ff, --squash, and --abort. Returns the merge result as a JSON object.";

/**
 * Registers the git_merge tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitMergeTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_merge must be initialized before registration.",
    );
  }

  const operation = "registerGitMergeTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitMergeInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitMergeInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_merge";
          const requestContext = requestContextService.createRequestContext({
            operation: toolOperation,
            parentContext: callContext,
          });

          const sessionId = _getSessionId!(requestContext);

          const getWorkingDirectoryForSession = () => {
            return _getWorkingDirectory!(sessionId);
          };

          const logicContext = {
            ...requestContext,
            sessionId: sessionId,
            getWorkingDirectory: getWorkingDirectoryForSession,
          };

          logger.info(`Executing tool: ${TOOL_NAME}`, logicContext);

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              // Call the core logic function
              const mergeResult: GitMergeResult = await gitMergeLogic(
                validatedArgs as GitMergeInput,
                logicContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(mergeResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              // Log based on the success flag in the result
              if (mergeResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully, returning JSON`,
                  logicContext,
                );
              } else {
                // Log non-fatal conditions (like conflicts) differently from execution errors
                logger.info(
                  `Tool ${TOOL_NAME} completed with specific condition (e.g., conflict, no merge to abort), returning JSON`,
                  logicContext,
                );
              }
              // Even if success is false (e.g., conflicts), it's not a tool execution *error* in the MCP sense,
              // the tool ran, but the git operation failed predictably. Return the structured result.
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs,
              errorCode: BaseErrorCode.INTERNAL_ERROR, // Default for unexpected logic errors
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  );
};
