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
} from "../../../utils/index.js"; // ErrorHandler (./utils/internal/errorHandler.js), logger (./utils/internal/logger.js), requestContextService (./utils/internal/requestContext.js)
import {
  GitRemoteInput,
  GitRemoteInputSchema,
  gitRemoteLogic,
  GitRemoteResult,
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
 * Initializes the state accessors needed by the git_remote tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitRemoteStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_remote tool registration.");
}

const TOOL_NAME = "git_remote";
const TOOL_DESCRIPTION =
  "Manages remote repositories (list, add, remove, show).";

/**
 * Registers the git_remote tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitRemoteTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_remote must be initialized before registration.",
    );
  }

  const operation = "registerGitRemoteTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitRemoteInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitRemoteInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = `tool:${TOOL_NAME}:${validatedArgs.mode}`; // Include mode in operation
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

          logger.info(
            `Executing tool: ${TOOL_NAME} (mode: ${validatedArgs.mode})`,
            logicContext,
          );

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              // Call the core logic function which returns a GitRemoteResult object
              const remoteResult: GitRemoteResult = await gitRemoteLogic(
                validatedArgs as GitRemoteInput,
                logicContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(remoteResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              // Log based on the success flag in the result
              if (remoteResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} (mode: ${validatedArgs.mode}) executed successfully, returning JSON`,
                  logicContext,
                );
              } else {
                // Log specific failure message from the result
                logger.warning(
                  `Tool ${TOOL_NAME} (mode: ${validatedArgs.mode}) failed: ${remoteResult.message}`,
                  { ...logicContext, errorDetails: remoteResult.error },
                );
              }
              // Return the result, whether success or structured failure
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs,
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
