import { z } from "zod";
import { logger, RequestContext } from "../../../utils/index.js"; // Added logger
import { getGitStatus, GitStatusResult } from "../gitStatus/logic.js"; // Corrected path

// Define the input schema
export const GitWrapupInstructionsInputSchema = z.object({
  acknowledgement: z.enum(["Y", "y", "Yes", "yes"], {
    required_error: "Acknowledgement is required.",
    description:
      'Acknowledgement that you have permission (implicit allowed, explicit preferred) from the user to initiate this tool. Must be "Y" or "Yes" (case-insensitive).',
  }),
  updateAgentMetaFiles: z
    .enum(["Y", "y", "Yes", "yes"])
    .optional()
    .describe(
      "If set to 'Y' or 'Yes', include an extra instruction to review and update agent-specific meta files like .clinerules or claude.md if present. Only use this if the user explicitly requested it.",
    ),
});

// Infer the TypeScript type for the input.
export type GitWrapupInstructionsInput = z.infer<
  typeof GitWrapupInstructionsInputSchema
>;

// Define the structure of the result object that the logic function will return.
export interface GitWrapupInstructionsResult {
  instructions: string;
  gitStatus?: GitStatusResult; // To hold the structured git status output
  gitStatusError?: string; // To hold any error message if git status fails
}

// The predefined instructions string.
const WRAPUP_INSTRUCTIONS = `
Perform all actions for our git wrapup workflow:
1. Use the git_diff tool to understand the precise nature and rationale behind each change (what changed and why did it change?) within the code base. Use the 'includeUntracked' parameter to view all changes, including untracked files. This will help you understand the context and purpose of the modifications made.
2. For substantial code updates, review and update the README to ensure it is up to date with our current codebase (make a note to the user of any discrepancies you noticed, gathered from everything you've seen of our codebase so far).
3. Update the CHANGELOG with concise, descriptive entries detailing all modifications, clearly indicating their purpose (e.g., bug fix, feature implementation, refactoring). Include specific metrics or identifiers where applicable, such as issue numbers or pull request links, to provide context and traceability for each change. This will help maintain a clear history of changes and their impacts on the project.
4. Proceed to commit all changes; based on your review of the git_diff and readme, group these changes into logical, atomic commits, each accompanied by a clear and descriptive message adhering to Conventional Commits standards (e.g. "docs(readme): updated readme to include xyz."). Note the 'git_commit' tool allows you to also stage the files while commiting. Ensure commit messages accurately convey the scope and impact of the changes, incorporating specific metrics or identifiers where applicable.
Note: Be sure to set 'git_set_working_dir' if not already set.

Instructions: Now write a concise list of what you must do to complete the git wrapup workflow, then perform all actions. Do not push unless requested.
`;

/**
 * Core logic for the git_wrapup_instructions tool.
 * This tool simply returns a predefined set of instructions, potentially augmented.
 *
 * @param {GitWrapupInstructionsInput} input - The validated input, may contain 'updateAgentMetaFiles'.
 * @param {RequestContext} _context - The request context (included for consistency, not used in this simple logic).
 * @returns {Promise<GitWrapupInstructionsResult>} A promise that resolves with the wrap-up instructions.
 */
export async function getWrapupInstructions(
  input: GitWrapupInstructionsInput,
  // The context is now expected to be enhanced by the registration layer
  // to include session-specific methods like getWorkingDirectory.
  context: RequestContext & {
    sessionId?: string;
    getWorkingDirectory: () => string | undefined;
  },
): Promise<GitWrapupInstructionsResult> {
  const operation = "getWrapupInstructions";
  logger.debug(`Executing ${operation}`, { ...context, input });

  let finalInstructions = WRAPUP_INSTRUCTIONS;
  if (
    input.updateAgentMetaFiles &&
    ["Y", "y", "Yes", "yes"].includes(input.updateAgentMetaFiles)
  ) {
    finalInstructions += ` Extra request: review and update if needed the .clinerules and claude.md files if present.`;
  }

  let statusResult: GitStatusResult | undefined = undefined;
  let statusError: string | undefined = undefined;

  const workingDir = context.getWorkingDirectory();

  if (workingDir) {
    try {
      // The `getGitStatus` function expects `path` and a context with `getWorkingDirectory`.
      // Passing `path: '.'` signals `getGitStatus` to use the working directory from the context.
      // The `registration.ts` for this tool will be responsible for ensuring `context.getWorkingDirectory` is correctly supplied.
      statusResult = await getGitStatus({ path: "." }, context);
    } catch (error: any) {
      logger.warning(
        `Failed to get git status while generating wrapup instructions (working dir: ${workingDir}). Tool will proceed without it.`,
        {
          ...context,
          tool: "gitWrapupInstructions",
          originalError: error.message,
        },
      );
      statusError = error instanceof Error ? error.message : String(error);
    }
  } else {
    logger.info(
      "No working directory set for session, skipping git status for wrapup instructions.",
      { ...context, tool: "gitWrapupInstructions" },
    );
    statusError = "No working directory set for session, git status skipped.";
  }

  return {
    instructions: finalInstructions,
    gitStatus: statusResult,
    gitStatusError: statusError,
  };
}
