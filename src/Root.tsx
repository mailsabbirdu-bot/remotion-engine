import React from 'react';
import { Composition, continueRender, delayRender } from 'remotion';
import { MainComposition } from './Composition';
import data from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

// Handle font registration for Colab/Local environment
const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  // SSR check
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
  // We use the names from JSON as the font-family identifiers
  const fontsToLoad = [
    {
      type: 'English',
      name: data.englishFont,
      url: getFontUrl(data.englishFont)
    },
    {
      type: 'Bangla',
      name: data.banglaFont,
      url: getFontUrl(data.banglaFont)
    }
  ].filter(f => f.name && f.url);

  console.log(`[FONT_SYSTEM] Blueprint requested English: "${data.englishFont}", Bangla: "${data.banglaFont}"`);

  try {
    await Promise.all(
      fontsToLoad.map(async (f) => {
        try {
          console.log(`[FONT_SYSTEM] [${f.type}] Attempting to load font-face "${f.name}" from "${f.url}"`);
          const fontFace = new FontFace(f.name, `url("${f.url}")`);
          const loadedFace = await fontFace.load();
          document.fonts.add(loadedFace);
          console.log(`[FONT_SYSTEM] [${f.type}] SUCCESS: Font-face "${f.name}" registered and ready.`);
        } catch (e) {
          console.error(`[FONT_SYSTEM] [${f.type}] FAILED to load "${f.name}" from "${f.url}":`, e);
          console.warn(`[FONT_SYSTEM] [${f.type}] The engine will try to use system fallbacks for "${f.name}".`);
        }
      })
    );
  } catch (err) {
    console.error("[FONT_SYSTEM] CRITICAL ERROR during font loading process:", err);
  } finally {
    // Crucial: Always allow rendering to proceed even if fonts fail
    continueRender(waitForFont);
  }
};

// Fire and forget, the delayRender handles the sync
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
