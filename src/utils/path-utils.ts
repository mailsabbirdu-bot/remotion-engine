import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Physically copied assets in public/ folder are accessed via staticFile.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Paths starting with / are assumed to be in the public folder
  return path.startsWith('/') ? staticFile(path.substring(1)) : staticFile(path);
};
