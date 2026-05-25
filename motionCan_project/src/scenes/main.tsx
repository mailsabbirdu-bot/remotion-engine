import {makeScene2D, Rect, Video, Img} from '@motion-canvas/2d';
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

  console.log(`🎬 Overlay Engine Started: ${config.scenes.length} scenes at ${width}x${height}`);

  if (isRendering) {
      (window as any).finished = false;
      console.log('⏳ Waiting for bridge functions...');
      // Busy wait for 10 frames to ensure Playwright has time to inject functions if needed
      for (let j = 0; j < 10; j++) yield;

      while (!(window as any).startScene || !(window as any).saveFrame || !(window as any).endScene) {
          console.log('...still waiting for bridge...');
          yield* waitFor(0.1);
      }
      console.log('✅ Bridge functions detected!');
  }

  for (let i = 0; i < config.scenes.length; i++) {
    const scene = config.scenes[i];
    console.log(`🎬 Rendering Scene ${i + 1}/${config.scenes.length}: ${scene.id}`);

    if (isRendering) {
        let done = false;
        (window as any).startScene(i, scene.id).then(() => { done = true; });
        while (!done) yield;
    }

    const container = createRef<Rect>();
    view.add(<Rect ref={container} width={width} height={height} opacity={0} fill={null} />);

    // Add background
    if (scene.background) {
        try {
            if (scene.background.type === 'color') {
                container().add(<Rect width={width} height={height} fill={scene.background.src} />);
            } else if (scene.background.type === 'image') {
                container().add(<Img src={scene.background.src} width={width} height={height} />);
            } else if (scene.background.type === 'video') {
                const videoRef = createRef<Video>();
                container().add(<Video ref={videoRef} src={scene.background.src} width={width} height={height} play={true} />);
            }
        } catch (e) {
            console.error(`❌ Background error in ${scene.id}:`, e);
        }
    }

    const totalFrames = Math.round(scene.duration * 30);
    const transitionDur = scene.transition?.duration ?? 0.5;

    // Start scene animations
    spawn(function*() {
        yield* all(
            renderScene(container, scene),
            container().opacity(1, transitionDur)
        );
    });

    // Frame capture loop
    for(let f=0; f < totalFrames; f++) {
        if (isRendering) {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                const dataUrl = canvas.toDataURL('image/png');
                let done = false;
                (window as any).saveFrame(scene.id, f, dataUrl).then(() => { done = true; });
                while (!done) yield;
            }
        }
        yield* waitFor(1/30);
    }

    if (isRendering) {
        let done = false;
        (window as any).endScene(scene.id).then(() => { done = true; });
        while (!done) yield;
    }

    container().remove();
    console.log(`✅ Scene Complete: ${scene.id}`);
  }

  if (isRendering) {
      console.log('🏁 All tasks finished, signalling renderer...');
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
