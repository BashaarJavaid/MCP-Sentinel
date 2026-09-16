import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
import { BaseErrorCode } from "../../../types-global/errors.js"; // Direct import for types-global
import {
  ErrorHandler,
  logger,
  requestContextService,
} from "../../../utils/index.js"; // ErrorHandler (./utils/internal/errorHandler.js), logger (./utils/internal/logger.js), requestContextService & RequestContext (./utils/internal/requestContext.js)
import {
  GitResetInput,
  GitResetInputSchema,
  GitResetResult,
  resetGitState,
} from "./logic.js";

// --- State Accessors ---
// These functions need to be provided by the server setup layer (server.ts)

/** Type definition for the function that gets the working directory for a session */
export type GetWorkingDirectoryFn = (
  sessionId: string | undefined,
) => string | undefined;
/** Type definition for the function that gets the session ID from the context */
export type GetSessionIdFn = (
  context: Record<string, any>,
) => string | undefined;

let _getWorkingDirectory: GetWorkingDirectoryFn | undefined;
let _getSessionId: GetSessionIdFn | undefined;

/**
 * Initializes the state accessors needed by the tool registration.
 * This should be called once during server setup.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitResetStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_reset tool registration.");
}

const TOOL_NAME = "git_reset";
const TOOL_DESCRIPTION =
  "Resets the current HEAD to a specified state. Supports different modes ('soft', 'mixed', 'hard', 'merge', 'keep') to control how the index and working tree are affected. Can reset to a specific commit. USE 'hard' MODE WITH EXTREME CAUTION as it discards local changes.";

/**
 * Registers the git_reset tool with the MCP server.
 *
 * @param {McpServer} server - The MCP server instance.
 * @throws {Error} If state accessors are not initialized.
 */
export async function registerGitResetTool(server: McpServer): Promise<void> {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_reset must be initialized before registration.",
    );
  }

  const operation = "registerGitResetTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitResetInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitResetInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_reset";
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
              const resetResult: GitResetResult = await resetGitState(
                validatedArgs as GitResetInput,
                logicContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                // Stringify the entire GitResetResult object
                text: JSON.stringify(resetResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              logger.info(
                `Tool ${TOOL_NAME} executed successfully: ${resetResult.message}`,
                logicContext,
              );
              // Success is determined by the logic function and included in the result object
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs,
              errorCode: BaseErrorCode.INTERNAL_ERROR, // Default if unexpected error in logic
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  );
}
