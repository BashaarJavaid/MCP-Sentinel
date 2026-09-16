// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { gitInitLogic } from "./mcp-server/tools/gitInit/logic.js";

const server = new McpServer({ name: "phase23-git-init", version: "1.0.0" });
server.tool("git_init", "Initialize a Git repository", { initialBranch: z.string().optional() },
  async (input) => {
    await gitInitLogic(input);
    return { content: [{ type: "text" as const, text: "Complete" }] };
  });
await server.connect(new StdioServerTransport());
