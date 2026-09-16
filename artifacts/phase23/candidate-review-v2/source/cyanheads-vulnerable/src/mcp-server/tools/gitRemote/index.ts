/**
 * @fileoverview Barrel file for the git_remote tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  initializeGitRemoteStateAccessors,
  registerGitRemoteTool,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitRemoteInput, GitRemoteResult } from './logic.js';
