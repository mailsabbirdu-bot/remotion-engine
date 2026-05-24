import {Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutExpo} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Textbox(layer: Layer, parent: any) {
  const rectRef = createRef<Rect>();
  const textRef = createRef<Txt>();
  const accentRef = createRef<Rect>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Rect
        x={style?.x ?? 0}
        y={style?.y ?? 0}
    >
        <Rect
            ref={accentRef}
            x={-(Number(style?.width ?? 600) / 2) - 5}
            width={10}
            height={0}
            fill={style?.stroke ?? '#f1c40f'}
        />
        <Rect
            ref={rectRef}
            width={0}
            height={style?.height ?? 100}
            fill={style?.fill ?? 'rgba(0, 0, 0, 0.8)'}
            radius={style?.borderRadius ?? 0}
            clip
        >
            <Txt
                ref={textRef}
                text={content || ''}
                fill={style?.color ?? '#ffffff'}
                fontSize={style?.fontSize ?? 35}
                fontFamily={style?.fontFamily ?? 'Inter, sans-serif'}
                fontWeight={style?.fontWeight ?? 600}
                padding={30}
                opacity={0}
            />
        </Rect>
    </Rect>
  );

  const targetWidth = Number(style?.width ?? 600);
  const targetHeight = Number(style?.height ?? 100);
  const duration = animationIn?.duration ?? 1;

  yield* accentRef().height(targetHeight, duration / 2, easeOutExpo);
  yield* all(
      rectRef().width(targetWidth, duration, easeOutExpo),
      textRef().opacity(1, duration, easeOutExpo),
  );
}
