import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import removeSandbox, { argumentsSchema as inputSchema } from './tools/stop.ts';

const mcpServer = new McpServer({ name: 'phase23-stop-reproduction', version: '1.0.0' });
mcpServer.tool('sandbox_stop', 'Remove a sandbox container.', inputSchema, removeSandbox);
await mcpServer.connect(new StdioServerTransport());
