/**
 * @fileoverview Barrel file for the git_tag tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitTagTool,
  initializeGitTagStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitTagInput, GitTagResult } from './logic.js';
