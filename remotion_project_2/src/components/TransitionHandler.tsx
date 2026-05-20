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
        const transitionDuration = (index < scenes.length - 1) ? (scene.transition?.duration || 0) : 0;

        // "Clean Finish" logic: Extend the sequence duration by the transition duration
        // so the actual content plays fully before the overlap begins.
        const sequenceDuration = scene.duration + transitionDuration;

        // Automatically extend layers that were meant to last the full scene
        const layers = scene.Layers || scene.layers || [];
        const extendedLayers = layers.map(layer => {
          if (layer.duration >= scene.duration - 1) {
             return { ...layer, duration: sequenceDuration };
          }
          return layer;
        });

        return (
          <React.Fragment key={scene.Id || scene.id || `scene-${index}`}>
            <TransitionSeries.Sequence durationInFrames={sequenceDuration}>
              <Scene
                scene={{
                  ...scene,
                  duration: sequenceDuration,
                  layers: extendedLayers,
                  Layers: extendedLayers
                }}
                banglaFontFamily={banglaFontFamily}
                englishFontFamily={englishFontFamily}
              />
            </TransitionSeries.Sequence>
            {transitionDuration > 0 && (
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
