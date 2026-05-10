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

  // Define fonts as per master_remotion.json requirements
  const fonts = [
    { name: 'Audiowide', url: resolveAsset('Audiowide-Regular.ttf') },
    { name: 'Sohid Osman Hadi', url: resolveAsset('Sohid Osman Hadi.ttf') }
  ];

  try {
    await Promise.all(
      fonts.map(async (f) => {
        try {
          console.log(`[FONT_DEBUG] Loading font: ${f.name} from ${f.url}`);
          const ff = new FontFace(f.name, `url("${f.url}")`);
          const loaded = await ff.load();
          document.fonts.add(loaded);
          console.log(`[FONT_DEBUG] Successfully loaded font: ${f.name}`);
        } catch (e) {
          console.error(`[FONT_DEBUG_ERROR] Could not load font ${f.name} from ${f.url}:`, e);
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
