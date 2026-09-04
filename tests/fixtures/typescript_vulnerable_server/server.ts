import { McpServer } from "@modelcontextprotocol/server";
import { readFile, readFileSync, writeFileSync } from "node:fs";
import express from "express";

const server = new McpServer({ name: "vulnerable", version: "0.0.0" });
writeFileSync("top-level-marker", "target code executed");
const apiKey = "ghp_abcdefghijklmnopqrstuvwxyz123456";

server.registerTool(
  "unsafe",
  { description: "Read and evaluate a file." },
  async (path) => {
    const source = await readFile(path, "utf8");
    return eval(source);
  },
);

async function forwardToolResult() {
  const result = await client.callTool({ name: "remote" });
  const text = result.text;
  return openai.responses.create({ input: text });
}

const app = express();
app.get("/admin", (_request, response) => response.send(apiKey));

function loadTools() {
  const bytes = readFileSync("tools.json", "utf8");
  return JSON.parse(bytes);
}
