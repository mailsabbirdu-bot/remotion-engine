import React from 'react';
import { Composition, continueRender, delayRender, getInputProps } from 'remotion';
import { MainComposition } from './Composition';
import internalData from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

const inputProps = getInputProps();
const data = (inputProps.data as any) || internalData;

const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  if (typeof window === 'undefined' || !('FontFace' in window)) {
    continueRender(waitForFont);
    return;
  }

  const fontsToLoad = [
    { name: data.englishFont, url: data.englishFont ? resolveAsset(`${data.englishFont}.ttf`) : null },
    { name: data.banglaFont, url: data.banglaFont ? resolveAsset(`${data.banglaFont}.ttf`) : null }
  ].filter(f => f.name && f.url);

  console.log(`[FONT_SYSTEM] Blueprint: English="${data.englishFont}", Bangla="${data.banglaFont}"`);

  try {
    await Promise.all(
      fontsToLoad.map(async (f) => {
        try {
          const fontFace = new FontFace(f.name!, `url("${f.url}")`);
          const loadedFace = await fontFace.load();
          document.fonts.add(loadedFace);
          console.log(`[FONT_SYSTEM] SUCCESS: Loaded "${f.name}"`);
        } catch (e) {
          console.error(`[FONT_SYSTEM] FAILED: "${f.name}" at ${f.url}`, e);
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

  const totalDuration = scenes.reduce((acc: number, scene: any, index: number) => {
    const transitionDuration = (index < scenes.length - 1) ? (scene.transition?.duration || 0) : 0;
    return acc + (scene.duration || 0) - transitionDuration;
  }, 0);

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
