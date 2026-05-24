import {Line, Rect, Txt} from '@motion-canvas/2d';
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
    const areaRef = createRef<Line>();
    const points = data || [[-300, 200], [-100, -50], [100, 100], [300, -200]];

    const container = createRef<Rect>();
    parent.add(
        <Rect ref={container} x={style?.x ?? 0} y={style?.y ?? 0}>
            {/* Area Fill */}
            <Line
                ref={areaRef}
                points={[...points, [points[points.length-1][0], 300], [points[0][0], 300]]}
                fill={'rgba(0, 210, 255, 0.15)'}
                closed
                opacity={0}
            />

            {/* Grid */}
            <Rect width={1000} height={2} fill="rgba(255,255,255,0.05)" y={200} />
            <Rect width={1000} height={2} fill="rgba(255,255,255,0.05)" y={0} />
            <Rect width={1000} height={2} fill="rgba(255,255,255,0.05)" y={-200} />

            <Line
                ref={lineRef}
                points={points}
                stroke={style?.stroke ?? '#00d2ff'}
                lineWidth={style?.strokeWidth ?? 12}
                lineCap={'round'}
                lineJoin={'round'}
                end={0}
                shadowColor={style?.stroke ?? '#00d2ff'}
                shadowBlur={40}
            />

            <Rect
                width={24}
                height={24}
                radius={12}
                fill={'#ffffff'}
                stroke={style?.stroke ?? '#00d2ff'}
                lineWidth={4}
                position={() => lineRef().getPointAtPercentage(lineRef().end()).position}
                opacity={() => lineRef().end()}
            />
        </Rect>
    );

    const duration = animationIn?.duration ?? 2.5;
    yield* all(
        lineRef().end(1, duration, easeOutCubic),
        areaRef().opacity(1, duration, easeOutCubic)
    );
}

function* BarChart({data, style, animationIn}: Layer, parent: any) {
    const bars = data || [100, 250, 180, 320, 150];
    const barWidth = 70;
    const spacing = 50;
    const container = createRef<Rect>();

    const barRefs = bars.map(() => createRef<Rect>());
    const labelRefs = bars.map(() => createRef<Txt>());

    parent.add(
        <Rect ref={container} x={style?.x ?? 0} y={style?.y ?? 0}>
            {bars.map((val: number, i: number) => (
                <Rect key={i.toString()}>
                    <Rect
                        ref={barRefs[i]}
                        x={i * (barWidth + spacing) - ((bars.length - 1) * (barWidth + spacing)) / 2}
                        y={250}
                        width={barWidth}
                        height={0}
                        fill={style?.fill ?? '#ff4d4d'}
                        radius={6}
                        offsetY={1}
                        shadowBlur={20}
                        shadowColor={style?.fill ?? '#ff4d4d'}
                    />
                    <Txt
                        ref={labelRefs[i]}
                        text={val.toString()}
                        x={i * (barWidth + spacing) - ((bars.length - 1) * (barWidth + spacing)) / 2}
                        y={250}
                        fill={'#ffffff'}
                        fontSize={24}
                        fontFamily={'Inter, sans-serif'}
                        fontWeight={700}
                        opacity={0}
                    />
                </Rect>
            ))}
        </Rect>
    );

    const duration = animationIn?.duration ?? 2;
    yield* all(
        ...barRefs.map((ref: any, i: number) => ref().height(bars[i], duration, easeOutCubic)),
        ...labelRefs.map((ref: any, i: number) => all(
            ref().opacity(1, duration, easeOutCubic),
            ref().y(250 - bars[i] - 30, duration, easeOutCubic)
        ))
    );
}
