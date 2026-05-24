import {Line, Rect} from '@motion-canvas/2d';
import {createRef, easeOutCubic, all} from '@motion-canvas/core';
import {Layer} from '../types';

export function* DataVisuals(layer: Layer, parent: any) {
    if (layer.type === 'graph') {
        yield* LineGraph(layer, parent);
    } else if (layer.type === 'chart') {
        yield* BarChart(layer, parent);
    }
}

function* LineGraph({data, style, animationIn}: Layer, parent: any) {
    const lineRef = createRef<Line>();
    const points = data || [[-300, 200], [-100, -50], [100, 100], [300, -200]];

    const container = createRef<Rect>();
    parent.add(
        <Rect ref={container} x={style?.x ?? 0} y={style?.y ?? 0}>
            {/* Grid */}
            <Rect width={800} height={2} fill="rgba(255,255,255,0.1)" y={200} />
            <Rect width={800} height={2} fill="rgba(255,255,255,0.1)" y={0} />
            <Rect width={800} height={2} fill="rgba(255,255,255,0.1)" y={-200} />

            <Line
                ref={lineRef}
                points={points}
                stroke={style?.stroke ?? '#00d2ff'}
                lineWidth={style?.strokeWidth ?? 10}
                lineCap={'round'}
                lineJoin={'round'}
                end={0}
                shadowColor={style?.stroke ?? '#00d2ff'}
                shadowBlur={30}
            />

            <Rect
                width={20}
                height={20}
                radius={10}
                fill={style?.stroke ?? '#00d2ff'}
                position={() => lineRef().getPointAtPercentage(lineRef().end()).position}
                opacity={() => lineRef().end()}
            />
        </Rect>
    );

    const duration = animationIn?.duration ?? 2;
    yield* lineRef().end(1, duration, easeOutCubic);
}

function* BarChart({data, style, animationIn}: Layer, parent: any) {
    const bars = data || [100, 250, 180, 320, 150];
    const barWidth = 60;
    const spacing = 40;
    const container = createRef<Rect>();

    const barRefs = bars.map(() => createRef<Rect>());

    parent.add(
        <Rect ref={container} x={style?.x ?? 0} y={style?.y ?? 0}>
            {bars.map((val: number, i: number) => (
                <Rect
                    ref={barRefs[i]}
                    key={i.toString()}
                    x={i * (barWidth + spacing) - (bars.length * (barWidth + spacing)) / 2}
                    y={200} // Bottom aligned
                    width={barWidth}
                    height={0}
                    fill={style?.fill ?? '#ff4d4d'}
                    radius={5}
                    offsetY={1} // Animate from bottom
                />
            ))}
        </Rect>
    );

    const duration = animationIn?.duration ?? 1.5;
    yield* all(...barRefs.map((ref: any, i: number) => ref().height(bars[i], duration, easeOutCubic)));
}
