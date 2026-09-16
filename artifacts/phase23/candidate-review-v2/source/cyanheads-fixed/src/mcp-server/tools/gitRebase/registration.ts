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
  GitRebaseBaseSchema,
  GitRebaseInput,
  gitRebaseLogic,
  GitRebaseResult,
} from "./logic.js";

// --- State Accessors ---
export type GetWorkingDirectoryFn = (
  sessionId: string | undefined,
) => string | undefined;
export type GetSessionIdFn = (
  context: Record<string, any>,
) => string | undefined;

let _getWorkingDirectory: GetWorkingDirectoryFn | undefined;
let _getSessionId: GetSessionIdFn | undefined;

/**
 * Initializes the state accessors needed by the git_rebase tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitRebaseStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_rebase tool registration.");
}

const TOOL_NAME = "git_rebase";
const TOOL_DESCRIPTION =
  "Reapplies commits on top of another base tip. Supports starting a rebase (standard or interactive), continuing, aborting, or skipping steps in an ongoing rebase. Returns results as a JSON object.";

/**
 * Registers the git_rebase tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitRebaseTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_rebase must be initialized before registration.",
    );
  }

  const operation = "registerGitRebaseTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      // Register using the BASE schema shape
      server.tool<typeof GitRebaseBaseSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitRebaseBaseSchema.shape,
        // SDK validates against the full GitRebaseInputSchema before calling this handler
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolInput = validatedArgs as GitRebaseInput; // Cast for use
          const toolOperation = `tool:${TOOL_NAME}:${toolInput.mode}`;
          const requestContext = requestContextService.createRequestContext({
            operation: toolOperation,
            parentContext: callContext,
          });

          const sessionId = _getSessionId!(requestContext);
          const getWorkingDirectoryForSession = () =>
            _getWorkingDirectory!(sessionId);

          const logicContext = {
            ...requestContext,
            sessionId: sessionId,
            getWorkingDirectory: getWorkingDirectoryForSession,
          };

          logger.info(
            `Executing tool: ${TOOL_NAME} (mode: ${toolInput.mode})`,
            logicContext,
          );

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              const rebaseResult: GitRebaseResult = await gitRebaseLogic(
                toolInput,
                logicContext,
              );

              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(rebaseResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              if (rebaseResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} (mode: ${toolInput.mode}) executed successfully (Needs Manual Action: ${!!rebaseResult.needsManualAction}), returning JSON`,
                  logicContext,
                );
              } else {
                logger.warning(
                  `Tool ${TOOL_NAME} (mode: ${toolInput.mode}) failed: ${rebaseResult.message}`,
                  {
                    ...logicContext,
                    errorDetails: rebaseResult.error,
                    conflicts: rebaseResult.conflicts,
                  },
                );
              }
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: logicContext,
              input: validatedArgs,
              errorCode: BaseErrorCode.INTERNAL_ERROR,
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  );
};
