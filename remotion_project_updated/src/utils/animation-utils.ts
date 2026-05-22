import { Easing, interpolate } from 'remotion';

/**
 * Parses a cubic-bezier string or standard easing names.
 */
export const getEasing = (easingStr?: string) => {
  if (!easingStr) return Easing.linear;

  if (easingStr.startsWith('cubic-bezier')) {
    const parts = easingStr
      .replace('cubic-bezier(', '')
      .replace(')', '')
      .split(',')
      .map((p) => parseFloat(p.trim()));
    if (parts.length === 4) {
      return Easing.bezier(parts[0], parts[1], parts[2], parts[3]);
    }
  }

  switch (easingStr) {
    case 'ease-in': return Easing.in(Easing.ease);
    case 'ease-out': return Easing.out(Easing.ease);
    case 'ease-in-out': return Easing.inOut(Easing.ease);
    case 'linear': return Easing.linear;
    case 'bounce': return Easing.bounce;
    case 'elastic': return Easing.elastic(1);
    default: return Easing.linear;
  }
};

/**
 * Handles multiple keyframes and interpolates values.
 */
export const interpolateKeyframes = (
  frame: number,
  keyframes: { frame: number; value: number; easing?: string }[],
  defaultValue: number
) => {
  if (!keyframes || keyframes.length === 0) return defaultValue;

  const sorted = [...keyframes].sort((a, b) => a.frame - b.frame);

  if (frame <= sorted[0].frame) return sorted[0].value;
  if (frame >= sorted[sorted.length - 1].frame) return sorted[sorted.length - 1].value;

  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];

    if (frame >= start.frame && frame <= end.frame) {
      return interpolate(
        frame,
        [start.frame, end.frame],
        [start.value, end.value],
        {
          easing: getEasing(end.easing),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }
      );
    }
  }

  return defaultValue;
};
