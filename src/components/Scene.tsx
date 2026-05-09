import React from 'react';
import { AbsoluteFill, Video, Audio, OffthreadVideo } from 'remotion';
import { Layer, LayerData } from './Layer';

export interface SceneData {
  id: string;
  duration: number;
  background: {
    type: 'video' | 'image' | 'color';
    src: string;
    audio?: string;
  };
  layers: LayerData[];
  transition?: {
    type: string;
    duration: number;
  };
}

interface SceneProps {
  scene: SceneData;
  banglaFontFamily: string;
  englishFontFamily: string;
}

export const Scene: React.FC<SceneProps> = ({ scene, banglaFontFamily, englishFontFamily }) => {
  return (
    <AbsoluteFill>
      {scene.background.type === 'video' && (
        <OffthreadVideo
          src={scene.background.src}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      )}
      {scene.background.type === 'image' && (
        <img
          src={scene.background.src}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          alt=""
        />
      )}
      {scene.background.type === 'color' && (
        <div style={{ width: '100%', height: '100%', backgroundColor: scene.background.src }} />
      )}

      {scene.background.audio && <Audio src={scene.background.audio} />}

      {scene.layers.map((layer) => (
        <Layer
          key={layer.id}
          layer={layer}
          banglaFontFamily={banglaFontFamily}
          englishFontFamily={englishFontFamily}
        />
      ))}
    </AbsoluteFill>
  );
};
