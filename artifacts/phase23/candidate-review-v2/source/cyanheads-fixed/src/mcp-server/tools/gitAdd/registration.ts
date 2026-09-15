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
import { requestContextService } from "../../../utils/index.js";
// Import the result type along with the function and input schema
import { BaseErrorCode } from "../../../types-global/errors.js"; // Import BaseErrorCode
import {
  addGitFiles,
  GitAddInput,
  GitAddInputSchema,
  GitAddResult,
} from "./logic.js";

// --- State Accessors ---
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
export function initializeGitAddStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_add tool registration.");
}

const TOOL_NAME = "git_add";
const TOOL_DESCRIPTION =
  "Stages changes in the Git repository for the next commit by adding file contents to the index (staging area). Can stage specific files/patterns or all changes (default: '.'). Returns the result as a JSON object.";

/**
 * Registers the git_add tool with the MCP server.
 * Uses the high-level server.tool() method for registration, schema validation, and routing.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitAddTool = async (server: McpServer): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_add must be initialized before registration.",
    );
  }

  const operation = "registerGitAddTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitAddInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitAddInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_add";
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
              // Call the core logic function which now returns a GitAddResult object
              const addResult: GitAddResult = await addGitFiles(
                validatedArgs as GitAddInput,
                logicContext,
              );

              // Format the successful result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                // Stringify the JSON object for the response content
                text: JSON.stringify(addResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              logger.info(
                `Tool ${TOOL_NAME} executed successfully, returning JSON`,
                logicContext,
              );
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs,
              errorCode: BaseErrorCode.INTERNAL_ERROR, // Default error code
              // Let the logic function throw specific errors like NOT_FOUND
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  );
};
