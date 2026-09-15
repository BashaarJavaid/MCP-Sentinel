import { BaseErrorCode, McpError } from "../../types-global/errors.js"; // Corrected path
import { logger } from "./logger.js";
import { sanitizeInputForLogging } from "../index.js"; // Import from main barrel file

/**
 * Generic error context interface
 */
export interface ErrorContext {
  /** Unique request or operation identifier */
  requestId?: string;
  /** Any additional context information */
  [key: string]: unknown;
}

/**
 * Error handler options
 */
export interface ErrorHandlerOptions {
  /** The context of the operation that caused the error */
  context?: ErrorContext;
  /** The name of the operation being performed */
  operation: string;
  /** The input that caused the error */
  input?: unknown;
  /** Whether to rethrow the error after handling */
  rethrow?: boolean;
  /** Custom error code to use when creating an McpError */
  errorCode?: BaseErrorCode;
  /** Custom error mapper function */
  errorMapper?: (error: unknown) => Error;
  /** Whether to include stack traces in logs */
  includeStack?: boolean;
  /** Whether this is a critical error that should abort operations */
  critical?: boolean;
}

/**
 * Base error mapping rule
 */
export interface BaseErrorMapping {
  /** Pattern to match in the error message */
  pattern: string | RegExp;
  /** Error code for mapped errors */
  errorCode: BaseErrorCode;
  /** Custom error message template */
  messageTemplate?: string;
}

/**
 * Error mapping configuration
 */
export interface ErrorMapping<T extends Error = Error>
  extends BaseErrorMapping {
  /** Factory function to create the mapped error */
  factory: (error: unknown, context?: Record<string, unknown>) => T;
  /** Additional context to merge with error context */
  additionalContext?: Record<string, unknown>;
}

/**
 * Simple mapper that maps error types to error codes
 */
const ERROR_TYPE_MAPPINGS: Record<string, BaseErrorCode> = {
  SyntaxError: BaseErrorCode.VALIDATION_ERROR,
  TypeError: BaseErrorCode.VALIDATION_ERROR,
  ReferenceError: BaseErrorCode.INTERNAL_ERROR,
  RangeError: BaseErrorCode.VALIDATION_ERROR,
  URIError: BaseErrorCode.VALIDATION_ERROR,
  EvalError: BaseErrorCode.INTERNAL_ERROR,
};

/**
 * Common error patterns for automatic classification
 */
const COMMON_ERROR_PATTERNS: BaseErrorMapping[] = [
  // Authentication related errors
  {
    pattern:
      /auth|unauthorized|unauthenticated|not.*logged.*in|invalid.*token|expired.*token/i,
    errorCode: BaseErrorCode.UNAUTHORIZED,
  },
  // Permission related errors
  {
    pattern: /permission|forbidden|access.*denied|not.*allowed/i,
    errorCode: BaseErrorCode.FORBIDDEN,
  },
  // Not found errors
  {
    pattern: /not.*found|missing|no.*such|doesn't.*exist|couldn't.*find/i,
    errorCode: BaseErrorCode.NOT_FOUND,
  },
  // Validation errors
  {
    pattern: /invalid|validation|malformed|bad request|wrong format/i,
    errorCode: BaseErrorCode.VALIDATION_ERROR,
  },
  // Conflict errors
  {
    pattern: /conflict|already.*exists|duplicate|unique.*constraint/i,
    errorCode: BaseErrorCode.CONFLICT,
  },
  // Rate limiting
  {
    pattern: /rate.*limit|too.*many.*requests|throttled/i,
    errorCode: BaseErrorCode.RATE_LIMITED,
  },
  // Timeout errors
  {
    pattern: /timeout|timed.*out|deadline.*exceeded/i,
    errorCode: BaseErrorCode.TIMEOUT,
  },
  // External service errors
  {
    pattern: /service.*unavailable|bad.*gateway|gateway.*timeout/i,
    errorCode: BaseErrorCode.SERVICE_UNAVAILABLE,
  },
];

/**
 * Get a readable name for an error
 * @param error Error to get name for
 * @returns User-friendly error name
 */
function getErrorName(error: unknown): string {
  if (error instanceof Error) {
    return error.name || "Error";
  }

  if (error === null) {
    return "NullError";
  }

  if (error === undefined) {
    return "UndefinedError";
  }

  return typeof error === "object" ? "ObjectError" : "UnknownError";
}

/**
 * Get a message from an error
 * @param error Error to get message from
 * @returns Error message
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (error === null) {
    return "Null error occurred";
  }

  if (error === undefined) {
    return "Undefined error occurred";
  }

  return typeof error === "string" ? error : String(error);
}

/**
 * Error handler utility class with various error handling methods
 */
export class ErrorHandler {
  /**
   * Determine the appropriate error code for an error based on patterns and type
   * @param error The error to classify
   * @returns The appropriate error code
   */
  public static determineErrorCode(error: unknown): BaseErrorCode {
    // If it's already an McpError, use its code
    if (error instanceof McpError) {
      return error.code;
    }

    const errorName = getErrorName(error);
    const errorMessage = getErrorMessage(error);

    // Check if the error type has a direct mapping
    if (errorName in ERROR_TYPE_MAPPINGS) {
      return ERROR_TYPE_MAPPINGS[errorName as keyof typeof ERROR_TYPE_MAPPINGS];
    }

    // Check for common error patterns
    for (const pattern of COMMON_ERROR_PATTERNS) {
      const regex =
        pattern.pattern instanceof RegExp
          ? pattern.pattern
          : new RegExp(pattern.pattern, "i");

      if (regex.test(errorMessage) || regex.test(errorName)) {
        return pattern.errorCode;
      }
    }

    // Default to internal error if no pattern matches
    return BaseErrorCode.INTERNAL_ERROR;
  }

  /**
   * Handle operation errors with consistent logging and transformation
   * @param error The error that occurred
   * @param options Error handling options
   * @returns The transformed error
   */
  public static handleError(
    error: unknown,
    options: ErrorHandlerOptions,
  ): Error {
    const {
      context,
      operation,
      input,
      rethrow = false,
      errorCode: explicitErrorCode,
      includeStack = true,
      critical = false,
    } = options;

    // If it's already an McpError, use it directly but apply additional context
    if (error instanceof McpError) {
      // Add any additional context
      if (context && Object.keys(context).length > 0) {
        // Ensure details is an object before spreading
        const existingDetails =
          typeof error.details === "object" && error.details !== null
            ? error.details
            : {};
        error.details = { ...existingDetails, ...context };
      }

      // Log the error with sanitized input
      logger.error(`Error ${operation}: ${error.message}`, {
        errorCode: error.code,
        requestId: context?.requestId,
        input: input ? sanitizeInputForLogging(input) : undefined,
        stack: includeStack ? error.stack : undefined,
        critical,
        ...context,
      });

      if (rethrow) {
        throw error;
      }

      // Ensure the function returns an Error type
      return error;
    }

    // Sanitize input for logging
    const sanitizedInput = input ? sanitizeInputForLogging(input) : undefined;

    // Log the error with consistent format
    logger.error(`Error ${operation}`, {
      error: getErrorMessage(error), // Use helper function
      errorType: getErrorName(error),
      input: sanitizedInput,
      requestId: context?.requestId,
      stack: includeStack && error instanceof Error ? error.stack : undefined,
      critical,
      ...context,
    });

    // Choose the error code (explicit > determined > default)
    const errorCode =
      explicitErrorCode ||
      ErrorHandler.determineErrorCode(error) ||
      BaseErrorCode.INTERNAL_ERROR;

    // Transform to appropriate error type
    let transformedError: Error;
    if (options.errorMapper) {
      transformedError = options.errorMapper(error);
    } else {
      transformedError = new McpError(
        errorCode,
        `Error ${operation}: ${getErrorMessage(error)}`, // Use helper function
        {
          originalError: getErrorName(error),
          ...context,
        },
      );
    }

    // Rethrow if requested
    if (rethrow) {
      throw transformedError;
    }

    // Ensure the function returns an Error type
    return transformedError;
  }

  /**
   * Map an error to a specific error type based on error message patterns
   * @param error The error to map
   * @param mappings Array of pattern and factory mappings
   * @param defaultFactory Default factory function if no pattern matches
   * @returns The mapped error
   */
  public static mapError<T extends Error>(
    error: unknown,
    mappings: ErrorMapping<T>[],
    defaultFactory?: (error: unknown, context?: Record<string, unknown>) => T,
  ): T | Error {
    // If it's already the target type and we have a default factory to check against, return it
    if (defaultFactory && error instanceof Error) {
      const defaultInstance = defaultFactory(error);
      if (error.constructor === defaultInstance.constructor) {
        return error as T;
      }
    }

    const errorMessage = getErrorMessage(error);

    // Check each pattern and return the first match
    for (const mapping of mappings) {
      const matches =
        mapping.pattern instanceof RegExp
          ? mapping.pattern.test(errorMessage)
          : errorMessage.includes(mapping.pattern);

      if (matches) {
        return mapping.factory(error, mapping.additionalContext);
      }
    }

    // Return default or original error
    if (defaultFactory) {
      return defaultFactory(error);
    }

    return error instanceof Error ? error : new Error(String(error));
  }

  // Removed createErrorMapper method for simplification

  /**
   * Format an error for consistent response structure
   * @param error The error to format
   * @returns Formatted error object
   */
  public static formatError(error: unknown): Record<string, unknown> {
    if (error instanceof McpError) {
      return {
        code: error.code,
        message: error.message,
        // Ensure details is an object
        details:
          typeof error.details === "object" && error.details !== null
            ? error.details
            : {},
      };
    }

    if (error instanceof Error) {
      return {
        code: ErrorHandler.determineErrorCode(error),
        message: error.message,
        details: { errorType: error.name },
      };
    }

    return {
      code: BaseErrorCode.UNKNOWN_ERROR,
      message: String(error),
      details: { errorType: typeof error },
    };
  }

  /**
   * Safely execute a function and handle any errors
   * @param fn Function to execute
   * @param options Error handling options
   * @returns The result of the function or error
   */
  public static async tryCatch<T>(
    fn: () => Promise<T> | T,
    options: ErrorHandlerOptions,
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      throw ErrorHandler.handleError(error, { ...options, rethrow: true });
    }
  }
}
