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
} from "../../../utils/index.js"; // logger (./utils/internal/logger.js), ErrorHandler (./utils/internal/errorHandler.js), requestContextService (./utils/internal/requestContext.js)
// Import the schema and types
import {
  GitShowInput,
  GitShowInputSchema,
  gitShowLogic,
  GitShowResult,
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
 * Initializes the state accessors needed by the git_show tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitShowStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_show tool registration.");
}

const TOOL_NAME = "git_show";
const TOOL_DESCRIPTION =
  "Shows information about Git objects (commits, tags, blobs, trees) based on a reference. Can optionally show the content of a specific file at that reference. Returns the raw output.";

/**
 * Registers the git_show tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitShowTool = async (server: McpServer): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_show must be initialized before registration.",
    );
  }

  const operation = "registerGitShowTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      // Register the tool using the schema's shape (no refinements here)
      server.tool<typeof GitShowInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitShowInputSchema.shape, // Use the shape directly
        // Let TypeScript infer handler argument types.
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          // Cast validatedArgs to the specific input type for use within the handler
          const toolInput = validatedArgs as GitShowInput;
          const toolOperation = `tool:${TOOL_NAME}`;
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
              // Call the core logic function which returns a GitShowResult object
              const showResult: GitShowResult = await gitShowLogic(
                toolInput,
                logicContext,
              );

              // Format the result within TextContent
              const resultContent: TextContent = {
                type: "text",
                // Return raw content on success, or error message on failure
                text: showResult.success
                  ? showResult.content
                  : `Error: ${showResult.message}${showResult.error ? `\nDetails: ${showResult.error}` : ""}`,
                // Use plain text content type, unless we decide to return JSON later
                contentType: "text/plain",
              };

              // Log based on the success flag in the result
              if (showResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully`,
                  logicContext,
                );
              } else {
                // Log specific failure message from the result
                logger.warning(
                  `Tool ${TOOL_NAME} failed: ${showResult.message}`,
                  { ...logicContext, errorDetails: showResult.error },
                );
              }
              // Return the result, whether success or structured failure
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs, // Log the raw validated args
              errorCode: BaseErrorCode.INTERNAL_ERROR, // Default if unexpected error occurs in logic/wrapper
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  ); // Mark registration as critical
};
