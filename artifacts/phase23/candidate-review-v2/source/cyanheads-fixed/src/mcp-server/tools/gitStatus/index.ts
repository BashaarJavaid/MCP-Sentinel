/**
 * @fileoverview Barrel file for the gitStatus tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitStatusTool,
  initializeGitStatusStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitStatusInput, GitStatusResult } from './logic.js';
