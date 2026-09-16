/**
 * @fileoverview Barrel file for the git_merge tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitMergeTool,
  initializeGitMergeStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitMergeInput, GitMergeResult } from './logic.js';
