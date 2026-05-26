import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Freeze, useCurrentFrame } from 'remotion';
import { Layer, LayerData } from './Layer';
import { resolveAsset } from '../utils/path-utils';

export interface SceneData {
  id?: string;
  Id?: string; // Support for capitalized Id
  duration: number;
  contentDuration?: number; // Raw video duration
  offset?: number; // Start offset due to previous transition
  background: {
    type: 'video' | 'image' | 'color';
    src: string;
    audio?: string;
  };
  layers?: LayerData[];
  Layers?: LayerData[]; // Support for capitalized Layers
  transition?: {
    type: string;
    duration: number;
  };
}

interface SceneProps {
  scene: SceneData;
  banglaFontFamily: string;
  englishFontFamily: string;
  showBackground?: boolean;
}

export const Scene: React.FC<SceneProps> = ({
  scene,
  banglaFontFamily,
  englishFontFamily,
  showBackground = true
}) => {
  const frame = useCurrentFrame();
  const layers = scene.Layers || scene.layers || [];
  const id = scene.Id || scene.id || 'scene';

  // "Clean Finish" frame calculation:
  const offset = scene.offset || 0;
  const contentDuration = scene.contentDuration || scene.duration;
  const activeFrame = Math.min(Math.max(0, frame - offset), contentDuration - 1);

  return (
    <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
      {showBackground && (
        <Freeze frame={activeFrame}>
          {scene.background.type === 'video' && (
            <OffthreadVideo
              src={resolveAsset(scene.background.src)}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          )}
          {scene.background.type === 'image' && (
            <img
              src={resolveAsset(scene.background.src)}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              alt=""
            />
          )}
          {scene.background.type === 'color' && (
            <div style={{ width: '100%', height: '100%', backgroundColor: scene.background.src }} />
          )}

          {scene.background.audio && <Audio src={resolveAsset(scene.background.audio)} />}
        </Freeze>
      )}

      {layers.map((layer, index) => (
        <Layer
          key={`${id}-layer-${index}`}
          layer={layer}
          banglaFontFamily={banglaFontFamily}
          englishFontFamily={englishFontFamily}
        />
      ))}
    </AbsoluteFill>
  );
};
