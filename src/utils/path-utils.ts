import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Bypasses folder structures by extracting the filename and looking
 * in the root of the public folder (where Colab mirrors assets).
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Extract just the filename (e.g. "scene_1.mp4")
  const filename = path.split('/').pop();

  // If we have a filename, we assume the Colab script put it in public/
  if (filename) {
      return staticFile(filename);
  }

  return path;
};
