import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
// Import utils from barrel (ErrorHandler from ../utils/internal/errorHandler.js)
import { ErrorHandler } from "../../../utils/index.js";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (requestContextService, RequestContext from ../utils/internal/requestContext.js)
import { BaseErrorCode } from "../../../types-global/errors.js"; // Keep direct import for types-global
import { requestContextService } from "../../../utils/index.js";
import {
  GitClearWorkingDirInput,
  GitClearWorkingDirInputSchema,
  gitClearWorkingDirLogic,
} from "./logic.js";

// --- State Accessors ---

/** Type definition for the function that clears the working directory for a session */
export type ClearWorkingDirectoryFn = (sessionId: string | undefined) => void;
/** Type definition for the function that gets the session ID from the context */
export type GetSessionIdFn = (
  context: Record<string, any>,
) => string | undefined; // Re-using from set tool

let _clearWorkingDirectory: ClearWorkingDirectoryFn | undefined;
let _getSessionId: GetSessionIdFn | undefined;

/**
 * Initializes the state accessors needed by the tool registration.
 * This should be called once during server setup.
 * @param clearFn - Function to clear the working directory for a session.
 * @param getFn - Function to get the session ID from context.
 */
export function initializeGitClearWorkingDirStateAccessors(
  clearFn: ClearWorkingDirectoryFn,
  getFn: GetSessionIdFn,
): void {
  _clearWorkingDirectory = clearFn;
  _getSessionId = getFn; // Can reuse the getter from the set tool
  logger.info(
    "State accessors initialized for git_clear_working_dir tool registration.",
  );
}

const TOOL_NAME = "git_clear_working_dir";
const TOOL_DESCRIPTION =
  "Clears the session-specific working directory previously set by `git_set_working_dir`. Subsequent Git tool calls in this session will require an explicit `path` parameter or will default to the server's current working directory. Returns the result as a JSON object.";

/**
 * Registers the git_clear_working_dir tool with the MCP server.
 *
 * @param {McpServer} server - The MCP server instance.
 * @throws {Error} If state accessors are not initialized.
 */
export async function registerGitClearWorkingDirTool(
  server: McpServer,
): Promise<void> {
  if (!_clearWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_clear_working_dir must be initialized before registration.",
    );
  }

  try {
    server.tool<typeof GitClearWorkingDirInputSchema.shape>(
      TOOL_NAME,
      TOOL_DESCRIPTION,
      GitClearWorkingDirInputSchema.shape, // Empty shape
      async (validatedArgs, callContext) => {
        const operation = "tool:git_clear_working_dir";
        const requestContext = requestContextService.createRequestContext({
          operation,
          parentContext: callContext,
        });

        const sessionId = _getSessionId!(requestContext);

        // Define the session-specific clear function
        const clearWorkingDirectoryForSession = () => {
          _clearWorkingDirectory!(sessionId);
        };

        const logicContext = {
          ...requestContext,
          sessionId: sessionId,
          clearWorkingDirectory: clearWorkingDirectoryForSession,
        };

        return await ErrorHandler.tryCatch<CallToolResult>(
          async () => {
            // Call the core logic function
            const result = await gitClearWorkingDirLogic(
              validatedArgs as GitClearWorkingDirInput,
              logicContext,
            );

            // Format the successful result
            const responseContent: TextContent = {
              type: "text",
              text: JSON.stringify(result, null, 2),
              contentType: "application/json",
            };
            logger.info(`Tool ${TOOL_NAME} executed successfully`, {
              ...logicContext,
              result,
            });
            return { content: [responseContent] };
          },
          {
            operation,
            context: logicContext,
            input: validatedArgs,
            errorCode: BaseErrorCode.INTERNAL_ERROR,
          },
        );
      },
    );
    logger.info(`Tool registered: ${TOOL_NAME}`);
  } catch (error) {
    logger.error(`Failed to register tool: ${TOOL_NAME}`, {
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    throw error;
  }
}
