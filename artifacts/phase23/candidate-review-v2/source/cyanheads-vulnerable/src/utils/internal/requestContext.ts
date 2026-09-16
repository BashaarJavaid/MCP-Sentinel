import { logger } from "./logger.js";
// Import utils from the main barrel file (generateUUID from ../security/idGenerator.js)
import { generateUUID } from "../index.js";
// Removed incorrect import: import { RequestContext } from './rateLimiter.js';

/**
 * Defines the structure for context information associated with a request or operation.
 */
export interface RequestContext {
  /** Unique identifier generated for the request context instance. */
  requestId: string;
  /** ISO 8601 timestamp indicating when the context was created. */
  timestamp: string;
  /** Allows for additional, arbitrary key-value pairs for specific context needs. */
  [key: string]: any; // Allow flexible extension
}

/**
 * Configuration interface for request context utilities
 */
export interface ContextConfig {
  /** Custom configuration properties */
  [key: string]: unknown;
}

/**
 * Operation context with request data
 */
export interface OperationContext {
  /** Request context data */
  requestContext?: RequestContext;
  /** Custom context properties */
  [key: string]: unknown;
}

// Direct instance for request context utilities
const requestContextServiceInstance = {
  config: {} as ContextConfig,

  /**
   * Configure service settings
   * @param config New configuration
   * @returns Updated configuration
   */
  configure(config: Partial<ContextConfig>): ContextConfig {
    this.config = {
      ...this.config,
      ...config,
    };
    logger.debug("RequestContext configuration updated", {
      config: this.config,
    });
    return { ...this.config };
  },

  /**
   * Get current configuration
   * @returns Current configuration
   */
  getConfig(): ContextConfig {
    return { ...this.config };
  },

  /**
   * Create a request context with unique ID and timestamp
   * @param additionalContext Additional context properties
   * @returns Request context object
   */
  createRequestContext(
    additionalContext: Record<string, unknown> = {},
  ): RequestContext {
    const requestId = generateUUID(); // Use imported generateUUID
    const timestamp = new Date().toISOString();

    return {
      requestId,
      timestamp,
      ...additionalContext,
    };
  },

  // generateSecureRandomString function removed as it was unused and redundant
};

// Export the instance directly
export const requestContextService = requestContextServiceInstance;

// Removed delegate functions and default export for simplicity.
// Users should import and use `requestContextService` directly.
// e.g., import { requestContextService } from './requestContext.js';
// requestContextService.createRequestContext();
