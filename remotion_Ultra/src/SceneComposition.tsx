import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Scene, SceneData } from './components/Scene';

interface SceneCompositionProps {
  scene: SceneData;
  banglaFontFamily: string;
  englishFontFamily: string;
}

export const SceneComposition: React.FC<SceneCompositionProps> = ({
  scene,
  banglaFontFamily,
  englishFontFamily
}) => {
  return (
    <AbsoluteFill>
      <Scene
        scene={scene}
        banglaFontFamily={banglaFontFamily}
        englishFontFamily={englishFontFamily}
        showBackground={false}
      />
    </AbsoluteFill>
  );
};
