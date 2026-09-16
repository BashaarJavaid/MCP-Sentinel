import dotenv from "dotenv";
import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
// Removed logger import to break circular dependency

dotenv.config(); // Load environment variables from .env file

// Determine the directory name of the current module
const __dirname = dirname(fileURLToPath(import.meta.url));
// Construct the path to package.json relative to the current file
const pkgPath = join(__dirname, "../../package.json");
// Default package information in case package.json is unreadable
let pkg = { name: "obsidian-mcp-server", version: "0.0.0" };

try {
  // Read and parse package.json to get server name and version
  pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
} catch (error) {
  // Silently use default pkg info if reading fails. Error will be logged later if needed.
}

/**
 * Main application configuration object.
 * Aggregates settings from environment variables and package.json.
 */
export const config = {
  /** The name of the MCP server, derived from package.json. */
  mcpServerName: pkg.name,
  /** The version of the MCP server, derived from package.json. */
  mcpServerVersion: pkg.version,
  /** Logging level for the application (e.g., "debug", "info", "warning", "error"). Defaults to "info". */
  logLevel: process.env.MCP_LOG_LEVEL || "info", // Use MCP_LOG_LEVEL consistently
  /** The runtime environment (e.g., "development", "production"). Defaults to "development". */
  environment: process.env.NODE_ENV || "development",
  /** The communication transport type ('stdio' or 'http'). Defaults to 'stdio'. */
  mcpTransportType: process.env.MCP_TRANSPORT_TYPE || "stdio",
  /** Port for the HTTP transport. Defaults to 3000. */
  mcpHttpPort: parseInt(process.env.MCP_HTTP_PORT || "3010", 10),
  /** Host for the HTTP transport. Defaults to '127.0.0.1'. */
  mcpHttpHost: process.env.MCP_HTTP_HOST || "127.0.0.1",
  /** Allowed origins for HTTP transport (comma-separated). */
  mcpAllowedOrigins: process.env.MCP_ALLOWED_ORIGINS?.split(",") || [],
  /** Flag to enable GPG signing for commits made by the git_commit tool. Requires server-side GPG setup. */
  gitSignCommits: process.env.GIT_SIGN_COMMITS === "true",
  /** The authentication mode ('jwt', 'oauth', or 'none'). Defaults to 'none'. */
  mcpAuthMode: process.env.MCP_AUTH_MODE || "none",
  /** Secret key for signing/verifying JWTs. Required if mcpAuthMode is 'jwt'. */
  mcpAuthSecretKey: process.env.MCP_AUTH_SECRET_KEY,
  /** The OIDC issuer URL for OAuth token validation. Required if mcpAuthMode is 'oauth'. */
  oauthIssuerUrl: process.env.OAUTH_ISSUER_URL,
  /** The audience claim for OAuth token validation. Required if mcpAuthMode is 'oauth'. */
  oauthAudience: process.env.OAUTH_AUDIENCE,
  /** The JWKS URI for fetching public keys for OAuth. Optional, can be derived from issuer URL. */
  oauthJwksUri: process.env.OAUTH_JWKS_URI,
  /** Security-related configurations. */
  security: {
    // Placeholder for security settings
    // Example: authRequired: process.env.AUTH_REQUIRED === 'true'
    /** Indicates if authentication is required for server operations. */
    authRequired: false,
  },
  // Note: mcpClient configuration is now loaded separately from mcp-config.json
};

/**
 * The configured logging level for the application.
 * Exported separately for convenience (e.g., logger initialization).
 * @type {string}
 */
export const logLevel = config.logLevel;

/**
 * The configured runtime environment for the application.
 * Exported separately for convenience.
 * @type {string}
 */
export const environment = config.environment;

// Logger initialization is now handled in the main application entry point (e.g., src/index.ts)
// after the config module has been fully loaded.
