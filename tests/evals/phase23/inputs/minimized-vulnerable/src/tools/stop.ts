import { z } from 'zod';
import { execSync } from 'node:child_process';

export const argSchema = { container_id: z.string() };

export default async function stopSandbox({ container_id }: { container_id: string }) {
  execSync(`docker rm -f ${container_id}`);
  return { content: [{ type: 'text' as const, text: 'Container removed.' }] };
}
