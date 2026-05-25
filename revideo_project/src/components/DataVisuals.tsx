import {Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic, delay} from '@motion-canvas/core';
import {Layer} from '../types';

export function* DataVisuals(layer: Layer, parent: any) {
  const containerRef = createRef<Rect>();
  const {data, style, animationIn} = layer;

  if (!data || !Array.isArray(data)) return;

  const barWidth = 60;
  const barGap = 30;
  const maxVal = Math.max(...data);
  const maxHeight = 400;

  parent.add(
    <Rect
      ref={containerRef}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      layout
      direction={'row'}
      alignItems={'end'}
      gap={barGap}
      opacity={0}
    >
      {data.map((val, i) => {
        const barHeight = (val / maxVal) * maxHeight;
        const barRef = createRef<Rect>();
        const labelRef = createRef<Txt>();

        return (
          <Rect direction={'column'} alignItems={'center'} gap={10}>
             <Txt
              ref={labelRef}
              text={val.toString()}
              fill={style?.fill ?? '#f1c40f'}
              fontSize={24}
              fontWeight={700}
              opacity={0}
            />
            <Rect
              ref={barRef}
              width={barWidth}
              height={0}
              fill={style?.fill ?? '#f1c40f'}
              radius={5}
            />
          </Rect>
        );
      })}
    </Rect>
  );

  const duration = animationIn?.duration ?? 1.5;
  const bars = containerRef().children();

  yield* containerRef().opacity(1, 0.5);

  const animations = bars.map((barContainer: any, i) => {
    const bar = barContainer.children()[1] as Rect;
    const label = barContainer.children()[0] as Txt;
    const val = data[i];
    const targetH = (val / maxVal) * maxHeight;

    return all(
        delay(i * 0.1, bar.height(targetH, duration, easeOutCubic)),
        delay(i * 0.1 + 0.5, label.opacity(1, 0.5))
    );
  });

  yield* all(...animations);
}
