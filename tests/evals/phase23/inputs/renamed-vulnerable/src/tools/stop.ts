import { z } from 'zod';
import { execSync } from 'node:child_process';

export const argumentsSchema = { sandbox_ref: z.string() };

export default async function removeSandbox({ sandbox_ref }: { sandbox_ref: string }) {
  execSync(`docker rm -f ${sandbox_ref}`);
  return { content: [{ type: 'text' as const, text: 'Container removed.' }] };
}
