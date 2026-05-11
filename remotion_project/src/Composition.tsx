import React from 'react';
import { AbsoluteFill } from 'remotion';
import { TransitionHandler } from './components/TransitionHandler';
import { SceneData } from './components/Scene';

interface MainCompositionProps {
  data: {
    scenes: SceneData[];
    banglaFont: string;
    englishFont: string;
  };
}

export const MainComposition: React.FC<MainCompositionProps> = ({ data }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      <TransitionHandler
        scenes={data.scenes}
        banglaFontFamily={data.banglaFont}
        englishFontFamily={data.englishFont}
      />
    </AbsoluteFill>
  );
};
