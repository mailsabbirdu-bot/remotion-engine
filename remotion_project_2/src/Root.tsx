import React from 'react';
import { Composition, continueRender, delayRender, getInputProps } from 'remotion';
import { MainComposition } from './Composition';
import internalData from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

const inputProps = getInputProps();
const isUsingInputProps = !!inputProps.data;
const data = (inputProps.data as typeof internalData) || internalData;

console.log(`[ULTRA_DEBUG] Source: ${isUsingInputProps ? 'External (getInputProps)' : 'Internal (master_remotion.json)'}`);
console.log(`[ULTRA_DEBUG] Config Overview: FPS=${data.fps}, Resolution=${data.width}x${data.height}, Scenes=${(data.scenes || (data as any).Scenes || []).length}`);

if (data.scenes || (data as any).Scenes) {
    const debugScenes = data.scenes || (data as any).Scenes || [];
    debugScenes.forEach((s: any, i: number) => {
        const textLayer = (s.Layers || s.layers || []).find((l: any) => l.type === 'text');
        console.log(`[ULTRA_DEBUG] Scene ${i + 1}: ID=${s.Id || s.id}, Src=${s.src}, Text="${textLayer?.content?.substring(0, 30)}..."`);
    });
}

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
  const scenes = data.scenes || (data as any).Scenes || [];

  // Clean Finish Calculation: Total duration is simply the sum of all scene durations.
  // The transitions are now handled as extensions within TransitionHandler.
  const totalDuration = scenes.reduce((acc: number, scene: any) => {
    return acc + (scene.duration || 0);
  }, 0);

  return (
    <>
      <Composition
        id="Main"
        component={MainComposition as any}
        durationInFrames={Math.max(1, totalDuration)}
        fps={data.fps || 30}
        width={data.width || 1080}
        height={data.height || 1920}
        defaultProps={{
          data: {
            ...data,
            scenes: scenes
          } as any,
        }}
      />
    </>
  );
};
