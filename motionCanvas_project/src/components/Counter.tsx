import {Txt} from '@motion-canvas/2d';
import {createRef, easeOutExpo} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Counter({content, style, animationIn}: Layer, parent: any) {
  const textRef = createRef<Txt>();
  const targetValue = parseInt(content || '0');

  parent.add(
    <Txt
      ref={textRef}
      text="0"
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      fill={style?.color ?? '#ffffff'}
      fontSize={style?.fontSize ?? 100}
      fontFamily={'Inter, sans-serif'}
      fontWeight={900}
    />
  );

  const duration = animationIn?.duration ?? 2;
  // Animate the text value
  yield* textRef().text(targetValue.toString(), duration, easeOutExpo, (v) => Math.round(parseFloat(v)).toString());
}
