import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import winston from "winston";
import TransportStream from "winston-transport";
import { config } from "../../config/index.js";

/**
 * Supported logging levels based on RFC 5424 Syslog severity levels used by MCP.
 * emerg: 0, alert: 1, crit: 2, error: 3, warning: 4, notice: 5, info: 6, debug: 7
 */
export type McpLogLevel =
  | "debug"
  | "info"
  | "notice"
  | "warning"
  | "error"
  | "crit"
  | "alert"
  | "emerg";

// Define the numeric severity for comparison (lower is more severe)
const mcpLevelSeverity: Record<McpLogLevel, number> = {
  emerg: 0,
  alert: 1,
  crit: 2,
  error: 3,
  warning: 4,
  notice: 5,
  info: 6,
  debug: 7,
};

// Map MCP levels to Winston's core levels for file logging
const mcpToWinstonLevel: Record<
  McpLogLevel,
  "debug" | "info" | "warn" | "error"
> = {
  debug: "debug",
  info: "info",
  notice: "info", // Map notice to info for file logging
  warning: "warn",
  error: "error",
  crit: "error", // Map critical levels to error for file logging
  alert: "error",
  emerg: "error",
};

// Type for the MCP notification sender function
export type McpNotificationSender = (
  level: McpLogLevel,
  data: any,
  loggerName?: string,
) => void;

// Resolve __dirname for ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate project root robustly (works from src/ or dist/)
const isRunningFromDist = __dirname.includes(path.sep + "dist" + path.sep);
const levelsToGoUp = isRunningFromDist ? 3 : 2;
const pathSegments = Array(levelsToGoUp).fill("..");
const projectRoot = path.resolve(__dirname, ...pathSegments);

const logsDir = path.join(projectRoot, "logs");

// Security: ensure logsDir is within projectRoot
const resolvedLogsDir = path.resolve(logsDir);
const isLogsDirSafe =
  resolvedLogsDir === projectRoot ||
  resolvedLogsDir.startsWith(projectRoot + path.sep);
if (!isLogsDirSafe) {
  // Use console.error for critical pre-init errors.
  // Only log to console if TTY to avoid polluting stdout for stdio MCP clients.
  if (process.stdout.isTTY) {
    console.error(
      `FATAL: logs directory "${resolvedLogsDir}" is outside project root "${projectRoot}". File logging disabled.`,
    );
  }
}

/**
 * Helper function to create the Winston console format.
 * This is extracted to avoid duplication between initialize and setLevel.
 */
function createWinstonConsoleFormat() {
  return winston.format.combine(
    winston.format.colorize(),
    winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      let metaString = "";
      const metaCopy = { ...meta };
      if (metaCopy.error && typeof metaCopy.error === "object") {
        const errorObj = metaCopy.error as any;
        if (errorObj.message) metaString += `\n  Error: ${errorObj.message}`;
        if (errorObj.stack)
          metaString += `\n  Stack: ${String(errorObj.stack)
            .split("\n")
            .map((l: string) => `    ${l}`)
            .join("\n")}`;
        delete metaCopy.error;
      }
      if (Object.keys(metaCopy).length > 0) {
        try {
          const remainingMetaJson = JSON.stringify(metaCopy, null, 2);
          if (remainingMetaJson !== "{}")
            metaString += `\n  Meta: ${remainingMetaJson}`;
        } catch (stringifyError) {
          metaString += `\n  Meta: [Error stringifying metadata: ${(stringifyError as Error).message}]`;
        }
      }
      return `${timestamp} ${level}: ${message}${metaString}`;
    }),
  );
}

/**
 * Singleton Logger wrapping Winston, adapted for MCP.
 * Logs to files and optionally sends MCP notifications/message.
 */
class Logger {
  private static instance: Logger;
  private winstonLogger?: winston.Logger;
  private initialized = false;
  private mcpNotificationSender?: McpNotificationSender;
  private currentMcpLevel: McpLogLevel = "info"; // Default MCP level
  private currentWinstonLevel: "debug" | "info" | "warn" | "error" = "info"; // Default Winston level

  private constructor() {}

  /**
   * Initialize Winston logger for file transport. Must be called once at app start.
   * Console transport is added conditionally.
   * @param level Initial minimum level to log ('info' default).
   */
  public async initialize(level: McpLogLevel = "info"): Promise<void> {
    if (this.initialized) {
      this.warning("Logger already initialized.", { loggerSetup: true });
      return;
    }
    this.currentMcpLevel = level;
    this.currentWinstonLevel = mcpToWinstonLevel[level];

    let logsDirCreatedMessage: string | null = null;

    // Ensure logs directory exists
    if (isLogsDirSafe) {
      try {
        if (!fs.existsSync(resolvedLogsDir)) {
          fs.mkdirSync(resolvedLogsDir, { recursive: true });
          logsDirCreatedMessage = `Created logs directory: ${resolvedLogsDir}`;
        }
      } catch (err: any) {
        // Conditional console output for pre-init errors to avoid issues with stdio MCP clients.
        if (process.stdout.isTTY) {
          console.error(
            `Error creating logs directory at ${resolvedLogsDir}: ${err.message}. File logging disabled.`,
          );
        }
      }
    }

    // Common format for files
    const fileFormat = winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json(),
    );

    const transports: TransportStream[] = [];

    // Add file transports only if the directory is safe
    if (isLogsDirSafe) {
      transports.push(
        new winston.transports.File({
          filename: path.join(resolvedLogsDir, "error.log"),
          level: "error",
          format: fileFormat,
        }),
        new winston.transports.File({
          filename: path.join(resolvedLogsDir, "warn.log"),
          level: "warn",
          format: fileFormat,
        }),
        new winston.transports.File({
          filename: path.join(resolvedLogsDir, "info.log"),
          level: "info",
          format: fileFormat,
        }),
        new winston.transports.File({
          filename: path.join(resolvedLogsDir, "debug.log"),
          level: "debug",
          format: fileFormat,
        }),
        new winston.transports.File({
          filename: path.join(resolvedLogsDir, "combined.log"),
          format: fileFormat,
        }),
      );
    } else {
      // Conditional console output for pre-init warnings.
      if (process.stdout.isTTY) {
        console.warn(
          "File logging disabled due to unsafe logs directory path.",
        );
      }
    }

    let consoleLoggingEnabledMessage: string | null = null;
    let consoleLoggingSkippedMessage: string | null = null;

    // Conditionally add Console transport only if:
    // 1. MCP level is 'debug'
    // 2. stdout is a TTY (interactive terminal, not piped)
    if (this.currentMcpLevel === "debug" && process.stdout.isTTY) {
      const consoleFormat = createWinstonConsoleFormat();
      transports.push(
        new winston.transports.Console({
          level: "debug",
          format: consoleFormat,
        }),
      );
      consoleLoggingEnabledMessage =
        "Console logging enabled at level: debug (stdout is TTY)";
    } else if (this.currentMcpLevel === "debug" && !process.stdout.isTTY) {
      consoleLoggingSkippedMessage =
        "Console logging skipped: Level is debug, but stdout is not a TTY (likely stdio transport).";
    }

    // Create logger with the initial Winston level and configured transports
    this.winstonLogger = winston.createLogger({
      level: this.currentWinstonLevel,
      transports,
      exitOnError: false,
    });

    // Log deferred messages now that winstonLogger is initialized
    if (logsDirCreatedMessage) {
      this.info(logsDirCreatedMessage, { loggerSetup: true });
    }
    if (consoleLoggingEnabledMessage) {
      this.info(consoleLoggingEnabledMessage, { loggerSetup: true });
    }
    if (consoleLoggingSkippedMessage) {
      this.info(consoleLoggingSkippedMessage, { loggerSetup: true });
    }

    this.initialized = true;
    await Promise.resolve(); // Yield to event loop
    this.info(
      `Logger initialized. File logging level: ${this.currentWinstonLevel}. MCP logging level: ${this.currentMcpLevel}. Console logging: ${process.stdout.isTTY && this.currentMcpLevel === "debug" ? "enabled" : "disabled"}`,
      { loggerSetup: true },
    );
  }

  /**
   * Sets the function used to send MCP 'notifications/message'.
   */
  public setMcpNotificationSender(
    sender: McpNotificationSender | undefined,
  ): void {
    this.mcpNotificationSender = sender;
    const status = sender ? "enabled" : "disabled";
    this.info(`MCP notification sending ${status}.`, { loggerSetup: true });
  }

  /**
   * Dynamically sets the minimum logging level.
   */
  public setLevel(newLevel: McpLogLevel): void {
    if (!this.ensureInitialized()) {
      // Conditional console output if logger not usable.
      if (process.stdout.isTTY) {
        console.error("Cannot set level: Logger not initialized.");
      }
      return;
    }
    if (!(newLevel in mcpLevelSeverity)) {
      this.warning(
        `Invalid MCP log level provided: ${newLevel}. Level not changed.`,
      );
      return;
    }

    const oldLevel = this.currentMcpLevel;
    this.currentMcpLevel = newLevel;
    this.currentWinstonLevel = mcpToWinstonLevel[newLevel];
    this.winstonLogger!.level = this.currentWinstonLevel;

    // Add or remove console transport based on the new level and TTY status
    const consoleTransport = this.winstonLogger!.transports.find(
      (t) => t instanceof winston.transports.Console,
    );
    const shouldHaveConsole = newLevel === "debug" && process.stdout.isTTY;

    if (shouldHaveConsole && !consoleTransport) {
      // Add console transport
      const consoleFormat = createWinstonConsoleFormat();
      this.winstonLogger!.add(
        new winston.transports.Console({
          level: "debug",
          format: consoleFormat,
        }),
      );
      this.info("Console logging dynamically enabled.", { loggerSetup: true });
    } else if (!shouldHaveConsole && consoleTransport) {
      // Remove console transport
      this.winstonLogger!.remove(consoleTransport);
      this.info("Console logging dynamically disabled.", { loggerSetup: true });
    }

    if (oldLevel !== newLevel) {
      this.info(
        `Log level changed. File logging level: ${this.currentWinstonLevel}. MCP logging level: ${this.currentMcpLevel}. Console logging: ${shouldHaveConsole ? "enabled" : "disabled"}`,
        { loggerSetup: true },
      );
    }
  }

  /** Get singleton instance. */
  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /** Ensures the logger has been initialized. */
  private ensureInitialized(): boolean {
    if (!this.initialized || !this.winstonLogger) {
      // Conditional console output if logger not usable.
      if (process.stdout.isTTY) {
        console.warn("Logger not initialized; message dropped.");
      }
      return false;
    }
    return true;
  }

  /** Centralized log processing */
  private log(
    level: McpLogLevel,
    msg: string,
    context?: Record<string, any>,
    error?: Error,
  ): void {
    if (!this.ensureInitialized()) return;
    if (mcpLevelSeverity[level] > mcpLevelSeverity[this.currentMcpLevel]) {
      return;
    }

    const logData: Record<string, any> = { ...context };
    const winstonLevel = mcpToWinstonLevel[level];

    if (error) {
      this.winstonLogger!.log(winstonLevel, msg, { ...logData, error: error });
    } else {
      this.winstonLogger!.log(winstonLevel, msg, logData);
    }

    if (this.mcpNotificationSender) {
      const mcpDataPayload: any = { message: msg };
      if (context) mcpDataPayload.context = context;
      if (error) {
        mcpDataPayload.error = { message: error.message };
        if (this.currentMcpLevel === "debug" && error.stack) {
          mcpDataPayload.error.stack = error.stack.substring(0, 500);
        }
      }
      try {
        this.mcpNotificationSender(level, mcpDataPayload, config.mcpServerName);
      } catch (sendError) {
        this.winstonLogger!.error("Failed to send MCP log notification", {
          originalLevel: level,
          originalMessage: msg,
          sendError:
            sendError instanceof Error ? sendError.message : String(sendError),
          mcpPayload: mcpDataPayload,
        });
      }
    }
  }

  // --- Public Logging Methods ---
  public debug(msg: string, context?: Record<string, any>): void {
    this.log("debug", msg, context);
  }
  public info(msg: string, context?: Record<string, any>): void {
    this.log("info", msg, context);
  }
  public notice(msg: string, context?: Record<string, any>): void {
    this.log("notice", msg, context);
  }
  public warning(msg: string, context?: Record<string, any>): void {
    this.log("warning", msg, context);
  }
  public error(
    msg: string,
    err?: Error | Record<string, any>,
    context?: Record<string, any>,
  ): void {
    const errorObj = err instanceof Error ? err : undefined;
    const combinedContext =
      err instanceof Error ? context : { ...(err || {}), ...(context || {}) };
    this.log("error", msg, combinedContext, errorObj);
  }
  public crit(
    msg: string,
    err?: Error | Record<string, any>,
    context?: Record<string, any>,
  ): void {
    const errorObj = err instanceof Error ? err : undefined;
    const combinedContext =
      err instanceof Error ? context : { ...(err || {}), ...(context || {}) };
    this.log("crit", msg, combinedContext, errorObj);
  }
  public alert(
    msg: string,
    err?: Error | Record<string, any>,
    context?: Record<string, any>,
  ): void {
    const errorObj = err instanceof Error ? err : undefined;
    const combinedContext =
      err instanceof Error ? context : { ...(err || {}), ...(context || {}) };
    this.log("alert", msg, combinedContext, errorObj);
  }
  public emerg(
    msg: string,
    err?: Error | Record<string, any>,
    context?: Record<string, any>,
  ): void {
    const errorObj = err instanceof Error ? err : undefined;
    const combinedContext =
      err instanceof Error ? context : { ...(err || {}), ...(context || {}) };
    this.log("emerg", msg, combinedContext, errorObj);
  }
  public fatal(
    msg: string,
    context?: Record<string, any>,
    error?: Error,
  ): void {
    this.log("emerg", msg, context, error);
  }
}

// Export singleton instance
export const logger = Logger.getInstance();
