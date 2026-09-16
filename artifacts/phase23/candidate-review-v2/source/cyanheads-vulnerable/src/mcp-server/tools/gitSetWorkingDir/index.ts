/**
 * @fileoverview Barrel file for the git_set_working_dir tool.
 * Exports the registration function and potentially other related components.
 */

export {
  registerGitSetWorkingDirTool,
  initializeGitSetWorkingDirStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitSetWorkingDirInput, GitSetWorkingDirResult } from './logic.js';
