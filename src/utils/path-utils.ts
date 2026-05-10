import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * We rely on the Colab script to have mirrored the Drive structure
 * into the public folder.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Normalize path by removing leading slash if present for staticFile
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;

  return staticFile(normalizedPath);
};
