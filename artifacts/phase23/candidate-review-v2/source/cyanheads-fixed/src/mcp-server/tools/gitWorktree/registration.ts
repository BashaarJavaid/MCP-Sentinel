import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
import {
  logger,
  ErrorHandler,
  requestContextService,
} from "../../../utils/index.js";
import { BaseErrorCode } from "../../../types-global/errors.js";
import {
  GitWorktreeBaseSchema,
  GitWorktreeInput,
  gitWorktreeLogic,
  GitWorktreeResult,
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
 * Initializes the state accessors needed by the git_worktree tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitWorktreeStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info(
    "State accessors initialized for git_worktree tool registration.",
  );
}

const TOOL_NAME = "git_worktree";
const TOOL_DESCRIPTION =
  "Manages Git worktrees. Supports listing, adding, removing, moving, and pruning worktrees. Returns results as a JSON object.";

/**
 * Registers the git_worktree tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitWorktreeTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_worktree must be initialized before registration.",
    );
  }

  const operation = "registerGitWorktreeTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitWorktreeBaseSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitWorktreeBaseSchema.shape,
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolInput = validatedArgs as GitWorktreeInput; // Cast for use
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
              const worktreeResult: GitWorktreeResult = await gitWorktreeLogic(
                toolInput,
                logicContext,
              );

              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(worktreeResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              if (worktreeResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} (mode: ${toolInput.mode}) executed successfully, returning JSON`,
                  logicContext,
                );
              } else {
                logger.warning(
                  `Tool ${TOOL_NAME} (mode: ${toolInput.mode}) failed: ${worktreeResult.message}`,
                  { ...logicContext, errorDetails: worktreeResult.error },
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
