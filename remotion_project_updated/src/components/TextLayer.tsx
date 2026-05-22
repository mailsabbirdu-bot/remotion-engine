import React from 'react';
import { useCurrentFrame, interpolate, AbsoluteFill } from 'remotion';
import { getEasing } from '../utils/animation-utils';
import { WordByWordText } from './WordByWordText';

export const TextLayer: React.FC<{ data: any; banglaFont: string; englishFont: string; sceneDuration: number }> = ({
  data,
  banglaFont,
  englishFont,
}) => {
  const frame = useCurrentFrame();
  const { start, duration, content, style, animationIn, animationOut, textbox, textAnimation } = data;

  if (frame < start || frame >= start + duration) return null;

  const localFrame = frame - start;

  // Animation In
  let opacity = 1;
  let translateY = 0;
  let scale = 1;
  let blur = 0;

  const animInDur = animationIn?.duration || 15;
  if (localFrame < animInDur) {
    const easing = getEasing(animationIn?.easing);
    opacity = interpolate(localFrame, [0, animInDur], [0, 1], { easing, extrapolateRight: 'clamp' });

    if (animationIn?.type === 'fade-up') {
        translateY = interpolate(localFrame, [0, animInDur], [50, 0], { easing });
    } else if (animationIn?.type === 'zoom-in') {
        scale = interpolate(localFrame, [0, animInDur], [0.5, 1], { easing });
    } else if (animationIn?.type === 'blur-in') {
        blur = interpolate(localFrame, [0, animInDur], [20, 0], { easing });
    }
  }

  // Animation Out
  const animOutDur = animationOut?.duration || 15;
  const outStart = duration - animOutDur;
  if (localFrame > outStart) {
    const outProgress = localFrame - outStart;
    const easing = getEasing(animationOut?.easing);
    const outOpacity = interpolate(outProgress, [0, animOutDur], [1, 0], { easing, extrapolateRight: 'clamp' });
    opacity *= outOpacity;

    if (animationOut?.type === 'fade-down') {
        translateY = interpolate(outProgress, [0, animOutDur], [0, 50], { easing });
    } else if (animationOut?.type === 'zoom-out') {
        scale *= interpolate(outProgress, [0, animOutDur], [1, 1.5], { easing });
    }
  }

  const containerStyle: React.CSSProperties = {
    position: 'absolute',
    left: style?.x ?? '50%',
    top: style?.y ?? '50%',
    transform: `translate(-50%, -50%) translate(0, ${translateY}px) scale(${scale})`,
    opacity,
    filter: blur > 0 ? `blur(${blur}px)` : 'none',
    width: '100%',
    textAlign: 'center',
    zIndex: style?.zIndex || 10,
  };

  const boxStyle: React.CSSProperties = textbox?.enabled ? {
    backgroundColor: textbox.color || 'rgba(0,0,0,0.5)',
    padding: `${textbox.padding || 20}px`,
    borderRadius: textbox.type === 'rounded-rect' ? '20px' : '0px',
    display: 'inline-block',
    boxShadow: textbox.shadow || 'none',
    border: textbox.border || 'none',
  } : {};

  return (
    <div style={containerStyle}>
        <div style={boxStyle}>
            <WordByWordText
                text={content}
                style={{
                    fontSize: style?.fontSize || 60,
                    color: style?.color || '#ffffff',
                    fontWeight: style?.fontWeight || 'bold',
                    textShadow: style?.textShadow || 'none',
                }}
                banglaFontFamily={banglaFont}
                englishFontFamily={englishFont}
                duration={textAnimation?.duration || (duration / 2)}
                animationMode={textAnimation?.mode || 'word'}
                localFrame={localFrame}
            />
        </div>
    </div>
  );
};
