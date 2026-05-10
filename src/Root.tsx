import React from 'react';
import { Composition, continueRender, delayRender } from 'remotion';
import { MainComposition } from './Composition';
import data from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

// Handle font registration for Colab/Local environment
const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  if (typeof window === 'undefined' || !('FontFace' in window)) {
    continueRender(waitForFont);
    return;
  }

  const getFontUrl = (name: string) => {
    if (!name) return '';
    // If it already has an extension, use it as is
    if (/\.(ttf|otf|woff2?)$/i.test(name)) {
      return resolveAsset(name);
    }
    // Default to .ttf if no extension provided
    return resolveAsset(`${name}.ttf`);
  };

  // Dynamically determine fonts from master_remotion.json
  const fonts = [
    {
      name: data.englishFont,
      url: getFontUrl(data.englishFont)
    },
    {
      name: data.banglaFont,
      url: getFontUrl(data.banglaFont)
    }
  ];

  try {
    await Promise.all(
      fonts.map(async (f) => {
        if (!f.url) return;
        try {
          console.log(`[FONT_DEBUG] Attempting to load: "${f.name}" from "${f.url}"`);
          const ff = new FontFace(f.name, `url("${f.url}")`);
          const loaded = await ff.load();
          document.fonts.add(loaded);
          console.log(`[FONT_DEBUG] Successfully loaded: "${f.name}"`);
        } catch (e) {
          console.error(`[FONT_DEBUG_ERROR] Could not load font "${f.name}" from "${f.url}":`, e);
        }
      })
    );
  } catch (err) {
    console.error("[FONT_LOAD_CRITICAL_ERROR]", err);
  } finally {
    // Always continue render even if some fonts failed (will fallback to system fonts)
    continueRender(waitForFont);
  }
};

loadFonts();

export const RemotionRoot: React.FC = () => {
  // Calculate total duration based on scenes and transitions
  const totalDuration = data.scenes.reduce((acc, scene, index) => {
    const transitionOverlap = index < data.scenes.length - 1 ? (scene.transition?.duration || 0) : 0;
    return acc + scene.duration - transitionOverlap;
  }, 0);

  return (
    <>
      <Composition
        id="Main"
        component={MainComposition as any}
        durationInFrames={Math.max(1, totalDuration)}
        fps={data.fps}
        width={data.width}
        height={data.height}
        defaultProps={{
          data: data as any,
        }}
      />
    </>
  );
};
