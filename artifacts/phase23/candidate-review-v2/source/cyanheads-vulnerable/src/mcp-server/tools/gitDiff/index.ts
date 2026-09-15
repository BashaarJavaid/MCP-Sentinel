/**
 * @fileoverview Barrel file for the gitDiff tool.
 */

export {
  registerGitDiffTool,
  initializeGitDiffStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitDiffInput, GitDiffResult } from './logic.js';
