import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  CallToolResult,
  TextContent,
} from "@modelcontextprotocol/sdk/types.js";
import path from "path";
import { z } from "zod";
import { BaseErrorCode, McpError } from "../../../types-global/errors.js";
import {
  ErrorHandler,
  logger,
  requestContextService,
  sanitization,
} from "../../../utils/index.js";
import {
  GitInitInput,
  GitInitInputSchema,
  gitInitLogic,
  GitInitResult,
} from "./logic.js";

const TOOL_NAME = "git_init";
const TOOL_DESCRIPTION =
  "Initializes a new Git repository at the specified path. If path is relative or omitted, it resolves against the session working directory (if you have set the git_working_dir). Can optionally set the initial branch name and create a bare repository.";

const RegistrationSchema = GitInitInputSchema.extend({
  path: z.string().min(1).optional().default("."),
}).shape;

// --- Module-level State Accessors ---
// These will be populated by the initialize function called from server.ts
let _getWorkingDirectory: (
  sessionId: string | undefined,
) => string | undefined = () => undefined;
let _getSessionIdFromContext: (
  context: Record<string, any>,
) => string | undefined = () => undefined;

/**
 * Initializes state accessor functions for the git_init tool.
 * This function is called by the main server setup to provide the tool
 * with a way to access session-specific state (like the working directory)
 * without needing direct access to the server or transport layer internals.
 *
 * @param getWorkingDirectory - Function to retrieve the working directory for a given session ID.
 * @param getSessionIdFromContext - Function to extract the session ID from a tool's execution context.
 */
export function initializeGitInitStateAccessors(
  getWorkingDirectory: (sessionId: string | undefined) => string | undefined,
  getSessionIdFromContext: (context: Record<string, any>) => string | undefined,
): void {
  _getWorkingDirectory = getWorkingDirectory;
  _getSessionIdFromContext = getSessionIdFromContext;
  logger.debug(`State accessors initialized for ${TOOL_NAME}`);
}

/**
 * Registers the git_init tool with the MCP server.
 *
 * @param {McpServer} server - The McpServer instance to register the tool with.
 * @returns {Promise<void>}
 * @throws {Error} If registration fails.
 */
export const registerGitInitTool = async (server: McpServer): Promise<void> => {
  const operation = "registerGitInitTool";
  const context = requestContextService.createRequestContext({ operation });

  await ErrorHandler.tryCatch(
    async () => {
      server.tool<typeof RegistrationSchema>(
        TOOL_NAME,
        TOOL_DESCRIPTION,
        RegistrationSchema,
        async (validatedArgs, callContext): Promise<CallToolResult> => {
          // Removed explicit type for callContext
          const toolOperation = "tool:git_init";
          const requestContext = requestContextService.createRequestContext({
            operation: toolOperation,
            parentContext: callContext,
          });

          // Use the initialized accessor to get the session ID
          const sessionId = _getSessionIdFromContext(requestContext); // Pass the created context
          if (!sessionId && !path.isAbsolute(validatedArgs.path)) {
            // If path is relative, we NEED a session ID to resolve against a potential working dir
            logger.error(
              "Session ID is missing in context, cannot resolve relative path",
              requestContext,
            );
            throw new McpError(
              BaseErrorCode.INTERNAL_ERROR,
              "Session context is unavailable for relative path resolution.",
              { context: requestContext, operation: toolOperation },
            );
          }

          logger.info(`Executing tool: ${TOOL_NAME}`, requestContext);

          return await ErrorHandler.tryCatch<CallToolResult>(
            async () => {
              // Use the initialized accessor to get the working directory
              const sessionWorkingDirectory = _getWorkingDirectory(sessionId);

              const inputPath = validatedArgs.path;
              let resolvedPath: string;

              try {
                if (path.isAbsolute(inputPath)) {
                  resolvedPath = sanitization.sanitizePath(inputPath, {
                    allowAbsolute: true,
                  }).sanitizedPath;
                  logger.debug(
                    `Using absolute path: ${resolvedPath}`,
                    requestContext,
                  );
                } else if (sessionWorkingDirectory) {
                  resolvedPath = sanitization.sanitizePath(
                    path.resolve(sessionWorkingDirectory, inputPath),
                    { allowAbsolute: true },
                  ).sanitizedPath;
                  logger.debug(
                    `Resolved relative path '${inputPath}' to absolute path: ${resolvedPath} using session CWD`,
                    requestContext,
                  );
                } else {
                  // This case should now only be hit if the path is relative AND there's no session CWD set.
                  logger.error(
                    `Relative path '${inputPath}' provided but no session working directory is set.`,
                    requestContext,
                  );
                  throw new McpError(
                    BaseErrorCode.VALIDATION_ERROR,
                    `Relative path '${inputPath}' provided but no session working directory is set. Please provide an absolute path or set a working directory using git_set_working_dir.`,
                    { context: requestContext, operation: toolOperation },
                  );
                }
              } catch (error) {
                logger.error("Path resolution or sanitization failed", {
                  ...requestContext,
                  operation: toolOperation,
                  error,
                });
                if (error instanceof McpError) throw error;
                throw new McpError(
                  BaseErrorCode.VALIDATION_ERROR,
                  `Invalid path processing: ${error instanceof Error ? error.message : String(error)}`,
                  {
                    context: requestContext,
                    operation: toolOperation,
                    originalError: error,
                  },
                );
              }

              const logicArgs: GitInitInput = {
                ...validatedArgs,
                path: resolvedPath,
              };

              const initResult: GitInitResult = await gitInitLogic(
                logicArgs,
                requestContext,
              );

              const resultContent: TextContent = {
                type: "text",
                text: JSON.stringify(initResult, null, 2), // Pretty-print JSON
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
