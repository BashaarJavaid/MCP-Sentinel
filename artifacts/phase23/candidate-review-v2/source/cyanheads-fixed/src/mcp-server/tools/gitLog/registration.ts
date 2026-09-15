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
  GitLogInput,
  GitLogInputSchema,
  GitLogResult,
  logGitHistory,
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
export function initializeGitLogStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_log tool registration.");
}

const TOOL_NAME = "git_log";
const TOOL_DESCRIPTION =
  "Shows commit logs for the repository. Supports limiting count, filtering by author, date range, and specific branch/file. Returns a JSON object containing a list of commit objects (`commits` array) by default. If `showSignature: true` is used, it returns a JSON object where the `commits` array is empty and the raw signature verification output is included in the `message` field.";

/**
 * Registers the git_log tool with the MCP server.
 *
 * @param {McpServer} server - The MCP server instance.
 * @throws {Error} If state accessors are not initialized.
 */
export async function registerGitLogTool(server: McpServer): Promise<void> {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_log must be initialized before registration.",
    );
  }

  const operation = "registerGitLogTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitLogInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitLogInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_log";
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
              const logResult: GitLogResult = await logGitHistory(
                validatedArgs as GitLogInput,
                logicContext,
              );

              // Format the result (array of commits) as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                // Stringify the entire GitLogResult object which includes the commits array and success flag
                text: JSON.stringify(logResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              logger.info(
                `Tool ${TOOL_NAME} executed successfully, returning JSON`,
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
