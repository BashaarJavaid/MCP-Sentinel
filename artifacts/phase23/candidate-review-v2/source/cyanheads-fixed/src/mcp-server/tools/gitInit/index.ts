/**
 * @fileoverview Barrel file for the git_init tool.
 * Exports the registration function and the state accessor initializer.
 */

export {
  registerGitInitTool,
  initializeGitInitStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitInitInput, GitInitResult } from './logic.js';
