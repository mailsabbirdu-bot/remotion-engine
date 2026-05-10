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
  const parts = path.split(/[/\\]/).filter(p => p.length > 0);
  const filename = parts[parts.length - 1];

  if (filename) {
    try {
      // staticFile() is the recommended way to reference files in the public/ folder.
      // It returns a path that works in both Studio and during Render.
      const resolved = staticFile(filename);

      // Log for debugging (will show up in Remotion logs)
      console.log(`[ASSET_RESOLVE] "${path}" -> "${resolved}"`);

      return resolved;
    } catch (e) {
      console.error(`[ASSET_RESOLVE_ERROR] Failed to resolve ${filename}:`, e);
      return filename;
    }
  }

  return path;
};
