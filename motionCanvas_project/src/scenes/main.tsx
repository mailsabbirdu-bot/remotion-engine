import {makeScene2D, Video, Rect} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
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

  // Force view resolution
  view.size({x: width, y: height});

  let frameCount = 0;
  console.log(`🎬 Starting Motion Canvas Engine with ${config.scenes.length} scenes at ${width}x${height}`);

  for (let i = 0; i < config.scenes.length; i++) {
    const scene = config.scenes[i];
    console.log(`🎥 Rendering Scene ${i + 1}/${config.scenes.length}: ${scene.id}`);

    const container = createRef<Rect>();
    view.add(<Rect ref={container} width="100%" height="100%" opacity={0} />);

    // Capture Loop Wrapper
    yield* renderScene(container, scene);

    // The duration in config should be the total time this scene is active
    const totalFrames = Math.round(scene.duration * 30);

    for(let f=0; f < totalFrames; f++) {
        if (isRendering && (window as any).saveFrame) {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                if (f === 0) {
                    console.log(`Canvas dimensions: ${canvas.width}x${canvas.height}`);
                }
                const dataUrl = canvas.toDataURL('image/png');
                yield (window as any).saveFrame(frameCount, dataUrl);
            }
        }
        frameCount++;
        yield* waitFor(1/30);
    }

    container().remove();
  }

  console.log('✅ All scenes rendered!');
  if (typeof window !== 'undefined') {
      (window as any).finished = true;
  }
});

function* renderScene(container: any, scene: Scene) {
  container().add(
      <Rect
        width="100%"
        height="100%"
        fill={'rgba(0,0,0,0.2)'}
        zIndex={10}
      />
  );

  const videoRef = createRef<Video>();

  container().add(
    <Rect width="100%" height="100%" fill="#0a0a0a" zIndex={-2} />
  );

  if (scene.background) {
      if (scene.background.type === 'video') {
          container().add(
              <Video
                  ref={videoRef}
                  src={scene.background.src}
                  width="100%"
                  height="100%"
                  play
                  opacity={scene.background.opacity ?? 1}
              />
          );
      } else if (scene.background.type === 'color') {
          container().add(
              <Rect width="100%" height="100%" fill={scene.background.src} />
          );
      }
  }

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

  const transitionDur = scene.transition?.duration ?? 0.5;
  yield* container().opacity(1, transitionDur);
  yield* all(...animations);

  // Wait for the total scene duration minus the initial transition
  const remainingWait = Math.max(0, scene.duration - transitionDur);
  yield* waitFor(remainingWait);
}
