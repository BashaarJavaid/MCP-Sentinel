/**
 * @fileoverview Barrel file for the git_clean tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitCleanTool,
  initializeGitCleanStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitCleanInput, GitCleanResult } from './logic.js';
