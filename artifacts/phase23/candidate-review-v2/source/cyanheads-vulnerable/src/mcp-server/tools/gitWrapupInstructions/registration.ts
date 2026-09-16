import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"; // Removed McpRequestContext import
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
import { BaseErrorCode } from "../../../types-global/errors.js";
import {
  ErrorHandler,
  logger,
  RequestContext,
  requestContextService,
} from "../../../utils/index.js";
import {
  getWrapupInstructions,
  GitWrapupInstructionsInput,
  GitWrapupInstructionsInputSchema,
  GitWrapupInstructionsResult,
} from "./logic.js";

// --- State Accessors ---
/** Type definition for the function that gets the working directory for a session */
export type GetWorkingDirectoryFn = (
  sessionId: string | undefined,
) => string | undefined;
/** Type definition for the function that gets the session ID from the context */
// Changed context type to Record<string, any> to align with _getSessionId's expected input type (getSessionIdFromContext in server.ts)
export type GetSessionIdFn = (
  context: Record<string, any>,
) => string | undefined;

let _getWorkingDirectory: GetWorkingDirectoryFn | undefined;
let _getSessionId: GetSessionIdFn | undefined;

/**
 * Initializes the state accessors needed by the git_wrapup_instructions tool.
 * This should be called once during server setup by server.ts.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitWrapupInstructionsStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info(
    "State accessors initialized for git_wrapup_instructions tool registration.",
  );
}

const TOOL_NAME = "git_wrapup_instructions";
const TOOL_DESCRIPTION =
  "Provides a standard Git wrap-up workflow. This involves reviewing changes with `git_diff`, updating documentation (README, CHANGELOG), and making logical, descriptive commits using the `git_commit` tool. The tool's response also includes the current `git status` output. You should set the working directory using `git_set_working_dir` before running this tool.";

/**
 * Registers the git_wrapup_instructions tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitWrapupInstructionsTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_wrapup_instructions must be initialized before registration.",
    );
  }

  const operation = "registerGitWrapupInstructionsTool";
  // Context for the registration operation itself
  const registrationOpContext = requestContextService.createRequestContext({
    operation,
  });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitWrapupInstructionsInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitWrapupInstructionsInputSchema.shape,
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_wrapup_instructions";

          // Create a base RequestContext for this specific tool call,
          // potentially linking to the callContext provided by the McpServer.
          // Pass callContext directly; createRequestContext will handle it appropriately
          // (e.g., by trying to extract a requestId or sessionId if relevant for linking).
          const baseRequestContext = requestContextService.createRequestContext(
            { operation: toolOperation, parentContext: callContext },
          );

          // Retrieve the session ID using the initialized accessor.
          // _getSessionId (which is getSessionIdFromContext from server.ts) expects Record<string, any>.
          // callContext from server.tool() is compatible with Record<string, any>.
          const sessionId = _getSessionId!(callContext);

          // Create the session-specific getWorkingDirectory function.
          const getWorkingDirectoryForSession = () => {
            // _getWorkingDirectory is guaranteed to be defined by the check at the start of register function.
            return _getWorkingDirectory!(sessionId);
          };

          // Construct the logicContext to be passed to the tool's core logic.
          // This includes the base request context properties, the session ID,
          // and the specific getWorkingDirectory function for this session.
          const logicContext: RequestContext & {
            sessionId?: string;
            getWorkingDirectory: () => string | undefined;
          } = {
            ...baseRequestContext,
            sessionId: sessionId,
            getWorkingDirectory: getWorkingDirectoryForSession,
          };

          logger.info(`Executing tool: ${TOOL_NAME}`, logicContext);

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              // Call the core logic function with validated arguments and the prepared logicContext.
              const result: GitWrapupInstructionsResult =
                await getWrapupInstructions(
                  validatedArgs as GitWrapupInstructionsInput,
                  logicContext,
                );

              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(result, null, 2),
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
              context: logicContext, // Use the enhanced logicContext for error reporting
              input: validatedArgs,
              errorCode: BaseErrorCode.INTERNAL_ERROR,
            },
          );
        },
      );
      logger.info(`Tool registered: ${TOOL_NAME}`, registrationOpContext); // Use context for registration operation
    },
    { operation, context: registrationOpContext, critical: true },
  ); // Use context for registration operation
};
