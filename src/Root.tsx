import React from 'react';
import { Composition } from 'remotion';
import { MainComposition } from './Composition';
import data from './master_remotion.json';

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
        schema={undefined}
        calculateMetadata={undefined}
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
