/**
 * @fileoverview Barrel file for the gitLog tool.
 */

export {
  registerGitLogTool,
  initializeGitLogStateAccessors,
} from "./registration.js";
// Export types if needed elsewhere, e.g.:
// export type { GitLogInput, GitLogResult } from './logic.js';
