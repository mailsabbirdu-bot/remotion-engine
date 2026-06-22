import React from 'react';
import { useCamera } from './CameraContext';

export interface CameraKeyframe {
  frame: number;
  x: number;
  y: number;
  zoom: number;
  easing?: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

export interface CameraConfig {
  enabled: boolean;
  debug: boolean;
  keyframes: CameraKeyframe[];
}

interface CameraRigProps {
  debug?: boolean;
  children: React.ReactNode;
  width: number;
  height: number;
}

export const CameraRig: React.FC<CameraRigProps> = ({
  debug,
  children,
  width,
  height,
}) => {
  const { x, y, zoom } = useCamera();

  const cameraStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    transform: `scale(${zoom}) translate(${-x}px, ${-y}px)`,
    transformOrigin: 'center center',
  };

  return (
    <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <div style={cameraStyle}>
        {children}
        {debug && (
           <div style={{
             position: 'absolute',
             top: 20,
             left: 20,
             backgroundColor: 'rgba(0,0,0,0.8)',
             color: '#0f0',
             padding: '10px',
             fontFamily: 'monospace',
             fontSize: '16px',
             zIndex: 9999,
             border: '1px solid #0f0'
           }}>
             <div>DEBUG_CAMERA: ENABLED</div>
             <div>CAM_X: {x.toFixed(2)}</div>
             <div>CAM_Y: {y.toFixed(2)}</div>
             <div>ZOOM: {zoom.toFixed(2)}</div>
             <div style={{ marginTop: '10px', borderTop: '1px solid #0f0', paddingTop: '5px' }}>
                WORLD: 4000x4000
             </div>
           </div>
        )}
      </div>
    </div>
  );
};
