import React from 'react';
import { Scene, SceneData } from './Scene';
import { fade } from '@remotion/transitions/fade';
import { TransitionSeries, linearTiming } from '@remotion/transitions';

interface TransitionHandlerProps {
  scenes: SceneData[];
  banglaFontFamily: string;
  englishFontFamily: string;
}

export const TransitionHandler: React.FC<TransitionHandlerProps> = ({
  scenes,
  banglaFontFamily,
  englishFontFamily
}) => {
  return (
    <TransitionSeries>
      {scenes.map((scene, index) => {
        const transitionDuration = scene.transition?.duration || 0;

        return (
          <React.Fragment key={scene.Id || scene.id || `scene-${index}`}>
            <TransitionSeries.Sequence durationInFrames={scene.duration}>
              <Scene
                scene={scene}
                banglaFontFamily={banglaFontFamily}
                englishFontFamily={englishFontFamily}
              />
            </TransitionSeries.Sequence>
            {index < scenes.length - 1 && transitionDuration > 0 && (
                <TransitionSeries.Transition
                    presentation={fade()}
                    timing={linearTiming({ durationInFrames: transitionDuration })}
                />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};
