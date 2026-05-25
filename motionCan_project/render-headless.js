import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true&ui=false`;

    console.log('🏗️ Building project...');
    try {
        execSync('npm run build', {cwd: process.cwd(), stdio: 'inherit'});
    } catch (err) {
        console.error('❌ Build failed:', err.message);
        process.exit(1);
    }

    console.log('🚀 Starting preview server...');
    const vite = spawn('npm', ['run', 'serve', '--', '--port', port.toString(), '--host', '127.0.0.1', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stderr.on('data', (data) => {
        process.stderr.write(`Vite Error: ${data}`);
    });

    console.log('⏳ Waiting for server to respond...');
    let viteReady = false;
    for (let i = 0; i < 60; i++) {
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
        console.error('❌ Server failed to start.');
        vite.kill();
        process.exit(1);
    }
    console.log('✅ Server is ready!');

    console.log('🌐 Launching Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });

    const page = await browser.newPage();
    page.setDefaultTimeout(0);

    // Capture ALL browser console logs
    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER ERROR]:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    // EXPOSE FUNCTIONS BEFORE GOTO
    await page.exposeFunction('startScene', (index, id) => {
        console.log(`🎬 Scene Start: ${id} (Index: ${index})`);
        const sceneDir = path.join(outRoot, id);
        if (!fs.existsSync(sceneDir)) fs.mkdirSync(sceneDir);
        return true;
    });

    await page.exposeFunction('saveFrame', async (sceneId, frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const filePath = path.join(outRoot, sceneId, `${frameNumber.toString().padStart(6, '0')}.png`);
        fs.writeFileSync(filePath, base64Data, 'base64');
        return true;
    });

    await page.exposeFunction('endScene', (id) => {
        console.log(`✅ Scene Captured: ${id}. Encoding to WebM...`);
        const sceneDir = path.join(outRoot, id);
        const videoOutput = path.join(outRoot, `${id}.webm`);
        const framesPattern = path.join(sceneDir, '%06d.png');

        try {
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 Video Exported: ${videoOutput}`);
            fs.rmSync(sceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ FFmpeg Error for ${id}:`, err.message);
        }
        return true;
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'load'});

        console.log('⏳ Waiting for "window.finished" signal...');
        await page.waitForFunction(() => (window as any).finished === true, {timeout: 0, polling: 500});
        console.log('🏁 Rendering sequence complete.');

    } catch (e) {
        console.error('❌ Headless Render Failed:', e.message);
        await page.screenshot({path: 'error-screenshot.png'});
    } finally {
        await browser.close();
        vite.kill();
        process.exit(0);
    }
}

render().catch(err => {
    console.error('💥 Fatal Renderer Error:', err);
    process.exit(1);
});
