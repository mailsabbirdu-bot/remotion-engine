import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * We extract the filename and use staticFile().
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';

  if (path.startsWith('http') || path.startsWith('data:')) {
    return path;
  }

  // Aggressively extract filename
  const parts = path.split(/[/\\]/);
  const filename = parts[parts.length - 1];

  if (filename) {
    try {
      // staticFile() is the standard way to reference files in the public/ folder.
      let resolved = staticFile(filename);

      // Ensure the URL is absolute relative to the host
      if (!resolved.startsWith('/') && !resolved.startsWith('http')) {
        resolved = '/' + resolved;
      }

      console.log(`[ASSET_RESOLVE] "${path}" -> "${resolved}"`);
      return resolved;
    } catch (e) {
      console.error(`[ASSET_RESOLVE_ERROR] Failed for ${filename}:`, e);
      return `/${filename}`;
    }
  }

  return path;
};
