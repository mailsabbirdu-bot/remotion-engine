import {Img} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic} from '@motion-canvas/core';
import {Layer} from '../types';

export function* ImageLayer(layer: Layer, parent: any) {
  const imageRef = createRef<Img>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Img
      ref={imageRef}
      src={content || ''}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      width={style?.width}
      height={style?.height}
      opacity={0}
      radius={style?.borderRadius ?? 0}
    />
  );

  const duration = animationIn?.duration ?? 0.8;
  const easing = easeOutCubic;

  if (animationIn) {
    if (animationIn.type === 'fade') {
      yield* imageRef().opacity(1, duration, easing);
    } else if (animationIn.type === 'zoom') {
        imageRef().scale(0.8);
        yield* all(
            imageRef().opacity(1, duration, easing),
            imageRef().scale(1, duration, easing),
        );
    } else if (animationIn.type === 'slide-up') {
        const currentY = Number(imageRef().y());
        imageRef().y(currentY + 50);
        yield* all(
            imageRef().opacity(1, duration, easing),
            imageRef().y(currentY, duration, easing),
        );
    }
  } else {
    imageRef().opacity(1);
  }
}
