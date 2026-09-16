/**
 * @fileoverview Barrel file for the gitAdd tool.
 * Exports the registration function and state accessor initialization function.
 */

export {
  registerGitAddTool,
  initializeGitAddStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitAddInput, GitAddResult } from './logic.js';
