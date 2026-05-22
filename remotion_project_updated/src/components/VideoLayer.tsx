import React from 'react';
import { useCurrentFrame, interpolate, OffthreadVideo, staticFile } from 'remotion';

export const VideoLayer: React.FC<{ data: any }> = ({ data }) => {
    const frame = useCurrentFrame();
    const { start, duration, content, style, animationIn } = data;

    if (frame < start || frame >= start + duration) return null;
    const localFrame = frame - start;

    const resolveAsset = (path: string) => {
      if (path.startsWith('http') || path.startsWith('data:')) return path;
      return staticFile(path);
    };

    let opacity = 1;
    const animInDur = animationIn?.duration || 15;
    if (localFrame < animInDur) {
      opacity = interpolate(localFrame, [0, animInDur], [0, 1]);
    }

    const containerStyle: React.CSSProperties = {
      position: 'absolute',
      left: style?.x ?? '50%',
      top: style?.y ?? '50%',
      transform: `translate(-50%, -50%)`,
      opacity,
      width: style?.width || 'auto',
      height: style?.height || 'auto',
      zIndex: style?.zIndex || 5,
    };

    return (
      <div style={containerStyle}>
        <OffthreadVideo src={resolveAsset(content)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
    );
  };
