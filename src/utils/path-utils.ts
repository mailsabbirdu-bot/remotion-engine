import { staticFile } from 'remotion';

/**
 * Resolves an asset path to a URL that Remotion can handle.
 * We rely on the Colab script to have copied Drive assets into public/assets/
 */
export const resolveAsset = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;

  // Extract the filename from the path (e.g., scene_1.mp4)
  const filename = path.split('/').pop();

  // If the path looks like a media file, we try to find it in our mirrored assets folder
  if (path.match(/\.(mp4|mov|m4v|png|jpg|jpeg|wav|mp3|ttf)$/i) && filename) {
      return staticFile(`assets/${filename}`);
  }

  // Fallback: use the path as-is relative to the public folder
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;
  return staticFile(normalizedPath);
};
