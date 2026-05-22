import React from 'react';
import { Composition, continueRender, delayRender, getInputProps, staticFile } from 'remotion';
import { MainComposition } from './Composition';
import internalData from './master_remotion.json';

const inputProps = getInputProps();
const data = (inputProps.data as any) || internalData;

const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  if (typeof window === 'undefined' || !('FontFace' in window)) {
    continueRender(waitForFont);
    return;
  }

  const resolveAsset = (path: string) => {
    if (path.startsWith('http') || path.startsWith('data:')) return path;
    return staticFile(path);
  };

  const fontsToLoad = [
    { name: data.englishFont, url: data.englishFont ? resolveAsset(`${data.englishFont}.ttf`) : null },
    { name: data.banglaFont, url: data.banglaFont ? resolveAsset(`${data.banglaFont}.ttf`) : null }
  ].filter(f => f.name && f.url);

  try {
    await Promise.all(
      fontsToLoad.map(async (f) => {
        try {
          const fontFace = new FontFace(f.name!, `url("${f.url}")`);
          const loadedFace = await fontFace.load();
          document.fonts.add(loadedFace);
          console.log(`[FONT_SYSTEM] Loaded: ${f.name}`);
        } catch (e) {
          console.error(`[FONT_SYSTEM] Failed to load: ${f.name}`, e);
        }
      })
    );
  } finally {
    continueRender(waitForFont);
  }
};

loadFonts();

export const RemotionRoot: React.FC = () => {
  const scenes = data.scenes || [];

  // Total Duration Calculation:
  // Remotion's <TransitionSeries> works by overlapping sequences.
  // Duration = Sum(scenes.duration) - Sum(transitions.duration)
  const totalDuration = scenes.reduce((acc: number, scene: any, index: number) => {
    const transitionDuration = (index < scenes.length - 1) ? (scene.transition?.duration || 0) : 0;
    return acc + (scene.duration || 0) - transitionDuration;
  }, 0);

  // Fallback if no scenes
  const finalDuration = Math.max(1, totalDuration || 100);

  return (
    <>
      <Composition
        id="Main"
        component={MainComposition as any}
        durationInFrames={finalDuration}
        fps={data.fps || 30}
        width={data.width || 1080}
        height={data.height || 1920}
        defaultProps={{
          data: data,
        }}
      />
    </>
  );
};
