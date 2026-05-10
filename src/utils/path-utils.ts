import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Since assets are flattened into the public/ folder during Colab runs,
 * we extract the filename and resolve it using staticFile.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Extract only the filename (e.g. "scene_1.mp4")
  const parts = path.split('/');
  const filename = parts[parts.length - 1];

  if (filename) {
    // We try to find it in the public root first (where Colab flattens them)
    return staticFile(filename);
  }

  return path;
};
