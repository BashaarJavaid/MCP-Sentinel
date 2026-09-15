/**
 * @fileoverview Barrel file for the git_clear_working_dir tool.
 * Exports the registration function and related components.
 */

export {
  registerGitClearWorkingDirTool,
  initializeGitClearWorkingDirStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitClearWorkingDirInput, GitClearWorkingDirResult } from './logic.js';
