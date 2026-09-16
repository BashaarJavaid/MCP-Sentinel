// Modified source reproduction for Phase 23; see MODIFICATIONS.md and LICENSE.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { initializeRepository } from "./mcp-server/tools/gitInit/logic.js";

const mcpServer = new McpServer({ name: "phase23-git-init", version: "1.0.0" });
mcpServer.tool("git_init", "Initialize a Git repository", { branchLabel: z.string().optional() },
  async (requestData) => {
    await initializeRepository(requestData);
    return { content: [{ type: "text" as const, text: "Complete" }] };
  });
await mcpServer.connect(new StdioServerTransport());
