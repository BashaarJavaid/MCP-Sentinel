import { z } from 'zod';
import { execFileSync } from 'node:child_process';
import { validateSandboxRef } from '../utils.ts';

export const argumentsSchema = {
  sandbox_ref: z.string().regex(/^[a-zA-Z0-9_.-]+$/, 'Invalid container ID'),
};

export default async function removeSandbox({ sandbox_ref }: { sandbox_ref: string }) {
  const checkedRef = validateSandboxRef(sandbox_ref);
  if (!checkedRef) {
    return { content: [{ type: 'text' as const, text: 'Invalid container ID' }] };
  }
  execFileSync('docker', ['rm', '-f', checkedRef]);
  return { content: [{ type: 'text' as const, text: 'Container removed.' }] };
}
