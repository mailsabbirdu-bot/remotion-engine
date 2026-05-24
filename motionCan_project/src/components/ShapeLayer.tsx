import {Rect} from '@motion-canvas/2d';
import {createRef} from '@motion-canvas/core';
import {Layer} from '../types';

export function* ShapeLayer(layer: Layer, parent: any) {
    const shapeRef = createRef<Rect>();
    const {style, animationIn} = layer;

    parent.add(
        <Rect
            ref={shapeRef}
            width={style?.width ?? 100}
            height={style?.height ?? 100}
            fill={style?.fill ?? '#ffffff'}
            x={style?.x ?? 0}
            y={style?.y ?? 0}
            opacity={0}
        />
    );

    yield* shapeRef().opacity(1, animationIn?.duration ?? 0.5);
}
