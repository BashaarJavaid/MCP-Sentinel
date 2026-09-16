/**
 * @fileoverview Barrel file for the git_branch tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitBranchTool,
  initializeGitBranchStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitBranchInput, GitBranchResult } from './logic.js';
