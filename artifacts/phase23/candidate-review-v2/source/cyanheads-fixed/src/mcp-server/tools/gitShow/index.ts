/**
 * @fileoverview Barrel file for the git_show tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitShowTool,
  initializeGitShowStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitShowInput, GitShowResult } from './logic.js';
