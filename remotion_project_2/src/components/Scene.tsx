import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Freeze, useCurrentFrame } from 'remotion';
import { Layer, LayerData } from './Layer';
import { resolveAsset } from '../utils/path-utils';

export interface SceneData {
  id?: string;
  Id?: string; // Support for capitalized Id
  duration: number;
  contentDuration?: number; // Raw video duration
  videoDuration?: number; // Actual physical length of video asset
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
}

export const Scene: React.FC<SceneProps> = ({ scene, banglaFontFamily, englishFontFamily }) => {
  const frame = useCurrentFrame();
  const layers = scene.Layers || scene.layers || [];
  const id = scene.Id || scene.id || 'scene';

  // "Clean Finish" frame calculation:
  // 1. We determine the 'real' clock for this scene by subtracting the transition offset.
  // 2. We use 'videoDuration' (physical file length) if available, otherwise fallback to contentDuration.
  // 3. If the video is shorter than the intended scene duration, we freeze it at its last frame.
  const offset = scene.offset || 0;
  const videoLimit = scene.videoDuration || scene.contentDuration || scene.duration;
  const activeFrame = Math.min(Math.max(0, frame - offset), videoLimit - 1);

  const contentDuration = scene.contentDuration || scene.duration;
  React.useEffect(() => {
    console.log(`[ULTRA_DEBUG] [SCENE_MOUNT] ID=${id}, Offset=${offset}, Content=${contentDuration}, Total=${scene.duration}f`);
  }, [id, scene.duration, contentDuration, offset]);

  return (
    <AbsoluteFill>
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
