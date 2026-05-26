import React from 'react';
import { Composition, continueRender, delayRender, getInputProps } from 'remotion';
import { MainComposition } from './Composition';
import { SceneComposition } from './SceneComposition';
import internalData from './master_remotion.json';
import { resolveAsset } from './utils/path-utils';

const inputProps = getInputProps();
const data = (inputProps.data as typeof internalData) || internalData;

// Handle font registration
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

  try {
    await Promise.all(
      fontsToLoad.map(async (f) => {
        try {
          const safeUrl = f.url.includes('%') ? f.url : encodeURI(f.url);
          const fontFace = new FontFace(f.name, `url("${safeUrl}")`);
          const loadedFace = await fontFace.load();
          document.fonts.add(loadedFace);
        } catch (e) {
          console.error(`[FONT_SYSTEM] FAILED to load font "${f.name}":`, e);
        }
      })
    );
  } finally {
    continueRender(waitForFont);
  }
};

loadFonts();

export const RemotionRoot: React.FC = () => {
  const scenes = data.scenes || (data as any).Scenes || [];

  return (
    <>
      {/* Legacy Main Composition */}
      <Composition
        id="Main"
        component={MainComposition as any}
        durationInFrames={Math.max(1, scenes.reduce((acc: number, s: any) => acc + (s.duration || 0), 0))}
        fps={data.fps || 30}
        width={data.width || 1080}
        height={data.height || 1920}
        defaultProps={{
          data: { ...data, scenes } as any,
        }}
      />

      {/* Individual Scene Compositions for Overlays */}
      {scenes.map((scene: any, index: number) => {
        const rawId = scene.Id || scene.id || `scene-${index + 1}`;
        const sceneId = rawId.replace(/_/g, '-');
        return (
          <Composition
            key={sceneId}
            id={sceneId}
            component={SceneComposition as any}
            durationInFrames={Math.max(1, scene.duration || 30)}
            fps={data.fps || 30}
            width={data.width || 1080}
            height={data.height || 1920}
            defaultProps={{
              scene,
              banglaFontFamily: data.banglaFont,
              englishFontFamily: data.englishFont,
            }}
          />
        );
      })}
    </>
  );
};
