import React, { createContext, useContext } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { getEasing } from '../utils/animation-utils';
import { CameraConfig } from './CameraRig';

interface CameraState {
  x: number;
  y: number;
  zoom: number;
}

const CameraContext = createContext<CameraState>({ x: 0, y: 0, zoom: 1 });

export const useCamera = () => useContext(CameraContext);

export const CameraProvider: React.FC<{ camera?: CameraConfig; children: React.ReactNode }> = ({ camera, children }) => {
  const frame = useCurrentFrame();

  let currentX = 0;
  let currentY = 0;
  let currentZoom = 1;

  if (camera && camera.enabled && camera.keyframes.length > 0) {
    const sortedKeyframes = [...camera.keyframes].sort((a, b) => a.frame - b.frame);

    if (frame <= sortedKeyframes[0].frame) {
      currentX = sortedKeyframes[0].x;
      currentY = sortedKeyframes[0].y;
      currentZoom = sortedKeyframes[0].zoom;
    } else if (frame >= sortedKeyframes[sortedKeyframes.length - 1].frame) {
      currentX = sortedKeyframes[sortedKeyframes.length - 1].x;
      currentY = sortedKeyframes[sortedKeyframes.length - 1].y;
      currentZoom = sortedKeyframes[sortedKeyframes.length - 1].zoom;
    } else {
      for (let i = 0; i < sortedKeyframes.length - 1; i++) {
        const start = sortedKeyframes[i];
        const end = sortedKeyframes[i + 1];

        if (frame >= start.frame && frame <= end.frame) {
          const easing = getEasing(end.easing);
          currentX = interpolate(frame, [start.frame, end.frame], [start.x, end.x], {
            easing,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          currentY = interpolate(frame, [start.frame, end.frame], [start.y, end.y], {
            easing,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          currentZoom = interpolate(frame, [start.frame, end.frame], [start.zoom, end.zoom], {
            easing,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          break;
        }
      }
    }
  }

  return (
    <CameraContext.Provider value={{ x: currentX, y: currentY, zoom: currentZoom }}>
      {children}
    </CameraContext.Provider>
  );
};
