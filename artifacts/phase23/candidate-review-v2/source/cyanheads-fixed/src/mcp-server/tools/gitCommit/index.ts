/**
 * @fileoverview Barrel file for the gitCommit tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  initializeGitCommitStateAccessors,
  registerGitCommitTool,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitCommitInput, GitCommitResult } from './logic.js';
