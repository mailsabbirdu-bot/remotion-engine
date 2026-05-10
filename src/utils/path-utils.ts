import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * We rely on the Colab script to have mirrored the Drive structure
 * into the public folder.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // The user's JSON uses "/drive/Counterism_Studio_V4/renders/scene_1.mp4"
  // The script copies to "public/drive/Counterism_Studio_V4/renders/scene_1.mp4"
  // staticFile expects paths relative to public/, without the leading slash.
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;

  return staticFile(normalizedPath);
};
