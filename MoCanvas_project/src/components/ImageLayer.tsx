import {Img} from '@motion-canvas/2d';
import {createRef, easeOutCubic, all} from '@motion-canvas/core';
import {Layer} from '../types';

export function* ImageLayer(layer: Layer, parent: any) {
  const imgRef = createRef<Img>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Img
      ref={imgRef}
      src={content || ''}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      width={style?.width}
      height={style?.height}
      opacity={0}
    />
  );

  const duration = animationIn?.duration ?? 1;
  const easing = easeOutCubic;

  if (animationIn?.type === 'fade') {
    yield* imgRef().opacity(1, duration, easing);
  } else if (animationIn?.type === 'zoom') {
    imgRef().scale(0.8);
    yield* all(
        imgRef().opacity(1, duration, easing),
        imgRef().scale(1, duration, easing)
    );
  } else {
    imgRef().opacity(1);
  }
}
