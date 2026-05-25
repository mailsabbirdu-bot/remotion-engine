import {Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutExpo, delay, waitFor} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Textbox(layer: Layer, parent: any) {
  const rectRef = createRef<Rect>();
  const textRef = createRef<Txt>();
  const subTextRef = createRef<Txt>();
  const accentRef = createRef<Rect>();
  const containerRef = createRef<Rect>();
  const {content, style, animationIn} = layer;

  // Split content into title and subtitle if pipe exists
  const parts = content ? content.split('|') : ['', ''];
  const title = parts[0].trim();
  const sub = parts[1]?.trim() || '';

  parent.add(
    <Rect
        ref={containerRef}
        x={style?.x ?? 0}
        y={style?.y ?? 0}
        layout
        direction={'row'}
        alignItems={'stretch'}
        opacity={0}
    >
        <Rect
            ref={accentRef}
            width={10}
            height={0}
            fill={style?.stroke ?? '#f1c40f'}
            marginRight={20}
        />
        <Rect
            ref={rectRef}
            width={0}
            height={style?.height ?? 120}
            fill={style?.fill ?? 'rgba(15, 15, 15, 0.85)'}
            radius={style?.borderRadius ?? 4}
            clip
            layout
            direction={'column'}
            padding={30}
            justifyContent={'center'}
        >
            <Txt
                ref={textRef}
                text={title}
                fill={style?.color ?? '#ffffff'}
                fontSize={style?.fontSize ?? 35}
                fontFamily={'Inter, sans-serif'}
                fontWeight={800}
                letterSpacing={2}
                opacity={0}
            />
            {sub && (
                <Txt
                    ref={subTextRef}
                    text={sub}
                    fill={'#f1c40f'}
                    fontSize={(style?.fontSize ?? 35) * 0.7}
                    fontFamily={'Inter, sans-serif'}
                    fontWeight={600}
                    letterSpacing={1}
                    opacity={0}
                    marginTop={10}
                />
            )}
        </Rect>
    </Rect>
  );

  const targetWidth = Number(style?.width ?? 700);
  const targetHeight = Number(style?.height ?? 120);
  const duration = animationIn?.duration ?? 1.2;

  if (animationIn?.type === 'slide-right') {
      const startX = Number(containerRef().x());
      containerRef().x(startX - 200);
      yield* all(
        containerRef().opacity(1, 0.5),
        containerRef().x(startX, duration, easeOutExpo),
        accentRef().height(targetHeight, duration * 0.6, easeOutExpo),
        rectRef().width(targetWidth, duration, easeOutExpo),
        delay(0.4, textRef().opacity(1, 0.5)),
        sub ? delay(0.6, subTextRef().opacity(1, 0.5)) : waitFor(0)
      );
  } else {
    yield* all(
        containerRef().opacity(1, 0.3),
        accentRef().height(targetHeight, duration / 2, easeOutExpo),
        rectRef().width(targetWidth, duration, easeOutExpo),
        delay(0.3, textRef().opacity(1, 0.8)),
        sub ? delay(0.5, subTextRef().opacity(1, 0.8)) : waitFor(0)
    );
  }
}
