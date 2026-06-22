import React from 'react';
import { useCurrentFrame, interpolate, OffthreadVideo } from 'remotion';
import { getEasing, interpolateKeyframes } from '../utils/animation-utils';
import { WordByWordText, TextAnimationMode } from './WordByWordText';
import { TextBox } from './TextBox';
import { resolveAsset } from '../utils/path-utils';
import { useCamera } from './CameraContext';

export interface LayerData {
  id: string;
  type: 'text' | 'image' | 'video' | 'shape';
  content: string;
  start: number;
  duration: number;
  style: any;
  depth?: number;
  animationIn?: {
    type: string;
    duration: number;
    easing?: string;
  };
  animationOut?: {
    type: string;
    duration: number;
    easing?: string;
  };
  keyframes?: { frame: number; scale?: number; opacity?: number; x?: number; y?: number; easing?: string }[];
  textbox?: {
    enabled: boolean;
    type: 'rounded-rect' | 'rect' | 'none';
    padding?: number;
    fill?: string;
  };
  textAnimation?: {
    mode?: TextAnimationMode;
    duration?: number;
  };
}

interface LayerProps {
  layer: LayerData;
  banglaFontFamily: string;
  englishFontFamily: string;
  debug?: boolean;
}

export const Layer: React.FC<LayerProps> = ({ layer, banglaFontFamily, englishFontFamily, debug }) => {
  const frame = useCurrentFrame();
  const camera = useCamera();
  const { start, duration, animationIn, animationOut, keyframes, textAnimation, depth = 1.0 } = layer;

  if (frame < start || frame >= start + duration) return null;

  const localFrame = frame - start;

  // In Animation
  let opacity = 1;
  let translateY = 0;
  let scale = 1;

  if (animationIn && localFrame < animationIn.duration) {
    opacity = interpolate(localFrame, [0, animationIn.duration], [0, 1], {
      easing: getEasing(animationIn.easing),
      extrapolateRight: 'clamp',
    });
    if (animationIn.type === 'fade-up') {
      translateY = interpolate(localFrame, [0, animationIn.duration], [50, 0], {
        easing: getEasing(animationIn.easing),
      });
    }
  }

  // Out Animation
  const outStart = duration - (animationOut?.duration || 0);
  if (animationOut && localFrame >= outStart) {
    const outProgress = localFrame - outStart;
    const outOpacity = interpolate(outProgress, [0, animationOut.duration], [1, 0], {
      easing: getEasing(animationOut.easing),
      extrapolateRight: 'clamp',
    });
    opacity *= outOpacity;
    if (animationOut.type === 'fade-down') {
      translateY = interpolate(outProgress, [0, animationOut.duration], [0, 50], {
        easing: getEasing(animationOut.easing),
      });
    }
  }

  // Keyframes
  if (keyframes) {
    const kOpacity = interpolateKeyframes(localFrame, keyframes.filter(k => k.opacity !== undefined).map(k => ({frame: k.frame, value: k.opacity!, easing: k.easing})), 1);
    const kScale = interpolateKeyframes(localFrame, keyframes.filter(k => k.scale !== undefined).map(k => ({frame: k.frame, value: k.scale!, easing: k.easing})), 1);
    opacity *= kOpacity;
    scale *= kScale;
  }

  // Parallax Depth Logic:
  // Offset = (1 - depth) * camera_movement
  // If depth = 1.0 (on the plane), offset = 0.
  // If depth = 0.3 (far away), it moves 0.7x of camera.
  // If depth = 1.5 (very close), it moves -0.5x of camera.
  const offsetX = (1 - depth) * camera.x;
  const offsetY = (1 - depth) * camera.y;

  const containerStyle: React.CSSProperties = {
    position: 'absolute',
    left: (layer.style.x ?? 0) + offsetX,
    top: (layer.style.y ?? 0) + offsetY,
    transform: `translate(-50%, -50%) translate(0, ${translateY}px) scale(${scale})`,
    opacity,
    zIndex: Math.round(depth * 100),
  };

  return (
    <div style={containerStyle}>
      {layer.type === 'text' && (
        <TextBox
          type={layer.textbox?.enabled ? (layer.textbox.type || 'rounded-rect') : 'none'}
          fill={layer.textbox?.fill}
          padding={layer.textbox?.padding}
        >
          <WordByWordText
            text={layer.content}
            style={{
               fontSize: layer.style.fontSize || 40,
               color: layer.style.color || '#fff',
               textAlign: 'center'
            }}
            banglaFontFamily={banglaFontFamily}
            englishFontFamily={englishFontFamily}
            duration={textAnimation?.duration ?? (layer.duration / 2)}
            animationMode={textAnimation?.mode || 'word'}
          />
        </TextBox>
      )}
      {layer.type === 'image' && (
        <img src={resolveAsset(layer.content)} style={{ width: layer.style.width || 'auto', height: layer.style.height || 'auto' }} alt="" />
      )}
      {layer.type === 'video' && (
        <OffthreadVideo src={resolveAsset(layer.content)} style={{ width: layer.style.width || 'auto', height: layer.style.height || 'auto' }} />
      )}
      {layer.type === 'shape' && (
        <div style={{
          width: layer.style.width || 100,
          height: layer.style.height || 100,
          borderRadius: layer.style.borderRadius || 0,
          background: layer.style.background || 'white',
          border: layer.style.border || 'none',
        }} />
      )}

      {debug && (
        <div style={{
          position: 'absolute',
          top: -20,
          left: 0,
          backgroundColor: 'rgba(0,0,255,0.7)',
          color: 'white',
          fontSize: '10px',
          padding: '2px',
          whiteSpace: 'nowrap',
          pointerEvents: 'none'
        }}>
          {layer.id} | D:{depth} | X:{Math.round(layer.style.x)} Y:{Math.round(layer.style.y)}
        </div>
      )}
    </div>
  );
};
