import {makeScene2D, Video, Rect} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {TextLayer} from '../components/TextLayer';
import {Textbox} from '../components/Textbox';
import {DataVisuals} from '../components/DataVisuals';
import {ShapeLayer} from '../components/ShapeLayer';
import {Callout} from '../components/Callout';
import {Counter} from '../components/Counter';
import {MotionCanvasConfig, Scene} from '../types';

import configData from '../../motion_canvas.json';

export default makeScene2D(function* (view) {
  const config = configData as MotionCanvasConfig;
  const isRendering = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('render') === 'true';

  let frameCount = 0;

  for (const scene of config.scenes) {
    yield* renderScene(view, scene, isRendering, () => {
        if (isRendering && (window as any).saveFrame) {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                const dataUrl = canvas.toDataURL('image/png');
                (window as any).saveFrame(frameCount, dataUrl);
            }
        }
        frameCount++;
    });
  }

  if (typeof window !== 'undefined') {
      yield* waitFor(1); // Final buffer
      (window as any).finished = true;
  }
});

function* renderScene(view: any, scene: Scene, isRendering: boolean, onFrame: () => void) {
  const container = createRef<Rect>();
  view.add(<Rect ref={container} width="100%" height="100%" opacity={0} />);

  // Background Overlay (Vignette)
  container().add(
      <Rect
        width="100%"
        height="100%"
        fill={'radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,0.4) 100%)'}
        zIndex={10}
        opacity={0.8}
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
      } else if (layer.type === 'image' && layer.id.startsWith('callout')) {
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

  const transitionDur = scene.transition?.duration ?? 1;
  yield* container().opacity(1, transitionDur);

  yield* all(...animations);

  const totalFrames = Math.round(scene.duration * 30);
  for(let i=0; i<totalFrames; i++) {
      yield* waitFor(1/30);
      onFrame();
  }

  yield* container().opacity(0, transitionDur);
  container().remove();
}
