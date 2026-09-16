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
  GitCherryPickInput,
  GitCherryPickInputSchema,
  gitCherryPickLogic,
  GitCherryPickResult,
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
 * Initializes the state accessors needed by the git_cherry_pick tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitCherryPickStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info(
    "State accessors initialized for git_cherry_pick tool registration.",
  );
}

const TOOL_NAME = "git_cherry_pick";
const TOOL_DESCRIPTION =
  "Applies the changes introduced by existing commits. Supports picking single commits or ranges, handling merge commits, and options like --no-commit and --signoff. Returns results as a JSON object, indicating success, failure, or conflicts.";

/**
 * Registers the git_cherry_pick tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitCherryPickTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_cherry_pick must be initialized before registration.",
    );
  }

  const operation = "registerGitCherryPickTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitCherryPickInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitCherryPickInputSchema.shape,
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolInput = validatedArgs as GitCherryPickInput;
          const toolOperation = `tool:${TOOL_NAME}`;
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

          logger.info(`Executing tool: ${TOOL_NAME}`, logicContext);

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              const cherryPickResult: GitCherryPickResult =
                await gitCherryPickLogic(toolInput, logicContext);

              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(cherryPickResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              if (cherryPickResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully (Conflicts: ${!!cherryPickResult.conflicts}), returning JSON`,
                  logicContext,
                );
              } else {
                logger.warning(
                  `Tool ${TOOL_NAME} failed: ${cherryPickResult.message}`,
                  {
                    ...logicContext,
                    errorDetails: cherryPickResult.error,
                    conflicts: cherryPickResult.conflicts,
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
