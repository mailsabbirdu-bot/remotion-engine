import {makeScene2D, Rect, Video, Img} from '@motion-canvas/2d';
import {all, createRef, waitFor, spawn} from '@motion-canvas/core';
import {TextLayer} from '../components/TextLayer';
import {Textbox} from '../components/Textbox';
import {DataVisuals} from '../components/DataVisuals';
import {Callout} from '../components/Callout';
import {ImageLayer} from '../components/ImageLayer';
import {MotionCanvasConfig, Scene} from '../types';

import configData from '../../master_motion.json';

console.log('🚀 [ENGINE] Module Loaded. Initializing scene...');

export default makeScene2D(function* (view) {
  const config = configData as MotionCanvasConfig;
  const isRendering = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('render') === 'true';
  console.log(`🔍 [ENGINE] Render mode: ${isRendering} | URL: ${window.location.search}`);

  const width = config.width || 1920;
  const height = config.height || 1080;

  // Force strict resolution
  view.size({x: width, y: height});
  view.fill(null);

  console.log(`🎬 MoCanvas Init: ${config.scenes.length} scenes`);

  if (isRendering) {
      (window as any).finished = false;
      console.log('⏳ [ENGINE] Waiting for Headless Bridge...');
      // Bridge check with safety timeout
      let bridgeAttempts = 0;
      while (!(window as any).startScene && bridgeAttempts < 300) {
          bridgeAttempts++;
          yield* waitFor(0.1);
      }

      if (!(window as any).startScene) {
          console.error('❌ [ENGINE] Bridge Timeout! StartScene function not found.');
          return;
      }
      console.log('✅ [ENGINE] Bridge Connected!');
  }

  for (let i = 0; i < config.scenes.length; i++) {
    const scene = config.scenes[i];
    console.log(`📸 Scene [${i+1}/${config.scenes.length}]: ${scene.id}`);

    if (isRendering) {
        console.log(`🎬 [SCENE] Requesting Start: ${scene.id}`);
        let sceneStarted = false;
        (window as any).startScene(i, scene.id).then(() => { sceneStarted = true; });
        while (!sceneStarted) yield;
        console.log(`🎬 [SCENE] Start Confirmed: ${scene.id}`);
    }

    const container = createRef<Rect>();
    view.add(<Rect ref={container} width={width} height={height} opacity={0} fill={null} />);

    // Add background
    if (scene.background) {
        if (scene.background.type === 'color') {
            container().add(<Rect width={width} height={height} fill={scene.background.src} />);
        } else if (scene.background.type === 'image') {
            container().add(<Img src={scene.background.src} width={width} height={height} />);
        } else if (scene.background.type === 'video') {
            const videoRef = createRef<Video>();
            container().add(<Video ref={videoRef} src={scene.background.src} width={width} height={height} play={true} />);
        }
    }

    const totalFrames = Math.round(scene.duration * config.fps);

    // Start scene animations
    spawn(function*() {
        yield* all(
            renderLayers(container, scene),
            container().opacity(1, 0.5)
        );
    });

    // Frame capture loop
    for(let f=0; f < totalFrames; f++) {
        if (isRendering) {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                const dataUrl = canvas.toDataURL('image/png');
                let frameSaved = false;
                (window as any).saveFrame(scene.id, f, dataUrl).then(() => { frameSaved = true; });
                while (!frameSaved) yield;
                if (f % 30 === 0) console.log(`🎞️ [FRAME] Scene ${scene.id}: ${f}/${totalFrames}`);
            }
        }
        yield* waitFor(1/config.fps);
    }

    if (isRendering) {
        let sceneEnded = false;
        (window as any).endScene(scene.id).then(() => { sceneEnded = true; });
        while (!sceneEnded) yield;
    }

    container().remove();
  }

  if (isRendering) {
      console.log('🏁 [ENGINE] Sequence Complete. Signaling finished...');
      (window as any).finished = true;
  }
});

function* renderLayers(container: any, scene: Scene) {
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
      } else if (layer.type === 'image' && layer.id.startsWith('callout')) {
          animations.push(function* () {
            yield* waitFor(startDelay);
            yield* Callout(layer, container());
        }());
      } else if (layer.type === 'image') {
          animations.push(function* () {
            yield* waitFor(startDelay);
            yield* ImageLayer(layer, container());
          }());
      }
  }

  yield* all(...animations);
}
