import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import stopSandbox, { argSchema as stopSchema } from './tools/stop.ts';

const server = new McpServer({ name: 'phase23-stop-reproduction', version: '1.0.0' });
server.tool('sandbox_stop', 'Remove a sandbox container.', stopSchema, stopSandbox);
await server.connect(new StdioServerTransport());
