export function sanitizeContainerId(id: string): string | null {
  // Docker container names/IDs: https://docs.docker.com/engine/reference/commandline/run/#container-name
  // Allow alphanumerics, underscores, periods, dashes. Must start with alphanumeric.
  if (typeof id !== 'string') return null;
  if (/^[a-zA-Z0-9][a-zA-Z0-9_.-]*$/.test(id)) return id;
  return null;
}
