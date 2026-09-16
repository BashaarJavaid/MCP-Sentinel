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
  checkoutGit,
  GitCheckoutInput,
  GitCheckoutInputSchema,
  GitCheckoutResult,
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
export function initializeGitCheckoutStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info(
    "State accessors initialized for git_checkout tool registration.",
  );
}

const TOOL_NAME = "git_checkout";
const TOOL_DESCRIPTION =
  "Switches branches or restores working tree files. Can checkout branches, commits, tags, or specific file paths. Supports creating new branches and forcing checkout.";

/**
 * Registers the git_checkout tool with the MCP server.
 *
 * @param {McpServer} server - The MCP server instance.
 * @throws {Error} If state accessors are not initialized.
 */
export async function registerGitCheckoutTool(
  server: McpServer,
): Promise<void> {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_checkout must be initialized before registration.",
    );
  }

  const operation = "registerGitCheckoutTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitCheckoutInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitCheckoutInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_checkout";
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
              const checkoutResult: GitCheckoutResult = await checkoutGit(
                validatedArgs as GitCheckoutInput,
                logicContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(checkoutResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              // Log based on the success flag in the result
              if (checkoutResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully: ${checkoutResult.message}`,
                  logicContext,
                );
              } else {
                // Log non-fatal conditions like conflicts differently if needed
                logger.info(
                  `Tool ${TOOL_NAME} completed with status: ${checkoutResult.message}`,
                  logicContext,
                );
              }
              // Even if success is false (e.g., due to conflicts reported by logic),
              // it's not a tool execution error unless the logic threw an McpError.
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
