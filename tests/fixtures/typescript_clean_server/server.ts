import { McpServer } from "@modelcontextprotocol/server";
import { readFile, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { bearerAuth } from "hono/bearer-auth";
import { z } from "zod";

const server = new McpServer({ name: "clean", version: "0.0.0" });
writeFileSync("top-level-marker", "target code executed");

server.registerTool(
  "read",
  {
    description: "Read the approved file.",
    inputSchema: { path: z.string().default("./data.txt") },
  },
  async ({ path }) => ({
    content: [{ type: "text", text: await readFile("./data.txt", "utf8") }],
    requested: path,
  }),
);

const app = new Hono();
app.use(bearerAuth({ token: process.env.PUBLIC_TOKEN }));
app.get("/admin", (context) => context.text("ok"));

function loadTools() {
  const bytes = readFileSync("tools.json", "utf8");
  const digest = createHash("sha256").update(bytes).digest("hex");
  if (digest !== EXPECTED_DIGEST) throw new Error("bad manifest");
  return JSON.parse(bytes);
}
