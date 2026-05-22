import { staticFile } from 'remotion';

/**
 * Robustly resolves an asset path to a URL.
 * Extracts the filename to ensure it works even if full paths are provided in JSON.
 * Normalizes the URL to prevent double /public/ or missing leading slashes.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';

  if (path.startsWith('http') || path.startsWith('data:')) {
    return path;
  }

  // Extract just the filename (e.g., "C:\path\to\scene.mp4" -> "scene.mp4")
  const filename = path.split(/[/\\]/).pop() || path;

  try {
    // staticFile() handles the public/ folder mapping
    const resolved = staticFile(filename);

    // Normalize: Ensure starts with / and doesn't have double /public/
    // Remotion 4.0 staticFile('a.mp4') might return 'a.mp4' or '/a.mp4' or 'public/a.mp4'
    let url = resolved;

    // Remove leading / if present for easier manipulation
    url = url.replace(/^\//, '');

    // Remove public/ prefix if it returned it (common in some renderer configs)
    url = url.replace(/^public\//, '');

    // Final absolute URL
    return `/${url}`;
  } catch (e) {
    console.error(`[RESOLVE_ASSET_ERROR] ${filename}:`, e);
    return `/${filename}`;
  }
};
