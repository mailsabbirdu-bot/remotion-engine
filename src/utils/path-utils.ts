import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * We aggressively strip all path segments to extract only the filename,
 * and then use staticFile() to get the correct URL for the bundled environment.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';

  // If it's already a full URL or data URI, return as is
  if (path.startsWith('http') || path.startsWith('data:')) {
    return path;
  }

  // Extract only the filename (e.g. "my-video.mp4" from "/any/complex/path/my-video.mp4")
  const filename = path.split(/[/\\]/).pop() || '';

  if (filename) {
    try {
      // staticFile() is the standard Remotion way to reference files in the public/ folder.
      let resolved = staticFile(filename);

      /**
       * CRITICAL FIX:
       * In some environments, staticFile might return a path starting with '/public/'.
       * However, Remotion's asset server serves the public folder contents at the root.
       * Attempting to fetch '/public/file.ttf' often results in a 404 because the file
       * is actually at '/file.ttf' or '/static/file.ttf'.
       */
      if (resolved.startsWith('/public/')) {
        resolved = resolved.replace('/public/', '/');
      }

      // Ensure it starts with a slash if it's a relative-looking path
      if (!resolved.startsWith('/') && !resolved.startsWith('http')) {
        resolved = '/' + resolved;
      }

      console.log(`[RESOLVE] Input: "${path}" -> Output: "${resolved}"`);
      return resolved;
    } catch (e) {
      console.error(`[RESOLVE_ERROR] Failed for ${filename}:`, e);
      return `/${filename}`; // Desperate fallback
    }
  }

  return path;
};
