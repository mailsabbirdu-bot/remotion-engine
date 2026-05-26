import React from 'react';
import { useCurrentFrame, interpolate, OffthreadVideo } from 'remotion';
import { getEasing, interpolateKeyframes } from '../utils/animation-utils';
import { WordByWordText, TextAnimationMode } from './WordByWordText';
import { TextBox } from './TextBox';
import { resolveAsset } from '../utils/path-utils';

export interface LayerData {
  id: string;
  type: 'text' | 'image' | 'video';
  content: string;
  start: number;
  duration: number;
  style: any;
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
}

export const Layer: React.FC<LayerProps> = ({ layer, banglaFontFamily, englishFontFamily }) => {
  const frame = useCurrentFrame();
  const { start, duration, animationIn, animationOut, keyframes, textAnimation } = layer;

  if (frame < start || frame >= start + duration) return null;

  const localFrame = frame - start;

  // In Animation
  let opacity = 1;
  let translateY = 0;
  let scale = 1;

  const animInDuration = animationIn?.duration ?? 15;
  if (animationIn && localFrame < animInDuration) {
    opacity = interpolate(localFrame, [0, animInDuration], [0, 1], {
      easing: getEasing(animationIn.easing),
      extrapolateRight: 'clamp',
    });
    if (animationIn.type === 'fade-up') {
      translateY = interpolate(localFrame, [0, animInDuration], [50, 0], {
        easing: getEasing(animationIn.easing),
      });
    }
  }

  // Out Animation
  const animOutDuration = animationOut?.duration ?? 15;
  const outStart = duration - animOutDuration;
  if (animationOut && localFrame >= outStart) {
    const outProgress = localFrame - outStart;
    const outOpacity = interpolate(outProgress, [0, animOutDuration], [1, 0], {
      easing: getEasing(animationOut.easing),
      extrapolateRight: 'clamp',
    });
    opacity *= outOpacity;
    if (animationOut.type === 'fade-down') {
      translateY = interpolate(outProgress, [0, animOutDuration], [0, 50], {
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

  const containerStyle: React.CSSProperties = {
    position: 'absolute',
    left: layer.style.x ?? '50%',
    top: layer.style.y ?? '50%',
    transform: `translate(-50%, -50%) translate(0, ${translateY}px) scale(${scale})`,
    opacity,
  };

  return (
    <div style={containerStyle}>
      {layer.type === 'text' && (
        <TextBox
          type={layer.textbox?.enabled ? (layer.textbox.type || 'rounded-rect') : 'none'}
          fill={layer.textbox?.fill}
          color={(layer.textbox as any)?.color}
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
    </div>
  );
};
