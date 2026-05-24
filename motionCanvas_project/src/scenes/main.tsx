import {makeScene2D, Video, Rect} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {TextLayer} from '../components/TextLayer';
import {Textbox} from '../components/Textbox';
import {DataVisuals} from '../components/DataVisuals';
import {ShapeLayer} from '../components/ShapeLayer';
import {Callout} from '../components/Callout';
import {MotionCanvasConfig, Scene} from '../types';

import configData from '../../motion_canvas.json';

export default makeScene2D(function* (view) {
  const config = configData as MotionCanvasConfig;

  for (const scene of config.scenes) {
    yield* renderScene(view, scene);
  }
});

function* renderScene(view: any, scene: Scene) {
  const container = createRef<Rect>();
  view.add(<Rect ref={container} width="100%" height="100%" opacity={0} />);

  const videoRef = createRef<Video>();

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
              <Rect
                  width="100%"
                  height="100%"
                  fill={scene.background.src}
              />
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
      }
  }

  const transitionDur = scene.transition?.duration ?? 0.5;
  yield* container().opacity(1, transitionDur);

  yield* all(...animations);
  yield* waitFor(scene.duration);
  yield* container().opacity(0, transitionDur);
  container().remove();
}
