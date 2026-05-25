import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';
import http from 'http';

async function render() {
    const port = 3000;
    const host = '127.0.0.1'; // Force IPv4
    const url = `http://${host}:${port}/?render=true&ui=false`;

    console.log('🏗️ Building project for production...');
    try {
        execSync('npm run build', {cwd: process.cwd(), stdio: 'inherit'});
    } catch (err) {
        console.error('❌ Build failed:', err.message);
        process.exit(1);
    }

    console.log('🚀 Starting preview server...');
    const vite = spawn('npm', ['run', 'serve', '--', '--port', port.toString(), '--host', host, '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        const line = data.toString();
        if (line.includes('Local:') || line.includes('Network:')) {
            console.log(`Vite: ${line.trim()}`);
        }
    });

    vite.stderr.on('data', (data) => {
        // console.log(`Vite Server Log: ${data}`);
    });

    console.log(`⏳ Waiting for server to be ready at ${url}...`);
    let viteReady = false;
    // Wait up to 2 minutes
    for (let i = 0; i < 120; i++) {
        try {
            await new Promise((resolve, reject) => {
                const req = http.get(`http://${host}:${port}`, (res) => {
                    if (res.statusCode === 200) {
                        viteReady = true;
                        resolve();
                    } else {
                        reject(new Error(`Status: ${res.statusCode}`));
                    }
                });
                req.on('error', reject);
                req.end();
            });
            if (viteReady) break;
        } catch (e) {
            // console.log(`...waiting (${e.message})`);
        }
        await new Promise(r => setTimeout(r, 1000));
    }

    if (!viteReady) {
        console.error(`❌ Server failed to respond at http://${host}:${port} after 120s`);
        vite.kill();
        process.exit(1);
    }
    console.log('✅ Server is responsive!');

    console.log('🌐 Launching Headless Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--autoplay-policy=no-user-gesture-required'
        ]
    });

    const page = await browser.newPage();
    page.setDefaultTimeout(0);

    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER ERROR]:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    await page.exposeFunction('startScene', (index, id) => {
        console.log(`🎬 Scene [${index+1}] Start: ${id}`);
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
        console.log(`✅ Scene Captured: ${id}. Encoding...`);
        const sceneDir = path.join(outRoot, id);
        const videoOutput = path.join(outRoot, `${id}.webm`);
        const framesPattern = path.join(sceneDir, '%06d.png');

        try {
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 scene video saved: ${id}.webm`);
            fs.rmSync(sceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ FFmpeg failed for ${id}:`, err.message);
        }
        return true;
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'load', timeout: 90000});

        console.log('⏳ Stabilizing bundle...');
        await new Promise(r => setTimeout(r, 5000));

        console.log('🎬 Rendering sequence...');
        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 500});
        console.log('🏁 Rendering sequence complete.');

    } catch (e) {
        console.error('❌ Headless Render Failed:', e.message);
        await page.screenshot({path: 'render-error.png'});
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
