import React from 'react';
import { Composition, continueRender, delayRender, getInputProps } from 'remotion';
import { MainComposition } from './Composition';
import internalData from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

const inputProps = getInputProps();
const data = (inputProps.data as typeof internalData) || internalData;

// Handle font registration for Colab/Local environment
const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  if (typeof window === 'undefined' || !('FontFace' in window)) {
    continueRender(waitForFont);
    return;
  }

  const getFontUrl = (name: string) => {
    if (!name) return '';
    if (/\.(ttf|otf|woff2?)$/i.test(name)) {
      return resolveAsset(name);
    }
    return resolveAsset(`${name}.ttf`);
  };

  const fontsToLoad = [
    { type: 'English', name: data.englishFont, url: getFontUrl(data.englishFont) },
    { type: 'Bangla', name: data.banglaFont, url: getFontUrl(data.banglaFont) }
  ].filter(f => f.name && f.url);

  console.log(`[FONT_SYSTEM] Blueprint Config: English="${data.englishFont}", Bangla="${data.banglaFont}"`);

  try {
    await Promise.all(
      fontsToLoad.map(async (f) => {
        try {
          // Encode spaces for URL
          const safeUrl = f.url.includes('%') ? f.url : encodeURI(f.url);
          console.log(`[FONT_SYSTEM] [${f.type}] Attempting registration: Name="${f.name}", URL="${safeUrl}"`);

          const fontFace = new FontFace(f.name, `url("${safeUrl}")`);
          const loadedFace = await fontFace.load();
          document.fonts.add(loadedFace);

          console.log(`[FONT_SYSTEM] [${f.type}] SUCCESS: Font-face "${f.name}" is now available in the document.`);
        } catch (e) {
          console.error(`[FONT_SYSTEM] [${f.type}] FAILED to load font "${f.name}":`, e);
        }
      })
    );
  } catch (err) {
    console.error("[FONT_SYSTEM] CRITICAL ERROR during font loading:", err);
  } finally {
    continueRender(waitForFont);
  }
};

loadFonts();

export const RemotionRoot: React.FC = () => {
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
