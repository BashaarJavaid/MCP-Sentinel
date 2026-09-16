/**
 * @fileoverview Barrel file for the git_stash tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitStashTool,
  initializeGitStashStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitStashInput, GitStashResult } from './logic.js';
