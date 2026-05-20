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
        const prevTransitionDuration = index > 0 ? (scenes[index - 1].transition?.duration || 0) : 0;
        const nextTransitionDuration = (index < scenes.length - 1) ? (scene.transition?.duration || 0) : 0;

        // The original 'scene.duration' is the intended CONTENT length.
        // The sequence duration must include both overlap margins.
        const sequenceDuration = prevTransitionDuration + scene.duration + nextTransitionDuration;

        const layers = scene.Layers || scene.layers || [];
        const shiftedLayers = layers.map(layer => {
          // 1. Shift the start time by the previous transition duration.
          // This ensures that 'start: 0' layers begin AFTER the fade-in from the previous scene.
          const newStart = layer.start + prevTransitionDuration;

          // 2. Extend full-scene layers to cover the "Tail" transition.
          // This ensures textboxes stay visible until the fade-out is complete.
          let newDuration = layer.duration;
          if (layer.duration >= scene.duration - 1) {
             newDuration = scene.duration + nextTransitionDuration;
          }

          return { ...layer, start: newStart, duration: newDuration };
        });

        return (
          <React.Fragment key={scene.Id || scene.id || `scene-${index}`}>
            <TransitionSeries.Sequence durationInFrames={sequenceDuration}>
              <Scene
                scene={{
                  ...scene,
                  duration: sequenceDuration,
                  contentDuration: scene.duration,
                  offset: prevTransitionDuration,
                  layers: shiftedLayers,
                  Layers: shiftedLayers
                }}
                banglaFontFamily={banglaFontFamily}
                englishFontFamily={englishFontFamily}
              />
            </TransitionSeries.Sequence>
            {nextTransitionDuration > 0 && (
                <TransitionSeries.Transition
                    presentation={fade()}
                    timing={linearTiming({ durationInFrames: nextTransitionDuration })}
                />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};
