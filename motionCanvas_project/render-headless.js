import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true&ui=false`;

    console.log('🏗️ Building project for production...');
    execSync('npm run build', {cwd: process.cwd(), stdio: 'inherit'});

    console.log('🚀 Starting preview server...');
    const vite = spawn('npm', ['run', 'serve', '--', '--port', port.toString(), '--host', '127.0.0.1', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        process.stdout.write(`Vite: ${data}`);
    });

    vite.stderr.on('data', (data) => {
        process.stderr.write(`Vite Error: ${data}`);
    });

    console.log('⏳ Waiting for server to be ready...');
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
        console.warn('⚠️ Server did not respond in time, proceeding anyway...');
    } else {
        console.log('✅ Server is ready!');
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

    await page.exposeFunction('startScene', (index, id) => {
        currentSceneId = id || `scene_${index + 1}`;
        currentSceneDir = path.join(outRoot, currentSceneId);
        if (!fs.existsSync(currentSceneDir)) fs.mkdirSync(currentSceneDir);
    });

    await page.exposeFunction('saveFrame', async (frameNumber, dataUrl) => {
        if (!currentSceneDir) return;
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const fileName = `${frameNumber.toString().padStart(6, '0')}.png`;
        const filePath = path.join(currentSceneDir, fileName);
        fs.writeFileSync(filePath, base64Data, 'base64');
    });

    await page.exposeFunction('endScene', (index) => {
        console.log(`✅ Scene ${currentSceneId} captured. Encoding...`);
        const videoOutput = path.join(outRoot, `${currentSceneId}.webm`);
        const framesPattern = path.join(currentSceneDir, '%06d.png');

        try {
            // Encode scene as WebM with VP9 to preserve transparency
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 Scene Video ready: ${currentSceneId}.webm`);
            // Cleanup frames to save space
            fs.rmSync(currentSceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ Failed to encode scene ${currentSceneId}:`, err.message);
        }
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'networkidle', timeout: 120000});

        console.log('⏳ Rendering overlays...');
        await page.waitForFunction(() => window.finished === true, {timeout: 3600000, polling: 1000});
        console.log('🏁 All tasks finished!');

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
