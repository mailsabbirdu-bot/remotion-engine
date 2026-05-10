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
  // We handle both forward and backslashes, and then take the last part.
  const parts = path.split(/[/\\]/);
  const filename = parts.pop() || '';

  if (filename) {
    try {
      // staticFile() is the recommended way to reference files in the public/ folder.
      // In Remotion 4.0+, it will return the correct path to the asset in the public folder.
      const resolved = staticFile(filename);

      // Explicitly log for debugging in the browser console
      console.log(`[RESOLVE] Input: "${path}" -> Filename: "${filename}" -> Output: "${resolved}"`);

      return resolved;
    } catch (e) {
      console.error(`[RESOLVE_ERROR] Failed for ${filename}:`, e);
      return `/${filename}`; // Fallback to root-relative
    }
  }

  return path;
};
