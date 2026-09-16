import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
// Import utils from barrel (ErrorHandler from ../utils/internal/errorHandler.js)
import { ErrorHandler } from "../../../utils/index.js";
// Import utils from barrel (logger from ../utils/internal/logger.js)
import { logger } from "../../../utils/index.js";
// Import utils from barrel (requestContextService from ../utils/internal/requestContext.js)
import { requestContextService } from "../../../utils/index.js";
import {
  GitCloneInputSchema,
  gitCloneLogic,
  GitCloneInput,
  GitCloneResult,
} from "./logic.js";
import { BaseErrorCode } from "../../../types-global/errors.js"; // Keep direct import for types-global

const TOOL_NAME = "git_clone";
const TOOL_DESCRIPTION =
  "Clones a Git repository from a given URL into a specified absolute directory path. Supports cloning specific branches and setting clone depth.";

/**
 * Registers the git_clone tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails.
 */
export const registerGitCloneTool = async (
  server: McpServer,
): Promise<void> => {
  const operation = "registerGitCloneTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitCloneInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitCloneInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_clone";
          const requestContext = requestContextService.createRequestContext({
            operation: toolOperation,
            parentContext: callContext,
          });

          logger.info(`Executing tool: ${TOOL_NAME}`, requestContext);

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              // Call the core logic function
              const cloneResult: GitCloneResult = await gitCloneLogic(
                validatedArgs as GitCloneInput,
                requestContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(cloneResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              logger.info(
                `Tool ${TOOL_NAME} executed successfully, returning JSON`,
                requestContext,
              );
              return { content: [resultContent] };
            },
            {
              operation: toolOperation,
              context: requestContext,
              input: validatedArgs, // Log sanitized input
              errorCode: BaseErrorCode.INTERNAL_ERROR, // Default if unexpected error occurs
            },
          );
        },
      );

      logger.info(`Tool registered: ${TOOL_NAME}`, context);
    },
    { operation, context, critical: true },
  ); // Mark registration as critical
};
