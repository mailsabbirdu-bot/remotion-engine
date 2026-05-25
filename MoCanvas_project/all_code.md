# MoCanvas Project Source Code

## MoCanvas_project/public/index.html

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MoCanvas Engine</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.ts"></script>
  </body>
</html>

```

## MoCanvas_project/src/components/DataVisuals.tsx

```
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

```

## MoCanvas_project/src/components/TextLayer.tsx

```
import {Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic} from '@motion-canvas/core';
import {Layer} from '../types';

export function* TextLayer(layer: Layer, parent: any) {
  const textRef = createRef<Txt>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Txt
      ref={textRef}
      text={content || ''}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      fill={style?.color ?? '#ffffff'}
      fontSize={style?.fontSize ?? 60}
      fontFamily={style?.fontFamily ?? 'Inter, sans-serif'}
      fontWeight={style?.fontWeight ?? 700}
      letterSpacing={style?.letterSpacing ?? 0}
      lineHeight={style?.lineHeight ?? 1.2}
      opacity={0}
      shadowColor={style?.shadowColor ?? 'rgba(0,0,0,0.5)'}
      shadowBlur={style?.shadowBlur ?? 0}
      textAlign={'center'}
      width={1400} // Wide multi-line support
      textWrap={true}
    />
  );

  const duration = animationIn?.duration ?? 0.8;
  const easing = easeOutCubic;

  if (animationIn) {
    if (animationIn.type === 'fade') {
      yield* textRef().opacity(1, duration, easing);
    } else if (animationIn.type === 'slide-up') {
      const currentY = Number(textRef().y());
      textRef().y(currentY + 100);
      yield* all(
        textRef().opacity(1, duration, easing),
        textRef().y(currentY, duration, easing),
      );
    } else if (animationIn.type === 'zoom') {
        textRef().scale(0.5);
        yield* all(
            textRef().opacity(1, duration, easing),
            textRef().scale(1, duration, easing),
        );
    } else if (animationIn.type === 'typewriter') {
        const fullText = content || '';
        textRef().text('');
        textRef().opacity(1);
        yield* textRef().text(fullText, duration);
    }
  } else {
    textRef().opacity(1);
  }
}

```

## MoCanvas_project/src/components/ImageLayer.tsx

```
import {Img} from '@motion-canvas/2d';
import {createRef, easeOutCubic, all} from '@motion-canvas/core';
import {Layer} from '../types';

export function* ImageLayer(layer: Layer, parent: any) {
  const imgRef = createRef<Img>();
  const {content, style, animationIn} = layer;

  parent.add(
    <Img
      ref={imgRef}
      src={content || ''}
      x={style?.x ?? 0}
      y={style?.y ?? 0}
      width={style?.width}
      height={style?.height}
      opacity={0}
    />
  );

  const duration = animationIn?.duration ?? 1;
  const easing = easeOutCubic;

  if (animationIn?.type === 'fade') {
    yield* imgRef().opacity(1, duration, easing);
  } else if (animationIn?.type === 'zoom') {
    imgRef().scale(0.8);
    yield* all(
        imgRef().opacity(1, duration, easing),
        imgRef().scale(1, duration, easing)
    );
  } else {
    imgRef().opacity(1);
  }
}

```

## MoCanvas_project/src/components/Callout.tsx

```
import {Rect, Txt, Line} from '@motion-canvas/2d';
import {all, createRef, easeOutBack} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Callout(layer: Layer, parent: any) {
  const lineRef = createRef<Line>();
  const circleRef = createRef<Rect>();
  const labelRef = createRef<Txt>();
  const {content, style, animationIn} = layer;

  const color = style?.color ?? '#00d2ff';
  const targetX = style?.x ?? 400;
  const targetY = style?.y ?? -250;

  parent.add(
    <Rect>
        <Line
            ref={lineRef}
            points={[
                [0, 0],
                [targetX, targetY]
            ]}
            stroke={color}
            lineWidth={4}
            end={0}
        />
        <Rect
            ref={circleRef}
            x={targetX}
            y={targetY}
            width={20}
            height={20}
            radius={10}
            fill={color}
            scale={0}
        />
        <Txt
            ref={labelRef}
            text={content || ''}
            x={targetX + (targetX > 0 ? 40 : -40)}
            y={targetY}
            fill={color}
            fontSize={40}
            fontWeight={700}
            textAlign={targetX > 0 ? 'left' : 'right'}
            opacity={0}
            offsetX={targetX > 0 ? -1 : 1}
        />
    </Rect>
  );

  const duration = animationIn?.duration ?? 1.5;

  yield* all(
      lineRef().end(1, duration),
      circleRef().scale(1.5, duration, easeOutBack),
      labelRef().opacity(1, duration)
  );
}

```

## MoCanvas_project/src/components/Textbox.tsx

```
import {Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutExpo, delay, waitFor} from '@motion-canvas/core';
import {Layer} from '../types';

export function* Textbox(layer: Layer, parent: any) {
  const rectRef = createRef<Rect>();
  const textRef = createRef<Txt>();
  const subTextRef = createRef<Txt>();
  const accentRef = createRef<Rect>();
  const containerRef = createRef<Rect>();
  const {content, style, animationIn} = layer;

  // Split content into title and subtitle if pipe exists
  const parts = content ? content.split('|') : ['', ''];
  const title = parts[0].trim();
  const sub = parts[1]?.trim() || '';

  parent.add(
    <Rect
        ref={containerRef}
        x={style?.x ?? 0}
        y={style?.y ?? 0}
        layout
        direction={'row'}
        alignItems={'stretch'}
        opacity={0}
    >
        <Rect
            ref={accentRef}
            width={10}
            height={0}
            fill={style?.stroke ?? '#f1c40f'}
            marginRight={20}
        />
        <Rect
            ref={rectRef}
            width={0}
            height={style?.height ?? 120}
            fill={style?.fill ?? 'rgba(15, 15, 15, 0.85)'}
            radius={style?.borderRadius ?? 4}
            clip
            layout
            direction={'column'}
            padding={30}
            justifyContent={'center'}
        >
            <Txt
                ref={textRef}
                text={title}
                fill={style?.color ?? '#ffffff'}
                fontSize={style?.fontSize ?? 35}
                fontFamily={'Inter, sans-serif'}
                fontWeight={800}
                letterSpacing={2}
                opacity={0}
            />
            {sub && (
                <Txt
                    ref={subTextRef}
                    text={sub}
                    fill={'#f1c40f'}
                    fontSize={(style?.fontSize ?? 35) * 0.7}
                    fontFamily={'Inter, sans-serif'}
                    fontWeight={600}
                    letterSpacing={1}
                    opacity={0}
                    marginTop={10}
                />
            )}
        </Rect>
    </Rect>
  );

  const targetWidth = Number(style?.width ?? 700);
  const targetHeight = Number(style?.height ?? 120);
  const duration = animationIn?.duration ?? 1.2;

  if (animationIn?.type === 'slide-right') {
      const startX = Number(containerRef().x());
      containerRef().x(startX - 200);
      yield* all(
        containerRef().opacity(1, 0.5),
        containerRef().x(startX, duration, easeOutExpo),
        accentRef().height(targetHeight, duration * 0.6, easeOutExpo),
        rectRef().width(targetWidth, duration, easeOutExpo),
        delay(0.4, textRef().opacity(1, 0.5)),
        sub ? delay(0.6, subTextRef().opacity(1, 0.5)) : waitFor(0)
      );
  } else {
    yield* all(
        containerRef().opacity(1, 0.3),
        accentRef().height(targetHeight, duration / 2, easeOutExpo),
        rectRef().width(targetWidth, duration, easeOutExpo),
        delay(0.3, textRef().opacity(1, 0.8)),
        sub ? delay(0.5, subTextRef().opacity(1, 0.8)) : waitFor(0)
    );
  }
}

```

## MoCanvas_project/src/scenes/main.meta

```
{
  "version": 0,
  "timeEvents": [],
  "seed": 1267567465
}
```

## MoCanvas_project/src/scenes/main.tsx

```
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
      while (!(window as any).startScene && bridgeAttempts < 200) {
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
        let done = false;
        (window as any).startScene(i, scene.id).then(() => { done = true; });
        while (!done) yield;
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
                let done = false;
                (window as any).saveFrame(scene.id, f, dataUrl).then(() => { done = true; });
                while (!done) yield;
                if (f % 30 === 0) console.log(`🎞️ [FRAME] Scene ${scene.id}: ${f}/${totalFrames}`);
            }
        }
        yield* waitFor(1/config.fps);
    }

    if (isRendering) {
        let done = false;
        (window as any).endScene(scene.id).then(() => { done = true; });
        while (!done) yield;
    }

    container().remove();
  }

  if (isRendering) {
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

```

## MoCanvas_project/src/index.ts

```
import {bootstrap} from "@motion-canvas/core";
import project from "./project";
bootstrap(project);

```

## MoCanvas_project/src/types.ts

```
export interface StyleProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  fontSize?: number;
  color?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  scale?: number;
  rotation?: number;
  fontFamily?: string;
  fontWeight?: number;
  padding?: number;
  borderRadius?: number;
  letterSpacing?: number;
  lineHeight?: number;
  shadowColor?: string;
  shadowBlur?: number;
}

export interface AnimationProps {
  type: 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right' | 'zoom' | 'blur' | 'typewriter';
  duration: number;
  delay?: number;
  easing?: string;
}

export interface Layer {
  id: string;
  type: 'text' | 'textbox' | 'image' | 'video' | 'shape' | 'chart' | 'graph';
  content?: string;
  start?: number; // start time in seconds
  duration?: number; // duration in seconds
  style?: StyleProps;
  animationIn?: AnimationProps;
  animationOut?: AnimationProps;
  data?: any;
  chartType?: 'bar' | 'line' | 'pie';
}

export interface Scene {
  id: string;
  duration: number;
  background?: {
    type: 'video' | 'image' | 'color';
    src: string;
    opacity?: number;
    audio?: string;
  };
  layers: Layer[];
}

export interface MotionCanvasConfig {
  width: number;
  height: number;
  fps: number;
  scenes: Scene[];
}

```

## MoCanvas_project/src/project.ts

```
import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../master_motion.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

console.log('🚀 [INDEX] Defining Motion Canvas project...');

export default makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

```

## MoCanvas_project/render-headless.js

```
import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';
import dns from 'dns';

if (dns.setDefaultResultOrder) {
    dns.setDefaultResultOrder('ipv4first');
}

async function render() {
    const port = 3000;
    // Navigation URL
    const url = `http://localhost:${port}/index.html?render=true&ui=false`;

    console.log('🏗️  Step 1: Building project for production...');
    try {
        execSync('npm run build', {cwd: process.cwd(), stdio: 'inherit'});
    } catch (err) {
        console.error('❌ Build failed:', err.message);
        process.exit(1);
    }

    console.log('🚀 Step 2: Starting preview server...');
    const vite = spawn('npm', ['run', 'serve', '--', '--port', port.toString(), '--host', '0.0.0.0', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        const line = data.toString();
        if (line.includes('Local:') || line.includes('Network:')) {
            console.log(`[Vite]: ${line.trim()}`);
        }
    });

    console.log('🌐 Step 3: Launching Headless Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security'
        ]
    });

    const page = await browser.newPage({
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 1
    });
    page.setDefaultTimeout(0);

    // Asset tracing
    page.on('request', request => {
        if (request.url().includes('localhost') || request.url().includes('127.0.0.1')) {
            // console.log(`🔍 [REQ]: ${request.url()}`);
        }
    });

    page.on('requestfailed', request => {
        console.error(`❌ [REQ FAILED]: ${request.url()} - ${request.failure()?.errorText}`);
    });

    page.on('response', response => {
        if (response.status() >= 400) {
            console.error(`❌ [RES ERR]: ${response.url()} status ${response.status()}`);
        }
    });

    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER FATAL]:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    await page.exposeFunction('startScene', (index, id) => {
        console.log(`🎬 [RENDER] Scene ${index+1} Started: ${id}`);
        const sceneDir = path.join(outRoot, id);
        if (!fs.existsSync(sceneDir)) fs.mkdirSync(sceneDir);
        return true;
    });

    await page.exposeFunction('saveFrame', async (sceneId, frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const filePath = path.join(outRoot, sceneId, `${frameNumber.toString().padStart(6, '0')}.png`);
        fs.writeFileSync(filePath, base64Data, 'base64');
        if (frameNumber % 60 === 0) console.log(`[DISK]: Saved frame ${frameNumber} for ${sceneId}`);
        return true;
    });

    await page.exposeFunction('endScene', (id) => {
        console.log(`✅ [RENDER] Scene Captured: ${id}. Encoding to transparent WebM...`);
        const sceneDir = path.join(outRoot, id);
        const videoOutput = path.join(outRoot, `${id}.webm`);
        const framesPattern = path.join(sceneDir, '%06d.png');

        try {
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 [SUCCESS] Video saved: ${id}.webm`);
            fs.rmSync(sceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ [ERROR] FFmpeg failed for ${id}:`, err.message);
        }
        return true;
    });

    try {
        console.log(`🔗 Step 4: Connecting to local server...`);
        let success = false;
        for (let i = 0; i < 60; i++) {
            try {
                const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 10000});
                if (response && response.status() === 200) {
                    success = true;
                    console.log('✅ Page loaded successfully.');
                    break;
                }
                console.log(`...waiting (status: ${response ? response.status() : 'none'})`);
            } catch (e) {
                console.log(`...waiting for server (attempt ${i+1}/60)`);
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) {
            await page.screenshot({path: 'connection-failure.png'});
            throw new Error(`Server at ${url} not reachable.`);
        }

        console.log('🎬 Step 5: Rendering sequence...');

        // Progress monitor
        let lastLog = Date.now();
        const progressCheck = setInterval(async () => {
            if (Date.now() - lastLog > 60000) {
                console.log('⚠️ [STUCK MONITOR]: No progress for 60s. Taking emergency screenshot...');
                await page.screenshot({path: 'stuck-screenshot.png'});
                lastLog = Date.now();
            }
        }, 30000);

        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 1000});
        clearInterval(progressCheck);
        console.log('🏁 All renders complete.');

    } catch (e) {
        console.error('❌ Render Process Failed:', e.message);
        try {
            await page.screenshot({path: 'fatal-error-screenshot.png'});
            console.log('📸 Fatal error screenshot saved.');
        } catch(ssErr) {}
    } finally {
        await browser.close();
        vite.kill();
        process.exit(0);
    }
}

render().catch(err => {
    console.error('💥 Fatal Error:', err);
    process.exit(1);
});

```

## MoCanvas_project/guideline.md

```
# MoCanvas JSON Guideline

🌟 **Engine Principles**
- **Sequential Flow:** Scenes play one after another. No overlaps.
- **Timing:** Use `duration` (seconds) to control how long a scene stays visible.
- **Coordinates:** (0,0) is the exact center of the screen. 1920x1080 resolution is standard.

🎬 **Scene Object**
- `id`: Unique name (string).
- `duration`: Visible length in seconds (number).
- `background`: (Optional)
  - `type`: "video", "image", "color".
  - `src`: Path or color code.

💎 **Storyteller Layers**

### 1. Text Layer (type: "text")
- `content`: Supports multi-line Bengali/English text.
- `style`: `fontSize`, `fontWeight`, `color`, `shadowBlur`, `x`, `y`.
- `animationIn`: "fade", "slide-up", "zoom", "typewriter".

### 2. Textbox Layer (type: "textbox")
- Sleek accent-lined boxes for locations or facts.
- `content`: Use `|` to separate title and subtitle (e.g., "Title | Subtitle").
- `style`: `width`, `height`, `fill` (bg color), `stroke` (accent line color), `fontSize`.
- `animationIn`: "slide-right", "fade", etc.

### 3. Data Visuals (type: "graph" or "chart")
- `data`: Array of numbers (for bar charts) or `[x,y]` pairs (for graphs).
- `style`: `fill` or `stroke`, `x`, `y`.

### 4. Callout Layer (type: "image" with id: "callout_...")
- Points to a specific spot in the background.
- `content`: The label text.
- `style`: `x`, `y` (the destination of the line), `color`.

---

**Note on Fonts:** Default fonts support Bangla and English. Custom fonts can be linked via style properties.

```

## MoCanvas_project/master_motion.json

```
{
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "scenes": [
    {
      "id": "scene_01_intro",
      "duration": 10,
      "layers": [
        {
          "id": "hook_text",
          "type": "text",
          "content": "ঢাকা। এই প্ল্যানেটের অন্যতম ক্রাউডেড একটা মেগাসিটি।",
          "start": 2,
          "style": {
            "x": 0,
            "y": 0,
            "fontSize": 80,
            "fontWeight": 800,
            "color": "#ffffff",
            "shadowBlur": 20
          },
          "animationIn": {
            "type": "slide-up",
            "duration": 1.5
          }
        }
      ]
    },
    {
      "id": "scene_02_catalyst",
      "duration": 12,
      "layers": [
        {
          "id": "location_box",
          "type": "textbox",
          "content": "মাধবদী, নরসিংদী | ৫.৭ মাত্রা",
          "start": 1,
          "style": {
            "x": -500,
            "y": 350,
            "width": 650,
            "height": 90,
            "fill": "rgba(231, 76, 60, 0.9)",
            "stroke": "#ffffff",
            "fontSize": 35
          },
          "animationIn": {
            "type": "slide-right",
            "duration": 1
          }
        },
        {
          "id": "alert_text",
          "type": "text",
          "content": "৩টি আফটারশক",
          "start": 4,
          "style": {
            "x": 0,
            "y": -300,
            "fontSize": 100,
            "fontWeight": 900,
            "color": "#e74c3c"
          },
          "animationIn": {
            "type": "zoom",
            "duration": 1
          }
        }
      ]
    },
    {
      "id": "scene_03_impact",
      "duration": 15,
      "layers": [
        {
          "id": "stats_chart",
          "type": "chart",
          "start": 2,
          "data": [
            50,
            150,
            300,
            450,
            500
          ],
          "style": {
            "x": 0,
            "y": 100,
            "fill": "#f1c40f"
          },
          "animationIn": {
            "type": "fade",
            "duration": 2
          }
        },
        {
          "id": "stats_label",
          "type": "text",
          "content": "৫০০+ আহত এবং ইউনিভার্সিটি বন্ধ",
          "start": 1,
          "style": {
            "x": 0,
            "y": -350,
            "fontSize": 60,
            "fontWeight": 700,
            "color": "#f1c40f"
          },
          "animationIn": {
            "type": "slide-up",
            "duration": 1
          }
        }
      ]
    },
    {
      "id": "scene_04_geology",
      "duration": 15,
      "layers": [
        {
          "id": "callout_fault",
          "type": "image",
          "content": "মেগাথ্রাস্ট ফল্ট লাইন",
          "start": 3,
          "style": {
            "x": 400,
            "y": -250,
            "color": "#00d2ff"
          },
          "animationIn": {
            "type": "fade",
            "duration": 1.5
          }
        },
        {
          "id": "plates_label",
          "type": "text",
          "content": "ইন্ডিয়ান এবং ইউরেশিয়ান প্লেটের সংঘর্ষ",
          "start": 1,
          "style": {
            "x": 0,
            "y": 400,
            "fontSize": 50,
            "color": "#ffffff",
            "fill": "rgba(0,0,0,0.5)"
          },
          "animationIn": {
            "type": "fade",
            "duration": 1
          }
        }
      ]
    },
    {
      "id": "scene_05_outro",
      "duration": 10,
      "layers": [
        {
          "id": "final_warning",
          "type": "text",
          "content": "প্রকৃতি কিন্তু বাংলাদেশকে তার ফাইনাল ওয়ার্নিংটা দিয়ে দিয়েছে।",
          "start": 2,
          "style": {
            "x": 0,
            "y": 0,
            "fontSize": 70,
            "fontWeight": 800,
            "color": "#ffffff"
          },
          "animationIn": {
            "type": "typewriter",
            "duration": 4
          }
        }
      ]
    }
  ]
}

```

## MoCanvas_project/vite.config.ts

```
import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';

export default defineConfig({
  plugins: [
    (motionCanvas as any).default(),
  ],
  base: './',
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true,
  },
  build: {
    rollupOptions: {
        input: 'index.html',
    }
  }
});

```

## MoCanvas_project/COLAB.md

```
# 🚀 MoCanvas Overlay Engine - Colab Runner

```python
# @title 🎬 START MOCANVAS OVERLAY RENDER
from google.colab import drive
import os, shutil, subprocess, time, sys

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_ROOT = "/content/mocanvas-production"
PROJECT_NAME = "MoCanvas_project"
# Repository URL for the engine
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"

def print_progress(step, percentage, message=""):
    bar_length = 30
    filled_length = int(bar_length * percentage / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rSTEP {step}: [{bar}] {percentage}% | {message}')
    sys.stdout.flush()
    if percentage == 100:
        print()

def run_command(cmd, cwd=None, step_info=None):
    if step_info:
        print(f"\n▶️ {step_info}")

    # Use unbuffered output
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               cwd=cwd, universal_newlines=True, bufsize=1)

    for line in process.stdout:
        # Simple heuristic for progress if applicable
        if "[FRAME]" in line:
            try:
                # 🎞️ [FRAME] Scene scene_id: 30/300
                parts = line.split(": ")[1].split("/")
                curr, total = int(parts[0]), int(parts[1])
                print_progress(4, int((curr/total)*100), line.strip())
            except:
                print(f"  {line.strip()}")
        elif "Scene" in line and "/" in line and "[" in line:
             try:
                parts = line.split("[")[1].split("]")[0].split("/")
                curr, total = int(parts[0]), int(parts[1])
                print_progress(4, int((curr/total)*100), line.strip())
             except:
                print(f"  {line.strip()}")
        else:
            print(f"  {line.strip()}")
            sys.stdout.flush() # Force flush

    process.wait()
    return process.returncode

def setup_and_render():
    print("🌟 MoCanvas Engine Initialization...")

    # Step 1: Dependencies
    print_progress(1, 0, "Installing system dependencies")
    run_command("apt-get update && apt-get install -y ffmpeg build-essential fonts-beng-extra --quiet")
    print_progress(1, 100, "System dependencies installed (FFmpeg + Fonts)")

    # Step 2: Project Setup
    print_progress(2, 0, "Setting up project directory")
    if os.path.exists(LOCAL_ROOT):
        shutil.rmtree(LOCAL_ROOT)
    os.makedirs(LOCAL_ROOT, exist_ok=True)

    if REPO_URL:
        run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    # Find Project
    project_dir = ""
    search_locations = [
        os.getcwd(),
        LOCAL_ROOT,
        os.path.join(BASE_DRIVE, "projects"),
        "/content",
        "/content/drive/MyDrive" # Scan entire drive as last resort
    ]

    # Priority 1: Direct name match
    for loc in search_locations:
        if not os.path.exists(loc): continue
        if os.path.basename(loc) == PROJECT_NAME:
            project_dir = loc
            break
        potential = os.path.join(loc, PROJECT_NAME)
        if os.path.exists(potential):
            project_dir = potential
            break

    # Priority 2: Marker file match (master_motion.json)
    if not project_dir:
        print_progress(2, 30, "Project folder name not found. Searching for marker file...")
        for root, dirs, files in os.walk("/content"):
            if "master_motion.json" in files and "render-headless.js" in files:
                project_dir = root
                break

    if not project_dir:
        print(f"\n❌ FAILED: Could not find '{PROJECT_NAME}' folder.")
        print(f"💡 TIP: Ensure you have cloned the repository or uploaded the '{PROJECT_NAME}' folder to Colab.")
        return

    print_progress(2, 50, f"Found project at {project_dir}")

    # Sync Manifest
    drive_manifest = os.path.join(BASE_DRIVE, "manifests/master_motion.json")
    local_manifest = os.path.join(project_dir, "master_motion.json")
    if os.path.exists(drive_manifest):
        shutil.copy2(drive_manifest, local_manifest)
        print_progress(2, 80, "Synced manifest from Drive")
    else:
        print_progress(2, 80, "Using local manifest (Drive manifest not found)")

    print_progress(2, 100, "Project setup complete")

    # Step 3: Node Setup
    print_progress(3, 0, "Installing Node modules")
    run_command("npm install", cwd=project_dir)
    print_progress(3, 40, "Installing Playwright")
    run_command("npx playwright install chromium", cwd=project_dir)
    print_progress(3, 70, "Installing Playwright dependencies")
    run_command("npx playwright install-deps", cwd=project_dir)
    print_progress(3, 100, "Node environment ready")

    # Verify Build
    dist_index = os.path.join(project_dir, "dist/index.html")
    print(f"\n🔍 Verifying build at {project_dir}/dist...")
    run_command("npm run build", cwd=project_dir)
    if not os.path.exists(dist_index):
        print(f"⚠️ Build verification failed (index.html not found in dist). Attempting local build...")
        run_command("npx vite build", cwd=project_dir)

    # Step 4: Render
    print("\n🎬 Starting Production Render...")
    out_dir = os.path.join(project_dir, "out")
    if os.path.exists(out_dir): shutil.rmtree(out_dir)

    render_code = run_command("NODE_OPTIONS='--max-old-space-size=4096' npm run render", cwd=project_dir)

    if render_code != 0:
        print("\n❌ Render failed. Check logs above.")
        return

    # Step 5: Export
    print_progress(5, 0, "Exporting to Drive")
    final_destination_root = os.path.join(BASE_DRIVE, "renders/overlays/motion_canvas")
    os.makedirs(final_destination_root, exist_ok=True)

    if os.path.exists(out_dir):
        files = [f for f in os.listdir(out_dir) if f.endswith(".webm")]
        total_files = len(files)
        for i, f in enumerate(files):
            shutil.copy2(os.path.join(out_dir, f), os.path.join(final_destination_root, f))
            print_progress(5, int(((i+1)/total_files)*100), f"Exported {f}")

        print(f"\n✅ SUCCESS! All overlays saved to: {final_destination_root}")
    else:
        print("\n❌ ERROR: No output found.")

if __name__ == "__main__":
    setup_and_render()
```

```

## MoCanvas_project/project_summary.md

```
# MoCanvas Project Summary

## What it does
MoCanvas is a JSON-driven overlay engine built with **Motion Canvas**. It takes a structured JSON manifest (`master_motion.json`) and renders each scene into a separate, transparent `.webm` video. These videos are designed to be used as high-quality overlays for video production.

## How it works
1. **JSON Driven**: The entire animation sequence, including timing, content, and styling, is defined in a single JSON file.
2. **Motion Canvas Power**: Uses the Motion Canvas framework for programmatic, ultra-smooth, "edged" animations.
3. **Headless Capture**: A custom Playwright-based script (`render-headless.js`) runs a headless browser, captures each frame of the animation as a PNG, and then uses **FFmpeg** to encode them into transparent WebM files.
4. **Colab Ready**: Designed to run entirely in Google Colab with a single cell, syncing assets from Google Drive and exporting the final renders back to Drive.
5. **Modern Aesthetics**: Built-in components for sleek textboxes, data visualizations, and animated text with various entrance effects.

## Output Path
Renders are saved to: `Counterism_Studio_V4/renders/overlays/motion_canvas` on Google Drive.

```

## MoCanvas_project/tsconfig.json

```
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "declaration": false,
    "declarationMap": false,
    "sourceMap": true,
    "removeComments": false,
    "strict": true,
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "jsx": "react-jsx",
    "jsxImportSource": "@motion-canvas/2d/lib",
    "skipLibCheck": true,
    "baseUrl": ".",
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"]
}

```

## MoCanvas_project/package.json

```
{
  "name": "mo-canvas-project",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "vite",
    "build": "vite build",
    "serve": "vite preview",
    "render": "node render-headless.js"
  },
  "dependencies": {
    "@motion-canvas/2d": "^3.17.2",
    "@motion-canvas/core": "^3.17.2",
    "@motion-canvas/ui": "^3.17.2"
  },
  "devDependencies": {
    "@motion-canvas/vite-plugin": "^3.17.2",
    "playwright": "^1.40.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0"
  }
}

```
