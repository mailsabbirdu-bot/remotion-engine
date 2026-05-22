import React from 'react';
import { useCurrentFrame, interpolate, staticFile } from 'remotion';
import { getEasing } from '../utils/animation-utils';

export const ImageLayer: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { start, duration, content, style, animationIn, animationOut } = data;

  if (frame < start || frame >= start + duration) return null;
  const localFrame = frame - start;

  const resolveAsset = (path: string) => {
    if (path.startsWith('http') || path.startsWith('data:')) return path;
    return staticFile(path);
  };

  let opacity = 1;
  let scale = style?.scale || 1;

  // In/Out Animations
  const animInDur = animationIn?.duration || 15;
  if (localFrame < animInDur) {
    opacity = interpolate(localFrame, [0, animInDur], [0, 1], {
        easing: getEasing(animationIn?.easing),
        extrapolateRight: 'clamp'
    });
  }

  // Ken Burns for layer
  if (style?.zoom) {
      scale *= interpolate(localFrame, [0, duration], [1, style.zoom]);
  }

  const containerStyle: React.CSSProperties = {
    position: 'absolute',
    left: style?.x ?? '50%',
    top: style?.y ?? '50%',
    transform: `translate(-50%, -50%) scale(${scale}) rotate(${style?.rotate || 0}deg)`,
    opacity,
    width: style?.width || 'auto',
    height: style?.height || 'auto',
    zIndex: style?.zIndex || 5,
    borderRadius: style?.borderRadius || 0,
    overflow: 'hidden',
  };

  return (
    <div style={containerStyle}>
      <img src={resolveAsset(content)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="" />
    </div>
  );
};
