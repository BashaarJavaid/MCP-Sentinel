export {
  registerGitWrapupInstructionsTool,
  initializeGitWrapupInstructionsStateAccessors,
} from "./registration.js";
// This tool now requires session-specific state accessors (getWorkingDirectory, getSessionId)
// to fetch git status, so initializeGitWrapupInstructionsStateAccessors is exported for server setup.
