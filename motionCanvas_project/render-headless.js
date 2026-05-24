import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true&ui=false`;

    console.log('🚀 Starting Vite server...');
    const vite = spawn('npm', ['run', 'start', '--', '--port', port.toString(), '--host', '127.0.0.1', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        process.stdout.write(`Vite: ${data}`);
    });

    vite.stderr.on('data', (data) => {
        process.stderr.write(`Vite Error: ${data}`);
    });

    console.log('⏳ Waiting for Vite to be ready...');
    let viteReady = false;
    for (let i = 0; i < 30; i++) {
        try {
            const res = await fetch(`http://127.0.0.1:${port}`);
            if (res.ok) {
                viteReady = true;
                break;
            }
        } catch (e) {}
        await new Promise(r => setTimeout(r, 1000));
    }
    if (!viteReady) {
        console.warn('⚠️ Vite server did not respond in time, proceeding anyway...');
    } else {
        console.log('✅ Vite server is ready!');
    }

    console.log('🌐 Opening browser...');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security'
        ]
    });

    const context = await browser.newContext({
        viewport: {width: 1920, height: 1080},
        deviceScaleFactor: 1,
        screen: {width: 1920, height: 1080}
    });

    const page = await context.newPage();
    page.setDefaultTimeout(0);

    page.on('console', msg => {
        console.log(`BROWSER [${msg.type()}]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('BROWSER ERROR:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    let currentSceneDir = '';
    let currentSceneId = '';

    // Signaling for scenes
    await page.exposeFunction('startScene', (index, id) => {
        currentSceneId = id || `scene_${index + 1}`;
        currentSceneDir = path.join(outRoot, currentSceneId);
        if (!fs.existsSync(currentSceneDir)) fs.mkdirSync(currentSceneDir);
        console.log(`🎬 Rendering Scene: ${currentSceneId}`);
    });

    await page.exposeFunction('saveFrame', async (frameNumber) => {
        if (!currentSceneDir) return;
        const fileName = `${frameNumber.toString().padStart(6, '0')}.png`;
        const filePath = path.join(currentSceneDir, fileName);

        const canvas = await page.$('canvas');
        if (canvas) {
            await canvas.screenshot({path: filePath, omitBackground: true});
        }
    });

    await page.exposeFunction('endScene', (index) => {
        console.log(`✅ Scene ${currentSceneId} frames captured. Encoding...`);
        const videoOutput = path.join(outRoot, `${currentSceneId}.webm`);
        const framesPattern = path.join(currentSceneDir, '%06d.png');

        try {
            // Encode scene as WebM with VP9 to preserve transparency (alpha channel)
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 2M -crf 30 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 Scene Video ready: ${currentSceneId}.webm`);
        } catch (err) {
            console.error(`❌ Failed to encode scene ${currentSceneId}:`, err.message);
        }
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'load', timeout: 120000});

        try {
            await page.waitForLoadState('networkidle', {timeout: 15000});
        } catch (e) {
            console.log('⚠️ Networkidle timeout, proceeding with render...');
        }

        console.log('⏳ Waiting for all scenes to complete...');
        await page.waitForFunction(() => window.finished === true, {timeout: 3600000, polling: 1000});
        console.log('🏁 All rendering and encoding tasks finished!');

    } catch (e) {
        console.error('❌ Render failed:', e.message);
        await page.screenshot({path: 'error-screenshot.png'});
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
