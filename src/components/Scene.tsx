import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo } from 'remotion';
import { Layer, LayerData } from './Layer';
import { resolveAsset } from '../utils/path-utils';
import { CameraRig } from './CameraRig';
import { CameraProvider } from './CameraContext';
import { CameraConfig } from './CameraRig'; // Although it's exported from CameraContext too now

export interface SceneData {
  id: string;
  duration: number;
  background: {
    type: 'video' | 'image' | 'color';
    src: string;
    audio?: string;
    zoom?: {
      start: number;
      end: number;
    };
  };
  layers: LayerData[];
  camera?: any; // Use any to avoid circularity if defined in multiple places
  debug_camera?: boolean;
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
      <div style={{ width: '100%', height: '100%' }}>
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
      </div>

      {scene.background.audio && <Audio src={resolveAsset(scene.background.audio)} />}

      <CameraProvider camera={scene.camera}>
        <CameraRig
          debug={scene.debug_camera}
          width={1920}
          height={1080}
        >
          {scene.layers.map((layer) => (
            <Layer
              key={layer.id}
              layer={layer}
              banglaFontFamily={banglaFontFamily}
              englishFontFamily={englishFontFamily}
              debug={scene.debug_camera}
            />
          ))}
        </CameraRig>
      </CameraProvider>
    </AbsoluteFill>
  );
};
