import {makeScene2D, Rect} from '@motion-canvas/2d';
import {all, createRef, waitFor, spawn} from '@motion-canvas/core';
import {TextLayer} from '../components/TextLayer';
import {Textbox} from '../components/Textbox';
import {DataVisuals} from '../components/DataVisuals';
import {ShapeLayer} from '../components/ShapeLayer';
import {Callout} from '../components/Callout';
import {Counter} from '../components/Counter';
import {ImageLayer} from '../components/ImageLayer';
import {MotionCanvasConfig, Scene} from '../types';

import configData from '../../motion_canvas.json';

export default makeScene2D(function* (view) {
  const config = configData as MotionCanvasConfig;
  const isRendering = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('render') === 'true';

  const width = config.width || 1920;
  const height = config.height || 1080;

  // Force strict resolution
  view.size({x: width, y: height});
  view.fill(null);

  console.log(`🎬 Overlay Engine: ${config.scenes.length} scenes at ${width}x${height}`);

  if (isRendering) {
    const canvas = document.querySelector('canvas');
    if (canvas) {
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        canvas.width = width;
        canvas.height = height;
    }
  }

  for (let i = 0; i < config.scenes.length; i++) {
    const scene = config.scenes[i];

    if (isRendering && (window as any).startScene) {
        yield (window as any).startScene(i, scene.id);
    }

    const container = createRef<Rect>();
    view.add(<Rect ref={container} width={width} height={height} opacity={0} fill={null} />);

    // Timing logic
    const totalFrames = Math.round(scene.duration * 30);

    // Start scene animations and fade in container concurrently
    const transitionDur = scene.transition?.duration ?? 0.5;
    yield* spawn(function*() {
        yield* all(
            renderScene(container, scene),
            container().opacity(1, transitionDur)
        );
    }());

    // Frame capture loop - capturing from the very first frame of the scene
    for(let f=0; f < totalFrames; f++) {
        if (isRendering && (window as any).saveFrame) {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                const dataUrl = canvas.toDataURL('image/png');
                yield (window as any).saveFrame(f, dataUrl);
            }
        }
        yield* waitFor(1/30);
    }

    if (isRendering && (window as any).endScene) {
        yield (window as any).endScene(i);
    }

    container().remove();
  }

  if (typeof window !== 'undefined') {
      (window as any).finished = true;
  }
});

function* renderScene(container: any, scene: Scene) {
  const animations = [];
  for (const layer of scene.layers) {
      const startDelay = layer.start ?? 0;

      if (layer.type === 'text') {
          animations.push(function* () {
              yield* waitFor(startDelay);
              yield* TextLayer(layer, container());
          }());
      } else if (layer.type === 'textbox') {
          animations.push(function* () {
              yield* waitFor(startDelay);
              yield* Textbox(layer, container());
          }());
      } else if (layer.type === 'graph' || layer.type === 'chart') {
          animations.push(function* () {
              yield* waitFor(startDelay);
              yield* DataVisuals(layer, container());
          }());
      } else if (layer.type === 'shape') {
          animations.push(function* () {
              yield* waitFor(startDelay);
              yield* ShapeLayer(layer, container());
          }());
      } else if (layer.type === 'image') {
          animations.push(function* () {
            yield* waitFor(startDelay);
            yield* ImageLayer(layer, container());
          }());
      } else if (layer.id.startsWith('callout')) {
          animations.push(function* () {
            yield* waitFor(startDelay);
            yield* Callout(layer, container());
        }());
      } else if (layer.id.startsWith('counter')) {
        animations.push(function* () {
            yield* waitFor(startDelay);
            yield* Counter(layer, container());
        }());
      }
  }

  yield* all(...animations);
}
