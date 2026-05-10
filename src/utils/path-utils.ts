import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Since assets are copied directly into the public/ folder root in Colab,
 * we extract the filename and resolve it using staticFile.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';

  // If it's already a URL or data URI, return as is
  if (path.startsWith('http') || path.startsWith('data:')) {
    return path;
  }

  // Extract only the filename (e.g. "scene_1.mp4" from "/drive/path/scene_1.mp4")
  // Works for both forward and backward slashes
  const filename = path.split(/[/\\]/).filter(Boolean).pop();

  if (filename) {
    try {
      // staticFile() expects a path relative to the public/ folder.
      // Since Colab mirrors everything to the root of public/,
      // providing just the filename is correct.
      const resolved = staticFile(filename);
      console.log(`[ASSET_RESOLVE] "${path}" -> "${resolved}"`);
      return resolved;
    } catch (e) {
      console.error(`[ASSET_RESOLVE_ERROR] Failed for ${filename}:`, e);
    }
  }

  console.warn(`[ASSET_RESOLVE_FALLBACK] Returning original path: ${path}`);
  return path;
};
