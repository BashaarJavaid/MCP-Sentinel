import { z } from 'zod';
import { execFileSync } from 'node:child_process';
import { sanitizeContainerId } from '../utils.ts';

export const argSchema = {
  container_id: z.string().regex(/^[a-zA-Z0-9_.-]+$/, 'Invalid container ID'),
};

export default async function stopSandbox({ container_id }: { container_id: string }) {
  const validId = sanitizeContainerId(container_id);
  if (!validId) {
    return { content: [{ type: 'text' as const, text: 'Invalid container ID' }] };
  }
  execFileSync('docker', ['rm', '-f', validId]);
  return { content: [{ type: 'text' as const, text: 'Container removed.' }] };
}
