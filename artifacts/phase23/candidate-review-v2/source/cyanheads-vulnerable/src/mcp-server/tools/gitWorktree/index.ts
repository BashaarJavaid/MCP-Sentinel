/**
 * @fileoverview Barrel file for the git_worktree tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitWorktreeTool,
  initializeGitWorktreeStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitWorktreeInput, GitWorktreeResult } from './logic.js';
