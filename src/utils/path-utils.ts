import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Since assets are mirrored directly into the public/ folder root,
 * we extract the filename and resolve it using staticFile.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Extract only the filename (e.g. "scene_1.mp4" from any path)
  const parts = path.split('/');
  const filename = parts[parts.length - 1];

  if (filename) {
    const resolved = staticFile(filename);
    console.log(`Resolving: ${path} -> ${resolved}`);
    return resolved;
  }

  return path;
};
