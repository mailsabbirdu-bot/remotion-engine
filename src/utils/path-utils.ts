import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * Specifically handles Google Drive absolute paths in Colab.
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // If it's a Colab Google Drive path, we expect a symlink at public/drive -> /content/drive/MyDrive
  if (path.includes('/drive/MyDrive/')) {
    const relativePart = path.split('/drive/MyDrive/')[1];
    return staticFile(`drive/${relativePart}`);
  }

  // Fallback for other paths
  return path.startsWith('/') ? staticFile(path) : path;
};
