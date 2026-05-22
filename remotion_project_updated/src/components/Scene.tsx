import React from 'react';
import { AbsoluteFill, OffthreadVideo, Audio, useCurrentFrame, interpolate } from 'remotion';
import { TextLayer } from './TextLayer';
import { ImageLayer } from './ImageLayer';
import { VideoLayer } from './VideoLayer';
import { ShapeLayer } from './ShapeLayer';
import { resolveAsset } from '../utils/path-utils';

export const Scene: React.FC<{ data: any; banglaFont: string; englishFont: string }> = ({
  data,
  banglaFont,
  englishFont,
}) => {
  const frame = useCurrentFrame();
  const background = data.background || {};
  const layers = data.layers || [];

  const renderBackground = () => {
    const { type, src, audio, zoom } = background;

    let transform = 'scale(1)';
    if (zoom) {
        const scale = interpolate(frame, [0, data.duration], [1, zoom], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
        });
        transform = `scale(${scale})`;
    }

    switch (type) {
      case 'video':
        return (
          <>
            <OffthreadVideo
              src={resolveAsset(src)}
              style={{ width: '100%', height: '100%', objectFit: 'cover', transform }}
            />
            {audio && <Audio src={resolveAsset(audio)} />}
          </>
        );
      case 'image':
        return (
          <img
            src={resolveAsset(src)}
            style={{ width: '100%', height: '100%', objectFit: 'cover', transform }}
            alt=""
          />
        );
      case 'color':
        return <div style={{ width: '100%', height: '100%', backgroundColor: src }} />;
      case 'gradient':
        return <div style={{ width: '100%', height: '100%', background: src }} />;
      default:
        return <div style={{ width: '100%', height: '100%', backgroundColor: 'black' }} />;
    }
  };

  return (
    <AbsoluteFill>
      <AbsoluteFill>{renderBackground()}</AbsoluteFill>
      {layers.map((layer: any, index: number) => {
        const props = {
            key: layer.id || index,
            data: layer,
            banglaFont,
            englishFont,
            sceneDuration: data.duration
        };

        switch (layer.type) {
          case 'text': return <TextLayer {...props} />;
          case 'image': return <ImageLayer {...props} />;
          case 'video': return <VideoLayer {...props} />;
          case 'shape': return <ShapeLayer {...props} />;
          default: return null;
        }
      })}
    </AbsoluteFill>
  );
};
