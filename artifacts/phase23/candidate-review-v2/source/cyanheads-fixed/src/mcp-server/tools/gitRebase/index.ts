/**
 * @fileoverview Barrel file for the git_rebase tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitRebaseTool,
  initializeGitRebaseStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitRebaseInput, GitRebaseResult } from './logic.js';
