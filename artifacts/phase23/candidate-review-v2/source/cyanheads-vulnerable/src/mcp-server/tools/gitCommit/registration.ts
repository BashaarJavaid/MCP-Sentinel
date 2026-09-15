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
// Import the result type along with the function and input schema
import { BaseErrorCode } from "../../../types-global/errors.js"; // Keep direct import for types-global
import {
  commitGitChanges,
  GitCommitInput,
  GitCommitInputSchema,
  GitCommitResult,
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
export function initializeGitCommitStateAccessors(
  getWdFn: GetWorkingDirectoryFn,
  getSidFn: GetSessionIdFn,
): void {
  _getWorkingDirectory = getWdFn;
  _getSessionId = getSidFn;
  logger.info("State accessors initialized for git_commit tool registration.");
}

const TOOL_NAME = "git_commit";
const TOOL_DESCRIPTION = `Commits staged changes to the Git repository index with a descriptive message. Supports author override, amending, and empty commits. Returns a JSON result.

**Commit Message Guidance:**
Write clear, concise commit messages using the Conventional Commits format: \`type(scope): subject\`.
- \`type\`: feat, fix, docs, style, refactor, test, chore, etc.
- \`(scope)\`: Optional context (e.g., \`auth\`, \`ui\`, filename).
- \`subject\`: Imperative, present tense description (e.g., "add login button", not "added login button").

I want to understand what you did and why. Use the body for detailed explanations, if necessary.

**Example Commit Message:**
\`\`\`
feat(auth): implement password reset endpoint

- Adds the /api/auth/reset-password endpoint to allow users to reset their password via an email link. 
- Includes input validation and rate limiting.

Closes #123 (if applicable).
\`\`\`

**Tool Options & Behavior:**
- Commit related changes logically. Use the optional \`filesToStage\` parameter to auto-stage specific files before committing.
- The \`path\` defaults to the session's working directory unless overridden. If \`GIT_SIGN_COMMITS=true\` is set, commits are signed (\`-S\`), with an optional \`forceUnsignedOnFailure\` fallback.`;

/**
 * Registers the git_commit tool with the MCP server.
 * Uses the high-level server.tool() method for registration, schema validation, and routing.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails or state accessors are not initialized.
 */
export const registerGitCommitTool = async (
  server: McpServer,
): Promise<void> => {
  if (!_getWorkingDirectory || !_getSessionId) {
    throw new Error(
      "State accessors for git_commit must be initialized before registration.",
    );
  }

  const operation = "registerGitCommitTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof GitCommitInputSchema.shape>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        GitCommitInputSchema.shape, // Provide the Zod schema shape
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          const toolOperation = "tool:git_commit";
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
              // Call the core logic function which now returns a GitCommitResult object
              const commitResult: GitCommitResult = await commitGitChanges(
                validatedArgs as GitCommitInput,
                logicContext,
              );

              // Format the result as a JSON string within TextContent
              const resultContent: TextContent = {
                type: "text",
                // Stringify the JSON object for the response content
                text: JSON.stringify(commitResult, null, 2), // Pretty-print JSON
                contentType: "application/json",
              };

              // Log based on the success flag in the result
              if (commitResult.success) {
                logger.info(
                  `Tool ${TOOL_NAME} executed successfully, returning JSON`,
                  logicContext,
                );
              } else {
                logger.info(
                  `Tool ${TOOL_NAME} completed with non-fatal condition (e.g., nothing to commit), returning JSON`,
                  logicContext,
                );
              }
              // Even if success is false (e.g., nothing to commit), it's not a tool execution error
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
