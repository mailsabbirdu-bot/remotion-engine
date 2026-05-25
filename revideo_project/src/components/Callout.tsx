import {Rect, Txt, Line} from '@motion-canvas/2d';
import {all, createRef, easeOutBack} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Callout(layer: Layer, parent: any) {
  const lineRef = createRef<Line>();
  const circleRef = createRef<Rect>();
  const labelRef = createRef<Txt>();
  const {content, style, animationIn} = layer;

  const color = style?.color ?? '#00d2ff';
  const targetX = style?.x ?? 400;
  const targetY = style?.y ?? -250;

  parent.add(
    <Rect>
        <Line
            ref={lineRef}
            points={[
                [0, 0],
                [targetX, targetY]
            ]}
            stroke={color}
            lineWidth={4}
            end={0}
        />
        <Rect
            ref={circleRef}
            x={targetX}
            y={targetY}
            width={20}
            height={20}
            radius={10}
            fill={color}
            scale={0}
        />
        <Txt
            ref={labelRef}
            text={content || ''}
            x={targetX + (targetX > 0 ? 40 : -40)}
            y={targetY}
            fill={color}
            fontSize={40}
            fontWeight={700}
            textAlign={targetX > 0 ? 'left' : 'right'}
            opacity={0}
            offsetX={targetX > 0 ? -1 : 1}
        />
    </Rect>
  );

  const duration = animationIn?.duration ?? 1.5;

  yield* all(
      lineRef().end(1, duration),
      circleRef().scale(1.5, duration, easeOutBack),
      labelRef().opacity(1, duration)
  );
}
