import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL.
 * It strictly uses only the filename to find assets in the 'public' folder.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';

  if (path.startsWith('http') || path.startsWith('data:')) {
    return path;
  }

  // Extract filename only (removes directory paths)
  const filename = path.split(/[/\\]/).pop() || path;

  try {
    // staticFile(filename) returns the URL for the file in the public folder.
    // In Remotion 4.x, this is typically /filename
    const resolved = staticFile(filename);

    // Ensure absolute path for the web server
    return resolved.startsWith('/') || resolved.startsWith('http') ? resolved : `/${resolved}`;
  } catch (e) {
    console.error(`[ASSET_RESOLVE_ERROR] Failed for "${filename}":`, e);
    return `/${filename}`;
  }
};
