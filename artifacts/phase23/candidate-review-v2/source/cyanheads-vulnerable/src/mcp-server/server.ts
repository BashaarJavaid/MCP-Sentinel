/**
 * Main entry point for the MCP (Model Context Protocol) server.
 * This file orchestrates the server's lifecycle:
 * 1. Initializes the core McpServer instance with its identity and capabilities.
 * 2. Registers available resources and tools, making them discoverable and usable by clients.
 * 3. Selects and starts the appropriate communication transport (stdio or Streamable HTTP)
 *    based on configuration.
 * 4. Handles top-level error management during startup.
 *
 * MCP Specification References:
 * - Lifecycle: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/basic/lifecycle.mdx
 * - Overview (Capabilities): https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/basic/index.mdx
 * - Transports: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/basic/transports.mdx
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
// Import validated configuration and environment details.
import { config, environment } from "../config/index.js";
// Import core utilities: ErrorHandler, logger, requestContextService.
import {
  ErrorHandler,
  logger,
  RequestContext,
  requestContextService,
} from "../utils/index.js"; // Added RequestContext

// Import registration AND state initialization functions for ALL Git tools (alphabetized)
import {
  initializeGitAddStateAccessors,
  registerGitAddTool,
} from "./tools/gitAdd/index.js";
import {
  initializeGitBranchStateAccessors,
  registerGitBranchTool,
} from "./tools/gitBranch/index.js";
import {
  initializeGitCheckoutStateAccessors,
  registerGitCheckoutTool,
} from "./tools/gitCheckout/index.js";
import {
  initializeGitCherryPickStateAccessors,
  registerGitCherryPickTool,
} from "./tools/gitCherryPick/index.js";
import {
  initializeGitCleanStateAccessors,
  registerGitCleanTool,
} from "./tools/gitClean/index.js";
import {
  initializeGitClearWorkingDirStateAccessors,
  registerGitClearWorkingDirTool,
} from "./tools/gitClearWorkingDir/index.js";
import { registerGitCloneTool } from "./tools/gitClone/index.js"; // No initializer needed/available
import {
  initializeGitCommitStateAccessors,
  registerGitCommitTool,
} from "./tools/gitCommit/index.js";
import {
  initializeGitDiffStateAccessors,
  registerGitDiffTool,
} from "./tools/gitDiff/index.js";
import {
  initializeGitFetchStateAccessors,
  registerGitFetchTool,
} from "./tools/gitFetch/index.js";
import {
  initializeGitInitStateAccessors,
  registerGitInitTool,
} from "./tools/gitInit/index.js";
import {
  initializeGitLogStateAccessors,
  registerGitLogTool,
} from "./tools/gitLog/index.js";
import {
  initializeGitMergeStateAccessors,
  registerGitMergeTool,
} from "./tools/gitMerge/index.js";
import {
  initializeGitPullStateAccessors,
  registerGitPullTool,
} from "./tools/gitPull/index.js";
import {
  initializeGitPushStateAccessors,
  registerGitPushTool,
} from "./tools/gitPush/index.js";
import {
  initializeGitRebaseStateAccessors,
  registerGitRebaseTool,
} from "./tools/gitRebase/index.js";
import {
  initializeGitRemoteStateAccessors,
  registerGitRemoteTool,
} from "./tools/gitRemote/index.js";
import {
  initializeGitResetStateAccessors,
  registerGitResetTool,
} from "./tools/gitReset/index.js";
import {
  initializeGitSetWorkingDirStateAccessors,
  registerGitSetWorkingDirTool,
} from "./tools/gitSetWorkingDir/index.js";
import {
  initializeGitShowStateAccessors,
  registerGitShowTool,
} from "./tools/gitShow/index.js";
import {
  initializeGitStashStateAccessors,
  registerGitStashTool,
} from "./tools/gitStash/index.js";
import {
  initializeGitStatusStateAccessors,
  registerGitStatusTool,
} from "./tools/gitStatus/index.js";
import {
  initializeGitTagStateAccessors,
  registerGitTagTool,
} from "./tools/gitTag/index.js";
import {
  initializeGitWorktreeStateAccessors,
  registerGitWorktreeTool,
} from "./tools/gitWorktree/index.js";
import {
  initializeGitWrapupInstructionsStateAccessors,
  registerGitWrapupInstructionsTool,
} from "./tools/gitWrapupInstructions/index.js";

// Import transport setup functions
import { startHttpTransport } from "./transports/httpTransport.js";
import { connectStdioTransport } from "./transports/stdioTransport.js";

/**
 * Creates and configures a new instance of the McpServer.
 *
 * This function is central to defining the server's identity and functionality
 * as presented to connecting clients during the MCP initialization phase.
 *
 * MCP Spec Relevance:
 * - Server Identity (`serverInfo`): The `name` and `version` provided here are part
 *   of the `ServerInformation` object returned in the `InitializeResult` message,
 *   allowing clients to identify the server they are connected to.
 * - Capabilities Declaration: The `capabilities` object declares the features this
 *   server supports, enabling clients to tailor their interactions.
 *   - `logging: {}`: Indicates the server can receive `logging/setLevel` requests
 *     and may send `notifications/message` log messages (handled by the logger utility).
 *   - `resources: { listChanged: true }`: Signals that the server supports dynamic
 *     resource lists and will send `notifications/resources/list_changed` if the
 *     available resources change after initialization. (Currently no resources registered)
 *   - `tools: { listChanged: true }`: Signals support for dynamic tool lists and
 *     `notifications/tools/list_changed`.
 * - Resource/Tool Registration: This function calls specific registration functions
 *   (e.g., `registerGitAdd`) which use SDK methods (`server.resource`, `server.tool`)
 *   to make capabilities available for discovery (`resources/list`, `tools/list`) and
 *   invocation (`resources/read`, `tools/call`).
 *
 * Design Note: This factory function is used to create server instances. For the 'stdio'
 * transport, it's called once. For the 'http' transport, it's passed to `startHttpTransport`
 * and called *per session* to ensure session isolation.
 *
 * @returns {Promise<McpServer>} A promise resolving with the configured McpServer instance.
 * @throws {Error} If any resource or tool registration fails.
 */
// Removed sessionId parameter, it will be retrieved from context within tool handlers
async function createMcpServerInstance(): Promise<McpServer> {
  const context = requestContextService.createRequestContext({
    operation: "createMcpServerInstance",
  });
  logger.info("Initializing MCP server instance", context);

  // Configure the request context service (used for correlating logs/errors).
  requestContextService.configure({
    appName: config.mcpServerName,
    appVersion: config.mcpServerVersion,
    environment,
  });

  // Instantiate the core McpServer using the SDK.
  // Provide server identity (name, version) and declare supported capabilities.
  // Note: Resources capability declared, but none are registered currently.
  logger.debug("Instantiating McpServer with capabilities", {
    ...context,
    serverInfo: {
      name: config.mcpServerName,
      version: config.mcpServerVersion,
    },
    capabilities: {
      logging: {},
      resources: { listChanged: true },
      tools: { listChanged: true },
    },
  });
  const server = new McpServer(
    { name: config.mcpServerName, version: config.mcpServerVersion }, // ServerInformation part of InitializeResult
    {
      capabilities: {
        logging: {},
        resources: { listChanged: true },
        tools: { listChanged: true },
      },
    }, // Declared capabilities
  );

  // Each server instance is isolated per session. This variable will hold the
  // working directory for the duration of this session.
  let sessionWorkingDirectory: string | undefined = undefined;

  // --- Define Unified State Accessor Functions ---
  // These functions abstract away the transport type to get/set session state.

  /** Gets the session ID from the tool's execution context. */
  const getSessionIdFromContext = (
    toolContext: Record<string, any>,
  ): string | undefined => {
    // The RequestContext created by the tool registration wrapper should contain the sessionId.
    return (toolContext as RequestContext)?.sessionId;
  };

  /** Gets the working directory for the current session. */
  const getWorkingDirectory = (
    sessionId: string | undefined,
  ): string | undefined => {
    // The working directory is now stored in a variable scoped to this server instance.
    // The sessionId is kept for potential logging or more complex future state management.
    return sessionWorkingDirectory;
  };

  /** Sets the working directory for the current session. */
  const setWorkingDirectory = (
    sessionId: string | undefined,
    dir: string,
  ): void => {
    // The working directory is now stored in a variable scoped to this server instance.
    logger.debug("Setting session working directory", {
      ...context,
      sessionId,
      newDirectory: dir,
    });
    sessionWorkingDirectory = dir;
  };

  // --- Initialize Tool State Accessors BEFORE Registration ---
  // Pass the defined unified accessor functions to the initializers.
  logger.debug("Initializing state accessors for tools...", context);
  try {
    // Call initializers for all tools that likely need state access (alphabetized).
    // If an initializer doesn't exist, the import would have failed earlier (or build will fail).
    initializeGitAddStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitBranchStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitCheckoutStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitCherryPickStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitCleanStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitClearWorkingDirStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    // initializeGitCloneStateAccessors - No initializer needed/available
    initializeGitCommitStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitDiffStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitFetchStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitInitStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitLogStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitMergeStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitPullStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitPushStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitRebaseStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitRemoteStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitResetStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitSetWorkingDirStateAccessors(
      getWorkingDirectory,
      setWorkingDirectory,
      getSessionIdFromContext,
    ); // Special case
    initializeGitShowStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitStashStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitStatusStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitTagStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitWorktreeStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    );
    initializeGitWrapupInstructionsStateAccessors(
      getWorkingDirectory,
      getSessionIdFromContext,
    ); // Added this line
    logger.debug("State accessors initialized successfully.", context);
  } catch (initError) {
    // Catch errors specifically during initialization phase
    logger.error("Failed during state accessor initialization", {
      ...context,
      error: initError instanceof Error ? initError.message : String(initError),
      stack: initError instanceof Error ? initError.stack : undefined,
    });
    throw initError; // Re-throw to prevent server starting incorrectly
  }

  try {
    // Register all defined Git tools (alphabetized). These calls populate the server's
    // internal registry, making them available via MCP methods like 'tools/list'.
    logger.debug("Registering Git tools...", context);
    await registerGitAddTool(server);
    await registerGitBranchTool(server);
    await registerGitCheckoutTool(server);
    await registerGitCherryPickTool(server);
    await registerGitCleanTool(server);
    await registerGitClearWorkingDirTool(server);
    await registerGitCloneTool(server);
    await registerGitCommitTool(server);
    await registerGitDiffTool(server);
    await registerGitFetchTool(server);
    await registerGitInitTool(server);
    await registerGitLogTool(server);
    await registerGitMergeTool(server);
    await registerGitPullTool(server);
    await registerGitPushTool(server);
    await registerGitRebaseTool(server);
    await registerGitRemoteTool(server);
    await registerGitResetTool(server);
    await registerGitSetWorkingDirTool(server);
    await registerGitShowTool(server);
    await registerGitStashTool(server);
    await registerGitStatusTool(server);
    await registerGitTagTool(server);
    await registerGitWorktreeTool(server);
    await registerGitWrapupInstructionsTool(server);
    // Add calls to register other resources/tools here if needed in the future.
    logger.info("Git tools registered successfully", context);
  } catch (err) {
    // Registration is critical; log and re-throw errors.
    logger.error("Failed to register resources/tools", {
      ...context,
      error: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined, // Include stack for debugging
    });
    throw err; // Propagate error to prevent server starting with incomplete capabilities.
  }

  return server;
}

/**
 * Selects, sets up, and starts the appropriate MCP transport layer based on configuration.
 * This function acts as the bridge between the core server logic and the communication channel.
 *
 * MCP Spec Relevance:
 * - Transport Selection: Reads `config.mcpTransportType` ('stdio' or 'http') to determine
 *   which transport mechanism defined in the MCP specification to use.
 * - Transport Connection: Calls dedicated functions (`connectStdioTransport` or `startHttpTransport`)
 *   which handle the specifics of establishing communication according to the chosen
 *   transport's rules (e.g., stdin/stdout handling for 'stdio', HTTP server setup and
 *   endpoint handling for 'http').
 * - Server Instance Lifecycle:
 *   - For 'stdio', creates a single `McpServer` instance for the lifetime of the process.
 *   - For 'http', passes the `createMcpServerInstance` factory function to `startHttpTransport`,
 *     allowing the HTTP transport to create a new, isolated server instance for each client session,
 *     aligning with the stateful session management described in the Streamable HTTP spec.
 *
 * @returns {Promise<McpServer | void>} Resolves with the McpServer instance for 'stdio', or void for 'http'.
 * @throws {Error} If the configured transport type is unsupported or if transport setup fails.
 */
async function startTransport(): Promise<McpServer | void> {
  // Determine the transport type from the validated configuration.
  const transportType = config.mcpTransportType;
  const context = requestContextService.createRequestContext({
    operation: "startTransport",
    transport: transportType,
  });
  logger.info(`Starting transport: ${transportType}`, context);

  // --- HTTP Transport Setup ---
  if (transportType === "http") {
    logger.debug("Delegating to startHttpTransport...", context);
    // For HTTP, the transport layer manages its own lifecycle and potentially multiple sessions.
    // We pass the factory function to allow the HTTP transport to create server instances as needed (per session).
    await startHttpTransport(createMcpServerInstance, context);
    // The HTTP server runs indefinitely, listening for connections, so this function returns void.
    return;
  }

  // --- Stdio Transport Setup ---
  if (transportType === "stdio") {
    logger.debug(
      "Creating single McpServer instance for stdio transport...",
      context,
    );
    // For stdio, there's typically one persistent connection managed by a parent process.
    // Create a single McpServer instance for the entire process lifetime.
    const server = await createMcpServerInstance();
    logger.debug("Delegating to connectStdioTransport...", context);
    // Connect the server instance to the stdio transport handler.
    await connectStdioTransport(server, context);
    // Return the server instance; the caller (main entry point) might hold onto it.
    return server;
  }

  // --- Unsupported Transport ---
  // This case should theoretically not be reached due to config validation, but acts as a safeguard.
  logger.fatal(
    `Unsupported transport type configured: ${transportType}`,
    context,
  );
  throw new Error(
    `Unsupported transport type: ${transportType}. Must be 'stdio' or 'http'.`,
  );
}

/**
 * Main application entry point. Initializes and starts the MCP server.
 *
 * MCP Spec Relevance:
 * - Orchestrates the server startup sequence, culminating in a server ready to accept
 *   connections and process MCP messages according to the chosen transport's rules.
 * - Implements top-level error handling for critical startup failures, ensuring the
 *   process exits appropriately if it cannot initialize correctly.
 *
 * @returns {Promise<void | McpServer>} Resolves upon successful startup (void for http, McpServer for stdio). Rejects on critical failure.
 */
export async function initializeAndStartServer(): Promise<void | McpServer> {
  const context = requestContextService.createRequestContext({
    operation: "initializeAndStartServer",
  });
  logger.info("MCP Server initialization sequence started.", context);
  try {
    // Initiate the transport setup based on configuration.
    const result = await startTransport();
    logger.info(
      "MCP Server initialization sequence completed successfully.",
      context,
    );
    return result;
  } catch (err) {
    // Catch any errors that occurred during server instance creation or transport setup.
    logger.fatal("Critical error during MCP server initialization.", {
      ...context,
      error: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
    });
    // Use the centralized error handler for consistent critical error reporting.
    ErrorHandler.handleError(err, {
      ...context,
      operation: "initializeAndStartServer_Catch",
      critical: true,
    });
    // Exit the process with a non-zero code to indicate failure.
    logger.info(
      "Exiting process due to critical initialization error.",
      context,
    );
    process.exit(1);
  }
}
