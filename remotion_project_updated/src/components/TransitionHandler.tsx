import React from 'react';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { wipe } from '@remotion/transitions/wipe';
import { Scene } from './Scene';

interface TransitionHandlerProps {
  scenes: any[];
  banglaFont: string;
  englishFont: string;
}

export const TransitionHandler: React.FC<TransitionHandlerProps> = ({
  scenes,
  banglaFont,
  englishFont,
}) => {
  return (
    <TransitionSeries>
      {scenes.map((scene, index) => {
        const transition = scene.transition;
        const transitionDuration = transition?.duration || 0;

        let presentation: any = fade();
        if (transition?.type === 'slide') presentation = slide();
        if (transition?.type === 'wipe') presentation = wipe();

        const elements = [
          <TransitionSeries.Sequence key={`seq-${scene.id || index}`} durationInFrames={scene.duration}>
            <Scene
              data={scene}
              banglaFont={banglaFont}
              englishFont={englishFont}
            />
          </TransitionSeries.Sequence>
        ];

        if (index < scenes.length - 1 && transitionDuration > 0) {
          elements.push(
            <TransitionSeries.Transition
              key={`trans-${scene.id || index}`}
              presentation={presentation}
              timing={linearTiming({ durationInFrames: transitionDuration })}
            />
          );
        }

        return elements;
      }).flat()}
    </TransitionSeries>
  );
};
