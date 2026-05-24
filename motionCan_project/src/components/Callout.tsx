import {Line, Rect, Txt, Circle} from '@motion-canvas/2d';
import {createRef, easeOutExpo, all, waitFor} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Callout({content, style, animationIn}: Layer, parent: any) {
  const lineRef = createRef<Line>();
  const circleRef = createRef<Circle>();
  const textRef = createRef<Txt>();
  const boxRef = createRef<Rect>();

  const targetX = Number(style?.x ?? 200);
  const targetY = Number(style?.y ?? -200);

  parent.add(
    <Rect>
        {/* The Point of Interest */}
        <Circle
            ref={circleRef}
            width={20}
            height={20}
            fill={style?.color ?? '#ffcc00'}
            opacity={0}
        />

        {/* The Connector Line */}
        <Line
            ref={lineRef}
            points={[
                [0, 0],
                [targetX * 0.2, targetY * 0.2],
                [targetX, targetY]
            ]}
            stroke={style?.color ?? '#ffcc00'}
            lineWidth={4}
            end={0}
        />

        {/* The Label Box */}
        <Rect
            ref={boxRef}
            x={targetX + (targetX > 0 ? 100 : -100)}
            y={targetY}
            height={60}
            fill="rgba(0,0,0,0.8)"
            radius={8}
            padding={20}
            opacity={0}
            clip
        >
            <Txt
                ref={textRef}
                text={content || ''}
                fill="#ffffff"
                fontSize={24}
                fontFamily="Inter, sans-serif"
                fontWeight={700}
            />
        </Rect>
    </Rect>
  );

  const duration = animationIn?.duration ?? 1;

  yield* all(
      circleRef().opacity(1, duration / 2),
      lineRef().end(1, duration, easeOutExpo),
  );

  yield* all(
      boxRef().opacity(1, 0.5),
      boxRef().width(300, 0.8, easeOutExpo), // Dynamic width would be better but fixed for now
  );
}
