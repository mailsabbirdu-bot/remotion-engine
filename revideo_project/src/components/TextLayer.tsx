import {Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic} from '@motion-canvas/core';
import {Layer} from '../types';

export function* TextLayer(layer: Layer, parent: any) {
  const textRef = createRef<Txt>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Txt
      ref={textRef}
      text={content || ''}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      fill={style?.color ?? '#ffffff'}
      fontSize={style?.fontSize ?? 60}
      fontFamily={style?.fontFamily ?? 'Inter, sans-serif'}
      fontWeight={style?.fontWeight ?? 700}
      letterSpacing={style?.letterSpacing ?? 0}
      lineHeight={style?.lineHeight ?? 1.2}
      opacity={0}
      shadowColor={style?.shadowColor ?? 'rgba(0,0,0,0.5)'}
      shadowBlur={style?.shadowBlur ?? 0}
      textAlign={'center'}
      width={1400} // Wide multi-line support
      textWrap={true}
    />
  );

  const duration = animationIn?.duration ?? 0.8;
  const easing = easeOutCubic;

  if (animationIn) {
    if (animationIn.type === 'fade') {
      yield* textRef().opacity(1, duration, easing);
    } else if (animationIn.type === 'slide-up') {
      const currentY = Number(textRef().y());
      textRef().y(currentY + 100);
      yield* all(
        textRef().opacity(1, duration, easing),
        textRef().y(currentY, duration, easing),
      );
    } else if (animationIn.type === 'zoom') {
        textRef().scale(0.5);
        yield* all(
            textRef().opacity(1, duration, easing),
            textRef().scale(1, duration, easing),
        );
    } else if (animationIn.type === 'typewriter') {
        const fullText = content || '';
        textRef().text('');
        textRef().opacity(1);
        yield* textRef().text(fullText, duration);
    }
  } else {
    textRef().opacity(1);
  }
}
