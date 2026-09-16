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
// Import the schema and types
import { BaseErrorCode } from "../../../types-global/errors.js"; // Keep direct import for types-global
import {
  GitCleanInput,
  GitCleanInputSchema,
  gitCleanLogic,
  GitCleanResult,
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
 * Initializes the state accessors needed by the git_clean tool registration.
 * @param getWdFn - Function to get the working directory for a session.
 * @param getSidFn - Function to get the session ID from context.
 */
export function initializeGitCleanStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_clean tool registration.");
}

const TOOL_NAME = "git_clean";
const TOOL_DESCRIPTION =
  "Removes untracked files from the working directory. Supports dry runs, removing directories, and removing ignored files. CRITICAL: Requires explicit `force: true` parameter for safety as this is a destructive operation. Returns results as a JSON object.";

/**
 * Registers the git_clean tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitCleanTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_clean must be initialized before registration.",
    );
  }

  const operation = "registerGitCleanTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      // Register the tool using the schema's shape (no refinements here)
      server.tool<typeof GitCleanInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitCleanInputSchema.shape, // Use the shape directly
        // Let TypeScript infer handler argument types.
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          // Cast validatedArgs to the specific input type for use within the handler
          const toolInput = validatedArgs as GitCleanInput;
          const toolOperation = `tool:${TOOL_NAME}`;
          const requestContext = requestContextService.createRequestContext({
            operation: toolOperation,
            parentContext: callContext,
          });

          // --- SAFETY CHECK (Redundant but good practice) ---
          // The core logic already checks this, but adding a check here ensures
          // the intent is clear even before calling the logic.
          if (!toolInput.force) {
            logger.error(
              `Tool ${TOOL_NAME} called without force=true. Aborting.`,
              requestContext,
            );
            // Return a structured error via CallToolResult
            const errorContent: TextContent = {
              type: "text",
              text: JSON.stringify(
                {
                  success: false,
                  message:
                    "Operation aborted: 'force' parameter must be explicitly set to true to execute 'git clean'.",
                  dryRun: toolInput.dryRun, // Include dryRun status
                },
                null,
                2,
              ),
              contentType: "application/json",
            };
            return { content: [errorContent], isError: true }; // Indicate it's an error result
          }

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
              // Call the core logic function which returns a GitCleanResult object
              const cleanResult: GitCleanResult = await gitCleanLogic(
                toolInput,
                logicContext,
              );

              // Format the result as JSON within TextContent
              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(cleanResult, null, 2),
                contentType: "application/json",
              };

              // Log based on the success flag in the result
              if (cleanResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully (DryRun: ${cleanResult.dryRun})`,
                  logicContext,
                );
              } else {
                // Log specific failure message from the result
                logger.warning(
                  `Tool ${TOOL_NAME} failed: ${cleanResult.message}`,
                  { ...logicContext, errorDetails: cleanResult.error },
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
