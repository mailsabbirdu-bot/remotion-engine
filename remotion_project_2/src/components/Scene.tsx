import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo } from 'remotion';
import { Layer, LayerData } from './Layer';
import { resolveAsset } from '../utils/path-utils';

export interface SceneData {
  id?: string;
  Id?: string; // Support for capitalized Id
  duration: number;
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
}

export const Scene: React.FC<SceneProps> = ({ scene, banglaFontFamily, englishFontFamily }) => {
  const layers = scene.Layers || scene.layers || [];
  const id = scene.Id || scene.id || 'scene';

  React.useEffect(() => {
    console.log(`[ULTRA_DEBUG] [SCENE_MOUNT] ID=${id}, Duration=${scene.duration}f, Assets=[BG:${scene.background.src}, Audio:${scene.background.audio || 'none'}]`);
    layers.forEach((l, i) => {
      if (l.type === 'text') {
        console.log(`[ULTRA_DEBUG] [LAYER_TEXT] Scene=${id}, Layer=${i}, Content="${l.content?.substring(0, 50)}..."`);
      }
    });
  }, [id, scene.duration, scene.background.src, scene.background.audio, layers]);

  return (
    <AbsoluteFill>
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
