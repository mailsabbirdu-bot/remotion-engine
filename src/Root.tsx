import React from 'react';
import { Composition, continueRender, delayRender, staticFile } from 'remotion';
import { MainComposition } from './Composition';
import data from './master_remotion.json';

// Handle font registration for Colab/Local environment
const waitForFont = delayRender('Loading Fonts');

const loadFonts = async () => {
  if (typeof window === 'undefined' || !('FontFace' in window)) {
    return;
  }

  const fonts = [
    { name: 'Audiowide', url: staticFile('fonts/Audiowide-Regular.ttf') },
    { name: 'Sohid Osman Hadi', url: staticFile('fonts/Sohid Osman Hadi.ttf') }
  ];

  try {
    await Promise.all(
      fonts.map(async (f) => {
        try {
          const ff = new FontFace(f.name, `url(${f.url})`);
          const loaded = await ff.load();
          document.fonts.add(loaded);
          console.log(`Font loaded: ${f.name}`);
        } catch (e) {
          console.warn(`Could not load font ${f.name} from ${f.url}. Falling back to system fonts.`);
        }
      })
    );
  } finally {
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
        component={MainComposition}
        durationInFrames={Math.max(1, totalDuration)}
        fps={data.fps}
        width={data.width}
        height={data.height}
        {...({
          component: MainComposition,
        } as any)}
        defaultProps={{
          data: data as any,
        }}
      />
    </>
  );
};
