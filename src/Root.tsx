import React from 'react';
import { Composition, continueRender, delayRender, staticFile } from 'remotion';
import { MainComposition } from './Composition';
import data from './master_remotion.json';

// Handle font registration for Colab/Local environment
const waitForFont = delayRender('Loading Fonts');
if (typeof window !== 'undefined' && 'FontFace' in window) {
  const fonts = [
    { name: 'Audiowide', url: staticFile('fonts/Audiowide-Regular.ttf') },
    { name: 'Sohid Osman Hadi', url: staticFile('fonts/Sohid Osman Hadi.ttf') }
  ];

  Promise.all(
    fonts.map(f => {
      const ff = new FontFace(f.name, `url(${f.url})`);
      return ff.load().then(loaded => {
        document.fonts.add(loaded);
      });
    })
  ).then(() => {
    continueRender(waitForFont);
  }).catch(err => {
    console.error("Font loading failed", err);
    continueRender(waitForFont);
  });
} else {
  continueRender(waitForFont);
}

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
        // Use any to bypass strict type checking for the component prop in Root
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
