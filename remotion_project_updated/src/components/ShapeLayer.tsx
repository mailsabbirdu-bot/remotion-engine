import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { getEasing } from '../utils/animation-utils';

export const ShapeLayer: React.FC<{ data: any }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { start, duration, shape, style, animationIn } = data;

  if (frame < start || frame >= start + duration) return null;
  const localFrame = frame - start;

  let opacity = 1;
  let scale = 1;

  const animInDur = animationIn?.duration || 15;
  if (localFrame < animInDur) {
    opacity = interpolate(localFrame, [0, animInDur], [0, 1], { easing: getEasing(animationIn?.easing) });
    if (animationIn?.type === 'zoom-in') {
        scale = interpolate(localFrame, [0, animInDur], [0, 1], { easing: getEasing(animationIn?.easing) });
    }
  }

  const containerStyle: React.CSSProperties = {
    position: 'absolute',
    left: style?.x ?? '50%',
    top: style?.y ?? '50%',
    transform: `translate(-50%, -50%) scale(${scale})`,
    opacity,
    zIndex: style?.zIndex || 1,
  };

  const renderShape = () => {
      const { type, width, height, color, stroke, strokeWidth } = shape;
      const commonProps = {
          fill: color || 'white',
          stroke: stroke || 'none',
          strokeWidth: strokeWidth || 0,
      };

      if (type === 'rect') {
          return <rect width={width} height={height} {...commonProps} rx={shape.borderRadius || 0} />;
      }
      if (type === 'circle') {
          return <circle cx={width/2} cy={width/2} r={width/2} {...commonProps} />;
      }
      if (type === 'triangle') {
          const points = `0,${height} ${width/2},0 ${width},${height}`;
          return <polygon points={points} {...commonProps} />;
      }
      return null;
  };

  return (
    <div style={containerStyle}>
        <svg width={shape.width} height={shape.height} viewBox={`0 0 ${shape.width} ${shape.height}`}>
            {renderShape()}
        </svg>
    </div>
  );
};
