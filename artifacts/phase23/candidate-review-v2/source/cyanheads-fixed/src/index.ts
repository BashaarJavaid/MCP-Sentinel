#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import http from "http"; // Import http module
import { config, environment, logLevel } from "./config/index.js"; // Import logLevel from config
import { initializeAndStartServer } from "./mcp-server/server.js";
// Import utils from barrel
import { logger, McpLogLevel, requestContextService } from "./utils/index.js"; // Import McpLogLevel type

/**
 * The main MCP server instance (used for stdio transport).
 * @type {McpServer | undefined}
 */
let mcpServerInstance: McpServer | undefined;

/**
 * The main HTTP server instance (used for http transport).
 * @type {http.Server | undefined}
 */
let httpServerInstance: http.Server | undefined;

/**
 * Gracefully shuts down the main MCP server.
 * Handles process termination signals (SIGTERM, SIGINT) and critical errors.
 *
 * @param signal - The signal or event name that triggered the shutdown (e.g., "SIGTERM", "uncaughtException").
 */
const shutdown = async (signal: string) => {
  const transportType = (
    process.env.MCP_TRANSPORT_TYPE || "stdio"
  ).toLowerCase();
  const shutdownContext = {
    operation: "Shutdown",
    signal,
    transport: transportType,
  };

  logger.info(
    `Received ${signal}. Starting graceful shutdown...`,
    shutdownContext,
  );

  try {
    let closePromise: Promise<void> = Promise.resolve();

    if (transportType === "stdio") {
      // Close the main MCP server instance for stdio
      if (mcpServerInstance) {
        logger.info("Closing main MCP server (stdio)...", shutdownContext);
        closePromise = mcpServerInstance.close();
      } else {
        logger.warning(
          "Stdio MCP server instance not found during shutdown.",
          shutdownContext,
        );
      }
    } else if (transportType === "http") {
      // Close the main HTTP server listener for http
      if (httpServerInstance) {
        logger.info("Closing main HTTP server listener...", shutdownContext);
        closePromise = new Promise((resolve, reject) => {
          httpServerInstance!.close((err) => {
            if (err) {
              logger.error("Error closing HTTP server listener", {
                ...shutdownContext,
                error: err.message,
              });
              reject(err);
            } else {
              logger.info(
                "Main HTTP server listener closed successfully",
                shutdownContext,
              );
              resolve();
            }
          });
        });
      } else {
        logger.warning(
          "HTTP server instance not found during shutdown.",
          shutdownContext,
        );
      }
      // Note: Individual session transports (StreamableHTTPServerTransport) are closed
      // when the client disconnects or sends a DELETE request, managed in httpTransport.ts.
    }

    // Wait for the appropriate server/listener to close
    await closePromise;

    logger.info("Graceful shutdown completed successfully", shutdownContext);
    process.exit(0);
  } catch (error) {
    // Handle any errors during shutdown
    logger.error("Critical error during shutdown", {
      ...shutdownContext,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    process.exit(1); // Exit with error code if shutdown fails
  }
};

/**
 * Initializes and starts the main MCP server.
 * Sets up request context, initializes the server instance, starts the transport,
 * and registers signal handlers for graceful shutdown and error handling.
 */
const start = async () => {
  // --- Initialize Logger FIRST ---
  // Define valid MCP log levels based on the logger's type definition
  const validMcpLogLevels: McpLogLevel[] = [
    "debug",
    "info",
    "notice",
    "warning",
    "error",
    "crit",
    "alert",
    "emerg",
  ];
  let validatedMcpLogLevel: McpLogLevel = "info"; // Default to 'info'
  if (validMcpLogLevels.includes(logLevel as McpLogLevel)) {
    validatedMcpLogLevel = logLevel as McpLogLevel;
  } else {
    // Use console.warn as logger isn't ready yet
    console.warn(
      `Invalid MCP_LOG_LEVEL "${logLevel}" found in config. Defaulting to "info".`,
    );
  }
  // Initialize the logger singleton instance with the validated level.
  logger.initialize(validatedMcpLogLevel);
  // Now it's safe to use the logger.

  // --- Start Application ---
  const transportType = (
    process.env.MCP_TRANSPORT_TYPE || "stdio"
  ).toLowerCase();
  const startupContext = requestContextService.createRequestContext({
    operation: `ServerStartup_${transportType}`, // Include transport in operation name
    appName: config.mcpServerName,
    appVersion: config.mcpServerVersion,
    environment: environment,
  });

  logger.info(
    `Starting ${config.mcpServerName} v${config.mcpServerVersion} (Transport: ${transportType})...`,
    startupContext,
  );

  try {
    // Initialize the server instance and start the selected transport
    logger.debug(
      "Initializing and starting MCP server transport",
      startupContext,
    );

    // Start the server transport. This returns the McpServer instance for stdio
    // or the http.Server instance for http.
    const serverOrHttpInstance = await initializeAndStartServer();

    if (
      transportType === "stdio" &&
      serverOrHttpInstance instanceof McpServer
    ) {
      mcpServerInstance = serverOrHttpInstance; // Store McpServer for stdio shutdown
      logger.debug(
        "Stored McpServer instance for stdio transport.",
        startupContext,
      );
    } else if (
      transportType === "http" &&
      serverOrHttpInstance instanceof http.Server
    ) {
      httpServerInstance = serverOrHttpInstance; // Store http.Server for http shutdown
      logger.debug(
        "Stored http.Server instance for http transport.",
        startupContext,
      );
    } else {
      // This case should ideally not happen if initializeAndStartServer works correctly
      logger.warning(
        "initializeAndStartServer did not return the expected instance type.",
        {
          ...startupContext,
          instanceType: typeof serverOrHttpInstance,
        },
      );
    }

    // If initializeAndStartServer failed internally, it would have thrown an error,
    // and execution would jump to the outer catch block.

    logger.info(
      `${config.mcpServerName} is running with ${transportType} transport`,
      {
        ...startupContext,
        startTime: new Date().toISOString(),
      },
    );

    // --- Signal and Error Handling Setup ---

    // Handle process signals for graceful shutdown
    process.on("SIGTERM", () => shutdown("SIGTERM"));
    process.on("SIGINT", () => shutdown("SIGINT"));

    // Handle uncaught exceptions
    process.on("uncaughtException", async (error) => {
      const errorContext = {
        ...startupContext, // Include base context for correlation
        event: "uncaughtException",
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      };
      logger.error(
        "Uncaught exception detected. Initiating shutdown...",
        errorContext,
      );
      // Attempt graceful shutdown; shutdown() handles its own errors.
      await shutdown("uncaughtException");
      // If shutdown fails internally, it will call process.exit(1).
      // If shutdown succeeds, it calls process.exit(0).
      // If shutdown itself throws unexpectedly *before* exiting, this process might terminate abruptly,
      // but the core shutdown logic is handled within shutdown().
    });

    // Handle unhandled promise rejections
    process.on("unhandledRejection", async (reason: unknown) => {
      const rejectionContext = {
        ...startupContext, // Include base context for correlation
        event: "unhandledRejection",
        reason: reason instanceof Error ? reason.message : String(reason),
        stack: reason instanceof Error ? reason.stack : undefined,
      };
      logger.error(
        "Unhandled promise rejection detected. Initiating shutdown...",
        rejectionContext,
      );
      // Attempt graceful shutdown; shutdown() handles its own errors.
      await shutdown("unhandledRejection");
      // Similar logic as uncaughtException: shutdown handles its exit codes.
    });
  } catch (error) {
    // Handle critical startup errors (already logged by ErrorHandler or caught above)
    // Log the final failure context, including error details, before exiting
    logger.error("Critical error during startup, exiting.", {
      ...startupContext,
      finalErrorContext: "Startup Failure",
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    process.exit(1);
  }
};

// Start the application
start();
