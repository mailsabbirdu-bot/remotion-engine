import React from 'react';
import { AbsoluteFill } from 'remotion';
import { TransitionHandler } from './components/TransitionHandler';

export const MainComposition: React.FC<{ data: any }> = ({ data }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      <TransitionHandler
        scenes={data.scenes || []}
        banglaFont={data.banglaFont}
        englishFont={data.englishFont}
      />
    </AbsoluteFill>
  );
};
